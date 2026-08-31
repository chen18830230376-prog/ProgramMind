"""
ProgramMind

真实课程知识库多问题检索测试

测试目的：

1. 使用真实课程知识库
2. 连续测试多个高校学生问题
3. 获取每个问题的 Top-K 检索结果
4. 输出相似度、来源、Chunk ID 和内容
5. 观察不同问题的检索质量

本测试不会：

- 修改数据库
- 删除数据库数据
- 写入数据库
- 调用 DeepSeek
- 调用 Qwen
"""

from knowledge.vector_retrieval import VectorRetriever


# ============================================================
# 测试配置
# ============================================================

QUESTIONS = [
    "什么是人工智能？",
    "MIT 6.034 人工智能课程主要介绍哪三个核心主题？",
    "什么是搜索算法？",
    "什么是机器学习？",
    "什么是约束满足问题（CSP）？",
    "人工智能中的逻辑有什么作用？",
]

# 每个问题返回前几个结果
TOP_K = 5

# ------------------------------------------------------------
# 这里使用 0.0 是为了观察原始检索结果，
# 不让阈值提前过滤结果。
#
# 注意：
# 正式 RAG 当前使用的是 0.5。
# ------------------------------------------------------------

TEST_THRESHOLD = 0.0


# ============================================================
# 单个问题测试
# ============================================================

def test_question(
    retriever,
    question
):
    """
    测试一个问题。

    返回：

        {
            "question": "...",
            "count": 5,
            "scores": [...]
        }
    """

    print()
    print("=" * 70)
    print("当前测试问题")
    print("=" * 70)

    print()
    print(question)

    # --------------------------------------------------------
    # 检索
    # --------------------------------------------------------

    results = retriever.search(
        question,
        top_k=TOP_K,
        threshold=TEST_THRESHOLD
    )

    print()
    print(
        "检索结果数量：",
        len(results)
    )

    # --------------------------------------------------------
    # 没有结果
    # --------------------------------------------------------

    if not results:

        print()
        print(
            "没有检索到结果。"
        )

        return {
            "question": question,
            "count": 0,
            "scores": []
        }

    # --------------------------------------------------------
    # 输出 Top-K
    # --------------------------------------------------------

    scores = []

    for index, item in enumerate(
        results,
        start=1
    ):

        item_id = item.get(
            "id",
            "未知"
        )

        score = float(
            item.get(
                "score",
                0.0
            )
        )

        source = item.get(
            "source",
            "未知来源"
        )

        chunk_id = item.get(
            "chunk_id",
            "未知"
        )

        content = item.get(
            "content",
            ""
        )

        scores.append(
            score
        )

        print()
        print("-" * 70)
        print(
            f"检索结果 {index}"
        )
        print("-" * 70)

        print(
            "数据库 ID：",
            item_id
        )

        print(
            "相似度：",
            f"{score:.4f}"
        )

        print(
            "来源：",
            source
        )

        print(
            "Chunk ID：",
            chunk_id
        )

        print()
        print(
            "内容："
        )

        print(content)

    # --------------------------------------------------------
    # 当前问题统计
    # --------------------------------------------------------

    print()
    print("-" * 70)
    print("当前问题相似度统计")
    print("-" * 70)

    print(
        "Top-1：",
        f"{max(scores):.4f}"
    )

    print(
        "Top-5最低：",
        f"{min(scores):.4f}"
    )

    print(
        "Top-5平均：",
        f"{sum(scores) / len(scores):.4f}"
    )

    print(
        "Top-1 >= 0.6：",
        max(scores) >= 0.6
    )

    print(
        "Top-1 >= 0.5：",
        max(scores) >= 0.5
    )

    print(
        "Top-1 >= 0.4：",
        max(scores) >= 0.4
    )

    return {
        "question": question,
        "count": len(results),
        "scores": scores
    }


# ============================================================
# 主程序
# ============================================================

def main():

    print("=" * 70)
    print("ProgramMind 真实课程知识库多问题检索测试")
    print("=" * 70)

    print()
    print(
        f"测试问题数量：{len(QUESTIONS)}"
    )

    print(
        f"Top-K：{TOP_K}"
    )

    print(
        f"测试阈值：{TEST_THRESHOLD}"
    )

    # ========================================================
    # 创建检索器
    # ========================================================

    retriever = VectorRetriever(
        threshold=TEST_THRESHOLD
    )

    all_results = []

    try:

        # ====================================================
        # 连续测试所有问题
        # ====================================================

        for index, question in enumerate(
            QUESTIONS,
            start=1
        ):

            print()
            print("#" * 70)
            print(
                f"第 {index}/{len(QUESTIONS)} 个问题"
            )
            print("#" * 70)

            try:

                result = test_question(
                    retriever,
                    question
                )

                all_results.append(
                    result
                )

            except Exception as e:

                print()
                print(
                    f"这个问题测试失败：{e}"
                )

                all_results.append(
                    {
                        "question": question,
                        "count": 0,
                        "scores": []
                    }
                )

        # ====================================================
        # 汇总
        # ====================================================

        print()
        print("=" * 70)
        print("全部问题测试汇总")
        print("=" * 70)

        successful_questions = 0

        top1_scores = []

        for index, result in enumerate(
            all_results,
            start=1
        ):

            question = result[
                "question"
            ]

            count = result[
                "count"
            ]

            scores = result[
                "scores"
            ]

            if scores:

                successful_questions += 1

                top1 = max(
                    scores
                )

                top1_scores.append(
                    top1
                )

                print()
                print(
                    f"{index}. {question}"
                )

                print(
                    f"   检索数量：{count}"
                )

                print(
                    f"   Top-1相似度：{top1:.4f}"
                )

            else:

                print()
                print(
                    f"{index}. {question}"
                )

                print(
                    "   检索失败或没有结果"
                )

        # ====================================================
        # 整体统计
        # ====================================================

        print()
        print("-" * 70)
        print("整体统计")
        print("-" * 70)

        print()
        print(
            "测试问题总数：",
            len(QUESTIONS)
        )

        print(
            "成功检索问题数：",
            successful_questions
        )

        print(
            "失败/无结果问题数：",
            len(QUESTIONS)
            - successful_questions
        )

        if top1_scores:

            print()
            print(
                "所有问题最高 Top-1：",
                f"{max(top1_scores):.4f}"
            )

            print(
                "所有问题最低 Top-1：",
                f"{min(top1_scores):.4f}"
            )

            print(
                "所有问题平均 Top-1：",
                f"{sum(top1_scores) / len(top1_scores):.4f}"
            )

            print()
            print(
                "Top-1 >= 0.5 的问题：",
                sum(
                    score >= 0.5
                    for score in top1_scores
                ),
                "/",
                len(top1_scores)
            )

    finally:

        # ----------------------------------------------------
        # 关闭数据库连接
        # ----------------------------------------------------

        retriever.close()

    print()
    print("=" * 70)
    print("真实课程知识库多问题检索测试完成")
    print("=" * 70)


# ============================================================
# 程序入口
# ============================================================

if __name__ == "__main__":

    main()