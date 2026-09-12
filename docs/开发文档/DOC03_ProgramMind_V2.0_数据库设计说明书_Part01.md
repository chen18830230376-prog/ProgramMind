# ProgramMind V2.0 数据库设计说明书（DDS）

# Part 01 —— 数据库总体架构设计

> 面向开发成员：Backend（数据库负责人）、AI/RAG 成员、产品负责人
> 
> 数据库：MySQL 8.0
> 
> ORM：SQLAlchemy 2.x
> 
> 字符集：utf8mb4

---

# 第一章 数据库设计概述

## 1.1 文档目标

本文档定义 ProgramMind V2.0 的数据库整体设计。

包括：

- 数据库命名规范
- 表结构设计规范
- ER 模型
- 外键关系
- 索引规范
- JSON 字段规范
- AI 数据存储规范
- RAG 数据存储规范

Backend 成员开发数据库必须严格按照本文档实现。

本说明书与 SQL 文件一一对应。

---

## 1.2 数据库定位

ProgramMind 数据库承担五大能力。

| 能力    | 描述                          |
| ----- | --------------------------- |
| 用户中心  | 用户、身份、权限、学院专业               |
| 教学中心  | 课程、教材、作业、实验、测验              |
| AI 中心 | AI 会话、Agent、Workflow、Memory |
| 学习中心  | 学习记录、掌握度、成长画像               |
| 知识中心  | 文档、Chunk、Embedding、Citation |

数据库既服务 Backend，也服务 AI Engine。

---

## 1.3 数据库设计原则

### 原则一：业务数据全部入库

Demo 中大量业务数据存在 JSON。

V2 全部迁移 MySQL。

禁止使用运行时 JSON 保存业务数据。

---

### 原则二：一张表只负责一种实体

例如：

- homework
- homework_submission

不能混合。

---

### 原则三：统一 UUID 主键

所有业务表使用 UUID。

格式：

```
xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx
```

SQLAlchemy 自动生成。

---

### 原则四：统一时间字段

所有表必须包含：

| 字段         | 类型       |
| ---------- | -------- |
| created_at | DATETIME |
| updated_at | DATETIME |

软删除表增加：

| 字段         |
| ---------- |
| deleted_at |

---

### 原则五：统一状态字段

所有业务对象使用 status。

例如：

| status    | 描述  |
| --------- | --- |
| draft     | 草稿  |
| published | 已发布 |
| submitted | 已提交 |
| reviewing | 批改中 |
| finished  | 已完成 |

禁止 bool 表示复杂状态。

---

# 第二章 数据库整体模块划分

ProgramMind 数据库共设计 **18 张核心业务表**。

---

## 2.1 数据库模块

### 用户中心（4 张）

| 表名            | 功能     |
| ------------- | ------ |
| users         | 用户信息   |
| user_profiles | 用户扩展信息 |
| majors        | 专业信息   |
| enrollments   | 学生选课   |

---

### 教学中心（6 张）

| 表名                    | 功能   |
| --------------------- | ---- |
| courses               | 课程   |
| chapters              | 章节   |
| homework              | 作业   |
| homework_submission   | 作业提交 |
| experiments           | 实验   |
| experiment_submission | 实验提交 |

---

### 测验中心（3 张）

| 表名             | 功能     |
| -------------- | ------ |
| quizzes        | 测验     |
| quiz_questions | 题目     |
| quiz_records   | 学生作答记录 |

---

### AI 中心（4 张）

| 表名                | 功能             |
| ----------------- | -------------- |
| ai_conversations  | AI 会话          |
| ai_messages       | AI 消息          |
| ai_workflows      | Agent Workflow |
| ai_workflow_steps | Workflow 节点    |

---

### 知识中心（5 张）

| 表名                  | 功能        |
| ------------------- | --------- |
| knowledge_documents | 文档        |
| knowledge_chunks    | Chunk     |
| embeddings          | Embedding |
| citations           | Citation  |
| course_resources    | 教材/PPT资源  |

---

### 学习画像（3 张）

| 表名               | 功能   |
| ---------------- | ---- |
| learning_records | 学习行为 |
| mastery_records  | 掌握度  |
| growth_profiles  | 成长画像 |

> 总计：**25 张业务表（V2.0 正式版）**

其中比赛 MVP 必做 **18 张**。

---

# 第三章 数据库 ER 总图

## 3.1 ER 模型

```text
                   users
                     │
        ┌────────────┼────────────┐
        ▼            ▼            ▼
 user_profiles   enrollments   ai_conversations
                      │              │
                      ▼              ▼
                   courses      ai_messages
                      │
     ┌───────────────┼──────────────────────┐
     ▼               ▼                      ▼
 chapters        homework             experiments
     │               │                      │
     ▼               ▼                      ▼
 knowledge_documents homework_submission experiment_submission
     │
     ▼
 knowledge_chunks
     │
     ▼
 embeddings
     │
     ▼
 citations

 users
   │
   ▼
 learning_records
   │
   ▼
 mastery_records
   │
   ▼
 growth_profiles
```

---

## 3.2 数据流关系

教师：

课程

↓

章节

↓

教材上传

↓

Chunk

↓

Embedding

↓

RAG Ready

学生：

课程

↓

学习

↓

记录

↓

掌握度

↓

成长画像

AI：

聊天

↓

Workflow

↓

Message

↓

Memory

---

# 第四章 数据库命名规范

## 4.1 表命名规范

统一：

小写。

下划线。

复数。

例如：

```
users
courses
homework_submissions
knowledge_chunks
```

禁止：

```
User
CourseTable
HomeworkInfo
```

---

## 4.2 字段命名规范

统一 snake_case。

例如：

| 正确              | 错误         |
| --------------- | ---------- |
| course_id       | courseId   |
| created_at      | createTime |
| knowledge_point | pointName  |

---

## 4.3 主键命名规范

统一：

id。

外键：

entity_id。

例如：

```
course_id
teacher_id
student_id
document_id
```

---

## 4.4 JSON 字段规范

允许 JSON 类型字段：

| 字段        | 用途       |
| --------- | -------- |
| tags      | 标签       |
| citations | 引用       |
| metadata  | 文档元信息    |
| config    | Agent 配置 |

禁止把业务对象整体塞 JSON。

---

# 第五章 通用字段规范

## 5.1 BaseModel 字段

所有 ORM Model 继承 BaseModel。

包含：

| 字段         | 类型       |
| ---------- | -------- |
| id         | CHAR(36) |
| created_at | DATETIME |
| updated_at | DATETIME |

---

## 5.2 审计字段

需要记录创建者。

| 字段         |
| ---------- |
| created_by |
| updated_by |

教师创建课程必须记录教师 ID。

---

## 5.3 状态字段

统一 ENUM。

示例：

课程：

draft

published

archived

作业：

draft

published

closed

提交：

submitted

reviewed

returned

---

## 5.4 排序字段

统一：

sort_order。

章节排序。

课程排序。

知识点排序。

---

# 第六章 外键规范

## 6.1 外键原则

所有关联必须建立外键。

例如：

```
course.teacher_id
→ users.id
```

---

## 6.2 删除策略

统一 CASCADE / SET NULL。

| 场景          | 删除策略               |
| ----------- | ------------------ |
| Course 删除   | CASCADE Chapters   |
| Homework 删除 | CASCADE Submission |
| User 删除     | SET NULL CreatedBy |
| Document 删除 | CASCADE Chunk      |

---

## 6.3 多对多关系

使用中间表。

例如：

学生选课：

users

↓

enrollments

↓

courses

---

# 第七章 索引规范

## 7.1 必建索引

所有外键必须建立索引。

例如：

| 字段              |
| --------------- |
| course_id       |
| teacher_id      |
| student_id      |
| document_id     |
| conversation_id |

---

## 7.2 唯一索引

例如：

users.username。

users.email。

majors.code。

---

## 7.3 联合索引

推荐：

| 索引                           |
| ---------------------------- |
| (course_id,status)           |
| (student_id,course_id)       |
| (conversation_id,created_at) |
| (document_id,chunk_order)    |

---

## 7.4 全文索引（预留）

知识库：

content。

title。

支持 MySQL FullText。

RAG 默认仍走向量库。

---

# 第八章 数据一致性规范

## 8.1 禁止 JSON 双写

Demo：

SQLite + runtime_state.json。

V2：

所有数据写 MySQL。

JSON 只缓存。

---

## 8.2 事务规范

涉及多个表：

必须事务。

例如：

发布作业：

homework

notification

learning_task

三步必须成功。

---

## 8.3 AI Workflow 一致性

Workflow。

Step。

Message。

Memory。

统一事务提交。

---

# 第九章 SQLAlchemy 目录规范

目录：

```
backend/

app/

models/

base.py

user.py

course.py

homework.py

quiz.py

knowledge.py

growth.py

ai.py
```

每张表一个 Model 文件。

禁止全部写 models.py。

---

## 9.1 ORM Base

所有 Model：

继承 Base。

自动 created_at。

自动 updated_at。

UUID 自动生成。

---

## 9.2 Migration 规范

Alembic。

目录：

```
alembic/

versions/
```

禁止手写 ALTER TABLE。

所有结构修改必须 Migration。

---

# 第十章 数据库 Checklist（Part01）

## 数据库基础

- [ ] MySQL8 初始化
- [ ] utf8mb4
- [ ] programmind_v2 数据库
- [ ] SQLAlchemy Base
- [ ] Alembic 初始化

## 命名规范

- [ ] snake_case
- [ ] UUID 主键
- [ ] created_at
- [ ] updated_at

## 外键规范

- [ ] 所有关联建 FK
- [ ] CASCADE 策略
- [ ] 联合索引

## 目录规范

- [ ] models/
- [ ] migrations/
- [ ] repositories/

---

# 本章输出成果

完成 ProgramMind V2.0 数据库总体设计：

- 数据库整体架构
- ER 模型
- 命名规范
- 字段规范
- 外键规范
- 索引规范
- SQLAlchemy 规范
- Migration 规范

下一章节开始设计第一批业务表（用户中心 + 课程中心）。

---

**DOC03 Part01 完成。**
