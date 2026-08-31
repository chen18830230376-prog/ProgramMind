from core.model_deploy import LLMModel



llm=LLMModel()



print("================")
print("教学任务测试")


answer=llm.generate(

    "什么是人工智能？",

    task="教学"

)


print(answer)



print("================")

print("代码任务测试")


answer=llm.generate(

    "解释快速排序算法",

    task="代码"

)


print(answer)