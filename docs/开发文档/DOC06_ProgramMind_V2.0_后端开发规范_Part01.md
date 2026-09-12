# ProgramMind V2.0 后端开发规范

# Part01 —— FastAPI 工程规范与项目目录（完整版）

> 文档版本：V2.0
> 更新时间：2026-09
> 项目：ProgramMind——面向高校学科建设的垂类大模型与智能教学科研平台
> 技术栈：FastAPI + SQLAlchemy + MySQL + Redis + Alembic + LangChain + Docker

---

# 第一章 Backend 工程定位

## 1.1 Backend 职责

ProgramMind Backend 是整个项目的业务中心，负责：

- 用户认证（JWT）
- RBAC 权限控制
- MySQL 数据库访问
- AI Agent 调用
- RAG 检索服务
- 文件上传
- 学习状态镜像计算
- 推荐系统接口
- WebSocket / SSE 实时通信
- 后台定时任务

Backend **不负责页面渲染**，所有数据通过 REST API 或 SSE 返回给 Vue3 前端。

---

## 1.2 Backend 技术栈

| 模块             | 技术                                |
| -------------- | --------------------------------- |
| Web Framework  | FastAPI 0.118+                    |
| ORM            | SQLAlchemy 2.x                    |
| Database       | MySQL 8.0                         |
| Migration      | Alembic                           |
| Validation     | Pydantic V2                       |
| Authentication | JWT + OAuth2 PasswordBearer       |
| AI Framework   | LangChain + LangGraph             |
| Embedding      | bge-m3                            |
| Vector Store   | FAISS                             |
| Cache          | Redis                             |
| Async Task     | Celery（预留）                        |
| File Storage   | OSS / 本地 uploads                  |
| Deployment     | Docker + Nginx + Gunicorn/Uvicorn |

---

## 1.3 Backend 开发原则

ProgramMind Backend 遵循六项原则：

### 单一职责（SRP）

每一层只负责自己的事情。

例如：

Router 只接收请求。

Service 只写业务逻辑。

Repository 只操作数据库。

### 分层架构

Controller → Service → Repository → Database。

禁止跨层调用。

### 类型安全

所有请求必须使用 Pydantic Schema。

禁止直接接收 dict。

### 全异步设计

所有数据库、AI 调用、文件上传优先使用 async。

### 模块解耦

AI、Learning、Knowledge、Growth 独立模块。

### 可测试

所有 Service 支持 pytest 单元测试。

---

# 第二章 Backend 最终目录结构（完整版）

## 2.1 项目目录（最终版）

```text
backend/

├── app/
│
│   ├── main.py
│   ├── core/
│   ├── api/
│   ├── schemas/
│   ├── models/
│   ├── repositories/
│   ├── services/
│   ├── ai/
│   ├── knowledge/
│   ├── growth/
│   ├── learning/
│   ├── middleware/
│   ├── utils/
│   ├── database/
│   └── tasks/
│
├── migrations/
├── uploads/
├── tests/
├── scripts/
├── docs/
├── requirements.txt
├── Dockerfile
└── alembic.ini
```

整个 Backend 统一采用 Domain Driven Design（DDD）思想组织目录。

---

## 2.2 一级目录职责

| 目录           | 职责                              |
| ------------ | ------------------------------- |
| app/main.py  | FastAPI 启动入口                    |
| api          | 所有 Router                       |
| services     | 业务逻辑层                           |
| repositories | 数据访问层                           |
| models       | SQLAlchemy Models               |
| schemas      | Pydantic Models                 |
| ai           | AI Agent 引擎                     |
| knowledge    | RAG 知识库模块                       |
| growth       | Learning Mirror 模块              |
| learning     | Homework / Quiz / Experiment 模块 |
| core         | JWT、配置、日志                       |
| middleware   | 中间件                             |
| utils        | 工具函数                            |
| database     | Session、Seed、Enum               |
| tasks        | Celery / 定时任务                   |

---

# 第三章 app/main.py 启动规范

## 3.1 main.py 职责

整个 FastAPI 唯一启动入口。

负责：

- 创建 FastAPI App。
- 注册 Router。
- 注册 Middleware。
- 生命周期管理。
- 挂载静态目录。
- 初始化数据库。

---

## 3.2 main.py 初始化流程

```text
读取 Config

↓

创建 FastAPI()

↓

注册 Middleware

↓

注册 Exception Handler

↓

注册 Routers

↓

初始化 Redis

↓

初始化 AI Engine

↓

初始化 RAG Retriever

↓

Application Ready
```

---

## 3.3 生命周期（Lifespan）

启动：

初始化：

数据库连接。

Redis。

Embedding。

FAISS Index。

关闭：

关闭数据库连接。

释放 AI Session。

保存缓存。

统一放入 lifespan。

---

# 第四章 API Router 目录规范

## 4.1 Router 目录

```text
app/api/v1/

├── auth.py
├── users.py
├── courses.py
├── homework.py
├── experiments.py
├── quizzes.py
├── knowledge.py
├── ai.py
├── growth.py
├── dashboard.py
├── upload.py
└── admin.py
```

所有接口放这里。

---

## 4.2 API Version 管理

统一：

```text
/api/v1/
```

未来：

```text
/api/v2/
```

支持版本升级。

---

## 4.3 Router 注册规范

main.py 中统一注册。

禁止 Router 相互 import。

统一：

```python
app.include_router(...)
```

---

# 第五章 Core 模块规范

## 5.1 core/ 目录

```text
core/

config.py

security.py

logging.py

exceptions.py

responses.py

constants.py
```

Core 保存全局能力。

---

## 5.2 config.py

职责：

读取 `.env`。

输出：

Settings。

禁止项目其他地方直接读取环境变量。

统一依赖 Config。

---

## 5.3 security.py

职责：

JWT。

Password Hash。

Token 校验。

OAuth2。

Refresh Token。

全部认证能力集中这里。

---

## 5.4 logging.py

统一日志。

日志等级：

INFO。

WARNING。

ERROR。

DEBUG。

日志输出：

Console + File。

---

## 5.5 responses.py

统一返回格式。

所有接口必须返回统一结构。

禁止裸 dict。

---

# 第六章 Middleware 规范

## 6.1 middleware 目录

```text
middleware/

auth.py

cors.py

request_logger.py

rate_limit.py

exception_handler.py
```

---

## 6.2 Middleware 顺序

CORS。

↓

Request Logger。

↓

JWT Auth。

↓

Rate Limit。

↓

Router。

顺序不能乱。

---

## 6.3 Request Logger

记录：

请求路径。

耗时。

用户 ID。

IP。

Method。

Status。

写入日志。

---

## 6.4 Rate Limit（预留）

限制：

AI 接口。

登录接口。

上传接口。

例如：

一分钟：

20 次。

---

# 第七章 Utils 工具目录规范

## 7.1 utils/

```text
utils/

uuid_utils.py

datetime_utils.py

file_utils.py

markdown_utils.py

oss_utils.py

pagination.py
```

---

## 7.2 工具职责

UUID。

时间格式。

分页。

Markdown 清洗。

文件路径。

OSS URL。

不得写业务逻辑。

---

# 第八章 Schemas（Pydantic）目录规范

## 8.1 schemas/

```text
schemas/

auth.py

user.py

course.py

learning.py

knowledge.py

ai.py

growth.py

common.py
```

Schema 与 Models 一一对应。

---

## 8.2 Schema 分类

每个领域统一三类 Schema。

| 类型             | 用途        |
| -------------- | --------- |
| CreateSchema   | POST      |
| UpdateSchema   | PUT/PATCH |
| ResponseSchema | GET 返回    |

例如：

CourseCreate。

CourseUpdate。

CourseResponse。

---

## 8.3 Schema 命名规范

统一：

```
UserCreateSchema

UserLoginSchema

UserResponseSchema

HomeworkSubmitSchema

QuizAnswerSchema
```

禁止混乱命名。

---

# 第九章 Models（SQLAlchemy）目录规范

## 9.1 Models 分类

```text
models/

base.py

user.py

course.py

learning.py

knowledge.py

ai.py

growth.py
```

一个领域一个文件。

---

## 9.2 每个文件内容

例如：

course.py

包含：

Major。

Course。

CourseChapter。

KnowledgePoint。

Enrollment。

统一放一起。

---

## 9.3 Relationship 原则

所有 FK 建立 relationship。

lazy="selectin"。

cascade="all, delete-orphan"。

禁止裸 ForeignKey 无 relationship。

---

# 第十章 Repositories（数据访问层）

## 10.1 Repository 原则

Repository 只操作数据库。

禁止：

AI。

HTTP。

Redis。

业务逻辑。

---

## 10.2 Repository 分类

| Repository          | 负责           |
| ------------------- | ------------ |
| UserRepository      | 用户           |
| CourseRepository    | 课程           |
| LearningRepository  | 作业/实验/测验     |
| KnowledgeRepository | RAG          |
| AIRepository        | Conversation |
| GrowthRepository    | Mirror       |

---

## 10.3 Repository 返回值规范

返回 ORM Model。

不返回 dict。

Service 再转换 Schema。

---

# 第十一章 Services（业务逻辑层）

## 11.1 Service 分类

每个领域一个 Service。

支持组合调用。

---

## 11.2 Service 目录

```text
services/

auth_service.py

course_service.py

homework_service.py

quiz_service.py

knowledge_service.py

ai_service.py

growth_service.py
```

---

## 11.3 Service 职责

权限。

事务。

业务计算。

AI 调用。

Mirror 更新。

推荐生成。

---

# 第十二章 Backend 模块依赖关系（必须遵守）

```text
API Router

↓

Service

↓

Repository

↓

Database

↓

MySQL
```

AI Service：

Service

↓

AI Engine

↓

Repository

↓

Database

Growth：

Service

↓

Repository

↓

Mirror Builder

↓

Database

禁止 Repository 调 Service。

---

# 第十三章 Backend 环境变量规范（.env）

## 必须存在以下配置

```env
APP_NAME=ProgramMind

APP_ENV=development

APP_PORT=8000

SECRET_KEY=xxxxxxxx

JWT_EXPIRE_HOURS=2

REFRESH_EXPIRE_DAYS=7

DB_HOST=localhost

DB_PORT=3306

DB_NAME=programmind

DB_USER=root

DB_PASSWORD=123456

REDIS_HOST=localhost

REDIS_PORT=6379

OLLAMA_BASE_URL=http://localhost:11434

EMBEDDING_MODEL=bge-m3

VECTOR_STORE=faiss
```

统一通过 Settings 加载。

---

# 第十四章 Backend Checklist（工程初始化）

## FastAPI

- [ ] main.py
- [ ] lifespan
- [ ] Router 注册

## Core

- [ ] config
- [ ] security
- [ ] logging
- [ ] responses

## Middleware

- [ ] JWT
- [ ] Logger
- [ ] CORS
- [ ] RateLimit

## Schemas

- [ ] auth
- [ ] user
- [ ] course
- [ ] learning
- [ ] ai
- [ ] growth

## Models

- [ ] 32 张 Models 导入

## Repository

- [ ] 六个 Repository

## Service

- [ ] 六个 Service

---

# 第十五章 本章开发成果

完成 Part01 后，Backend 工程正式建立：

- FastAPI 工程目录统一。
- Core 模块统一。
- Middleware 架构统一。
- Schema / Model / Repository / Service 分层完成。
- 所有开发成员按照统一目录提交代码，不会出现目录混乱和循环依赖问题。
