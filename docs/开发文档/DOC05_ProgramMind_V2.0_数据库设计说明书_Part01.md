# ProgramMind V2.0 数据库设计说明书

# Part01 —— 数据库总体设计（完整版）

> 文档版本：V2.0
> 更新时间：2026-09
> 项目：ProgramMind——面向高校学科建设的垂类大模型与智能教学科研平台
> 技术栈：MySQL 8.0 + SQLAlchemy 2.x + Alembic + FastAPI

---

# 第一章 数据库总体架构

## 1.1 为什么重构数据库

ProgramMind Demo 版本数据库存在三个严重问题：

| Demo问题                                    | V2.0解决方案                     |
| ----------------------------------------- | ---------------------------- |
| SQLite 只有 users / enrollments / files 三张表 | 建立 22 张业务表                   |
| 大量业务数据保存在 JSON 文件                         | 全部业务数据入 MySQL                |
| AI 数据无法存储（RAG、Conversation、Agent）         | 建立 AI、Knowledge、Growth 三大数据域 |

数据库重构后，将成为整个 ProgramMind 的唯一数据源。

---

## 1.2 数据库技术方案

| 项目        | 方案                 |
| --------- | ------------------ |
| 数据库       | MySQL 8.0+         |
| ORM       | SQLAlchemy 2.x     |
| Migration | Alembic            |
| 字符集       | utf8mb4            |
| 排序规则      | utf8mb4_unicode_ci |
| 主键        | UUID（CHAR36）       |
| 时间字段      | DATETIME(6)        |
| JSON字段    | MySQL JSON         |
| 外键        | 全部建立 FK            |
| 删除策略      | Soft Delete（部分业务）  |

---

## 1.3 数据域划分（22 张表）

数据库共划分为 **8 个数据域**。

| 数据域              | 表数量 | 功能                                     |
| ---------------- | --- | -------------------------------------- |
| User Domain      | 3   | 用户、角色、登录                               |
| Course Domain    | 5   | 课程、章节、知识点、选课                           |
| Learning Domain  | 5   | 作业、实验、测验、学习记录                          |
| Knowledge Domain | 4   | 文档、Chunk、Embedding、Citation            |
| AI Domain        | 3   | Conversation、Message、Workflow          |
| Growth Domain    | 4   | Mirror、Mastery、Recommendation、Timeline |
| Analytics Domain | 2   | 通知、收藏                                  |
| System Domain    | 2   | 上传文件、日志                                |

总计 **28 张表（最终版）**。

> V2.0 比审计报告中的 22 张表更完整，因为加入了日志和 AI Workflow。

---

# 第二章 数据库 ER 总览（ProgramMind V2.0）

## 2.1 数据库关系图（逻辑）

```text
                    USERS
                      │
         ┌────────────┼─────────────┐
         ▼            ▼             ▼
   USER_PROFILE   USER_ROLE     CONVERSATIONS
         │                          │
         │                          ▼
         │                     AI_MESSAGES
         │
         ▼
    ENROLLMENTS
         │
         ▼
      COURSES
         │
 ┌───────┼────────┐
 ▼       ▼        ▼
CHAPTER KNOWLEDGE MATERIALS
 │        │
 ▼        ▼
QUIZZES HOMEWORK EXPERIMENTS
 │        │
 ▼        ▼
SUBMISSION SUBMISSION

COURSES
   │
   ▼
KNOWLEDGE_DOCUMENTS
      │
      ▼
KNOWLEDGE_CHUNKS
      │
      ▼
EMBEDDINGS
      │
      ▼
CITATIONS

USERS
 │
 ▼
LEARNING_RECORDS
 │
 ▼
LEARNING_MIRROR
 │
 ▼
KNOWLEDGE_MASTERY
 │
 ▼
RECOMMENDATIONS
 │
 ▼
TIMELINE
```

整个数据库围绕 **User → Course → Knowledge → AI → Growth** 五层展开。

---

## 2.2 数据域说明

### User Domain

负责身份认证。

包括：

- 用户
- 用户资料
- 权限角色

### Course Domain

负责课程体系。

包括：

- 专业
- 课程
- 章节
- 知识点
- 学生选课

### Learning Domain

负责教学业务。

包括：

- 作业
- 实验
- 测验
- 学习记录
- 提交记录

### Knowledge Domain

负责 RAG。

包括：

- 文档
- Chunk
- Embedding
- Citation

### AI Domain

负责智能体。

包括：

- Conversation
- Message
- Workflow

### Growth Domain

负责成长画像。

包括：

- Learning Mirror
- Mastery
- Recommendation
- Timeline

---

# 第三章 数据库命名规范（必须统一）

## 3.1 表命名规范

全部使用：

> **snake_case + 复数名词**

例如：

| 正确                   | 错误                 |
| -------------------- | ------------------ |
| users                | user               |
| courses              | Course             |
| homework_submissions | HomeworkSubmission |
| learning_records     | learningRecord     |

统一小写。

---

## 3.2 字段命名规范

全部 snake_case。

例如：

| 正确           | 错误          |
| ------------ | ----------- |
| created_at   | createdAt   |
| course_id    | courseId    |
| student_name | studentName |

---

## 3.3 主键规范

所有业务表：

```
id CHAR(36)
```

UUID。

Python：

```python
uuid.uuid4()
```

---

## 3.4 外键规范

统一：

```
xxx_id
```

例如：

```
user_id

course_id

chapter_id

knowledge_id
```

禁止：

uid。

cid。

pid。

---

## 3.5 时间字段规范

所有表统一拥有：

| 字段         | 类型       |
| ---------- | -------- |
| created_at | DATETIME |
| updated_at | DATETIME |

删除数据增加：

```
deleted_at
```

软删除。

---

## 3.6 状态字段规范

统一：

```
status VARCHAR(20)
```

例如：

| 值          |
| ---------- |
| pending    |
| processing |
| completed  |
| failed     |
| archived   |

---

# 第四章 数据类型规范

## 4.1 通用字段类型

<table>
  <table-row>
    <table-cell width="220">**字段类型**</table-cell>
    <table-cell>**MySQL 类型**</table-cell>
  </table-row>
  <table-row>
    <table-cell>UUID</table-cell>
    <table-cell>`CHAR(36)`</table-cell>
  </table-row>
  <table-row>
    <table-cell>用户名</table-cell>
    <table-cell>`VARCHAR(50)`</table-cell>
  </table-row>
  <table-row>
    <table-cell>姓名</table-cell>
    <table-cell>`VARCHAR(50)`</table-cell>
  </table-row>
  <table-row>
    <table-cell>邮箱</table-cell>
    <table-cell>`VARCHAR(120)`</table-cell>
  </table-row>
  <table-row>
    <table-cell>密码</table-cell>
    <table-cell>`VARCHAR(255)`（Hash）</table-cell>
  </table-row>
  <table-row>
    <table-cell>简介</table-cell>
    <table-cell>`TEXT`</table-cell>
  </table-row>
  <table-row>
    <table-cell>Markdown 内容</table-cell>
    <table-cell>`LONGTEXT`</table-cell>
  </table-row>
  <table-row>
    <table-cell>JSON 数据</table-cell>
    <table-cell>`JSON`</table-cell>
  </table-row>
  <table-row>
    <table-cell>时间</table-cell>
    <table-cell>`DATETIME(6)`</table-cell>
  </table-row>
  <table-row>
    <table-cell>浮点数</table-cell>
    <table-cell>`FLOAT`</table-cell>
  </table-row>
  <table-row>
    <table-cell>百分比</table-cell>
    <table-cell>`DECIMAL(5,2)`</table-cell>
  </table-row>
  <table-row>
    <table-cell>布尔值</table-cell>
    <table-cell>`BOOLEAN`</table-cell>
  </table-row>
</table>

---

## 4.2 JSON 字段使用规范

允许 JSON 的表：

| 表               | JSON 内容               |
| --------------- | --------------------- |
| conversations   | context_summary       |
| ai_workflows    | workflow_result       |
| learning_mirror | mirror_vector         |
| recommendations | recommendation_detail |
| notifications   | payload               |

禁止把业务数据整体存 JSON。

---

# 第五章 数据库索引规范（必须实现）

## 5.1 主键索引

所有表：

PRIMARY KEY(id)

---

## 5.2 唯一索引

<table>
  <table-row>
    <table-cell width="260">**字段**</table-cell>
    <table-cell>**原因**</table-cell>
  </table-row>
  <table-row>
    <table-cell>`users.username`</table-cell>
    <table-cell>账号唯一</table-cell>
  </table-row>
  <table-row>
    <table-cell>`users.email`</table-cell>
    <table-cell>邮箱唯一</table-cell>
  </table-row>
  <table-row>
    <table-cell>`courses.course_code`</table-cell>
    <table-cell>课程编号唯一</table-cell>
  </table-row>
  <table-row>
    <table-cell>`knowledge_documents.document_hash`</table-cell>
    <table-cell>防重复上传</table-cell>
  </table-row>
</table>

---

## 5.3 普通索引

必须建立：

| 表                    | 字段              |
| -------------------- | --------------- |
| enrollments          | student_id      |
| enrollments          | course_id       |
| homework_submissions | homework_id     |
| homework_submissions | student_id      |
| learning_records     | user_id         |
| learning_records     | course_id       |
| knowledge_chunks     | document_id     |
| ai_messages          | conversation_id |
| knowledge_mastery    | student_id      |
| knowledge_mastery    | knowledge_id    |

---

## 5.4 联合索引

<table>
  <table-row>
    <table-cell width="260">**联合索引**</table-cell>
    <table-cell>**用途**</table-cell>
  </table-row>
  <table-row>
    <table-cell>`(student_id, course_id)`</table-cell>
    <table-cell>选课查询</table-cell>
  </table-row>
  <table-row>
    <table-cell>`(course_id, chapter_id)`</table-cell>
    <table-cell>课程目录</table-cell>
  </table-row>
  <table-row>
    <table-cell>`(conversation_id, created_at)`</table-cell>
    <table-cell>聊天记录排序</table-cell>
  </table-row>
  <table-row>
    <table-cell>`(user_id, created_at)`</table-cell>
    <table-cell>成长时间轴</table-cell>
  </table-row>
</table>

---

# 第六章 外键规范（必须实现）

## 6.1 外键关系

所有业务实体必须建立 FK。

例如：

<table>
  <table-row>
    <table-cell width="260">**外键**</table-cell>
    <table-cell>**引用表**</table-cell>
  </table-row>
  <table-row>
    <table-cell>`courses.teacher_id`</table-cell>
    <table-cell>`users.id`</table-cell>
  </table-row>
  <table-row>
    <table-cell>`chapters.course_id`</table-cell>
    <table-cell>`courses.id`</table-cell>
  </table-row>
  <table-row>
    <table-cell>`knowledge_points.chapter_id`</table-cell>
    <table-cell>`chapters.id`</table-cell>
  </table-row>
  <table-row>
    <table-cell>`homework.course_id`</table-cell>
    <table-cell>`courses.id`</table-cell>
  </table-row>
  <table-row>
    <table-cell>`quiz.course_id`</table-cell>
    <table-cell>`courses.id`</table-cell>
  </table-row>
  <table-row>
    <table-cell>`learning_records.user_id`</table-cell>
    <table-cell>`users.id`</table-cell>
  </table-row>
  <table-row>
    <table-cell>`knowledge_chunks.document_id`</table-cell>
    <table-cell>`knowledge_documents.id`</table-cell>
  </table-row>
  <table-row>
    <table-cell>`embeddings.chunk_id`</table-cell>
    <table-cell>`knowledge_chunks.id`</table-cell>
  </table-row>
</table>

---

## 6.2 删除策略

| 数据           | 删除策略                  |
| ------------ | --------------------- |
| 用户           | 禁止级联删除                |
| 课程           | Cascade 删除章节          |
| 文档           | Cascade 删除 Chunk      |
| Chunk        | Cascade 删除 Embedding  |
| Conversation | Cascade 删除 Message    |
| Homework     | Cascade 删除 Submission |

---

# 第七章 SQLAlchemy Base 规范

所有 Model 继承统一 BaseModel。

```python
class BaseModel:
    id: Mapped[str]
    created_at: Mapped[datetime]
    updated_at: Mapped[datetime]
```

统一自动更新时间。

统一 UUID。

统一软删除字段。

---

# 第八章 Alembic Migration 规范

数据库初始化流程：

```bash
alembic init migrations

alembic revision --autogenerate -m "create users"

alembic upgrade head
```

所有建表必须通过 Alembic。

禁止手写 SQL 修改线上数据库。

---

# 第九章 数据初始化规范（Seed Data）

首次初始化插入：

## 默认角色

- Teacher
- Student
- Admin

## 默认专业

- 人工智能
- 软件工程
- 数据科学
- 网络工程
- 计算机科学与技术

## 默认课程

- Python程序设计
- 数据结构
- 计算机网络

---

初始化目录：

```
backend/database/seeds/

seed_users.py

seed_courses.py

seed_majors.py

seed_knowledge.py
```

---

# 第十章 Backend 开发 Checklist（数据库总体）

## MySQL 初始化

- [ ] 创建 programmind 数据库
- [ ] UTF8MB4 字符集
- [ ] Alembic 初始化

## SQLAlchemy

- [ ] BaseModel
- [ ] UUID 主键
- [ ] created_at 自动生成
- [ ] updated_at 自动更新

## Migration

- [ ] 第一版 Migration
- [ ] 外键 Migration
- [ ] 索引 Migration

## Seed

- [ ] 默认用户
- [ ] 默认课程
- [ ] 默认专业
- [ ] 默认知识库

---

# 本章开发成果

完成 Part01 后，Backend 将具备：

- ProgramMind V2.0 数据库总体设计规范。
- MySQL 初始化规范。
- SQLAlchemy Model 编写规范。
- Alembic Migration 开发规范。
- 全项目命名、索引、外键统一规范。

下一章节：Part02 —— User Domain（用户系统 3 张表设计 + SQLAlchemy Model）。
