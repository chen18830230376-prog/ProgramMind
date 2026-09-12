# ProgramMind V2.0 后端开发规范

# Part07.2B —— Knowledge Mastery Engine（知识掌握算法引擎·下）

> 文档版本：V2.0
> 更新时间：2026-09
> 模块负责人：AI（Knowledge Mastery Engine）
> 技术栈：FastAPI + SQLAlchemy + NumPy + Redis + ECharts

---

# 第一章 Knowledge HeatMap（知识掌握热力图）

## 1.1 HeatMap 模块定位

Knowledge HeatMap 用于可视化学生对于课程知识点的掌握情况。

HeatMap 是 Dashboard 的核心图表，也是 AI Tutor 推荐复习内容的重要依据。

输出对象：

- Student Dashboard
- Teacher Dashboard
- AI Tutor
- Recommendation Engine

---

## 1.2 HeatMap 数据来源

HeatMap 不直接读取测验成绩，而读取：

knowledge_mastery_records

每个知识点对应一个掌握度。

聚合形成二维热力图。

---

## 1.3 HeatMap 数据结构

每个知识点输出：

| 字段             | 含义    |
| -------------- | ----- |
| knowledge_id   | 知识点ID |
| knowledge_name | 名称    |
| chapter_name   | 所属章节  |
| mastery_score  | 当前掌握度 |
| confidence     | 掌握置信度 |
| difficulty     | 知识点难度 |
| trend          | 趋势    |

---

## 1.4 HeatMap JSON 输出

```json
{
  "chapter":"Python基础",
  "knowledge_points":[
    {
      "name":"变量",
      "mastery":0.92
    },
    {
      "name":"列表推导式",
      "mastery":0.58
    }
  ]
}
```

---

# 第二章 HeatMap 颜色规范

## 2.1 Dashboard 配色

统一颜色映射。

| Mastery   | 颜色  |
| --------- | --- |
| 0.90~1.00 | 深绿色 |
| 0.75~0.89 | 绿色  |
| 0.60~0.74 | 黄色  |
| 0.40~0.59 | 橙色  |
| 0~0.39    | 红色  |

颜色固定，保证教师端一致。

---

## 2.2 HeatMap 排序规则

默认排序：

章节 → 知识点顺序。

支持：

掌握度排序。

风险排序。

更新时间排序。

---

## 2.3 HeatMap 聚合规则

章节内部平均掌握度。

课程平均掌握度。

输出统计数据。

---

# 第三章 Chapter Mastery（章节掌握度）

## 3.1 模块定位

章节掌握度表示学生对某章节整体学习情况。

用于：

- Dashboard
- AI Tutor
- Teacher Dashboard
- Recommendation

---

## 3.2 聚合来源

一个章节包含多个知识点。

章节掌握度来自：

Knowledge Mastery 平均聚合。

并考虑知识点权重。

---

## 3.3 聚合字段

| 字段               | 描述      |
| ---------------- | ------- |
| chapter_id       | 章节      |
| mastery_score    | 章节掌握度   |
| confidence       | 平均置信度   |
| weak_points      | 薄弱知识点数量 |
| completed_points | 已掌握数量   |

---

## 3.4 输出 JSON

```json
{
 "chapter":"链表",
 "mastery_score":0.68,
 "confidence":0.82,
 "weak_points":3,
 "completed_points":8
}
```

---

# 第四章 Course Mastery（课程掌握度）

## 4.1 模块定位

Course Mastery 是课程总体掌握程度。

Dashboard 首页展示。

Teacher Dashboard 排序。

---

## 4.2 聚合来源

章节掌握度。

课程完成率。

实验完成率。

Quiz 完成率。

综合聚合。

---

## 4.3 输出字段

course_id。

course_name。

mastery_score。

confidence。

completion_rate。

trend。

---

## 4.4 Dashboard 示例

Python程序设计：

82%。

数据结构：

71%。

计算机网络：

65%。

形成课程排行榜。

---

# 第五章 Mastery Radar（课程能力雷达）

## 5.1 Radar 图定位

展示课程能力维度。

不是六维 Learning Mirror。

而是课程内部能力。

---

## 5.2 Python Radar 示例

能力：

- 基础语法
- 数据结构
- 函数设计
- 面向对象
- 文件处理
- 算法实践

每项来自知识点聚合。

---

## 5.3 Dashboard JSON

```json
[
  {"dimension":"基础语法","score":92},
  {"dimension":"函数","score":76}
]
```

ECharts Radar 使用。

---

# 第六章 Weak Knowledge Detection（薄弱知识识别）

## 6.1 模块定位

自动发现需要重点学习的知识点。

Recommendation Engine 输入。

---

## 6.2 判定条件

满足任意：

Mastery 低。

Trend Down。

Confidence 高但 Mastery 低。

遗忘严重。

Risk 高。

进入薄弱知识集合。

---

## 6.3 Weak Knowledge JSON

```json
{
 "knowledge":"递归",
 "mastery":0.31,
 "reason":"连续三次测验错误"
}
```

---

## 6.4 Priority 分级

| 等级     | 条件           |
| ------ | ------------ |
| High   | Mastery ＜0.4 |
| Medium | 0.4~0.6      |
| Low    | 0.6~0.7      |

Recommendation 优先 High。

---

# 第七章 Strong Knowledge Detection（优势知识识别）

## 7.1 模块定位

识别学生优势能力。

Teacher Dashboard 展示。

AI Tutor 调整讲解难度。

---

## 7.2 判定条件

Mastery ≥0.85。

Confidence ≥0.8。

Trend Stable/Up。

连续保持。

---

## 7.3 输出字段

knowledge_name。

mastery。

confidence。

连续保持时间。

可推荐挑战题。

---

# 第八章 Mastery Trend Engine

## 8.1 Trend Engine 定位

分析掌握度变化趋势。

支持：

7天。

30天。

学期趋势。

---

## 8.2 Trend 数据来源

每日 Mirror Snapshot。

knowledge_mastery_history。

Timeline。

---

## 8.3 Trend 输出

日期。

Mastery。

Confidence。

Trend。

Dashboard 折线图使用。

---

## 8.4 Trend 分类

| 类型         | 条件    |
| ---------- | ----- |
| improving  | 连续增长  |
| stable     | 波动小   |
| declining  | 连续下降  |
| recovering | 下降后恢复 |

---

# 第九章 Mastery History（掌握历史）

## 9.1 History Repository

每日保存：

knowledge_mastery_history。

支持历史查询。

---

## 9.2 保存频率

每天凌晨快照。

Quiz/Homework 更新时增量保存。

最多保留：

365 天。

---

## 9.3 输出格式

```json
{
 "date":"2026-09-01",
 "mastery":0.73
}
```

---

# 第十章 Review Priority Queue（复习优先队列）

## 10.1 Queue 定位

ProgramMind 自动生成今日复习知识点。

AI Tutor 首页使用。

---

## 10.2 Queue 输入

Mastery。

Forget Factor。

Difficulty。

Risk。

Trend。

Review Count。

---

## 10.3 Priority Score

综合排序。

优先：

低掌握。

高遗忘。

高风险。

高难度。

近期考试。

---

## 10.4 Queue 输出

```json
[
 {
   "knowledge":"链表",
   "priority":"high",
   "estimated_minutes":30
 }
]
```

---

# 第十一章 Review Scheduler

## 11.1 Scheduler 定位

每天生成复习任务。

凌晨运行。

---

## 11.2 Scheduler 输出

今日推荐。

本周推荐。

章节推荐。

课程推荐。

保存 recommendation_records。

---

## 11.3 AI Tutor 联动

学生进入 Tutor。

优先展示：

今日建议复习。

支持一键开始。

---

# 第十二章 Knowledge Coverage Analysis

## 12.1 Coverage 定义

课程知识覆盖率。

学生学习过多少知识点。

---

## 12.2 输出字段

知识点总数。

已学习数量。

已掌握数量。

覆盖率。

---

## 12.3 Teacher Dashboard

班级知识覆盖率。

课程知识覆盖率。

章节覆盖率。

排行榜。

---

# 第十三章 Knowledge Cluster Analysis

## 13.1 Cluster 定位

将知识点聚合能力域。

例如 Python：

语法。

函数。

数据结构。

文件。

异常。

OOP。

---

## 13.2 Cluster 输出

Cluster Score。

Mastery。

Weak Count。

Trend。

Radar 使用。

---

## 13.3 AI Tutor 使用

推荐整个知识模块学习。

不是单知识点。

---

# 第十四章 Mastery 与 Recommendation 联动

## 14.1 Recommendation 输入

Weak Knowledge。

Trend。

Forget Curve。

Review Queue。

Risk。

---

## 14.2 Recommendation 输出

推荐知识点。

推荐实验。

推荐 Quiz。

推荐资料。

推荐 AI Tutor Session。

---

## 14.3 Recommendation 更新事件

Mastery 更新。

自动刷新 Recommendation。

无需等待 Scheduler。

---

# 第十五章 Mastery 与 Learning Mirror 联动

## 15.1 Mirror Builder 输入

Course Mastery。

Chapter Mastery。

Knowledge Mastery。

更新 Mirror.M。

---

## 15.2 Mirror Dashboard 输出

雷达图。

课程热图。

趋势图。

推荐数量。

全部来自 Mastery Engine。

---

# 第十六章 Teacher Dashboard 聚合分析

## 教师端输出

班级平均掌握度。

知识点 Top10。

知识点 Bottom10。

章节掌握排行。

课程掌握排行。

风险学生数量。

---

## 班级 HeatMap

二维矩阵：

学生 × 知识点。

颜色表示掌握度。

支持筛选章节。

---

# 第十七章 Repository 与 Service

## MasteryRepository

方法：

- get_student_mastery()
- get_chapter_mastery()
- get_course_mastery()
- save_mastery_history()
- get_heatmap()

---

## MasteryService

方法：

- update_mastery()
- build_heatmap()
- build_review_queue()
- detect_weak_points()
- calculate_course_mastery()

---

# 第十八章 Knowledge Mastery Engine Checklist（完整版）

## Mastery

- [ ] Mastery Calculator
- [ ] Confidence Calculator
- [ ] Forget Curve
- [ ] Trend Engine

## Analytics

- [ ] HeatMap
- [ ] Chapter Mastery
- [ ] Course Mastery
- [ ] Mastery Radar
- [ ] Weak Knowledge
- [ ] Strong Knowledge
- [ ] Coverage Analysis

## Review

- [ ] Review Queue
- [ ] Scheduler
- [ ] Recommendation Link

## Dashboard

- [ ] HeatMap API
- [ ] Radar API
- [ ] Trend API
- [ ] Teacher HeatMap API

---

# 第十九章 本章开发成果（Knowledge Mastery Engine 完整版）

完成 Part07.2A + Part07.2B 后，ProgramMind Knowledge Mastery Engine 将具备：

- 每知识点动态掌握度模型。
- Confidence（掌握置信度）模型。
- 艾宾浩斯遗忘曲线衰减机制。
- HeatMap（知识热力图）生成能力。
- Chapter / Course Mastery 聚合能力。
- Mastery Trend 趋势分析。
- Weak Knowledge Detection。
- Review Priority Queue。
- Teacher Dashboard 聚合分析。
- 与 Learning Mirror、Recommendation、Risk Engine 完整联动。
