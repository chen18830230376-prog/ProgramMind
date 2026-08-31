"""
ProgramMind

AI 统一接口服务

基于 FastAPI。

提供：

1. AI 普通问答
2. RAG 学科知识问答
3. Agent 任务执行
4. KCI 知识评价
5. 动态学习规划


当前模型分工：

教学 / 答疑 / 知识库 / RAG
        ↓
      Qwen

代码 / 算法 / 论文 / 科研
        ↓
    DeepSeek
"""


from fastapi import FastAPI
from pydantic import BaseModel


# ============================================================
# 核心模块
# ============================================================

from core.model_deploy import LLMModel

from knowledge.rag_pipeline import RAGPipeline

from agent.task_workflow import ProgramMindWorkflow

from innovation.kci_model import KCIModel

from innovation.dynamic_plan import DynamicPlanner


# ============================================================
# 创建 FastAPI 应用
# ============================================================

app = FastAPI(
    title="ProgramMind AI",
    description="高校学科垂类大模型智能教学科研平台",
    version="1.0.0"
)


# ============================================================
# 全局服务对象
#
# 使用懒加载：
#
# FastAPI 启动时：
#     不立即加载 Qwen 7B
#
# 第一次真正调用 AI / RAG 时：
#     再加载模型
#
# 这样可以避免服务启动阶段直接占用大量显存和内存。
# ============================================================

llm = None

rag = None


# ------------------------------------------------------------
# Agent / KCI / 学习规划模块
#
# 这些模块目前初始化成本相对较低。
# ------------------------------------------------------------

workflow = ProgramMindWorkflow()

kci_model = KCIModel()

planner = DynamicPlanner()


# ============================================================
# 请求数据结构
# ============================================================


class ChatRequest(BaseModel):
    """
    普通 AI 问答请求。

    示例：

    {
        "question": "什么是人工智能？"
    }
    """

    question: str


class RAGRequest(BaseModel):
    """
    RAG 学科知识问答请求。

    示例：

    {
        "question": "什么是A*搜索算法？"
    }
    """

    question: str


class TaskRequest(BaseModel):
    """
    Agent 任务请求。

    示例：

    {
        "task": "帮我生成机器学习课程教案"
    }
    """

    task: str


class KCIRequest(BaseModel):
    """
    KCI 知识评价请求。

    示例：

    {
        "data": {
            "accuracy": 0.8
        }
    }
    """

    data: dict


class PlanRequest(BaseModel):
    """
    动态学习规划请求。

    示例：

    {
        "kci": 0.72,
        "weak_points": [
            "A*搜索",
            "CSP"
        ]
    }
    """

    kci: float

    weak_points: list


# ============================================================
# 1. 普通 AI 问答
# ============================================================


@app.post("/api/chat")
def chat(req: ChatRequest):
    """
    普通 AI 问答接口。

    流程：

        用户问题
            ↓
        LLMModel
            ↓
        ModelRouter
            ↓
        教学
            ↓
        Qwen
            ↓
        返回答案

    请求：

    {
        "question": "什么是人工智能？"
    }

    返回：

    {
        "question": "什么是人工智能？",
        "answer": "..."
    }
    """

    global llm

    # --------------------------------------------------------
    # 参数检查
    # --------------------------------------------------------

    if not req.question or not req.question.strip():

        return {
            "question": req.question,
            "answer": "问题不能为空。"
        }

    question = req.question.strip()

    # --------------------------------------------------------
    # 第一次调用时初始化统一模型系统
    # --------------------------------------------------------

    if llm is None:

        llm = LLMModel()

    # --------------------------------------------------------
    # 教学任务
    #
    # ModelRouter：
    #
    # 教学 → Qwen
    # --------------------------------------------------------

    answer = llm.generate(
        question,
        task="教学"
    )

    # --------------------------------------------------------
    # 返回
    # --------------------------------------------------------

    return {
        "question": question,
        "answer": answer
    }


# ============================================================
# 2. RAG 学科知识问答
# ============================================================


@app.post("/api/rag")
def rag_chat(req: RAGRequest):
    """
    RAG 学科知识增强问答接口。

    流程：

        用户问题
            ↓
        bge-m3
            ↓
        PGVector
            ↓
        课程知识检索
            ↓
        RAG Prompt
            ↓
        ModelRouter
            ↓
        RAG
            ↓
        Qwen
            ↓
        返回答案 + 来源


    请求：

    {
        "question": "什么是A*搜索算法？"
    }


    返回：

    {
        "question": "什么是A*搜索算法？",
        "answer": "...",
        "sources": [
            {
                "document": "...pdf",
                "score": 0.6586
            }
        ]
    }
    """

    global rag

    # --------------------------------------------------------
    # 参数检查
    # --------------------------------------------------------

    if not req.question or not req.question.strip():

        return {
            "question": req.question,
            "answer": "问题不能为空。",
            "sources": []
        }

    question = req.question.strip()

    # --------------------------------------------------------
    # 第一次调用 RAG 时初始化
    #
    # 初始化过程中：
    #
    # bge-m3
    # PGVector
    # LLMModel
    #
    # Qwen 本身依然采用懒加载，
    # 真正执行 rag.run() 时才加载。
    # --------------------------------------------------------

    if rag is None:

        rag = RAGPipeline(
            load_llm=True
        )

    # --------------------------------------------------------
    # 动态执行 RAG
    #
    # 注意：
    # question 来自前端请求，
    # 不是固定问题。
    # --------------------------------------------------------

    result = rag.run(
        question
    )

    # --------------------------------------------------------
    # 只返回前端需要的数据
    #
    # 不再返回 retrieved_docs。
    #
    # retrieved_docs 中包含完整知识 Chunk，
    # 会导致 API 返回大量无必要数据。
    # --------------------------------------------------------

    return {
        "question": result.get(
            "question",
            question
        ),

        "answer": result.get(
            "answer",
            ""
        ),

        "sources": result.get(
            "sources",
            []
        )
    }


# ============================================================
# 3. Agent 任务接口
# ============================================================


@app.post("/api/task")
def task_execute(req: TaskRequest):
    """
    Agent 任务执行接口。

    示例：

    {
        "task": "帮我生成机器学习课程教案"
    }
    """

    # --------------------------------------------------------
    # 参数检查
    # --------------------------------------------------------

    if not req.task or not req.task.strip():

        return {
            "error": "任务不能为空。"
        }

    task = req.task.strip()

    # --------------------------------------------------------
    # 执行 Agent
    # --------------------------------------------------------

    result = workflow.run(
        task
    )

    return result


# ============================================================
# 4. KCI 知识评价接口
# ============================================================


@app.post("/api/kci")
def calculate_kci(req: KCIRequest):
    """
    学生知识掌握可信指标计算接口。
    """

    # --------------------------------------------------------
    # 参数检查
    # --------------------------------------------------------

    if req.data is None:

        return {
            "error": "评价数据不能为空。"
        }

    # --------------------------------------------------------
    # 计算 KCI
    # --------------------------------------------------------

    result = kci_model.calculate(
        req.data
    )

    return result


# ============================================================
# 5. 动态学习规划接口
# ============================================================


@app.post("/api/plan")
def learning_plan(req: PlanRequest):
    """
    根据 KCI 和薄弱知识点生成动态学习路线。

    请求：

    {
        "kci": 0.72,
        "weak_points": [
            "A*搜索",
            "CSP"
        ]
    }
    """

    # --------------------------------------------------------
    # 参数检查
    # --------------------------------------------------------

    if req.kci < 0 or req.kci > 1:

        return {
            "error": "KCI 应该在 0 到 1 之间。"
        }

    # --------------------------------------------------------
    # 生成学习计划
    # --------------------------------------------------------

    result = planner.generate_plan(
        {
            "KCI": req.kci,
            "weak_points": req.weak_points
        }
    )

    return result


# ============================================================
# 6. 健康检查
# ============================================================


@app.get("/")
def index():
    """
    系统健康检查。

    返回：

    {
        "system": "ProgramMind AI",
        "status": "running"
    }
    """

    return {
        "system": "ProgramMind AI",
        "status": "running"
    }