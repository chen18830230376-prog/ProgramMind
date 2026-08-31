"""
ProgramMind

知识库上传模块

流程：

文本
 ↓
bge-m3 Embedding
 ↓
1024维向量
 ↓
PGVector
 ↓
knowledge_chunks
"""

from core.embedding_model import EmbeddingModel
from database.pgvector_db import PGVectorManager


class KnowledgeUploader:
    """
    知识库上传器。

    负责：
    1. 文本 Embedding
    2. 向量写入 PGVector
    """

    def __init__(self):
        """
        初始化 Embedding 和 PGVector。
        """

        print("=" * 60)
        print("初始化知识库上传器")
        print("=" * 60)

        self.embedding = EmbeddingModel()

        self.vector_db = PGVectorManager()

        self.vector_db.connect()

    # ========================================================
    # 上传知识
    # ========================================================

    def upload(self, documents):
        """
        上传知识片段。

        documents 格式：

        [
            {
                "content": "人工智能是一门研究智能机器的学科。",
                "source": "人工智能基础.txt",
                "chunk_id": 0
            }
        ]
        """

        if not documents:

            return {
                "status": "success",
                "count": 0
            }

        uploaded_count = 0

        for doc in documents:

            content = doc.get(
                "content"
            )

            if not content:

                continue

            source = doc.get(
                "source"
            )

            chunk_id = doc.get(
                "chunk_id",
                0
            )

            # ------------------------------------------------
            # 生成 Embedding
            # ------------------------------------------------

            print(
                f"正在向量化第 {chunk_id} 个知识片段..."
            )

            vector = (
                self.embedding.encode_single(
                    content
                )
            )

            # ------------------------------------------------
            # 写入 PGVector
            # ------------------------------------------------

            row_id = self.vector_db.insert(
                content=content,
                embedding=vector,
                source=source,
                chunk_id=chunk_id
            )

            print(
                f"知识片段已写入，ID：{row_id}"
            )

            uploaded_count += 1

        return {
            "status": "success",
            "count": uploaded_count
        }

    # ========================================================
    # 关闭
    # ========================================================

    def close(self):
        """
        关闭数据库连接。
        """

        self.vector_db.close()


# ============================================================
# 单独测试
# ============================================================

if __name__ == "__main__":

    print("=" * 60)
    print("ProgramMind 知识库上传测试")
    print("=" * 60)

    uploader = KnowledgeUploader()

    try:

        documents = [

            {
                "content":
                    "人工智能是计算机科学的重要研究方向，"
                    "研究如何让计算机具备感知、学习、推理和决策能力。",
                "source":
                    "人工智能基础测试.txt",
                "chunk_id":
                    0
            },

            {
                "content":
                    "机器学习是人工智能的重要组成部分，"
                    "通过数据学习规律并完成预测或决策任务。",
                "source":
                    "人工智能基础测试.txt",
                "chunk_id":
                    1
            }

        ]

        result = uploader.upload(
            documents
        )

        print()
        print("上传结果：")
        print(result)

    finally:

        uploader.close()

    print()
    print("=" * 60)
    print("知识库上传测试结束")
    print("=" * 60)