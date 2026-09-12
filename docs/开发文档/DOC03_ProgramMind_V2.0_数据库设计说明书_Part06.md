# ProgramMind V2.0 数据库设计说明书（DDS）

# Part 06 —— AI Engine 数据库设计（Conversation / Agent Workflow / Memory）

> 面向开发成员：AI负责人、Backend负责人
> 
> 技术栈：MySQL 8.0 + SQLAlchemy 2.x + LangGraph（或自研Workflow Engine）

---

# 第五十九章 AI Engine 总体设计

## 59.1 模块定位

AI Engine 是 ProgramMind V2.0 的核心中台。

所有 AI 能力（Tutor、Lesson、Quiz、Summary、Analytics、Planner）统一经过 AI Engine。

负责：

- AI 对话历史
- 多智能体任务流
- Agent 执行日志
- 长期记忆（Memory）
- Prompt Metadata
- Citation 关联

所有 Agent 不允许直接调用数据库，而必须经过 AI Engine。

---

## 59.2 AI Engine 数据流

```text
Frontend
    │
    ▼
Conversation Service
    │
    ▼
Planner Agent
    │
    ├──────── Tutor Agent
    ├──────── Quiz Agent
    ├──────── Lesson Agent
    ├──────── Summary Agent
    ├──────── Analytics Agent
    └──────── Retriever Tool
                    │
                    ▼
            Knowledge Base

Workflow Trace
      │
      ▼
Database
```

---

## 59.3 数据表清单

| 表名               | 描述             |
| ---------------- | -------------- |
| ai_conversations | AI 会话          |
| ai_messages      | AI 消息          |
| agent_workflows  | Agent Workflow |
| agent_tasks      | Agent Step     |
| agent_memory     | 长期记忆           |

共 **5 张 AI 核心数据库表**。

---

# 第六十章 ai_conversations（AI 会话）

## 60.1 表定位

每次 AI 会话一条记录。

例如：

AI学习辅导。

AI代码调试。

AI命题。

AI教案。

AI总结。

都是 Conversation。

---

## 60.2 字段设计

| 字段                | 类型           | 描述                                     |
| ----------------- | ------------ | -------------------------------------- |
| id                | CHAR(36)     | UUID                                   |
| user_id           | CHAR(36)     | FK users                               |
| course_id         | CHAR(36)     | FK courses，可空                          |
| conversation_type | ENUM         | tutor/debug/review/lesson/summary/chat |
| title             | VARCHAR(200) | 自动生成标题                                 |
| latest_message    | TEXT         | 最近一句消息                                 |
| total_messages    | INT          | 消息数量                                   |
| citation_count    | INT          | 引用数量                                   |
| memory_enabled    | BOOLEAN      | 是否启用长期记忆                               |
| status            | ENUM         | active / archived                      |
| created_at        | DATETIME     | 创建时间                                   |
| updated_at        | DATETIME     | 更新时间                                   |

---

## 60.3 conversation_type

| 类型      | 页面     |
| ------- | ------ |
| tutor   | AI学习辅导 |
| debug   | AI代码调试 |
| review  | AI复习规划 |
| lesson  | AI教案   |
| summary | AI总结   |
| chat    | AI通用助手 |

统一 Conversation。

---

## 60.4 自动标题

第一次问题生成：

例如：

```
Python循环语句

链表和数组区别

如何设计二叉树实验？
```

Summary Agent 自动生成。

---

## 60.5 API

| API                           | 功能   |
| ----------------------------- | ---- |
| GET /ai/conversations         | 会话列表 |
| POST /ai/conversations        | 新建会话 |
| DELETE /ai/conversations/{id} | 删除会话 |
| PATCH /ai/conversations/{id}  | 重命名  |

---

# 第六十一章 ai_messages（AI 消息）

## 61.1 表定位

Conversation 中每一句消息。

支持流式回复。

支持 Citation。

支持 Tool。

---

## 61.2 字段设计

| 字段              | 类型           | 描述                               |
| --------------- | ------------ | -------------------------------- |
| id              | CHAR(36)     | UUID                             |
| conversation_id | CHAR(36)     | FK ai_conversations              |
| role            | ENUM         | user / assistant / tool / system |
| content         | LONGTEXT     | Markdown 内容                      |
| token_count     | INT          | Token 数                          |
| model_name      | VARCHAR(100) | qwen / deepseek                  |
| generation_time | INT          | 毫秒                               |
| has_citation    | BOOLEAN      | 是否引用知识                           |
| has_tool_call   | BOOLEAN      | 是否调用工具                           |
| created_at      | DATETIME     | 时间                               |

---

## 61.3 role 定义

| role      | 描述            |
| --------- | ------------- |
| user      | 用户消息          |
| assistant | AI 回复         |
| tool      | Tool 返回       |
| system    | Prompt/System |

Conversation 可重放。

---

## 61.4 Tool Message 示例

```json
{
  "tool":"Retriever",
  "chunks":["chunk1","chunk2"]
}
```

Tool 独立消息。

方便调试。

---

## 61.5 API

| API                                | 功能   |
| ---------------------------------- | ---- |
| GET /ai/messages/{conversation_id} | 获取历史 |
| POST /ai/messages                  | 保存消息 |
| DELETE /ai/messages/{id}           | 删除消息 |

---

# 第六十二章 agent_workflows（Workflow）

## 62.1 表定位

一次 Agent Workflow 一条记录。

例如：

AI 教案生成。

AI PPT生成。

AI 命题。

AI 学情总结。

---

## 62.2 字段设计

| 字段              | 类型           | 描述                             |
| --------------- | ------------ | ------------------------------ |
| id              | CHAR(36)     | UUID                           |
| conversation_id | CHAR(36)     | FK ai_conversations            |
| workflow_name   | VARCHAR(100) | lesson_workflow                |
| planner_agent   | VARCHAR(50)  | planner                        |
| status          | ENUM         | pending/running/success/failed |
| total_steps     | INT          | Step 数                         |
| finished_steps  | INT          | 已完成                            |
| duration        | INT          | 毫秒                             |
| created_at      | DATETIME     | 创建时间                           |
| updated_at      | DATETIME     | 更新时间                           |

---

## 62.3 Workflow 类型

| Workflow         | Agent             |
| ---------------- | ----------------- |
| lesson_workflow  | Lesson Planner    |
| ppt_workflow     | PPT Planner       |
| quiz_workflow    | Quiz Planner      |
| summary_workflow | Analytics Planner |
| review_workflow  | Tutor Planner     |

---

## 62.4 Workflow 生命周期

```text
pending

↓

running

↓

success

↓

archived
```

失败进入 failed。

---

## 62.5 API

| API                       | 功能         |
| ------------------------- | ---------- |
| POST /agent/workflows     | 创建Workflow |
| GET /agent/workflows/{id} | Workflow详情 |
| GET /agent/workflows      | Workflow列表 |

---

# 第六十三章 agent_tasks（Agent Step）

## 63.1 表定位

Workflow 中每一步。

记录 Agent 执行轨迹。

Challenge Cup Demo 要展示这里。

---

## 63.2 字段设计

| 字段             | 类型           | 描述                             |
| -------------- | ------------ | ------------------------------ |
| id             | CHAR(36)     | UUID                           |
| workflow_id    | CHAR(36)     | FK agent_workflows             |
| step_index     | INT          | 顺序                             |
| agent_name     | VARCHAR(50)  | lesson_agent                   |
| task_name      | VARCHAR(100) | extract_outline                |
| input_summary  | TEXT         | 输入摘要                           |
| output_summary | TEXT         | 输出摘要                           |
| tool_used      | VARCHAR(100) | retriever/search               |
| token_input    | INT          | 输入Token                        |
| token_output   | INT          | 输出Token                        |
| duration       | INT          | 耗时                             |
| status         | ENUM         | pending/running/success/failed |
| created_at     | DATETIME     | 时间                             |

---

## 63.3 Agent Name

统一命名。

| Agent           | 描述      |
| --------------- | ------- |
| planner_agent   | Planner |
| tutor_agent     | Tutor   |
| lesson_agent    | 教案      |
| ppt_agent       | PPT     |
| quiz_agent      | 命题      |
| summary_agent   | 总结      |
| analytics_agent | 学情      |
| retriever_agent | 检索      |

---

## 63.4 Step 示例

| Step | Agent         |
| ---- | ------------- |
| 1    | Retriever     |
| 2    | Lesson Agent  |
| 3    | PPT Agent     |
| 4    | Quiz Agent    |
| 5    | Summary Agent |

前端时间轴展示。

---

## 63.5 API

| API                            | 功能     |
| ------------------------------ | ------ |
| GET /agent/tasks/{workflow_id} | 查看执行轨迹 |

Demo 中 Agent Timeline 数据来自这里。

---

# 第六十四章 agent_memory（长期记忆）

## 64.1 表定位

ProgramMind AI 长期学习记忆。

不是聊天历史。

保存用户画像。

---

## 64.2 Memory 分类

| 类型         | 描述   |
| ---------- | ---- |
| preference | 学习偏好 |
| mastery    | 知识掌握 |
| schedule   | 学习计划 |
| mistake    | 高频错误 |
| interest   | 兴趣方向 |

---

## 64.3 字段设计

| 字段           | 类型           | 描述                     |
| ------------ | ------------ | ---------------------- |
| id           | CHAR(36)     | UUID                   |
| user_id      | CHAR(36)     | FK users               |
| course_id    | CHAR(36)     | FK courses             |
| memory_type  | ENUM         | preference/mastery/... |
| memory_key   | VARCHAR(100) | preferred_language     |
| memory_value | LONGTEXT     | JSON                   |
| confidence   | DECIMAL(4,2) | 可信度                    |
| source       | VARCHAR(100) | tutor_agent            |
| created_at   | DATETIME     | 创建时间                   |
| updated_at   | DATETIME     | 更新时间                   |

---

## 64.4 Memory 示例

```json
{
  "preferred_language":"Python",
  "study_time":"night",
  "difficulty":"medium"
}
```

Memory Value 保存 JSON。

---

## 64.5 Confidence

Memory 可衰减。

0~1。

Agent 更新。

---

## 64.6 API

| API                 | 功能       |
| ------------------- | -------- |
| GET /agent/memory   | Memory列表 |
| PATCH /agent/memory | 更新Memory |

---

# 第六十五章 Conversation 生命周期

## 65.1 生命周期

```mermaid
flowchart TD

Create Conversation

↓

User Message

↓

Planner

↓

Retriever

↓

Agent

↓

Citation

↓

Memory Update

↓

Archive
```

---

## 65.2 Memory 更新策略

不是每句话更新。

更新条件：

- 用户连续行为。
- Quiz结果。
- Homework结果。
- Tutor总结。

---

## 65.3 Conversation 删除

删除 Conversation。

保留 Memory。

保留 Citation（可选）。

---

# 第六十六章 Workflow Trace 前端设计

## 66.1 Timeline

展示：

```text
09:30 Retriever 检索教材

09:31 Lesson Agent 教案生成

09:32 PPT Agent 生成PPT

09:33 Quiz Agent 命题
```

实时刷新。

---

## 66.2 Workflow Detail

点击展开：

输入。

输出。

Token。

耗时。

Citation。

---

## 66.3 Debug 页面

AI Debug 页面展示：

Workflow。

Tool。

Retriever。

Prompt Version。

方便开发。

---

# 第六十七章 Repository 设计（AI Engine）

## ConversationRepository

方法：

create()

list()

archive()

delete()

---

## MessageRepository

方法：

append()

history()

delete()

---

## WorkflowRepository

方法：

create()

update_status()

finish()

---

## TaskRepository

方法：

append_step()

update_step()

list_steps()

---

## MemoryRepository

方法：

upsert()

list_memory()

delete_memory()

---

# 第六十八章 Service 设计（AI Engine）

## ConversationService

负责：

创建会话。

保存消息。

流式回复。

---

## WorkflowService

负责：

Workflow 生命周期。

Step 更新。

失败恢复。

---

## MemoryService

负责：

Memory 更新。

Memory 检索。

Memory 衰减。

---

## PromptService

负责：

Prompt Version。

System Prompt。

Agent Prompt。

统一管理。

---

# 第六十九章 AI Engine 与 RAG 集成

## 69.1 Conversation → Retriever

Conversation 提供：

课程。

章节。

用户身份。

Retriever 返回 Context。

---

## 69.2 Conversation → Citation

Assistant 回复。

Citation 保存。

Conversation_count 更新。

---

## 69.3 Workflow → Retriever

Retriever Step 保存 Tool。

Task Trace 可回放。

---

## 69.4 Memory → Tutor Agent

Tutor Agent Prompt：

加入 Memory。

形成个性化教学。

---

# 第七十章 Demo 升级映射

## Demo AI_HISTORY

迁移：

Conversation。

Message。

---

## Demo Agent 动画

迁移：

Workflow。

Task。

Timeline。

---

## Demo callAI()

改造：

ConversationService。

WorkflowService。

MemoryService。

RetrieverService。

统一 AI Engine。

---

# 第七十一章 Checklist（AI Engine）

## 数据表

- [ ] ai_conversations
- [ ] ai_messages
- [ ] agent_workflows
- [ ] agent_tasks
- [ ] agent_memory

## Repository

- [ ] ConversationRepository
- [ ] MessageRepository
- [ ] WorkflowRepository
- [ ] TaskRepository
- [ ] MemoryRepository

## Service

- [ ] ConversationService
- [ ] WorkflowService
- [ ] MemoryService
- [ ] PromptService

## API

- [ ] Conversation CRUD
- [ ] Message History
- [ ] Workflow Timeline
- [ ] Agent Step
- [ ] Memory Update

## AI 集成

- [ ] Workflow Trace
- [ ] Citation
- [ ] Memory Injection
- [ ] Tool Call Log

---

# 本章输出成果

AI Engine 数据库设计完成。

Backend + AI 成员完成本章节后，可以实现：

- AI 对话历史永久保存。
- Multi-Agent 工作流可追踪。
- Agent Timeline 可视化。
- 长期 Memory。
- Citation 与 Conversation 关联。
- Prompt 可版本化管理。

下一章节进入 Learning Profile 数据库设计（学习画像 / 掌握度 / 成长热力图 / 学习轨迹）。

---

**DOC03 Part06 完成。**
