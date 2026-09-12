# ProgramMind V2.0 后端开发规范

# Part06.1 —— AI Engine 总体架构与 Multi-Agent 系统设计（完整版）

> 文档版本：V2.0
> 更新时间：2026-09
> 模块负责人：AI（Multi-Agent）
> 技术栈：LangChain + LangGraph + Ollama + Qwen3 + DeepSeek + FastAPI

---

# 第一章 AI Engine 模块定位

## 1.1 AI Engine 在 ProgramMind 中的位置

AI Engine 是整个 ProgramMind 的智能决策中心。

负责协调：

- RAG 检索模块（Knowledge）
- Learning Mirror（Growth）
- Course Service（课程）
- Learning Service（作业/实验/测验）
- Conversation Memory
- Prompt Builder
- LLM Router
- Tool Calling

整个 AI Engine 不直接访问数据库，而是调用 Service 层。

---

## 1.2 AI Engine 整体架构

```text
                Vue Frontend
                     │
                     ▼
               AI API Router
                     │
                     ▼
                AIService（入口）
                     │
        ┌────────────┼─────────────┐
        ▼            ▼             ▼
   PlannerAgent   TutorAgent   TeacherAgent
        │            │             │
        └────────────┼─────────────┘
                     ▼
             LangGraph Workflow
                     │
        ┌────────────┼────────────┐
        ▼            ▼            ▼
 Retriever Tool  Mirror Tool  Course Tool
        │            │            │
        ▼            ▼            ▼
 KnowledgeSvc  GrowthSvc   CourseSvc
                     │
                     ▼
               Prompt Builder
                     │
                     ▼
                Model Router
             (Qwen3 / DeepSeek)
                     │
                     ▼
                 Stream Service
                     │
                     ▼
                SSE 返回前端
```

AI Engine 是多个 Agent 的调度中心。

---

# 第二章 AI Engine 目录结构（最终版）

## 2.1 app/ai/

```text
ai/

├── agents/
│   ├── base_agent.py
│   ├── planner_agent.py
│   ├── tutor_agent.py
│   ├── teacher_agent.py
│   ├── research_agent.py
│   ├── evaluation_agent.py
│   └── recommendation_agent.py
│
├── workflows/
│   ├── tutor_workflow.py
│   ├── lesson_workflow.py
│   ├── review_workflow.py
│   ├── research_workflow.py
│   └── workflow_registry.py
│
├── router/
│   ├── model_router.py
│   ├── qwen_provider.py
│   ├── deepseek_provider.py
│   └── ollama_provider.py
│
├── prompt/
│   ├── prompt_builder.py
│   ├── prompt_loader.py
│   ├── prompt_registry.py
│   └── prompt_templates.py
│
├── memory/
│   ├── conversation_memory.py
│   ├── summary_memory.py
│   ├── long_memory.py
│   └── memory_manager.py
│
├── tools/
│   ├── rag_tool.py
│   ├── mirror_tool.py
│   ├── course_tool.py
│   ├── quiz_tool.py
│   ├── recommendation_tool.py
│   └── tool_registry.py
│
├── streaming/
│   └── stream_service.py
│
├── schemas/
│   └── workflow_state.py
│
└── services/
    └── ai_service.py
```

目录与 LangGraph 一一对应。

---

# 第三章 Multi-Agent 设计思想

## 3.1 为什么使用多个 Agent

ProgramMind 不使用一个万能 Prompt。

而是多个专业 Agent。

优势：

- Prompt 更短。
- 上下文更精准。
- 工具调用更明确。
- 更容易维护。

---

## 3.2 Agent 分类

| Agent               | 职责               |
| ------------------- | ---------------- |
| PlannerAgent        | 任务规划、选择 Workflow |
| TutorAgent          | 学习辅导、知识问答        |
| TeacherAgent        | 教案、课件、出题         |
| ResearchAgent       | 科研助手、论文分析        |
| EvaluationAgent     | 作业/实验 AI 评价      |
| RecommendationAgent | 学习推荐生成           |

---

## 3.3 Agent 生命周期

收到用户问题

↓

Planner 判断任务

↓

选择 Agent

↓

调用工具

↓

调用 LLM

↓

返回 Response

↓

更新 Memory

---

# 第四章 BaseAgent（所有 Agent 基类）

## 4.1 BaseAgent 职责

所有 Agent 必须继承 BaseAgent。

统一能力：

- Prompt Builder
- Tool Registry
- Memory
- Model Router
- Stream Output

---

## 4.2 BaseAgent 提供的方法

```text
build_prompt()

call_model()

call_tools()

run()

stream()

save_memory()

save_message()
```

所有 Agent 保持一致接口。

---

## 4.3 Agent Context

Agent 接收统一 Context。

包含：

- user_id
- conversation_id
- course_id
- learning_state
- history_summary
- tools
- prompt_version

方便切换 Agent。

---

# 第五章 PlannerAgent（调度中心）

## 5.1 PlannerAgent 定位

Planner 不回答问题。

Planner 负责判断：

用户需要哪个 Workflow。

---

## 5.2 Planner 输入

用户消息。

课程。

Conversation。

Memory。

---

## 5.3 Planner 输出

Workflow Type。

Agent。

Tool List。

Model。

---

## 5.4 Planner 决策规则（V2）

| 用户问题          | Workflow            |
| ------------- | ------------------- |
| Python 怎么写列表？ | Tutor Workflow      |
| 帮我写教案         | Lesson Workflow     |
| 帮我生成 PPT      | Lesson Workflow     |
| 帮我分析论文        | Research Workflow   |
| 帮我制定复习计划      | Review Workflow     |
| 帮我评价实验报告      | Evaluation Workflow |

Planner 输出 JSON。

---

# 第六章 TutorAgent（学习辅导 Agent）

## 6.1 TutorAgent 定位

ProgramMind 最常用 Agent。

负责：

- 知识问答。
- 代码解释。
- 学习计划。
- RAG 检索。
- Citation。

---

## 6.2 TutorAgent 工具

| Tool                | 用途     |
| ------------------- | ------ |
| rag_tool            | 检索教材   |
| mirror_tool         | 获取学习状态 |
| course_tool         | 获取课程信息 |
| recommendation_tool | 获取推荐   |

---

## 6.3 Tutor Workflow

Question

↓

Retriever

↓

Citation

↓

Prompt Builder

↓

Qwen3

↓

Answer

---

# 第七章 TeacherAgent（教师助手）

## 7.1 TeacherAgent 职责

教师侧 AI。

负责：

- 教案生成。
- PPT 大纲。
- 作业生成。
- 测验生成。
- 教学建议。

---

## 7.2 TeacherAgent Tool

Course Tool。

Knowledge Tool。

Quiz Tool。

Mirror Tool。

---

## 7.3 输出内容

Markdown。

JSON。

PPT Outline。

Quiz JSON。

Lesson Plan Markdown。

---

# 第八章 ResearchAgent（科研助手）

## 8.1 ResearchAgent 职责

科研辅助。

支持：

论文阅读。

文献总结。

算法解释。

实验设计。

参考文献整理。

---

## 8.2 Tool

RAG。

Citation。

Paper Parser（预留）。

Web Search（预留）。

---

## 8.3 输出

Markdown。

引用列表。

算法解释。

研究计划。

---

# 第九章 EvaluationAgent（AI评价）

## 9.1 模块定位

评价：

作业。

实验。

代码。

报告。

---

## 9.2 输入

学生提交。

评分标准。

课程知识点。

---

## 9.3 输出

分数建议。

知识点掌握更新。

AI Feedback。

Timeline Event。

Mirror 更新建议。

---

# 第十章 RecommendationAgent（推荐 Agent）

## 10.1 职责

读取：

Learning Mirror。

Knowledge Mastery。

Risk Prediction。

生成 Recommendation。

---

## 10.2 输出

知识推荐。

实验推荐。

测验推荐。

复习计划。

课程资料推荐。

---

# 第十一章 Model Router（模型路由）

## 11.1 为什么需要 Router

ProgramMind 使用多个模型。

统一 Router。

---

## 11.2 默认模型映射

| Agent      | 默认模型      |
| ---------- | --------- |
| Tutor      | Qwen3 14B |
| Teacher    | Qwen3 14B |
| Research   | DeepSeek  |
| Evaluation | DeepSeek  |
| Planner    | Qwen3 8B  |

---

## 11.3 Router 输入

Agent。

Prompt。

Tools。

Stream。

Temperature。

输出：

Provider。

Model。

---

# 第十二章 Workflow Registry

## Registry 职责

维护所有 Workflow。

统一入口。

---

## Workflow 列表

```text
tutor_workflow

lesson_workflow

review_workflow

research_workflow

evaluation_workflow
```

Planner 调 Registry。

---

# 第十三章 AI Service（唯一入口）

## AIService 方法

```text
chat()

stream_chat()

execute_workflow()

generate_lesson()

generate_quiz()

evaluate_homework()

generate_recommendation()
```

Router 只调用 AIService。

---

# 第十四章 AI Engine Checklist

## Agents

- [ ] BaseAgent
- [ ] PlannerAgent
- [ ] TutorAgent
- [ ] TeacherAgent
- [ ] ResearchAgent
- [ ] EvaluationAgent
- [ ] RecommendationAgent

## Router

- [ ] Model Router
- [ ] Provider Router

## Workflow

- [ ] Workflow Registry
- [ ] Planner 输出 Workflow

## Service

- [ ] AIService
- [ ] Stream Chat
- [ ] Workflow Execute

---

# 第十五章 本章开发成果

完成 Part06.1 后，ProgramMind AI Engine 将建立统一的 Multi-Agent 架构：

- 6 个专业 Agent。
- Planner 调度中心。
- Model Router。
- Workflow Registry。
- AIService 唯一入口。
- 与 Knowledge、Growth、Course 三大模块建立统一调用关系。
