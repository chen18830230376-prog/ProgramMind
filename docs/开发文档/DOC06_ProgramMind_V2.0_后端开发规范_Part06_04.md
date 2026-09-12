# ProgramMind V2.0 后端开发规范

# Part06.4 —— Model Router、Streaming SSE 与 Token 管理（完整版）

> 文档版本：V2.0
> 更新时间：2026-09
> 模块负责人：AI（Model Router）
> 技术栈：FastAPI + Ollama + Qwen3 + DeepSeek + SSE + LangChain

---

# 第一章 Model Router 模块定位

## 1.1 为什么需要 Model Router

ProgramMind 使用多个大模型，不同 Agent 使用不同模型。

Model Router 负责：

- 模型选择。
- Provider 切换。
- 参数统一管理。
- Fallback。
- Token 统计。

所有 Agent 只能调用 Model Router。

---

## 1.2 AI 推理流程

Agent

↓

Prompt Builder

↓

Model Router

↓

Provider

↓

LLM

↓

Streaming

↓

Conversation Memory

↓

Usage Log

---

## 1.3 Router 目录结构

ai/router/

model_router.py

provider_manager.py

qwen_provider.py

deepseek_provider.py

ollama_provider.py

model_config.py

token_counter.py

---

# 第二章 Provider 设计规范

## 2.1 Provider 统一接口

所有模型 Provider 必须实现统一接口。

能力：

generate()

stream()

embedding()

health_check()

provider_info()

---

## 2.2 Provider 分类

| Provider          | 用途                 |
| ----------------- | ------------------ |
| OllamaProvider    | 本地模型统一入口           |
| QwenProvider      | AI Tutor / Teacher |
| DeepSeekProvider  | 科研 / AI评价          |
| CloudProvider（预留） | 云模型                |

统一继承 BaseProvider。

---

## 2.3 BaseProvider 职责

统一：

模型名称。

Token 统计。

Stream。

错误处理。

Retry。

Timeout。

---

# 第三章 Ollama Provider

## 3.1 Ollama 定位

ProgramMind Demo 默认本地部署。

负责：

Qwen3。

DeepSeek。

Embedding。

---

## 3.2 配置项

.env

OLLAMA_BASE_URL=http://localhost:11434

DEFAULT_MODEL=qwen3:14b

EMBEDDING_MODEL=bge-m3

TIMEOUT=120

---

## 3.3 OllamaProvider 方法

generate()

stream_generate()

list_models()

pull_model()

health_check()

---

## 3.4 健康检查

AI 启动时：

检查 Ollama 是否启动。

检查模型是否存在。

检查 Embedding 模型。

失败：

Application Warning。

---

# 第四章 Qwen Provider

## 4.1 Qwen 默认用途

Tutor Agent。

Teacher Agent。

Planner Agent。

Recommendation Agent。

---

## 4.2 默认参数

| 参数             | 默认值  |
| -------------- | ---- |
| temperature    | 0.4  |
| top_p          | 0.9  |
| max_tokens     | 1500 |
| repeat_penalty | 1.1  |

适合教学问答。

---

## 4.3 输出格式规范

Markdown。

支持：

代码块。

表格。

Mermaid（预留）。

引用。

---

# 第五章 DeepSeek Provider

## 5.1 DeepSeek 默认用途

Research Agent。

Evaluation Agent。

复杂推理。

算法分析。

---

## 5.2 默认参数

temperature=0.2

max_tokens=2500

top_p=0.85

适合长推理。

---

## 5.3 DeepSeek 输出规范

Markdown。

JSON。

评分。

分析报告。

科研总结。

---

# 第六章 Model Config 管理

## 6.1 model_config.py

统一维护模型配置。

禁止写死参数。

---

## 6.2 ModelConfig 字段

| 字段          | 描述          |
| ----------- | ----------- |
| model_name  | 模型名         |
| provider    | Ollama/Qwen |
| temperature | 温度          |
| max_tokens  | 最大输出        |
| top_p       | TopP        |
| timeout     | 超时时间        |
| stream      | 是否支持流式      |

---

## 6.3 Agent 默认模型映射

Planner → qwen3:8b

Tutor → qwen3:14b

Teacher → qwen3:14b

Research → deepseek-r1

Evaluation → deepseek-r1

Recommendation → qwen3:14b

---

# 第七章 Dynamic Model Routing（动态路由）

## 7.1 Router 输入

WorkflowState。

Agent。

Prompt。

是否 Stream。

---

## 7.2 Router 输出

Provider。

ModelConfig。

LLM Client。

---

## 7.3 自动切换策略

Priority：

指定模型。

↓

Agent 默认模型。

↓

Fallback 模型。

---

## 7.4 Fallback 策略

Qwen 不可用。

↓

DeepSeek。

DeepSeek 不可用。

↓

Qwen。

全部失败。

↓

返回 AI 服务不可用。

---

# 第八章 Streaming Service（核心）

## 8.1 为什么使用 SSE

ProgramMind AI Tutor 支持实时输出。

FastAPI 使用 Server-Sent Events。

而不是等待全部回答结束。

---

## 8.2 Streaming 架构

Frontend

↓

SSE Endpoint

↓

AIService.stream_chat()

↓

Model Router Stream

↓

Token Stream

↓

SSE Event

↓

Vue Markdown 渲染

---

## 8.3 stream_service.py 职责

统一：

SSE。

Chunk。

结束事件。

错误事件。

Conversation 保存。

---

# 第九章 SSE Event 规范

## 9.1 Event 类型

| Event    | 描述          |
| -------- | ----------- |
| message  | Token       |
| citation | Citation 更新 |
| thinking | AI 推理阶段     |
| done     | 完成          |
| error    | 错误          |

---

## 9.2 Message Event JSON

```json
{
  "type":"message",
  "delta":"列表推导式..."
}
```

逐 Token 返回。

---

## 9.3 Done Event

返回：

token_usage。

latency。

conversation_id。

message_id。

供前端保存。

---

# 第十章 Streaming 生命周期

## 10.1 生命周期

Create Workflow

↓

Stream Start

↓

Token Event

↓

Citation Event（可选）

↓

Done Event

↓

Save Conversation

↓

Memory Update

---

## 10.2 Streaming 保存策略

Streaming 不立即保存消息。

全部 Token 输出完成后：

保存一条完整 assistant message。

避免数据库碎片。

---

## 10.3 中断恢复

用户关闭连接。

Workflow Cancel。

Conversation 保留。

已输出内容保存。

支持重新生成。

---

# 第十一章 Token Usage 管理

## 11.1 TokenCounter 定位

统计：

输入 Token。

输出 Token。

总 Token。

Prompt Token。

Completion Token。

---

## 11.2 TokenUsageSchema

字段：

prompt_tokens。

completion_tokens。

total_tokens。

latency_ms。

model_name。

provider。

---

## 11.3 Token 保存数据库

model_usage_logs。

AIMessage。

Workflow。

三处同步。

---

# 第十二章 Usage Logger

## UsageLogger 保存内容

用户 ID。

Conversation。

Workflow。

Model。

Token。

Latency。

Success。

Created At。

用于 Dashboard。

---

## 聚合统计

每日 Token。

课程 Token。

模型 Token。

用户 Token。

教师 Token。

---

# 第十三章 Streaming 与 Conversation 联动

## Conversation 更新顺序

User Message

↓

Assistant Streaming

↓

Done

↓

Message Save

↓

Conversation Summary 更新

↓

Usage Log 保存

---

## Citation 更新

Streaming 中 Citation 可延迟发送。

回答结束后统一 Citation。

---

# 第十四章 AI Timeout 与 Retry

## Timeout 默认值

| Agent      | Timeout |
| ---------- | ------- |
| Tutor      | 120s    |
| Teacher    | 180s    |
| Research   | 240s    |
| Evaluation | 180s    |

---

## Retry 策略

Timeout Retry 1 次。

Connection Error Retry。

LLM Error 不超过两次。

---

## Cancel Strategy

用户点击停止。

Workflow Status：

cancelled。

释放 Stream。

---

# 第十五章 AI Concurrency 管理

## 限制并发

单用户：

最多 2 个 AI Workflow。

Tutor 与 Research 可同时运行。

Teacher Workflow 独占。

---

## Queue（预留）

Celery Queue。

大型 Workflow 后台执行。

生成 PPT。

生成成长报告。

---

# 第十六章 AI Provider 健康检查

## Health Check API

GET /api/v1/ai/models

返回：

模型状态。

Provider 状态。

Embedding 状态。

GPU 状态（预留）。

---

## Health Status

healthy。

loading。

missing。

offline。

前端 Dashboard 展示。

---

# 第十七章 Streaming Checklist

## Provider

- [ ] Ollama Provider
- [ ] Qwen Provider
- [ ] DeepSeek Provider

## Router

- [ ] Dynamic Routing
- [ ] Fallback
- [ ] Config

## Streaming

- [ ] SSE Endpoint
- [ ] Message Event
- [ ] Citation Event
- [ ] Done Event
- [ ] Error Event

## Token

- [ ] Token Counter
- [ ] Usage Logger
- [ ] Conversation Save

## Reliability

- [ ] Timeout
- [ ] Retry
- [ ] Cancel Workflow
- [ ] Health Check

---

# 第十八章 本章开发成果

完成 Part06.4 后，ProgramMind AI Engine 将具备：

- 多模型统一路由（Qwen3 / DeepSeek / Ollama）。
- SSE 实时流式聊天。
- Token Usage 全链路统计。
- Provider 健康检查。
- Fallback 自动切换。
- Conversation Streaming 持久化。
- AI Dashboard Token 数据来源。
