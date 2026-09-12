# -*- coding: utf-8 -*-
"""
ProgramMind 数据库层（SQLite）
================================
【设计说明】按最新需求，平台接入真实数据库（SQLite，零外部服务、文件即库），
满足“可注册 / 可登录 / 新学生可加入课程并享受学习资源”的完整业务闭环。

为什么选 SQLite：
- Python 标准库自带（sqlite3），无需 pip 安装、无需启动数据库服务；
- 数据落地为单个文件 programmind.db，进程重启不丢失，依然“开箱即演示”；
- 既保留了原有内存 Mock 业务数据（课程/作业/知识点等）的离线演示能力，
  又把“用户账号 / 选课关系”这类需要持久化、由用户产生的数据交给数据库管理。

数据表：
- users（用户：账号、密码、角色、资料）—— 注册写入、登录校验
- enrollments（选课：student_id, course_id, progress）—— 新学生加入课程后写入

对外暴露的辅助函数供 routes_auth / routes_api 直接调用。
"""
import os
import sqlite3
import datetime

# 数据库文件与 backend 同目录（programmind/backend/programmind.db）
DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "programmind.db")

# 导入 Mock 中的初始演示账号与选课关系，用于首次启动“播种”数据库
from mock_data import USERS, ENROLLMENTS


def get_conn():
    """获取数据库连接（row_factory 以便按列名访问）。"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    """
    初始化并播种数据库。幂等：表已存在则跳过；数据为空则写入演示种子。
    首次运行即生成 programmind.db，之后所有账号与选课真实落库。
    """
    conn = get_conn()
    cur = conn.cursor()
    # 用户表
    cur.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id       TEXT PRIMARY KEY,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            role     TEXT NOT NULL,
            name     TEXT,
            title    TEXT,
            grade    TEXT,
            major    TEXT,
            school   TEXT,
            dept     TEXT,
            email    TEXT,
            avatar   TEXT,
            intro    TEXT,
            joined   TEXT
        )
    """)
    # 选课表（学生 -> 课程 -> 进度）
    cur.execute("""
        CREATE TABLE IF NOT EXISTS enrollments (
            student_id TEXT NOT NULL,
            course_id  TEXT NOT NULL,
            progress   INTEGER DEFAULT 0,
            PRIMARY KEY (student_id, course_id)
        )
    """)
    conn.commit()

    # 迁移：确保 do_not_disturb（消息免打扰）列存在（老库升级用，幂等）
    _ensure_user_column(conn, "do_not_disturb", "INTEGER DEFAULT 0")

    # 上传文件表：字节直接落库（避免公开静态 URL 任意下载，下载走带权限的接口）
    cur.execute("""
        CREATE TABLE IF NOT EXISTS files (
            id            TEXT PRIMARY KEY,
            owner         TEXT,
            role          TEXT,
            course_id     TEXT,
            kind          TEXT,
            original_name TEXT,
            mime          TEXT,
            size          INTEGER,
            data          BLOB,
            created_at    TEXT
        )
    """)
    conn.commit()

    # 仅当表为空时播种，避免覆盖用户注册产生的新数据
    cur.execute("SELECT COUNT(*) AS n FROM users")
    if cur.fetchone()["n"] == 0:
        for u in USERS.values():
            cur.execute(
                """INSERT OR IGNORE INTO users
                   (id,username,password,role,name,title,grade,major,school,dept,email,avatar,intro,joined)
                   VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
                (u["id"], u["username"], u["password"], u["role"], u.get("name", ""),
                 u.get("title", ""), u.get("grade", ""), u.get("major", ""), u.get("school", ""),
                 u.get("dept", ""), u.get("email", ""), u.get("avatar", ""), u.get("intro", "") or "",
                 u.get("joined", "")),
            )
    # 播种默认选课关系（让预置学生一登录就能看到课程）
    cur.execute("SELECT COUNT(*) AS n FROM enrollments")
    if cur.fetchone()["n"] == 0:
        for sid, cs in ENROLLMENTS.items():
            for cid, prog in cs.items():
                cur.execute(
                    "INSERT OR IGNORE INTO enrollments (student_id, course_id, progress) VALUES (?,?,?)",
                (sid, cid, prog),
            )
    conn.commit()

    # 头像默认策略：未设置时前端按“姓名首字 + 自动配色”渲染（类似学习通）。
    # 清理历史播种的在线头像（pravatar 需联网，且并非用户主动设置），统一改为默认。
    # 已设置自定义头像（data:image / emoji: / 外链）不受影响，重复执行幂等。
    cur.execute("UPDATE users SET avatar='' WHERE avatar LIKE 'https://i.pravatar.cc%'")
    conn.commit()
    conn.close()


# ---------------------------------------------------------------------------
# 用户相关
# ---------------------------------------------------------------------------
def _row_to_user(row):
    """sqlite3.Row -> 普通 dict（含 password，供内部校验用）。"""
    if not row:
        return None
    return dict(row)


def _ensure_user_column(conn, col, coldef):
    """幂等地为 users 表追加列（用于老库升级，避免重复 ALTER 报错）。"""
    cur = conn.cursor()
    cols = [r["name"] for r in cur.execute("PRAGMA table_info(users)")]
    if col not in cols:
        cur.execute(f"ALTER TABLE users ADD COLUMN {col} {coldef}")
        conn.commit()


def public_user(u):
    """脱敏后的用户信息（移除密码字段），供接口返回。"""
    if not u:
        return None
    return {k: v for k, v in u.items() if k != "password"}


def db_get_user_by_username(username):
    conn = get_conn()
    row = conn.execute("SELECT * FROM users WHERE username=?", (username,)).fetchone()
    conn.close()
    return _row_to_user(row)


def db_get_user_by_id(uid):
    conn = get_conn()
    row = conn.execute("SELECT * FROM users WHERE id=?", (uid,)).fetchone()
    conn.close()
    return _row_to_user(row)


def db_username_exists(username):
    conn = get_conn()
    row = conn.execute("SELECT 1 FROM users WHERE username=?", (username,)).fetchone()
    conn.close()
    return row is not None


def db_authenticate(username, password, role):
    """
    登录校验：返回 (user_dict, error_msg)。
    - user 为 None 表示失败，error_msg 给出友好原因
    - 校验账号是否存在、密码是否正确、所选身份是否匹配
    """
    u = db_get_user_by_username(username)
    if not u:
        return None, "用户不存在，请先注册或检查账号"
    if u["password"] != password:
        return None, "密码错误，请重试"
    if u["role"] != role:
        return None, f"身份不匹配：该账号为『{u['role'] == 'teacher' and '教师' or '学生'}』，请切换身份"
    return u, None


def db_register(username, password, name, role="student", school="", major="", grade="", email=""):
    """
    注册新用户：返回 (user_dict, error_msg)。
    - 账号唯一性校验
    - 自动生成全局唯一 id（S/T + 时间戳后 7 位，避免并发碰撞）
    - 默认头像取自 pravatar，演示更真实
    """
    username = (username or "").strip()
    password = password or ""
    name = (name or "").strip()
    if not username or not password:
        return None, "账号和密码不能为空"
    if len(username) < 3:
        return None, "账号至少 3 个字符"
    if db_username_exists(username):
        return None, "该账号已被注册，请直接登录或换一个"
    uid = ("S" if role == "student" else "T") + datetime.datetime.now().strftime("%y%m%d%H%M%S")[-7:]
    # 默认头像为空：前端按“姓名首字 + 自动配色”渲染（类似学习通），可由用户自行设置
    avatar = ""
    conn = get_conn()
    conn.execute(
        """INSERT INTO users (id,username,password,role,name,title,grade,major,school,dept,email,avatar,intro,joined)
           VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
        (uid, username, password, role, name,
         "讲师" if role == "teacher" else "", grade, major, school or "计算机科学与技术学院",
         "", email, avatar, "新注册用户", datetime.datetime.now().strftime("%Y-%m-%d")),
    )
    conn.commit()
    conn.close()
    return db_get_user_by_username(username), None


def db_update_profile(uid, fields):
    """
    更新用户资料（昵称 / 邮箱 / 简介 / 头像 / 消息免打扰），fields 为 dict。
    - 仅允许白名单字段，避免 SQL 注入与越权字段
    - 头像取值约定：空串=使用姓名默认头像；emoji:<字符>=内置表情头像；
      data:image/...=用户上传的图片（base64）；http(s)://...=外链图片
    - do_not_disturb：消息免打扰开关，传入布尔 / 0|1，统一存为 0/1
    """
    allowed = {"name", "email", "intro", "avatar", "do_not_disturb"}
    sets = {k: v for k, v in (fields or {}).items() if k in allowed}
    if not sets:
        return db_get_user_by_id(uid)
    conn = get_conn()
    cur = conn.cursor()
    for k, v in sets.items():
        if k == "do_not_disturb":
            v = 1 if v else 0
        cur.execute(f"UPDATE users SET {k}=? WHERE id=?", (v, uid))
    conn.commit()
    conn.close()
    return db_get_user_by_id(uid)


# ---------------------------------------------------------------------------
# 上传文件（字节落库，下载走带权限接口，避免公开静态 URL 任意下载）
# ---------------------------------------------------------------------------
def db_insert_file(owner, role, course_id, kind, original_name, mime, data):
    """保存上传文件字节到 files 表，返回文件 id（fid）。"""
    import time as _t
    fid = "F" + str(int(_t.time() * 1000)) + str(abs(hash(owner + original_name)) % 10000)
    conn = get_conn()
    conn.execute(
        """INSERT OR REPLACE INTO files
           (id, owner, role, course_id, kind, original_name, mime, size, data, created_at)
           VALUES (?,?,?,?,?,?,?,?,?,?)""",
        (fid, owner, role, course_id or "", kind, original_name,
         mime, len(data) if data else 0, data,
         _t.strftime("%Y-%m-%d %H:%M:%S")),
    )
    conn.commit()
    conn.close()
    return fid


def db_get_file(fid):
    """按 id 取文件（含字节），不存在返回 None。"""
    conn = get_conn()
    row = conn.execute("SELECT * FROM files WHERE id=?", (fid,)).fetchone()
    conn.close()
    if not row:
        return None
    return {
        "id": row["id"], "owner": row["owner"], "role": row["role"],
        "course_id": row["course_id"], "kind": row["kind"],
        "original_name": row["original_name"], "mime": row["mime"],
        "size": row["size"], "data": row["data"],
    }


# ---------------------------------------------------------------------------
# 选课（课程成员关系）相关 —— 支撑“新学生也可以享受课程”
# ---------------------------------------------------------------------------
def db_student_course_ids(sid):
    """返回某学生已加入的全部课程 id 列表。"""
    conn = get_conn()
    rows = conn.execute("SELECT course_id FROM enrollments WHERE student_id=?", (sid,)).fetchall()
    conn.close()
    return [r["course_id"] for r in rows]


def db_student_progress(sid, cid):
    """返回某学生在某课程的进度（0-100），未选课返回 0。"""
    conn = get_conn()
    row = conn.execute(
        "SELECT progress FROM enrollments WHERE student_id=? AND course_id=?",
        (sid, cid),
    ).fetchone()
    conn.close()
    return int(row["progress"]) if row else 0


def db_enroll(sid, cid):
    """学生加入课程（幂等：已加入则不重复插入）。返回是否新加入。"""
    conn = get_conn()
    exist = conn.execute(
        "SELECT 1 FROM enrollments WHERE student_id=? AND course_id=?",
        (sid, cid),
    ).fetchone()
    if exist:
        conn.close()
        return False
    conn.execute(
        "INSERT INTO enrollments (student_id, course_id, progress) VALUES (?,?,?)",
        (sid, cid, 0),
    )
    conn.commit()
    conn.close()
    return True


def db_course_student_ids(cid):
    """返回某课程的全部学生 id 列表（教师端查看学生名单用）。"""
    conn = get_conn()
    rows = conn.execute("SELECT student_id FROM enrollments WHERE course_id=?", (cid,)).fetchall()
    conn.close()
    return [r["student_id"] for r in rows]


# 模块加载即初始化数据库（保证首次请求前表已存在）
init_db()
