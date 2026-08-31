"""
ProgramMind

Qwen 统一接口测试

测试流程：

LLMModel
    ↓
ModelRouter
    ↓
Qwen
    ↓
QwenModel
    ↓
GPU + CPU Offload
    ↓
生成回答

本测试不会：

- 修改 PGVector
- 修改知识库
- 调用 DeepSeek
"""

from core.model_deploy import LLMModel


def main():

    print("=" * 70)
    print("ProgramMind Qwen 统一接口测试")
    print("=" * 70)

    # ========================================================
    # 初始化统一模型接口
    # ========================================================

    llm = LLMModel()

    try:

        # ----------------------------------------------------
        # 测试问题
        # ----------------------------------------------------

        question = (
            "请用简单易懂的语言解释什么是人工智能。"
        )

        print()
        print("=" * 70)
        print("测试问题")
        print("=" * 70)

        print()
        print(question)

        # ----------------------------------------------------
        # 通过统一接口调用 Qwen
        #
        # 教学任务 → ModelRouter → Qwen
        # ----------------------------------------------------

        print()
        print("=" * 70)
        print("开始调用 Qwen")
        print("=" * 70)

        answer = llm.generate(
            question,
            task="教学"
        )

        # ----------------------------------------------------
        # 输出回答
        # ----------------------------------------------------

        print()
        print("=" * 70)
        print("Qwen 最终回答")
        print("=" * 70)

        print()
        print(answer)

        # ----------------------------------------------------
        # 检查模型状态
        # ----------------------------------------------------

        print()
        print("=" * 70)
        print("模型状态")
        print("=" * 70)

        print()
        print(
            "Qwen 是否已经加载：",
            llm.qwen is not None
        )

        print(
            "DeepSeek 是否已经加载：",
            llm.deepseek is not None
        )

    finally:

        # ----------------------------------------------------
        # 清理 Qwen CUDA 缓存
        # ----------------------------------------------------

        try:

            import torch

            if torch.cuda.is_available():

                torch.cuda.empty_cache()

        except Exception:

            pass

    print()
    print("=" * 70)
    print("Qwen 统一接口测试完成")
    print("=" * 70)


if __name__ == "__main__":

    main()