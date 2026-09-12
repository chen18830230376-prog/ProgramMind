# ProgramMind V2.0 后端开发规范

# Part07.4B —— Growth Report Engine 与 Teacher Analytics Engine（Learning Mirror 最终章）

> 文档版本：V2.0
> 更新时间：2026-09
> 模块负责人：AI（Growth Analytics Engine）
> 技术栈：FastAPI + SQLAlchemy + LangGraph + Markdown + ReportLab（PDF）

---

# 第一章 Growth Report Engine 模块定位

## 1.1 模块职责

Growth Report Engine 用于自动生成学生成长分析报告。

支持：

- AI 周报
- AI 月报
- AI 学期成长报告
- AI 学习总结
- 教师成长报告

输出 Markdown，可转换 PDF。

---

## 1.2 Growth Report 数据来源

Learning Mirror

Knowledge Mastery

Risk Prediction

Recommendation

Timeline

Learning Records

Conversation Summary

↓

Growth Report Builder

---

## 1.3 Report 生命周期

Scheduler

↓

Analytics Builder

↓

Prompt Builder

↓

AI Report Generator

↓

Markdown Report

↓

PDF Export（可选）

---

# 第二章 Growth Report 目录结构

## 2.1 growth/reports/

reports/

report_engine.py

weekly_report_builder.py

monthly_report_builder.py

semester_report_builder.py

report_prompt_builder.py

report_repository.py

pdf_exporter.py

---

## 2.2 Report 类型

| 类型              | 周期   |
| --------------- | ---- |
| Weekly Report   | 每周   |
| Monthly Report  | 每月   |
| Semester Report | 每学期  |
| Manual Report   | 手动生成 |

统一 Report Engine。

---

# 第三章 Weekly Report Builder

## 3.1 Weekly Report 内容结构

固定八个部分：

1. 本周学习概览
2. 六维状态变化
3. 知识掌握提升
4. 风险变化
5. 学习行为分析
6. AI Tutor 使用情况
7. 推荐完成情况
8. 下周学习建议

---

## 3.2 Weekly Overview JSON

字段：

overall_score_delta

study_hours

quiz_count

homework_completion

risk_change

recommendation_completion

---

## 3.3 学习行为统计

统计：

学习总时长。

学习天数。

最长连续学习。

课程访问次数。

实验次数。

AI Tutor 次数。

---

# 第四章 Weekly Mirror Analysis

## 4.1 六维变化分析

输出：

本周 vs 上周。

每一维变化值。

---

## 4.2 JSON 输出

```json
{
 "mastery":{
    "current":0.78,
    "delta":0.05
 }
}
```

Radar Trend 使用。

---

## 4.3 自动生成分析文字

例如：

> 本周知识掌握度提升 5%，主要来自 Python 链表章节测验。

AI 自动生成。

---

# 第五章 Knowledge Growth Analysis

## 5.1 掌握增长分析

统计：

新增掌握知识点。

恢复掌握知识点。

下降知识点。

遗忘知识点。

---

## 5.2 输出

Top5 提升。

Top5 下降。

HeatMap 差异。

---

## 5.3 Weak Knowledge Summary

输出：

薄弱知识列表。

原因。

建议。

预计学习时间。

---

# 第六章 Risk Analysis Report

## 6.1 风险变化分析

Risk Score。

Risk Trend。

Risk Factor。

---

## 6.2 输出字段

当前风险。

变化幅度。

风险原因。

AI 干预效果。

---

## 6.3 示例 Markdown

> 本周学习风险由 Medium 降至 Low，主要原因是完成了链表专项测验并恢复连续学习。

---

# 第七章 Recommendation Completion Analysis

## 7.1 推荐完成率

统计：

推荐数量。

完成数量。

忽略数量。

完成率。

---

## 7.2 推荐效果

完成推荐后：

Mastery 提升。

Risk 下降。

形成效果分析。

---

## 7.3 输出 JSON

```json
{
 "completion_rate":0.82,
 "completed":9,
 "ignored":2
}
```

---

# 第八章 AI Tutor Learning Summary

## 8.1 AI 学习分析

统计：

Tutor 次数。

平均 Session 时间。

AI Quiz 次数。

AI Coding 次数。

---

## 8.2 Conversation Summary

自动摘要：

学习主题。

高频问题。

重点知识。

AI 自动总结。

---

## 8.3 AI Learning Preference

输出：

喜欢代码示例。

喜欢图解。

喜欢练习。

长期 Memory 来源。

---

# 第九章 Monthly Report Builder

## 9.1 月报结构

包括：

学习统计。

课程统计。

成长趋势。

Mastery 趋势。

Risk 趋势。

推荐分析。

学习建议。

---

## 9.2 月趋势分析

四周趋势。

学习投入变化。

课程变化。

掌握变化。

---

## 9.3 月成长总结

AI 自动生成 Markdown。

长度：

600~1000 字。

---

# 第十章 Semester Report Builder

## 10.1 学期报告定位

ProgramMind 最大报告。

用于课程总结。

---

## 10.2 报告结构

课程表现。

学习行为。

知识掌握。

实验能力。

风险变化。

成长建议。

AI Tutor 总结。

---

## 10.3 输出格式

Markdown。

PDF。

教师下载。

学生下载。

---

# 第十一章 Report Prompt Builder

## 11.1 Prompt Builder 输入

Mirror。

Mastery。

Risk。

Timeline。

Recommendation。

Conversation Summary。

---

## 11.2 Prompt 输出

成长分析 Prompt。

课程总结 Prompt。

教师建议 Prompt。

学生建议 Prompt。

---

## 11.3 Prompt Version

独立 Prompt Registry。

report_v2。

可后台更新。

---

# 第十二章 PDF Export Engine

## 12.1 PDF 导出定位

Markdown 转 PDF。

使用 ReportLab。

---

## 12.2 PDF 内容

封面。

目录。

统计卡片。

图表占位。

成长分析。

建议。

附录。

---

## 12.3 导出规范

A4。

分页。

页码。

ProgramMind Logo（预留）。

---

# 第十三章 Teacher Analytics Engine 定位

## 13.1 教师分析中心职责

分析整个班级学习状态。

支持教师查看：

班级整体。

课程整体。

章节整体。

学生个人。

---

## 13.2 Teacher Analytics 数据来源

所有学生 Mirror。

Mastery。

Risk。

Timeline。

Recommendation。

聚合统计。

---

# 第十四章 Class Knowledge Matrix

## 14.1 知识掌握矩阵

二维矩阵：

学生 × 知识点。

颜色表示掌握度。

---

## 14.2 Matrix 输出

knowledge_name。

student_count。

average_mastery。

weak_students。

---

## 14.3 Dashboard HeatMap

教师端 HeatMap。

支持筛选：

章节。

班级。

课程。

---

# 第十五章 Class Risk Analytics

## 15.1 风险分布

统计：

Low。

Medium。

High。

Critical。

---

## 15.2 Risk Distribution JSON

```json
{
 "low":18,
 "medium":10,
 "high":4,
 "critical":1
}
```

Pie Chart 使用。

---

## 15.3 高风险学生列表

输出：

Risk Score。

Risk Trend。

原因。

建议干预。

---

# 第十六章 Class Ranking Analytics

## 16.1 Top10 Students

综合成长分 Top10。

学习投入 Top10。

掌握增长 Top10。

---

## 16.2 Bottom10 Students

风险 Top10。

掌握下降 Top10。

连续学习中断 Top10。

教师重点关注。

---

## 16.3 排行字段

姓名。

成长分。

风险。

掌握率。

学习时长。

---

# 第十七章 Teaching Analytics Builder

## 17.1 教学分析定位

自动生成教师教学建议。

---

## 17.2 输出内容

班级薄弱章节。

班级知识覆盖率。

实验完成率。

Quiz 表现。

推荐教学重点。

---

## 17.3 AI Teaching Suggestion

Markdown 输出。

例如：

> 建议下一次课堂重点讲解链表插入与删除操作，并增加一次专项实验。

---

# 第十八章 Teacher Report Builder

## 18.1 班级成长报告

输出：

班级概览。

风险分析。

知识掌握分析。

学习行为分析。

教学建议。

---

## 18.2 JSON 数据

overview。

risk_distribution。

heatmap。

top_students。

bottom_students。

teaching_suggestion。

---

## 18.3 导出 PDF

教师下载：

班级成长报告。

课程成长报告。

学期分析报告。

---

# 第十九章 Growth Analytics API

## API 列表

| API                       | 描述     |
| ------------------------- | ------ |
| /growth/dashboard         | 学生成长中心 |
| /growth/report/weekly     | 周报     |
| /growth/report/monthly    | 月报     |
| /growth/report/semester   | 学期报告   |
| /growth/teacher/dashboard | 教师分析中心 |
| /growth/teacher/report    | 班级成长报告 |

对应 DOC04 API。

---

# 第二十章 Growth Analytics Checklist

## Dashboard

- [ ] Student Dashboard
- [ ] Overview Cards
- [ ] Radar
- [ ] HeatMap
- [ ] Timeline
- [ ] Trend Charts

## Report

- [ ] Weekly Report
- [ ] Monthly Report
- [ ] Semester Report
- [ ] PDF Export

## Teacher Analytics

- [ ] Knowledge Matrix
- [ ] Risk Distribution
- [ ] Top/Bottom Ranking
- [ ] Teaching Suggestion
- [ ] Class Report

---

# 第二十一章 Learning Mirror Engine 最终成果

完成 Part07.1 ~ Part07.4 后，ProgramMind Learning Mirror Engine 完整具备：

- 六维学习状态镜像（Mirror）。
- Knowledge Mastery Engine。
- Forgetting Curve。
- Confidence 模型。
- HeatMap 与 Review Queue。
- Risk Prediction Engine。
- Recommendation Engine。
- Growth Dashboard。
- AI 周报/月报/学期成长报告。
- Teacher Analytics Center。
- 完整 AI 学习预测—干预—分析闭环。
