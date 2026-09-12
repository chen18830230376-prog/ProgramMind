# ProgramMind V2.0 后端开发规范

# Part08.1 —— Redis Cache Engine（缓存引擎）

> 文档版本：V2.0
> 更新时间：2026-09
> 模块负责人：Backend Infrastructure
> 技术栈：Redis 7.x + FastAPI + SQLAlchemy + aioredis

---

# 第一章 Redis Cache Engine 模块定位

## 1.1 模块职责

Redis 是 ProgramMind Backend 的高速缓存中心。

负责：

- Conversation Cache（聊天缓存）
- Learning Mirror Cache（学习状态缓存）
- Prompt Cache
- Embedding Cache
- Session Cache
- Rate Limit
- Scheduler Lock
- 热数据缓存

Redis 不保存永久数据，只缓存热点数据。

---

## 1.2 Redis 在系统中的位置

Frontend

↓

FastAPI

↓

Redis Cache

↓

MySQL

↓

Repository

所有热点数据优先查询 Redis。

---

## 1.3 Cache 原则

ProgramMind 采用：

**Cache Aside Pattern（旁路缓存模式）**

流程：

读取：

Redis → MySQL → Redis。

更新：

MySQL → 删除 Cache → 下次重新加载。

保证一致性。

---

# 第二章 Redis 模块目录

## 2.1 infrastructure/cache/

```text
cache/

redis_client.py

cache_manager.py

cache_keys.py

conversation_cache.py

mirror_cache.py

prompt_cache.py

session_cache.py

rate_limit_cache.py

scheduler_lock.py
```

缓存模块独立。

---

## 2.2 CacheManager 职责

统一管理：

- Set
- Get
- Delete
- TTL
- Prefix
- JSON 序列化

所有业务只能调用 CacheManager。

---

# 第三章 Redis Key 设计规范（核心）

## 3.1 Key 命名原则

统一格式：

```text
programmind:{module}:{resource}:{id}
```

禁止随意命名。

---

## 3.2 Key 分类

| 模块             | Prefix       |
| -------------- | ------------ |
| Conversation   | pm:chat      |
| Mirror         | pm:mirror    |
| Prompt         | pm:prompt    |
| Recommendation | pm:recommend |
| Session        | pm:session   |
| Rate Limit     | pm:rate      |
| Embedding      | pm:embed     |
| Lock           | pm:lock      |

全部统一。

---

## 3.3 示例 Key

```text
pm:chat:conversation:uuid

pm:mirror:student:uuid

pm:prompt:tutor:v2.0

pm:rate:user:uuid
```

统一可维护。

---

# 第四章 Conversation Cache

## 4.1 模块定位

缓存最近聊天消息。

减少数据库查询。

---

## 4.2 Cache 内容

最近：

10 条消息。

Summary。

Conversation Metadata。

Token Usage。

---

## 4.3 TTL

默认：

2 小时。

聊天活跃自动续期。

---

## 4.4 生命周期

新消息。

↓

Redis 更新。

↓

数据库异步保存。

↓

Summary 更新。

---

# 第五章 Learning Mirror Cache

## 5.1 模块定位

缓存学生最新 Mirror。

AI Tutor 高频读取。

---

## 5.2 Cache 内容

Mirror Vector。

Overall Score。

Risk。

Recommendations。

Updated At。

---

## 5.3 TTL

默认：

10 分钟。

Mirror 更新立即失效。

---

## 5.4 更新事件

Homework。

Quiz。

Experiment。

AI Evaluation。

Scheduler。

全部刷新 Mirror Cache。

---

# 第六章 Prompt Cache

## 6.1 为什么缓存 Prompt

Prompt Builder 拼接成本较高。

缓存最终 Prompt。

---

## 6.2 Cache Key

Prompt Hash。

Agent。

Version。

Course。

Mirror Version。

---

## 6.3 TTL

30 分钟。

Prompt 更新立即删除。

---

# 第七章 Session Cache

## 7.1 Session 定位

缓存登录 Session。

JWT Refresh。

最近访问课程。

---

## 7.2 内容

User ID。

Role。

Permission。

Last Login。

Last Active。

---

## 7.3 TTL

Access：

30 分钟。

Refresh：

7 天。

---

# 第八章 Recommendation Cache

## 8.1 模块定位

缓存今日推荐。

AI Tutor 首页。

Dashboard 首页。

---

## 8.2 TTL

每天凌晨失效。

Mirror 更新立即刷新。

---

## 8.3 数据内容

今日推荐。

优先任务。

AI Tutor Session。

Review Queue。

---

# 第九章 Embedding Cache

## 9.1 模块定位

缓存 Chunk Embedding。

避免重复计算。

---

## 9.2 Key

Chunk Hash。

Model。

Dimension。

---

## 9.3 生命周期

Chunk 更新。

删除 Cache。

重新 Embedding。

---

# 第十章 Rate Limit Cache

## 10.1 模块定位

API 限流。

防止刷接口。

---

## 10.2 限流对象

登录。

AI Chat。

Upload。

Admin API。

---

## 10.3 默认策略

| API      | 次数     |
| -------- | ------ |
| Login    | 5/min  |
| AI Chat  | 30/min |
| Upload   | 10/min |
| Register | 3/hour |

Redis 自增实现。

---

# 第十一章 Scheduler Lock

## 11.1 为什么需要 Lock

Celery 与 Scheduler 避免重复执行。

---

## 11.2 Lock Key

pm:lock:scheduler

TTL：

5 分钟。

---

## 11.3 使用场景

每日 Mirror Refresh。

Recommendation Refresh。

Risk Refresh。

Report Generate。

只能执行一次。

---

# 第十二章 Cache Aside Pattern

## 12.1 查询流程

请求。

↓

Redis。

命中返回。

未命中。

↓

MySQL。

↓

写 Redis。

---

## 12.2 更新流程

更新数据库。

↓

删除 Redis。

↓

下一次查询重新缓存。

避免脏数据。

---

# 第十三章 Cache TTL 策略

## TTL 表

| Cache          | TTL   |
| -------------- | ----- |
| Conversation   | 2h    |
| Mirror         | 10min |
| Prompt         | 30min |
| Recommendation | Daily |
| Session        | 30min |
| Rate Limit     | 1min  |
| Scheduler Lock | 5min  |

统一配置。

---

# 第十四章 Redis JSON 存储规范

## JSON Serializer

所有对象序列化 JSON。

禁止 Pickle。

---

## 保存对象

Mirror。

Conversation。

Prompt。

Recommendation。

使用统一 Serializer。

---

# 第十五章 Cache Monitoring

## Dashboard 输出

Redis Hit Rate。

Miss Rate。

Memory Usage。

Key Count。

Eviction Count。

TTL Distribution。

---

## Health API

GET /api/v1/system/cache

返回：

Redis 状态。

连接数。

内存。

版本。

---

# 第十六章 Redis Checklist

## Cache

- [ ] Conversation Cache
- [ ] Mirror Cache
- [ ] Prompt Cache
- [ ] Recommendation Cache
- [ ] Session Cache
- [ ] Embedding Cache

## Infrastructure

- [ ] CacheManager
- [ ] Cache Keys
- [ ] Rate Limit
- [ ] Scheduler Lock
- [ ] Health Check

---

# 第十七章 本章开发成果

完成 Part08.1 后，ProgramMind Backend 将具备：

- Redis Cache Engine。
- 统一 CacheManager。
- Cache Aside 模式。
- Conversation / Mirror / Prompt 缓存。
- Session 缓存。
- API Rate Limit。
- Scheduler 分布式锁。
- Redis Dashboard 与监控。
