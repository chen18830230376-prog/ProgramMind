# -*- coding: utf-8 -*-
"""
ProgramMind 后端配置模块
================================
说明：本项目为国家级软件竞赛演示项目，刻意不接入任何真实数据库，
全部业务数据使用内存字典（见 mock_data.py）模拟，便于评委/老师一键运行演示。

本文件仅放置 Flask 运行所需的最小配置：
- SECRET_KEY：用于 session 签名（Cookie 安全），演示项目使用固定值即可
- SESSION_COOKIE 相关：保证登录态在浏览器会话中保持
"""
import os

# 演示用密钥（竞赛部署时可替换为环境变量）
SECRET_KEY = os.environ.get("PROGRAMMIND_SECRET", "programmind-demo-secret-key-2026")

# Session 配置：浏览器关闭后失效（演示友好）
PERMANENT_SESSION_LIFETIME = 3600 * 8  # 8 小时
SESSION_COOKIE_NAME = "programmind_session"
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SAMESITE = "Lax"

# 项目元信息（供前端展示 / 接口返回）
PROJECT_NAME = "ProgramMind"
PROJECT_SLOGAN = "面向高校计算机学科的 AI-Native 教学科研垂类大模型平台"
