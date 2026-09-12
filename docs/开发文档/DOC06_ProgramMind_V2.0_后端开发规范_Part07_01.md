# ProgramMind V2.0 后端开发规范

# Part07.1 —— Learning State Mirror Engine 架构与状态建模（完整版）

> 文档版本：V2.0
> 更新时间：2026-09
> 模块负责人：AI（Learning Mirror Engine）
> 技术栈：FastAPI + SQLAlchemy + NumPy + LangGraph + ECharts

---

# 第一章 Learning State Mirror 模块定位

## 1.1 什么是 Learning State Mirror

Learning State Mirror（学习状态镜像）是 ProgramMind 的核心创新模块。

它不是“认知数字孪生”，而是学生学习状态的动态计算模型，用于持续描述学生当前学习能力与学习过程。

Mirror 是一个持续更新的数据对象，而不是静态画像。

---

## 1.2 Learning Mirror 在系统中的位置

学习行为数据

↓

Learning Records

↓

Knowledge Mastery Engine

↓

Learning State Mirror Engine

↓

Risk Prediction Engine

↓

Recommendation Engine

↓

Dashboard / AI Tutor / Teacher Dashboard

Mirror 是所有 AI Agent 的共同上下文来源。

---

## 1.3 Learning Mirror 的职责

Learning Mirror 负责：

- 学习状态建模
- 六维学习状态计算
- 学习画像生成
- 学习趋势计算
- AI Tutor 个性化上下文
- Risk Prediction 输入
- Recommendation 输入
- Dashboard 雷达图数据

---

# 第二章 Learning Mirror 总体架构（完整版）

## 2.1 Mirror Engine 架构图

```text
Homework Records
Quiz Records
Experiment Records
Learning Records
Conversation Records
AI Evaluation
Knowledge Mastery

        │
        ▼

Learning Feature Extractor

        │
        ▼

Mirror Builder

        │
        ▼

Six-Dimension State Vector

        │
        ▼

Mirror Repository

        │
        ▼

Growth Dashboard
AI Tutor
Teacher Dashboard
Recommendation
Risk Prediction
```

Mirror Engine 是 Growth Domain 的计算核心。

---

## 2.2 Engine 模块目录

```text
growth/

mirror/

mirror_engine.py

mirror_builder.py

state_vector.py

feature_extractor.py

score_calculator.py

mirror_repository.py

mirror_scheduler.py
```

Mirror 与 GrowthService 分离。

---

## 2.3 Engine 生命周期

新学习行为产生

↓

Feature Extractor

↓

State Calculator

↓

Mirror Builder

↓

Repository 更新

↓

Timeline 更新

↓

Recommendation 更新（可选）

---

# 第三章 Learning State 六维向量（核心）

## 3.1 六维状态定义

ProgramMind 定义六维学习状态向量：

S = [M,E,P,C,A,R]

其中：

| 缩写  | 名称                | 含义       |
| --- | ----------------- | -------- |
| M   | Knowledge Mastery | 知识掌握程度   |
| E   | Engagement        | 学习投入程度   |
| P   | Practice          | 实践能力     |
| C   | Consistency       | 学习连续性    |
| A   | AI Interaction    | AI学习互动程度 |
| R   | Risk              | 学习风险程度   |

所有指标范围：

0~1。

---

## 3.2 六维向量 JSON

```json
{
  "mastery":0.82,
  "engagement":0.75,
  "practice":0.68,
  "consistency":0.88,
  "ai_interaction":0.61,
  "risk":0.24
}
```

数据库 learning_mirror.mirror_vector 保存。

---

## 3.3 六维来源

| 指标             | 数据来源                         |
| -------------- | ---------------------------- |
| Mastery        | Quiz + Homework + Experiment |
| Engagement     | Learning Records             |
| Practice       | Experiment + Coding Homework |
| Consistency    | Timeline + Daily Records     |
| AI Interaction | AI Conversation              |
| Risk           | Prediction Engine            |

Mirror Builder 聚合这些特征。

---

# 第四章 Feature Extractor（特征提取）

## 4.1 Feature Extractor 定位

负责从数据库提取学习行为特征。

不做评分。

输出 Feature Vector。

---

## 4.2 Feature 分类

### 学习行为特征

学习时长。

登录频率。

学习次数。

课程完成率。

---

### 作业特征

提交率。

平均成绩。

平均延迟。

重提交次数。

---

### 测验特征

正确率。

章节正确率。

难题正确率。

完成时间。

---

### AI 特征

聊天次数。

Tutor 使用次数。

提问长度。

AI 推荐接受率。

---

## 4.3 输出 FeatureVector

字段：

study_hours_week

quiz_accuracy

experiment_count

ai_chat_count

completion_rate

active_days

所有特征进入 Score Calculator。

---

# 第五章 State Calculator（状态计算引擎）

## 5.1 State Calculator 职责

输入：

FeatureVector。

输出：

六维状态分数。

---

## 5.2 Score Calculator 模块

```text
score_calculator.py

mastery_score()

engagement_score()

practice_score()

consistency_score()

ai_score()

overall_score()
```

一个指标一个函数。

---

## 5.3 输出对象

StateVector。

MirrorScore。

OverallScore。

Trend。

---

# 第六章 Mastery Score（M）计算规范

## 6.1 Mastery 定义

知识掌握程度来自 Knowledge Mastery Engine。

不是直接测验分数。

---

## 6.2 数据来源

Quiz。

Homework。

Experiment。

AI Evaluation。

Teacher Review。

Knowledge Mastery。

---

## 6.3 Mastery 聚合公式

权重：

Quiz：40%

Homework：20%

Experiment：20%

AI Evaluation：10%

Teacher Review：10%

输出：

0~1。

---

## 6.4 更新策略

新的 Mastery。

采用滑动更新。

避免剧烈波动。

Mastery Engine 负责细节（Part07.2）。

---

# 第七章 Engagement Score（E）

## 7.1 Engagement 定义

学习投入程度。

衡量是否持续学习。

---

## 7.2 数据来源

Learning Records。

登录。

课程浏览。

视频学习（预留）。

笔记。

AI Tutor。

---

## 7.3 Feature

| 特征                     | 权重  |
| ---------------------- | --- |
| Active Days            | 30% |
| Study Hours            | 25% |
| Course Completion      | 20% |
| Homework Participation | 15% |
| AI Tutor Usage         | 10% |

输出：

0~1。

---

## 7.4 Engagement 更新周期

每天凌晨刷新。

Homework 完成立即刷新。

Quiz 完成立即刷新。

---

# 第八章 Practice Score（P）

## 8.1 Practice 定义

实践能力。

强调实验、编程、项目。

---

## 8.2 数据来源

实验。

编程作业。

代码提交。

项目（预留）。

AI Evaluation。

---

## 8.3 Feature

实验完成率。

实验成绩。

代码评分。

实践次数。

实践时长。

---

## 8.4 Practice 更新事件

实验提交。

代码评分。

AI 评价完成。

立即刷新。

---

# 第九章 Consistency Score（C）

## 9.1 Consistency 定义

学习连续性。

关注习惯。

---

## 9.2 Feature

连续学习天数。

本周学习天数。

学习中断次数。

学习热力图。

学习时间规律。

---

## 9.3 连续学习计算

Daily Learning Timeline。

连续学习：

1~30 天。

连续越长。

Consistency 越高。

---

## 9.4 中断惩罚

超过三天未学习。

Consistency 快速下降。

Risk 上升。

---

# 第十章 AI Interaction Score（A）

## 10.1 AI Interaction 定义

学生与 AI Tutor 的学习互动程度。

不是聊天数量。

强调学习价值。

---

## 10.2 Feature

Tutor Chat。

Lesson Review。

AI 推荐完成率。

AI Quiz。

AI 总学习时间。

---

## 10.3 Interaction Feature 权重

Tutor Conversation：35%。

AI Quiz：25%。

AI Review：20%。

Recommendation Completion：20%。

---

## 10.4 防刷机制

连续重复聊天。

无学习行为。

不增加 AI Score。

---

# 第十一章 Risk Score（R）

## 11.1 Risk 定义

学习风险程度。

由 Prediction Engine 输出。

Mirror 保存结果。

---

## 11.2 Risk 来源

Knowledge Weakness。

Consistency。

Homework Delay。

Quiz Failure。

Engagement。

Prediction Engine。

---

## 11.3 Risk 等级

| 分数      | 等级     |
| ------- | ------ |
| 0~0.3   | Low    |
| 0.3~0.6 | Medium |
| 0.6~1   | High   |

Risk Engine Part07.3 详细说明。

---

# 第十二章 Overall Score（成长综合分）

## 12.1 综合成长分

综合成长分范围：

0~100。

Dashboard 使用。

---

## 12.2 权重设计

| 指标             | 权重  |
| -------------- | --- |
| Mastery        | 30% |
| Engagement     | 20% |
| Practice       | 15% |
| Consistency    | 15% |
| AI Interaction | 10% |
| Risk（反向）       | 10% |

Risk 越高综合分越低。

---

## 12.3 输出等级

| 分数     | 等级         |
| ------ | ---------- |
| 90~100 | Excellent  |
| 75~89  | Good       |
| 60~74  | Developing |
| 40~59  | Warning    |
| 0~39   | High Risk  |

Teacher Dashboard 使用。

---

# 第十三章 Mirror Builder（核心）

## 13.1 Mirror Builder 职责

Mirror Builder 聚合全部状态。

输入：

Feature。

输出：

Learning Mirror。

保存数据库。

---

## 13.2 Builder 生命周期

Feature Extractor

↓

Score Calculator

↓

Overall Score

↓

Mirror Vector

↓

Mirror Repository

↓

Timeline Event

---

## 13.3 Builder 输出对象

```json
{
 "overall_score":81.4,
 "learning_state":"improving",
 "mirror_vector":{}
}
```

---

# 第十四章 Learning State 分类

## Learning State

| 状态        | 条件           |
| --------- | ------------ |
| stable    | 波动较小         |
| improving | 综合分持续提升      |
| warning   | Risk 上升或分数下降 |

Dashboard 使用颜色区分。

---

## Trend Detection

连续七天：

综合分提升。

状态 improving。

连续下降：

warning。

---

# 第十五章 Mirror 更新机制

## 15.1 更新事件

| 事件              | 是否刷新 Mirror |
| --------------- | ----------- |
| Homework 提交     | ✅           |
| Homework 批改     | ✅           |
| Quiz 提交         | ✅           |
| Experiment 提交   | ✅           |
| AI Evaluation   | ✅           |
| Daily Scheduler | ✅           |
| AI Tutor 聊天     | 部分更新        |

---

## 15.2 Scheduler

每天凌晨：

重新聚合 Engagement。

Consistency。

Risk。

Recommendation。

Mirror。

---

## 15.3 实时刷新

Quiz。

Homework。

Experiment。

立即刷新 Mirror。

Teacher Dashboard 实时更新。

---

# 第十六章 Mirror Repository

## MirrorRepository 方法

get_mirror()

refresh_mirror()

update_state_vector()

get_history()

get_dashboard_data()

---

## Mirror History

每日保存快照。

Dashboard 展示趋势。

Timeline 使用。

---

# 第十七章 Dashboard 输出数据

## Dashboard JSON

包含：

综合分。

雷达图。

成长趋势。

学习热力图。

推荐数量。

风险等级。

全部来自 Mirror。

---

## Radar Chart 数据

六维状态。

前端 ECharts 使用。

无需再次计算。

---

# 第十八章 Learning Mirror Checklist

## Engine

- [ ] Feature Extractor
- [ ] Score Calculator
- [ ] Mirror Builder
- [ ] Repository
- [ ] Scheduler

## State

- [ ] Mastery
- [ ] Engagement
- [ ] Practice
- [ ] Consistency
- [ ] AI Interaction
- [ ] Risk

## Dashboard

- [ ] Radar Data
- [ ] Trend Data
- [ ] Overall Score
- [ ] Learning State

---

# 第十九章 本章开发成果

完成 Part07.1 后，ProgramMind Learning Mirror Engine 将建立完整状态建模体系：

- 六维学习状态向量。
- Feature Extractor。
- State Calculator。
- Mirror Builder。
- Overall Score。
- Learning State。
- Dashboard 输出数据规范。
- Growth Engine 数据入口。
