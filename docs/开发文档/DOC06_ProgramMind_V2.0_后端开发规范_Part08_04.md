# ProgramMind V2.0 后端开发规范

# Part08.4 —— Infrastructure Monitoring（系统监控与运维中心）

> 文档版本：V2.0
> 更新时间：2026-09
> 模块负责人：Backend Infrastructure
> 技术栈：FastAPI + Redis + Celery + SQLAlchemy + Prometheus（预留）+ Docker

---

# 第一章 Infrastructure Monitoring 模块定位

## 1.1 模块职责

Infrastructure Monitoring 是 ProgramMind Backend 的系统运行中心。

负责：

- 日志管理（Logging）
- 服务健康检查（Health Check）
- Redis / Celery / MySQL / Ollama 状态监控
- AI Token 使用监控
- API 性能监控
- Cache 命中率统计
- 异常中心
- 告警中心
- 数据备份恢复

管理员 Dashboard 的全部数据来源于 Monitoring Engine。

---

## 1.2 Monitoring 在系统中的位置

FastAPI Services

↓

Logging Engine

↓

Monitoring Collector

↓

Health Engine

↓

Alert Engine

↓

Admin Dashboard

---

## 1.3 Monitoring 原则

ProgramMind Monitoring 满足：

- 实时监控。
- 可观测。
- 可追踪。
- 可恢复。
- 可告警。

---

# 第二章 Monitoring 总体架构

## 2.1 模块目录

system/

logging/

logger.py

log_formatter.py

monitor/

health_engine.py

metrics_collector.py

performance_monitor.py

token_monitor.py

cache_monitor.py

alert_engine.py

backup/

backup_engine.py

restore_engine.py

backup_scheduler.py

---

## 2.2 Monitoring 生命周期

API Request

↓

Logger

↓

Metrics Collector

↓

Health Check

↓

Alert Engine

↓

Dashboard

---

# 第三章 Logging Engine（日志系统）

## 3.1 Logger 定位

统一日志入口。

禁止 print。

全部使用 Logger。

---

## 3.2 日志分类

| 日志            | 内容            |
| ------------- | ------------- |
| app.log       | FastAPI 请求    |
| ai.log        | AI Workflow   |
| rag.log       | RAG 检索        |
| auth.log      | 登录认证          |
| scheduler.log | Scheduler     |
| worker.log    | Celery Worker |
| error.log     | 系统异常          |

---

## 3.3 日志等级

DEBUG。

INFO。

WARNING。

ERROR。

CRITICAL。

统一 Python logging。

---

## 3.4 Log 字段规范

timestamp。

request_id。

user_id。

module。

endpoint。

duration_ms。

status_code。

message。

---

# 第四章 Request Logging

## 4.1 Middleware Logging

所有请求记录：

请求路径。

IP。

用户。

耗时。

状态码。

---

## 4.2 Response Logging

响应：

状态。

Body Size。

Duration。

Token（AI）。

---

## 4.3 Trace ID

每个请求生成：

request_id。

贯穿：

API。

AI Workflow。

Celery。

日志。

---

# 第五章 Health Check Engine

## 5.1 Health API

GET /system/health

返回：

整体健康状态。

---

## 5.2 子服务健康检查

| 服务      | 检查内容       |
| ------- | ---------- |
| FastAPI | 服务状态       |
| MySQL   | 数据库连接      |
| Redis   | Ping       |
| Celery  | Worker     |
| Ollama  | 模型状态       |
| FAISS   | Index 是否加载 |

---

## 5.3 Health JSON

```json
{
 "status":"healthy",
 "services":[]
}
```

---

# 第六章 Performance Monitor

## 6.1 API 性能监控

统计：

请求耗时。

平均耗时。

P95。

P99。

错误率。

---

## 6.2 Endpoint Metrics

每个 API：

调用次数。

成功率。

平均耗时。

最大耗时。

---

## 6.3 Dashboard 指标

Top10 最慢 API。

错误最多 API。

AI API 平均耗时。

---

# 第七章 AI Token Monitor

## 7.1 Token Monitor 定位

统计 AI Token 使用。

---

## 7.2 指标

Prompt Token。

Completion Token。

Total Token。

Latency。

Provider。

Model。

---

## 7.3 Dashboard 输出

每日 Token。

课程 Token。

学生 Token。

教师 Token。

模型排行榜。

---

# 第八章 Cache Monitor

## 8.1 Redis Metrics

统计：

Hit。

Miss。

Hit Rate。

Memory。

TTL。

---

## 8.2 Mirror Cache 指标

命中率。

刷新次数。

TTL 剩余。

失效率。

---

## 8.3 Prompt Cache 指标

Prompt 命中率。

Prompt 构建次数。

平均节省耗时。

---

# 第九章 Database Monitor

## 9.1 MySQL 指标

连接数。

慢查询。

事务数量。

数据库大小。

---

## 9.2 Slow Query

超过：

500ms。

记录 slow_query.log。

---

## 9.3 Repository Metrics

查询次数。

缓存命中。

失败率。

平均耗时。

---

# 第十章 Celery Monitor

## 10.1 Worker Metrics

Worker 数量。

Running。

Pending。

Retry。

Failed。

---

## 10.2 Queue Metrics

AI Queue。

RAG Queue。

Mirror Queue。

Report Queue。

Storage Queue。

长度统计。

---

## 10.3 Dashboard

任务实时状态。

成功率。

平均耗时。

失败任务。

---

# 第十一章 RAG Monitor

## 11.1 Retriever Metrics

检索耗时。

TopK。

命中率。

Chunk 数量。

---

## 11.2 Embedding Metrics

Embedding 数量。

缓存命中。

重建次数。

失败次数。

---

## 11.3 FAISS Metrics

Index 数量。

向量数量。

更新时间。

内存占用。

---

# 第十二章 Alert Engine（告警中心）

## 12.1 Alert 分类

| 类型              | 描述           |
| --------------- | ------------ |
| System Alert    | 服务异常         |
| AI Alert        | AI 服务异常      |
| Storage Alert   | 文件系统异常       |
| Database Alert  | 数据库异常        |
| Scheduler Alert | Scheduler 异常 |

---

## 12.2 Alert Level

INFO。

WARNING。

ERROR。

CRITICAL。

---

## 12.3 Alert Trigger

Redis Down。

MySQL Down。

Worker Down。

Ollama Down。

磁盘不足。

自动生成 Alert。

---

# 第十三章 Exception Center

## 13.1 Exception Handler

统一 FastAPI Exception Handler。

返回统一错误结构。

---

## 13.2 ErrorCode

AUTH。

VALIDATION。

DATABASE。

AI。

RAG。

SYSTEM。

统一错误码。

---

## 13.3 Error Repository

保存：

错误。

Traceback。

Request ID。

User ID。

时间。

---

# 第十四章 Backup Engine

## 14.1 Backup 分类

MySQL。

Redis（可选）。

FAISS。

MinIO。

Reports。

---

## 14.2 Backup Scheduler

每天凌晨：

数据库备份。

每周：

FAISS Backup。

每月：

全量 Backup。

---

## 14.3 Backup Metadata

版本。

大小。

时间。

Checksum。

Provider。

---

# 第十五章 Restore Engine

## 15.1 Restore 流程

选择 Backup。

↓

验证 Checksum。

↓

恢复数据库。

↓

恢复对象存储。

↓

恢复 FAISS。

---

## 15.2 Recovery 场景

数据库损坏。

索引损坏。

文件误删。

支持恢复。

---

## 15.3 Recovery Checklist

验证 Backup。

停止 Worker。

恢复。

重建 Cache。

Health Check。

---

# 第十六章 Admin Monitoring Dashboard

## Dashboard 模块

服务状态。

API 性能。

AI Token。

Redis。

Celery。

数据库。

RAG。

Storage。

Alert。

---

## Dashboard Card

CPU（预留）。

Memory。

Redis Memory。

Worker 数。

Token 今日使用。

在线人数。

---

## 实时刷新

每：

30 秒刷新。

Health。

Metrics。

Alert。

---

# 第十七章 Monitoring API

## API 列表

| API                 | 描述        |
| ------------------- | --------- |
| GET /system/health  | 健康检查      |
| GET /system/metrics | 性能指标      |
| GET /system/token   | Token 使用  |
| GET /system/cache   | Redis 状态  |
| GET /system/alerts  | 告警列表      |
| GET /system/logs    | 日志查询      |
| GET /system/tasks   | Worker 状态 |

管理员权限。

---

# 第十八章 Infrastructure Checklist

## Logging

- [ ] Request Logger
- [ ] AI Logger
- [ ] Error Logger
- [ ] Worker Logger

## Monitoring

- [ ] Health Check
- [ ] API Metrics
- [ ] Redis Metrics
- [ ] Token Metrics
- [ ] Worker Metrics
- [ ] RAG Metrics

## Recovery

- [ ] Backup
- [ ] Restore
- [ ] Alert Engine
- [ ] Exception Center

---

# 第十九章 本章开发成果

完成 Part08.4 后，ProgramMind Backend 将具备：

- 企业级日志系统。
- Health Check 中心。
- Redis / MySQL / Celery / Ollama 监控。
- API Performance Dashboard。
- AI Token Dashboard。
- Cache Dashboard。
- Alert Center。
- Backup & Restore Engine。
- Admin Monitoring Dashboard。
