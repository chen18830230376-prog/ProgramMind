from core.embedding_model import EmbeddingModel
from database.pgvector_db import PGVectorManager


print("=" * 60)
print("ProgramMind PGVector 向量检索测试")
print("=" * 60)


# ------------------------------------------------------------
# 1. 加载 Embedding 模型
# ------------------------------------------------------------

embedding_model = EmbeddingModel()


# ------------------------------------------------------------
# 2. 连接 PGVector
# ------------------------------------------------------------

db = PGVectorManager()
db.connect()


# ------------------------------------------------------------
# 3. 用户问题
# ------------------------------------------------------------

question = "什么是人工智能？"

print()
print("查询问题：")
print(question)


# ------------------------------------------------------------
# 4. 问题向量化
# ------------------------------------------------------------

query_vector = embedding_model.encode_single(
    question
)

print()
print(
    "查询向量维度：",
    len(query_vector)
)


# ------------------------------------------------------------
# 5. PGVector 检索
# ------------------------------------------------------------

results = db.search(
    query_vector,
    top_k=2
)


# ------------------------------------------------------------
# 6. 输出结果
# ------------------------------------------------------------

print()
print(
    "检索结果数量：",
    len(results)
)

for i, result in enumerate(
    results,
    start=1
):

    print()
    print(
        f"---------- 检索结果 {i} ----------"
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


# ------------------------------------------------------------
# 7. 关闭数据库
# ------------------------------------------------------------

db.close()


print()
print("=" * 60)
print("向量检索测试完成")
print("=" * 60)