"""
ProgramMind

RAG 完整流程模块

流程：

用户问题
    ↓
VectorRetriever
    ↓
PGVector 知识检索
    ↓
PromptTemplate
    ↓
LLMModel
    ↓
ModelRouter
    ↓
Qwen
    ↓
最终回答
    ↓
知识来源

当前架构：

教学 / 答疑 / 知识库 / RAG
        ↓
      Qwen

代码 / 算法 / 论文 / 科研
        ↓
    DeepSeek
"""

from .vector_retrieval import VectorRetriever
from .source_trace import SourceTracer

from core.prompt_template import PromptTemplate
from core.model_deploy import LLMModel


class RAGPipeline:
    """
    ProgramMind RAG 完整问答系统。

    RAG 任务通过 ModelRouter 路由到 Qwen。
    """

    def __init__(self, load_llm=True):

        print("=" * 60)
        print("初始化 ProgramMind RAG 系统")
        print("=" * 60)

        # ----------------------------------------------------
        # 向量检索器
        # ----------------------------------------------------

        self.retriever = VectorRetriever(
            threshold=0.5
        )

        # ----------------------------------------------------
        # 来源追踪
        # ----------------------------------------------------

        self.tracer = SourceTracer()

        # ----------------------------------------------------
        # 统一大模型接口
        # ----------------------------------------------------

        self.llm = None

        if load_llm:

            self.llm = LLMModel()

        print("=" * 60)
        print("RAG 系统初始化完成")
        print("=" * 60)

    # ========================================================
    # RAG 问答
    # ========================================================

    def run(
        self,
        question
    ):
        """
        执行一次完整 RAG 问答。

        流程：

            question
                ↓
            bge-m3
                ↓
            PGVector
                ↓
            Top-K
                ↓
            RAG Prompt
                ↓
            ModelRouter
                ↓
            Qwen
        """

        if not question:

            raise ValueError(
                "question 不能为空"
            )

        question = str(
            question
        ).strip()

        # ----------------------------------------------------
        # 第一步：知识检索
        # ----------------------------------------------------

        print()
        print(
            "第 1 步：正在检索知识..."
        )

        docs = self.retriever.search(
            question,
            top_k=5,
            threshold=0.5
        )

        print(
            f"检索到 {len(docs)} 条相关知识"
        )

        # ----------------------------------------------------
        # 第二步：构造知识上下文
        # ----------------------------------------------------

        print()
        print(
            "第 2 步：正在构造知识上下文..."
        )

        context_parts = []

        for i, doc in enumerate(
            docs,
            start=1
        ):

            content = doc.get(
                "content",
                ""
            )

            source = doc.get(
                "source",
                "未知来源"
            )

            score = float(
                doc.get(
                    "score",
                    0.0
                )
            )

            context_parts.append(
                f"[知识片段 {i}]\n"
                f"来源：{source}\n"
                f"相似度：{score:.4f}\n"
                f"内容：{content}"
            )

        if context_parts:

            context = "\n\n".join(
                context_parts
            )

        else:

            context = (
                "当前知识库中没有找到"
                "与问题相关的知识。"
            )

        # ----------------------------------------------------
        # 第三步：构造 RAG Prompt
        # ----------------------------------------------------

        print()
        print(
            "第 3 步：正在构造 RAG Prompt..."
        )

        prompt_template = (
            PromptTemplate.rag_answer()
        )

        prompt = prompt_template.format(
            context=context,
            question=question
        )

        # ----------------------------------------------------
        # 第四步：调用模型
        # ----------------------------------------------------

        if self.llm is None:

            raise RuntimeError(
                "LLM 尚未初始化，"
                "请使用 RAGPipeline(load_llm=True)"
            )

        print()
        print(
            "第 4 步：正在调用 RAG 模型..."
        )

        # ----------------------------------------------------
        # RAG → ModelRouter
        #
        # RAG 在 ModelRouter 中被定义为 Qwen 任务。
        # ----------------------------------------------------

        answer = self.llm.generate(
            prompt,
            task="RAG"
        )

        # ----------------------------------------------------
        # 第五步：来源追踪
        # ----------------------------------------------------

        print()
        print(
            "第 5 步：正在生成知识来源..."
        )

        sources = self.tracer.trace(
            docs
        )

        # ----------------------------------------------------
        # 返回结果
        # ----------------------------------------------------

        return {
            "question": question,
            "answer": answer,
            "sources": sources,
            "retrieved_docs": docs
        }

    # ========================================================
    # 关闭资源
    # ========================================================

    def close(self):

        if self.retriever is not None:

            self.retriever.close()


# ============================================================
# 单独测试
# ============================================================

if __name__ == "__main__":

    print("=" * 60)
    print("ProgramMind 完整 RAG 测试")
    print("=" * 60)

    rag = RAGPipeline(
        load_llm=True
    )

    try:

        # ----------------------------------------------------
        # 标准课程知识库测试问题
        # ----------------------------------------------------

        question = (
            "MIT 6.034 人工智能课程主要介绍哪三个核心主题？"
        )

        result = rag.run(
            question
        )

        # ----------------------------------------------------
        # 输出最终回答
        # ----------------------------------------------------

        print()
        print("=" * 60)
        print("最终 RAG 回答")
        print("=" * 60)

        print()
        print(
            result["answer"]
        )

        # ----------------------------------------------------
        # 输出知识来源
        # ----------------------------------------------------

        print()
        print("=" * 60)
        print("知识来源")
        print("=" * 60)

        if result["sources"]:

            for i, source in enumerate(
                result["sources"],
                start=1
            ):

                print(
                    f"{i}. "
                    f"{source['document']} "
                    f"(相似度："
                    f"{source['score']:.4f})"
                )

        else:

            print(
                "没有检索到知识来源。"
            )

    finally:

        rag.close()

    print()
    print("=" * 60)
    print("完整 RAG 测试结束")
    print("=" * 60)