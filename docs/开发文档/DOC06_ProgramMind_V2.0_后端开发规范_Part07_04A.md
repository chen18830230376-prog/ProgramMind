# ProgramMind V2.0 后端开发规范

# Part07.4A —— Growth Dashboard Engine（成长分析引擎·学生成长中心）

> 文档版本：V2.0
> 更新时间：2026-09
> 模块负责人：AI（Growth Analytics Engine）
> 技术栈：FastAPI + SQLAlchemy + Redis + ECharts

---

# 第一章 Growth Dashboard Engine 模块定位

## 1.1 模块职责

Growth Dashboard Engine 是 ProgramMind 成长中心的数据聚合引擎。

它不负责计算 Learning Mirror，而负责把 Mirror、Mastery、Risk、Recommendation 聚合成前端 Dashboard 所需要的数据。

服务对象：

- Student Dashboard（学生成长中心）
- Teacher Dashboard（教师分析中心）
- AI Tutor 首页
- AI 成长报告

---

## 1.2 Dashboard 在系统中的位置

Learning Mirror

Knowledge Mastery

Risk Prediction

Recommendation

Timeline

↓

Growth Analytics Engine

↓

Dashboard JSON API

↓

Vue + ECharts 可视化

---

## 1.3 Dashboard 输出目标

Growth Dashboard 输出的数据必须满足三个特点：

- 可直接渲染（无需前端二次计算）。
- 保持统一 JSON 结构。
- 支持历史趋势查询。

---

# 第二章 Dashboard Engine 总体架构

## 2.1 Engine 模块目录

growth/dashboard/

dashboard_engine.py

dashboard_builder.py

radar_builder.py

trend_builder.py

heatmap_builder.py

statistics_builder.py

timeline_builder.py

dashboard_repository.py

---

## 2.2 Dashboard 生命周期

Mirror 更新

↓

Dashboard Builder

↓

Statistics Builder

↓

Chart Builder

↓

Dashboard Repository

↓

API 返回前端

---

## 2.3 Dashboard Builder 输出模块

| 模块                   | 页面位置  |
| -------------------- | ----- |
| Overview Card        | 首页顶部  |
| Radar Chart          | 六维能力  |
| Mastery Trend        | 趋势图   |
| Study HeatMap        | 学习热力图 |
| Risk Trend           | 风险变化  |
| Timeline             | 学习轨迹  |
| Recommendation Panel | 今日推荐  |

---

# 第三章 Student Dashboard 数据模型

## 3.1 DashboardResponseSchema

Student Dashboard 返回统一 JSON。

字段：

| 字段              | 描述     |
| --------------- | ------ |
| overview        | 顶部统计卡片 |
| radar           | 六维雷达图  |
| mastery_trend   | 掌握趋势   |
| study_heatmap   | 学习热力图  |
| risk_trend      | 风险趋势   |
| timeline        | 学习时间轴  |
| recommendations | 今日推荐   |

所有页面统一调用。

---

## 3.2 Overview 数据结构

包含：

综合成长分。

学习状态。

连续学习天数。

课程完成率。

知识掌握率。

风险等级。

---

## 3.3 Dashboard JSON 示例

```json
{
  "overview":{},
  "radar":[],
  "timeline":[]
}
```

---

# 第四章 Overview Statistics Builder

## 4.1 Overview Card 定位

首页顶部展示核心指标。

---

## 4.2 Card 列表

| Card   | 来源               |
| ------ | ---------------- |
| 综合成长分  | Learning Mirror  |
| 学习状态   | Mirror State     |
| 连续学习天数 | Timeline         |
| 学习总时长  | Learning Records |
| 已完成课程数 | Enrollment       |
| 今日学习时间 | Timeline         |

---

## 4.3 Overview JSON

```json
{
 "overall_score":86,
 "learning_state":"improving",
 "study_hours_today":95,
 "streak_days":12
}
```

---

# 第五章 Radar Builder（六维雷达图）

## 5.1 Radar 图定位

展示 Learning Mirror 六维状态。

M/E/P/C/A/R。

---

## 5.2 数据来源

Learning Mirror Vector。

无需再次计算。

---

## 5.3 Radar JSON

```json
[
 {"dimension":"Knowledge Mastery","score":82},
 {"dimension":"Engagement","score":74}
]
```

ECharts Radar 使用。

---

## 5.4 雷达图颜色规范

Mastery：蓝。

Engagement：绿。

Practice：橙。

Consistency：紫。

AI Interaction：青。

Risk：红（反向）。

统一主题。

---

# 第六章 Mastery Trend Builder

## 6.1 模块定位

展示知识掌握变化。

---

## 6.2 支持时间维度

7 天。

30 天。

学期。

全部。

---

## 6.3 数据来源

knowledge_mastery_history。

Mirror Snapshot。

---

## 6.4 输出 JSON

```json
[
 {
   "date":"09-01",
   "mastery":72
 }
]
```

折线图直接使用。

---

# 第七章 Study HeatMap Builder

## 7.1 学习热力图定位

展示每天学习情况。

GitHub Contribution 风格。

---

## 7.2 数据来源

learning_records。

Timeline。

AI Tutor。

Quiz。

Homework。

---

## 7.3 HeatMap 数据结构

日期。

学习分钟数。

学习次数。

活跃程度。

---

## 7.4 HeatMap JSON

```json
[
 {
   "date":"2026-09-01",
   "minutes":95,
   "level":3
 }
]
```

---

# 第八章 Daily Learning Statistics

## 8.1 每日统计

输出：

学习时长。

课程数。

AI Tutor 时间。

实验时间。

Quiz 时间。

---

## 8.2 Weekly Statistics

一周学习统计。

每天：

学习分钟。

学习任务数量。

完成率。

---

## 8.3 Monthly Statistics

本月学习：

总时长。

平均每日学习。

学习天数。

最长连续学习。

---

# 第九章 Timeline Builder

## 9.1 Timeline 定位

记录学习成长轨迹。

按时间排序。

---

## 9.2 Timeline Event 来源

Homework。

Quiz。

Experiment。

AI Tutor。

Recommendation。

Achievement。

Warning。

---

## 9.3 Timeline JSON

```json
[
 {
   "time":"09-01 20:00",
   "type":"quiz_completed",
   "title":"完成链表专项测验"
 }
]
```

---

## 9.4 Timeline 分类颜色

学习。

绿色。

测验。

蓝色。

实验。

橙色。

推荐。

紫色。

风险。

红色。

---

# 第十章 Risk Trend Builder

## 10.1 模块定位

展示学习风险变化。

---

## 10.2 数据来源

risk_history。

Risk Prediction。

Mirror Snapshot。

---

## 10.3 输出 JSON

```json
[
 {
   "date":"09-01",
   "risk":0.42
 }
]
```

折线图展示。

---

## 10.4 Risk Trend 分类

持续下降。

绿色。

稳定。

黄色。

持续上升。

红色。

---

# 第十一章 Recommendation Panel Builder

## 11.1 Dashboard 推荐中心

展示：

今日学习建议。

---

## 11.2 推荐分类

今日推荐。

继续学习。

AI Tutor 推荐。

实验推荐。

Quiz 推荐。

课程资源推荐。

---

## 11.3 JSON

```json
[
 {
   "priority":"high",
   "title":"复习链表"
 }
]
```

---

# 第十二章 Course Progress Builder

## 12.1 模块定位

课程学习进度。

---

## 12.2 数据来源

Enrollment。

Chapter Completion。

Homework。

Quiz。

---

## 12.3 输出 JSON

课程名称。

完成率。

掌握率。

风险。

章节数。

---

# 第十三章 Achievement Builder

## 13.1 Achievement 定位

学习成就。

激励系统。

---

## 13.2 Achievement 类型

连续学习。

Quiz 达成。

实验完成。

知识掌握。

AI Tutor 连续学习。

---

## 13.3 Achievement JSON

```json
[
 {
   "badge":"连续学习7天",
   "time":"09-01"
 }
]
```

---

# 第十四章 Learning Statistics Builder

## 14.1 学习统计中心

输出：

累计学习时间。

累计 Quiz 数。

累计实验数。

累计 Homework 数。

AI Tutor 次数。

---

## 14.2 学期统计

课程平均掌握。

课程平均风险。

课程平均投入。

学习增长率。

---

# 第十五章 Dashboard Repository 与 Service

## DashboardRepository

方法：

get_dashboard()

get_heatmap()

get_radar()

get_trend()

get_statistics()

---

## DashboardService

build_dashboard()

refresh_dashboard()

get_student_dashboard()

get_teacher_dashboard()

---

# 第十六章 Dashboard API 对应关系

| API               | 数据来源         |
| ----------------- | ------------ |
| /growth/dashboard | 全部 Dashboard |
| /growth/radar     | Radar        |
| /growth/trend     | Trend        |
| /growth/heatmap   | HeatMap      |
| /growth/timeline  | Timeline     |

DOC04 API 对应。

---

# 第十七章 Dashboard Checklist

## Overview

- [ ] Overall Score
- [ ] Learning State
- [ ] Streak Days
- [ ] Study Hours

## Charts

- [ ] Radar Chart
- [ ] Mastery Trend
- [ ] Risk Trend
- [ ] Study HeatMap

## Timeline

- [ ] Timeline Events
- [ ] Achievement Timeline
- [ ] Recommendation Timeline

## Recommendation

- [ ] Today Recommendation
- [ ] AI Tutor Recommendation
- [ ] Quiz Recommendation

---

# 第十八章 本章开发成果（上）

完成 Part07.4A 后，ProgramMind Growth Dashboard Engine 将具备：

- Student Dashboard 数据聚合。
- 六维雷达图数据生成。
- Mastery 趋势图。
- Study HeatMap。
- Timeline 时间轴。
- Recommendation Dashboard。
- Achievement Dashboard。
- Course Progress Dashboard。
