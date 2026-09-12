# ProgramMind V2.0 数据库设计说明书

# Part08 —— SQLAlchemy + Alembic + init.sql 数据库工程落地规范（完整版）

> 文档版本：V2.0
> 更新时间：2026-09
> 模块负责人：Backend（数据库）
> 技术栈：FastAPI + SQLAlchemy 2.x + Alembic + MySQL 8.0

---

# 第一章 数据库工程目录（最终版）

## 1.1 Backend 数据库目录结构

整个数据库目录必须统一如下：

```text
backend/

├── app/
│   ├── models/
│   │   ├── base.py
│   │   ├── user.py
│   │   ├── course.py
│   │   ├── learning.py
│   │   ├── knowledge.py
│   │   ├── ai.py
│   │   ├── growth.py
│   │   └── __init__.py
│   │
│   ├── repositories/
│   │   ├── user_repository.py
│   │   ├── course_repository.py
│   │   ├── learning_repository.py
│   │   ├── knowledge_repository.py
│   │   ├── ai_repository.py
│   │   └── growth_repository.py
│   │
│   ├── database/
│   │   ├── session.py
│   │   ├── config.py
│   │   ├── seed_runner.py
│   │   └── enums.py
│   │
│   └── services/
│
├── migrations/
│   ├── versions/
│   └── env.py
│
├── scripts/
│   ├── init_database.py
│   ├── seed_database.py
│   ├── rebuild_embeddings.py
│   └── reset_database.py
│
├── alembic.ini
└── requirements.txt
```

所有数据库代码全部放入 `app/models` 与 `app/repositories`。

---

# 第二章 SQLAlchemy BaseModel（所有 Model 必须继承）

## 2.1 BaseModel 统一规范

所有 28 张表统一继承 BaseModel。

字段统一：

| 字段         | 类型       |
| ---------- | -------- |
| id         | UUID     |
| created_at | DATETIME |
| updated_at | DATETIME |

---

## 2.2 BaseModel 示例

```python
class BaseModel:

    id = mapped_column(
        CHAR(36),
        primary_key=True,
        default=lambda: str(uuid.uuid4())
    )

    created_at = mapped_column(
        DateTime(timezone=True),
        default=datetime.utcnow
    )

    updated_at = mapped_column(
        DateTime(timezone=True),
        default=datetime.utcnow,
        onupdate=datetime.utcnow
    )
```

所有 Model 禁止重复写这些字段。

---

## 2.3 Soft Delete Mixin（可选）

部分业务支持软删除：

```python
deleted_at = mapped_column(DateTime, nullable=True)
```

适用于：

- users
- courses
- conversations
- knowledge_documents

不适用于：

- learning_records
- quiz_records

---

# 第三章 SQLAlchemy Session 配置

## 3.1 session.py

数据库连接统一在一个文件。

职责：

- 创建 Engine。
- SessionLocal。
- Base.metadata。

---

## 3.2 Engine 配置

统一：

```python
create_engine(
    DATABASE_URL,
    pool_pre_ping=True,
    pool_size=20,
    max_overflow=10,
    echo=False
)
```

生产环境禁止 echo=True。

---

## 3.3 Session 生命周期

FastAPI Dependency：

```python
def get_db():

    db = SessionLocal()

    try:
        yield db

    finally:
        db.close()
```

所有 Repository 注入 db。

---

# 第四章 MySQL 配置规范

## 4.1 config.py

环境变量：

```env
DB_HOST=localhost

DB_PORT=3306

DB_NAME=programmind

DB_USER=root

DB_PASSWORD=password
```

统一读取 `.env`。

---

## 4.2 DATABASE_URL

```text
mysql+pymysql://root:password@localhost:3306/programmind
```

SQLAlchemy 使用。

---

## 4.3 字符集

创建数据库：

```sql
CREATE DATABASE programmind
CHARACTER SET utf8mb4
COLLATE utf8mb4_unicode_ci;
```

所有表保持一致。

---

# 第五章 Alembic Migration（完整流程）

## 5.1 初始化 Alembic

```bash
alembic init migrations
```

生成：

- env.py
- versions/
- script.py.mako

---

## 5.2 修改 env.py

导入：

Base.metadata。

所有 Models。

保证自动生成 Migration。

---

## 5.3 Migration 命名规范

| Version | 描述                      |
| ------- | ----------------------- |
| 001     | create_users            |
| 002     | create_profiles         |
| 003     | create_courses          |
| 004     | create_learning_tables  |
| 005     | create_knowledge_tables |
| 006     | create_ai_tables        |
| 007     | create_growth_tables    |
| 008     | create_indexes          |

禁止无意义命名。

---

## 5.4 自动生成 Migration

```bash
alembic revision --autogenerate \
-m "create learning tables"
```

检查 SQL。

禁止直接执行。

---

## 5.5 升级数据库

```bash
alembic upgrade head
```

数据库升级最新版。

---

## 5.6 回滚 Migration

```bash
alembic downgrade -1
```

开发阶段允许。

生产禁止。

---

# 第六章 建表顺序（必须严格执行）

数据库存在大量外键。

建表顺序不能乱。

---

## 第一阶段 User Domain

1. users
2. user_profiles
3. user_roles

---

## 第二阶段 Course Domain

4. majors
5. courses
6. course_chapters
7. knowledge_points
8. course_enrollments

---

## 第三阶段 Learning Domain

9. homework_assignments
10. homework_submissions
11. experiments
12. experiment_submissions
13. quizzes
14. quiz_questions
15. quiz_records
16. learning_records

---

## 第四阶段 Knowledge Domain

17. knowledge_documents
18. knowledge_chunks
19. embedding_vectors
20. citation_records

---

## 第五阶段 AI Domain

21. conversations
22. ai_messages
23. ai_workflows
24. prompt_templates
25. conversation_memory
26. model_usage_logs

---

## 第六阶段 Growth Domain

27. learning_mirror
28. knowledge_mastery_records
29. learning_timeline
30. recommendations
31. risk_predictions
32. growth_reports

---

# 第七章 init.sql 建库规范

## 7.1 init.sql 目录

```text
backend/database/sql/

init.sql

indexes.sql

seed.sql
```

职责分离。

---

## 7.2 init.sql 内容

负责：

- 创建数据库。
- 创建所有表。
- 创建外键。
- 创建索引。

禁止插入数据。

---

## 7.3 indexes.sql

负责：

所有 UNIQUE INDEX。

所有普通 INDEX。

所有联合 INDEX。

方便单独优化。

---

## 7.4 seed.sql

负责初始化：

角色。

专业。

课程。

Prompt。

默认管理员。

---

# 第八章 Seed 数据规范

## 8.1 scripts/seed_database.py

初始化入口：

```bash
python scripts/seed_database.py
```

执行全部 Seed。

---

## 8.2 Seed 执行顺序

Major Seed

↓

Role Seed

↓

User Seed

↓

Course Seed

↓

Chapter Seed

↓

Knowledge Seed

↓

Prompt Seed

↓

Mirror Seed

↓

Recommendation Seed

---

## 8.3 默认管理员

| 字段       | 内容                   |
| -------- | -------------------- |
| username | admin                |
| email    | admin@programmind.ai |
| role     | admin                |

密码 Hash。

---

## 8.4 默认教师

teacher_demo。

Python老师。

DataStructure老师。

Network老师。

---

## 8.5 默认学生

student_demo。

人工智能2405。

自动选修三门课程。

---

# 第九章 Repository 工程规范

## 9.1 Repository 分层

Repository 只负责数据库。

禁止写业务逻辑。

---

## Repository 目录

```text
repositories/

user_repository.py

course_repository.py

learning_repository.py

knowledge_repository.py

ai_repository.py

growth_repository.py
```

一个领域一个 Repository。

---

## Repository 示例规范

```python
class CourseRepository:

    def create():

    def update():

    def delete():

    def get():

    def list():
```

所有 CRUD 在这里。

---

# 第十章 Service 与 Repository 分工

## Repository

负责：

SQL。

CRUD。

Join。

分页。

聚合。

---

## Service

负责：

业务规则。

权限。

Workflow。

Learning Mirror 更新。

AI 调用。

---

## 示例

HomeworkService：

发布作业。

↓

HomeworkRepository：

INSERT homework_assignments。

---

# 第十一章 SQLAlchemy Relationship 规范

所有外键必须建立 Relationship。

例如：

Course

↓

Chapters

↓

Knowledge Points

↓

Homework

↓

Quiz

↓

Documents

User

↓

Enrollments

↓

Learning Records

↓

Mirror

Conversation

↓

Messages

↓

Workflow

Document

↓

Chunks

↓

Embeddings

↓

Citation

统一 lazy="selectin"。

避免 N+1 查询。

---

# 第十二章 Enum 统一管理

所有枚举放：

app/database/enums.py

禁止散落。

---

## 示例

```python
class UserRole(Enum):

    student="student"

    teacher="teacher"

    admin="admin"
```

统一引用。

---

## 枚举分类

UserRole。

UserStatus。

HomeworkStatus。

ExperimentType。

QuizType。

ConversationType。

WorkflowStatus。

RecommendationType。

RiskLevel。

LearningState。

DocumentType。

---

# 第十三章 数据初始化脚本（Scripts）

## init_database.py

创建数据库。

执行 Migration。

初始化表。

---

## seed_database.py

执行全部 Seed。

可重复执行。

支持覆盖。

---

## rebuild_embeddings.py

重新生成所有 Embedding。

流程：

读取 Chunk。

↓

Embedding。

↓

FAISS。

↓

更新 embedding_vectors。

---

## reset_database.py

开发阶段：

删除数据库。

重新 Migration。

重新 Seed。

一键恢复。

---

# 第十四章 MySQL 索引优化规范

## 高频查询索引

必须建立：

student_id。

course_id。

knowledge_id。

conversation_id。

created_at。

---

## 联合索引

student_id + course_id。

course_id + chapter_id。

conversation_id + created_at。

knowledge_id + mastery_score。

---

## Explain 检查

上线前所有复杂 SQL 使用：

```sql
EXPLAIN SELECT ...
```

检查索引命中。

---

# 第十五章 数据一致性规范

## Transaction

涉及多个表更新必须事务。

例如：

提交测验：

quiz_records

+

learning_records

+

knowledge_mastery_records

+

learning_mirror

事务提交。

---

## SQLAlchemy Session

统一：

```python
with Session.begin():
```

保证一致性。

---

# 第十六章 数据备份规范

## 开发环境

每日：

mysqldump。

---

## 生产环境

凌晨：

全库备份。

Embedding 单独备份。

FAISS 单独备份。

OSS 文件单独备份。

---

## 恢复流程

数据库恢复。

↓

Embedding 恢复。

↓

重新建立 FAISS。

↓

校验 document_hash。

---

# 第十七章 Backend 开发 Checklist（数据库工程）

## SQLAlchemy

- [ ] BaseModel
- [ ] Session
- [ ] Config
- [ ] Enums

## Models

- [ ] 32 张 Model
- [ ] Relationship
- [ ] ForeignKey
- [ ] UUID

## Alembic

- [ ] Migration 初始化
- [ ] Version001~008
- [ ] Upgrade Head

## Seed

- [ ] Major
- [ ] User
- [ ] Course
- [ ] Chapter
- [ ] Knowledge
- [ ] Prompt
- [ ] Mirror

## Scripts

- [ ] init_database.py
- [ ] seed_database.py
- [ ] rebuild_embeddings.py
- [ ] reset_database.py

## Optimization

- [ ] Index
- [ ] Transaction
- [ ] Backup
- [ ] Explain SQL

---

# 第十八章 ProgramMind 数据库最终统计（V2.0）

## 数据库规模

| 数据域              | 表数量 |
| ---------------- | --- |
| User Domain      | 3   |
| Course Domain    | 5   |
| Learning Domain  | 8   |
| Knowledge Domain | 4   |
| AI Domain        | 6   |
| Growth Domain    | 6   |

总计：

**32 张业务数据表。**

---

## Backend 数据库目录统计

Models：32 个。

Repositories：6 个领域。

Migration：8 个版本。

Scripts：4 个数据库脚本。

Seed：8 个初始化模块。

---

# 第十九章 Backend 数据库开发顺序（必须执行）

第一周：

完成 User + Course。

第二周：

完成 Learning。

第三周：

完成 Knowledge（RAG）。

第四周：

完成 AI Domain。

第五周：

完成 Growth Domain。

第六周：

Migration、Seed、联调。

---

# 第二十章 DOC05 全文开发成果（数据库设计完成）

完成 DOC05 后，ProgramMind V2.0 数据库正式定型：

- MySQL 8.0 数据库架构。
- SQLAlchemy 32 张 Model。
- Alembic Migration 全流程。
- Repository + Service 分层规范。
- Seed 初始化规范。
- RAG 知识库数据库。
- AI Multi-Agent 数据库。
- Learning State Mirror 数据库。
- 推荐、风险预测、成长报告数据库。
- Backend 可直接按照本文档开始编码开发。
