# ProgramMind V2.0 API 接口设计说明书

# Part04 —— Learning Center 学习中心接口设计（Homework / Quiz / Experiment / Learning Record）

> 文档版本：V2.0
> 
> 面向成员：Backend + Frontend
> 
> 模块负责人：Backend（学习业务） + Frontend（学习页面）

---

# 第一章 模块说明

## 1.1 模块定位

Learning Center 是学生端核心业务模块。

负责：

- 我的课程学习
- 今日学习任务
- 作业管理
- 实验管理
- 测验中心
- AI 学习记录
- 学习行为埋点
- 学习进度统计

所有学习数据最终流向 Growth Center（成长画像）。

---

## 1.2 Backend 目录

```
backend/app/api/learning.py

backend/app/services/homework_service.py
backend/app/services/quiz_service.py
backend/app/services/experiment_service.py
backend/app/services/learning_record_service.py

backend/app/repositories/
```

---

## 1.3 Frontend 页面

```
frontend/src/views/learning/

TodayLearning.vue
Homework.vue
HomeworkDetail.vue
QuizCenter.vue
QuizPage.vue
ExperimentCenter.vue
ExperimentDetail.vue
LearningRecords.vue
LearningMaterials.vue
```

---

## 1.4 数据表

| 表名                     | 说明    |
| ---------------------- | ----- |
| homework_assignments   | 作业    |
| homework_submissions   | 作业提交  |
| quizzes                | 测验    |
| quiz_questions         | 题目    |
| quiz_submissions       | 测验记录  |
| experiments            | 实验    |
| experiment_submissions | 实验提交  |
| learning_records       | 学习行为  |
| mastery_records        | 知识掌握度 |

---

# 第二章 API 总览（25 个接口）

## Homework（7）

| API | Method | 描述     |
| --- | ------ | ------ |
| 301 | GET    | 我的作业列表 |
| 302 | GET    | 作业详情   |
| 303 | POST   | 提交作业   |
| 304 | PATCH  | 更新作业提交 |
| 305 | GET    | 我的提交记录 |
| 306 | POST   | 上传作业附件 |
| 307 | GET    | 下载作业附件 |

---

## Quiz（8）

| API | Method | 说明     |
| --- | ------ | ------ |
| 308 | GET    | 测验列表   |
| 309 | GET    | 测验详情   |
| 310 | GET    | 获取测验题目 |
| 311 | POST   | 提交测验   |
| 312 | GET    | 测验结果   |
| 313 | GET    | 测验历史   |
| 314 | POST   | 收藏错题   |
| 315 | GET    | 错题本    |

---

## Experiment（6）

| API | Method | 说明     |
| --- | ------ | ------ |
| 316 | GET    | 实验列表   |
| 317 | GET    | 实验详情   |
| 318 | POST   | 提交实验   |
| 319 | PATCH  | 更新实验   |
| 320 | POST   | 上传实验附件 |
| 321 | GET    | 实验历史   |

---

## Learning Record（4）

| API | Method | 说明     |
| --- | ------ | ------ |
| 322 | POST   | 记录学习行为 |
| 323 | GET    | 学习记录列表 |
| 324 | GET    | 今日学习任务 |
| 325 | GET    | 学习统计信息 |

---

# 第三章 Homework 接口设计

---

# API-301 获取我的作业列表

## URL

```
GET /api/learning/homeworks
```

登录学生。

---

## Query

| 参数        | 说明                    |
| --------- | --------------------- |
| course_id | 课程过滤                  |
| status    | todo/submitted/graded |
| page      | 分页                    |
| page_size | 分页                    |

---

## 返回

```json
{
  "code":0,
  "data":{
    "list":[
      {
        "id":"uuid",
        "title":"Python第一次作业",
        "course_name":"Python程序设计",
        "deadline":"2026-09-20",
        "status":"todo",
        "score":null,
        "teacher_name":"李老师"
      }
    ]
  }
}
```

---

## SQL

JOIN：

- homework_assignments
- courses
- users
- homework_submissions

---

## 页面

Homework.vue。

Workspace 今日待办。

---

# API-302 获取作业详情

## URL

```
GET /api/learning/homeworks/{homework_id}
```

---

## 返回

作业说明。

截止时间。

附件。

提交状态。

评分。

教师评语。

---

## 页面

HomeworkDetail.vue。

---

# API-303 提交作业

## URL

```
POST /api/learning/homeworks/{homework_id}/submit
```

---

## 请求

```json
{
  "content":"我的答案",
  "attachments":[
    "file_uuid"
  ]
}
```

---

## Backend

新增 submission。

记录提交时间。

创建通知。

更新 learning_records。

---

## 返回

submission_id。

status=submitted。

---

# API-304 更新作业提交

截止前允许重新提交。

```
PATCH /api/learning/homeworks/submissions/{submission_id}
```

---

更新：

content。

附件。

---

# API-305 获取我的作业提交记录

```
GET /api/learning/homeworks/submissions
```

分页。

课程过滤。

---

返回：

所有历史成绩。

教师评语。

时间线。

---

# API-306 上传作业附件

```
POST /api/learning/homeworks/upload
```

multipart/form-data。

---

支持：

PDF。

ZIP。

PY。

CPP。

DOCX。

PNG。

最大：

30MB。

---

返回 file_id。

---

# API-307 下载附件

```
GET /api/files/{file_id}
```

JWT 校验。

返回下载地址。

---

# 第四章 Quiz 接口设计

---

# API-308 获取测验列表

```
GET /api/learning/quizzes
```

---

返回：

课程。

状态。

截止时间。

是否完成。

得分。

---

# API-309 获取测验详情

```
GET /api/learning/quizzes/{quiz_id}
```

返回：

描述。

时间限制。

题量。

总分。

---

# API-310 获取测验题目

```
GET /api/learning/quizzes/{quiz_id}/questions
```

---

返回结构

```json
{
  "questions":[
    {
      "id":"uuid",
      "type":"single_choice",
      "title":"Python中list属于什么？",
      "options":[
        "集合",
        "列表",
        "元组",
        "字典"
      ]
    }
  ]
}
```

---

支持题型

| 类型              |
| --------------- |
| single_choice   |
| multiple_choice |
| judge           |
| blank           |
| code            |

---

# API-311 提交测验

```
POST /api/learning/quizzes/{quiz_id}/submit
```

---

请求

```json
{
  "answers":[
    {
      "question_id":"uuid",
      "answer":"B"
    }
  ]
}
```

---

Backend

自动判分。

更新 mastery。

写 quiz_submissions。

生成学习记录。

---

返回

score。

accuracy。

mastery_update。

---

# API-312 获取测验结果

```
GET /api/learning/quizzes/submissions/{submission_id}
```

返回：

每题答案。

正确答案。

解析。

掌握度变化。

---

# API-313 获取历史测验记录

```
GET /api/learning/quizzes/history
```

分页。

课程过滤。

时间过滤。

---

返回：

历史成绩趋势。

---

# API-314 收藏错题

```
POST /api/learning/wrongbook
```

请求：

question_id。

submission_id。

---

Backend：

wrong_questions。

---

# API-315 获取错题本

```
GET /api/learning/wrongbook
```

返回：

错题。

课程。

知识点。

错误次数。

掌握度。

---

# 第五章 Experiment 接口设计

---

# API-316 获取实验列表

```
GET /api/learning/experiments
```

---

返回：

实验名称。

课程。

截止时间。

状态。

得分。

---

# API-317 获取实验详情

```
GET /api/learning/experiments/{experiment_id}
```

---

返回：

实验要求。

评分标准。

附件。

实验指导。

---

# API-318 提交实验

```
POST /api/learning/experiments/{experiment_id}/submit
```

请求：

说明。

附件。

GitHub 地址（可选）。

---

Backend：

experiment_submissions。

通知教师。

学习记录。

---

# API-319 更新实验提交

```
PATCH /api/learning/experiments/submissions/{submission_id}
```

截止前允许更新。

---

# API-320 上传实验附件

```
POST /api/learning/experiments/upload
```

支持：

ZIP。

PDF。

MP4。

PY。

CPP。

最大：

100MB。

---

# API-321 获取实验历史

```
GET /api/learning/experiments/history
```

返回：

所有实验成绩。

教师评语。

---

# 第六章 Learning Record 接口设计

---

# API-322 记录学习行为

## URL

```
POST /api/learning/records
```

---

## 请求

```json
{
  "course_id":"uuid",
  "chapter_id":"uuid",
  "record_type":"watch_video",
  "duration":1200
}
```

---

## record_type

| 类型            |
| ------------- |
| watch_video   |
| read_material |
| quiz          |
| homework      |
| experiment    |
| ai_chat       |
| note          |

---

Backend：

learning_records。

更新学习时长。

更新成长画像。

---

# API-323 获取学习记录

```
GET /api/learning/records
```

分页。

课程过滤。

行为过滤。

日期过滤。

---

返回：

学习时间轴。

---

# API-324 获取今日学习任务

```
GET /api/learning/today
```

---

返回：

今日课程。

待完成作业。

实验。

测验。

AI 推荐。

---

Backend：

聚合查询。

按截止时间排序。

---

# API-325 获取学习统计

```
GET /api/learning/statistics
```

---

返回

```json
{
  "today_duration":95,
  "week_duration":520,
  "month_duration":1820,
  "completed_tasks":23,
  "completion_rate":81.5
}
```

---

页面：

TodayLearning.vue。

Learning Dashboard。

---

# 第七章 文件上传规范

统一上传接口。

| 类型         | 最大大小  |
| ---------- | ----- |
| Homework   | 30MB  |
| Experiment | 100MB |
| Image      | 10MB  |
| Video      | 200MB |

---

保存路径：

```
uploads/homework/

uploads/experiment/

uploads/images/
```

数据库仅保存 URL。

---

# 第八章 Pydantic Schema

## HomeworkSubmitRequest

content。

attachments。

---

## QuizSubmitRequest

answers。

time_used。

---

## ExperimentSubmitRequest

description。

attachments。

github_url。

---

## LearningRecordRequest

course_id。

chapter_id。

record_type。

duration。

---

# 第九章 Repository

HomeworkRepository。

QuizRepository。

ExperimentRepository。

LearningRecordRepository。

WrongBookRepository。

---

# 第十章 Service

HomeworkService。

QuizService。

ExperimentService。

LearningRecordService。

MasteryService。

---

# 第十一章 Frontend SDK

```
learning.ts

getHomeworkList()

getHomeworkDetail()

submitHomework()

updateHomework()

uploadHomework()

getQuizList()

getQuizDetail()

getQuizQuestions()

submitQuiz()

getQuizResult()

getQuizHistory()

favoriteWrongQuestion()

getWrongBook()

getExperimentList()

getExperimentDetail()

submitExperiment()

updateExperiment()

uploadExperiment()

getExperimentHistory()

createLearningRecord()

getLearningRecords()

getTodayTasks()

getLearningStatistics()
```

---

# 第十二章 Checklist

## Homework

- [ ] 作业列表
- [ ] 作业详情
- [ ] 作业提交
- [ ] 更新提交
- [ ] 上传附件
- [ ] 下载附件
- [ ] 我的提交记录

---

## Quiz

- [ ] 测验列表
- [ ] 测验详情
- [ ] 获取题目
- [ ] 提交测验
- [ ] 查看结果
- [ ] 历史记录
- [ ] 收藏错题
- [ ] 错题本

---

## Experiment

- [ ] 实验列表
- [ ] 实验详情
- [ ] 提交实验
- [ ] 更新实验
- [ ] 上传附件
- [ ] 实验历史

---

## Learning Record

- [ ] 学习行为记录
- [ ] 学习记录时间轴
- [ ] 今日学习任务
- [ ] 学习统计

---

## 本章输出成果

Learning Center 全部接口设计完成。

Backend 完成本章节后，可支撑：

- 学生学习中心全部页面。
- 作业/实验/测验完整闭环。
- 学习记录与成长画像数据来源。
- 错题本系统。
- 今日学习任务系统。

下一章节 **DOC04 Part05** 将进入教师端 **Teaching Center 接口设计**（约 22 个 API），包括发布课程、发布作业、实验批改、AI 学情分析等，是教师工作台全部接口。
