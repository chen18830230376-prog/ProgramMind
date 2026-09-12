# ProgramMind V2.0 系统总体设计说明书（SDS）

# Part 04B —— AI Engine 架构设计（Multi-Agent 协同架构）

> 面向开发成员：AI/RAG 成员、产品负责人（AI 架构）
> 
> 技术栈：LangGraph + Ollama(Qwen3) + FastAPI + Tool Calling + RAG Engine

---

# 第三十九章 Multi-Agent 总体设计

## 39.1 为什么设计 Multi-Agent

ProgramMind 不使用「一个万能 AI」。

而是多个智能体分别完成不同任务。

优势：

| 单 Agent   | Multi-Agent    |
| --------- | -------------- |
| Prompt 很长 | Prompt 更专一     |
| 难维护       | 每个 Agent 单独维护  |
| 上下文混乱     | Agent 只关注自己的任务 |
| 不可扩展      | 可新增 Agent      |

ProgramMind 所有 AI 能力统一由 Agent 完成。

---

## 39.2 Agent 架构图

```text
                 User Request
                       │
                       ▼
                Planner Agent
                       │
     ┌─────────────────┼───────────────────┐
     ▼                 ▼                   ▼
 Lesson Agent     Tutor Agent        Quiz Agent
     │                 │                   │
     ▼                 ▼                   ▼
 RAG Engine        RAG Engine        RAG Engine
     │                 │                   │
     ▼                 ▼                   ▼
 Citation         Citation          Citation
                       │
                       ▼
                Summary Agent
                       │
                       ▼
                Final Response
```

Planner 是唯一入口。

其它 Agent 不直接互相调用。

---

## 39.3 AI Center Agent 地图

ProgramMind 共设计 **10 个 Agent**。

| Agent                | 职责     |
| -------------------- | ------ |
| Planner Agent        | 工作流调度器 |
| Tutor Agent          | 学科问答   |
| Lesson Agent         | 教案生成   |
| PPT Agent            | PPT 生成 |
| Quiz Agent           | AI 命题  |
| Summary Agent        | 总结助手   |
| Debug Agent          | 代码调试   |
| Analytics Agent      | 学情分析   |
| Recommendation Agent | 学习路径推荐 |
| Growth Agent         | 成长报告生成 |

所有 Agent 注册到 Agent Registry。

---

# 第四十章 Agent Registry（智能体注册中心）

## 40.1 Agent Registry 定位

所有 Agent 都必须注册。

目录：

```text
ai-engine/

agents/

registry.py

planner_agent.py

lesson_agent.py

quiz_agent.py

summary_agent.py

tutor_agent.py
```

Registry 提供统一入口。

---

## 40.2 Agent 生命周期

```mermaid
flowchart TD

Request

↓

Planner

↓

Select Agent

↓

Execute Agent

↓

Return Result

↓

Save Memory
```

统一生命周期。

---

## 40.3 Agent Metadata

每个 Agent 都有配置。

字段：

| 字段          | 描述       |
| ----------- | -------- |
| agent_id    | 唯一ID     |
| name        | Agent名称  |
| description | 功能说明     |
| tools       | 可调用工具    |
| memory      | 是否启用记忆   |
| prompt      | Prompt模板 |
| temperature | 默认温度     |

统一 YAML / JSON 配置。

---

# 第四十一章 Planner Agent（工作流调度器）

## 41.1 Planner Agent 定位

Planner 是 AI Engine 中最重要 Agent。

职责：

分析用户请求。

决定调用哪些 Agent。

生成 Workflow DAG。

---

## 41.2 Planner 输入

输入：

```json
{
"role":"teacher",
"task":"lesson_plan",
"course":"Python程序设计",
"chapter":"递归函数"
}
```

Planner 不生成内容。

Planner 生成计划。

---

## 41.3 Planner 输出

输出 DAG。

```json
{
"workflow":[
"lesson_agent",
"ppt_agent",
"quiz_agent"
]
}
```

后续 Workflow Engine 执行。

---

## 41.4 Planner 分类策略

根据任务分类。

| Task          | Agent           |
| ------------- | --------------- |
| ai_tutor      | Tutor Agent     |
| lesson_plan   | Lesson Agent    |
| ppt_generate  | PPT Agent       |
| quiz_generate | Quiz Agent      |
| summary       | Summary Agent   |
| debug         | Debug Agent     |
| analytics     | Analytics Agent |
| growth        | Growth Agent    |

统一 Task Router。

---

# 第四十二章 Tutor Agent（学科问答）

## 42.1 Tutor Agent 定位

ProgramMind 学科 AI 助教。

职责：

课程知识问答。

必须结合 RAG。

---

## 42.2 Tutor Pipeline

```mermaid
flowchart TD

Question

↓

Query Rewrite

↓

Retriever

↓

Prompt Builder

↓

Qwen3

↓

Citation Builder

↓

Response
```

---

## 42.3 Tutor 输入

包含：

课程。

章节。

问题。

历史上下文。

---

## 42.4 Tutor 输出

输出：

回答。

引用。

推荐知识点。

推荐实验。

推荐 Quiz。

---

## 42.5 Tutor Tool

可调用：

- Knowledge Search
- Chapter Search
- Homework Search
- Quiz Search

---

# 第四十三章 Lesson Agent（AI 教案）

## 43.1 Lesson Agent 定位

教师 AI 教案助手。

---

## 43.2 Lesson Workflow

```mermaid
flowchart TD

Course

↓

Chapter

↓

Knowledge Search

↓

Lesson Prompt

↓

LLM

↓

Lesson Markdown
```

---

## 43.3 Lesson 输出模板

输出：

教学目标。

教学重点。

难点。

课堂活动。

案例。

板书。

作业。

---

## 43.4 Lesson Tool

工具：

- Search Knowledge
- Search PPT
- Search Experiment

---

# 第四十四章 PPT Agent

## 44.1 PPT Agent 定位

生成 PPT 大纲。

---

## 44.2 PPT Workflow

```mermaid
flowchart TD

Lesson Markdown

↓

Split Slides

↓

Generate Outline

↓

Generate Speaker Note

↓

Output PPT JSON
```

---

## 44.3 PPT 输出

字段：

| 字段             |
| -------------- |
| page           |
| title          |
| content        |
| image_hint     |
| animation_hint |

---

# 第四十五章 Quiz Agent

## 45.1 Quiz Agent 定位

AI 命题助手。

---

## 45.2 Quiz Workflow

```mermaid
flowchart TD

Knowledge Point

↓

Retriever

↓

Generate Question

↓

Generate Answer

↓

Generate Analysis

↓

Quiz JSON
```

---

## 45.3 Quiz 输出格式

字段：

题目。

选项。

答案。

解析。

知识点。

难度。

Bloom 分类。

---

## 45.4 Quiz Tool

调用：

Knowledge Search。

Mastery Search。

Question Template。

---

# 第四十六章 Summary Agent

## 46.1 Summary Agent 定位

总结助手。

---

## 46.2 Summary 输入

支持：

PDF。

Markdown。

PPT。

AI Conversation。

Learning Record。

---

## 46.3 Summary 输出

摘要。

知识点。

关键词。

思维导图。

推荐学习内容。

---

# 第四十七章 Debug Agent

## 47.1 Debug Agent 定位

代码调试助手。

课程限定：

Python。

C++。

SQL。

---

## 47.2 Debug Pipeline

代码。

↓

Code Analyzer。

↓

Error Explain。

↓

Fix Suggestion。

↓

Diff。

---

## 47.3 输出

错误位置。

原因。

修复。

复杂度建议。

最佳实践。

---

# 第四十八章 Analytics Agent

## 48.1 Analytics Agent 定位

教师 AI 学情分析助手。

---

## 48.2 输入

班级 Mastery。

Homework。

Quiz。

Experiment。

Learning Record。

---

## 48.3 输出

课堂总结。

风险学生。

知识点分析。

教学建议。

---

# 第四十九章 Growth Agent

## 49.1 Growth Agent 定位

成长报告生成器。

---

## 49.2 输入

Learning Record。

Mastery。

HeatMap。

Timeline。

---

## 49.3 输出

成长报告。

学习建议。

风险提示。

学习目标。

---

# 第五十章 Recommendation Agent

## 50.1 Recommendation Agent 定位

学习路径推荐。

---

## 50.2 输入

Mastery。

课程。

学习目标。

---

## 50.3 输出

推荐课程。

推荐实验。

推荐 Quiz。

推荐 Tutor。

---

# 第五十一章 Tool Calling 设计

## 51.1 Tool Router

所有 Agent 使用 Tool Router。

工具目录：

```text
tools/

knowledge_tool.py

course_tool.py

quiz_tool.py

growth_tool.py

search_tool.py
```

---

## 51.2 Tool 分类

| Tool            | 功能     |
| --------------- | ------ |
| search_chunks   | 检索知识块  |
| search_homework | 查询作业   |
| search_quiz     | 查询测验   |
| get_mastery     | 查询掌握度  |
| get_growth      | 查询成长画像 |
| search_resource | 查询课程资源 |

---

## 51.3 Tool 生命周期

Agent。

↓

Tool Router。

↓

Tool。

↓

Return JSON。

↓

LLM。

工具不能直接输出 Markdown。

---

# 第五十二章 Workflow Engine

## 52.1 Workflow Engine 定位

执行 Planner DAG。

---

## 52.2 Workflow 生命周期

```mermaid
flowchart TD

Planner

↓

Create DAG

↓

Execute Node

↓

Collect Output

↓

Execute Next

↓

Finish
```

---

## 52.3 Workflow Node

字段：

| 字段       |
| -------- |
| node_id  |
| agent    |
| input    |
| output   |
| status   |
| token    |
| duration |

---

## 52.4 Workflow 状态

Waiting。

Running。

Success。

Failed。

Retry。

---

## 52.5 Workflow 可视化

前端 Timeline 使用。

展示：

Agent。

Token。

耗时。

日志。

---

# 第五十三章 Agent Memory（工作流级记忆）

## 53.1 Memory 分类

Workflow Memory。

Conversation Memory。

Growth Memory。

---

## 53.2 Workflow Memory

保存 Agent 输出。

下一节点共享。

例如：

Lesson Agent 输出。

↓

PPT Agent 输入。

---

## 53.3 Memory 生命周期

Start。

↓

Append。

↓

Read。

↓

Finish。

Workflow 完成后保存历史。

---

# 第五十四章 Multi-Agent Checklist

## Planner

- [ ] Task Router
- [ ] DAG Builder
- [ ] Agent Selector

## Agent

- [ ] Tutor Agent
- [ ] Lesson Agent
- [ ] PPT Agent
- [ ] Quiz Agent
- [ ] Summary Agent
- [ ] Debug Agent
- [ ] Analytics Agent
- [ ] Growth Agent
- [ ] Recommendation Agent

## Workflow

- [ ] Workflow Engine
- [ ] Timeline
- [ ] Retry
- [ ] Memory

## Tool

- [ ] Tool Router
- [ ] Knowledge Tool
- [ ] Growth Tool
- [ ] Search Tool

---

# 本章输出成果

ProgramMind Multi-Agent 系统正式定义：

- 10 个 Agent。
- Planner Agent。
- Workflow Engine。
- Tool Calling。
- Agent Registry。
- Workflow Timeline。
- Agent Memory。
- Tool Router。

这是 Challenge Cup **多智能体协同创新点** 的完整技术设计。

---

**DOC02 Part04B 完成。**
