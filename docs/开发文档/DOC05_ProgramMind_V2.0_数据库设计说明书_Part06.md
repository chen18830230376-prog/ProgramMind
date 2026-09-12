# ProgramMind V2.0 数据库设计说明书

# Part06 —— AI Domain（AI 多智能体数据库设计）

> 文档版本：V2.0
> 更新时间：2026-09
> 模块负责人：AI（Multi-Agent）+ Backend（数据库）
> 技术栈：FastAPI + SQLAlchemy + LangGraph + Ollama + Qwen3 + DeepSeek

---

# 第一章 AI Domain 模块说明

## 1.1 模块定位

AI Domain 是 ProgramMind 的智能引擎数据中心。

负责管理：

- AI Tutor 多轮聊天。
- Teacher Agent 教案生成。
- Research Agent 科研助手。
- Planner Agent Workflow。
- Prompt Template。
- Conversation Memory。
- Citation 引用。
- Token 消耗统计。

所有 AI Agent 都共享这一层数据库。

---

## 1.2 AI 数据流（Multi-Agent）

用户输入问题

↓

Planner Agent

↓

Workflow Builder

↓

Retriever（RAG）

↓

Tutor / Teacher / Research Agent

↓

LLM（Qwen / DeepSeek）

↓

Citation Agent

↓

Conversation 保存

↓

Memory 更新

---

## 1.3 数据库结构（6 张核心表）

| 表名                  | 功能                  |
| ------------------- | ------------------- |
| conversations       | AI 会话               |
| ai_messages         | 聊天消息                |
| ai_workflows        | Workflow 执行记录       |
| prompt_templates    | Prompt 模板           |
| conversation_memory | Conversation Memory |
| model_usage_logs    | Token / 模型调用日志      |

ER 图：

users

↓

conversations

↓

ai_messages

↓

citation_records（Knowledge Domain）

↓

conversation_memory

↓

learning_mirror

Workflow 独立关联 conversations。

---

# 第二章 conversations（AI 会话）

## 2.1 表定位

保存一次 AI 会话。

相当于 ChatGPT 左侧聊天列表。

支持多个 Agent。

支持课程绑定。

支持继续聊天。

---

## 2.2 字段设计（完整版）

| 字段                 | 类型           | 说明                             |
| ------------------ | ------------ | ------------------------------ |
| id                 | UUID         | 主键                             |
| user_id            | UUID         | 用户                             |
| course_id          | UUID         | 所属课程（可空）                       |
| conversation_title | VARCHAR(200) | 会话标题                           |
| conversation_type  | ENUM         | tutor/teacher/research/general |
| current_model      | VARCHAR(50)  | 当前模型                           |
| current_agent      | VARCHAR(50)  | 当前Agent                        |
| summary            | LONGTEXT     | AI总结                           |
| total_messages     | INT          | 消息数量                           |
| status             | ENUM         | active/archived/deleted        |
| created_at         | DATETIME     | 创建时间                           |
| updated_at         | DATETIME     | 更新时间                           |

---

## 2.3 conversation_type

| 类型       | 用途             |
| -------- | -------------- |
| tutor    | AI Tutor       |
| teacher  | Teacher Agent  |
| research | Research Agent |
| planner  | Planner Agent  |
| general  | 通用聊天           |

---

## 2.4 MySQL DDL

```sql
CREATE TABLE conversations (

    id CHAR(36) PRIMARY KEY,

    user_id CHAR(36) NOT NULL,

    course_id CHAR(36),

    conversation_title VARCHAR(200),

    conversation_type ENUM(
        'general',
        'tutor',
        'teacher',
        'research',
        'planner'
    ),

    current_model VARCHAR(50),

    current_agent VARCHAR(50),

    summary LONGTEXT,

    total_messages INT DEFAULT 0,

    status ENUM(
        'active',
        'archived',
        'deleted'
    ) DEFAULT 'active',

    created_at DATETIME(6),

    updated_at DATETIME(6),

    FOREIGN KEY(user_id)
        REFERENCES users(id),

    FOREIGN KEY(course_id)
        REFERENCES courses(id)
);
```

---

## 2.5 SQLAlchemy Model

```python
class Conversation(Base, BaseModel):

    __tablename__="conversations"

    user_id = mapped_column(ForeignKey("users.id"))

    course_id = mapped_column(ForeignKey("courses.id"))

    conversation_title = mapped_column(String(200))

    conversation_type = mapped_column(Enum(ConversationType))

    current_model = mapped_column(String(50))

    current_agent = mapped_column(String(50))

    summary = mapped_column(Text)

    messages = relationship("AIMessage")

    workflows = relationship("AIWorkflow")
```

---

# 第三章 ai_messages（聊天消息）

## 3.1 表定位

保存每一条聊天消息。

支持：

用户消息。

AI 回复。

Tool Calling。

Workflow 输出。

Streaming。

---

## 3.2 字段设计（完整版）

| 字段              | 类型       |
| --------------- | -------- |
| id              | UUID     |
| conversation_id | UUID     |
| role            | ENUM     |
| content         | LONGTEXT |
| model_name      | VARCHAR  |
| agent_name      | VARCHAR  |
| prompt_version  | VARCHAR  |
| token_input     | INT      |
| token_output    | INT      |
| latency_ms      | INT      |
| citation_count  | INT      |
| created_at      | DATETIME |

---

## 3.3 role

| Role      |
| --------- |
| user      |
| assistant |
| system    |
| tool      |

支持 Tool Calling。

---

## 3.4 DDL

```sql
CREATE TABLE ai_messages (

    id CHAR(36) PRIMARY KEY,

    conversation_id CHAR(36),

    role ENUM(
        'user',
        'assistant',
        'system',
        'tool'
    ),

    content LONGTEXT,

    model_name VARCHAR(50),

    agent_name VARCHAR(50),

    prompt_version VARCHAR(30),

    token_input INT,

    token_output INT,

    latency_ms INT,

    citation_count INT DEFAULT 0,

    created_at DATETIME(6),

    FOREIGN KEY(conversation_id)
        REFERENCES conversations(id)
        ON DELETE CASCADE
);
```

---

## 3.5 SQLAlchemy Model

```python
class AIMessage(Base, BaseModel):

    __tablename__="ai_messages"

    conversation_id = mapped_column(ForeignKey("conversations.id"))

    role = mapped_column(Enum(MessageRole))

    content = mapped_column(Text)

    model_name = mapped_column(String(50))

    agent_name = mapped_column(String(50))

    token_input = mapped_column(Integer)

    token_output = mapped_column(Integer)

    latency_ms = mapped_column(Integer)
```

---

## 3.6 Streaming 保存策略

Streaming Token 不写数据库。

回答结束后写一条完整 assistant message。

---

# 第四章 ai_workflows（多智能体 Workflow）

## 4.1 表定位

保存 AI Workflow。

例如：

AI备课。

AI出题。

AI复习计划。

AI实验生成。

每次 Workflow 一条记录。

---

## 4.2 Workflow 生命周期

pending

↓

planning

↓

retrieving

↓

executing

↓

completed

失败：

failed

取消：

cancelled

---

## 4.3 字段设计（完整版）

| 字段              | 类型       |
| --------------- | -------- |
| id              | UUID     |
| conversation_id | UUID     |
| workflow_type   | ENUM     |
| planner_agent   | VARCHAR  |
| current_step    | VARCHAR  |
| total_steps     | INT      |
| progress        | DECIMAL  |
| workflow_status | ENUM     |
| workflow_result | JSON     |
| started_at      | DATETIME |
| finished_at     | DATETIME |

---

## 4.4 workflow_type

| Workflow            |
| ------------------- |
| lesson_generation   |
| quiz_generation     |
| ppt_generation      |
| homework_generation |
| review_plan         |
| learning_analysis   |

---

## 4.5 workflow_result JSON

```json
{
  "outline":"...",
  "ppt_pages":12,
  "quiz_count":20
}
```

---

# 第五章 prompt_templates（Prompt 模板）

## 5.1 为什么单独建表

Prompt 不写代码里。

方便版本管理。

支持后台修改。

支持 Prompt A/B Test。

---

## 5.2 字段设计

| 字段              | 类型       |
| --------------- | -------- |
| id              | UUID     |
| prompt_name     | VARCHAR  |
| agent_name      | VARCHAR  |
| version         | VARCHAR  |
| system_prompt   | LONGTEXT |
| template_prompt | LONGTEXT |
| description     | TEXT     |
| enabled         | BOOLEAN  |
| created_at      | DATETIME |

---

## Prompt 示例

Tutor Prompt。

Teacher Prompt。

Research Prompt。

Evaluation Prompt。

Planner Prompt。

---

## Prompt Version

例如：

v1.0

v2.0

v2.1-hotfix

AIMessage 保存 prompt_version。

---

# 第六章 conversation_memory（Conversation Memory）

## 6.1 表定位

Conversation Memory。

区别于 Learning Mirror。

这里只保存 AI 对话记忆。

---

## Memory 分类

| Memory  | 描述      |
| ------- | ------- |
| short   | 当前聊天上下文 |
| summary | 自动摘要    |
| long    | 长期偏好    |

---

## 字段设计

| 字段              | 类型       |
| --------------- | -------- |
| id              | UUID     |
| conversation_id | UUID     |
| memory_type     | ENUM     |
| memory_content  | LONGTEXT |
| token_size      | INT      |
| created_at      | DATETIME |
| updated_at      | DATETIME |

---

## Memory 更新策略

消息超过 15 条：

自动 Summary。

旧消息压缩。

Prompt Builder 使用 Summary。

---

# 第七章 model_usage_logs（模型调用日志）

## 7.1 模块定位

记录所有模型调用。

用于：

Token统计。

费用统计。

性能分析。

答辩展示。

---

## 字段设计

| 字段              | 类型       |
| --------------- | -------- |
| id              | UUID     |
| user_id         | UUID     |
| conversation_id | UUID     |
| model_name      | VARCHAR  |
| provider        | VARCHAR  |
| token_input     | INT      |
| token_output    | INT      |
| latency_ms      | INT      |
| success         | BOOLEAN  |
| created_at      | DATETIME |

---

## Provider

| Provider |
| -------- |
| Ollama   |
| Qwen     |
| DeepSeek |

---

# 第八章 AI Conversation 数据流

用户输入

↓

Conversation 创建

↓

Message(user)

↓

Workflow

↓

Retriever

↓

Citation

↓

LLM

↓

Message(assistant)

↓

Memory 更新

↓

ModelUsageLog 写入

---

# 第九章 Workflow Step 日志设计

Workflow JSON 示例：

```json
[
 {
   "step":"Planner",
   "duration":500,
   "status":"success"
 },
 {
   "step":"Retriever",
   "duration":210
 }
]
```

保存在 workflow_result。

前端可展示执行过程。

---

# 第十章 Prompt Builder 数据关系

Conversation

↓

Prompt Template

↓

Retriever Context

↓

Memory Summary

↓

User Prompt

↓

LLM Prompt

Prompt 不保存最终 Prompt。

保存模板版本即可。

---

# 第十一章 Repository 设计

## ConversationRepository

create()

rename()

archive()

delete()

list()

detail()

---

## MessageRepository

append_message()

list_messages()

delete_messages()

count_tokens()

---

## WorkflowRepository

create()

update_progress()

finish()

cancel()

logs()

---

## PromptRepository

list()

enable()

disable()

update_prompt()

---

## MemoryRepository

save_summary()

list_memory()

delete_memory()

---

## UsageRepository

record_usage()

statistics()

daily_usage()

model_usage()

---

# 第十二章 Service 设计

ConversationService。

WorkflowService。

PromptBuilderService。

MemoryService。

CitationService。

UsageStatisticsService。

ModelRouterService。

---

# 第十三章 索引设计（AI Domain）

| 表                   | 索引                           |
| ------------------- | ---------------------------- |
| conversations       | user_id                      |
| conversations       | course_id                    |
| ai_messages         | conversation_id + created_at |
| ai_messages         | model_name                   |
| ai_workflows        | conversation_id              |
| ai_workflows        | workflow_status              |
| prompt_templates    | agent_name + enabled         |
| conversation_memory | conversation_id              |
| model_usage_logs    | user_id + created_at         |

---

# 第十四章 Seed 初始化规范

初始化 Prompt：

Tutor Prompt。

Teacher Prompt。

Research Prompt。

Planner Prompt。

Evaluation Prompt。

版本：

v2.0。

默认启用。

---

# 第十五章 AI Domain Checklist

## Conversation

- [ ] conversations
- [ ] 多Agent聊天
- [ ] 标题自动生成

## Message

- [ ] ai_messages
- [ ] Token统计
- [ ] Citation数量

## Workflow

- [ ] AI Workflow
- [ ] Progress
- [ ] Result JSON

## Prompt

- [ ] Prompt模板
- [ ] Prompt版本
- [ ] Prompt启停

## Memory

- [ ] Short Memory
- [ ] Summary Memory
- [ ] Long Memory

## Usage Logs

- [ ] Token统计
- [ ] Provider统计
- [ ] 延迟统计

---

# 第十六章 本章开发成果

AI Domain 完成后，ProgramMind V2.0 将具备：

- AI Tutor 多轮会话数据库。
- Multi-Agent Workflow 持久化。
- Prompt 模板管理系统。
- Conversation Memory 系统。
- Token 消耗统计。
- 多模型路由记录（Qwen / DeepSeek / Ollama）。
- 支撑 DOC04 AI Engine 全部接口的数据底座。
