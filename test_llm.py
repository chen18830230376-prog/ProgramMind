"""
ProgramMind

DeepSeek 流式输出测试

测试流程：

用户问题
    ↓
LLMModel
    ↓
ModelRouter
    ↓
DeepSeek
    ↓
DeepSeek API
    ↓
流式返回
"""

from core.model_deploy import LLMModel


print("=" * 60)
print("ProgramMind DeepSeek 流式输出测试")
print("=" * 60)


# ============================================================
# 创建统一模型入口
# ============================================================

llm = LLMModel()


# ============================================================
# 流式调用 DeepSeek
# ============================================================

print()
print("=" * 60)
print("开始调用 DeepSeek")
print("=" * 60)

print()
print("DeepSeek：")


for text in llm.stream_generate(
    "请用简单的语言解释什么是人工智能，并举一个实际应用例子。",
    task="代码"
):

    print(
        text,
        end="",
        flush=True
    )


print()
print()
print("=" * 60)
print("DeepSeek 流式测试结束")
print("=" * 60)