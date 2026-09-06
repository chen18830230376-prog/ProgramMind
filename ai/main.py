"""
ProgramMind

项目统一启动入口

启动:

    start.bat       生产模式（waitress 同级体验，uvicorn 承载）
    start_dev.bat   开发模式（RELOAD=true 热重载）

配置:

    HOST / PORT / RELOAD 均从 .env 或环境变量读取
"""

import logging
import os
from logging.handlers import RotatingFileHandler

import uvicorn

from dotenv import load_dotenv

from api.ai_api import app


def setup_logging():
    """统一日志配置：控制台 + 滚动文件 logs/programmind.log"""
    os.makedirs("logs", exist_ok=True)
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s %(message)s",
        handlers=[
            logging.StreamHandler(),
            RotatingFileHandler(
                "logs/programmind.log",
                maxBytes=5 * 1024 * 1024,
                backupCount=3,
                encoding="utf-8",
            ),
        ],
    )


def init_system():
    """
    系统初始化

    后续可以加入:

    1. 模型加载
    2. PGVector连接
    3. Redis连接
    4. 数据初始化
    """
    logger = logging.getLogger(__name__)
    logger.info("====================")
    logger.info("ProgramMind AI启动")
    logger.info("====================")
    logger.info("初始化大模型...")
    logger.info("初始化知识库...")
    logger.info("初始化Agent...")
    logger.info("系统准备完成")


if __name__ == "__main__":
    load_dotenv()
    setup_logging()

    HOST = os.getenv("HOST", "0.0.0.0")
    PORT = int(os.getenv("PORT", "8000"))
    RELOAD = os.getenv("RELOAD", "false").lower() in ("1", "true", "yes", "on")

    init_system()

    if RELOAD:
        # reload 模式必须传导入字符串，否则 uvicorn 无法重启子进程
        uvicorn.run("main:app", host=HOST, port=PORT, log_level="info",
                    reload=True)
    else:
        uvicorn.run(app, host=HOST, port=PORT, log_level="info")
