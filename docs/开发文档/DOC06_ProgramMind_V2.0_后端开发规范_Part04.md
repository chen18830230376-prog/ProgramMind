# ProgramMind V2.0 后端开发规范

# Part04 —— Repository 与 Service 开发规范（完整版）

> 文档版本：V2.0
> 更新时间：2026-09
> 模块负责人：Backend
> 技术栈：FastAPI + SQLAlchemy 2.x + MySQL + Pydantic V2

---

# 第一章 Repository 与 Service 总体设计

## 1.1 为什么必须分层

ProgramMind Backend 必须采用四层架构：

```text
Vue Frontend

        │

        ▼

FastAPI Router（API）

        │

        ▼

Service（业务逻辑）

        │

        ▼

Repository（数据库）

        │

        ▼

MySQL
```

职责不能交叉。

---

## 1.2 Repository 职责

Repository **只负责数据库访问**。

允许：

- CRUD
- JOIN 查询
- 聚合查询
- 分页查询
- 排序
- 条件过滤

禁止：

- AI 调用
- 权限判断
- Learning Mirror 更新
- Redis 操作
- HTTP 请求

一句话：Repository 不知道业务。

---

## 1.3 Service 职责

Service **负责业务逻辑**。

包括：

- 权限校验
- 调用多个 Repository
- SQLAlchemy Transaction
- AI 调用
- RAG 调用
- Learning Mirror 更新
- Recommendation 生成
- Timeline 更新

一句话：Service 负责整个业务流程。

---

# 第二章 Repository 目录规范

## 2.1 repositories/

```text
repositories/

base_repository.py

user_repository.py

course_repository.py

learning_repository.py

knowledge_repository.py

ai_repository.py

growth_repository.py
```

每个领域一个 Repository 文件。

---

## 2.2 Repository 类划分

| Repository          | 管理数据表                                                        |
| ------------------- | ------------------------------------------------------------ |
| UserRepository      | users / profiles / roles                                     |
| CourseRepository    | majors / courses / chapters / knowledge_points / enrollments |
| LearningRepository  | homework / experiments / quizzes / learning_records          |
| KnowledgeRepository | documents / chunks / embeddings / citations                  |
| AIRepository        | conversations / messages / workflows / prompts               |
| GrowthRepository    | mirror / mastery / recommendation / report                   |

---

# 第三章 BaseRepository（所有 Repository 基类）

## 3.1 BaseRepository 功能

所有 Repository 继承 BaseRepository。

统一提供：

- create()
- update()
- delete()
- get_by_id()
- list()
- paginate()

避免重复代码。

---

## 3.2 BaseRepository 提供能力

统一：

UUID 查询。

分页。

软删除过滤。

created_at 排序。

异常转换。

---

## 3.3 Repository 返回值规范

Repository 返回：

SQLAlchemy ORM Model。

禁止返回：

- dict
- JSON
- ResponseSchema

Schema 转换放 Service。

---

# 第四章 UserRepository 规范

## 4.1 UserRepository 方法列表

```text
create_user()

get_user_by_id()

get_user_by_email()

get_user_by_username()

update_password()

update_login_info()

update_avatar()

update_profile()

disable_user()

delete_user()
```

---

## 4.2 查询规范

用户名唯一查询。

邮箱唯一查询。

UUID 查询。

全部返回 ORM。

---

## 4.3 ProfileRepository

负责：

- 创建 Profile。
- 更新兴趣标签。
- 更新简介。
- 更新学院专业。

独立 Repository。

---

# 第五章 CourseRepository 规范

## 5.1 CourseRepository 方法

```text
create_course()

update_course()

publish_course()

archive_course()

list_courses()

list_teacher_courses()

list_student_courses()

search_course()

delete_course()
```

---

## 5.2 ChapterRepository 方法

```text
create_chapter()

update_chapter()

delete_chapter()

reorder_chapters()

list_by_course()
```

---

## 5.3 KnowledgePointRepository 方法

```text
create_knowledge()

update_knowledge()

list_knowledge()

search_knowledge()

get_prerequisite()
```

---

## 5.4 EnrollmentRepository 方法

```text
enroll_course()

drop_course()

update_progress()

get_progress()

list_students()
```

---

# 第六章 LearningRepository 规范

## 6.1 HomeworkRepository

负责：

```text
create_homework()

publish_homework()

close_homework()

list_homework()

get_homework()
```

---

## 6.2 HomeworkSubmissionRepository

负责：

```text
submit()

resubmit()

grade()

latest_submission()

history()
```

支持版本记录。

---

## 6.3 ExperimentRepository

负责：

实验 CRUD。

实验提交。

实验评分。

---

## 6.4 QuizRepository

负责：

测验。

题目。

成绩。

统计。

---

## 6.5 LearningRecordRepository

负责：

新增学习事件。

查询学习流水。

统计学习时间。

热力图查询。

成长聚合查询。

---

# 第七章 KnowledgeRepository 规范

## 7.1 DocumentRepository

负责：

上传文档。

解析状态。

删除文档。

搜索文档。

---

## 7.2 ChunkRepository

负责：

新增 Chunk。

查询 Chunk。

按知识点查询 Chunk。

删除 Chunk。

---

## 7.3 EmbeddingRepository

负责：

创建 Embedding。

查询 Embedding。

重建 Embedding。

删除 Embedding。

---

## 7.4 CitationRepository

负责：

保存 Citation。

查询 Citation。

Conversation Citation。

---

# 第八章 AIRepository 规范

## 8.1 ConversationRepository

负责：

创建会话。

重命名。

归档。

删除。

获取历史。

---

## 8.2 MessageRepository

负责：

追加消息。

分页消息。

统计 Token。

删除消息。

---

## 8.3 WorkflowRepository

负责：

创建 Workflow。

更新 Progress。

完成 Workflow。

取消 Workflow。

---

## 8.4 PromptRepository

负责：

Prompt CRUD。

启停 Prompt。

查询版本。

---

## 8.5 UsageRepository

负责：

记录 Token。

模型统计。

每日统计。

用户统计。

---

# 第九章 GrowthRepository 规范

## 9.1 MirrorRepository

负责：

获取当前 Mirror。

刷新 Mirror。

更新六维向量。

Mirror 历史。

---

## 9.2 MasteryRepository

负责：

更新知识掌握度。

查询课程掌握图谱。

查询章节掌握图谱。

掌握度趋势。

---

## 9.3 RecommendationRepository

负责：

生成推荐。

查询推荐。

完成推荐。

忽略推荐。

---

## 9.4 RiskRepository

负责：

保存风险预测。

查询最新风险。

查询高风险学生。

---

## 9.5 GrowthReportRepository

负责：

生成成长报告。

查询周报。

查询月报。

查询学期报告。

---

# 第十章 Service 目录规范

## 10.1 services/

```text
services/

auth_service.py

course_service.py

homework_service.py

experiment_service.py

quiz_service.py

knowledge_service.py

ai_service.py

growth_service.py

dashboard_service.py
```

业务按领域划分。

---

## 10.2 Service 调用关系

例如 Homework：

Router

↓

HomeworkService

↓

HomeworkRepository

↓

LearningRecordRepository

↓

MirrorService

↓

RecommendationService

一个 Service 可以调用多个 Repository。

---

# 第十一章 SQLAlchemy Transaction 规范

## 11.1 必须事务的业务

以下操作必须开启事务：

| 操作      | 原因                             |
| ------- | ------------------------------ |
| 注册用户    | users + profile + mirror       |
| 提交作业    | submission + learning_record   |
| 批改作业    | score + mastery + mirror       |
| 提交测验    | quiz_record + mastery + mirror |
| AI 推荐生成 | recommendation + timeline      |

---

## 11.2 Transaction 生命周期

业务开始。

↓

数据库修改。

↓

Learning Mirror 更新。

↓

Timeline 更新。

↓

Commit。

异常：

Rollback。

---

## 11.3 Service 中事务规范

统一：

Session.begin()。

禁止 Repository Commit。

Commit 放 Service。

---

# 第十二章 CRUD 编写规范

## 12.1 Create

流程：

Schema

↓

ORM Model

↓

Repository.create()

↓

Commit

↓

ResponseSchema

---

## 12.2 Update

查询对象。

↓

更新字段。

↓

Commit。

↓

返回最新对象。

---

## 12.3 Delete

默认软删除。

仅日志允许物理删除。

---

## 12.4 Batch Update

统一：

Repository.batch_update()

减少循环 Commit。

---

# 第十三章 查询规范（Query）

## 13.1 分页查询

统一：

page。

page_size。

offset。

limit。

返回 PaginationResponseSchema。

---

## 13.2 排序规范

默认：

updated_at DESC。

支持：

created_at。

score。

progress。

---

## 13.3 条件过滤

统一 Query Params：

status。

course_id。

teacher_id。

student_id。

keyword。

date_range。

---

## 13.4 搜索规范

关键词搜索：

LIKE。

全文搜索预留 ElasticSearch。

---

# 第十四章 Learning Mirror 更新流程（核心业务）

## 14.1 Homework 提交流程

HomeworkService

↓

HomeworkSubmissionRepository

↓

LearningRecordRepository

↓

MasteryService.update()

↓

MirrorService.refresh()

↓

TimelineService.append()

↓

Commit

---

## 14.2 Quiz 提交流程

QuizService.submit()

↓

QuizRecordRepository

↓

MasteryRepository

↓

RiskService.predict()

↓

MirrorRepository

↓

RecommendationRepository

↓

TimelineRepository

---

## 14.3 Experiment 完成流程

ExperimentSubmission

↓

LearningRecord

↓

PracticeScore 更新。

↓

Mirror 更新。

---

# 第十五章 Repository 与 Schema 转换规范

## 15.1 Create

CreateSchema

↓

Service

↓

ORM

↓

Repository

---

## 15.2 Response

Repository 返回 ORM。

↓

Service 转 ResponseSchema。

↓

Router 返回 APIResponseSchema。

统一转换。

---

## 15.3 ORM 嵌套转换

Course ORM。

↓

CourseResponseSchema。

↓

TeacherSimpleSchema。

↓

ChapterSchema[]。

自动转换。

---

# 第十六章 异常处理规范

## 16.1 Repository 不处理 HTTP

Repository 抛数据库异常。

Service 转业务异常。

Router 返回 HTTPException。

---

## 16.2 常见业务异常

| 异常       | HTTP |
| -------- | ---- |
| 用户不存在    | 404  |
| 权限不足     | 403  |
| 参数非法     | 422  |
| 重复数据     | 409  |
| Token 失效 | 401  |

统一异常结构。

---

# 第十七章 Repository 单元测试规范

## tests/repositories/

```text
tests/

repositories/

test_user_repository.py

test_course_repository.py

test_learning_repository.py

test_growth_repository.py
```

Repository 单独测试 CRUD。

使用测试数据库。

---

## Service 测试

测试：

事务。

权限。

Mirror 更新。

Recommendation。

不测试 SQL。

---

# 第十八章 Repository + Service Checklist

## Repository

- [ ] BaseRepository
- [ ] UserRepository
- [ ] CourseRepository
- [ ] LearningRepository
- [ ] KnowledgeRepository
- [ ] AIRepository
- [ ] GrowthRepository

## Service

- [ ] AuthService
- [ ] CourseService
- [ ] HomeworkService
- [ ] QuizService
- [ ] KnowledgeService
- [ ] AIService
- [ ] GrowthService

## Transaction

- [ ] 注册事务
- [ ] 作业事务
- [ ] 测验事务
- [ ] Mirror 更新事务

## Query

- [ ] 分页
- [ ] 排序
- [ ] 条件过滤
- [ ] 搜索

---

# 第十九章 本章开发成果

完成 Part04 后，ProgramMind Backend 将建立完整的数据访问规范：

- Repository 负责所有数据库 CRUD。
- Service 负责全部业务流程。
- SQLAlchemy Transaction 统一管理。
- Learning Mirror 更新链路固定。
- Recommendation、Timeline、Risk 自动联动。
- Backend 开发成员可直接按照 Repository + Service 模式开发全部接口。
