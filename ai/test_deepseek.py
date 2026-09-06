from core.model_deploy import LLMModel


print("======================")
print("开始测试ProgramMind AI")
print("======================")


llm = LLMModel()


answer = llm.generate(

    "请解释快速排序算法的核心思想",

    task="代码"

)


print("======================")
print("AI回答:")
print("======================")


print(answer)


print("======================")
print("测试结束")
print("======================")