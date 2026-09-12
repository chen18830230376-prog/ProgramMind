# ProgramMind V2.0 数据库设计说明书

# Part04 —— Learning Domain（学习中心数据库设计）

> 文档版本：V2.0
> 更新时间：2026-09
> 模块负责人：Backend（数据库）+ AI（Learning Mirror）
> 对应模块：学习中心、教学中心、成长中心、AI评价

---

# 第一章 Learning Domain 模块说明

## 1.1 模块职责

Learning Domain 是 ProgramMind 的教学业务中心。

负责管理整个教学闭环：

学生学习课程

↓

教师发布作业 / 实验 / 测验

↓

学生提交内容

↓

教师批改

↓

更新 Learning Mirror

↓

AI 生成成长建议。

Learning Domain 是 Growth Center 的数据来源。

---

## 1.2 数据库结构（8张表）

| 表名                     | 功能     |
| ---------------------- | ------ |
| homework_assignments   | 作业     |
| homework_submissions   | 作业提交   |
| experiments            | 实验任务   |
| experiment_submissions | 实验提交   |
| quizzes                | 测验     |
| quiz_questions         | 测验题目   |
| quiz_records           | 测验记录   |
| learning_records       | 学习行为流水 |

ER 图：

users

↓

course_enrollments

↓

homework_assignments

↓

homework_submissions

↓

learning_records

↓

learning_mirror

实验、测验共享 learning_records。

---

# 第二章 homework_assignments（作业）

## 2.1 表定位

教师发布的课程作业。

支持：

- Markdown
- 富文本
- 图片
- 附件
- 截止时间

---

## 2.2 字段设计（完整版）

| 字段             | 类型           | 说明                        |
| -------------- | ------------ | ------------------------- |
| id             | UUID         | 主键                        |
| course_id      | UUID         | 所属课程                      |
| chapter_id     | UUID         | 所属章节                      |
| teacher_id     | UUID         | 发布教师                      |
| title          | VARCHAR(150) | 作业标题                      |
| description    | LONGTEXT     | Markdown 内容               |
| homework_type  | ENUM         | coding/report/upload/text |
| attachment_url | VARCHAR(255) | 附件                        |
| total_score    | INT          | 满分                        |
| due_time       | DATETIME     | 截止时间                      |
| publish_time   | DATETIME     | 发布时间                      |
| status         | ENUM         | draft/published/closed    |
| created_at     | DATETIME     | 创建时间                      |
| updated_at     | DATETIME     | 更新时间                      |

---

## 2.3 MySQL DDL

```sql
CREATE TABLE homework_assignments (

    id CHAR(36) PRIMARY KEY,

    course_id CHAR(36) NOT NULL,

    chapter_id CHAR(36),

    teacher_id CHAR(36) NOT NULL,

    title VARCHAR(150) NOT NULL,

    description LONGTEXT,

    homework_type ENUM(
        'coding',
        'report',
        'upload',
        'text'
    ),

    attachment_url VARCHAR(255),

    total_score INT DEFAULT 100,

    due_time DATETIME,

    publish_time DATETIME,

    status ENUM(
        'draft',
        'published',
        'closed'
    ) DEFAULT 'draft',

    created_at DATETIME(6),

    updated_at DATETIME(6),

    FOREIGN KEY(course_id) REFERENCES courses(id),

    FOREIGN KEY(chapter_id) REFERENCES course_chapters(id),

    FOREIGN KEY(teacher_id) REFERENCES users(id)
);
```

---

## 2.4 SQLAlchemy Model

```python
class HomeworkAssignment(Base, BaseModel):

    __tablename__="homework_assignments"

    course_id = mapped_column(ForeignKey("courses.id"))

    chapter_id = mapped_column(ForeignKey("course_chapters.id"))

    teacher_id = mapped_column(ForeignKey("users.id"))

    title = mapped_column(String(150))

    description = mapped_column(Text)

    homework_type = mapped_column(Enum(HomeworkType))

    total_score = mapped_column(Integer)

    due_time = mapped_column(DateTime)

    status = mapped_column(Enum(HomeworkStatus))

    submissions = relationship("HomeworkSubmission")
```

---

# 第三章 homework_submissions（作业提交）

## 3.1 表定位

学生提交记录。

一个学生一条提交记录。

支持重复提交。

保留历史版本。

---

## 3.2 字段设计

| 字段             | 类型           | 说明                       |
| -------------- | ------------ | ------------------------ |
| id             | UUID         | 主键                       |
| homework_id    | UUID         | FK 作业                    |
| student_id     | UUID         | FK 学生                    |
| submit_content | LONGTEXT     | Markdown                 |
| attachment_url | VARCHAR(255) | 文件                       |
| version        | INT          | 第几次提交                    |
| score          | DECIMAL(5,2) | 分数                       |
| feedback       | LONGTEXT     | 教师评语                     |
| ai_feedback    | LONGTEXT     | AI评语                     |
| status         | ENUM         | submitted/graded/revised |
| submitted_at   | DATETIME     | 提交时间                     |
| graded_at      | DATETIME     | 批改时间                     |

---

## 3.3 Repository

HomeworkRepository。

HomeworkSubmissionRepository。

支持：

create_submission()

grade_submission()

list_submissions()

latest_submission()

---

## 3.4 Learning Mirror 更新规则

教师评分完成后：

更新：

knowledge_mastery_records。

learning_records。

learning_mirror。

---

# 第四章 experiments（课程实验）

## 4.1 表定位

课程实验。

区别于作业：

实验强调实践。

支持实验报告。

支持图片上传。

支持代码文件。

---

## 4.2 字段设计

| 字段              | 类型           |
| --------------- | ------------ |
| id              | UUID         |
| course_id       | UUID         |
| chapter_id      | UUID         |
| teacher_id      | UUID         |
| title           | VARCHAR(150) |
| objective       | TEXT         |
| description     | LONGTEXT     |
| expected_result | LONGTEXT     |
| total_score     | INT          |
| due_time        | DATETIME     |
| status          | ENUM         |

---

## 4.3 实验类型

| 类型            |
| ------------- |
| programming   |
| report        |
| simulation    |
| hardware      |
| comprehensive |

ProgramMind AI 推荐实验依据实验类型。

---

# 第五章 experiment_submissions（实验提交）

## 字段设计

| 字段              | 类型           |
| --------------- | ------------ |
| id              | UUID         |
| experiment_id   | UUID         |
| student_id      | UUID         |
| report_markdown | LONGTEXT     |
| attachment_url  | VARCHAR(255) |
| screenshot_url  | VARCHAR(255) |
| code_repository | VARCHAR(255) |
| score           | DECIMAL      |
| feedback        | LONGTEXT     |
| ai_feedback     | LONGTEXT     |
| submitted_at    | DATETIME     |
| graded_at       | DATETIME     |

---

## AI Evaluation

AI Agent 可以评价：

实验规范。

代码风格。

实验报告完整性。

评价写 ai_feedback。

教师可修改。

---

# 第六章 quizzes（测验）

## 6.1 表定位

课程测验。

支持章节测验。

支持期末模拟。

支持 AI 自动命题。

---

## 字段设计

| 字段               | 类型       |
| ---------------- | -------- |
| id               | UUID     |
| course_id        | UUID     |
| chapter_id       | UUID     |
| teacher_id       | UUID     |
| title            | VARCHAR  |
| description      | TEXT     |
| duration_minutes | INT      |
| total_score      | INT      |
| publish_time     | DATETIME |
| due_time         | DATETIME |
| quiz_type        | ENUM     |
| status           | ENUM     |

---

## quiz_type

| 类型           |
| ------------ |
| chapter      |
| midterm      |
| final        |
| ai_generated |
| practice     |

---

# 第七章 quiz_questions（测验题目）

## 7.1 表定位

保存每一道题。

支持 AI 自动生成。

---

## 字段设计（完整版）

| 字段            | 类型       |
| ------------- | -------- |
| id            | UUID     |
| quiz_id       | UUID     |
| knowledge_id  | UUID     |
| question_type | ENUM     |
| title         | LONGTEXT |
| options       | JSON     |
| answer        | JSON     |
| explanation   | LONGTEXT |
| difficulty    | ENUM     |
| score         | INT      |
| sort_order    | INT      |

---

## question_type

| 类型           |
| ------------ |
| single       |
| multiple     |
| judge        |
| blank        |
| coding       |
| short_answer |

---

## options JSON

```json
[
 {"key":"A","value":"列表"},
 {"key":"B","value":"元组"}
]
```

---

# 第八章 quiz_records（测验记录）

## 字段设计

| 字段               | 类型       |
| ---------------- | -------- |
| id               | UUID     |
| quiz_id          | UUID     |
| student_id       | UUID     |
| score            | DECIMAL  |
| accuracy         | DECIMAL  |
| duration_seconds | INT      |
| answers          | JSON     |
| wrong_questions  | JSON     |
| submitted_at     | DATETIME |

---

## answers JSON

```json
[
 {
   "question_id":"uuid",
   "answer":"A",
   "correct":true
 }
]
```

---

## wrong_questions JSON

用于 AI 推荐。

记录错误知识点。

---

## Learning Mirror 更新

Quiz 提交完成：

更新掌握度。

更新 Recommendation。

更新 Timeline。

更新 Heatmap。

---

# 第九章 learning_records（学习行为流水）

## 9.1 表定位

ProgramMind 最重要的数据流水表。

所有行为都会写这里。

Growth Center 所有统计来自 learning_records。

---

## 9.2 字段设计（完整版）

| 字段               | 类型       |
| ---------------- | -------- |
| id               | UUID     |
| user_id          | UUID     |
| course_id        | UUID     |
| chapter_id       | UUID     |
| knowledge_id     | UUID     |
| event_type       | ENUM     |
| event_source     | ENUM     |
| duration_seconds | INT      |
| score            | DECIMAL  |
| payload          | JSON     |
| created_at       | DATETIME |

---

## 9.3 event_type

| 类型                |
| ----------------- |
| course_visit      |
| chapter_visit     |
| homework_submit   |
| experiment_submit |
| quiz_submit       |
| ai_chat           |
| ai_review         |
| material_read     |
| note_create       |
| favorite          |

---

## 9.4 event_source

| 来源      |
| ------- |
| web     |
| ai      |
| mobile  |
| teacher |

---

## payload 示例

```json
{
 "quiz_id":"uuid",
 "accuracy":0.92,
 "wrong":["链表","队列"]
}
```

---

## 为什么设计 payload

减少重复字段。

支持 AI Agent 写额外信息。

支持日志扩展。

---

# 第十章 Learning Record 数据流（核心）

学生学习：

进入课程

↓

learning_record(course_visit)

↓

AI问答

↓

learning_record(ai_chat)

↓

完成测验

↓

learning_record(quiz_submit)

↓

完成作业

↓

learning_record(homework_submit)

↓

Learning Mirror 更新。

---

# 第十一章 Learning Analytics 聚合规则

Analytics 不直接统计业务表。

全部聚合 learning_records。

例如：

学习时长。

课程访问次数。

AI 次数。

每日学习次数。

实验完成率。

全部 SQL 聚合。

---

## 示例 SQL

统计今日学习次数：

```sql
SELECT COUNT(*)

FROM learning_records

WHERE user_id=?

AND DATE(created_at)=CURDATE();
```

---

# 第十二章 SQLAlchemy Relationships

Course

↓

Homework

↓

HomeworkSubmission

Course

↓

Experiment

↓

ExperimentSubmission

Course

↓

Quiz

↓

QuizQuestion

↓

QuizRecord

User

↓

LearningRecord

全部建立 relationship。

---

# 第十三章 Repository 设计（Learning）

## HomeworkRepository

```
create_homework()

publish_homework()

close_homework()

list_homework()
```

---

## SubmissionRepository

```
submit()

resubmit()

grade()

latest()

history()
```

---

## QuizRepository

```
create_quiz()

publish_quiz()

get_questions()

submit_quiz()

statistics()
```

---

## LearningRecordRepository

```
record_event()

list_events()

get_today_records()

get_heatmap_records()

aggregate_duration()
```

---

# 第十四章 Service 设计（Learning）

HomeworkService。

ExperimentService。

QuizService。

LearningRecordService。

AnalyticsAggregatorService。

EvaluationService。

---

# 第十五章 索引设计（Learning Domain）

| 表                      | 索引                   |
| ---------------------- | -------------------- |
| homework_submissions   | homework_id          |
| homework_submissions   | student_id           |
| experiments            | course_id            |
| experiment_submissions | experiment_id        |
| quiz_questions         | quiz_id              |
| quiz_records           | student_id + quiz_id |
| learning_records       | user_id + created_at |
| learning_records       | course_id            |
| learning_records       | knowledge_id         |

---

# 第十六章 Seed 初始化规范

Python课程：

初始化：

3份作业。

2个实验。

3个章节测验。

数据结构：

3份作业。

3个实验。

2个测验。

计网：

2份作业。

2个实验。

2个测验。

全部状态 published。

---

# 第十七章 Learning Domain Checklist

## Homework

- [ ] homework_assignments
- [ ] homework_submissions
- [ ] 多版本提交
- [ ] AI评价字段

## Experiment

- [ ] experiments
- [ ] experiment_submissions
- [ ] 图片上传
- [ ] Git仓库字段

## Quiz

- [ ] quizzes
- [ ] quiz_questions
- [ ] quiz_records
- [ ] AI命题支持

## Learning Records

- [ ] learning_records
- [ ] Event流水
- [ ] Analytics聚合
- [ ] Mirror消费

---

# 第十八章 本章开发成果

Learning Domain 完成后，ProgramMind V2.0 将具备：

- 作业发布与提交数据库。
- 实验发布与提交数据库。
- AI命题支持数据库。
- 测验记录数据库。
- 学习行为流水数据库。
- Learning Mirror、Analytics、Recommendation 的统一数据来源。
