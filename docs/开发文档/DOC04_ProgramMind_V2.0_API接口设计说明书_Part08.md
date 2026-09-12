# ProgramMind V2.0 API 接口设计说明书

# Part08 —— Growth Center（学习状态镜像 / 成长画像 / 推荐系统接口设计）

> 文档版本：V2.0
> 
> 模块负责人：AI（学习状态镜像）+ Backend（成长中心）
> 
> 技术栈：FastAPI + SQLAlchemy + ECharts + NetworkX + bge-m3 + Recommendation Engine

---

# 第一章 模块定位（ProgramMind 核心创新模块）

## 1.1 Learning State Mirror 是什么？

ProgramMind V2.0 不使用“认知数字孪生（Cognitive Digital Twin）”这一概念，而采用：

> **Learning State Mirror（学习状态镜像）**

它表示：

系统持续采集学生学习行为、课程成绩、知识掌握情况、AI学习记录等数据，实时生成一份学生学习状态镜像，用于：

- AI 个性化辅导
- 学情分析
- 学习风险预测
- 推荐学习路径
- 教师智能干预

不是复制学生，而是构建学生当前学习状态的一份动态画像。

---

## 1.2 模块职责

Growth Center 管理 ProgramMind 所有成长数据。

包括：

- 学习画像（Profile）
- 知识掌握图谱
- 学习时间轴
- 热力图
- 风险预测
- AI推荐
- 班级镜像
- 成长报告

所有 Agent 都会读取这里的数据。

---

## 1.3 Backend 目录结构

```
backend/app/growth/

├── profile_service.py
├── mastery_service.py
├── analytics_service.py
├── recommendation_service.py
├── prediction_service.py
├── timeline_service.py
├── intervention_service.py
│
├── mirror/
│   ├── state_builder.py
│   ├── state_updater.py
│   ├── state_metrics.py
│   └── mirror_repository.py
│
└── reports/
    ├── growth_report.py
    ├── weekly_report.py
    └── class_report.py
```

---

## 1.4 Frontend 页面

```
GrowthDashboard.vue

LearningMirror.vue

KnowledgeMastery.vue

LearningTimeline.vue

LearningHeatmap.vue

RecommendationCenter.vue

GrowthReport.vue
```

---

# 第二章 Growth API 总览（18个接口）

## Learning Mirror（5）

| API | Method | 描述       |
| --- | ------ | -------- |
| 801 | GET    | 获取学习状态镜像 |
| 802 | PATCH  | 刷新状态镜像   |
| 803 | GET    | 状态指标详情   |
| 804 | GET    | 班级状态镜像   |
| 805 | GET    | 状态变化历史   |

---

## Knowledge Mastery（4）

| API | Method | 描述      |
| --- | ------ | ------- |
| 806 | GET    | 知识掌握图谱  |
| 807 | GET    | 知识点详情   |
| 808 | PATCH  | 更新掌握度   |
| 809 | GET    | 知识点变化趋势 |

---

## Recommendation（4）

| API | Method | 描述     |
| --- | ------ | ------ |
| 810 | GET    | 今日AI推荐 |
| 811 | GET    | 学习路径推荐 |
| 812 | POST   | 生成复习计划 |
| 813 | GET    | 推荐历史   |

---

## Growth Analytics（5）

| API | Method | 描述       |
| --- | ------ | -------- |
| 814 | GET    | 学习热力图    |
| 815 | GET    | 学习时间轴    |
| 816 | GET    | 成长报告     |
| 817 | GET    | 学习风险预测   |
| 818 | POST   | 教师智能干预建议 |

---

# 第三章 Learning State Mirror API

## API-801 获取学习状态镜像

### URL

```
GET /api/growth/mirror
```

---

### 返回内容

```json
{
  "student_id":"uuid",
  "overall_score":82.5,
  "learning_state":"stable",
  "mastery":0.76,
  "engagement":0.81,
  "practice":0.69,
  "consistency":0.88,
  "risk_level":"low"
}
```

---

## 镜像六大指标

| 指标                  | 来源         |
| ------------------- | ---------- |
| Knowledge Mastery   | 测验+作业+实验   |
| Learning Engagement | 学习记录       |
| Practice Frequency  | 每日学习次数     |
| Consistency         | 连续学习天数     |
| AI Interaction      | AI Tutor记录 |
| Risk Level          | 预测模型       |

---

## API-802 刷新学习状态镜像

触发时机：

- 完成测验
- 完成实验
- AI聊天
- 作业批改
- 学习记录新增

系统重新计算镜像。

---

## API-803 获取状态指标详情

返回：

每项指标组成。

例如：

```json
{
  "engagement":{
    "course_visit":22,
    "ai_chat":14,
    "video_watch":35
  }
}
```

---

## API-804 获取班级状态镜像

教师接口。

返回：

班级平均镜像。

风险人数。

掌握度排行。

---

## API-805 获取状态变化历史

返回：

每天镜像。

支持：

7天。

30天。

学期。

---

# 第四章 Knowledge Mastery API

## API-806 获取知识掌握图谱

### URL

```
GET /api/growth/mastery
```

---

### 返回

```json
{
  "nodes":[
    {
      "knowledge":"Python列表",
      "mastery":0.91
    }
  ]
}
```

---

前端：

ECharts Graph。

颜色表示掌握程度。

---

## API-807 获取知识点详情

返回：

掌握度。

最近练习。

引用教材。

推荐资源。

---

## API-808 更新掌握度

内部接口。

输入：

Quiz。

Homework。

Experiment。

AI Evaluation。

更新：

knowledge_mastery_records。

---

### 更新公式

```
new_mastery

=

0.7 × old

+

0.3 × score
```

保持平滑更新。

---

## API-809 知识点变化趋势

返回：

折线图数据。

掌握提升。

下降原因。

---

# 第五章 Recommendation Engine API

## API-810 今日AI推荐

根据：

课程。

镜像。

风险。

知识掌握。

返回：

今日任务。

推荐教材。

推荐题目。

推荐实验。

推荐AI助手。

---

### 返回示例

```json
{
  "recommendations":[
    {
      "type":"quiz",
      "title":"链表专项训练"
    }
  ]
}
```

---

## API-811 学习路径推荐

输入：

课程。

目标章节。

输出：

学习路径 DAG。

例如：

数组

↓

链表

↓

栈

↓

队列

↓

树

---

## API-812 AI生成复习计划

输入：

考试日期。

课程。

每天学习时间。

返回：

每日任务。

知识点。

AI建议。

---

## API-813 推荐历史

记录：

什么时候推荐。

是否完成。

效果反馈。

---

# 第六章 Learning Heatmap API

## API-814 获取学习热力图

返回：

365天学习数据。

```json
[
 {
   "date":"2026-08-12",
   "value":3
 }
]
```

---

来源：

LEARNING_RECORDS 聚合。

不是随机数据。

---

统计：

学习次数。

学习时长。

AI次数。

实验次数。

---

# 第七章 Learning Timeline API

## API-815 获取学习时间轴

返回：

所有学习事件。

包括：

- 学习课程
- 提交作业
- AI聊天
- 测验
- 实验
- 收藏
- 推荐完成

---

前端：

Timeline。

---

# 第八章 Growth Report API

## API-816 获取成长报告

自动生成成长报告。

内容：

总体表现。

知识掌握。

成长趋势。

学习建议。

风险分析。

AI总结。

---

导出：

Markdown。

PDF。

---

# 第九章 Learning Risk Prediction API

## API-817 学习风险预测

### URL

```
GET /api/growth/risk
```

---

### 返回

```json
{
 "risk":"medium",
 "score":0.63,
 "reasons":[
   "连续三天未学习"
 ]
}
```

---

### 风险来源

学习时长。

知识掌握下降。

实验未完成。

作业延期。

AI学习减少。

---

### 风险等级

| Score   | 等级     |
| ------- | ------ |
| 0~0.3   | Low    |
| 0.3~0.6 | Medium |
| 0.6~1   | High   |

---

# 第十章 Teacher Intervention API

## API-818 教师智能干预建议

教师接口。

输入：

学生ID。

课程ID。

返回：

建议。

提醒。

资源推荐。

干预等级。

---

示例

```json
{
 "interventions":[
   "建议完成链表实验"
 ]
}
```

---

# 第十一章 Learning Mirror 数据模型

## 六维学习状态向量

```
S

=

[M,E,P,C,A,R]
```

---

| 缩写  | 含义             |
| --- | -------------- |
| M   | Mastery        |
| E   | Engagement     |
| P   | Practice       |
| C   | Consistency    |
| A   | AI Interaction |
| R   | Risk           |

---

所有指标范围：

0~1。

---

## Overall Score

```
Overall

=

Σ(weight × metric)
```

默认权重：

Mastery 30%。

Engagement 20%。

Practice 15%。

Consistency 15%。

AI Interaction 10%。

Risk 10%。

---

# 第十二章 Mirror Builder Service

负责生成镜像。

流程：

读取数据库。

↓

聚合学习记录。

↓

聚合掌握度。

↓

聚合AI记录。

↓

聚合风险。

↓

输出状态镜像。

---

更新频率：

实时。

夜间批处理。

教师查看前刷新。

---

# 第十三章 Recommendation Service

输入：

Learning Mirror。

Knowledge Mastery。

Learning Timeline。

Risk Prediction。

输出：

推荐资源。

推荐实验。

推荐题目。

推荐课程。

推荐AI任务。

---

推荐类型

| 类型                        | 描述     |
| ------------------------- | ------ |
| Knowledge Recommendation  | 知识点    |
| Resource Recommendation   | 教材/PPT |
| Quiz Recommendation       | 题目     |
| Experiment Recommendation | 实验     |
| AI Recommendation         | AI辅导   |

---

# 第十四章 Prediction Service

负责风险预测。

输入：

历史学习记录。

掌握度变化。

连续学习情况。

AI使用频率。

输出：

Risk Score。

Risk Reason。

Suggestion。

---

预留：

ML模型。

LightGBM。

XGBoost。

---

# 第十五章 Analytics Service

负责统计：

学习时长。

课程排名。

知识掌握。

实验完成率。

测验通过率。

成长趋势。

班级统计。

---

所有 Dashboard 调这里。

---

# 第十六章 Repository 设计

ProfileRepository。

MirrorRepository。

MasteryRepository。

TimelineRepository。

RecommendationRepository。

PredictionRepository。

---

# 第十七章 Frontend SDK

```
growth.ts

getLearningMirror()

refreshMirror()

getMirrorMetrics()

getClassMirror()

getMirrorHistory()

getKnowledgeMastery()

getKnowledgeDetail()

updateKnowledgeMastery()

getMasteryTrend()

getTodayRecommendation()

getLearningPath()

generateReviewPlan()

getRecommendationHistory()

getLearningHeatmap()

getLearningTimeline()

getGrowthReport()

getRiskPrediction()

getTeacherIntervention()
```

---

# 第十八章 Growth Center Checklist

## Learning Mirror

- [ ] 学习状态镜像
- [ ] 状态刷新
- [ ] 状态历史
- [ ] 班级镜像

## Knowledge Mastery

- [ ] 图谱
- [ ] 趋势
- [ ] 更新掌握度

## Recommendation

- [ ] 今日推荐
- [ ] 学习路径
- [ ] AI复习计划

## Analytics

- [ ] 热力图
- [ ] 时间轴
- [ ] 成长报告
- [ ] 风险预测
- [ ] 教师干预

---

# 第十九章 Challenge Cup 创新点映射（答辩重点）

## 创新点一：学习状态镜像（Learning State Mirror）

替代 Demo 中“认知数字孪生”。

强调：

学习行为实时镜像。

知识掌握动态更新。

AI个性化驱动。

---

## 创新点二：知识掌握图谱

课程知识网络。

节点颜色表示掌握度。

支持AI推荐。

---

## 创新点三：智能推荐引擎

不是随机推荐。

依据：

学习状态。

风险。

知识点。

课程路径。

---

## 创新点四：智能干预机制

教师看到风险学生。

系统自动生成干预建议。

形成：

学习 → AI → 教师 → 学生

闭环。

---

# 第二十章 本章开发成果（DOC04 完结）

Growth Center 完成后，ProgramMind V2.0 将具备：

- 学习状态镜像（Learning State Mirror）。
- 知识掌握图谱。
- 学习热力图。
- 学习时间轴。
- AI个性化推荐。
- AI复习计划。
- 学习风险预测。
- 教师智能干预。
- 成长报告自动生成。

至此，ProgramMind V2.0 全部 API（Auth、Profile、Courses、Learning、Teaching、Knowledge Base、AI Engine、Growth Center）设计完成，共 **约150+ REST API**，覆盖整个挑战杯项目开发。
