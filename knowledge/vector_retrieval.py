"""
ProgramMind

向量检索模块

功能：

1. 用户问题 Embedding
2. PGVector 相似度检索
3. 相似度阈值过滤
4. 返回知识内容、来源和分数
"""

from core.embedding_model import EmbeddingModel
from database.pgvector_db import PGVectorManager


class VectorRetriever:
    """
    ProgramMind 向量检索器。

    流程：

        用户问题
            ↓
        bge-m3
            ↓
        1024维向量
            ↓
        PGVector
            ↓
        相似度检索
            ↓
        相关知识
    """

    def __init__(
        self,
        threshold=0.5
    ):
        """
        初始化检索器。

        参数：

            threshold:
                默认相似度阈值。
                当前真实课程知识库测试使用 0.5。
        """

        self.threshold = threshold

        print("=" * 60)
        print("初始化向量检索器")
        print("=" * 60)

        # ----------------------------------------------------
        # Embedding 模型
        # ----------------------------------------------------

        self.embedding = EmbeddingModel()

        # ----------------------------------------------------
        # PGVector
        # ----------------------------------------------------

        self.db = PGVectorManager()

        self.db.connect()

    # ========================================================
    # 向量检索
    # ========================================================

    def search(
        self,
        query,
        top_k=5,
        threshold=None
    ):
        """
        根据用户问题检索相关知识。

        参数：

            query：
                用户问题。

            top_k：
                最多返回多少条。

            threshold：
                相似度阈值。
                如果不传，使用初始化时的 threshold。

        返回：

        [
            {
                "id": 1,
                "content": "...",
                "source": "...",
                "chunk_id": 0,
                "score": 0.85
            }
        ]
        """

        if not query:
            return []

        query = str(
            query
        ).strip()

        if not query:
            return []

        # ----------------------------------------------------
        # 使用默认阈值
        # ----------------------------------------------------

        if threshold is None:
            threshold = self.threshold

        # ----------------------------------------------------
        # Query Embedding
        # ----------------------------------------------------

        print(
            f"正在检索：{query}"
        )

        vector = (
            self.embedding.encode_single(
                query
            )
        )

        # ----------------------------------------------------
        # PGVector 检索
        # ----------------------------------------------------

        # ----------------------------------------------------
        # 候选召回扩展
        #
        # 内部多取候选（max(2N, N+3)），再经阈值过滤与去重后
        # 截断回用户请求的 top_k，保证“返回条数不超过 N”的语义不变。
        # ----------------------------------------------------

        try:

            requested_k = int(top_k)

        except (TypeError, ValueError):

            requested_k = 5

        if requested_k < 1:

            requested_k = 1

        candidate_k = max(
            requested_k * 2,
            requested_k + 3
        )

        results = self.db.search(
            query_vector=vector,
            top_k=candidate_k
        )

        # ----------------------------------------------------
        # 相似度阈值过滤
        # ----------------------------------------------------

        output = []

        for item in results:

            try:

                score = float(
                    item.get(
                        "score",
                        0.0
                    )
                )

            except (TypeError, ValueError):

                score = 0.0

            if score >= threshold:

                output.append(
                    {
                        "id": item.get(
                            "id"
                        ),

                        "content": item.get(
                            "content",
                            ""
                        ),

                        "source": item.get(
                            "source"
                        ),

                        "chunk_id": item.get(
                            "chunk_id",
                            0
                        ),

                        "score": score
                    }
                )

        # ----------------------------------------------------
        # ??????
        # ----------------------------------------------------
        # ??????????????????????????????????
        deduplicated = []
        seen_contents = set()

        for item in output:
            content = str(
                item.get("content", "")
            ).strip()

            if not content:
                continue

            normalized_content = " ".join(
                content.split()
            )

            if normalized_content in seen_contents:
                continue

            seen_contents.add(normalized_content)
            deduplicated.append(item)

        return deduplicated[:requested_k]

    # ========================================================
    # 关闭
    # ========================================================

    def close(self):
        """
        关闭数据库连接。
        """

        self.db.close()


# ============================================================
# 单独测试
# ============================================================

if __name__ == "__main__":

    print("=" * 60)
    print("ProgramMind 向量检索测试")
    print("=" * 60)

    retriever = VectorRetriever(
        threshold=0.5
    )

    try:

        query = "什么是人工智能？"

        results = retriever.search(
            query,
            top_k=5
        )

        print()
        print(
            f"检索到 {len(results)} 条相关知识"
        )

        for i, result in enumerate(
            results,
            start=1
        ):

            print()
            print(
                f"---------- 结果 {i} ----------"
            )

            print(
                "ID：",
                result["id"]
            )

            print(
                "相似度：",
                f"{result['score']:.4f}"
            )

            print(
                "来源：",
                result["source"]
            )

            print(
                "Chunk ID：",
                result["chunk_id"]
            )

            print(
                "内容：",
                result["content"]
            )

    finally:

        retriever.close()

    print()
    print("=" * 60)
    print("向量检索测试完成")
    print("=" * 60)