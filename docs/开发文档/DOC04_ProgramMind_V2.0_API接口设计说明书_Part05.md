# ProgramMind V2.0 API 接口设计说明书

# Part05 —— Teaching Center 教学中心接口设计（完整版）

> 文档版本：V2.0
> 
> 面向成员：Backend + Frontend
> 
> 模块负责人：教师端负责人（后端）+ 教师端页面负责人（Vue）

---

# 第一章 模块说明

## 1.1 模块定位

Teaching Center 是 ProgramMind 教师端核心模块。

教师围绕课程完成完整教学流程：

课程 → 教材 → 作业 → 实验 → 测验 → 批改 → 学情分析 → AI 总结。

所有接口仅教师（teacher）角色可访问。

---

## 1.2 Backend 目录

```
backend/app/api/teaching.py

backend/app/services/
    teaching_service.py
    homework_service.py
    experiment_service.py
    analytics_service.py
    grading_service.py
    quiz_service.py

backend/app/repositories/
    teaching_repository.py
```

---

## 1.3 Frontend 页面

```
frontend/src/views/teaching/

TeacherDashboard.vue
CourseManage.vue
HomeworkManage.vue
HomeworkGrade.vue
ExperimentManage.vue
ExperimentGrade.vue
QuestionBank.vue
KnowledgeGraph.vue
Analytics.vue
AISummary.vue
LessonPlan.vue
PPTGenerator.vue
```

---

## 1.4 数据表

| 表名                     | 说明   |
| ---------------------- | ---- |
| courses                | 教师课程 |
| homework_assignments   | 作业   |
| homework_submissions   | 学生提交 |
| experiments            | 实验   |
| experiment_submissions | 实验提交 |
| quizzes                | 测验   |
| quiz_questions         | 题库   |
| notifications          | 通知   |
| mastery_records        | 学情   |
| learning_records       | 学习行为 |

---

# 第二章 API 总览（22 个接口）

## Dashboard（3）

| API | Method | 描述      |
| --- | ------ | ------- |
| 401 | GET    | 教师工作台数据 |
| 402 | GET    | 教师课程统计  |
| 403 | GET    | 最近待处理任务 |

---

## Homework（6）

| API | Method | 描述     |
| --- | ------ | ------ |
| 404 | POST   | 发布作业   |
| 405 | PATCH  | 修改作业   |
| 406 | DELETE | 删除作业   |
| 407 | GET    | 作业提交列表 |
| 408 | GET    | 作业提交详情 |
| 409 | POST   | 批改作业   |

---

## Experiment（5）

| API | Method | 描述     |
| --- | ------ | ------ |
| 410 | POST   | 发布实验   |
| 411 | PATCH  | 修改实验   |
| 412 | DELETE | 删除实验   |
| 413 | GET    | 实验提交列表 |
| 414 | POST   | 批改实验   |

---

## Quiz（3）

| API | Method | 描述   |
| --- | ------ | ---- |
| 415 | POST   | 发布测验 |
| 416 | PATCH  | 修改测验 |
| 417 | DELETE | 删除测验 |

---

## Analytics（5）

| API | Method | 描述      |
| --- | ------ | ------- |
| 418 | GET    | 课程学情分析  |
| 419 | GET    | 知识点掌握度  |
| 420 | GET    | 学生个人画像  |
| 421 | GET    | 课程成绩统计  |
| 422 | POST   | AI 学情总结 |

---

# 第三章 Dashboard 接口

---

# API-401 获取教师工作台数据

## URL

```
GET /api/teaching/dashboard
```

---

## 返回结构

```json
{
  "code":0,
  "data":{
    "teacher":{
      "name":"李老师",
      "avatar":"..."
    },
    "overview":{
      "course_count":4,
      "student_count":132,
      "pending_homework":18,
      "pending_experiment":9,
      "today_classes":2
    }
  }
}
```

---

## Backend 聚合

统计：

- courses
- enrollments
- homework_submissions
- experiment_submissions

---

## 页面

TeacherDashboard.vue

---

# API-402 获取教师课程统计

```
GET /api/teaching/course-statistics
```

---

返回：

每门课人数。

平均成绩。

完成率。

活跃度。

---

用于 Dashboard 图表。

---

# API-403 获取最近待处理任务

```
GET /api/teaching/pending-tasks
```

返回：

待批改作业。

待批改实验。

即将截止测验。

课程提醒。

按时间排序。

---

# 第四章 Homework 教师接口

---

# API-404 发布作业

## URL

```
POST /api/teaching/homeworks
```

---

## 请求

```json
{
  "course_id":"uuid",
  "chapter_id":"uuid",
  "title":"Python第一次作业",
  "description":"完成列表相关练习",
  "deadline":"2026-09-20 23:59",
  "attachments":[
    "file_uuid"
  ]
}
```

---

## Backend 流程

创建作业。

↓

通知所有学生。

↓

创建学习任务。

↓

更新课程统计。

---

## 数据库

homework_assignments。

notifications。

learning_tasks。

---

## 页面

HomeworkManage.vue。

---

# API-405 修改作业

```
PATCH /api/teaching/homeworks/{homework_id}
```

允许修改：

标题。

截止时间。

附件。

描述。

---

# API-406 删除作业

```
DELETE /api/teaching/homeworks/{homework_id}
```

逻辑删除。

通知学生。

---

# API-407 获取作业提交列表

```
GET /api/teaching/homeworks/{homework_id}/submissions
```

---

## Query

分页。

状态。

关键词。

---

返回：

学生头像。

提交时间。

是否迟交。

状态。

得分。

---

## 页面

HomeworkGrade.vue。

---

# API-408 获取单个提交详情

```
GET /api/teaching/homeworks/submissions/{submission_id}
```

返回：

答案。

附件。

教师评语。

AI 检测结果。

---

# API-409 教师批改作业

```
POST /api/teaching/homeworks/submissions/{submission_id}/grade
```

---

## 请求

```json
{
  "score":92,
  "comment":"代码规范很好",
  "mastery_updates":[
    {
      "knowledge_point_id":"uuid",
      "delta":8
    }
  ]
}
```

---

## Backend 流程

写成绩。

↓

更新 mastery_records。

↓

生成通知。

↓

生成 learning_record。

---

# 第五章 Experiment 教师接口

---

# API-410 发布实验

```
POST /api/teaching/experiments
```

请求：

课程。

实验要求。

评分标准。

附件。

截止时间。

---

Backend：

experiments。

notifications。

---

# API-411 修改实验

```
PATCH /api/teaching/experiments/{experiment_id}
```

---

允许修改：

评分标准。

附件。

描述。

---

# API-412 删除实验

```
DELETE /api/teaching/experiments/{experiment_id}
```

逻辑删除。

---

# API-413 获取实验提交列表

```
GET /api/teaching/experiments/{experiment_id}/submissions
```

返回：

学生。

GitHub。

附件。

状态。

成绩。

---

# API-414 教师批改实验

```
POST /api/teaching/experiments/submissions/{submission_id}/grade
```

请求：

成绩。

评语。

能力评分。

---

能力评分包括：

代码规范。

实验完成度。

创新能力。

文档质量。

---

Backend：

更新 mastery。

更新成长画像。

通知学生。

---

# 第六章 Quiz 教师接口

---

# API-415 发布测验

```
POST /api/teaching/quizzes
```

请求：

课程。

章节。

题目。

截止时间。

时间限制。

总分。

---

Backend：

创建 quiz。

创建 question。

通知学生。

---

# API-416 修改测验

```
PATCH /api/teaching/quizzes/{quiz_id}
```

允许：

修改题目。

时间。

状态。

---

# API-417 删除测验

```
DELETE /api/teaching/quizzes/{quiz_id}
```

逻辑删除。

---

# 第七章 Analytics 学情分析接口

---

# API-418 获取课程学情分析

## URL

```
GET /api/teaching/analytics/{course_id}
```

---

## 返回

```json
{
  "overview":{
    "student_count":132,
    "avg_score":88.2,
    "completion_rate":84
  },
  "charts":{
    "score_distribution":[],
    "weekly_learning_time":[],
    "completion_trend":[]
  }
}
```

---

## 页面

Analytics.vue。

---

# API-419 获取知识点掌握度热力图

```
GET /api/teaching/analytics/{course_id}/mastery
```

---

返回二维矩阵。

学生 × 知识点。

数值：

0~100。

---

前端：

HeatMap。

Radar。

---

# API-420 获取学生画像

```
GET /api/teaching/students/{student_id}/profile
```

---

返回

成长趋势。

学习时长。

掌握度。

能力雷达图。

最近学习行为。

AI 总结。

---

页面：

点击学生进入画像。

---

# API-421 获取课程成绩统计

```
GET /api/teaching/analytics/{course_id}/scores
```

---

返回：

平均分。

最高分。

最低分。

优秀率。

及格率。

章节平均分。

---

页面：

课程统计。

ECharts。

---

# API-422 AI 学情总结

## URL

```
POST /api/teaching/analytics/{course_id}/ai-summary
```

---

## 请求

```json
{
  "summary_type":"weekly"
}
```

---

支持：

weekly。

chapter。

exam。

semester。

---

## Backend

调用 AI Engine。

输入：

Analytics 数据。

输出：

Markdown。

---

返回：

AI 总结。

风险学生。

建议。

教学建议。

---

# 第八章 AI 教学辅助接口（预留）

以下接口全部调用 AI Engine。

---

## AI 教案生成

```
POST /api/teaching/lesson-plan
```

输入：

课程。

章节。

课时。

输出 Markdown。

---

## AI PPT 大纲生成

```
POST /api/teaching/ppt-outline
```

输出：

PPT Page List。

---

## AI 命题生成

```
POST /api/teaching/question-generation
```

输入：

知识点。

难度。

题量。

输出：

Question JSON。

---

## AI 作业生成

```
POST /api/teaching/homework-generation
```

输入：

课程。

章节。

输出：

Homework Draft。

---

说明：

真正实现放在 DOC04 Part07 AI Engine。

这里教师端仅负责调用。

---

# 第九章 Pydantic Schema

## CreateHomeworkRequest

字段：

course_id。

chapter_id。

deadline。

attachments。

---

## GradeHomeworkRequest

score。

comment。

mastery_updates。

---

## CreateExperimentRequest

课程。

章节。

评分标准。

截止时间。

---

## GradeExperimentRequest

score。

comment。

ability_scores。

---

## CreateQuizRequest

课程。

章节。

题目数组。

时间限制。

---

# 第十章 Repository 设计

TeachingRepository。

HomeworkRepository。

ExperimentRepository。

QuizRepository。

AnalyticsRepository。

---

# 第十一章 Service 设计

TeachingService。

HomeworkService。

ExperimentService。

QuizService。

AnalyticsService。

GradingService。

---

# 第十二章 Frontend SDK

```
teaching.ts

getTeacherDashboard()

getCourseStatistics()

getPendingTasks()

publishHomework()

updateHomework()

deleteHomework()

getHomeworkSubmissions()

getHomeworkSubmissionDetail()

gradeHomework()

publishExperiment()

updateExperiment()

deleteExperiment()

getExperimentSubmissions()

gradeExperiment()

publishQuiz()

updateQuiz()

deleteQuiz()

getAnalytics()

getMasteryHeatmap()

getStudentProfile()

getCourseScores()

generateAISummary()
```

---

# 第十三章 Checklist

## Dashboard

- [ ] 教师首页
- [ ] 课程统计
- [ ] 待办任务

---

## Homework

- [ ] 发布作业
- [ ] 编辑作业
- [ ] 删除作业
- [ ] 提交列表
- [ ] 提交详情
- [ ] 批改作业

---

## Experiment

- [ ] 发布实验
- [ ] 编辑实验
- [ ] 删除实验
- [ ] 提交列表
- [ ] 批改实验

---

## Quiz

- [ ] 发布测验
- [ ] 编辑测验
- [ ] 删除测验

---

## Analytics

- [ ] 课程学情
- [ ] 热力图
- [ ] 学生画像
- [ ] 成绩统计
- [ ] AI 总结

---

## 本章输出成果

Teaching Center 接口设计完成。

Backend 完成本章节后，可支撑：

- 教师工作台。
- 作业发布与批改完整闭环。
- 实验发布与批改完整闭环。
- 测验发布系统。
- 学情分析页面。
- AI 学情总结页面。

下一章节进入 **DOC04 Part06 —— Knowledge Base（RAG 知识库接口设计）**，这是 ProgramMind V2.0 与 Demo 最大区别的一章，也是挑战杯核心技术模块。
