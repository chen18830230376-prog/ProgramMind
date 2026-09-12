# ProgramMind V2.0 API 接口设计说明书

# Part07 —— AI Engine（Multi-Agent + Workflow + SSE）接口设计（完整版）

> 文档版本：V2.0
> 
> 模块负责人：AI（大模型/RAG/Agent）+ Backend（FastAPI）
> 
> 技术栈：Qwen3 / DeepSeek / Ollama / FastAPI / LangGraph / FAISS / SSE

---

# 第一章 AI Engine 模块定位

## 1.1 为什么要独立 AI Engine

ProgramMind V1 Demo 中 AI 是：

用户输入 → llm.py → Mock 文本。

ProgramMind V2 中 AI Engine 是：

用户输入

↓

Planner Agent

↓

RAG Retriever

↓

多个 Agent 协同

↓

Workflow

↓

LLM Streaming

↓

Citation + Memory + Tool Result

这是整个项目最大的技术升级。

---

## 1.2 AI Engine 总体架构

```
                    User Prompt
                         │
                         ▼
                 AI Gateway(API)
                         │
            ┌────────────┼────────────┐
            ▼            ▼            ▼
      Conversation     Workflow     Memory
            │            │            │
            └──────┬─────┴────────────┘
                   ▼
              Planner Agent
                   │
     ┌─────────────┼─────────────┐
     ▼             ▼             ▼
 TutorAgent   TeacherAgent   ResearchAgent
     │             │             │
     ├──────RAG Retriever────────┤
     ▼             ▼             ▼
 EvaluationAgent CitationAgent PromptBuilder
           │
           ▼
        LLM Provider
     (Qwen/DeepSeek/Ollama)
           │
           ▼
       SSE Streaming Output
```

AI Engine 所有 Agent 共用 Memory、Knowledge Base、Citation。

---

## 1.3 Backend 目录结构

```
backend/app/ai_engine/

├── gateway.py                # AI统一入口
├── conversation_service.py    # 对话管理
├── workflow_service.py        # Workflow调度
├── prompt_builder.py          # Prompt模板构建
├── citation_service.py        # Citation生成
├── stream_service.py          # SSE输出
│
├── agents/
│   ├── planner_agent.py
│   ├── tutor_agent.py
│   ├── teacher_agent.py
│   ├── evaluation_agent.py
│   ├── research_agent.py
│   └── citation_agent.py
│
├── providers/
│   ├── qwen_provider.py
│   ├── deepseek_provider.py
│   ├── ollama_provider.py
│   └── provider_manager.py
│
├── memory/
│   ├── short_memory.py
│   ├── long_memory.py
│   └── summary_memory.py
│
└── tools/
    ├── rag_tool.py
    ├── search_tool.py
    ├── statistics_tool.py
    └── workflow_tool.py
```

---

# 第二章 AI Engine API 总览（26个接口）

## Conversation（8）

| API | Method | 描述          |
| --- | ------ | ----------- |
| 701 | POST   | 普通AI对话      |
| 702 | POST   | 流式AI对话（SSE） |
| 703 | GET    | 获取聊天历史      |
| 704 | DELETE | 删除聊天        |
| 705 | PATCH  | 重命名聊天       |
| 706 | GET    | 聊天详情        |
| 707 | POST   | 继续聊天        |
| 708 | POST   | 清空上下文       |

---

## Workflow（6）

| API | Method | 描述           |
| --- | ------ | ------------ |
| 709 | POST   | 启动Workflow   |
| 710 | GET    | Workflow状态   |
| 711 | GET    | Workflow执行日志 |
| 712 | POST   | 终止Workflow   |
| 713 | POST   | 恢复Workflow   |
| 714 | GET    | Workflow历史   |

---

## Agent（6）

| API | Method | 描述               |
| --- | ------ | ---------------- |
| 715 | POST   | Planner Agent    |
| 716 | POST   | Tutor Agent      |
| 717 | POST   | Teacher Agent    |
| 718 | POST   | Evaluation Agent |
| 719 | POST   | Research Agent   |
| 720 | POST   | Citation Agent   |

---

## Prompt & Memory（6）

| API | Method | 描述                   |
| --- | ------ | -------------------- |
| 721 | GET    | Prompt模板             |
| 722 | PATCH  | 更新Prompt             |
| 723 | GET    | Memory列表             |
| 724 | DELETE | 删除Memory             |
| 725 | POST   | 总结Memory             |
| 726 | POST   | RAG + Prompt Builder |

---

# 第三章 Conversation API（聊天系统）

## API-701 普通 AI 对话

### URL

```
POST /api/ai/chat
```

---

### 请求

```json
{
  "conversation_id":"uuid",
  "course_id":"uuid",
  "agent":"tutor",
  "message":"Python中的列表是什么？"
}
```

---

### Backend 流程

ConversationService

↓

Planner

↓

Tutor Agent

↓

Retriever

↓

LLM

↓

Citation

↓

保存 Memory

---

### 返回

```json
{
  "answer":"列表(List)...",
  "citations":[
    {
      "document":"Python教材",
      "page":15
    }
  ]
}
```

---

## API-702 流式 AI 对话（SSE）

### URL

```
POST /api/ai/chat/stream
```

---

### Response

```
event:start

event:token

event:token

event:citation

event:end
```

---

### Streaming Event

| Event    | 内容      |
| -------- | ------- |
| start    | 开始回答    |
| token    | Token流  |
| citation | 引用来源    |
| workflow | Agent步骤 |
| end      | 结束      |

---

### Frontend

EventSource。

Markdown Streaming。

---

## API-703 获取聊天历史

返回：

所有 Conversation。

最后一句。

更新时间。

消息数量。

---

## API-704 删除聊天

逻辑删除 Conversation。

保留 Memory。

---

## API-705 修改聊天标题

自动标题。

人工修改标题。

---

## API-706 获取聊天详情

返回：

消息数组。

Citation。

Workflow。

Agent。

---

## API-707 继续聊天

自动带上下文。

Long Memory。

Short Memory。

---

## API-708 清空聊天上下文

删除：

Short Memory。

Conversation Messages。

保留 Long Memory。

---

# 第四章 Workflow API

## API-709 启动 Workflow

### URL

```
POST /api/ai/workflow
```

---

### 请求

```json
{
  "workflow_type":"lesson_generation",
  "course_id":"uuid",
  "chapter_id":"uuid"
}
```

---

### Workflow Type

| Workflow            | 描述     |
| ------------------- | ------ |
| lesson_generation   | AI备课   |
| ppt_generation      | AI PPT |
| homework_generation | AI作业   |
| quiz_generation     | AI命题   |
| review_plan         | AI复习规划 |
| student_analysis    | AI学情总结 |

---

### 返回

workflow_id。

status=running。

---

## API-710 查询 Workflow 状态

返回：

当前步骤。

Agent。

耗时。

百分比。

---

## API-711 Workflow 执行日志

返回

```json
[
  {
    "step":"Planner",
    "status":"success",
    "duration":1.2
  }
]
```

---

## API-712 停止 Workflow

取消执行。

---

## API-713 恢复 Workflow

继续执行下一节点。

---

## API-714 Workflow 历史

分页。

类型过滤。

用户过滤。

---

# 第五章 Planner Agent

## API-715 Planner Agent

Planner 不回答问题。

Planner 负责拆任务。

---

输入：

课程。

用户问题。

目标。

输出：

Workflow DAG。

---

示例

```json
{
  "steps":[
    "Retrieve Knowledge",
    "Generate Outline",
    "Generate Homework"
  ]
}
```

---

Planner 输出写 workflow_steps。

---

# 第六章 Tutor Agent

## API-716 Tutor Agent

学生学习智能体。

输入：

课程。

章节。

问题。

输出：

教学回答。

知识点。

引用。

建议。

---

必须调用：

RAG Tool。

Memory Tool。

Citation Tool。

---

# 第七章 Teacher Agent

## API-717 Teacher Agent

教师智能体。

支持：

教案。

PPT。

命题。

实验。

课程总结。

输入：

课程。

章节。

目标。

输出：

Markdown。

JSON。

Workflow。

---

# 第八章 Evaluation Agent

## API-718 Evaluation Agent

负责评价。

输入：

Homework。

Quiz。

Experiment。

Learning Records。

输出：

知识掌握变化。

成长建议。

风险等级。

---

更新：

mastery_records。

growth_profile。

---

# 第九章 Research Agent

## API-719 Research Agent

V2 预留。

支持：

论文。

知识图谱。

科研助手。

实验设计。

文献综述。

---

# 第十章 Citation Agent

## API-720 Citation Agent

输入：

Chunk IDs。

输出：

引用列表。

页码。

章节。

文档链接。

---

# 第十一章 Prompt Template API

## API-721 获取 Prompt 模板

返回：

Tutor Prompt。

Teacher Prompt。

Evaluation Prompt。

Research Prompt。

Planner Prompt。

---

## API-722 更新 Prompt 模板

管理员接口。

修改 Prompt。

版本管理。

---

# 第十二章 Memory API

## Memory 分类

| Memory         | 描述       |
| -------------- | -------- |
| Short Memory   | 当前聊天上下文  |
| Long Memory    | 用户长期学习记录 |
| Summary Memory | 自动摘要     |

---

## API-723 获取 Memory

分页。

Conversation。

用户。

Agent。

---

## API-724 删除 Memory

删除：

Conversation Memory。

Long Memory。

---

## API-725 总结 Memory

LLM 自动总结。

压缩上下文。

写 Summary Memory。

---

# 第十三章 Prompt Builder（核心）

## API-726 Prompt Builder

输入：

用户问题。

课程。

Agent。

Memory。

Retriever Result。

输出：

最终 Prompt。

---

### Prompt 拼接顺序

```
System Prompt

↓

Agent Prompt

↓

Course Context

↓

Retrieved Chunks

↓

Memory Summary

↓

User Prompt
```

这是整个 AI Engine 唯一 Prompt 构建入口。

---

# 第十四章 Tool Calling 规范

AI 可以调用 Tool。

---

## Tool 1 RAG Tool

输入：

问题。

课程。

返回：

Chunks。

Citation。

---

## Tool 2 Statistics Tool

读取：

Analytics。

Mastery。

Learning Records。

---

## Tool 3 Search Tool

课程资源搜索。

知识搜索。

---

## Tool 4 Workflow Tool

启动 Workflow。

查询 Workflow。

---

# 第十五章 Provider Manager

统一模型入口。

---

## Provider

| Provider         | 模型          |
| ---------------- | ----------- |
| QwenProvider     | Qwen3-14B   |
| DeepSeekProvider | DeepSeek-V3 |
| OllamaProvider   | 本地模型        |

---

ProviderManager 自动路由。

Tutor 默认：

Qwen。

Code：

DeepSeek。

Research：

Qwen Long Context。

---

# 第十六章 SSE 规范

统一返回事件。

```
start

token

agent

citation

workflow

memory

done
```

---

每次 Token 都带 index。

支持断点恢复。

---

# 第十七章 Repository 设计

ConversationRepository。

MessageRepository。

WorkflowRepository。

MemoryRepository。

PromptRepository。

AgentLogRepository。

---

# 第十八章 Service 设计

ConversationService。

WorkflowService。

PromptBuilderService。

CitationService。

MemoryService。

ProviderManager。

---

# 第十九章 Frontend SDK

```
ai.ts

chat()

streamChat()

getConversationList()

getConversationDetail()

renameConversation()

deleteConversation()

continueConversation()

clearConversation()

startWorkflow()

getWorkflowStatus()

getWorkflowLogs()

stopWorkflow()

resumeWorkflow()

getWorkflowHistory()

planner()

tutor()

teacher()

evaluation()

research()

citation()

getPromptTemplates()

updatePromptTemplate()

getMemory()

deleteMemory()

summarizeMemory()

buildPrompt()
```

---

# 第二十章 AI Engine Checklist

## Conversation

- [ ] 普通聊天
- [ ] SSE聊天
- [ ] 聊天历史
- [ ] 删除聊天
- [ ] 重命名聊天

## Workflow

- [ ] Workflow启动
- [ ] Workflow日志
- [ ] Workflow状态
- [ ] Workflow历史

## Agent

- [ ] Planner Agent
- [ ] Tutor Agent
- [ ] Teacher Agent
- [ ] Evaluation Agent
- [ ] Research Agent
- [ ] Citation Agent

## Memory

- [ ] Short Memory
- [ ] Long Memory
- [ ] Summary Memory

## Prompt Builder

- [ ] Prompt模板
- [ ] Prompt拼接
- [ ] Prompt版本管理

## Provider

- [ ] Qwen
- [ ] DeepSeek
- [ ] Ollama

## Streaming

- [ ] SSE Token
- [ ] Citation Streaming
- [ ] Workflow Streaming

---

# 第二十一章 AI Engine 开发成果（挑战杯核心）

完成本章节后，ProgramMind 将具备：

- ✅ 多智能体协同（5 个 Agent）。
- ✅ AI Workflow 编排。
- ✅ RAG + Prompt Builder。
- ✅ Citation 可追溯回答。
- ✅ Conversation Memory。
- ✅ SSE 流式输出。
- ✅ 多模型路由（Qwen / DeepSeek / Ollama）。

下一章节进入 **DOC04 Part08 —— Growth Center（学习状态镜像 / 成长画像 / 推荐系统接口设计）**，这是 ProgramMind V2.0 最后一份 API 文档，也是整个项目的数据闭环模块。
