# ProgramMind V2.0 后端开发规范

# Part03 —— Pydantic Schema 设计规范（完整版）

> 文档版本：V2.0
> 更新时间：2026-09
> 模块负责人：Backend（Pydantic Schema）
> 技术栈：FastAPI + Pydantic V2 + SQLAlchemy

---

# 第一章 Schema 模块定位

## 1.1 Schema 的职责

ProgramMind Backend 使用 **Pydantic V2** 作为 API 数据校验层。

Schema 负责：

- 请求参数校验（Request）
- 响应数据序列化（Response）
- 参数类型提示
- OpenAPI 自动生成
- 数据脱敏（例如 password_hash）

**原则：数据库 Model 永远不会直接返回给前端。**

---

## 1.2 Schema 与 Model 的关系

```text
Vue 前端

↓

Request Schema

↓

FastAPI Router

↓

Service

↓

Repository

↓

SQLAlchemy Model

↓

Response Schema

↓

Vue 页面
```

Schema 是 API 与数据库之间的隔离层。

---

## 1.3 Schema 分类规范

每个业务实体统一分为三类 Schema。

| 类型             | 用途                |
| -------------- | ----------------- |
| CreateSchema   | 创建资源（POST）        |
| UpdateSchema   | 更新资源（PUT / PATCH） |
| ResponseSchema | 返回数据（GET）         |

例如 User：

```text
UserCreateSchema

UserUpdateSchema

UserResponseSchema
```

所有实体保持一致。

---

# 第二章 Schemas 目录结构（最终版）

## 2.1 app/schemas/

```text
schemas/

common.py

auth.py

user.py

course.py

learning.py

knowledge.py

ai.py

growth.py

admin.py
```

按照业务领域划分。

---

## 2.2 每个文件负责内容

| 文件           | 内容                                |
| ------------ | --------------------------------- |
| common.py    | 分页、统一响应、错误响应                      |
| auth.py      | 登录、注册、JWT                         |
| user.py      | 用户资料                              |
| course.py    | 专业、课程、章节、知识点                      |
| learning.py  | 作业、实验、测验、学习记录                     |
| knowledge.py | RAG 文档、Chunk、Citation             |
| ai.py        | Conversation、Workflow、Prompt      |
| growth.py    | Mirror、Recommendation、Risk、Report |
| admin.py     | 管理员后台                             |

---

# 第三章 Common Schema（所有接口共用）

## 3.1 APIResponse（统一响应）

所有接口统一返回：

```json
{
  "code":200,
  "message":"success",
  "data":{}
}
```

禁止返回裸 JSON。

---

## 3.2 APIResponseSchema

字段：

| 字段      | 类型  |
| ------- | --- |
| code    | int |
| message | str |
| data    | Any |

所有 Response 外层统一这一层。

---

## 3.3 PaginationSchema

分页请求统一：

| 字段        | 类型  |
| --------- | --- |
| page      | int |
| page_size | int |

限制：

page ≥1

page_size ≤100

---

## 3.4 PaginationResponseSchema

返回：

```json
{
  "items":[],
  "total":120,
  "page":1,
  "page_size":20,
  "pages":6
}
```

所有列表接口统一。

---

## 3.5 ErrorResponseSchema

统一错误格式：

```json
{
 "code":401,
 "message":"Unauthorized",
 "detail":"Token expired."
}
```

禁止返回字符串。

---

# 第四章 Auth Schema（auth.py）

## 4.1 LoginRequestSchema

字段：

| 字段       | 类型  |
| -------- | --- |
| username | str |
| password | str |

校验：

密码长度。

用户名不能为空。

---

## 4.2 RegisterRequestSchema

字段：

| 字段        | 类型       |
| --------- | -------- |
| username  | str      |
| email     | EmailStr |
| password  | str      |
| real_name | str      |
| major     | str      |
| grade     | str      |

Email 自动校验。

---

## 4.3 TokenResponseSchema

返回：

| 字段            | 类型  |
| ------------- | --- |
| access_token  | str |
| refresh_token | str |
| expires_in    | int |
| token_type    | str |

---

## 4.4 RefreshRequestSchema

字段：

refresh_token。

返回新的 Access Token。

---

# 第五章 User Schema（user.py）

## 5.1 UserCreateSchema

字段：

username

email

password

role（默认 student）

---

## 5.2 UserUpdateSchema

允许更新：

头像。

简介。

兴趣。

学院。

专业。

年级。

---

## 5.3 UserProfileResponseSchema

返回：

| 字段         |
| ---------- |
| id         |
| username   |
| email      |
| avatar_url |
| real_name  |
| school     |
| college    |
| major      |
| grade      |
| bio        |
| interests  |

不返回：

password_hash。

---

## 5.4 UserSimpleSchema

列表使用。

字段：

id。

username。

avatar。

role。

避免重复传输 Profile。

---

# 第六章 Course Schema（course.py）

## 6.1 MajorSchema

字段：

major_name。

major_code。

college_name。

---

## 6.2 CourseCreateSchema

字段：

course_name。

major_id。

teacher_id。

semester。

credit。

description。

difficulty。

course_type。

---

## 6.3 CourseResponseSchema

返回：

课程信息。

教师信息。

章节数量。

学生数量。

学习进度（学生接口）。

---

## 6.4 ChapterSchema

字段：

chapter_number。

chapter_title。

estimated_hours。

knowledge_count。

---

## 6.5 KnowledgePointSchema

字段：

knowledge_name。

difficulty。

importance。

learning_objective。

mastery（学生接口）。

---

## 6.6 EnrollmentSchema

字段：

student_id。

course_id。

progress。

learning_hours。

status。

---

# 第七章 Learning Schema（learning.py）

## 7.1 HomeworkCreateSchema

字段：

title。

description。

homework_type。

due_time。

attachment_url。

---

## 7.2 HomeworkSubmissionSchema

字段：

submit_content。

attachment_url。

version。

---

## 7.3 HomeworkResponseSchema

返回：

标题。

截止时间。

是否提交。

分数。

AI反馈。

教师反馈。

---

## 7.4 ExperimentCreateSchema

字段：

title。

objective。

description。

expected_result。

due_time。

---

## 7.5 ExperimentSubmissionSchema

字段：

report_markdown。

attachment_url。

code_repository。

screenshot_url。

---

## 7.6 QuizCreateSchema

字段：

title。

chapter_id。

duration_minutes。

total_score。

quiz_type。

---

## 7.7 QuizQuestionSchema

字段：

question_type。

title。

options。

difficulty。

score。

---

## 7.8 QuizSubmitSchema

字段：

quiz_id。

answers。

duration_seconds。

---

## 7.9 LearningRecordResponseSchema

返回：

event_type。

course_name。

chapter_name。

created_at。

duration_seconds。

payload。

---

# 第八章 Knowledge Schema（knowledge.py）

## 8.1 DocumentUploadSchema

字段：

course_id。

chapter_id。

document_name。

document_type。

file。

---

## 8.2 DocumentResponseSchema

返回：

解析状态。

Chunk 数。

摘要。

文件信息。

---

## 8.3 ChunkResponseSchema

返回：

chunk_index。

page_number。

token_count。

content。

knowledge_name。

---

## 8.4 CitationSchema

返回：

document_name。

page_number。

similarity_score。

citation_text。

---

## 8.5 KnowledgeSearchSchema

请求：

query。

course_id。

top_k。

返回：

Chunk 列表。

Citation。

---

# 第九章 AI Schema（ai.py）

## 9.1 ConversationCreateSchema

字段：

conversation_type。

course_id。

conversation_title（可空）。

---

## 9.2 ConversationResponseSchema

返回：

标题。

消息数量。

模型。

Agent。

更新时间。

---

## 9.3 MessageRequestSchema

字段：

conversation_id。

content。

stream（bool）。

---

## 9.4 MessageResponseSchema

返回：

role。

content。

citations。

latency_ms。

token_usage。

---

## 9.5 WorkflowCreateSchema

字段：

workflow_type。

input。

parameters。

---

## 9.6 WorkflowResponseSchema

返回：

progress。

status。

current_step。

workflow_result。

---

## 9.7 PromptResponseSchema

管理员接口。

返回 Prompt 模板。

版本。

启用状态。

---

# 第十章 Growth Schema（growth.py）

## 10.1 LearningMirrorResponseSchema

返回：

overall_score。

六维状态。

雷达图数据。

learning_state。

---

## 10.2 MasteryResponseSchema

返回：

knowledge_name。

mastery_score。

confidence。

trend。

---

## 10.3 RecommendationResponseSchema

返回：

title。

description。

priority。

reason。

status。

---

## 10.4 RiskPredictionSchema

返回：

risk_score。

risk_level。

reasons。

intervention_suggestion。

---

## 10.5 GrowthReportResponseSchema

返回：

summary。

overall_score。

mastery_distribution。

recommendations。

report_markdown。

---

# 第十一章 Schema 校验规范（Field Validation）

## 11.1 String 长度

统一限制：

| 字段          | 最大长度     |
| ----------- | -------- |
| username    | 50       |
| title       | 200      |
| course_name | 120      |
| description | LONGTEXT |

使用 Field(max_length=)。

---

## 11.2 数值范围

例如：

progress：

0~100。

mastery_score：

0~1。

risk_score：

0~1。

使用 ge/le。

---

## 11.3 Email 校验

使用：

EmailStr。

自动校验邮箱格式。

---

## 11.4 日期时间

统一：

datetime。

ISO8601 返回。

UTC 保存。

北京时间展示交给前端。

---

# 第十二章 ORM → Schema 转换规范

## 12.1 Response 使用 from_attributes

Pydantic V2：

开启：

from_attributes=True。

允许 ORM 自动转换。

---

## 12.2 嵌套 Schema

CourseResponse：

嵌套：

TeacherSimpleSchema。

MajorSchema。

ChapterSchema[]。

禁止返回 ORM 对象。

---

## 12.3 List Response

统一：

PaginationResponseSchema[CourseResponseSchema]

列表全部支持泛型分页。

---

# 第十三章 Schema 命名规范

统一命名：

| 操作   | Schema               |
| ---- | -------------------- |
| 创建用户 | UserCreateSchema     |
| 更新用户 | UserUpdateSchema     |
| 用户详情 | UserResponseSchema   |
| 创建课程 | CourseCreateSchema   |
| 更新课程 | CourseUpdateSchema   |
| 课程详情 | CourseResponseSchema |

禁止：

UserDTO。

CourseVO。

DataBean。

---

# 第十四章 Schema Checklist（Backend）

## Common

- [ ] APIResponse
- [ ] Pagination
- [ ] ErrorResponse

## Auth

- [ ] Login
- [ ] Register
- [ ] Token
- [ ] Refresh

## User

- [ ] Create
- [ ] Update
- [ ] Response
- [ ] Simple

## Course

- [ ] Major
- [ ] Course
- [ ] Chapter
- [ ] Knowledge
- [ ] Enrollment

## Learning

- [ ] Homework
- [ ] Experiment
- [ ] Quiz
- [ ] Record

## Knowledge

- [ ] Document
- [ ] Chunk
- [ ] Citation

## AI

- [ ] Conversation
- [ ] Message
- [ ] Workflow
- [ ] Prompt

## Growth

- [ ] Mirror
- [ ] Mastery
- [ ] Recommendation
- [ ] Risk
- [ ] Report

---

# 第十五章 本章开发成果

完成 Part03 后，ProgramMind Backend 将建立完整的 Pydantic Schema 体系：

- 8 个 Schema 文件。
- 70+ Request / Response Schema。
- 所有 API 参数统一校验。
- OpenAPI 文档自动生成。
- ORM 与前端数据彻底解耦。
- Backend 可以直接开始编写 Router 与 Service。
