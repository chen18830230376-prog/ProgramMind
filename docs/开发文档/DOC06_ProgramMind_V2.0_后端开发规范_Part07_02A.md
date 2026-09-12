# ProgramMind V2.0 后端开发规范

# Part07.2A —— Knowledge Mastery Engine（知识掌握算法引擎·上）

> 文档版本：V2.0
> 更新时间：2026-09
> 模块负责人：AI（Knowledge Mastery Engine）
> 技术栈：FastAPI + SQLAlchemy + NumPy + Redis

---

# 第一章 Knowledge Mastery Engine 模块定位

## 1.1 模块职责

Knowledge Mastery Engine 是 Learning Mirror Engine 的核心计算模块。

负责维护 **学生对于每一个知识点的掌握程度（Knowledge Mastery）**。

掌握度不是考试成绩，而是 AI 综合评估后的动态状态值。

输出给：

- Learning Mirror（Mastery 维度）
- AI Tutor
- Teacher Dashboard
- Recommendation Engine
- Risk Prediction Engine

---

## 1.2 Engine 数据流

Homework

Quiz

Experiment

AI Evaluation

Teacher Review

↓

Feature Extractor

↓

Mastery Calculator

↓

Confidence Calculator

↓

Forget Curve Calculator

↓

Knowledge Mastery Repository

↓

Mirror Builder

---

## 1.3 Mastery 生命周期

首次学习知识点

↓

初始化 Mastery

↓

测验更新

↓

实验更新

↓

AI评价更新

↓

遗忘曲线衰减

↓

推荐复习

↓

再次学习恢复 Mastery

形成动态循环。

---

# 第二章 Knowledge Mastery 数据模型

## 2.1 数据库来源

数据库：

knowledge_mastery_records。

一条记录代表：

**一个学生 × 一个知识点**。

---

## 2.2 数据对象（MasteryRecord）

字段：

| 字段                 | 含义      |
| ------------------ | ------- |
| student_id         | 学生      |
| knowledge_id       | 知识点     |
| mastery_score      | 当前掌握度   |
| confidence         | 置信度     |
| update_count       | 更新次数    |
| last_practice_time | 最近练习时间  |
| source             | 最近更新来源  |
| trend              | 上升/下降趋势 |

Mirror Engine 每次读取该对象。

---

## 2.3 KnowledgeMasteryState

AI 内部状态对象：

```json
{
  "knowledge_id":"python_list",
  "mastery_score":0.73,
  "confidence":0.82,
  "trend":"up",
  "forget_factor":0.94,
  "last_updated":"2026-09-01"
}
```

不是数据库对象。

用于计算。

---

# 第三章 Mastery Score 定义

## 3.1 Mastery Score 含义

Mastery Score 表示：

学生掌握某知识点的概率估计。

范围：

0~1。

---

## 3.2 Mastery 等级

| Score     | 等级             |
| --------- | -------------- |
| 0.90~1.00 | Fully Mastered |
| 0.75~0.89 | Proficient     |
| 0.60~0.74 | Developing     |
| 0.40~0.59 | Weak           |
| 0.00~0.39 | High Risk      |

Dashboard 使用颜色显示。

---

## 3.3 Mastery 初始化

首次出现知识点：

初始化：

0.5。

原因：

未知状态。

不是 0。

---

# 第四章 Mastery 更新来源（权重设计）

## 4.1 五类更新来源

| 来源             | 权重  |
| -------------- | --- |
| Quiz           | 40% |
| Homework       | 20% |
| Experiment     | 20% |
| AI Evaluation  | 10% |
| Teacher Review | 10% |

ProgramMind 默认权重。

后台可调整。

---

## 4.2 Quiz 更新

依据：

正确率。

题目难度。

完成时间。

章节覆盖率。

影响最大。

---

## 4.3 Homework 更新

依据：

得分。

重提交次数。

是否超时。

AI Feedback。

---

## 4.4 Experiment 更新

依据：

实验评分。

代码评分。

实验完成情况。

实践能力。

---

## 4.5 AI Evaluation 更新

AI 自动评价：

代码。

实验报告。

开放题。

生成掌握建议。

权重较低。

---

## 4.6 Teacher Review 更新

教师人工评价。

覆盖 AI。

用于最终修正。

---

# 第五章 Mastery Calculator（核心算法）

## 5.1 Calculator 输入

Feature：

score。

difficulty。

source。

confidence。

forget_factor。

last_mastery。

---

## 5.2 滑动更新策略

ProgramMind 使用指数滑动更新。

避免一次测验导致剧烈波动。

---

## 5.3 更新思想

旧掌握度保留历史。

新成绩部分融合。

学习越多越稳定。

---

## 5.4 更新参数

α（学习率）

默认：

0.3。

Quiz 可提高。

Teacher Review 可提高。

---

# 第六章 不同来源更新规则

## 6.1 Quiz 更新规则

影响最大。

根据：

正确率。

难度。

更新 Mastery。

---

## 6.2 Homework 更新规则

完成但错误较多。

Mastery 微升。

AI Feedback 影响 Confidence。

---

## 6.3 Experiment 更新规则

实践能力提升。

Practice 同时提升。

Mastery 增长较慢。

---

## 6.4 Teacher Override

教师评分。

可直接修正 Mastery。

记录来源 teacher_review。

---

# 第七章 Confidence（掌握置信度）模型

## 7.1 为什么需要 Confidence

Mastery 只是估计。

Confidence 衡量估计可信程度。

例如：

刚学一次：

Mastery=0.8。

Confidence=0.25。

不能认为真正掌握。

---

## 7.2 Confidence 来源

| 特征     | 来源                |
| ------ | ----------------- |
| 更新次数   | update_count      |
| 数据来源数量 | source diversity  |
| 时间跨度   | learning duration |
| 测验次数   | quiz count        |
| 实验次数   | experiment count  |

---

## 7.3 Confidence 范围

0~1。

越高表示掌握越稳定。

---

## 7.4 Confidence 更新策略

学习次数增加。

Confidence 增加。

长期未学习。

Confidence 下降。

---

# 第八章 Forgetting Curve（遗忘曲线模型）

## 8.1 为什么加入遗忘曲线

掌握不会永久保持。

ProgramMind 引入：

艾宾浩斯遗忘曲线。

模拟自然遗忘。

---

## 8.2 Forgetting 生命周期

学习

↓

记忆保持

↓

时间流逝

↓

掌握下降

↓

复习恢复

---

## 8.3 Forget Factor

Forget Factor：

0~1。

每日更新一次。

影响 Mastery。

---

## 8.4 数据来源

last_practice_time。

current_date。

knowledge_difficulty。

review_count。

---

# 第九章 艾宾浩斯遗忘模型设计（ProgramMind）

## 9.1 模型目标

不是严格心理学模型。

而是适用于教学系统。

强调：

- 可解释。
- 可调参数。
- 可恢复。

---

## 9.2 衰减阶段

| 时间   | 保留率（默认） |
| ---- | ------- |
| 第1天  | 0.95    |
| 第3天  | 0.90    |
| 第7天  | 0.82    |
| 第14天 | 0.72    |
| 第30天 | 0.60    |

参数可调整。

---

## 9.3 复习恢复

复习一次：

Forget Factor 提升。

Confidence 提升。

Mastery 恢复。

形成学习闭环。

---

# 第十章 Review Recovery Engine

## 10.1 Recovery 输入

Quiz。

Homework。

AI Tutor。

Experiment。

Review Session。

---

## 10.2 Recovery 输出

Mastery 增加。

Forget Factor 重置。

Confidence 增加。

Timeline 新事件。

---

## 10.3 Review 次数记录

review_count。

数据库保存。

影响 Forget Curve。

---

# 第十一章 Knowledge Difficulty 修正

## 11.1 为什么加入难度

困难知识点提升更慢。

遗忘更快。

推荐更多练习。

---

## 11.2 Difficulty 等级

| 等级       | 系数  |
| -------- | --- |
| Easy     | 0.8 |
| Medium   | 1.0 |
| Hard     | 1.2 |
| Advanced | 1.4 |

来自 knowledge_points.difficulty。

---

## 11.3 难度修正作用

Mastery 更新。

Forget Rate。

Recommendation Priority。

全部使用 Difficulty。

---

# 第十二章 Mastery Trend（趋势）

## 12.1 Trend 定义

连续多次更新。

计算趋势。

---

## 12.2 趋势分类

| Trend  | 条件   |
| ------ | ---- |
| up     | 连续增长 |
| stable | 波动很小 |
| down   | 连续下降 |

Dashboard 使用箭头。

---

## 12.3 Trend 保存

knowledge_mastery_records.trend。

Mirror 使用。

Recommendation 使用。

---

# 第十三章 Mastery 更新触发器

## 实时触发

Homework Grade。

Quiz Submit。

Experiment Grade。

Teacher Review。

AI Evaluation。

立即刷新。

---

## 定时触发

每天凌晨：

Forget Curve。

Confidence。

Trend。

Mirror Refresh。

Scheduler 执行。

---

# 第十四章 Repository 与 Service 联动

## MasteryService

update_mastery()

batch_update_mastery()

apply_forgetting_curve()

calculate_confidence()

get_course_mastery()

---

## Mirror 联动

Mastery 更新。

↓

Mirror Builder。

↓

Dashboard。

↓

Recommendation。

---

# 第十五章 Mastery Engine Checklist（上）

## Engine

- [ ] Feature Extractor
- [ ] Mastery Calculator
- [ ] Confidence Calculator
- [ ] Forget Curve
- [ ] Trend Calculator

## Trigger

- [ ] Homework
- [ ] Quiz
- [ ] Experiment
- [ ] AI Evaluation
- [ ] Teacher Review
- [ ] Daily Scheduler

---

# 第十六章 本章开发成果（上）

完成 Part07.2A 后，ProgramMind Knowledge Mastery Engine 已建立：

- Mastery 数据模型。
- Confidence 模型。
- Forgetting Curve 模型。
- 多来源掌握度更新机制。
- Trend 更新机制。
- 与 Learning Mirror 的联动入口。
