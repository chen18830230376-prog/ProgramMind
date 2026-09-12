# ProgramMind V2.0 数据库设计说明书（DDS）

# Part 07 —— Learning Profile 数据库设计（学习状态镜像 / 学情画像 / 推荐系统）

> 面向开发成员：Backend负责人、AI负责人、Frontend成长模块负责人
> 
> 技术栈：MySQL 8.0 + SQLAlchemy 2.x

---

# 第七十二章 Learning Profile 总体设计

## 72.1 模块定位

Learning Profile（学习画像）是 ProgramMind 的核心创新模块。

它负责持续记录学生学习行为，并生成可解释、可追踪、可干预的学习状态镜像。

ProgramMind 不使用“认知数字孪生”作为技术表达，而使用：

> **Learning State Mirror（学习状态镜像）**

所有成长分析、AI推荐、知识掌握、学习预测，都来自这里。

---

## 72.2 模块职责

负责维护：

- 学习行为流水
- 知识点掌握度
- 学习画像
- 成长时间轴
- 学习热力图
- AI推荐历史

形成完整学习数据闭环。

---

## 72.3 数据流关系图

```text
Homework
Quiz
Experiment
AI Tutor
Course Learning
Video Learning
Reading Material

        │
        ▼

Learning Records

        │
        ▼

Mastery Engine

        │
        ▼

Growth Profile

        │
        ▼

Recommendation Engine
```

所有行为最终更新画像。

---

## 72.4 数据表清单

| 表名                     | 描述     |
| ---------------------- | ------ |
| learning_records       | 学习行为流水 |
| mastery_records        | 知识掌握度  |
| growth_profiles        | 学习画像   |
| growth_timeline        | 成长轨迹   |
| study_heatmaps         | 学习热力图  |
| recommendation_records | AI推荐历史 |

共 **6 张核心表**。

---

# 第七十三章 learning_records（学习行为流水）

## 73.1 表定位

ProgramMind 最重要的数据表。

所有学习行为都写这里。

永不覆盖。

只追加。

---

## 73.2 支持行为

| 行为   | 来源           |
| ---- | ------------ |
| 学习课程 | Learn Course |
| 查看教材 | Material     |
| AI问答 | Tutor Agent  |
| 提交作业 | Homework     |
| 完成实验 | Experiment   |
| 完成测验 | Quiz         |
| 收藏资源 | Favorite     |
| 下载教材 | Resource     |

所有行为统一事件流。

---

## 73.3 字段设计

| 字段               | 类型           | 描述                      |
| ---------------- | ------------ | ----------------------- |
| id               | CHAR(36)     | UUID                    |
| user_id          | CHAR(36)     | FK users                |
| course_id        | CHAR(36)     | FK courses              |
| chapter_id       | CHAR(36)     | FK chapters             |
| knowledge_point  | VARCHAR(150) | 知识点                     |
| activity_type    | ENUM         | study/homework/quiz/... |
| activity_name    | VARCHAR(200) | 行为名称                    |
| duration_minutes | INT          | 学习时长                    |
| score            | DECIMAL(5,2) | 分数，可空                   |
| completion_rate  | DECIMAL(5,2) | 完成率                     |
| metadata         | JSON         | 行为附加信息                  |
| created_at       | DATETIME     | 行为时间                    |

---

## 73.4 activity_type 枚举

| 类型         | 描述   |
| ---------- | ---- |
| study      | 学习课程 |
| homework   | 作业   |
| experiment | 实验   |
| quiz       | 测验   |
| tutor      | AI辅导 |
| material   | 阅读资料 |
| resource   | 下载资源 |
| favorite   | 收藏   |
| login      | 登录   |
| review     | AI复习 |

统一事件类型。

---

## 73.5 metadata 示例

```json
{
  "quiz_id":"uuid",
  "correct_rate":0.85,
  "device":"web"
}
```

支持扩展。

---

## 73.6 API

| API                          | 功能    |
| ---------------------------- | ----- |
| POST /learning/record        | 写行为   |
| GET /learning/history        | 行为历史  |
| GET /learning/history/course | 某课程行为 |

所有页面调用这里。

---

## 73.7 索引设计

| 索引                   | 字段              |
| -------------------- | --------------- |
| idx_record_user      | user_id         |
| idx_record_course    | course_id       |
| idx_record_activity  | activity_type   |
| idx_record_time      | created_at      |
| idx_record_knowledge | knowledge_point |

支持学情统计。

---

# 第七十四章 mastery_records（知识掌握度）

## 74.1 表定位

ProgramMind Learning State Mirror 核心指标。

记录学生每个知识点掌握程度。

替换 Demo MASTERY JSON。

---

## 74.2 一条记录表示什么？

一个学生。

一个课程。

一个知识点。

当前掌握值。

---

## 74.3 字段设计

| 字段              | 类型           | 描述                |
| --------------- | ------------ | ----------------- |
| id              | CHAR(36)     | UUID              |
| user_id         | CHAR(36)     | FK users          |
| course_id       | CHAR(36)     | FK courses        |
| chapter_id      | CHAR(36)     | FK chapters       |
| knowledge_point | VARCHAR(150) | 知识点               |
| mastery_score   | DECIMAL(5,2) | 掌握值0-100          |
| confidence      | DECIMAL(5,2) | 数据可信度             |
| evidence_count  | INT          | 更新次数              |
| last_source     | ENUM         | homework/quiz/... |
| last_updated_at | DATETIME     | 更新时间              |
| created_at      | DATETIME     | 创建时间              |

---

## 74.4 mastery_score 定义

| 分数     | 状态   |
| ------ | ---- |
| 90-100 | 熟练掌握 |
| 75-89  | 基本掌握 |
| 60-74  | 初步掌握 |
| 40-59  | 薄弱   |
| 0-39   | 未掌握  |

成长模块统一颜色。

---

## 74.5 更新规则（保持 Demo 思路）

ProgramMind 保留 Demo 的平滑更新。

公式：

```
新掌握度 =
旧掌握度 × 0.7 +
当前成绩 × 0.3
```

不同来源权重不同。

---

## 74.6 来源权重

| 来源         | 权重   |
| ---------- | ---- |
| Quiz       | 0.35 |
| Homework   | 0.30 |
| Experiment | 0.25 |
| Tutor Quiz | 0.20 |
| Material   | 0.10 |

Mastery Engine 自动计算。

---

## 74.7 API

| API                   | 功能     |
| --------------------- | ------ |
| GET /mastery          | 我的掌握度  |
| GET /mastery/course   | 某课程掌握度 |
| PATCH /mastery/update | AI更新   |

---

## 74.8 索引

| 索引                 | 字段              |
| ------------------ | --------------- |
| idx_mastery_user   | user_id         |
| idx_mastery_course | course_id       |
| idx_mastery_point  | knowledge_point |

支持雷达图。

---

# 第七十五章 growth_profiles（学习画像）

## 75.1 表定位

每个学生一张画像。

不是流水。

是聚合指标。

---

## 75.2 字段设计

| 字段                      | 类型           | 描述            |
| ----------------------- | ------------ | ------------- |
| user_id                 | CHAR(36)     | PK            |
| learning_hours          | DECIMAL(6,1) | 总学习时长         |
| courses_completed       | INT          | 完成课程数         |
| homework_completed      | INT          | 完成作业数         |
| experiments_completed   | INT          | 完成实验数         |
| quizzes_completed       | INT          | 完成测验数         |
| avg_score               | DECIMAL(5,2) | 平均成绩          |
| mastery_average         | DECIMAL(5,2) | 平均掌握度         |
| streak_days             | INT          | 连续学习          |
| active_days             | INT          | 活跃天数          |
| strongest_topic         | VARCHAR(100) | 优势知识点         |
| weakest_topic           | VARCHAR(100) | 薄弱知识点         |
| preferred_learning_time | VARCHAR(20)  | morning/night |
| updated_at              | DATETIME     | 更新时间          |

---

## 75.3 画像来源

聚合：

Learning Records。

Mastery。

Homework。

Quiz。

Experiment。

每天刷新。

---

## 75.4 Growth Card 指标

前端成长页展示：

累计学习时间。

连续学习。

课程完成。

平均掌握度。

平均成绩。

优势能力。

待提升能力。

---

## 75.5 API

| API                  | 功能   |
| -------------------- | ---- |
| GET /growth/profile  | 获取画像 |
| POST /growth/rebuild | 重建画像 |

---

# 第七十六章 growth_timeline（成长轨迹）

## 76.1 表定位

成长时间轴。

支持展示学习历程。

---

## 76.2 字段设计

| 字段          | 类型           | 描述                |
| ----------- | ------------ | ----------------- |
| id          | CHAR(36)     | UUID              |
| user_id     | CHAR(36)     | FK users          |
| event_type  | ENUM         | quiz/homework/... |
| title       | VARCHAR(200) | 标题                |
| description | TEXT         | 描述                |
| course_id   | CHAR(36)     | FK courses        |
| score       | DECIMAL(5,2) | 成绩                |
| created_at  | DATETIME     | 时间                |

---

## 76.3 示例事件

```text
完成《Python第一次实验》

测验《链表基础》92分

连续学习7天

掌握度突破80%
```

Timeline 页面展示。

---

## 76.4 API

| API                  | 功能  |
| -------------------- | --- |
| GET /growth/timeline | 时间轴 |
| POST /growth/event   | 新事件 |

自动写入。

---

# 第七十七章 study_heatmaps（学习热力图）

## 77.1 表定位

真实学习热力图。

替换 Demo 随机热力图。

---

## 77.2 字段设计

| 字段               | 类型       | 描述       |
| ---------------- | -------- | -------- |
| id               | CHAR(36) | UUID     |
| user_id          | CHAR(36) | FK users |
| study_date       | DATE     | 日期       |
| total_minutes    | INT      | 学习分钟     |
| session_count    | INT      | 学习次数     |
| quiz_count       | INT      | 测验次数     |
| homework_count   | INT      | 作业次数     |
| experiment_count | INT      | 实验次数     |
| created_at       | DATETIME | 时间       |

---

## 77.3 聚合来源

每天凌晨聚合：

Learning Records。

更新 HeatMap。

不是随机。

---

## 77.4 前端颜色映射

| 时长     | 等级     |
| ------ | ------ |
| 0      | 空白     |
| 1-30   | Level1 |
| 31-60  | Level2 |
| 61-120 | Level3 |
| 120+   | Level4 |

GitHub 风格热力图。

---

## 77.5 API

| API                 | 功能    |
| ------------------- | ----- |
| GET /growth/heatmap | 获取热力图 |

支持年度。

支持课程过滤。

---

# 第七十八章 recommendation_records（AI推荐历史）

## 78.1 表定位

记录 AI 给学生推荐了什么。

方便解释推荐。

支持反馈。

---

## 78.2 字段设计

| 字段                  | 类型       | 描述                          |
| ------------------- | -------- | --------------------------- |
| id                  | CHAR(36) | UUID                        |
| user_id             | CHAR(36) | FK users                    |
| recommendation_type | ENUM     | course/review/quiz/resource |
| target_id           | CHAR(36) | 推荐对象                        |
| reason              | TEXT     | 推荐原因                        |
| accepted            | BOOLEAN  | 是否采纳                        |
| clicked_at          | DATETIME | 点击时间                        |
| created_at          | DATETIME | 推荐时间                        |

---

## 78.3 推荐类型

| 类型       | 描述   |
| -------- | ---- |
| course   | 推荐课程 |
| review   | 推荐复习 |
| quiz     | 推荐测验 |
| resource | 推荐资料 |

---

## 78.4 推荐来源

Recommendation Agent。

Analytics Agent。

Tutor Agent。

---

## 78.5 API

| API                            | 功能   |
| ------------------------------ | ---- |
| GET /recommendations           | 推荐列表 |
| POST /recommendations/feedback | 推荐反馈 |

支持学习推荐解释。

---

# 第七十九章 Learning State Mirror 聚合流程

## 79.1 数据更新流程

```mermaid
flowchart TD

LearningRecord

Homework

Quiz

Experiment

Tutor

↓

MasteryEngine

↓

GrowthProfileService

↓

HeatMapService

↓

RecommendationEngine
```

所有学习行为最终进入画像。

---

## 79.2 每日聚合任务

每天凌晨：

统计学习时间。

统计掌握度变化。

统计课程完成。

生成热力图。

刷新推荐。

---

## 79.3 实时更新事件

以下实时更新：

- Quiz完成。
- Homework批改。
- Experiment评分。
- Tutor完成学习任务。

更新 Mastery。

---

# 第八十章 Repository 设计（Learning Profile）

## LearningRecordRepository

方法：

append()

history()

course_history()

---

## MasteryRepository

方法：

update_mastery()

course_mastery()

knowledge_mastery()

---

## GrowthRepository

方法：

rebuild_profile()

timeline()

heatmap()

---

## RecommendationRepository

方法：

save()

history()

feedback()

---

# 第八十一章 Service 设计（Learning Profile）

## LearningRecordService

负责：

记录行为。

学习时长统计。

事件聚合。

---

## MasteryEngine

负责：

掌握度更新。

知识点计算。

平滑算法。

可信度。

---

## GrowthProfileService

负责：

生成画像。

雷达图。

成长卡片。

优势薄弱点。

---

## HeatMapService

负责：

学习热力图。

学习日历。

年度统计。

---

## RecommendationService

负责：

课程推荐。

资料推荐。

复习推荐。

测验推荐。

解释推荐原因。

---

# 第八十二章 前端模块映射

## Growth 页面

对应：

growth_profiles。

study_heatmaps。

growth_timeline。

mastery_records。

---

## Analytics 页面

教师查看：

学生画像。

班级画像。

课程画像。

知识点画像。

---

## AI Review 页面

读取：

mastery_records。

recommendation_records。

自动生成复习路径。

---

# 第八十三章 Demo 数据迁移方案

## Demo LEARNING_RECORDS

迁移：

learning_records。

---

## Demo MASTERY

迁移：

mastery_records。

保留更新算法。

---

## Demo GROWTH

拆分：

growth_profiles。

growth_timeline。

study_heatmaps。

recommendation_records。

不再使用随机数据。

---

# 第八十四章 全数据库最终 ER 图

```text
Users
 │
 ├── Courses
 │      ├── Chapters
 │      │      ├── Resources
 │      │      │      ├── KnowledgeDocuments
 │      │      │      │      ├── Chunks
 │      │      │      │      │      └── Embeddings
 │      │      │      │      └── Citations
 │      │      ├── Homework
 │      │      │      └── HomeworkSubmission
 │      │      ├── Experiment
 │      │      │      └── ExperimentSubmission
 │      │      └── Quiz
 │      │             ├── QuizQuestions
 │      │             └── QuizRecords
 │      │
 │      └── Enrollment
 │
 ├── LearningRecords
 │      ├── MasteryRecords
 │      ├── GrowthProfiles
 │      ├── GrowthTimeline
 │      └── StudyHeatMap
 │
 └── AIEngine
        ├── Conversations
        ├── Messages
        ├── AgentWorkflow
        ├── AgentTasks
        └── AgentMemory
```

共 **22 张核心数据库表**。

---

# 第八十五章 全数据库开发 Checklist

## 用户中心

- [ ] users
- [ ] teacher_profiles
- [ ] student_profiles
- [ ] majors
- [ ] enrollments

## 课程中心

- [ ] courses
- [ ] chapters
- [ ] course_resources

## 教学中心

- [ ] homework
- [ ] homework_submissions
- [ ] experiments
- [ ] experiment_submissions
- [ ] quizzes
- [ ] quiz_questions
- [ ] quiz_records

## RAG Knowledge Base

- [ ] knowledge_documents
- [ ] knowledge_chunks
- [ ] knowledge_embeddings
- [ ] knowledge_citations

## AI Engine

- [ ] ai_conversations
- [ ] ai_messages
- [ ] agent_workflows
- [ ] agent_tasks
- [ ] agent_memory

## Learning Profile

- [ ] learning_records
- [ ] mastery_records
- [ ] growth_profiles
- [ ] growth_timeline
- [ ] study_heatmaps
- [ ] recommendation_records

---

# 第八十六章 Backend 开发顺序（必须遵守）

## 第一阶段（Week1）

- [ ] users
- [ ] majors
- [ ] courses
- [ ] enrollments

## 第二阶段（Week2）

- [ ] chapters
- [ ] resources
- [ ] homework
- [ ] experiments

## 第三阶段（Week3）

- [ ] quizzes
- [ ] submissions
- [ ] learning_records

## 第四阶段（Week4）

- [ ] mastery_records
- [ ] growth_profiles
- [ ] heatmaps

## 第五阶段（Week5）

- [ ] knowledge_documents
- [ ] chunks
- [ ] embeddings

## 第六阶段（Week6）

- [ ] conversations
- [ ] messages
- [ ] workflows
- [ ] memory

完成后数据库进入 V2.0。

---

# 第八十七章 本文档交付成果

本文档完成后，ProgramMind 数据库设计全部完成。

最终数据库版本（V2.0）包括：

| 模块               | 数据表数量         |
| ---------------- | ------------- |
| 用户中心             | 5             |
| 课程中心             | 3             |
| 教学中心             | 7             |
| RAG知识库           | 4             |
| AI Engine        | 5             |
| Learning Profile | 6             |
| **合计**           | **30 张核心业务表** |

数据库能够完整支撑：

- 教师教学业务。
- 学生学习业务。
- RAG知识增强检索。
- Multi-Agent 工作流。
- 学习状态镜像。
- AI推荐系统。
- 学情分析。
- Challenge Cup 全部技术路线。

---

**DOC03《ProgramMind V2.0 数据库设计说明书》全部完成（Part01～Part07）。**
