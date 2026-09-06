"""
ProgramMind

PGVector 数据库管理模块

功能：

1. 连接 PostgreSQL
2. 注册 PGVector
3. 管理 knowledge_chunks 表
4. 插入知识片段和 Embedding
5. 向量相似度检索
6. 查询知识库统计信息
7. 创建 HNSW 向量索引

当前环境：

PostgreSQL 18.6
PGVector 0.8.6
数据库：programmind

当前知识表：

knowledge_chunks
"""

import logging
import os

import numpy as np
import psycopg2

from dotenv import load_dotenv
from pgvector.psycopg2 import register_vector


logger = logging.getLogger(__name__)


# ============================================================
# 加载环境变量
# ============================================================

load_dotenv()


class PGVectorManager:
    """
    ProgramMind PGVector 数据库管理器。

    数据流程：

        文本
          ↓
        bge-m3
          ↓
        1024维 Embedding
          ↓
        knowledge_chunks
          ↓
        PGVector 检索
    """

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

        优先使用显式传入参数，
        没有传入时从 .env 读取。

        .env 示例：

            PGVECTOR_HOST=localhost
            PGVECTOR_PORT=5432
            PGVECTOR_DATABASE=programmind
            PGVECTOR_USER=postgres
            PGVECTOR_PASSWORD=714698
        """

        self.config = {
            "host": host or os.getenv(
                "PGVECTOR_HOST",
                "localhost"
            ),

            "port": int(
                port or os.getenv(
                    "PGVECTOR_PORT",
                    "5432"
                )
            ),

            "database": database or os.getenv(
                "PGVECTOR_DATABASE"
            ) or os.getenv(
                "PGVECTOR_DB",
                "programmind"
            ),

            "user": user or os.getenv(
                "PGVECTOR_USER",
                "postgres"
            ),

            "password": (
                password
                if password is not None
                else os.getenv("PGVECTOR_PASSWORD")
            )
        }

        self.conn = None

    # ========================================================
    # 连接数据库
    # ========================================================

    def connect(self):
        """
        连接 PostgreSQL，并注册 PGVector。
        """

        if not self.config["password"]:

            raise ValueError(
                "未找到 PostgreSQL 密码。\n"
                "请在 .env 中配置：\n"
                "PGVECTOR_PASSWORD=你的postgres密码"
            )

        try:

            self.conn = psycopg2.connect(
                **self.config
            )

            # ------------------------------------------------
            # 注册 PostgreSQL vector 类型
            # ------------------------------------------------

            register_vector(
                self.conn
            )

            print(
                "PGVector 连接成功"
            )

            return self.conn

        except Exception as e:

            self.conn = None

            raise ConnectionError(
                f"PGVector 数据库连接失败：{e}"
            ) from e

    # ========================================================
    # 检查数据库连接
    # ========================================================

    def _check_connection(self):
        """
        检查数据库连接是否有效，失效时自动重连一次。

        连接缺失 / 已关闭 / 探活失败 三种情况都会触发重连；
        重连失败会抛出 ConnectionError。
        """

        if self.conn is not None and not self.conn.closed:

            try:

                cursor = self.conn.cursor()

                try:
                    cursor.execute("SELECT 1")
                finally:
                    cursor.close()

                return

            except Exception:

                logger.warning(
                    "PGVector 连接失效，尝试重连",
                    exc_info=True
                )

        self.conn = None

        self.connect()

    # ========================================================
    # 创建知识表
    # ========================================================

    def create_table(self):
        """
        创建 knowledge_chunks 表。

        表结构：

            id
            content
            source
            chunk_id
            embedding
            created_at
        """

        self._check_connection()

        sql = """
        CREATE EXTENSION IF NOT EXISTS vector;

        CREATE TABLE IF NOT EXISTS knowledge_chunks (
            id BIGSERIAL PRIMARY KEY,
            content TEXT NOT NULL,
            source TEXT,
            chunk_id INTEGER,
            embedding vector(1024),
            created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
        );
        """

        cursor = self.conn.cursor()

        try:

            cursor.execute(
                sql
            )

            self.conn.commit()

            print(
                "knowledge_chunks 表检查完成"
            )

        except Exception:

            self.conn.rollback()

            raise

        finally:

            cursor.close()

    # ========================================================
    # 创建 HNSW 索引
    # ========================================================

    def create_index(self):
        """
        创建 HNSW 余弦相似度索引。
        """

        self._check_connection()

        sql = """
        CREATE INDEX IF NOT EXISTS
        knowledge_chunks_embedding_idx
        ON knowledge_chunks
        USING hnsw (embedding vector_cosine_ops);
        """

        cursor = self.conn.cursor()

        try:

            cursor.execute(
                sql
            )

            self.conn.commit()

            print(
                "PGVector HNSW 索引检查完成"
            )

        except Exception:

            self.conn.rollback()

            raise

        finally:

            cursor.close()

    # ========================================================
    # 插入单条知识
    # ========================================================

    def insert(
        self,
        content,
        embedding,
        source=None,
        metadata=None,
        chunk_id=0
    ):
        """
        插入一个知识片段。

        参数：

            content:
                知识文本

            embedding:
                bge-m3 生成的 1024 维向量

            source:
                来源文件

            metadata:
                兼容旧接口

            chunk_id:
                文本块编号
        """

        self._check_connection()

        if not content:

            raise ValueError(
                "content 不能为空"
            )

        if embedding is None:

            raise ValueError(
                "embedding 不能为空"
            )

        # ----------------------------------------------------
        # 转成 float32
        #
        # 这样可以避免 PostgreSQL 将其识别成 numeric[]
        # ----------------------------------------------------

        vector = np.asarray(
            embedding,
            dtype=np.float32
        )

        # ----------------------------------------------------
        # 检查向量维度
        # ----------------------------------------------------

        if vector.ndim != 1:

            raise ValueError(
                "embedding 必须是一维向量"
            )

        if len(vector) != 1024:

            raise ValueError(
                f"Embedding 维度错误："
                f"当前为 {len(vector)}，"
                f"要求为 1024"
            )

        # ----------------------------------------------------
        # 如果 metadata 中包含 chunk_id，
        # 优先使用 metadata
        # ----------------------------------------------------

        if isinstance(
            metadata,
            dict
        ):

            chunk_id = metadata.get(
                "chunk_id",
                chunk_id
            )

        sql = """
        INSERT INTO knowledge_chunks
        (
            content,
            source,
            chunk_id,
            embedding
        )
        VALUES
        (%s, %s, %s, %s)
        RETURNING id;
        """

        cursor = self.conn.cursor()

        try:

            cursor.execute(
                sql,
                (
                    content,
                    source,
                    int(chunk_id),
                    vector
                )
            )

            row = cursor.fetchone()

            self.conn.commit()

            return row[0]

        except Exception:

            self.conn.rollback()

            raise

        finally:

            cursor.close()

    # ========================================================
    # 批量插入
    # ========================================================

    def insert_many(
        self,
        documents
    ):
        """
        批量插入知识片段。

        documents 格式：

        [
            {
                "content": "...",
                "source": "...",
                "chunk_id": 0,
                "embedding": [...]
            }
        ]
        """

        self._check_connection()

        if not documents:

            return 0

        sql = """
        INSERT INTO knowledge_chunks
        (
            content,
            source,
            chunk_id,
            embedding
        )
        VALUES
        (%s, %s, %s, %s);
        """

        cursor = self.conn.cursor()

        count = 0

        try:

            for document in documents:

                content = document.get(
                    "content"
                )

                source = document.get(
                    "source"
                )

                chunk_id = document.get(
                    "chunk_id",
                    0
                )

                embedding = document.get(
                    "embedding"
                )

                if not content:

                    continue

                if embedding is None:

                    continue

                vector = np.asarray(
                    embedding,
                    dtype=np.float32
                )

                if vector.ndim != 1:

                    raise ValueError(
                        f"第 {chunk_id} 个文本块的 "
                        f"Embedding 必须是一维向量"
                    )

                if len(vector) != 1024:

                    raise ValueError(
                        f"第 {chunk_id} 个文本块的 "
                        f"Embedding 维度不是 1024"
                    )

                cursor.execute(
                    sql,
                    (
                        content,
                        source,
                        int(chunk_id),
                        vector
                    )
                )

                count += 1

            self.conn.commit()

            return count

        except Exception:

            self.conn.rollback()

            raise

        finally:

            cursor.close()

    # ========================================================
    # 向量相似度搜索
    # ========================================================

    def search(
        self,
        query_vector,
        top_k=5
    ):
        """
        使用余弦距离进行向量检索。

        参数：

            query_vector:
                用户问题经过 bge-m3 得到的向量

            top_k:
                返回前几个结果

        返回：

        [
            {
                "id": 1,
                "content": "...",
                "source": "...",
                "chunk_id": 0,
                "score": 0.95
            }
        ]
        """

        self._check_connection()

        if query_vector is None:

            raise ValueError(
                "query_vector 不能为空"
            )

        # ----------------------------------------------------
        # 关键修复：
        #
        # Python list
        #       ↓
        # numpy.float32
        #       ↓
        # PGVector
        #
        # 避免 PostgreSQL 将其识别为 numeric[]
        # ----------------------------------------------------

        vector = np.asarray(
            query_vector,
            dtype=np.float32
        )

        # ----------------------------------------------------
        # 检查向量维度
        # ----------------------------------------------------

        if vector.ndim != 1:

            raise ValueError(
                "query_vector 必须是一维向量"
            )

        if len(vector) != 1024:

            raise ValueError(
                f"查询向量维度错误："
                f"{len(vector)}，"
                f"要求 1024"
            )

        # ----------------------------------------------------
        # 检查 top_k
        # ----------------------------------------------------

        if top_k <= 0:

            raise ValueError(
                "top_k 必须大于 0"
            )

        # ----------------------------------------------------
        # 确保连接有效（失效自动重连）
        # ----------------------------------------------------

        self._check_connection()

        sql = """
        SELECT
            id,
            content,
            source,
            chunk_id,
            1 - (embedding <=> %s) AS score
        FROM knowledge_chunks
        ORDER BY embedding <=> %s
        LIMIT %s;
        """

        cursor = self.conn.cursor()

        try:

            cursor.execute(
                sql,
                (
                    vector,
                    vector,
                    int(top_k)
                )
            )

            rows = cursor.fetchall()

            result = []

            for row in rows:

                result.append(
                    {
                        "id": row[0],
                        "content": row[1],
                        "source": row[2],
                        "chunk_id": row[3],
                        "score": float(
                            row[4]
                        )
                    }
                )

            return result

        finally:

            cursor.close()

    # ========================================================
    # 获取知识数量
    # ========================================================

    def count(self):
        """
        获取当前知识库中的文本块数量。
        """

        self._check_connection()

        cursor = self.conn.cursor()

        try:

            cursor.execute(
                """
                SELECT COUNT(*)
                FROM knowledge_chunks
                """
            )

            return cursor.fetchone()[0]

        finally:

            cursor.close()

    # ========================================================
    # 清空知识库
    # ========================================================

    def clear(self):
        """
        清空 knowledge_chunks。

        注意：

        这个操作会删除所有知识数据。
        """

        self._check_connection()

        cursor = self.conn.cursor()

        try:

            cursor.execute(
                "TRUNCATE TABLE knowledge_chunks"
            )

            self.conn.commit()

        except Exception:

            self.conn.rollback()

            raise

        finally:

            cursor.close()

    # ========================================================
    # 关闭数据库连接
    # ========================================================

    def close(self):
        """
        关闭数据库连接。
        """

        if self.conn is not None:

            self.conn.close()

            self.conn = None

            print(
                "PGVector 数据库连接已关闭"
            )


# ============================================================
# 单独测试
# ============================================================

if __name__ == "__main__":

    print("=" * 60)
    print("ProgramMind PGVector 数据库测试")
    print("=" * 60)

    db = PGVectorManager()

    try:

        db.connect()

        print()
        print(
            f"当前知识数量：{db.count()}"
        )

    except Exception as e:

        print()
        print(
            f"数据库测试失败：{e}"
        )

    finally:

        db.close()

    print()
    print("=" * 60)
    print("PGVector 测试结束")
    print("=" * 60)