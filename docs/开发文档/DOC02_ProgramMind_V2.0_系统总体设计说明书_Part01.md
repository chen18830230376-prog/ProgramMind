# ProgramMind V2.0 系统总体设计说明书（SDS）

# Part 01 —— 系统总体架构设计（Architecture Overview）

> 文档版本：V2.0
> 
> 项目名称：ProgramMind——面向高校学科建设的垂类大模型与智能教学科研平台
> 
> 本文档作为整个项目唯一技术架构标准，用于指导前端、后端、AI、数据库四个开发方向协同开发。

---

# 第一章 系统设计目标

## 1.1 系统定位

ProgramMind V2.0 是一套 **AI Native 教学科研平台**。

平台围绕高校课程建设，将课程资源、知识库、AI、多智能体、学习状态镜像整合为统一系统。

ProgramMind V2.0 不再是 Demo，而是一个可持续扩展的平台架构。

---

## 1.2 系统设计目标

本系统需要满足以下目标。

| 目标        | 描述                          |
| --------- | --------------------------- |
| 可扩展       | 后续支持更多课程、学院、多学校。            |
| AI Native | AI 深度融入教学流程，而不是聊天机器人。       |
| 模块解耦      | 前端、后端、AI 独立开发。              |
| 数据驱动      | 所有行为进入状态引擎。                 |
| 工程化       | Git、Docker、ORM、API、测试全部规范化。 |

---

## 1.3 技术路线

ProgramMind V2.0 使用四层架构。

```text
Presentation Layer（Vue）

↓

Application Layer（FastAPI）

↓

AI Engine Layer（RAG + Agent + State Engine）

↓

Data Layer（MySQL + Vector DB）
```

各层之间只能通过 API 或 Service 通信。

禁止跨层调用数据库。

---

# 第二章 总体系统架构

## 2.1 四层架构图

```text
                    ProgramMind V2.0 Architecture

 ┌──────────────────────────────────────────────────────────┐
 │                  Vue3 Frontend Layer                     │
 │----------------------------------------------------------│
 │ Workspace  Learning  Teaching  AI Center  Growth Center  │
 │ Element Plus / Pinia / Vue Router / ECharts             │
 └──────────────────────────────────────────────────────────┘
                          │ REST API
                          ▼
 ┌──────────────────────────────────────────────────────────┐
 │                 FastAPI Backend Layer                    │
 │----------------------------------------------------------│
 │ Auth │ Course │ Homework │ Quiz │ Experiment │ AI API    │
 │ Notification │ Upload │ Analytics │ Growth API            │
 └──────────────────────────────────────────────────────────┘
                          │ Service
                          ▼
 ┌──────────────────────────────────────────────────────────┐
 │                  AI Engine Layer                         │
 │----------------------------------------------------------│
 │ RAG Retriever │ Multi-Agent │ Prompt Engine │ StateEngine│
 │ Citation │ Embedding │ Recommendation │ Memory           │
 └──────────────────────────────────────────────────────────┘
                          │ Repository
                          ▼
 ┌──────────────────────────────────────────────────────────┐
 │                   Data Layer                             │
 │----------------------------------------------------------│
 │ MySQL │ SQLAlchemy │ Alembic │ Vector DB │ File Storage  │
 └──────────────────────────────────────────────────────────┘
```

---

## 2.2 四层职责划分

### Presentation Layer（前端）

负责：

- 页面展示。
- 页面状态。
- 请求 API。
- 图表展示。
- AI Streaming 展示。

不负责：

- 数据计算。
- 权限判断。
- AI 推理。

---

### Backend Layer（业务层）

负责：

- 权限。
- CRUD。
- 参数校验。
- 上传下载。
- Workflow 调度入口。
- AI API。

不负责：

- Embedding。
- Agent 推理。
- Prompt。

---

### AI Engine Layer

负责：

- RAG。
- Multi-Agent。
- State Engine。
- Memory。
- Recommendation。
- Citation。

这是 AI 成员主要开发区域。

---

### Data Layer

负责：

- MySQL。
- ORM。
- Migration。
- Vector Store。
- 文件存储。

所有数据统一管理。

---

# 第三章 模块划分设计

ProgramMind V2.0 共设计 **13 个一级模块**。

## 3.1 一级模块

| 模块                  | 功能       |
| ------------------- | -------- |
| Auth Center         | 登录注册权限。  |
| Workspace Center    | 双角色工作台。  |
| Course Center       | 课程管理。    |
| Learning Center     | 学习模块。    |
| Teaching Center     | 教学模块。    |
| AI Center           | AI 工具中心。 |
| Growth Center       | 学习状态镜像。  |
| Knowledge Center    | 学科知识库。   |
| Workflow Center     | 多智能体工作流。 |
| Notification Center | 通知系统。    |
| Upload Center       | 文件管理。    |
| Analytics Center    | 学情分析。    |
| Profile Center      | 用户中心。    |

---

## 3.2 模块依赖图

```text
Workspace
│
├── Course Center
│   ├── Homework
│   ├── Quiz
│   ├── Experiment
│   └── Knowledge
│
├── AI Center
│   ├── Workflow
│   ├── Tutor
│   ├── Lesson
│   ├── PPT
│   └── Summary
│
└── Growth Center
    ├── Mastery
    ├── Heatmap
    ├── Timeline
    └── Recommendation
```

模块之间只能调用 Service。

---

# 第四章 技术栈设计（正式版）

## 4.1 前端技术栈

| 技术           | 版本     |
| ------------ | ------ |
| Vue          | 3.5.x  |
| Vite         | 7.x    |
| Vue Router   | 4.x    |
| Pinia        | 3.x    |
| Element Plus | 2.11.x |
| Axios        | 最新稳定版  |
| ECharts      | 6.x    |
| TailwindCSS  | 4.x    |
| Markdown-It  | 最新稳定版  |
| Highlight.js | 最新稳定版  |

---

### 前端职责

每位前端成员必须遵循：

- Composition API。
- `<script setup>`。
- TypeScript 可选（推荐）。

所有请求统一 Axios。

---

## 4.2 后端技术栈

| 技术               | 用途      |
| ---------------- | ------- |
| FastAPI          | Web API |
| SQLAlchemy 2.x   | ORM     |
| Alembic          | 数据迁移    |
| Pydantic V2      | 数据模型    |
| Uvicorn          | 服务启动    |
| python-multipart | 文件上传    |
| Passlib/Bcrypt   | 密码哈希    |
| JWT              | 登录鉴权    |

---

### 后端职责

负责：

- API。
- Service。
- Repository。
- Auth。
- Upload。
- Analytics。

---

## 4.3 AI 技术栈

| 技术            | 用途              |
| ------------- | --------------- |
| Ollama        | 本地模型。           |
| Qwen3         | 默认大模型。          |
| DeepSeek      | 推理模型。           |
| bge-m3        | Embedding。      |
| FAISS/Chroma  | 向量库。            |
| LangGraph（推荐） | Agent Workflow。 |

---

## 4.4 数据技术栈

| 技术         | 用途         |
| ---------- | ---------- |
| MySQL8     | 主数据库。      |
| SQLAlchemy | ORM。       |
| Alembic    | Migration。 |
| Redis（预留）  | Cache。     |
| MinIO（预留）  | 文件对象存储。    |

---

# 第五章 前后端目录结构（正式版）

## 5.1 GitHub 根目录

```text
ProgramMind/
│
├── frontend/
├── backend/
├── ai-engine/
├── docs/
├── scripts/
├── docker/
├── dataset/
├── tests/
├── assets/
├── README.md
└── .gitignore
```

---

## 5.2 frontend 目录

```text
frontend/
│
├── src/
│   ├── api/
│   ├── components/
│   ├── layouts/
│   ├── router/
│   ├── stores/
│   ├── views/
│   ├── styles/
│   ├── assets/
│   └── utils/
│
├── public/
├── package.json
└── vite.config.ts
```

---

### 前端职责划分

| 文件夹        | 职责                    |
| ---------- | --------------------- |
| api        | Axios 请求。             |
| stores     | Pinia。                |
| router     | 路由。                   |
| components | 公共组件。                 |
| layouts    | Workspace Layout。     |
| views      | 全部页面。                 |
| utils      | Markdown、Token、格式化工具。 |

---

## 5.3 backend 目录

```text
backend/
│
├── app/
│   ├── api/
│   ├── core/
│   ├── models/
│   ├── schemas/
│   ├── services/
│   ├── repositories/
│   ├── middleware/
│   ├── utils/
│   └── main.py
│
├── migrations/
├── uploads/
├── requirements.txt
└── alembic.ini
```

---

### 后端职责划分

| 文件夹          | 职责          |
| ------------ | ----------- |
| api          | Router。     |
| schemas      | Pydantic。   |
| services     | 业务逻辑。       |
| repositories | 数据访问。       |
| models       | SQLAlchemy。 |
| middleware   | JWT。        |
| utils        | 公共工具。       |

---

## 5.4 AI Engine 目录（新增）

```text
ai-engine/
│
├── rag/
├── agents/
├── prompts/
├── workflows/
├── memory/
├── state_engine/
├── recommendation/
└── models/
```

这是 AI 成员开发目录。

---

# 第六章 四人开发职责映射

## 6.1 四人职责

| 成员       | GitHub 目录                         |
| -------- | --------------------------------- |
| 产品/AI（你） | docs、ai-engine、architecture       |
| 前端       | frontend/src                      |
| 后端       | backend/app                       |
| AI/RAG   | ai-engine/rag、agents、state_engine |

---

## 6.2 Git 分支规范

```text
main

develop

feature/frontend

feature/backend

feature/rag

feature/agent
```

禁止直接提交 main。

所有开发提交 develop。

---

# 第七章 系统生命周期

## 7.1 系统启动流程

```text
浏览器

↓

Vue App

↓

Axios

↓

FastAPI

↓

Service

↓

Repository

↓

MySQL
```

AI 请求：

```text
Vue

↓

FastAPI

↓

AI Engine

↓

LLM / RAG / Agent

↓

Response
```

---

## 7.2 页面请求生命周期

```text
Page Mounted

↓

Loading Skeleton

↓

API Request

↓

Success / Error

↓

Render

↓

User Action

↓

API Update

↓

Refresh State
```

统一生命周期。

---

# 第八章 系统设计规范

## 8.1 命名规范

统一：

### 页面

```text
WorkspaceDashboard.vue

HomeworkCenter.vue

KnowledgeGraph.vue
```

### API

```text
/api/v1/course/list

/api/v1/homework/list
```

### 数据表

```text
course_homework

learning_record

knowledge_chunk
```

---

## 8.2 时间规范

统一 UTC 存储。

前端转换北京时间。

---

## 8.3 文件规范

上传路径：

```text
uploads/course/{course_id}/

uploads/avatar/

uploads/homework/
```

统一 UUID 文件名。

---

# 本章输出成果

本章节确定了 ProgramMind V2.0 的：

- 四层系统架构。
- 一级模块划分。
- 技术栈。
- GitHub 目录。
- 前后端目录。
- AI Engine 目录。
- 四人职责。
- Git 分支规范。
- 生命周期规范。
- 命名规范。

这些内容作为整个项目开发的最高技术标准。

---

**DOC02 Part 01 完成。**
