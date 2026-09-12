# ProgramMind V2.0 后端开发规范

# Part08.3 —— Celery Task Engine（异步任务与调度中心）

> 文档版本：V2.0
> 更新时间：2026-09
> 模块负责人：Backend Infrastructure
> 技术栈：FastAPI + Celery + Redis + SQLAlchemy + FAISS

---

# 第一章 Celery Task Engine 模块定位

## 1.1 为什么需要 Celery

ProgramMind 中很多 AI 能力属于耗时任务。

例如：

- RAG 文档解析
- Embedding 生成
- FAISS 索引重建
- AI 成长报告生成
- PDF 导出
- Learning Mirror 全量刷新

这些任务不能阻塞 FastAPI API，因此统一交给 Celery Worker。

---

## 1.2 Celery 在系统中的位置

Vue

↓

FastAPI API

↓

Celery Producer

↓

Redis Broker

↓

Celery Worker

↓

MySQL / FAISS / Storage

↓

Task Status API

---

## 1.3 Celery 职责

ProgramMind Celery 负责：

- AI 长耗时任务。
- Scheduler 定时任务。
- Retry。
- Queue 管理。
- Task Status。
- Worker Health。

---

# 第二章 Task Engine 架构设计

## 2.1 目录结构

tasks/

celery_app.py

worker.py

beat.py

task_registry.py

task_status.py

scheduler/

daily_scheduler.py

weekly_scheduler.py

monthly_scheduler.py

queues/

ai_tasks.py

rag_tasks.py

mirror_tasks.py

report_tasks.py

storage_tasks.py

---

## 2.2 Queue 分类

| Queue   | 职责        |
| ------- | --------- |
| ai      | AI 推理耗时任务 |
| rag     | 文档解析与索引   |
| mirror  | Mirror 刷新 |
| report  | 成长报告生成    |
| storage | 文件处理      |

不同 Worker 可监听不同队列。

---

## 2.3 Celery Broker

默认：

Redis。

Redis 同时作为：

Broker。

Result Backend。

---

# 第三章 Celery 配置规范

## 3.1 celery_app.py

统一初始化 Celery。

禁止业务模块重复初始化。

---

## 3.2 配置项

.env

CELERY_BROKER_URL=redis://redis:6379/0

CELERY_RESULT_BACKEND=redis://redis:6379/1

TIMEZONE=Asia/Shanghai

ENABLE_UTC=False

---

## 3.3 Worker 配置

默认：

4 Worker。

并发可配置。

开发环境：

1 Worker。

---

# 第四章 AI Tasks（AI 异步任务）

## 4.1 AI Task 分类

AI Growth Report。

AI Summary。

AI PDF Export。

AI Batch Recommendation。

AI Batch Evaluation。

---

## 4.2 AI Growth Report Task

输入：

student_id。

report_type。

输出：

Markdown Report。

保存数据库。

---

## 4.3 AI Summary Task

Conversation Summary。

课程总结。

实验总结。

AI Tutor Summary。

异步生成。

---

# 第五章 RAG Tasks（知识库任务）

## 5.1 Parser Task

上传 PDF。

↓

Parser。

↓

Chunk。

↓

Metadata。

异步执行。

---

## 5.2 Embedding Task

Chunk。

↓

Embedding。

↓

Redis Cache。

↓

Vector DB。

---

## 5.3 FAISS Build Task

课程索引。

↓

重建。

↓

保存 Index。

↓

更新 Metadata。

---

## 5.4 Incremental Build Task

新增教材。

无需全量索引。

仅更新新增 Chunk。

---

# 第六章 Mirror Tasks

## 6.1 Mirror Refresh Task

凌晨刷新：

Learning Mirror。

全量计算。

---

## 6.2 Batch Mastery Task

重新计算：

全部知识掌握度。

用于：

教师更新课程。

RAG 更新。

---

## 6.3 Risk Refresh Task

批量预测：

课程 Risk。

学生 Risk。

更新 Dashboard。

---

# 第七章 Recommendation Scheduler Tasks

## 7.1 Daily Recommendation

每天凌晨：

生成今日推荐。

Review Queue。

AI Tutor 推荐。

---

## 7.2 Weekly Recommendation

每周一：

生成本周学习计划。

课程推荐。

实验推荐。

---

## 7.3 Exam Recommendation（预留）

考试周自动调整推荐策略。

---

# 第八章 Report Tasks

## 8.1 Weekly Report Task

每周日晚：

自动生成成长周报。

---

## 8.2 Monthly Report Task

每月最后一天：

生成成长月报。

---

## 8.3 Semester Report Task

学期结束：

生成成长分析 PDF。

---

## 8.4 Teacher Report Task

班级成长分析。

教师下载。

---

# 第九章 Storage Tasks

## 9.1 Image Compress Task

头像压缩。

课程图片压缩。

缩略图生成。

---

## 9.2 Garbage Collect Task

删除：

Temp 文件。

失效版本。

孤立对象。

---

## 9.3 File Virus Scan（预留）

上传完成后异步扫描。

---

# 第十章 Scheduler（Celery Beat）

## 10.1 Beat 定位

统一管理所有定时任务。

---

## 10.2 Daily Scheduler

每天凌晨：

Mirror Refresh。

Risk Refresh。

Recommendation Refresh。

HeatMap Snapshot。

---

## 10.3 Weekly Scheduler

每周：

Weekly Report。

课程统计。

班级统计。

---

## 10.4 Monthly Scheduler

每月：

Monthly Report。

Dashboard Aggregation。

垃圾回收。

---

# 第十一章 Scheduler Lock（防重复执行）

## 11.1 Redis Lock

Scheduler 启动。

↓

Redis Lock。

↓

成功执行。

↓

释放 Lock。

---

## 11.2 Lock TTL

5 分钟。

Worker Crash 自动失效。

---

## 11.3 Lock 场景

Mirror。

Recommendation。

Report。

RAG Rebuild。

---

# 第十二章 Task Retry 机制

## 12.1 Retry 场景

Embedding。

Ollama Timeout。

Storage Error。

FAISS Error。

---

## 12.2 Retry 策略

默认：

3 次。

指数退避。

---

## 12.3 不 Retry 场景

Permission Error。

Validation Error。

不存在资源。

---

# 第十三章 Task Status Engine

## 13.1 TaskStatus 表

数据库：

background_tasks。

保存：

任务状态。

---

## 13.2 Status 类型

pending。

running。

success。

failed。

cancelled。

---

## 13.3 查询 API

GET /tasks/{task_id}

返回：

状态。

进度。

错误。

结果 URL。

---

# 第十四章 Progress Reporting

## 14.1 Progress 更新

Embedding：

Chunk 百分比。

Report：

章节百分比。

Parser：

页数百分比。

---

## 14.2 Progress JSON

```json
{
 "status":"running",
 "progress":42
}
```

Dashboard ProgressBar 使用。

---

# 第十五章 Worker Health Monitoring

## 15.1 Health API

返回：

Worker 数。

Queue 长度。

Redis Broker。

Result Backend。

---

## 15.2 Worker Metrics

Active Tasks。

Completed。

Failed。

Retry Count。

Average Duration。

---

## 15.3 Dashboard

后台实时展示 Worker 状态。

---

# 第十六章 Celery 日志规范

## 日志分类

worker.log

scheduler.log

rag.log

report.log

mirror.log

统一 logger。

---

## 日志字段

Task ID。

Queue。

Duration。

Retry。

Error。

Status。

---

# 第十七章 Task Queue Dashboard

## Dashboard 内容

Queue Length。

Running Tasks。

Failed Tasks。

Completed Today。

Average Runtime。

Worker Health。

---

## 管理员操作

Retry。

Cancel。

Restart。

Rebuild。

---

# 第十八章 Celery Checklist

## Worker

- [ ] AI Worker
- [ ] RAG Worker
- [ ] Mirror Worker
- [ ] Report Worker
- [ ] Storage Worker

## Scheduler

- [ ] Daily Scheduler
- [ ] Weekly Scheduler
- [ ] Monthly Scheduler

## Reliability

- [ ] Retry
- [ ] Lock
- [ ] Progress
- [ ] Status API
- [ ] Worker Health

---

# 第十九章 本章开发成果

完成 Part08.3 后，ProgramMind Backend 将具备：

- Celery Worker 架构。
- Redis Broker。
- AI 长耗时任务中心。
- RAG 异步解析与索引。
- Learning Mirror Scheduler。
- Recommendation Scheduler。
- AI 周报/月报生成任务。
- Task Retry 与 Progress。
- Worker Dashboard。
- 分布式 Scheduler Lock。
