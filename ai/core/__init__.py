"""
ProgramMind Core AI模块

负责:

1. 大语言模型加载
2. Embedding向量生成
3. Prompt管理


技术:

Qwen
DeepSeek
bge-m3


"""


from .model_deploy import LLMModel

from .embedding_model import EmbeddingModel

from .prompt_template import PromptTemplate



__all__=[

    "LLMModel",

    "EmbeddingModel",

    "PromptTemplate"

]