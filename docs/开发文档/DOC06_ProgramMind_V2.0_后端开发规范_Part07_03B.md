# ProgramMind V2.0 后端开发规范

# Part07.3B —— Recommendation Engine（智能推荐与学习干预引擎）

> 文档版本：V2.0
> 更新时间：2026-09
> 模块负责人：AI（Recommendation Engine）
> 技术栈：FastAPI + SQLAlchemy + LangGraph + Redis + NumPy

---

# 第一章 Recommendation Engine 模块定位

## 1.1 模块职责

Recommendation Engine 是 Learning Mirror Engine 的智能干预模块。

它根据学生当前学习状态，生成个性化学习建议，而不是简单推荐课程。

主要职责：

- 知识点推荐。
- 今日复习任务。
- 实验推荐。
- 测验推荐。
- AI Tutor 学习任务推荐。
- 教师干预建议。
- 学习提醒。
- 学习激励。

形成预测后的主动干预。

---

## 1.2 Recommendation 在系统中的位置

Learning Mirror

↓

Knowledge Mastery

↓

Risk Prediction

↓

Recommendation Strategy Engine

↓

Recommendation Repository

↓

Student Dashboard / AI Tutor / Teacher Dashboard

---

## 1.3 Recommendation 原则

ProgramMind 推荐遵循四项原则：

- 个性化（基于学生状态）。
- 可解释（说明推荐原因）。
- 可执行（明确学习任务）。
- 可追踪（完成状态可记录）。

---

# 第二章 Recommendation Engine 总体架构

## 2.1 Engine 模块目录

growth/recommendation/

recommendation_engine.py

strategy_engine.py

review_strategy.py

knowledge_strategy.py

quiz_strategy.py

experiment_strategy.py

intervention_engine.py

recommendation_scheduler.py

recommendation_repository.py

---

## 2.2 生命周期

Learning Mirror 更新

↓

Risk Prediction 更新

↓

Strategy Engine

↓

Recommendation Generator

↓

Recommendation Repository

↓

Timeline Event

↓

Dashboard / AI Tutor 展示

---

## 2.3 Recommendation 分类

| 类型                        | 用途       |
| ------------------------- | -------- |
| Knowledge Review          | 知识点复习    |
| Quiz Recommendation       | 推荐测验     |
| Experiment Recommendation | 推荐实验     |
| Course Recommendation     | 推荐课程资源   |
| AI Tutor Session          | 推荐 AI 学习 |
| Intervention Reminder     | 学习提醒     |
| Motivation Recommendation | 学习激励     |

---

# 第三章 Recommendation 数据模型

## 3.1 RecommendationRecord

数据库：

recommendation_records。

一条记录代表：

一条推荐任务。

---

## 3.2 RecommendationSchema

字段：

| 字段                  | 含义     |
| ------------------- | ------ |
| recommendation_id   | UUID   |
| student_id          | 学生     |
| course_id           | 课程     |
| recommendation_type | 推荐类型   |
| priority            | 优先级    |
| title               | 标题     |
| description         | 描述     |
| reason              | 推荐原因   |
| estimated_minutes   | 建议学习时间 |
| status              | 状态     |

---

## 3.3 Recommendation JSON

```json
{
 "title":"复习链表基础操作",
 "priority":"high",
 "reason":"链表掌握度下降至0.38",
 "estimated_minutes":30
}
```

---

# 第四章 Strategy Engine（核心）

## 4.1 Strategy Engine 定位

负责决定：

推荐什么。

推荐多少。

推荐顺序。

---

## 4.2 Strategy 输入

Learning Mirror。

Knowledge Mastery。

Risk Prediction。

Timeline。

课程配置。

考试日期（预留）。

---

## 4.3 Strategy 输出

Recommendation List。

Priority。

Reason。

Deadline（可选）。

---

# 第五章 Knowledge Recommendation Strategy

## 5.1 推荐目标

自动推荐需要优先学习的知识点。

来源：

Weak Knowledge Detection。

---

## 5.2 输入

Weak Knowledge。

Forget Curve。

Risk。

Confidence。

---

## 5.3 推荐规则

优先：

掌握度低。

遗忘严重。

课程当前章节。

考试范围（预留）。

---

## 5.4 输出字段

知识点。

原因。

建议学习方式。

建议学习时长。

推荐资源。

---

# 第六章 Review Recommendation Strategy

## 6.1 今日复习计划

每天自动生成。

默认数量：

3~5 个知识点。

---

## 6.2 本周复习计划

根据：

Review Queue。

Risk。

课程安排。

生成一周计划。

---

## 6.3 考试周模式（预留）

考试日期前：

自动提高 Review Priority。

减少新知识推荐。

---

# 第七章 Quiz Recommendation Strategy

## 7.1 推荐测验目标

巩固薄弱知识。

不是随机出题。

---

## 7.2 推荐依据

Knowledge Mastery。

章节掌握度。

Trend。

Risk。

---

## 7.3 Quiz 类型

章节 Quiz。

专项 Quiz。

综合 Quiz。

AI 自适应 Quiz。

---

## 7.4 输出 JSON

```json
{
 "quiz_type":"chapter",
 "chapter":"链表",
 "difficulty":"medium"
}
```

---

# 第八章 Experiment Recommendation Strategy

## 8.1 推荐实验目标

Practice Score 提升。

---

## 8.2 推荐依据

Practice Score。

实验完成率。

课程章节。

掌握度。

---

## 8.3 推荐内容

实验。

项目练习。

代码练习。

Debug 练习。

AI Tutor Coding Session。

---

# 第九章 AI Tutor Session Recommendation

## 9.1 AI Tutor 推荐目标

主动引导学生学习。

---

## 9.2 推荐场景

连续三天未学习。

Risk 提高。

掌握度下降。

课程开始新章节。

---

## 9.3 Session 类型

AI Tutor。

AI Quiz。

AI Review。

AI Coding Practice。

---

## 9.4 Session JSON

```json
{
 "session_type":"review",
 "title":"AI带你复习链表"
}
```

---

# 第十章 Course Resource Recommendation

## 10.1 推荐资源来源

Knowledge Base。

教师资料。

教材。

实验指导书。

AI Tutor 文档。

---

## 10.2 推荐规则

知识点关联。

章节关联。

课程关联。

优先教师资源。

---

## 10.3 输出内容

教材章节。

实验文档。

PDF。

Markdown。

视频（预留）。

---

# 第十一章 Intervention Engine（智能干预）

## 11.1 模块定位

Recommendation 不只是展示。

Intervention Engine 负责主动干预。

---

## 11.2 干预类型

| 类型             | 描述     |
| -------------- | ------ |
| Reminder       | 学习提醒   |
| Warning        | 风险提醒   |
| Motivation     | 激励提醒   |
| Recovery       | 恢复学习提醒 |
| Teacher Notify | 教师建议   |

---

## 11.3 Intervention Trigger

Risk 提高。

连续未学习。

Recommendation 未完成。

课程截止日期临近。

自动生成事件。

---

# 第十二章 Timeline Intervention Engine

## 12.1 Timeline Event

Timeline 保存 AI 干预事件。

例如：

今日复习。

完成推荐。

连续学习。

风险提醒。

---

## 12.2 Event 类型

review_task。

quiz_task。

experiment_task。

achievement。

warning。

recommendation_completed。

---

## 12.3 Timeline JSON

```json
{
 "event":"review_task",
 "title":"今日复习链表",
 "status":"pending"
}
```

---

# 第十三章 Recommendation Scheduler

## 13.1 Scheduler 定位

每天自动刷新推荐。

凌晨执行。

---

## 13.2 Scheduler 输出

今日推荐。

本周推荐。

课程推荐。

实验推荐。

Quiz 推荐。

---

## 13.3 Trigger

Scheduler。

Mirror Refresh。

Risk Refresh。

考试模式。

均可触发。

---

# 第十四章 Recommendation Priority Engine

## 14.1 Priority 定义

推荐优先级。

---

## 14.2 Priority 等级

| 等级     | 条件                       |
| ------ | ------------------------ |
| High   | High Risk、Weak Knowledge |
| Medium | Forget Risk              |
| Low    | 兴趣拓展                     |

---

## 14.3 排序规则

Risk。

Mastery。

Deadline。

Difficulty。

Review Count。

综合排序。

---

# 第十五章 Recommendation 生命周期

## 生命周期

Generate。

↓

Pending。

↓

Student Start。

↓

Completed。

↓

Mirror Update。

↓

Recommendation Archive。

---

## 状态定义

pending。

started。

completed。

ignored。

expired。

数据库 recommendation_records 保存。

---

# 第十六章 Student Dashboard 推荐中心

## Dashboard 模块

今日推荐。

继续学习。

高优先任务。

AI Tutor 推荐。

课程资源推荐。

实验推荐。

Quiz 推荐。

---

## 今日推荐 JSON

包含：

标题。

优先级。

学习时间。

原因。

按钮。

---

# 第十七章 Teacher Intervention Recommendation

## 教师端建议

教师看到：

高风险学生。

推荐联系学生。

推荐布置实验。

推荐补充资料。

推荐课堂关注。

---

## Teacher Recommendation JSON

```json
{
 "student":"张三",
 "reason":"连续5天未学习",
 "action":"建议布置链表专项练习"
}
```

---

# 第十八章 Recommendation Repository 与 Service

## Repository

方法：

get_today_recommendations()

save_recommendation()

update_status()

archive_recommendation()

---

## Service

generate_recommendations()

refresh_today()

complete_recommendation()

trigger_intervention()

---

# 第十九章 Recommendation Engine Checklist

## Strategy

- [ ] Knowledge Recommendation
- [ ] Review Recommendation
- [ ] Quiz Recommendation
- [ ] Experiment Recommendation
- [ ] Course Recommendation

## Intervention

- [ ] Reminder
- [ ] Warning
- [ ] Motivation
- [ ] Recovery
- [ ] Teacher Notify

## Scheduler

- [ ] Daily Scheduler
- [ ] Weekly Scheduler
- [ ] Exam Scheduler

## Dashboard

- [ ] Student Recommendation Center
- [ ] Teacher Recommendation Center
- [ ] Timeline Event

---

# 第二十章 本章开发成果

完成 Part07.3B 后，ProgramMind Recommendation Engine 将具备：

- 个性化知识推荐。
- 今日/本周复习计划。
- Quiz 与实验推荐。
- AI Tutor Session 推荐。
- Timeline 干预事件生成。
- Teacher Intervention 建议。
- Recommendation 生命周期管理。
- 与 Learning Mirror、Risk Prediction、Dashboard 完整联动。
