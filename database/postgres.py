"""
ProgramMind

PostgreSQL业务数据库管理

保存:

1. 用户信息
2. 学习行为
3. 数字孪生数据
4. 课程信息

数据库:

PostgreSQL

配置:

POSTGRES_HOST / POSTGRES_PORT / POSTGRES_DB /
POSTGRES_USER / POSTGRES_PASSWORD（.env 或环境变量）
"""

import logging
import os

import psycopg2

from dotenv import load_dotenv
from psycopg2.extras import RealDictCursor


load_dotenv()


logger = logging.getLogger(__name__)


class PostgreSQLManager:

    def __init__(
        self,
        host=None,
        port=None,
        database=None,
        user=None,
        password=None
    ):
        """
        初始化数据库配置。

        优先使用显式传入参数，未传入时从环境变量读取
        （默认值与原硬编码保持一致）。
        """

        self.config = {
            "host": host or os.getenv("POSTGRES_HOST", "localhost"),
            "port": int(port or os.getenv("POSTGRES_PORT", "5432")),
            "database": database or os.getenv("POSTGRES_DB", "programmind"),
            "user": user or os.getenv("POSTGRES_USER", "postgres"),
            "password": (
                password
                if password is not None
                else os.getenv("POSTGRES_PASSWORD", "123456")
            )
        }

        self.conn = None

    # =====================
    # 数据库连接
    # =====================

    def connect(self):
        """
        建立数据库连接。

        连接失败时抛出 ConnectionError（不再返回 None，
        避免调用方拿着 None 继续执行导致难排查的崩溃）。
        """

        try:
            self.conn = psycopg2.connect(**self.config)
            print("PostgreSQL连接成功")
            return self.conn

        except Exception as e:
            logger.exception("PostgreSQL 连接失败")
            raise ConnectionError(f"PostgreSQL 数据库连接失败：{e}") from e

    def _check_connection(self):
        """
        确保连接有效，未连接时自动连接。
        """

        if self.conn is None or self.conn.closed:
            self.connect()

    # =====================
    # 创建数据表
    # =====================

    def create_tables(self):
        """
        创建ProgramMind业务表
        """

        sql = """
        CREATE TABLE IF NOT EXISTS students(
            id SERIAL PRIMARY KEY,
            student_id VARCHAR(100),
            name VARCHAR(100),
            kci FLOAT,
            profile JSONB
        );

        CREATE TABLE IF NOT EXISTS courses(
            id SERIAL PRIMARY KEY,
            course_id VARCHAR(100),
            name VARCHAR(200),
            description TEXT
        );

        CREATE TABLE IF NOT EXISTS learning_records(
            id SERIAL PRIMARY KEY,
            student_id VARCHAR(100),
            knowledge VARCHAR(200),
            score FLOAT,
            create_time TIMESTAMP DEFAULT NOW()
        );
        """

        self._check_connection()

        cursor = self.conn.cursor()

        try:
            cursor.execute(sql)
            self.conn.commit()
        except Exception as e:
            self.conn.rollback()
            logger.exception("创建业务表失败")
            raise RuntimeError(f"创建业务表失败：{e}") from e
        finally:
            cursor.close()

        print("业务表创建完成")

    # =====================
    # 保存学生画像
    # =====================

    def save_student_profile(
        self,
        student_id,
        name,
        kci,
        profile
    ):
        sql = """
        INSERT INTO students
        (student_id, name, kci, profile)
        VALUES (%s,%s,%s,%s)
        """

        self._check_connection()

        cursor = self.conn.cursor()

        try:
            cursor.execute(
                sql,
                (student_id, name, kci, profile)
            )
            self.conn.commit()
        except Exception as e:
            self.conn.rollback()
            logger.exception("保存学生画像失败")
            raise RuntimeError(f"保存学生画像失败：{e}") from e
        finally:
            cursor.close()

    # =====================
    # 查询学生
    # =====================

    def get_student(
        self,
        student_id
    ):
        sql = """
        SELECT *
        FROM students
        WHERE student_id=%s
        """

        self._check_connection()

        cursor = self.conn.cursor(
            cursor_factory=RealDictCursor
        )

        try:
            cursor.execute(sql, (student_id,))
            return cursor.fetchone()
        except Exception as e:
            logger.exception("查询学生失败")
            raise RuntimeError(f"查询学生失败：{e}") from e
        finally:
            cursor.close()


if __name__ == "__main__":
    db = PostgreSQLManager()
    db.connect()
