# ProgramMind V2.0 后端开发规范

# Part06.3 —— Prompt Builder、Conversation Memory 与 Tool Calling 开发规范（完整版）

> 文档版本：V2.0
> 更新时间：2026-09
> 模块负责人：AI（Prompt Engine）
> 技术栈：LangChain + LangGraph + SQLAlchemy + FastAPI

---

# 第一章 Prompt Engine 模块定位

## 1.1 Prompt Builder 在 AI Engine 中的位置

Prompt Builder 是 ProgramMind AI Engine 的 Prompt 生成中心。

负责组合：

- System Prompt
- Agent Prompt
- Course Prompt
- Conversation Memory
- Learning Mirror Context
- RAG Context
- User Question

最终生成发送给 LLM 的 Prompt。

---

## 1.2 Prompt Builder 数据流

User Question

↓

Conversation Memory

↓

Learning Mirror

↓

Retriever Context

↓

Citation Context

↓

Prompt Template

↓

Prompt Builder

↓

LLM

---

## 1.3 Prompt Builder 原则

ProgramMind 不允许把 Prompt 写死在代码中。

所有 Prompt 必须：

- 支持版本管理。
- 支持数据库管理。
- 支持后台修改。
- 支持不同 Agent 使用不同 Prompt。

---

# 第二章 Prompt 模块目录规范

## 2.1 prompt/

```text
prompt/

prompt_builder.py

prompt_registry.py

prompt_loader.py

prompt_templates.py

prompt_validator.py

prompt_version_manager.py
```

职责分离。

---

## 2.2 每个模块职责

| 文件                        | 职责           |
| ------------------------- | ------------ |
| prompt_builder.py         | 拼接 Prompt    |
| prompt_registry.py        | 注册 Prompt    |
| prompt_loader.py          | 加载数据库 Prompt |
| prompt_templates.py       | 默认 Prompt    |
| prompt_validator.py       | Prompt 校验    |
| prompt_version_manager.py | Prompt 版本管理  |

---

# 第三章 Prompt Registry

## 3.1 Registry 定位

统一管理所有 Prompt。

Planner 不直接读取 Prompt 文件。

统一从 Registry 获取。

---

## 3.2 Prompt 分类

| Prompt                | 用途            |
| --------------------- | ------------- |
| tutor_system          | AI Tutor      |
| teacher_system        | AI 教师助手       |
| research_system       | AI 科研助手       |
| planner_system        | Planner Agent |
| evaluation_system     | AI 评价         |
| recommendation_system | AI 推荐         |

---

## 3.3 Registry 返回内容

Prompt ID。

Version。

Agent。

System Prompt。

Template Prompt。

Enabled。

---

# 第四章 Prompt Template 数据结构

## 4.1 PromptTemplateSchema

字段：

| 字段              | 类型   |
| --------------- | ---- |
| prompt_id       | UUID |
| prompt_name     | str  |
| agent_name      | str  |
| version         | str  |
| system_prompt   | str  |
| template_prompt | str  |
| enabled         | bool |

数据库 prompt_templates 对应。

---

## 4.2 Version 命名规范

例如：

v2.0

v2.1

v2.1-hotfix

Conversation 保存 prompt_version。

---

## 4.3 Prompt 示例（Tutor）

包含：

角色。

教学目标。

回答规则。

引用规则。

禁止内容。

输出 Markdown。

Prompt 保持模板化。

---

# 第五章 Prompt Builder（核心）

## 5.1 Prompt Builder 输入

WorkflowState。

Conversation Summary。

Retriever Chunk。

Learning Mirror。

Course Context。

User Question。

---

## 5.2 Prompt Builder 输出

最终 Prompt String。

Token 数。

Metadata。

---

## 5.3 Prompt 拼接顺序（固定）

```text
System Prompt

↓

Agent Prompt

↓

Course Prompt

↓

Conversation Summary

↓

Learning Mirror

↓

Retriever Context

↓

Citation Context

↓

User Question
```

禁止调整顺序。

---

## 5.4 Prompt Token 控制

最大 Prompt：

3000 Tokens。

Context：

2500 Tokens。

Summary：

300 Tokens。

Question：

200 Tokens。

超出自动裁剪。

---

# 第六章 Course Prompt Builder

## 6.1 为什么需要 Course Prompt

AI 必须知道课程上下文。

例如：

Python程序设计。

数据结构。

计算机网络。

Prompt 自动加入课程信息。

---

## 6.2 Course Prompt 内容

课程名称。

课程目标。

章节。

知识点。

实验。

当前学习进度。

由 CourseService 提供。

---

# 第七章 Learning Mirror Context Builder

## 7.1 Mirror Context 定位

AI Tutor 个性化教学的重要来源。

读取 Learning Mirror。

---

## 7.2 Mirror Prompt 内容

综合成长分。

六维状态。

风险等级。

掌握薄弱知识点。

推荐学习目标。

---

## 7.3 示例 Context

当前学习状态：

Mastery：0.62

Risk：0.41

薄弱知识点：

链表。

队列。

递归。

AI Tutor 自动调整回答难度。

---

# 第八章 RAG Context Builder

## 8.1 Retriever Context

Retriever 返回 TopK Chunk。

Builder 拼接。

---

## 8.2 Citation Context

每个 Chunk 附带：

文档名称。

章节。

页码。

Similarity。

Prompt 引导模型引用来源。

---

## 8.3 Context 裁剪策略

Similarity 排序。

保留 TopK。

Token 超出裁剪最低分 Chunk。

---

# 第九章 Conversation Memory 系统（核心）

## 9.1 Memory 分类

ProgramMind Memory 分三层。

| Memory         | 描述     |
| -------------- | ------ |
| Short Memory   | 最近消息   |
| Summary Memory | 自动摘要   |
| Long Memory    | 长期学习偏好 |

三层共同组成 Conversation Context。

---

## 9.2 Memory 生命周期

消息新增

↓

Short Memory 更新

↓

超过15条消息

↓

Summary Generator

↓

Summary Memory 更新

↓

Long Memory 更新（可选）

---

# 第十章 Short Memory

## 10.1 定位

保存最近聊天记录。

默认：

最近 10 条消息。

---

## 10.2 保存规则

User Message。

Assistant Message。

Tool Message。

System Message。

保持顺序。

---

## 10.3 Token 控制

超过 Token 限制。

删除最旧消息。

Summary 不删除。

---

# 第十一章 Summary Memory

## 11.1 Summary Memory 定位

自动压缩历史聊天。

减少 Token。

---

## 11.2 Summary Trigger 条件

满足任一：

消息数量 ≥15。

Token ≥4000。

Conversation Idle。

自动摘要。

---

## 11.3 Summary Prompt

输入：

最近聊天。

输出：

200~300 Tokens Summary。

数据库保存 summary_memory。

---

## 11.4 Summary 更新策略

旧 Summary。

+

新增消息。

↓

重新摘要。

不是覆盖全部历史。

---

# 第十二章 Long Memory

## 12.1 Long Memory 定位

保存长期学习偏好。

例如：

喜欢代码示例。

学习目标。

课程偏好。

语言偏好。

---

## 12.2 Long Memory 来源

AI 推断。

用户设置。

教师设置。

Recommendation。

---

## 12.3 Long Memory 示例

```json
{
  "preferred_language":"Python",
  "difficulty":"beginner",
  "goal":"考研408"
}
```

保存在 conversation_memory。

---

# 第十三章 Memory Manager

## 13.1 MemoryManager 职责

统一管理 Memory。

提供：

append_message()

build_context()

summarize()

load_summary()

save_summary()

---

## 13.2 Memory 更新流程

Message 保存。

↓

Short Memory 更新。

↓

Summary 判断。

↓

Long Memory 更新。

↓

Conversation 更新。

---

## 13.3 Memory 与 Database

对应数据库：

conversation_memory。

conversations.summary。

ai_messages。

三张表联动。

---

# 第十四章 Tool Calling 系统

## 14.1 Tool Calling 定位

Agent 不直接访问业务模块。

统一通过 Tool。

---

## 14.2 Tool Registry

```text
tools/

tool_registry.py

rag_tool.py

mirror_tool.py

course_tool.py

quiz_tool.py

recommendation_tool.py
```

所有 Tool 注册到 Registry。

---

## 14.3 Tool 生命周期

Planner 输出 Tool。

↓

Tool Registry。

↓

执行 Tool。

↓

返回 Tool Result。

↓

Prompt Builder。

---

# 第十五章 rag_tool（知识检索）

## 15.1 输入

Question。

Course。

TopK。

---

## 15.2 输出

Chunks。

Citation。

Similarity。

供 Prompt Builder 使用。

---

## 15.3 不负责生成答案

rag_tool 只负责 Context。

---

# 第十六章 mirror_tool（学习状态工具）

## 16.1 输入

Student ID。

Course ID。

---

## 16.2 输出

Learning Mirror。

Mastery。

Risk。

Recommendation。

成长状态。

---

## 16.3 使用场景

Tutor。

Review。

Recommendation。

Evaluation。

---

# 第十七章 course_tool（课程工具）

## 17.1 输出内容

课程名称。

章节。

知识点。

实验。

测验。

教学目标。

供 Teacher Agent 使用。

---

# 第十八章 quiz_tool（测验工具）

## 18.1 支持能力

获取 Quiz。

获取题目。

获取学生成绩。

获取知识掌握。

生成 Prompt Context。

---

# 第十九章 recommendation_tool（推荐工具）

## 19.1 输入

Learning Mirror。

Risk。

Mastery。

Timeline。

---

## 19.2 输出

推荐知识点。

推荐实验。

推荐资料。

推荐测验。

推荐学习计划。

---

# 第二十章 Tool Registry 实现规范

## Registry 提供方法

```text
register()

list_tools()

execute()

exists()

remove()
```

Planner 查询 Registry。

---

## Tool Metadata

每个 Tool 保存：

名称。

描述。

输入 Schema。

输出 Schema。

Agent 权限。

---

# 第二十一章 Prompt 安全策略

## Prompt Guard

禁止：

越权操作。

数据库修改。

系统 Prompt 泄露。

Prompt Injection。

---

## Prompt Validator

检测：

Token 长度。

危险输入。

工具权限。

通过后才能进入 LLM。

---

# 第二十二章 Prompt + Memory + Tool 调用流程

```text
Question

↓

Planner

↓

MemoryManager

↓

Tool Registry

↓

Retriever / Mirror Tool

↓

Prompt Builder

↓

LLM

↓

Memory Save

↓

Conversation Update
```

形成完整 AI 推理链。

---

# 第二十三章 AI Prompt Checklist

## Prompt

- [ ] Prompt Registry
- [ ] Prompt Builder
- [ ] Prompt Version Manager
- [ ] Prompt Validator

## Memory

- [ ] Short Memory
- [ ] Summary Memory
- [ ] Long Memory
- [ ] MemoryManager

## Tool Calling

- [ ] Tool Registry
- [ ] rag_tool
- [ ] mirror_tool
- [ ] course_tool
- [ ] quiz_tool
- [ ] recommendation_tool

---

# 第二十四章 本章开发成果

完成 Part06.3 后，ProgramMind AI Engine 将具备：

- Prompt Builder 中心。
- Prompt Version 管理。
- 三层 Conversation Memory。
- Tool Calling 系统。
- Learning Mirror Context Builder。
- RAG Context Builder。
- AI Agent 个性化上下文生成能力。
