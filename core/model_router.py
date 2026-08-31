"""
ProgramMind

模型任务路由模块

功能：

根据任务类型自动选择 Qwen 或 DeepSeek。

Qwen：

    教学
    答疑
    知识库
    RAG
    学习规划
    备课

DeepSeek：

    代码
    算法
    论文
    科研
"""


class ModelRouter:
    """
    ProgramMind 模型任务路由器。
    """

    def __init__(self):

        print(
            "ModelRouter 初始化完成"
        )

    # ========================================================
    # 模型路由
    # ========================================================

    def route(
        self,
        task
    ):
        """
        根据任务类型选择模型。

        Qwen：

            教学
            答疑
            知识库
            RAG
            学习规划
            备课

        DeepSeek：

            代码
            算法
            论文
            科研
        """

        if not task:

            raise ValueError(
                "task 不能为空"
            )

        task = str(
            task
        ).strip()

        # ----------------------------------------------------
        # Qwen 任务
        # ----------------------------------------------------

        qwen_tasks = [
            "教学",
            "答疑",
            "知识库",
            "RAG",
            "学习规划",
            "备课",
        ]

        # ----------------------------------------------------
        # DeepSeek 任务
        # ----------------------------------------------------

        deepseek_tasks = [
            "代码",
            "算法",
            "论文",
            "科研",
        ]

        # ----------------------------------------------------
        # 路由
        # ----------------------------------------------------

        if task in qwen_tasks:

            return "qwen"

        elif task in deepseek_tasks:

            return "deepseek"

        else:

            # 未知任务默认使用 Qwen
            return "qwen"


# ============================================================
# 单独测试
# ============================================================

if __name__ == "__main__":

    print("=" * 60)
    print("ProgramMind ModelRouter 测试")
    print("=" * 60)

    router = ModelRouter()

    test_tasks = [
        "教学",
        "答疑",
        "知识库",
        "RAG",
        "学习规划",
        "备课",
        "代码",
        "算法",
        "论文",
        "科研",
    ]

    for task in test_tasks:

        model = router.route(
            task
        )

        print(
            f"{task} -> {model}"
        )

    print()
    print("=" * 60)
    print("Router 测试结束")
    print("=" * 60)