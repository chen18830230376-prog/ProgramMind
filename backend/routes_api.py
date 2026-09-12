# -*- coding: utf-8 -*-
"""
业务数据 API 蓝图（Data API Blueprint）
======================================
为前端各业务模块提供内存模拟数据。所有接口都先做登录校验（require_login），
并按角色返回对应数据，体现“权限隔离”。

模块覆盖：工作台 / 学习 / 教学 / AI助手 / 成长 / 个人中心
（AI 文本生成在【前端】模拟，本文件只提供结构化业务数据，保证离线可演示）
"""
import os
import time
import json
from flask import Blueprint, request, session, jsonify, Response, stream_with_context
from mock_data import (
    COURSES, HOMEWORK, QUIZZES, EXPERIMENTS, KNOWLEDGE_GRAPH,
    MASTERY, LEARNING_RECORDS, GROWTH, AI_HISTORY, NOTIFICATIONS, FAVORITES, COURSEWARE,
    course_by_id, MAJOR_COURSES, MAJORS,
    # 状态变更能力：让演示从"静态展示"升级为"可交互业务闭环"
    DATA_LOCK, append_record, append_timeline, update_mastery, add_notification, now_str,
)
# 本地大模型接入层（默认 Mock，配置环境变量即可切换本地部署模型）
from llm import generate as llm_generate
from llm import generate_with_sources as llm_generate_with_sources
from ai_client import find_rag_chunk
# 运行时业务数据持久化（项目记忆：重启不丢作业图片 / 批改 / 掌握度等）
from persist import save_runtime_state, load_runtime_state
from mock_data import set_persist_hook
set_persist_hook(save_runtime_state)
# 便捷别名：写操作后落盘
_persist = save_runtime_state
# 用户账号 / 选课关系 改由数据库（SQLite）提供，支撑注册与"新学生加入课程"
from db import (
    db_get_user_by_username, db_get_user_by_id, public_user, db_update_profile,
    db_student_course_ids, db_student_progress, db_enroll, db_course_student_ids,
    db_insert_file, db_get_file,
)
from urllib.parse import quote as _urlquote

api_bp = Blueprint("api", __name__, url_prefix="/api")

# 上传目录：frontend/uploads/（由前端静态托管直接服务，离线可用）
_BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # programmind/
FRONTEND_DIR = os.path.join(_BASE_DIR, "frontend")
UPLOAD_DIR = os.path.join(FRONTEND_DIR, "uploads")
os.makedirs(UPLOAD_DIR, exist_ok=True)
ALLOWED_IMG = {"png", "jpg", "jpeg", "gif", "webp", "bmp"}
# 实验报告允许的常见文档格式（图片之外的报告文件）
ALLOWED_DOC = {"pdf", "doc", "docx", "ppt", "pptx", "xls", "xlsx",
               "txt", "md", "csv", "zip", "rar"}


def require_login():
    """校验登录态，返回当前用户字典或 None（用户从数据库读取）。"""
    if "username" not in session:
        return None
    return db_get_user_by_username(session["username"])


def student_courses(sid):
    """返回某学生已加入的课程对象列表（成员关系来自 enrollments 表）。"""
    ids = set(db_student_course_ids(sid))
    return [c for c in COURSES if c["id"] in ids]


def student_public(sid):
    """根据学生 id 取脱敏信息（兼容数据库账号，含注册产生的新用户）。"""
    return public_user(db_get_user_by_id(sid))


def deny():
    return jsonify({"code": 401, "msg": "未登录或无权限"}), 401


# ---------------------------------------------------------------------------
# 工作台 Workspace：任务驱动式首页
# ---------------------------------------------------------------------------
@api_bp.route("/workspace", methods=["GET"])
def workspace():
    user = require_login()
    if not user:
        return deny()
    if user["role"] == "teacher":
        my_courses = [c for c in COURSES if c["teacher"] == user["username"]]
        # 待备课：演示用静态提醒（真实可由教师标注）
        todo_lessons = [
            {"course": "Python 程序设计", "chapter": "第4章 面向对象", "due": "今天 14:00"},
            {"course": "数据结构", "chapter": "第3章 树与二叉树", "due": "明天 10:00"},
        ]
        # 待批改作业
        pending_hw = []
        for h in HOMEWORK:
            for sid, sub in h["submissions"].items():
                if sub["status"] == "submitted":
                    # 带上 id，前端可直接发起"批改"动作（任务中心闭环）
                    pending_hw.append({
                        "hw_id": h["id"], "hw": h["title"],
                        "student_id": sid, "student": db_get_user_by_id(sid)["name"],
                        "course": course_by_id(h["course"])["name"] if course_by_id(h["course"]) else "",
                    })
        return jsonify({"code": 0, "role": "teacher", "data": {
            "today_schedule": [
                {"time": "08:00-09:40", "course": "Python 程序设计", "room": "逸夫楼 301", "class": "计科2301"},
                {"time": "10:00-11:40", "course": "数据结构", "room": "逸夫楼 305", "class": "软工2301"},
                {"time": "14:00-15:40", "course": "计算机网络", "room": "线上", "class": "计科2302"},
            ],
            "todo_lessons": todo_lessons,
            "ai_lesson_tips": "AI 已为你草拟《二叉树遍历》教案，建议补充可视化实验。",
            "grading_tips": pending_hw or [{"hw": "暂无新提交", "student": ""}],
            "analytics_tips": "学生 S002 的『二叉树』掌握度 48，建议推送针对性复习。",
            "recent_resources": [
                {"title": "Python 第3章 课件", "type": "PPT", "course": "Python 程序设计"},
                {"title": "数据结构 实验指导书", "type": "PDF", "course": "数据结构"},
            ],
            "ai_suggestions": [
                "为『计算机网络』生成一份期中复习 PPT 大纲",
                "对掌握度<50 的学生自动推送补强练习",
                "将本次作业优秀答案沉淀为知识库样例",
            ],
            "my_courses": [{"id": c["id"], "name": c["name"], "students": len(c["students"])} for c in my_courses],
        }})
    else:
        sid = user["id"]
        my_courses = student_courses(sid)
        today_tasks = [
            {"course": "Python 程序设计", "task": "完成实验：银行账户", "due": "今天 22:00", "done": False},
            {"course": "数据结构", "task": "复习二叉树遍历", "due": "今天", "done": True},
            {"course": "计算机网络", "task": "观看 TCP 三次握手动画", "due": "明天", "done": False},
        ]
        records = [r for r in LEARNING_RECORDS if r["student"] == sid][:5]
        growth = GROWTH.get(sid, {})
        return jsonify({"code": 0, "role": "student", "data": {
            "today_plan": today_tasks,
            "todo_tasks": [t for t in today_tasks if not t["done"]],
            "ai_advice": growth.get("ai_advice", "保持每日 coding 习惯，循序渐进。"),
            "nav_entries": [
                {"name": "我的课程", "to": "/learn/courses"},
                {"name": "AI 学习辅导", "to": "/learn/ai-tutor"},
                {"name": "成长中心", "to": "/growth"},
            ],
            "recent_records": records,
            "growth_trend": [62, 65, 68, 70, 73, 78, 80],  # 近 7 次学习活跃度
            "recommend_review": growth.get("recommendations", [])[:3],
            "enrolled_count": len(my_courses),
            "my_courses": [{"id": c["id"], "name": c["name"], "progress": db_student_progress(sid, c["id"])} for c in my_courses],
        }})


# ---------------------------------------------------------------------------
# 学习模块（学生）
# ---------------------------------------------------------------------------
@api_bp.route("/learn/overview", methods=["GET"])
def learn_overview():
    user = require_login()
    if not user or user["role"] != "student":
        return deny()
    sid = user["id"]
    my = student_courses(sid)
    # 教材 + 学习资料 分开展示：
    # textbooks = 已加入课程的本地教材封面（点击放大预览）
    # materials = 仅保留“有真实网络链接”的课件（点击跳转新标签页）
    textbooks = []
    materials = []
    for c in my:
        textbooks.append({"title": c["name"] + "（教材）", "type": "教材",
                          "course": c["id"], "course_name": c["name"],
                          "cover": c["textbook"]})
        for w in COURSEWARE.get(c["id"], []):
            if w.get("link"):
                materials.append({"title": w["title"], "type": w["type"],
                                  "course": c["id"], "course_name": c["name"],
                                  "link": w["link"]})
    return jsonify({"code": 0, "data": {
        "courses": [{"id": c["id"], "name": c["name"], "cover": c["cover"], "textbook": c["textbook"],
                     "progress": db_student_progress(sid, c["id"]),
                     "color": c["color"]} for c in my],
        "today": [
            {"course": "Python 程序设计", "task": "银行账户实验", "done": False},
            {"course": "数据结构", "task": "二叉树复习", "done": True},
        ],
        "textbooks": textbooks,
        "materials": materials,
        "records": [r for r in LEARNING_RECORDS if r["student"] == sid],
    }})


@api_bp.route("/learn/homework", methods=["GET"])
def learn_homework():
    user = require_login()
    if not user or user["role"] != "student":
        return deny()
    sid = user["id"]
    # 仅展示“已加入课程”的作业 —— 体现选课成员关系对内容的约束
    enrolled = set(db_student_course_ids(sid))
    result = []
    for h in HOMEWORK:
        if h["course"] not in enrolled:
            continue
        sub = h["submissions"].get(sid, {"status": "pending", "score": None, "feedback": "", "image": None})
        result.append({"id": h["id"], "course": course_by_id(h["course"])["name"],
                       "title": h["title"], "desc": h["desc"], "due": h["due"], **sub})
    return jsonify({"code": 0, "data": result})


@api_bp.route("/learn/quiz/<qid>", methods=["GET"])
def learn_quiz(qid):
    user = require_login()
    if not user or user["role"] != "student":
        return deny()
    for q in QUIZZES:
        if q["id"] == qid:
            return jsonify({"code": 0, "data": q})
    return jsonify({"code": 1, "msg": "测验不存在"})


# ---------------------------------------------------------------------------
# 教学模块（教师）
# ---------------------------------------------------------------------------
@api_bp.route("/teach/courses", methods=["GET"])
def teach_courses():
    user = require_login()
    if not user or user["role"] != "teacher":
        return deny()
    result = []
    for c in [c for c in COURSES if c["teacher"] == user["username"]]:
        # 学生名单来自 enrollments 表（含新注册并选课的学生）
        stu_ids = db_course_student_ids(c["id"])
        result.append({
            "id": c["id"], "code": c["code"], "name": c["name"], "cover": c["cover"],
            "color": c.get("color", "#165DFF"), "textbook": c["textbook"],
            "description": c["description"],
            "students": [student_public(s) for s in stu_ids],
        })
    return jsonify({"code": 0, "data": result})


@api_bp.route("/teach/homework", methods=["GET", "POST"])
def teach_homework():
    """教师作业管理：
    GET  —— 列出本人课程下的全部作业 + 提交情况概览；
    POST —— 发布作业（为选课学生建 pending 提交，并定向推送“新作业”通知）。"""
    user = require_login()
    if not user or user["role"] != "teacher":
        return deny()
    if request.method == "POST":
        d = request.get_json(silent=True, force=True) or {}
        cid = d.get("course_id")
        title = (d.get("title") or "").strip()
        if not cid or not title:
            return jsonify({"code": 1, "msg": "请选择课程并填写作业标题"})
        c = course_by_id(cid)
        if not c or c["teacher"] != user["username"]:
            return jsonify({"code": 1, "msg": "课程不存在或无权限"})
        hid = "H" + str(len(HOMEWORK) + 1)
        stu_ids = db_course_student_ids(cid)
        subs = {sid: {"status": "pending", "score": None, "feedback": "", "image": None} for sid in stu_ids}
        with DATA_LOCK:
            HOMEWORK.append({
                "id": hid, "course": cid, "title": title,
                "desc": d.get("desc") or "", "due": d.get("due") or "",
                "submissions": subs,
            })
        # 向每位选课学生定向推送“新作业”通知 —— 学生端即时收到
        for sid in stu_ids:
            u = db_get_user_by_id(sid)
            if u:
                add_notification("新作业待完成", f"《{title}》已发布，请在 {d.get('due') or '尽快'} 前提交",
                                 "homework", target=u["username"])
        return jsonify({"code": 0, "msg": "作业已发布，学生已收到通知", "hw_id": hid})

    # GET：列表概览
    my_courses = [c["id"] for c in COURSES if c["teacher"] == user["username"]]
    result = []
    for h in HOMEWORK:
        if h["course"] not in my_courses:
            continue
        c = course_by_id(h["course"])
        subs = h["submissions"]
        done = sum(1 for s in subs.values() if s["status"] == "submitted")
        graded = sum(1 for s in subs.values() if s["status"] == "graded")
        result.append({
            "id": h["id"], "course": c["name"] if c else "", "course_id": h["course"],
            "title": h["title"], "desc": h["desc"], "due": h["due"],
            "total": len(subs), "submitted": done, "graded": graded,
            "pending": len(subs) - done,
        })
    return jsonify({"code": 0, "data": result})


@api_bp.route("/teach/experiments", methods=["GET", "POST"])
def teach_experiments():
    user = require_login()
    if not user or user["role"] != "teacher":
        return deny()

    if request.method == "POST":
        d = request.get_json(silent=True, force=True) or {}
        cid = d.get("course")
        title = (d.get("title") or "").strip()
        if not cid or not title:
            return jsonify({"code": 1, "msg": "请选择课程并填写实验名称"})
        c = course_by_id(cid)
        if not c or c["teacher"] != user["username"]:
            return jsonify({"code": 1, "msg": "课程不存在或无权限"})
        eid = "E" + str(len(EXPERIMENTS) + 1).zfill(3)
        stu_ids = db_course_student_ids(cid)
        subs = {sid: {"status": "pending", "score": None, "feedback": "", "content": "", "image": None, "file": None, "file_name": None, "submitted_at": None} for sid in stu_ids}
        with DATA_LOCK:
            EXPERIMENTS.append({
                "id": eid, "course": cid, "title": title,
                "desc": d.get("desc") or "", "due": d.get("due") or "",
                "submissions": subs,
            })
        _persist()
        for sid in stu_ids:
            u = db_get_user_by_id(sid)
            if u:
                add_notification("新实验待完成", f"《{title}》已发布，请在 {d.get('due') or '尽快'} 前提交",
                                 "experiment", target=u["username"])
        return jsonify({"code": 0, "msg": "实验已发布，学生已收到通知", "exp_id": eid})

    # GET：列表概览
    my_courses = [c["id"] for c in COURSES if c["teacher"] == user["username"]]
    result = []
    for e in EXPERIMENTS:
        if e["course"] not in my_courses:
            continue
        subs = e.get("submissions", {})
        submitted = sum(1 for s in subs.values() if s.get("status") in ("submitted", "graded"))
        graded = sum(1 for s in subs.values() if s.get("status") == "graded")
        pending = sum(1 for s in subs.values() if s.get("status") == "pending")
        result.append({"id": e["id"], "course": course_by_id(e["course"])["name"],
                       "course_id": e["course"], "title": e["title"], "desc": e["desc"], "due": e["due"],
                       "submitted": submitted, "graded": graded, "pending": pending, "total": len(subs)})
    return jsonify({"code": 0, "data": result})


@api_bp.route("/teach/experiments/<eid>", methods=["GET"])
def teach_experiment_detail(eid):
    """教师查看单个实验的全部学生提交（批改工作台数据源，含学生姓名/头像与上传图片）。"""
    user = require_login()
    if not user or user["role"] != "teacher":
        return deny()
    exp = next((e for e in EXPERIMENTS if e["id"] == eid), None)
    c = course_by_id(exp["course"]) if exp else None
    if not exp or not c or c["teacher"] != user["username"]:
        return jsonify({"code": 1, "msg": "实验不存在或无权限"})
    subs = []
    for sid, sub in exp["submissions"].items():
        u = db_get_user_by_id(sid)
        subs.append({
            "student_id": sid,
            "student": u["name"] if u else sid,
            "avatar": u.get("avatar", "") if u else "",
            "status": sub["status"], "score": sub.get("score"),
            "feedback": sub.get("feedback", ""), "content": sub.get("content", ""),
            "image": sub.get("image"), "file": sub.get("file"), "file_name": sub.get("file_name", ""), "submitted_at": sub.get("submitted_at"),
        })
    return jsonify({"code": 0, "data": {
        "id": exp["id"], "course": c["name"], "course_id": exp["course"],
        "title": exp["title"], "desc": exp["desc"], "due": exp["due"], "submissions": subs,
    }})


@api_bp.route("/teach/experiments/grade", methods=["POST"])
def grade_experiment():
    """教师批改实验：写入分数与评语，并把评价结果反哺知识点掌握度（动态学情闭环）。"""
    user = require_login()
    if not user or user["role"] != "teacher":
        return deny()
    d = request.get_json(silent=True, force=True) or {}
    eid, sid = d.get("exp_id"), d.get("student_id")
    score = d.get("score")
    if score is None:
        return jsonify({"code": 1, "msg": "请填写分数"})
    for e in EXPERIMENTS:
        if e["id"] == eid and sid in e["submissions"]:
            c = course_by_id(e["course"])
            if not c or c["teacher"] != user["username"]:
                return jsonify({"code": 1, "msg": "无权限"})
            with DATA_LOCK:
                sub = e["submissions"][sid]
                sub["status"] = "graded"
                sub["score"] = int(score)
                sub["feedback"] = d.get("feedback", "")
            append_record(sid, e["course"], "实验批改", f"《{e['title']}》得分 {score}", 0)
            if c:
                pts = []
                for ch in c["chapters"]:
                    pts.extend(ch["points"])
                update_mastery(sid, {p: int(score) for p in pts[:6] if p in MASTERY.get(sid, {})})
            add_notification("实验已批改", f"《{e['title']}》已批改，得分 {score}", "experiment")
            _persist()
            return jsonify({"code": 0, "msg": "批改完成，学情已同步更新"})
    return jsonify({"code": 1, "msg": "未找到该提交"})


@api_bp.route("/learn/experiments", methods=["GET"])
def learn_experiments():
    """学生端：列出本人已加入课程下的实验及自己的提交状态。"""
    user = require_login()
    if not user or user["role"] != "student":
        return deny()
    sid = user["id"]
    enrolled = set(db_student_course_ids(sid))
    result = []
    for e in EXPERIMENTS:
        if e["course"] not in enrolled:
            continue
        sub = e["submissions"].get(sid, {"status": "pending", "score": None, "feedback": "",
                                         "content": "", "image": None, "file": None, "file_name": None, "submitted_at": None})
        result.append({"id": e["id"], "course": course_by_id(e["course"])["name"],
                       "title": e["title"], "desc": e["desc"], "due": e["due"], **sub})
    return jsonify({"code": 0, "data": result})


@api_bp.route("/learn/experiments/submit", methods=["POST"])
def submit_experiment():
    """学生提交实验：可附带文字说明与图片；状态改为 submitted 并通知教师。"""
    user = require_login()
    if not user or user["role"] != "student":
        return deny()
    data = request.get_json(silent=True, force=True) or {}
    eid = data.get("exp_id")
    sid = user["id"]
    for e in EXPERIMENTS:
        if e["id"] == eid:
            if e["course"] not in set(db_student_course_ids(sid)):
                return jsonify({"code": 1, "msg": "你未加入该课程"})
            sub = e["submissions"].setdefault(sid, {"status": "pending", "score": None,
                                                    "feedback": "", "content": "", "image": None, "file": None, "file_name": None, "submitted_at": None})
            with DATA_LOCK:
                sub["status"] = "submitted"
                sub["content"] = data.get("content", "") or sub.get("content", "")
                sub["image"] = data.get("image") or sub.get("image")
                sub["file"] = data.get("file") or sub.get("file")
                sub["file_name"] = data.get("file_name") or sub.get("file_name")
                sub["submitted_at"] = now_str()
            append_record(sid, e["course"], "提交实验", e["title"], 20)
            add_notification("实验待批改", f"{user['name']} 提交了《{e['title']}》", "experiment")
            _persist()
            return jsonify({"code": 0, "msg": "提交成功，等待教师批改"})
    return jsonify({"code": 1, "msg": "实验不存在"})


@api_bp.route("/teach/analytics", methods=["GET"])
def teach_analytics():
    """学情分析：返回班级/学生/课程/知识点多维度数据，支持前端重做为清晰可筛选的学情看板。"""
    user = require_login()
    if not user or user["role"] != "teacher":
        return deny()
    my_courses = [c for c in COURSES if c["teacher"] == user["username"]]
    my_students = set()
    for c in my_courses:
        my_students.update(db_course_student_ids(c["id"]))
    my_students = sorted(my_students)

    # 兼容“新注册、尚无掌握度数据”的学生：默认值取 0
    points = list(next(iter(MASTERY.values())).keys())
    class_avg = [round(sum(MASTERY.get(s, {}).get(p, 0) for s in my_students) / max(len(my_students), 1)) for p in points]

    # 班级薄弱知识点 TOP（平均掌握度 < 60 且薄弱人数 > 0）
    weak_global = {}
    for p in points:
        vals = [MASTERY.get(s, {}).get(p, 0) for s in my_students]
        avg = round(sum(vals) / max(len(vals), 1))
        weak_count = sum(1 for v in vals if v < 60)
        if weak_count > 0:
            weak_global[p] = {"avg": avg, "count": weak_count}
    weak_global_sorted = sorted(weak_global.items(), key=lambda x: x[1]["avg"])[:8]

    students = []
    for sid in my_students:
        u = db_get_user_by_id(sid)
        m = MASTERY.get(sid, {})
        overall_avg = round(sum(m.values()) / max(len(m), 1)) if m else 0
        weak_count = sum(1 for v in m.values() if v < 60)
        # 无有效学习数据（尚未产生任何掌握度记录）单独标记，避免全 0 分显示“良好”
        if not m or overall_avg == 0:
            risk_level = "未评估"
        elif overall_avg < 40 or weak_count >= 6:
            risk_level = "高危"
        elif overall_avg < 60 or weak_count >= 3:
            risk_level = "预警"
        else:
            risk_level = "良好"

        courses = []
        for c in my_courses:
            if sid not in db_course_student_ids(c["id"]):
                continue
            cpoints = []
            for ch in c["chapters"]:
                cpoints.extend(ch["points"])
            vals = [m.get(p, 0) for p in cpoints if p in m]
            avg = round(sum(vals) / max(len(vals), 1)) if vals else 0
            weak_pts = [p for p in cpoints if m.get(p, 0) < 60]
            courses.append({
                "course_id": c["id"], "course_name": c["name"], "color": c["color"],
                "avg": avg, "progress": db_student_progress(sid, c["id"]),
                "weak_points": weak_pts[:5],
            })

        students.append({
            "id": sid,
            "name": u["name"] if u else sid,
            "avatar": u.get("avatar", "") if u else "",
            "overall_avg": overall_avg,
            "weak_count": weak_count,
            "risk_level": risk_level,
            "courses": courses,
            "mastery": [{"point": p, "value": m.get(p, 0)} for p in points],
        })

    return jsonify({"code": 0, "data": {
        "points": points,
        "class_avg": class_avg,
        "students": students,
        "weak_global": [{"point": k, **v} for k, v in weak_global_sorted],
        "summary": {
            "total": len(my_students),
            "at_risk": sum(1 for s in students if s["risk_level"] in ("高危", "预警")),
            "unassessed": sum(1 for s in students if s["risk_level"] == "未评估"),
            "class_overall_avg": round(sum(s["overall_avg"] for s in students) / max(len(students), 1)),
            "total_weak_points": len(weak_global),
        },
    }})


# ---------------------------------------------------------------------------
# 公共模块：知识图谱 / 成长 / 个人中心
# ---------------------------------------------------------------------------
@api_bp.route("/knowledge-graph", methods=["GET"])
def knowledge_graph():
    user = require_login()
    if not user:
        return deny()
    return jsonify({"code": 0, "data": KNOWLEDGE_GRAPH})


@api_bp.route("/growth", methods=["GET"])
def growth():
    user = require_login()
    if not user:
        return deny()
    sid = user["id"] if user["role"] == "student" else "S001"  # 教师查看示范学生
    g = GROWTH.get(sid, {})
    m = MASTERY.get(sid, {})
    # 学习热力图：生成近 18 周（126 天）活跃度
    import random
    random.seed(hash(sid))
    heat = [{"date": f"2026-{ (i//7)+1 :02d}-{(i%7)+1:02d}", "value": random.randint(0, 9)} for i in range(126)]
    return jsonify({"code": 0, "data": {
        "tags": g.get("tags", []),
        "theory": g.get("theory", 0), "practice": g.get("practice", 0),
        "recommendations": g.get("recommendations", []),
        "timeline": g.get("timeline", []),
        "ai_advice": g.get("ai_advice", ""),
        "mastery": [{"name": k, "value": v} for k, v in m.items()],
        "heatmap": heat,
    }})


@api_bp.route("/profile", methods=["GET", "POST"])
def profile():
    user = require_login()
    if not user:
        return deny()
    sid = user["id"]

    # 写操作：更新资料（昵称 / 邮箱 / 简介 / 头像 / 消息免打扰），头像持久化到数据库
    if request.method == "POST":
        d = request.get_json(silent=True, force=True) or {}
        fields = {}
        if "name" in d:
            fields["name"] = (d["name"] or "").strip()[:40]
        if "email" in d:
            fields["email"] = (d["email"] or "").strip()[:80]
        if "intro" in d:
            fields["intro"] = (d["intro"] or "")[:300]
        if "avatar" in d:
            av = d.get("avatar") or ""
            # 仅接受约定格式：空（默认）/ emoji: / data:image / 外链
            if av == "" or av.startswith("emoji:") or av.startswith("data:image/") \
               or (av.startswith("http://") or av.startswith("https://")):
                fields["avatar"] = av[:4_000_000] if av.startswith("data:image/") else av[:500]
        if "do_not_disturb" in d:
            fields["do_not_disturb"] = 1 if d.get("do_not_disturb") else 0
        updated = db_update_profile(sid, fields)
        return jsonify({"code": 0, "user": public_user(updated)})

    return jsonify({"code": 0, "data": {
        "user": public_user(user),
        "history": AI_HISTORY.get(sid, AI_HISTORY.get("T001", [])),
        "favorites": FAVORITES.get(sid, []),
        "notifications": [n for n in NOTIFICATIONS if (n.get("target") in (None, user["username"]))],
    }})


@api_bp.route("/notifications", methods=["GET"])
def notifications():
    user = require_login()
    if not user:
        return deny()
    # 返回“全局通知” + “定向推送给当前用户”的通知（实现教师发布作业 -> 学生即时收到）
    uname = user["username"]
    data = [n for n in NOTIFICATIONS if (n.get("target") in (None, uname))]
    return jsonify({"code": 0, "data": data})


# ===========================================================================
# 以下为【写操作】接口：让演示具备真实业务闭环（数据写入内存，全端即时可见）
# 覆盖：作业提交 → 教师批改 → 学情联动；测验 → 掌握度更新；AI 对话长期记忆；
#       学习行为自动记录；收藏 / 通知 / 课程 / 实验的可交互管理
# ===========================================================================

@api_bp.route("/upload", methods=["POST"])
def upload_file():
    """文件上传：字节存入 SQLite（files 表），返回数据库文件 id 的下载 URL（带权限校验）。"""
    user = require_login()
    if not user:
        return deny()
    f = request.files.get("file")
    if not f or not f.filename:
        return jsonify({"code": 1, "msg": "未收到文件"})
    ext = f.filename.rsplit(".", 1)[-1].lower() if "." in f.filename else ""
    if ext not in ALLOWED_IMG | ALLOWED_DOC:
        return jsonify({"code": 1, "msg": "仅支持图片或实验报告文件（png/jpg/pdf/word/ppt/xls/zip 等）"})
    data = f.read()
    mime = f.mimetype or "application/octet-stream"
    # 落入数据库，返回 /api/files/<id> 下载链接（前端直接用于 <img src> 与 <a href>）
    fid = db_insert_file(
        owner=user["id"], role=user["role"], course_id=request.form.get("course_id") or "",
        kind=("image" if ext in ALLOWED_IMG else "doc"),
        original_name=(f.filename or f"file.{ext}").replace("\\", "/").split("/")[-1],
        mime=mime, data=data,
    )
    return jsonify({"code": 0, "url": "/api/files/" + fid, "file_id": fid, "name": f.filename})


@api_bp.route("/files/<fid>", methods=["GET"])
def serve_file(fid):
    """数据库文件下载/预览：需登录；仅上传者本人或教师可访问（权限隔离，避免公开 URL 任意下载）。"""
    user = require_login()
    if not user:
        return deny()
    rec = db_get_file(fid)
    if not rec:
        return jsonify({"code": 1, "msg": "文件不存在"}), 404
    # 权限：本人 或 教师（教师需查看/下载学生提交的作业与实验报告）
    if user["id"] != rec["owner"] and user["role"] != "teacher":
        return jsonify({"code": 1, "msg": "无权访问该文件"}), 403
    mime = rec["mime"] or "application/octet-stream"
    disp = "inline" if (mime.startswith("image/")) else "attachment"
    name = rec["original_name"] or "download"
    headers = {
        "Content-Type": mime,
        "Content-Disposition": f'{disp}; filename="{_urlquote(name)}"; filename*=UTF-8\'\'{_urlquote(name)}',
        "Content-Length": str(len(rec["data"])),
        "Cache-Control": "no-store",
    }
    return Response(rec["data"], headers=headers)


@api_bp.route("/learn/homework/submit", methods=["POST"])
def submit_homework():
    """学生提交作业：可附带图片；状态改为 submitted，并写入学习行为与教师通知。"""
    user = require_login()
    if not user or user["role"] != "student":
        return deny()
    data = request.get_json(silent=True, force=True) or {}
    hw_id = data.get("hw_id")
    sid = user["id"]
    for h in HOMEWORK:
        if h["id"] == hw_id:
            sub = h["submissions"].setdefault(sid, {"status": "pending", "score": None, "feedback": "", "image": None})
            sub["status"] = "submitted"
            sub["score"] = None
            sub["feedback"] = ""
            sub["image"] = data.get("image") or None   # 学生上传的作业图片 URL
            append_record(sid, h["course"], "提交作业", h["title"], 20)
            add_notification("作业待批改", f"{user['name']} 提交了《{h['title']}》", "homework")
            return jsonify({"code": 0, "msg": "提交成功，等待教师批改"})
    return jsonify({"code": 1, "msg": "作业不存在"})


@api_bp.route("/teach/submissions", methods=["GET"])
def teach_submissions():
    """教师查看全部作业提交情况（批改工作台数据源，含学生上传的图片）。"""
    user = require_login()
    if not user or user["role"] != "teacher":
        return deny()
    hw_id = request.args.get("hw_id")
    result = []
    for h in HOMEWORK:
        if hw_id and h["id"] != hw_id:
            continue
        c = course_by_id(h["course"])
        for sid, sub in h["submissions"].items():
            u = db_get_user_by_id(sid)
            result.append({
                "hw_id": h["id"], "hw": h["title"], "course": c["name"] if c else "",
                "student_id": sid, "student": u["name"] if u else sid,
                "status": sub["status"], "score": sub["score"], "feedback": sub.get("feedback", ""),
                "image": sub.get("image"),
            })
    return jsonify({"code": 0, "data": result})


@api_bp.route("/teach/grade", methods=["POST"])
def grade_homework():
    """
    教师批改作业：写入分数与评语，并把评价结果反哺知识掌握度。
    这一步让学生端「作业」与「成长模块 / 学情分析」即时联动。
    """
    user = require_login()
    if not user or user["role"] != "teacher":
        return deny()
    d = request.get_json(silent=True, force=True) or {}
    hw_id, sid = d.get("hw_id"), d.get("student_id")
    score, fb = d.get("score"), d.get("feedback", "")
    if score is None:
        return jsonify({"code": 1, "msg": "请填写分数"})
    for h in HOMEWORK:
        if h["id"] == hw_id and sid in h["submissions"]:
            with DATA_LOCK:
                sub = h["submissions"][sid]
                sub["status"] = "graded"; sub["score"] = score; sub["feedback"] = fb  # 保留已上传图片
            append_record(sid, h["course"], "作业批改", f"《{h['title']}》得分 {score}", 0)
            # 评价反哺知识画像：把该课程前若干知识点向本次得分平滑收敛
            c = course_by_id(h["course"])
            pts = []
            for ch in c["chapters"]:
                pts.extend(ch["points"])
            update_mastery(sid, {p: int(score) for p in pts[:6] if p in MASTERY.get(sid, {})})
            add_notification("作业已批改", f"《{h['title']}》已批改，得分 {score}", "homework")
            return jsonify({"code": 0, "msg": "批改完成，学情已同步更新"})
    return jsonify({"code": 1, "msg": "未找到该提交"})


@api_bp.route("/learn/quiz/submit", methods=["POST"])
def submit_quiz():
    """
    学生提交测验：判分 → 逐知识点分析 → 实时更新掌握度 → 写入成长轨迹。
    这是「评价结果驱动知识画像演进」的关键闭环。
    """
    user = require_login()
    if not user or user["role"] != "student":
        return deny()
    d = request.get_json(silent=True, force=True) or {}
    qid = d.get("quiz_id")
    answers = d.get("answers") or {}
    sid = user["id"]
    quiz = next((q for q in QUIZZES if q["id"] == qid), None)
    if not quiz:
        return jsonify({"code": 1, "msg": "测验不存在"})

    correct = 0
    points = []
    for i, q in enumerate(quiz["questions"]):
        a = answers.get(str(i), answers.get(i, -1))
        ok = (a == q["answer"])
        if ok:
            correct += 1
        points.append({"name": q["point"], "val": 100 if ok else 40})
    score = round(correct * 100 / max(len(quiz["questions"]), 1))

    # AI 实时更新知识掌握度
    update_mastery(sid, {p["name"]: p["val"] for p in points})
    append_record(sid, quiz["course"], "完成测验", f"{quiz['title']} {score} 分", 12)
    append_timeline(sid, now_str().split(" ")[0], "quiz", f"{quiz['title']} 得分 {score}")

    return jsonify({"code": 0, "data": {
        "score": score, "correct": correct, "total": len(quiz["questions"]),
        "points": points, "msg": "AI 已根据本次测验更新你的知识掌握度",
    }})


@api_bp.route("/ai/chat", methods=["POST"])
def ai_chat():
    """保存一问一答到历史对话 —— 体现『长期记忆 Long-term Memory』原则。"""
    user = require_login()
    if not user:
        return deny()
    d = request.get_json(silent=True, force=True) or {}
    now = now_str()
    with DATA_LOCK:
        hist = AI_HISTORY.setdefault(user["id"], [])
        hist.append({"role": "user", "text": d.get("text", ""), "time": now})
        hist.append({"role": "ai", "text": d.get("answer", ""), "time": now})
    save_runtime_state()
    return jsonify({"code": 0, "msg": "已存入长期记忆"})


@api_bp.route("/ai/generate", methods=["POST"])
def ai_generate():
    """统一 AI 生成入口（前端 PM.callAI 调用）。
    支持两种返回：
      - stream=true：SSE 流式（text/event-stream），逐块 data: {"chunk": "..."}，结尾 data: {"done": true}
      - 否则：JSON {"code":0, "text": "..."}
    底层由 llm.generate 分发：默认 Mock，配置环境变量即切换本地部署大模型。
    """
    user = require_login()
    if not user:
        return deny()
    d = request.get_json(silent=True, force=True) or {}
    task = d.get("task", "answer")
    params = d.get("params", {}) or {}
    stream = bool(d.get("stream", False))

    # 非流式：直接返回完整文本（便于调试 / 简单客户端）
    if not stream:
        try:
            text, sources = llm_generate_with_sources(task, params)
            return jsonify({"code": 0, "text": text, "sources": sources})
        except Exception as e:
            return jsonify({"code": -1, "msg": "AI 生成失败：" + str(e)})

    # 流式：后端分块推送，营造“大模型生成中”的真实感（Mock 与真实模型统一走此通道）
    def gen():
        try:
            text, sources = llm_generate_with_sources(task, params)
        except Exception as e:
            yield "data: " + json.dumps({"error": str(e)}, ensure_ascii=False) + "\n\n"
            return
        # 按字符切片推送（约 40 段），对中文友好
        step = max(1, len(text) // 40)
        i = 0
        while i < len(text):
            chunk = text[i:i + step]
            yield "data: " + json.dumps({"chunk": chunk}, ensure_ascii=False) + "\n\n"
            i += step
        # 真实知识来源（正式 RAG 命中时才有；前端据此渲染“知识来源”面板）
        if sources:
            yield "data: " + json.dumps({"sources": sources}, ensure_ascii=False) + "\n\n"
        yield "data: " + json.dumps({"done": True}, ensure_ascii=False) + "\n\n"

    return Response(
        stream_with_context(gen()),
        mimetype="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no", "Connection": "keep-alive"},
    )


@api_bp.route("/knowledge/source", methods=["POST"])
def knowledge_source_detail():
    """
    知识来源详情（点击 AI 回答下方的“知识来源”时按需拉取）。

    请求：

        {
            "query":    "原始问题",
            "document": "来源文档（正式 RAG 返回的 document）",
            "score":    0.5531,          # 可选，用于精确匹配同文档的多个片段
            "index":    2,               # 可选，匹配不到文档时按序号兜底
            "course":   "Python 程序设计"  # 可选，用于课程/章节归属推断
        }

    返回：

        {"code": 0, "source": {真实知识片段字段}}

    说明：一律以正式 AI Core（POST /api/rag/search）的真实返回为准，
    不补造文档名、课程名、章节或内容。
    """

    user = require_login()
    if not user:
        return deny()

    d = request.get_json(silent=True, force=True) or {}
    query = (d.get("query") or "").strip()
    document = (d.get("document") or "").strip()

    if not query or not document:
        return jsonify({"code": 1, "msg": "缺少原始问题或来源文档"})

    chunk = find_rag_chunk(
        query,
        document,
        score=d.get("score"),
        index=d.get("index"),
        course=(d.get("course") or "").strip(),
    )

    if not chunk:
        return jsonify({"code": 1, "msg": "未取到该知识片段（知识库可能已更新）"})

    return jsonify({"code": 0, "source": chunk})


@api_bp.route("/profile/favorite", methods=["POST"])
def toggle_favorite():
    """收藏 / 取消收藏（AI 回答、资料、实验均可收藏）。"""
    user = require_login()
    if not user:
        return deny()
    d = request.get_json(silent=True, force=True) or {}
    sid = user["id"]
    favs = FAVORITES.setdefault(sid, [])
    if d.get("action") == "add":
        with DATA_LOCK:
            favs.insert(0, {
                "id": "F" + str(len(favs) + 1),
                "title": d.get("title", ""), "type": d.get("type", "收藏"),
                "course": d.get("course", ""),
            })
        save_runtime_state()
        return jsonify({"code": 0, "msg": "已收藏", "data": favs})
    favs = [f for f in favs if f.get("id") != d.get("id")]
    FAVORITES[sid] = favs
    save_runtime_state()
    return jsonify({"code": 0, "msg": "已取消收藏", "data": favs})


@api_bp.route("/notifications/read", methods=["POST"])
def read_notification():
    """标记通知已读（支持 id='all' 一键全部已读）。"""
    user = require_login()
    if not user:
        return deny()
    d = request.get_json(silent=True, force=True) or {}
    nid = d.get("id")
    for n in NOTIFICATIONS:
        if nid == "all" or n.get("id") == nid:
            n["read"] = True
    save_runtime_state()
    return jsonify({"code": 0, "msg": "已标记已读"})


@api_bp.route("/teach/courses", methods=["POST"])
def create_course():
    """教师创建课程：真实写入 COURSES，教师课程列表即时刷新。"""
    user = require_login()
    if not user or user["role"] != "teacher":
        return deny()
    d = request.get_json(silent=True, force=True) or {}
    name = (d.get("name") or "").strip()
    if not name:
        return jsonify({"code": 1, "msg": "请填写课程名称"})
    cid = "C" + str(len(COURSES) + 1).zfill(3)
    colors = ["#165DFF", "#36CFC9", "#722ED1", "#FF7D00"]
    with DATA_LOCK:
        COURSES.append({
            "id": cid, "code": d.get("code") or ("CS" + str(len(COURSES) + 1)), "name": name,
            "teacher": user["username"], "color": colors[len(COURSES) % len(colors)],
            "cover": "https://picsum.photos/seed/" + cid + "/640/360",
            "textbook": "/assets/textbooks/default.svg",
            "description": d.get("desc") or "教师自建课程（演示）",
            "students": [], "chapters": [],
        })
    add_notification("课程已创建", f"《{name}》已创建", "course")
    return jsonify({"code": 0, "msg": "课程创建成功"})


@api_bp.route("/learn/record", methods=["POST"])
def learn_record():
    """
    通用学习行为采集：AI 提问 / 运行代码 / 查看资料 等均可调用。
    支撑『记录完整学习过程，而不只记录考试结果』这一核心创新点。
    """
    user = require_login()
    if not user:
        return deny()
    d = request.get_json(silent=True, force=True) or {}
    sid = user["id"] if user["role"] == "student" else "S001"
    append_record(sid, d.get("course") or "", d.get("action") or "学习行为",
                  d.get("detail") or "", int(d.get("duration") or 10))
    return jsonify({"code": 0, "msg": "已记录学习行为"})


# ===========================================================================
# 课程广场 / 选课中心：新学生注册后即可浏览全部课程并加入，享受学习资源
# ===========================================================================
@api_bp.route("/courses/catalog", methods=["GET"])
def courses_catalog():
    """返回全部课程（课程广场用），含是否已加入、选课人数，供学生选课。"""
    user = require_login()
    if not user:
        return deny()
    sid = user["id"] if user["role"] == "student" else None
    enrolled = set(db_student_course_ids(sid)) if sid else set()
    # 按当前学生专业计算“核心课 / 推荐课”标记，用于课程广场高亮
    major = user.get("major", "") if sid else ""
    mapping = MAJOR_COURSES.get(major, {})
    rec_ids = set(mapping.get("recommend", []))
    core_ids = set(mapping.get("core", []))
    data = []
    for c in COURSES:
        stu_ids = db_course_student_ids(c["id"])
        data.append({
            "id": c["id"], "name": c["name"], "code": c["code"], "cover": c["cover"],
            "textbook": c["textbook"], "color": c["color"], "description": c["description"],
            "teacher": db_get_user_by_username(c["teacher"])["name"] if db_get_user_by_username(c["teacher"]) else c["teacher"],
            "student_count": len(stu_ids),
            "enrolled": c["id"] in enrolled,
            "progress": db_student_progress(sid, c["id"]) if sid else 0,
            # 是否为该专业“核心课”（注册时已自动加入）或“推荐课”（展示为你推荐）
            "core": c["id"] in core_ids,
            "recommended": c["id"] in rec_ids and c["id"] not in enrolled,
        })
    return jsonify({"code": 0, "data": data, "major": major})


@api_bp.route("/learn/enroll", methods=["POST"])
def enroll_course():
    """学生加入课程：写入 enrollments 表，加入后该课程出现在『我的课程』且可访问作业/资料。"""
    user = require_login()
    if not user or user["role"] != "student":
        return deny()
    d = request.get_json(silent=True, force=True) or {}
    cid = d.get("course_id")
    if not course_by_id(cid):
        return jsonify({"code": 1, "msg": "课程不存在"})
    is_new = db_enroll(user["id"], cid)
    if is_new:
        # 全过程记录：选课本身是一个学习行为
        append_record(user["id"], cid, "加入课程", "加入《" + course_by_id(cid)["name"] + "》", 2)
    return jsonify({"code": 0, "msg": "已加入课程，快去学习吧！" if is_new else "你已在该课程中"})


@api_bp.route("/courses/majors", methods=["GET"])
def courses_majors():
    """返回全部可选专业列表，供注册表单下拉选择。"""
    return jsonify({"code": 0, "data": MAJORS})


@api_bp.route("/courses/recommend", methods=["GET"])
def courses_recommend():
    """
    按当前学生专业返回【为你推荐】的课程（相关专业拓展课，且尚未加入）。
    与“注册自动加入核心课”形成互补：核心课默认选，推荐课引导手动选。
    """
    user = require_login()
    if not user or user["role"] != "student":
        return deny()
    sid = user["id"]
    major = user.get("major", "")
    mapping = MAJOR_COURSES.get(major, {})
    enrolled = set(db_student_course_ids(sid))
    data = []
    for cid in mapping.get("recommend", []):
        c = course_by_id(cid)
        if c and c["id"] not in enrolled:
            stu_ids = db_course_student_ids(c["id"])
            data.append({
                "id": c["id"], "name": c["name"], "code": c["code"], "cover": c["cover"],
                "textbook": c["textbook"], "color": c["color"], "description": c["description"],
                "teacher": db_get_user_by_username(c["teacher"])["name"] if db_get_user_by_username(c["teacher"]) else c["teacher"],
                "student_count": len(stu_ids),
                "enrolled": False, "progress": 0, "core": False, "recommended": True,
            })
    return jsonify({"code": 0, "data": data, "major": major})


# ---------------------------------------------------------------------------
# 题库 / 测验中心：教师上传题目、学生导入题库并自测
# ---------------------------------------------------------------------------
def _valid_question(q):
    """校验单道题格式是否合法。"""
    if not isinstance(q, dict):
        return False
    if not (q.get("q") or "").strip():
        return False
    opts = q.get("options") or []
    if not isinstance(opts, list) or len(opts) < 2:
        return False
    ans = q.get("answer")
    if not isinstance(ans, int) or ans < 0 or ans >= len(opts):
        return False
    return True


@api_bp.route("/learn/quizzes", methods=["GET"])
def learn_quizzes():
    """学生测验中心：列出自己可做的全部测验（系统默认 + 教师创建 + 自建题库）。"""
    user = require_login()
    if not user or user["role"] != "student":
        return deny()
    sid = user["id"]
    enrolled = set(db_student_course_ids(sid))
    data = []
    for q in QUIZZES:
        cid = q.get("course")
        # 系统/教师题库：仅对已加入课程可见；自建题库：仅自己可见
        if q.get("source") == "student" and q.get("created_by") != sid:
            continue
        if q.get("source") in ("system", "teacher") and cid not in enrolled:
            continue
        data.append({
            "id": q["id"], "course": cid, "title": q["title"],
            "source": q.get("source", "system"),
            "question_count": len(q.get("questions", [])),
        })
    return jsonify({"code": 0, "data": data})


@api_bp.route("/teach/quiz", methods=["GET", "POST"])
def teach_quiz():
    """教师题库管理：GET 列本人创建的测验；POST 创建新测验并推送给选课学生。"""
    user = require_login()
    if not user or user["role"] != "teacher":
        return deny()
    if request.method == "POST":
        d = request.get_json(silent=True, force=True) or {}
        cid = d.get("course_id")
        title = (d.get("title") or "").strip()
        questions = d.get("questions") or []
        questions = [q for q in questions if _valid_question(q)]
        if not cid or not title:
            return jsonify({"code": 1, "msg": "请选择课程并填写测验标题"})
        if len(questions) < 1:
            return jsonify({"code": 1, "msg": "请至少添加 1 道题目"})
        c = course_by_id(cid)
        if not c or c["teacher"] != user["username"]:
            return jsonify({"code": 1, "msg": "课程不存在或无权限"})
        qid = "Q" + str(len(QUIZZES) + 1).zfill(3)
        with DATA_LOCK:
            QUIZZES.append({
                "id": qid, "course": cid, "title": title,
                "source": "teacher", "created_by": user["username"],
                "questions": questions,
            })
        # 向选课学生推送“新测验”通知
        for sid in db_course_student_ids(cid):
            u = db_get_user_by_id(sid)
            if u:
                add_notification("新测验可练习", f"《{title}》已发布，快去测验中心练习吧", "quiz", target=u["username"])
        return jsonify({"code": 0, "msg": "测验已发布，学生可在测验中心看到", "quiz_id": qid})

    # GET：教师本人创建的全部测验
    data = [{
        "id": q["id"], "course": q.get("course"), "title": q["title"],
        "question_count": len(q.get("questions", [])),
    } for q in QUIZZES if q.get("source") == "teacher" and q.get("created_by") == user["username"]]
    return jsonify({"code": 0, "data": data})


@api_bp.route("/learn/quiz/import", methods=["POST"])
def learn_quiz_import():
    """学生导入题库：支持单题添加或 JSON 批量导入，生成仅自己可见的测验。"""
    user = require_login()
    if not user or user["role"] != "student":
        return deny()
    d = request.get_json(silent=True, force=True) or {}
    title = (d.get("title") or "").strip() or "我的导入题库"
    questions = d.get("questions") or []
    questions = [q for q in questions if _valid_question(q)]
    if not questions:
        return jsonify({"code": 1, "msg": "没有合法题目，请检查格式"})
    qid = "Q" + str(len(QUIZZES) + 1).zfill(3)
    with DATA_LOCK:
        QUIZZES.append({
            "id": qid, "course": d.get("course") or "", "title": title,
            "source": "student", "created_by": user["id"],
            "questions": questions,
        })
    save_runtime_state()
    return jsonify({"code": 0, "msg": f"成功导入 {len(questions)} 道题目", "quiz_id": qid})
