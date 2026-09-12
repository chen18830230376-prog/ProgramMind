# -*- coding: utf-8 -*-
"""
鉴权蓝图（Auth Blueprint）
=========================
实现：注册 / 登录 / 登出 / 当前用户 四个接口。
- 用户账号真实落库（SQLite），注册写入、登录校验均走数据库
- 使用 Flask session 保存登录态与用户身份（role），满足“会话保持”要求
- 未登录访问受保护接口时返回 401，由前端路由守卫统一跳转登录页
- 登录失败 / 注册失败返回错误信息，前端以消息弹窗 / flash 形式提示
"""
from flask import Blueprint, request, session, jsonify, flash
from db import (
    db_get_user_by_username, db_authenticate, db_register, public_user, db_enroll,
)
from mock_data import MAJOR_COURSES, course_by_id

auth_bp = Blueprint("auth", __name__, url_prefix="/api/auth")


@auth_bp.route("/register", methods=["POST"])
def register():
    """
    注册接口：接收 {username, password, name, role, school, major, grade, email}
    - 账号唯一性校验；成功后写入数据库 users 表
    - 默认角色为 student（新学生），亦支持注册教师账号
    - 返回脱敏用户信息，前端可直接登录该账号
    """
    data = request.get_json(silent=True, force=True) or {}
    username = (data.get("username") or "").strip()
    password = data.get("password") or ""
    name = (data.get("name") or "").strip() or username
    role = data.get("role") or "student"
    if role not in ("student", "teacher"):
        role = "student"

    user, err = db_register(
        username, password, name, role,
        school=(data.get("school") or "").strip(),
        major=(data.get("major") or "").strip(),
        grade=(data.get("grade") or "").strip(),
        email=(data.get("email") or "").strip(),
    )
    if err:
        return jsonify({"code": 1, "msg": err})

    # 注册成功自动写入会话，省去“注册完再登录”的额外步骤
    session["user_id"] = user["id"]
    session["username"] = user["username"]
    session["role"] = user["role"]
    session.permanent = True

    # 学生注册选了专业 -> 按专业自动匹配核心课并写入 enrollments（默认选课）
    # 其余专业相关课作为“为你推荐”，返回前端引导其手动加入
    auto_joined, recommended = [], []
    if user["role"] == "student" and user.get("major"):
        mapping = MAJOR_COURSES.get(user["major"])
        if mapping:
            for cid in mapping.get("core", []):
                if db_enroll(user["id"], cid):           # 幂等，已在则不重复
                    c = course_by_id(cid)
                    if c:
                        auto_joined.append(c["name"])
            for cid in mapping.get("recommend", []):
                c = course_by_id(cid)
                if c:
                    recommended.append(c["name"])

    flash(f"注册成功，欢迎你，{user['name']}！", "success")
    return jsonify({
        "code": 0, "msg": "注册成功，已自动登录",
        "user": public_user(user),
        "auto_joined": auto_joined,   # 已自动加入的核心课名称
        "recommended": recommended,   # 为你推荐（相关专业拓展课）名称
    })


@auth_bp.route("/login", methods=["POST"])
def login():
    """
    登录接口：接收 {username, password, role}
    - 校验账号密码与所选身份是否匹配（防止学生用教师账号登录）
    - 成功写入 session，返回脱敏用户信息
    - 失败返回 code!=0 与 msg，前端弹出友好提示
    """
    data = request.get_json(silent=True, force=True) or {}
    username = (data.get("username") or "").strip()
    password = data.get("password") or ""
    role = data.get("role") or "student"

    user, err = db_authenticate(username, password, role)
    if err:
        return jsonify({"code": 1, "msg": err})

    # 写入会话（session 以签名 Cookie 保存，浏览器关闭前保持）
    session["user_id"] = user["id"]
    session["username"] = user["username"]
    session["role"] = user["role"]
    session.permanent = True

    # flash 消息：演示“登录成功”的服务器侧提示（前端也会 Toast）
    flash(f"欢迎回来，{user['name']}！", "success")
    return jsonify({"code": 0, "msg": "登录成功", "user": public_user(user)})


@auth_bp.route("/logout", methods=["POST"])
def logout():
    """登出：清除会话。"""
    session.clear()
    return jsonify({"code": 0, "msg": "已退出登录"})


@auth_bp.route("/me", methods=["GET"])
def me():
    """
    获取当前登录用户。未登录返回 code=401，前端据此跳转登录页。
    这是“会话保持”的关键：刷新页面后前端调用此接口恢复登录态。
    """
    if "username" not in session:
        return jsonify({"code": 401, "msg": "未登录"}), 401
    user = db_get_user_by_username(session["username"])
    if not user:
        return jsonify({"code": 401, "msg": "未登录"}), 401
    return jsonify({"code": 0, "user": public_user(user)})
