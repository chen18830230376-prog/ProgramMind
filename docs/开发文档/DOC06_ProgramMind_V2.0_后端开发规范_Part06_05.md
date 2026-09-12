# ProgramMind V2.0 后端开发规范

# Part06.5 —— AI Engine 联调、测试、性能优化与部署规范（完整版）

> 文档版本：V2.0
> 更新时间：2026-09
> 模块负责人：AI（Integration & Deployment）
> 技术栈：FastAPI + LangGraph + Ollama + Redis + Docker + FAISS

---

# 第一章 AI Engine 联调定位

## 1.1 AI Engine 联调目标

ProgramMind AI Engine 需要与 Backend 全部模块联调。

联调对象：

- Auth 模块
- Course 模块
- Learning 模块
- Knowledge（RAG）
- Growth（Learning Mirror）
- Database（Conversation）
- Redis
- SSE

最终形成完整 AI 调用链。

---

## 1.2 AI 调用链（完整版）

Vue AI Chat

↓

AI Router

↓

AIService.chat()

↓

PlannerAgent

↓

Workflow Executor

↓

Tool Calling

↓

KnowledgeService / GrowthService / CourseService

↓

Prompt Builder

↓

Model Router

↓

LLM

↓

Citation Builder

↓

Conversation Save

↓

Memory Update

↓

SSE 返回前端

---

# 第二章 AIService 与 Backend 联调

## 2.1 AIService 统一入口

AI Router 不允许直接调用 Agent。

所有请求进入：

AIService。

---

## 2.2 AIService 调用模块

AIService 内部协调：

- Workflow Executor
- ConversationRepository
- KnowledgeService
- MirrorService
- RecommendationService
- UsageLogger

AIService 是 AI 模块唯一 Facade。

---

## 2.3 AI API 与 DOC04 对应关系

| API                | Workflow                |
| ------------------ | ----------------------- |
| /ai/chat           | Tutor Workflow          |
| /ai/lesson         | Lesson Workflow         |
| /ai/research       | Research Workflow       |
| /ai/review-plan    | Review Workflow         |
| /ai/evaluate       | Evaluation Workflow     |
| /ai/recommendation | Recommendation Workflow |

全部通过 AIService 调度。

---

# 第三章 AI 与 RAG 联调规范

## 3.1 Retriever 联调流程

Question

↓

KnowledgeService.retrieve()

↓

Retriever

↓

TopK Chunk

↓

Prompt Builder

---

## 3.2 Citation 联调

Retriever 输出：

Citation Metadata。

↓

Citation Builder。

↓

Conversation Citation。

↓

citation_records 数据库。

---

## 3.3 文档过滤规则

Retriever 支持：

course_id。

chapter_id。

document_type。

knowledge_point。

保证课程隔离。

---

# 第四章 AI 与 Learning Mirror 联调

## 4.1 Mirror Tool 联调

Tutor Workflow。

↓

mirror_tool。

↓

GrowthService。

↓

Learning Mirror。

↓

Prompt Builder。

---

## 4.2 AI 使用 Mirror 的场景

Tutor：

个性化回答。

Review：

学习计划。

Recommendation：

推荐生成。

Evaluation：

更新掌握度。

---

## 4.3 Mirror 更新链路

AI Evaluation。

↓

Knowledge Mastery 更新。

↓

Learning Mirror Refresh。

↓

Risk Prediction。

↓

Recommendation。

↓

Timeline。

形成成长闭环。

---

# 第五章 AI 与 Conversation 联调

## 5.1 Conversation 生命周期

Create Conversation。

↓

Append User Message。

↓

Workflow。

↓

Streaming。

↓

Append Assistant Message。

↓

Summary Update。

---

## 5.2 Conversation Summary 更新策略

消息 ≥15。

↓

Summary Generator。

↓

Conversation.summary 更新。

↓

Memory 保存。

---

## 5.3 Usage Log 保存

Workflow 完成：

记录：

- Token
- Latency
- Provider
- Model
- Success

数据库 model_usage_logs。

---

# 第六章 AI Cache 设计（性能优化）

## 6.1 Cache 分类

| Cache              | 用途           |
| ------------------ | ------------ |
| Prompt Cache       | Prompt 拼接缓存  |
| Embedding Cache    | Embedding 缓存 |
| FAISS Cache        | Index 缓存     |
| Conversation Cache | 最近聊天缓存       |
| Mirror Cache       | 学习状态缓存       |

---

## 6.2 Prompt Cache

缓存 Key：

prompt_hash。

Value：

Prompt。

TTL：

30 分钟。

减少 Prompt 拼接。

---

## 6.3 Conversation Cache

Redis 保存：

最近 10 条消息。

TTL：

2 小时。

Summary 永久数据库。

---

## 6.4 Mirror Cache

Key：

student_id。

TTL：

10 分钟。

更新事件：

Homework。

Quiz。

Experiment。

立即失效缓存。

---

# 第七章 Embedding Cache

## 7.1 Embedding 缓存规则

Chunk Hash。

↓

Redis。

↓

Database。

↓

FAISS。

重复 Chunk 不重新生成。

---

## 7.2 增量更新

Document Hash 不变。

跳过 Embedding。

Document Hash 更新。

重新 Chunk。

重新 Embedding。

---

# 第八章 FAISS Index Cache

## 8.1 Index Manager

应用启动：

加载所有课程 Index。

保存在内存。

---

## 8.2 Index 热更新

新增文档：

Append Index。

管理员重建：

Replace Index。

无需重启服务。

---

## 8.3 Memory 管理

支持：

Unload。

Reload。

按课程释放。

---

# 第九章 AI 性能优化策略

## 9.1 Prompt Token 裁剪

优先保留：

Question。

Summary。

Retriever Context。

Mirror Context。

删除：

旧聊天。

---

## 9.2 Retriever 优化

TopK 默认：

5。

Similarity Threshold：

0.65。

Rerank 后保留：

3。

---

## 9.3 Chunk 优化

Chunk Size：

500。

Overlap：

100。

避免上下文断裂。

---

# 第十章 AI Benchmark（性能指标）

## 10.1 Tutor Workflow 指标

| 指标             | 目标     |
| -------------- | ------ |
| 首 Token 延迟     | ≤2 秒   |
| 完整回答           | ≤8 秒   |
| Retriever 时间   | ≤300ms |
| Prompt Builder | ≤50ms  |

---

## 10.2 Research Workflow 指标

允许：

15 秒。

长回答。

DeepSeek 推理。

---

## 10.3 Growth Workflow 指标

Recommendation：

≤2 秒。

Mirror Refresh：

≤1 秒。

---

# 第十一章 AI 单元测试规范

## tests/ai/

```text
tests/

ai/

test_prompt_builder.py

test_memory.py

test_retriever.py

test_workflow.py

test_router.py
```

AI 模块单独测试。

---

## 11.2 Prompt Builder 测试

验证：

Prompt 顺序。

Token 数。

Context 拼接。

Prompt Version。

---

## 11.3 Retriever 测试

上传教材。

检索问题。

验证：

TopK。

Similarity。

Citation。

---

# 第十二章 Workflow 集成测试

## Tutor Workflow

测试链路：

Question

↓

Retriever

↓

LLM

↓

Citation

↓

Memory

↓

Conversation

全部成功。

---

## Lesson Workflow

输入课程。

输出：

教案 Markdown。

Quiz JSON。

PPT Outline。

---

## Review Workflow

输入 Mirror。

输出每日学习计划。

推荐知识点。

推荐实验。

---

# 第十三章 Mock LLM 测试

## 为什么 Mock

CI 不依赖真实模型。

Mock Provider 返回固定结果。

测试 Workflow。

---

## Mock Provider 返回

固定 Markdown。

固定 Citation。

固定 Token。

保证测试稳定。

---

# 第十四章 AI 日志规范

## AI Logger 分类

| Logger        | 内容             |
| ------------- | -------------- |
| workflow.log  | Workflow 生命周期  |
| prompt.log    | Prompt Builder |
| retriever.log | Retriever 检索   |
| provider.log  | LLM Provider   |
| usage.log     | Token 使用       |

---

## 日志内容

Workflow ID。

Conversation ID。

Agent。

Latency。

Token。

Model。

Error。

---

# 第十五章 Docker AI 部署规范

## 15.1 AI Docker 容器

```text
docker/

Dockerfile.ai

docker-compose.yml

entrypoint.sh
```

AI 服务独立容器。

---

## 15.2 Docker Compose

服务：

backend。

mysql。

redis。

ollama。

nginx。

AI 与 Backend 可同容器 Demo。

生产建议分离。

---

## 15.3 Ollama 容器

挂载：

models。

Embedding。

缓存。

避免重复下载模型。

---

# 第十六章 GPU / CPU 配置规范

## CPU 模式

默认 Demo。

Qwen3。

DeepSeek。

bge-m3。

---

## GPU 模式（生产）

支持 CUDA。

GPU 自动检测。

Embedding GPU。

LLM GPU。

---

## 模型热加载

Application Startup：

检测模型。

不存在：

提示下载。

存在：

直接加载。

---

# 第十七章 AI Monitoring（监控）

## Health Endpoint

GET /api/v1/ai/health

返回：

Provider。

Retriever。

Embedding。

Redis。

FAISS。

Workflow Engine。

---

## Dashboard 指标

Token 使用量。

平均响应时间。

成功率。

模型调用次数。

Retriever 命中率。

Risk Prediction 次数。

---

# 第十八章 AI Security（安全）

## Prompt Injection 防护

过滤：

系统 Prompt 请求。

越权请求。

SQL Prompt。

危险 Tool。

---

## Tool Permission

Student：

不能调用 Teacher Tool。

Teacher：

不能调用 Admin Tool。

Admin：

全部 Tool。

---

## Conversation Isolation

Conversation 只能访问自己的 Memory。

课程 RAG 必须课程隔离。

---

# 第十九章 AI Engine Checklist（最终版）

## Integration

- [ ] AIService 联调
- [ ] Conversation 联调
- [ ] Mirror 联调
- [ ] Knowledge 联调

## Cache

- [ ] Prompt Cache
- [ ] Conversation Cache
- [ ] Mirror Cache
- [ ] Embedding Cache
- [ ] FAISS Cache

## Test

- [ ] Prompt Test
- [ ] Retriever Test
- [ ] Workflow Test
- [ ] Mock Provider

## Deploy

- [ ] Docker AI
- [ ] Ollama
- [ ] GPU 检测
- [ ] Health API

## Monitoring

- [ ] Token Dashboard
- [ ] Latency Dashboard
- [ ] Provider Dashboard
- [ ] Error Logger

---

# 第二十章 AI Engine 开发成果（ProgramMind V2.0）

完成 AI Engine（Part06.1 ~ Part06.5）后，ProgramMind AI 模块正式具备：

- Multi-Agent 协同架构。
- LangGraph Workflow Engine。
- Prompt Builder 与 Prompt Version 管理。
- 三层 Conversation Memory。
- Tool Calling（RAG / Mirror / Course / Quiz / Recommendation）。
- 多模型 Router（Qwen3 / DeepSeek / Ollama）。
- SSE 流式聊天。
- Token Usage 全链路统计。
- AI Cache 优化。
- Docker AI 部署规范。
- Health Monitor 与 Benchmark 测试体系。

AI Engine 至此成为 ProgramMind Backend 的智能核心，为 AI Tutor、Teacher Agent、Research Agent、Growth Center 等全部模块提供统一 AI 能力。
