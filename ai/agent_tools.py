"""
ProgramMind
Agent工具集

功能:
1. RAG知识检索工具
2. 文献处理工具
3. 学习分析工具
4. 论文辅助工具

对应平台:
智能能力层
"""


import datetime
import logging

from core.model_deploy import LLMModel
from core.prompt_template import PromptTemplate
from knowledge.vector_retrieval import VectorRetriever


logger = logging.getLogger(__name__)


# ==============================
# 1. RAG知识检索工具
# ==============================


class RAGTool:

    def __init__(self):

        """
        真实检索器采用懒加载：

        首次 search() 时才初始化
        VectorRetriever（bge-m3 + PGVector），
        避免工具创建阶段就加载 Embedding 模型。
        """

        self.retriever = None

    def _get_retriever(self):

        if self.retriever is None:

            self.retriever = VectorRetriever(
                threshold=0.5
            )

        return self.retriever

    def search(
        self,
        query,
        top_k=5
    ):

        """
        知识检索（真实链路：bge-m3 向量化 → PGVector 相似度检索）

        输入:
        query:
            用户问题

        输出:
        检索到的知识片段列表
        [
            {"content": ..., "source": ..., "score": ...},
            ...
        ]

        检索失败时返回 {"error": "..."}，不抛异常。
        """

        if not query:

            return {
                "error": "检索问题不能为空"
            }

        try:

            retriever = self._get_retriever()

            docs = retriever.search(
                query,
                top_k=top_k
            )

        except Exception as e:

            logger.exception("RAG 工具检索失败")
            return {
                "error": f"知识检索失败：{e}"
            }

        # ----------------------------------------------------
        # 只返回工具需要的字段
        # ----------------------------------------------------

        result = []

        for doc in docs:

            result.append(
                {
                    "content": doc.get("content", ""),
                    "source": doc.get("source"),
                    "score": doc.get("score", 0.0)
                }
            )

        if not result:

            return {
                "error": "知识库中未找到相关内容"
            }

        return result





# ==============================
# 2. 文献处理工具
# ==============================


class LiteratureTool:

    def __init__(self):

        """
        LLM 采用懒加载：首次 analyze/summarize 时才初始化，
        文献类任务经 ModelRouter 路由到 DeepSeek。
        """

        self.llm = None

    def _get_llm(self):

        if self.llm is None:

            self.llm = LLMModel()

        return self.llm

    def analyze(
        self,
        paper_text
    ):

        """
        文献分析（真实链路：research_review 模板 → DeepSeek）

        输出:
        - research_topic: 研究主题
        - analysis: 研究现状 / 技术路线 / 代表方法 / 未来方向

        调用失败时返回 {"error": "..."}，不抛异常。
        """

        if not paper_text:

            return {
                "error": "文献内容不能为空"
            }

        try:

            prompt = (
                PromptTemplate.research_review().format(
                    topic=paper_text
                )
            )

            answer = self._get_llm().generate(
                prompt,
                task="论文"
            )

        except Exception as e:

            logger.exception("文献分析失败")
            return {
                "error": f"文献分析失败：{e}"
            }

        return {
            "research_topic": paper_text,
            "analysis": answer
        }

    def summarize(
        self,
        papers
    ):

        """
        文献综述生成（真实链路：DeepSeek）

        输入:
        papers:
            文献内容字符串或文献列表

        输出:
        {"summary": 综述文本}

        调用失败时返回 {"error": "..."}，不抛异常。
        """

        if not papers:

            return {
                "error": "文献内容不能为空"
            }

        if isinstance(papers, (list, tuple)):

            text = "\n\n".join(str(p) for p in papers)

        else:

            text = str(papers)

        try:

            prompt = (
                "你是一名科研助手。请阅读以下文献内容，"
                "输出一篇结构清晰的文献综述，"
                "包括：1. 研究背景 2. 主要方法 3. 关键结论 "
                "4. 研究不足与展望。\n\n"
                f"文献内容：\n{text}"
            )

            summary = self._get_llm().generate(
                prompt,
                task="论文"
            )

        except Exception as e:

            logger.exception("文献综述生成失败")
            return {
                "error": f"文献综述生成失败：{e}"
            }

        return {
            "summary": summary
        }


# ==============================
# 3. 学习分析工具
# ==============================


class LearningAnalysisTool:



    def analyze_student(
        self,
        student_data
    ):


        """
        学习行为分析

        输入:

        {
        score:90,
        practice:80
        }


        输出:
        学习状态

        """


        score=student_data.get(
            "score",
            0
        )


        if score>=85:

            level="优秀"

        elif score>=60:

            level="良好"

        else:

            level="需要加强"



        return {


            "level":level,

            "suggestion":
            "建议加强算法实践"


        }





# ==============================
# 4. 论文排版工具
# ==============================


class PaperFormatTool:



    def format_check(
        self,
        paper
    ):


        """
        论文规范检查
        """



        return {


            "word_count":
            len(paper),


            "reference_check":
            True,


            "format":
            "符合基本论文格式"


        }




# ==============================
# Agent工具统一入口
# ==============================


class AgentTools:



    def __init__(self):


        self.rag=RAGTool()

        self.paper=LiteratureTool()

        self.learning=LearningAnalysisTool()

        self.format=PaperFormatTool()



    def execute(
        self,
        tool_name,
        params
    ):


        """
        统一工具调用接口

        """



        if tool_name=="rag":


            return self.rag.search(
                **params
            )


        elif tool_name=="paper":


            return self.paper.analyze(
                **params
            )


        elif tool_name=="learning":


            return self.learning.analyze_student(
                **params
            )


        elif tool_name=="format":


            return self.format.format_check(
                **params
            )



        else:


            return {

                "error":
                "未知工具"

            }






if __name__=="__main__":


    tools=AgentTools()


    print(

        tools.execute(

            "rag",

            {
            "query":
            "机器学习"
            }

        )

    )