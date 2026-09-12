# ProgramMind V2.0 数据库设计说明书

# Part07 —— Growth Domain（Learning State Mirror 成长中心数据库设计）

> 文档版本：V2.0
> 更新时间：2026-09
> 模块负责人：AI（Learning Mirror）+ Backend（数据库）
> 技术栈：FastAPI + SQLAlchemy + ECharts + Recommendation Engine + XGBoost（预留）

---

# 第一章 Growth Domain 模块说明

## 1.1 模块定位

Growth Domain 是 ProgramMind 的学习成长中心，也是平台最重要的创新模块。

负责持续构建学生的 **Learning State Mirror（学习状态镜像）**，生成成长画像、知识掌握图谱、风险预测和 AI 推荐。

Growth Domain 不直接产生数据，而是消费：

- Learning Domain
- Knowledge Domain
- AI Domain

的数据进行聚合分析。

---

## 1.2 Growth 数据流

learning_records

↓

knowledge_mastery_records

↓

learning_mirror

↓

risk_predictions

↓

recommendations

↓

growth_reports

↓

教师干预 / AI Tutor

---

## 1.3 数据库结构（6 张核心表）

| 表名                        | 功能      |
| ------------------------- | ------- |
| learning_mirror           | 学习状态镜像  |
| knowledge_mastery_records | 知识掌握记录  |
| learning_timeline         | 学习成长时间轴 |
| recommendations           | AI 推荐记录 |
| risk_predictions          | 学习风险预测  |
| growth_reports            | 成长报告    |

ER 图：

users

↓

learning_records

↓

knowledge_mastery_records

↓

learning_mirror

↓

recommendations

↓

growth_reports

risk_predictions 独立关联 mirror。

---

# 第二章 learning_mirror（学习状态镜像）

## 2.1 表定位

Learning Mirror 保存学生当前学习状态。

**一名学生只有一份最新镜像。**

历史镜像通过 Timeline 保存。

---

## 2.2 六维学习状态向量

ProgramMind 定义六维状态：

<math block value="S=[M,E,P,C,A,R]"/>

| 缩写  | 指标                      |
| --- | ----------------------- |
| M   | Knowledge Mastery（知识掌握） |
| E   | Engagement（学习投入）        |
| P   | Practice（实践频率）          |
| C   | Consistency（学习连续性）      |
| A   | AI Interaction（AI学习互动）  |
| R   | Risk（学习风险）              |

所有指标范围：

0~1。

---

## 2.3 字段设计（完整版）

| 字段                   | 类型           | 说明                              |
| -------------------- | ------------ | ------------------------------- |
| id                   | UUID         | 主键                              |
| student_id           | UUID         | 学生                              |
| overall_score        | DECIMAL(5,2) | 综合成长分                           |
| mastery_score        | DECIMAL(4,3) | M                               |
| engagement_score     | DECIMAL(4,3) | E                               |
| practice_score       | DECIMAL(4,3) | P                               |
| consistency_score    | DECIMAL(4,3) | C                               |
| ai_interaction_score | DECIMAL(4,3) | A                               |
| risk_score           | DECIMAL(4,3) | R                               |
| mirror_vector        | JSON         | 六维向量                            |
| learning_state       | ENUM         | stable/improving/warning        |
| updated_source       | ENUM         | quiz/homework/experiment/system |
| created_at           | DATETIME     | 创建时间                            |
| updated_at           | DATETIME     | 更新时间                            |

---

## 2.4 MySQL DDL

```sql
CREATE TABLE learning_mirror (

    id CHAR(36) PRIMARY KEY,

    student_id CHAR(36) UNIQUE NOT NULL,

    overall_score DECIMAL(5,2),

    mastery_score DECIMAL(4,3),

    engagement_score DECIMAL(4,3),

    practice_score DECIMAL(4,3),

    consistency_score DECIMAL(4,3),

    ai_interaction_score DECIMAL(4,3),

    risk_score DECIMAL(4,3),

    mirror_vector JSON,

    learning_state ENUM(
        'stable',
        'improving',
        'warning'
    ),

    updated_source ENUM(
        'quiz',
        'homework',
        'experiment',
        'system'
    ),

    created_at DATETIME(6),

    updated_at DATETIME(6),

    FOREIGN KEY(student_id)
        REFERENCES users(id)
        ON DELETE CASCADE
);
```

---

## 2.5 mirror_vector JSON 示例

```json
{
  "mastery":0.82,
  "engagement":0.77,
  "practice":0.71,
  "consistency":0.88,
  "ai_interaction":0.65,
  "risk":0.23
}
```

前端雷达图直接读取。

---

## 2.6 综合成长分计算

<math block value="Overall=0.30M+0.20E+0.15P+0.15C+0.10A+0.10(1-R)"/>

输出：

0~100。

---

# 第三章 knowledge_mastery_records（知识掌握记录）

## 3.1 表定位

记录学生每一个知识点的掌握程度。

Learning Mirror 的主要数据来源。

---

## 3.2 字段设计

| 字段                 | 类型           |
| ------------------ | ------------ |
| id                 | UUID         |
| student_id         | UUID         |
| course_id          | UUID         |
| chapter_id         | UUID         |
| knowledge_id       | UUID         |
| mastery_score      | DECIMAL(4,3) |
| confidence         | DECIMAL(4,3) |
| source             | ENUM         |
| update_count       | INT          |
| last_practice_time | DATETIME     |
| created_at         | DATETIME     |
| updated_at         | DATETIME     |

---

## 3.3 source

| 来源             |
| -------------- |
| homework       |
| experiment     |
| quiz           |
| ai_evaluation  |
| teacher_review |

支持 AI 更新掌握度。

---

## 3.4 掌握度更新公式

<math block value="Mastery_{new}=0.7\\times Mastery_{old}+0.3\\times Score"/>

避免剧烈波动。

---

## 3.5 SQLAlchemy Model

```python
class KnowledgeMasteryRecord(Base, BaseModel):

    __tablename__="knowledge_mastery_records"

    student_id = mapped_column(ForeignKey("users.id"))

    knowledge_id = mapped_column(ForeignKey("knowledge_points.id"))

    mastery_score = mapped_column(Float)

    confidence = mapped_column(Float)

    source = mapped_column(Enum(MasterySource))

    update_count = mapped_column(Integer)
```

---

# 第四章 learning_timeline（成长时间轴）

## 4.1 表定位

记录成长事件。

前端 Timeline 页面数据源。

---

## 4.2 字段设计

| 字段           | 类型       |
| ------------ | -------- |
| id           | UUID     |
| student_id   | UUID     |
| course_id    | UUID     |
| event_type   | ENUM     |
| title        | VARCHAR  |
| description  | TEXT     |
| score_change | FLOAT    |
| metadata     | JSON     |
| created_at   | DATETIME |

---

## 4.3 event_type

| 类型                   |
| -------------------- |
| course_started       |
| homework_completed   |
| experiment_completed |
| quiz_completed       |
| mastery_updated      |
| ai_recommendation    |
| report_generated     |
| risk_warning         |

---

## Timeline 示例

```json
{
 "title":"完成 Python 第五章测验",
 "score_change":2.8
}
```

---

## Timeline 前端用途

成长时间轴。

成长积分。

每日动态。

---

# 第五章 recommendations（AI 推荐记录）

## 5.1 表定位

保存 AI 给学生生成的推荐。

支持历史查看。

支持完成反馈。

---

## 5.2 推荐类型

| recommendation_type | 描述     |
| ------------------- | ------ |
| knowledge           | 推荐知识点  |
| quiz                | 推荐测验   |
| experiment          | 推荐实验   |
| homework            | 推荐作业   |
| resource            | 推荐资料   |
| review_plan         | 推荐复习计划 |

---

## 5.3 字段设计

| 字段                    | 类型       |
| --------------------- | -------- |
| id                    | UUID     |
| student_id            | UUID     |
| recommendation_type   | ENUM     |
| target_id             | UUID     |
| title                 | VARCHAR  |
| description           | TEXT     |
| priority              | ENUM     |
| status                | ENUM     |
| reason                | TEXT     |
| recommendation_detail | JSON     |
| created_at            | DATETIME |
| completed_at          | DATETIME |

---

## priority

low

medium

high

critical

---

## recommendation_detail JSON

```json
{
 "knowledge":"列表推导式",
 "reason":"连续两次测验错误",
 "estimated_minutes":25
}
```

---

## status

| 状态        |
| --------- |
| pending   |
| accepted  |
| completed |
| dismissed |

---

# 第六章 risk_predictions（学习风险预测）

## 6.1 表定位

保存 AI 风险预测。

每日刷新一次。

教师查看风险学生。

---

## 6.2 风险等级

| Risk Score | 等级     |
| ---------- | ------ |
| 0~0.30     | Low    |
| 0.30~0.60  | Medium |
| 0.60~1.00  | High   |

---

## 6.3 字段设计

| 字段                      | 类型       |
| ----------------------- | -------- |
| id                      | UUID     |
| student_id              | UUID     |
| mirror_id               | UUID     |
| risk_score              | DECIMAL  |
| risk_level              | ENUM     |
| prediction_model        | VARCHAR  |
| reasons                 | JSON     |
| intervention_suggestion | LONGTEXT |
| created_at              | DATETIME |

---

## reasons JSON

```json
[
 "连续三天未学习",
 "链表掌握度下降"
]
```

---

## intervention_suggestion 示例

教师建议：

完成链表实验。

重新学习第五章。

进行 AI Tutor 一对一辅导。

---

# 第七章 growth_reports（成长报告）

## 7.1 表定位

保存 AI 自动生成成长报告。

支持 PDF 导出。

支持学期报告。

---

## 7.2 report_type

| 类型       |
| -------- |
| weekly   |
| monthly  |
| semester |
| custom   |

---

## 字段设计

| 字段              | 类型       |
| --------------- | -------- |
| id              | UUID     |
| student_id      | UUID     |
| report_type     | ENUM     |
| report_markdown | LONGTEXT |
| report_summary  | TEXT     |
| overall_score   | DECIMAL  |
| report_data     | JSON     |
| generated_by    | VARCHAR  |
| generated_at    | DATETIME |

---

## report_data JSON

```json
{
 "heatmap":"...",
 "mastery":{},
 "recommendations":[]
}
```

支持前端图表。

---

# 第八章 Learning Mirror 更新机制

## 8.1 更新触发器

Learning Mirror 更新来源：

| 来源            | 更新                 |
| ------------- | ------------------ |
| Quiz 完成       | Mastery + Mirror   |
| Homework 批改   | Mastery + Timeline |
| Experiment 完成 | Practice + Mirror  |
| AI Tutor 聊天   | AI Interaction     |
| 学习记录新增        | Engagement         |
| 每日任务          | Consistency        |

---

## 8.2 Mirror Builder 流程

Learning Records

↓

Aggregate Metrics

↓

Knowledge Mastery

↓

Risk Prediction

↓

Recommendation Engine

↓

Learning Mirror

---

# 第九章 Recommendation Engine 数据模型

推荐依据：

Learning Mirror。

Knowledge Mastery。

Timeline。

Risk Prediction。

Course Progress。

AI Chat History。

输出 Recommendation。

---

## 推荐优先级规则

High Risk。

↓

Knowledge Weakness。

↓

Upcoming Deadline。

↓

Learning Goal。

---

# 第十章 Growth Analytics 聚合规则

Analytics 聚合：

learning_records。

knowledge_mastery_records。

recommendations。

risk_predictions。

生成：

热力图。

掌握图谱。

学习曲线。

课程排名。

成长积分。

---

# 第十一章 SQLAlchemy Relationships

User

↓

LearningMirror (1:1)

User

↓

KnowledgeMasteryRecord (1:N)

User

↓

LearningTimeline (1:N)

User

↓

Recommendation (1:N)

User

↓

RiskPrediction (1:N)

User

↓

GrowthReport (1:N)

---

# 第十二章 Repository 设计（Growth）

## MirrorRepository

```
get_mirror()

refresh_mirror()

update_vector()

history()
```

---

## MasteryRepository

```
get_mastery()

update_mastery()

batch_update()

trend()
```

---

## TimelineRepository

```
append_event()

list_events()

daily_events()
```

---

## RecommendationRepository

```
generate()

list()

complete()

dismiss()
```

---

## RiskRepository

```
predict()

save_prediction()

latest_prediction()

high_risk_students()
```

---

## GrowthReportRepository

```
generate_report()

weekly_report()

semester_report()

download_report()
```

---

# 第十三章 Service 设计（Growth）

MirrorService。

MasteryService。

RecommendationService。

PredictionService。

TimelineService。

GrowthReportService。

InterventionService。

---

# 第十四章 索引设计（Growth Domain）

| 表                         | 索引                               |
| ------------------------- | -------------------------------- |
| learning_mirror           | student_id UNIQUE                |
| knowledge_mastery_records | student_id + knowledge_id UNIQUE |
| learning_timeline         | student_id + created_at          |
| recommendations           | student_id + status              |
| risk_predictions          | student_id + created_at          |
| growth_reports            | student_id + report_type         |

---

# 第十五章 Seed 初始化规范

初始化：

所有学生生成默认 Learning Mirror。

Mastery 初始化为 0。

Timeline 创建：

课程加入事件。

Recommendation 空。

Risk Low。

---

# 第十六章 Growth Domain Checklist

## Learning Mirror

- [ ] 六维状态向量
- [ ] 综合成长分
- [ ] JSON 雷达图数据

## Mastery

- [ ] 每知识点掌握度
- [ ] Confidence
- [ ] 更新次数

## Timeline

- [ ] 成长事件
- [ ] 学习积分
- [ ] AI 推荐事件

## Recommendation

- [ ] 推荐历史
- [ ] 推荐状态
- [ ] 推荐原因

## Risk Prediction

- [ ] 风险等级
- [ ] 风险原因
- [ ] 教师建议

## Growth Report

- [ ] Weekly Report
- [ ] Semester Report
- [ ] PDF 导出

---

# 第十七章 Challenge Cup 创新点映射（数据库层）

## 创新点一：Learning State Mirror

数据库保存六维学习状态向量。

支持实时刷新。

支持雷达图。

---

## 创新点二：Knowledge Mastery Graph

知识点级掌握度数据库。

支持知识图谱。

支持 AI 推荐。

---

## 创新点三：Risk Prediction

风险预测数据库。

教师查看风险学生。

AI 自动干预。

---

## 创新点四：Recommendation Engine

推荐历史可追踪。

推荐效果可评估。

形成学习闭环。

---

# 第十八章 本章开发成果

Growth Domain 完成后，ProgramMind V2.0 将具备：

- Learning State Mirror 数据库。
- 知识掌握图谱数据库。
- AI 推荐数据库。
- 学习风险预测数据库。
- 成长时间轴数据库。
- AI 成长报告数据库。

Growth Center 至此形成完整的数据闭环，为 DOC04 Growth API、Dashboard、Learning Mirror 页面提供全部数据来源。
