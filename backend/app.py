# -*- coding: utf-8 -*-
"""
ProgramMind 后端入口
=====================
职责：
1. 创建 Flask 应用，加载配置
2. 注册蓝图：鉴权(auth) + 业务数据(api)
3. 托管前端 SPA（frontend 目录）：静态资源直接返回，其余路径回退 index.html
   —— 这样“每个页面都有独立 URL 路由”，且无需额外前端构建步骤，开箱即演示

运行方式：
    cd backend
    pip install -r requirements.txt
    python app.py
然后浏览器访问 http://127.0.0.1:5000
"""
import os
import sys

# ============================================================
# 启动即把标准输出 / 标准错误重定向到 logs/demo.log
#
# 背景（已用对照实验复现）：
#   本服务是长驻进程。如果它的输出目标被阻塞 ——
#   控制台窗口处于“标记/选择”冻结状态，或输出管道无人读取且缓冲写满 ——
#   那么任何一次写输出都会永久卡住。
#   而 Werkzeug 在把响应写回客户端之前，会先写一行访问日志到 stderr，
#   于是一旦输出被阻塞，就会出现：
#       端口 LISTENING、进程没崩溃、但任何请求都永远收不到响应。
#
#   把输出落到文件后，请求处理路径不再依赖控制台，不会再被冻死。
#   日志文件：项目根目录 logs/demo.log
#
# 注意：这段必须在 import flask / werkzeug 之前执行，
#       否则 Flask 的默认日志处理器会绑定旧的 sys.stderr。
# ============================================================

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

LOG_DIR = os.path.join(os.path.dirname(BASE_DIR), "logs")

try:

    os.makedirs(LOG_DIR, exist_ok=True)

    _log_stream = open(
        os.path.join(LOG_DIR, "demo.log"),
        "a",
        encoding="utf-8",
        buffering=1,
    )

    sys.stdout = _log_stream
    sys.stderr = _log_stream
    sys.__stdout__ = _log_stream
    sys.__stderr__ = _log_stream

except Exception:

    # 重定向失败时保持原样，绝不影响服务启动
    pass

from flask import Flask, send_from_directory, jsonify
from config import SECRET_KEY, SESSION_COOKIE_NAME, SESSION_COOKIE_HTTPONLY, SESSION_COOKIE_SAMESITE, PERMANENT_SESSION_LIFETIME
from routes_auth import auth_bp
from routes_api import api_bp

# 前端目录绝对路径（backend 的上一级的 frontend）
FRONTEND_DIR = os.path.join(os.path.dirname(BASE_DIR), "frontend")


def create_app():
    app = Flask(
        __name__,
        static_folder=FRONTEND_DIR,      # 静态资源根：frontend/
        static_url_path="/assets",       # 静态资源前缀：/assets/...
        template_folder=os.path.join(BASE_DIR, "templates"),
    )
    app.secret_key = SECRET_KEY
    app.config["SESSION_COOKIE_NAME"] = SESSION_COOKIE_NAME
    app.config["SESSION_COOKIE_HTTPONLY"] = SESSION_COOKIE_HTTPONLY
    app.config["SESSION_COOKIE_SAMESITE"] = SESSION_COOKIE_SAMESITE
    app.config["PERMANENT_SESSION_LIFETIME"] = PERMANENT_SESSION_LIFETIME

    # 注册蓝图
    app.register_blueprint(auth_bp)
    app.register_blueprint(api_bp)

    # ---- SPA 托管：前端资源（/assets/*）由 Flask 静态服务 ----
    # ---- 其余路径（页面路由）统一回退到 index.html，交给前端 Vue Router ----
    @app.route("/", defaults={"path": ""})
    @app.route("/<path:path>")
    def spa(path):
        # 若请求的是真实存在的静态文件（js/css/img），直接返回
        full = os.path.join(FRONTEND_DIR, path)
        if path and os.path.isfile(full):
            return send_from_directory(FRONTEND_DIR, path)
        return send_from_directory(FRONTEND_DIR, "index.html")

    @app.errorhandler(404)
    def not_found(e):
        return send_from_directory(FRONTEND_DIR, "index.html")

    return app


app = create_app()

# 启动时回填运行时业务数据（作业图片 / 批改 / 掌握度 / 通知 / 收藏 / AI 对话等），
# 保证重启后这些"项目记忆"不丢失
from persist import load_runtime_state
load_runtime_state()


if __name__ == "__main__":
    # 演示默认端口 5000；debug 关闭以避免竞赛现场热重载提示
    print("="*60)
    print(" ProgramMind 演示服务已启动（SQLite 数据库已就绪）")
    print(" 浏览器访问: http://127.0.0.1:5000")
    print(" 教师演示账号: teacher01 / teacher01")
    print(" 学生演示账号: student01 / student01")
    print(" 支持注册新账号（注册即写入数据库，新学生可立即选课）")
    print("="*60)
    app.run(host="0.0.0.0", port=5000, debug=False)
