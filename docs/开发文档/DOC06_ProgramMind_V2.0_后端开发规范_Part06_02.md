# ProgramMind V2.0 后端开发规范

# Part06.2 —— LangGraph Workflow 开发规范（完整版）

> 文档版本：V2.0
> 更新时间：2026-09
> 模块负责人：AI（Workflow Engine）
> 技术栈：LangGraph + LangChain + FastAPI + SQLAlchemy

---

# 第一章 Workflow Engine 模块定位

## 1.1 为什么使用 LangGraph

ProgramMind 不采用传统「Prompt → LLM → 返回」模式，而采用 **Workflow（智能工作流）**。

优势：

- 多 Agent 协同。
- Tool Calling。
- RAG 检索。
- Memory 更新。
- 支持复杂任务（教案、复习计划、科研助手）。

LangGraph 负责整个 AI 推理流程。

---

## 1.2 Workflow 在 AI Engine 中的位置

用户问题

↓

PlannerAgent

↓

Workflow Registry

↓

LangGraph Workflow

↓

Retriever / Tool / Memory

↓

LLM

↓

Citation

↓

Memory Update

↓

返回前端

Workflow 是 AI Engine 的执行器。

---

## 1.3 Workflow 类型（ProgramMind V2.0）

| Workflow                | 用途            |
| ----------------------- | ------------- |
| tutor_workflow          | AI Tutor 学习辅导 |
| lesson_workflow         | AI 教案生成       |
| review_workflow         | AI 学习规划       |
| research_workflow       | AI 科研助手       |
| evaluation_workflow     | AI 作业评价       |
| recommendation_workflow | AI 推荐生成       |

所有 Workflow 都继承统一状态。

---

# 第二章 Workflow 目录规范

## 2.1 app/ai/workflows/

```text
workflows/

workflow_registry.py

workflow_factory.py

workflow_executor.py

workflow_state.py

tutor_workflow.py

lesson_workflow.py

review_workflow.py

research_workflow.py

evaluation_workflow.py

recommendation_workflow.py
```

每个 Workflow 一个文件。

---

## 2.2 Workflow 生命周期

```text
Init

↓

Planning

↓

Retrieve Tool

↓

Prompt Build

↓

LLM Generate

↓

Citation Build

↓

Memory Update

↓

Finish
```

所有 Workflow 生命周期保持一致。

---

# 第三章 Workflow State（核心）

## 3.1 State 的定位

Workflow State 是 LangGraph 节点共享的数据对象。

所有 Node 都读取 / 修改 State。

---

## 3.2 WorkflowState 字段设计（完整版）

| 字段                 | 类型   | 说明                |
| ------------------ | ---- | ----------------- |
| conversation_id    | UUID | 会话                |
| user_id            | UUID | 用户                |
| course_id          | UUID | 当前课程              |
| workflow_type      | Enum | Workflow 类型       |
| question           | str  | 用户输入              |
| rewritten_question | str  | Planner 重写问题      |
| retrieved_chunks   | list | 检索结果              |
| citations          | list | Citation          |
| prompt             | str  | Prompt Builder 输出 |
| answer             | str  | LLM 输出            |
| model_name         | str  | 当前模型              |
| tools_called       | list | 调用工具              |
| current_node       | str  | 当前节点              |
| status             | Enum | Workflow 状态       |
| metadata           | dict | 扩展信息              |

---

## 3.3 Workflow Status

| 状态              | 含义         |
| --------------- | ---------- |
| pending         | 创建完成       |
| planning        | Planner 执行 |
| retrieving      | 检索阶段       |
| generating      | LLM 推理     |
| memory_updating | 更新 Memory  |
| completed       | 完成         |
| failed          | 失败         |

数据库 ai_workflows 同步更新。

---

## 3.4 WorkflowState JSON 示例

```json
{
  "conversation_id":"uuid",
  "workflow_type":"tutor",
  "question":"什么是列表推导式？",
  "retrieved_chunks":[...],
  "citations":[...],
  "status":"retrieving"
}
```

---

# 第四章 Node 开发规范

## 4.1 Node 的定义

Node 是 Workflow 中的执行单元。

每个 Node 完成一个任务。

禁止一个 Node 做多个职责。

---

## 4.2 ProgramMind 标准 Node

| Node          | 职责             |
| ------------- | -------------- |
| planner_node  | 重写问题、决定 Tool   |
| retrieve_node | RAG 检索         |
| mirror_node   | 获取学习状态         |
| course_node   | 获取课程信息         |
| prompt_node   | Prompt Builder |
| llm_node      | 调用模型           |
| citation_node | Citation 构建    |
| memory_node   | Memory 更新      |
| output_node   | 输出结果           |

Tutor Workflow 至少包含上述节点。

---

## 4.3 Node 输入输出规范

输入：

WorkflowState。

输出：

WorkflowState。

不得返回其他对象。

Node 修改 State 后返回。

---

# 第五章 Edge（节点跳转）规范

## 5.1 顺序 Edge

Tutor Workflow：

Planner

↓

Retriever

↓

Prompt

↓

LLM

↓

Citation

↓

Memory

↓

Output

---

## 5.2 条件 Edge

Planner 判断：

是否需要 RAG？

需要：

进入 Retriever。

否则：

直接 Prompt。

---

## 5.3 Conditional Edge 示例

问题类型：

- 闲聊
- 学科问答
- 教案生成
- 学习规划

不同 Workflow。

---

## 5.4 Error Edge

任意 Node 报错：

进入 Error Node。

记录 Workflow。

返回错误 Response。

---

# 第六章 Tutor Workflow（完整版）

## 6.1 Tutor Workflow 流程图

```text
User Question

↓

Planner Node

↓

Retriever Node

↓

Mirror Node（可选）

↓

Prompt Node

↓

LLM Node

↓

Citation Node

↓

Memory Node

↓

Output Node
```

---

## 6.2 Planner Node

职责：

问题分类。

Query Rewrite。

选择 Tool。

选择模型。

输出：

rewritten_question。

tools_called。

model_name。

---

## 6.3 Retriever Node

输入：

rewritten_question。

course_id。

输出：

TopK Chunk。

Citation Metadata。

写入：

retrieved_chunks。

---

## 6.4 Mirror Node

读取：

Learning Mirror。

Knowledge Mastery。

Recommendation。

Risk。

加入 Prompt Context。

---

## 6.5 Prompt Node

输入：

System Prompt。

Summary Memory。

Retriever Context。

Mirror Context。

Question。

输出：

最终 Prompt。

---

## 6.6 LLM Node

调用：

Model Router。

支持 Stream。

输出：

answer。

token_usage。

latency。

---

## 6.7 Citation Node

Chunk Metadata。

↓

Citation Builder。

↓

citations[]。

---

## 6.8 Memory Node

保存：

User Message。

Assistant Message。

Summary 更新。

Conversation 更新。

Usage Log。

---

# 第七章 Lesson Workflow（AI 教案生成）

## 7.1 Workflow 流程

课程信息

↓

Planner

↓

Retriever（教材）

↓

Lesson Prompt

↓

Qwen3

↓

Markdown 教案

↓

Memory

---

## 7.2 Lesson Workflow State

新增字段：

lesson_objective。

lesson_outline。

ppt_outline。

quiz_outline。

---

## 7.3 Lesson 输出格式

Markdown。

JSON Outline。

PPT Page List。

Quiz JSON。

支持下载。

---

# 第八章 Review Workflow（AI 学习规划）

## 8.1 输入

Learning Mirror。

Knowledge Mastery。

Risk Prediction。

课程进度。

考试时间。

---

## 8.2 Workflow

Mirror Node

↓

Recommendation Node

↓

Planner Node

↓

LLM

↓

Review Plan

---

## 8.3 输出内容

每日计划。

每周计划。

推荐知识点。

推荐实验。

推荐测验。

预计学习时间。

---

# 第九章 Research Workflow（科研助手）

## 9.1 Workflow

Question

↓

Retriever（论文知识库）

↓

Prompt Builder

↓

DeepSeek

↓

Citation

↓

Summary

---

## 9.2 输出

Markdown。

引用列表。

研究建议。

论文总结。

---

# 第十章 Evaluation Workflow（AI 作业评价）

## 10.1 Workflow

Submission

↓

Retriever（评分标准）

↓

Evaluation Prompt

↓

DeepSeek

↓

Score Suggestion

↓

Mastery Update

↓

Mirror Refresh

---

## 10.2 输出

AI Feedback。

知识点掌握变化。

Mirror 更新建议。

Timeline Event。

---

# 第十一章 Recommendation Workflow

## 11.1 输入

Mirror。

Risk。

Mastery。

Timeline。

---

## 11.2 输出

知识推荐。

实验推荐。

测验推荐。

课程推荐。

学习资料推荐。

---

## 11.3 Recommendation JSON

```json
{
  "priority":"high",
  "reason":"链表掌握度连续下降",
  "estimated_minutes":30
}
```

---

# 第十二章 Workflow Registry

## 12.1 Registry 职责

维护所有 Workflow。

Planner 不直接 import Workflow。

统一查询 Registry。

---

## 12.2 Registry 内容

```text
tutor

lesson

review

research

evaluation

recommendation
```

返回 Graph 实例。

---

## 12.3 Workflow Factory

根据 workflow_type 创建 Workflow。

支持动态扩展。

---

# 第十三章 Workflow Executor

## 13.1 Executor 职责

统一执行 Workflow。

负责：

创建 State。

执行 Graph。

异常处理。

保存 Workflow。

---

## 13.2 Executor 生命周期

Create State

↓

Run Graph

↓

Save Workflow Log

↓

Return Result

---

## 13.3 Workflow Log

数据库：

ai_workflows。

记录：

开始时间。

结束时间。

每一步耗时。

状态。

---

# 第十四章 Workflow 错误处理

## Error 分类

| 错误              | 处理       |
| --------------- | -------- |
| Retriever Error | 返回无引用回答  |
| LLM Error       | Retry 一次 |
| Tool Error      | 跳过 Tool  |
| Memory Error    | 不影响回答    |
| Workflow Error  | failed   |

Workflow 保持可恢复。

---

## Retry 策略

LLM Timeout。

Retry 一次。

Retriever Timeout。

返回空 Context。

---

# 第十五章 Workflow Checklist

## State

- [ ] WorkflowState
- [ ] Status Enum
- [ ] Metadata

## Nodes

- [ ] Planner
- [ ] Retriever
- [ ] Prompt
- [ ] LLM
- [ ] Citation
- [ ] Memory

## Workflow

- [ ] Tutor Workflow
- [ ] Lesson Workflow
- [ ] Review Workflow
- [ ] Research Workflow
- [ ] Evaluation Workflow
- [ ] Recommendation Workflow

## Engine

- [ ] Registry
- [ ] Factory
- [ ] Executor
- [ ] Error Handler

---

# 第十六章 本章开发成果

完成 Part06.2 后，ProgramMind AI Engine 将具备完整 LangGraph Workflow 引擎：

- WorkflowState 状态管理。
- Node/Edge 标准规范。
- 六个 AI Workflow。
- Workflow Registry 与 Factory。
- Workflow Executor。
- 与 AI 数据库、RAG、Learning Mirror 完整联动。
