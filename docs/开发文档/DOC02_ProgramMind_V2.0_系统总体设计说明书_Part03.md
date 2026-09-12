# ProgramMind V2.0 系统总体设计说明书（SDS）

# Part 03 —— 后端架构设计（Backend Architecture Specification）

> 面向开发成员：后端负责人（FastAPI 开发）
> 
> 技术栈：FastAPI + SQLAlchemy + Alembic + Pydantic V2 + JWT + MySQL + Uvicorn

---

# 第十三章 后端总体架构

## 13.1 后端设计目标

ProgramMind 后端负责整个平台业务逻辑，不负责 AI 推理。

设计目标：

| 目标               | 描述                  |
| ---------------- | ------------------- |
| API First        | 所有功能通过 REST API 提供。 |
| Service Layer    | Router 不写业务逻辑。      |
| Repository Layer | 数据访问统一封装。           |
| ORM              | SQLAlchemy 管理全部数据库。 |
| 类型安全             | Pydantic 管理请求/响应模型。 |
| 权限统一             | JWT + RBAC。         |
| 易扩展              | AI Engine 可独立部署。    |

---

## 13.2 Backend 四层架构

```text
FastAPI Backend

Router Layer

↓

Service Layer

↓

Repository Layer

↓

MySQL Database
```

说明：

- Router：HTTP 请求入口。
- Service：业务逻辑。
- Repository：数据库操作。
- Model：ORM。
- Schema：数据校验。

禁止 Router 写 SQL。

---

## 13.3 Backend 数据流

```text
Client

↓

FastAPI Router

↓

JWT Middleware

↓

Service

↓

Repository

↓

SQLAlchemy

↓

MySQL
```

返回 ResponseModel。

---

# 第十四章 后端目录结构（完整版）

## 14.1 backend 完整目录树

```text
backend/

├── app/
│
├── api/
│   ├── auth.py
│   ├── workspace.py
│   ├── course.py
│   ├── homework.py
│   ├── experiment.py
│   ├── quiz.py
│   ├── knowledge.py
│   ├── ai.py
│   ├── workflow.py
│   ├── growth.py
│   ├── analytics.py
│   ├── notification.py
│   ├── upload.py
│   └── profile.py
│
├── core/
│   ├── config.py
│   ├── database.py
│   ├── security.py
│   ├── jwt.py
│   ├── dependency.py
│   └── logger.py
│
├── middleware/
│   ├── auth.py
│   ├── permission.py
│   ├── cors.py
│   └── exception.py
│
├── models/
│
├── repositories/
│
├── schemas/
│
├── services/
│
├── utils/
│
├── uploads/
│
├── migrations/
│
├── tests/
│
├── main.py
│
├── requirements.txt
│
└── alembic.ini
```

---

## 14.2 每个目录职责

| 文件夹          | 职责                |
| ------------ | ----------------- |
| api          | Router。           |
| services     | 业务逻辑。             |
| repositories | ORM CRUD。         |
| models       | SQLAlchemy Model。 |
| schemas      | Pydantic Schema。  |
| middleware   | 权限、中间件。           |
| core         | 配置、数据库、安全。        |
| utils        | 工具函数。             |
| uploads      | 上传文件。             |
| tests        | 单元测试。             |

---

# 第十五章 FastAPI 应用初始化

## 15.1 main.py 生命周期

启动流程：

```text
Load Config

↓

Connect Database

↓

Register Middleware

↓

Register Routers

↓

Startup Events

↓

Uvicorn
```

---

## 15.2 Router 注册规范

统一 `/api/v1`

```text
/api/v1/auth

/api/v1/course

/api/v1/homework

/api/v1/experiment

/api/v1/quiz

/api/v1/knowledge

/api/v1/ai

/api/v1/growth

/api/v1/profile

/api/v1/workspace
```

禁止出现 `/api/course/list`。

全部版本化。

---

## 15.3 生命周期事件

Startup：

- 初始化数据库。
- 初始化向量库连接。
- 初始化日志。
- 初始化上传目录。

Shutdown：

- 关闭数据库连接。
- Flush Logger。
- 释放 AI Client。

---

# 第十六章 Core 基础模块设计

## 16.1 config.py

统一配置来源 `.env`

配置项：

| 配置             |
| -------------- |
| PROJECT_NAME   |
| VERSION        |
| SECRET_KEY     |
| JWT_SECRET     |
| MYSQL_HOST     |
| MYSQL_PORT     |
| MYSQL_DATABASE |
| MYSQL_USER     |
| MYSQL_PASSWORD |
| UPLOAD_DIR     |
| VECTOR_DB_DIR  |
| OLLAMA_URL     |

禁止硬编码。

---

## 16.2 database.py

职责：

SQLAlchemy Engine。

SessionFactory。

Base。

事务管理。

统一：

```python
SessionLocal()

get_db()
```

---

## 16.3 security.py

负责：

密码哈希。

密码验证。

使用：

Bcrypt。

接口：

- hash_password()
- verify_password()

---

## 16.4 jwt.py

负责：

JWT Token。

Access Token。

Refresh Token。

接口：

- create_access_token
- create_refresh_token
- verify_token

---

## 16.5 dependency.py

统一依赖注入。

包括：

- get_current_user
- get_teacher_user
- get_student_user
- get_db

所有 Router 使用 Depends。

---

## 16.6 logger.py

统一日志。

输出：

- INFO
- WARNING
- ERROR
- DEBUG

日志目录：

```text
logs/

backend.log

error.log

ai.log
```

---

# 第十七章 Middleware 设计

## 17.1 JWT Middleware

流程：

```text
Authorization Header

↓

Verify JWT

↓

Inject User

↓

Request.state.user
```

失败：

401。

---

## 17.2 Permission Middleware

支持 RBAC。

角色：

Teacher。

Student。

Admin（预留）。

权限矩阵统一管理。

---

## 17.3 Exception Middleware

统一异常。

返回：

```json
{
"code":50001,
"message":"Homework not found",
"data":null
}
```

所有异常统一格式。

---

## 17.4 CORS Middleware

开发：

允许 localhost。

生产：

限制域名。

---

# 第十八章 Model 层设计

## 18.1 Model 分类

目录：

```text
models/

user.py

course.py

chapter.py

resource.py

homework.py

experiment.py

quiz.py

knowledge.py

growth.py

notification.py

ai.py
```

每个文件一个实体。

---

## 18.2 ORM 规范

每张表：

- id
- created_at
- updated_at

统一 BaseModelMixin。

所有时间自动维护。

---

## 18.3 Relationship 规范

例如：

Course

↓

Chapter

↓

KnowledgePoint

↓

Chunk

统一 relationship。

避免手写 Join。

---

# 第十九章 Schema 层设计（Pydantic）

## 19.1 Schema 分类

```text
schemas/

auth.py

course.py

homework.py

experiment.py

quiz.py

knowledge.py

growth.py

profile.py

common.py
```

---

## 19.2 请求模型规范

Create。

Update。

Delete。

Detail。

List。

分页统一。

---

## 19.3 Response Model

统一：

```json
{
"code":0,
"message":"success",
"data":{}
}
```

分页：

```json
{
"list":[],
"total":100,
"page":1,
"page_size":10
}
```

---

# 第二十章 Repository 层设计

## 20.1 Repository 职责

Repository 只负责数据库。

禁止业务判断。

例如：

CourseRepository：

- create
- update
- delete
- get
- list

---

## 20.2 Repository 分类

```text
repositories/

user_repository.py

course_repository.py

homework_repository.py

experiment_repository.py

quiz_repository.py

knowledge_repository.py

growth_repository.py

notification_repository.py

ai_repository.py
```

---

## 20.3 Repository 返回规范

返回 ORM。

Service 转 Schema。

禁止 Repository 返回 JSON。

---

# 第二十一章 Service 层设计

## 21.1 Service 职责

所有业务逻辑。

例如：

HomeworkService：

- publish_homework
- submit_homework
- grade_homework

---

## 21.2 Service 分类

```text
services/

auth_service.py

workspace_service.py

course_service.py

homework_service.py

experiment_service.py

quiz_service.py

knowledge_service.py

analytics_service.py

growth_service.py

notification_service.py

profile_service.py
```

---

## 21.3 Service 调用关系

```text
Router

↓

Service

↓

Repository

↓

DB
```

Service 可调用多个 Repository。

---

## 21.4 Service 事务规范

涉及多个 Repository：

统一事务。

例如：

批改作业：

- HomeworkSubmission
- Mastery
- Notification
- LearningRecord

一次 Commit。

失败 Rollback。

---

# 第二十二章 API 模块职责

## 22.1 Auth API

职责：

登录。

注册。

刷新 Token。

获取用户。

退出登录。

---

## 22.2 Workspace API

职责：

工作台首页。

今日任务。

AI 推荐。

通知。

统计。

---

## 22.3 Course API

职责：

课程 CRUD。

章节。

课程资源。

课程学生。

---

## 22.4 Homework API

职责：

发布。

提交。

批改。

详情。

列表。

---

## 22.5 Experiment API

职责：

实验 CRUD。

Starter Code。

提交。

批改。

---

## 22.6 Quiz API

职责：

题库。

Quiz。

提交。

自动评分。

统计。

---

## 22.7 Knowledge API

职责：

文档上传。

文档解析。

Chunk。

Graph。

Search。

---

## 22.8 AI API

职责：

Streaming Chat。

Workflow。

Prompt。

Conversation。

Memory。

---

## 22.9 Growth API

职责：

Mastery。

HeatMap。

Timeline。

Recommendation。

Risk。

---

## 22.10 Analytics API

职责：

教师分析。

学生分析。

课程分析。

AI Summary。

---

## 22.11 Notification API

职责：

通知。

已读。

Badge。

轮询。

---

## 22.12 Upload API

职责：

上传。

下载。

删除。

预览。

---

# 第二十三章 文件上传中心设计

## 23.1 上传目录

```text
uploads/

avatar/

course/

homework/

experiment/

knowledge/
```

UUID 文件名。

数据库记录元信息。

---

## 23.2 上传流程

```text
Client

↓

Upload API

↓

File Validator

↓

Storage

↓

DB Metadata
```

---

## 23.3 文件权限

Teacher：

课程资源。

Student：

Homework。

Experiment。

头像。

权限统一校验。

---

# 第二十四章 Notification Center

## 24.1 通知来源

Homework。

Quiz。

Experiment。

Grade。

AI。

System。

---

## 24.2 通知生命周期

Unread。

Read。

Archived（预留）。

---

## 24.3 推送策略

当前版本：

轮询。

未来：

WebSocket。

---

# 第二十五章 权限体系（RBAC）

## 25.1 角色

Teacher。

Student。

Admin（预留）。

---

## 25.2 权限矩阵

Teacher：

全部 Teaching API。

Student：

Learning API。

共同：

AI。

Growth。

Profile。

---

## 25.3 Depends 权限注入

Router 示例：

Teacher API：

Depends(get_teacher_user)

Student API：

Depends(get_student_user)

---

# 第二十六章 错误码规范

## 26.1 错误码范围

| 范围    | 含义         |
| ----- | ---------- |
| 0     | Success    |
| 10000 | Auth       |
| 20000 | Course     |
| 30000 | Homework   |
| 40000 | Experiment |
| 50000 | Quiz       |
| 60000 | AI         |
| 70000 | Growth     |
| 80000 | Upload     |
| 90000 | System     |

---

## 26.2 HTTP 状态使用规范

| HTTP | 场景    |
| ---- | ----- |
| 200  | 成功    |
| 201  | 创建成功  |
| 400  | 参数错误  |
| 401  | 未登录   |
| 403  | 权限不足  |
| 404  | 数据不存在 |
| 409  | 冲突    |
| 500  | 系统异常  |

---

# 第二十七章 后端开发顺序（必须遵循）

## 第一阶段（基础设施）

- Config。
- Database。
- JWT。
- Logger。
- Middleware。

---

## 第二阶段（用户系统）

- Auth。
- Profile。
- Workspace。

---

## 第三阶段（课程系统）

- Course。
- Resource。
- Chapter。

---

## 第四阶段（学习系统）

Homework。

Experiment。

Quiz。

Notification。

Upload。

---

## 第五阶段（Growth）

Mastery。

Timeline。

Analytics。

Recommendation。

---

## 第六阶段（AI API）

Conversation。

Workflow。

Knowledge。

Growth AI。

---

# 第二十八章 后端开发 Checklist

## 基础工程

- [ ] FastAPI 初始化
- [ ] SQLAlchemy 初始化
- [ ] Alembic 初始化
- [ ] JWT 登录
- [ ] Logger
- [ ] Config(.env)

## API

- [ ] Auth API
- [ ] Workspace API
- [ ] Course API
- [ ] Homework API
- [ ] Experiment API
- [ ] Quiz API
- [ ] Upload API
- [ ] Notification API
- [ ] Growth API
- [ ] AI API

## Service

- [ ] AuthService
- [ ] CourseService
- [ ] HomeworkService
- [ ] ExperimentService
- [ ] QuizService
- [ ] GrowthService
- [ ] AnalyticsService
- [ ] NotificationService

## Repository

- [ ] UserRepository
- [ ] CourseRepository
- [ ] HomeworkRepository
- [ ] ExperimentRepository
- [ ] QuizRepository
- [ ] GrowthRepository

## Middleware

- [ ] JWT Middleware
- [ ] Permission Middleware
- [ ] Exception Middleware
- [ ] CORS Middleware

---

# 本章输出成果

本章节定义了 ProgramMind V2.0 后端完整工程规范，包括：

- FastAPI 四层架构。
- backend 完整目录（40+ 文件）。
- Core 模块（Config、Database、JWT、Logger）。
- Middleware 权限体系。
- SQLAlchemy Model 规范。
- Pydantic Schema 规范。
- Repository / Service 分层。
- Upload Center。
- Notification Center。
- RBAC 权限设计。
- 错误码规范。
- 后端开发顺序与 Checklist。

本文件是后端成员开发唯一参考标准。

---

**DOC02 Part 03 完成。**
