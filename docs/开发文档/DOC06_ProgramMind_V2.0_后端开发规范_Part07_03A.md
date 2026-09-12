# ProgramMind V2.0 后端开发规范

# Part07.3A —— Risk Prediction Engine（学习风险预测引擎）

> 文档版本：V2.0
> 更新时间：2026-09
> 模块负责人：AI（Risk Prediction Engine）
> 技术栈：FastAPI + SQLAlchemy + NumPy + Pandas + Redis

---

# 第一章 Risk Prediction Engine 模块定位

## 1.1 模块职责

Risk Prediction Engine 是 ProgramMind Learning Mirror Engine 的预测模块。

负责持续评估学生未来学习风险，而不是预测考试分数。

预测目标包括：

- 学习掉队风险
- 知识遗忘风险
- 连续学习中断风险
- 作业逾期风险
- 课程完成风险

输出 Risk Score，供 AI Tutor、Dashboard 和 Recommendation Engine 使用。

---

## 1.2 Risk Engine 在系统中的位置

Learning Records

Homework

Quiz

Experiment

Knowledge Mastery

Learning Mirror

↓

Risk Feature Extractor

↓

Risk Prediction Engine

↓

Risk Repository

↓

Recommendation Engine

↓

Teacher Dashboard / AI Tutor

形成预测—干预闭环。

---

## 1.3 Prediction 原则

ProgramMind 不预测“是否挂科”。

预测的是：

学生当前学习状态未来恶化的概率。

强调：

- 可解释。
- 可追踪。
- 可干预。
- 可恢复。

---

# 第二章 Risk Engine 架构

## 2.1 Engine 目录

growth/risk/

risk_engine.py

risk_feature_extractor.py

risk_calculator.py

risk_repository.py

risk_scheduler.py

risk_rules.py

risk_history.py

---

## 2.2 生命周期

学习行为更新

↓

Feature Extractor

↓

Risk Calculator

↓

Risk Score

↓

Risk Level

↓

Risk Repository

↓

Recommendation Trigger

---

## 2.3 Scheduler

每天凌晨运行：

重新计算：

- Consistency Risk
- Forget Risk
- Overall Risk
- Risk Trend

---

# 第三章 Risk 数据模型

## 3.1 RiskRecord

数据库：

risk_predictions。

一条记录表示：

学生某门课程当前风险状态。

---

## 3.2 RiskState

字段：

| 字段           | 描述   |
| ------------ | ---- |
| student_id   | 学生   |
| course_id    | 课程   |
| risk_score   | 综合风险 |
| risk_level   | 风险等级 |
| risk_factors | 风险因子 |
| trend        | 趋势   |
| updated_at   | 更新时间 |

---

## 3.3 Risk JSON

```json
{
 "risk_score":0.63,
 "risk_level":"high",
 "trend":"up",
 "risk_factors":[]
}
```

Mirror 保存 Risk。

---

# 第四章 Risk Feature Extractor

## 4.1 特征来源

Risk 特征来自多个模块。

| 模块              | 特征   |
| --------------- | ---- |
| Learning Mirror | 六维状态 |
| Mastery         | 掌握度  |
| Homework        | 提交情况 |
| Quiz            | 成绩   |
| Timeline        | 连续学习 |
| AI Tutor        | AI互动 |

---

## 4.2 Feature 分类

### 学习行为

study_hours_week

active_days

completion_rate

login_gap

### 作业行为

late_submission

missing_homework

average_score

### 测验行为

quiz_accuracy

quiz_decline_rate

### Mirror 特征

mastery

consistency

engagement

practice

### AI 特征

ai_chat_days

recommendation_accept_rate

review_completion_rate

---

## 4.3 FeatureVector

统一输出：

RiskFeatureVector。

供 Calculator 使用。

---

# 第五章 Risk Score 模型（核心）

## 5.1 Risk Score 定义

Risk Score：

学生未来学习风险概率估计。

范围：

0~1。

越高风险越高。

---

## 5.2 Risk 等级

| Score     | 等级       |
| --------- | -------- |
| 0.00~0.30 | Low      |
| 0.31~0.60 | Medium   |
| 0.61~0.80 | High     |
| 0.81~1.00 | Critical |

Dashboard 使用颜色区分。

---

## 5.3 Risk 聚合来源

| 因子               | 权重  |
| ---------------- | --- |
| Mastery Risk     | 30% |
| Consistency Risk | 20% |
| Homework Risk    | 15% |
| Quiz Risk        | 15% |
| Engagement Risk  | 10% |
| Forget Risk      | 10% |

默认权重。

后台支持配置。

---

# 第六章 Mastery Risk

## 6.1 定义

掌握度不足导致学习风险。

来源：

Knowledge Mastery Engine。

---

## 6.2 判定规则

课程掌握度。

章节掌握度。

薄弱知识数量。

趋势下降。

综合形成风险。

---

## 6.3 Risk 输出

```json
{
 "factor":"mastery",
 "score":0.72,
 "reason":"链表、队列掌握度持续下降"
}
```

---

# 第七章 Consistency Risk

## 7.1 定义

连续学习中断风险。

来源：

Timeline。

Daily Learning。

---

## 7.2 特征

连续学习天数。

连续中断天数。

学习热力图。

学习规律。

---

## 7.3 判定规则

超过：

3 天未学习。

Risk 快速增加。

超过：

7 天。

进入 High Risk。

---

# 第八章 Homework Risk

## 8.1 来源

Homework Repository。

---

## 8.2 特征

提交率。

迟交率。

未交次数。

平均成绩。

---

## 8.3 Risk Trigger

连续两次迟交。

Risk 提升。

连续未交。

Critical。

---

# 第九章 Quiz Risk

## 9.1 来源

Quiz Records。

---

## 9.2 特征

平均正确率。

下降趋势。

章节错误集中。

时间异常。

---

## 9.3 Trend Risk

连续三次下降。

Risk 增加。

连续提升。

Risk 降低。

---

# 第十章 Engagement Risk

## 10.1 来源

Learning Mirror Engagement。

---

## 10.2 特征

学习时间下降。

AI Tutor 使用减少。

课程访问减少。

实验减少。

---

## 10.3 Engagement Trend

连续两周下降。

进入 Warning。

---

# 第十一章 Forget Risk

## 11.1 来源

Forget Curve Engine。

---

## 11.2 特征

高掌握长期未复习。

高难知识长期未学习。

Review Queue 未完成。

---

## 11.3 Forget Trigger

Forget Factor ＜0.7。

Recommendation Trigger。

---

# 第十二章 Risk Trend Engine

## 12.1 Risk Trend 定义

分析风险变化。

不是 Risk Score。

而是变化趋势。

---

## 12.2 Trend 类型

| 类型        | 条件   |
| --------- | ---- |
| stable    | 波动小  |
| improving | 风险下降 |
| worsening | 风险上升 |
| critical  | 快速上升 |

---

## 12.3 Dashboard 输出

7 天 Risk Trend。

30 天 Risk Trend。

课程 Trend。

---

# 第十三章 Risk Factors（可解释风险）

## 13.1 风险解释机制

Risk Engine 必须输出原因。

不能只有分数。

---

## 13.2 Risk Factor Schema

字段：

factor_name。

score。

reason。

suggestion。

priority。

---

## 13.3 示例

```json
[
 {
   "factor":"consistency",
   "reason":"连续5天未学习",
   "priority":"high"
 }
]
```

Teacher Dashboard 展示。

---

# 第十四章 Risk History

## 14.1 保存历史

risk_history。

每日快照。

保留一年。

---

## 14.2 History 输出

日期。

Risk Score。

Risk Level。

Trend。

Dashboard 折线图。

---

## 14.3 Snapshot Trigger

每天凌晨。

Homework 更新。

Quiz 更新。

Mirror 更新。

保存历史。

---

# 第十五章 Risk Trigger Rules

## 实时 Trigger

Homework。

Quiz。

Experiment。

AI Evaluation。

Mirror Refresh。

立即重新预测。

---

## Scheduler Trigger

凌晨：

Forget Risk。

Consistency Risk。

Trend。

Risk Snapshot。

---

# 第十六章 Risk Repository 与 Service

## RiskRepository

get_current_risk()

save_prediction()

get_history()

list_high_risk()

---

## RiskService

calculate_risk()

refresh_risk()

detect_trend()

build_dashboard_data()

trigger_recommendation()

---

# 第十七章 Teacher Dashboard 风险分析

## 教师端输出

班级高风险人数。

课程风险排行。

风险趋势。

风险学生列表。

风险原因统计。

---

## 风险排行榜

学生。

Risk Score。

Risk Level。

Trend。

推荐数量。

---

# 第十八章 Risk Prediction Engine Checklist

## Engine

- [ ] Feature Extractor
- [ ] Risk Calculator
- [ ] Trend Engine
- [ ] Scheduler

## Factors

- [ ] Mastery Risk
- [ ] Consistency Risk
- [ ] Homework Risk
- [ ] Quiz Risk
- [ ] Engagement Risk
- [ ] Forget Risk

## Dashboard

- [ ] Risk History
- [ ] Trend Chart
- [ ] Teacher Ranking
- [ ] Factor Explainability

---

# 第十九章 本章开发成果

完成 Part07.3A 后，ProgramMind Risk Prediction Engine 将具备：

- 多因素学习风险预测。
- 可解释 Risk Factors。
- Risk Trend 分析。
- Risk History。
- Teacher Dashboard 风险聚合。
- Recommendation Engine 的触发入口。
