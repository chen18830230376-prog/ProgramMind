# ProgramMind V2.0 产品需求说明书（PRD）

# Part 04 —— 第九章 AI Center 与 Growth Center 页面规格

> 本章节定义 ProgramMind AI Center（AI 原生能力中心）与 Growth Center（学习状态镜像中心）的全部页面规格，是 AI 成员、算法成员以及前端开发的重要依据。

---

# 第九章 AI Center（AI 原生能力中心）

## 9.1 AI Center 产品定位

AI Center 是 ProgramMind 的 AI 能力中枢。

区别于普通聊天机器人，它负责：

- 学科知识问答（RAG）
- 多智能体工作流（Multi-Agent）
- AI 文档生成
- AI 教学助手
- AI 学习助手
- AI 课程资源助手

AI Center 面向 **教师、学生** 两种角色开放，但根据身份展示不同能力。

---

## 9.2 AI Center 页面地图（11 页面）

```text
AI Center
│
├── AI1 AI 工作台
├── AI2 AI 知识问答（RAG Tutor）
├── AI3 AI 文档助手
├── AI4 AI 工作流中心
├── AI5 AI 教案助手
├── AI6 AI PPT 助手
├── AI7 AI 命题助手
├── AI8 AI 总结助手
├── AI9 AI Prompt Studio
├── AI10 AI 历史记录
└── AI11 AI 设置中心
```

共 **11 个页面**。

---

# 页面 AI1 —— AI 工作台（AI Workspace）

## 页面定位

AI Center 首页。

提供 ProgramMind 所有 AI 能力入口。

路由：

```text
/ai
```

---

## 页面布局

```text
AI Workspace
│
├── AI 今日建议
├── AI 快捷工具
├── AI Workflow
├── 最近 AI 会话
├── AI 使用统计
└── 推荐智能体
```

---

## 模块一：AI 今日建议

根据角色生成建议。

教师示例：

> 今天建议为 Python 程序设计课程生成实验二教案。

学生示例：

> 今天建议复习递归与回溯算法。

支持一键执行。

---

## 模块二：快捷工具

展示 AI 卡片。

| 工具         | 描述    |
| ---------- | ----- |
| AI Tutor   | 课程问答  |
| AI Lesson  | 教案生成  |
| AI PPT     | PPT生成 |
| AI Quiz    | 智能命题  |
| AI Summary | 总结助手  |
| AI Debug   | 代码调试  |
| AI Review  | 学习规划  |

点击进入对应页面。

---

## 模块三：AI Workflow

展示最近运行工作流。

字段：

| 字段          |
| ----------- |
| Workflow 名称 |
| 状态          |
| 执行时间        |
| 使用 Agent 数  |
| Token 数     |

支持查看详情。

---

## 模块四：最近 AI 会话

展示最近聊天。

支持继续会话。

---

## 模块五：AI 使用统计

图表：

- 今日 AI 次数
- 本周 Token 使用
- AI 工具使用排行

---

# 页面 AI2 —— AI 知识问答（RAG Tutor）

路由：

```text
/ai/rag
```

产品定位：

课程知识增强问答页面。

这是 ProgramMind 最重要 AI 页面。

---

## 页面布局

```text
课程选择
│
章节定位
│
聊天窗口
│
引用来源
│
知识上下文
```

---

## 输入区域

字段：

| 字段    | 描述       |
| ----- | -------- |
| 当前课程  | Python   |
| 当前章节  | 函数       |
| 问题输入框 | Markdown |

支持：

- 图片
- PDF
- PPT
- Word
- 代码

---

## AI 回复区域

回复包括：

### 回答内容

Markdown。

数学公式。

代码高亮。

---

### 引用来源（Citation）

每条回答展示来源。

示例：

| 来源           | 类型       |
| ------------ | -------- |
| Python教材 第四章 | PDF      |
| 第12页 PPT     | PPT      |
| 实验指导 第二节     | Markdown |
| 课堂讲义         | TXT      |

点击跳转来源。

---

### 知识上下文 Drawer

展示：

- TopK Chunk。
- Chunk 来源。
- Chunk 相似度。

支持展开。

---

## AI 参数

高级模式支持：

| 参数          |
| ----------- |
| TopK        |
| Temperature |
| Retriever   |
| 是否引用来源      |
| 是否联网（预留）    |

---

## 页面状态

支持 Streaming 输出。

支持停止生成。

支持重新生成。

---

# 页面 AI3 —— AI 文档助手

路由：

```text
/ai/document
```

定位：

AI Document Agent。

---

## 页面能力

支持生成：

- Markdown。
- Word。
- 实验报告。
- 学习笔记。
- 课程总结。
- PPT 文案。

---

## 页面布局

```text
模板选择
│
Prompt编辑器
│
AI输出
│
文档编辑器
```

---

## 模板类型

| 模板    |
| ----- |
| 学习笔记  |
| 实验报告  |
| 教案    |
| PPT文案 |
| 总结    |
| 思维导图  |

支持保存模板。

---

## AI 输出

支持 Markdown 编辑。

支持导出：

- Markdown
- DOCX
- PDF

---

# 页面 AI4 —— AI 工作流中心（Workflow Center）

路由：

```text
/ai/workflow
```

产品定位：

ProgramMind Multi-Agent 可视化页面。

---

## 页面布局

```text
Workflow列表
│
创建Workflow
│
Workflow详情
│
运行日志
```

---

## Workflow 卡片

字段：

| 字段         |
| ---------- |
| Workflow名称 |
| Agent数量    |
| 创建时间       |
| 最近运行       |
| 成功率        |

---

## Workflow 详情

展示 DAG。

```text
Planner
  ↓
Lesson Agent
  ↓
PPT Agent
  ↓
Quiz Agent
  ↓
Summary Agent
```

展示执行时间轴。

---

## Workflow 日志

每一步展示：

- Agent。
- Prompt。
- 输出。
- Token。
- 状态。

支持重试失败节点。

---

# 页面 AI5 —— AI 教案助手

路由：

```text
/ai/lesson
```

Teacher 专属。

与 Teaching Center 共用页面能力。

新增：

Agent 运行轨迹。

支持查看 Prompt。

---

# 页面 AI6 —— AI PPT 助手

路由：

```text
/ai/ppt
```

新增：

支持 AI 自动配图建议。

支持 AI 动画建议。

支持 AI 页面排序建议。

---

# 页面 AI7 —— AI 命题助手

路由：

```text
/ai/question
```

定位：

Quiz Agent 独立入口。

支持：

- 章节命题。
- 知识点命题。
- Bloom 分类命题。
- AI 自动解析。

---

# 页面 AI8 —— AI 总结助手

路由：

```text
/ai/summary
```

定位：

Summary Agent。

支持总结：

- PDF。
- PPT。
- Markdown。
- Word。
- 学习记录。
- AI 对话。

输出：

摘要 + 思维导图。

---

# 页面 AI9 —— Prompt Studio

路由：

```text
/ai/prompts
```

定位：

Prompt 模板中心。

---

## 页面布局

```text
模板列表
│
Prompt编辑器
│
变量配置
│
测试区域
```

---

支持：

- Lesson Prompt。
- Tutor Prompt。
- Quiz Prompt。
- Summary Prompt。

教师可创建课程 Prompt。

---

# 页面 AI10 —— AI 历史记录

路由：

```text
/ai/history
```

定位：

AI Conversation Center。

展示：

- 会话列表。
- 收藏。
- 删除。
- 搜索。
- 分类。

支持继续聊天。

---

# 页面 AI11 —— AI 设置中心

路由：

```text
/ai/settings
```

配置 AI。

支持：

| 配置          |
| ----------- |
| 默认模型        |
| Temperature |
| TopK        |
| 引用来源        |
| Streaming   |
| Memory 开关   |

教师可配置课程 AI。

学生只能配置个人 AI。

---

# AI Center 页面索引

| 编号   | 页面                    |
| ---- | --------------------- |
| AI1  | AI Workspace          |
| AI2  | AI Tutor（RAG）         |
| AI3  | AI Document Assistant |
| AI4  | Workflow Center       |
| AI5  | Lesson Agent          |
| AI6  | PPT Agent             |
| AI7  | Quiz Agent            |
| AI8  | Summary Agent         |
| AI9  | Prompt Studio         |
| AI10 | Conversation History  |
| AI11 | AI Settings           |

---

# 第十章 Growth Center（学习状态镜像中心）

## 10.1 Growth Center 产品定位

Growth Center 是 ProgramMind 的学习状态镜像中心（State Engine）。

目标：

持续记录学生学习行为，构建成长画像。

Growth Center 不属于 AI Chat。

它属于 AI + Learning Analytics。

---

## 10.2 Growth Center 页面地图（6 页面）

```text
Growth Center
│
├── G1 成长首页
├── G2 掌握度画像
├── G3 学习热力图
├── G4 学习行为分析
├── G5 风险预测中心
└── G6 学习路径推荐
```

---

# 页面 G1 —— 成长首页（Growth Dashboard）

路由：

```text
/growth
```

定位：

成长中心首页。

---

## 页面布局

```text
成长卡片
│
能力雷达
│
成长时间轴
│
学习统计
│
AI成长建议
```

---

## 成长卡片

展示：

| 字段    |
| ----- |
| 当前等级  |
| 学习积分  |
| 连续学习  |
| 总学习时间 |

成长等级：

- Beginner
- Explorer
- Builder
- Master

---

## 能力雷达

六维能力：

| 能力     |
| ------ |
| 理论掌握   |
| 编程能力   |
| 实验能力   |
| 学习效率   |
| AI使用能力 |
| 综合能力   |

点击查看详情。

---

## 成长时间轴

展示成长事件。

例如：

- 完成实验。
- 完成测验。
- AI Tutor 学习。
- 获得成长徽章。

---

## AI 成长建议

AI 自动生成：

下一步学习建议。

---

# 页面 G2 —— 掌握度画像（Knowledge Mastery）

路由：

```text
/growth/mastery
```

定位：

知识掌握地图。

---

## 页面布局

```text
课程切换
│
章节树
│
知识点掌握度
│
推荐学习
```

---

## 知识树

展示：

```text
Python
├── 函数
├── 递归
├── 文件IO
├── 面向对象
```

每个知识点颜色表示掌握程度。

---

## 掌握度卡片

字段：

| 字段      |
| ------- |
| Mastery |
| 最近更新    |
| 来源行为    |
| 推荐练习    |

点击查看学习记录。

---

# 页面 G3 —— 学习热力图（Learning HeatMap）

路由：

```text
/growth/heatmap
```

定位：

365 天学习热力图。

---

## 页面布局

```text
学习热力图
│
时间统计
│
学习习惯分析
```

---

## 热力图

颜色：

- 深蓝：学习时间长。
- 浅蓝：学习时间少。
- 灰色：未学习。

支持年度切换。

---

## 学习统计

统计：

- 每日学习时间。
- 每周学习时间。
- 每月趋势。

---

# 页面 G4 —— 学习行为分析（Behavior Analytics）

路由：

```text
/growth/behavior
```

定位：

学习行为统计。

---

## 页面布局

```text
行为分类
│
课程投入
│
AI使用统计
│
行为时间轴
```

---

## 行为分类

展示比例：

- Homework
- Quiz
- Experiment
- AI Tutor
- Reading

---

## AI 使用统计

统计：

- AI Tutor 次数。
- AI Debug 次数。
- AI Review 次数。

---

# 页面 G5 —— 风险预测中心（Risk Prediction）

路由：

```text
/growth/risk
```

定位：

学习风险分析。

---

## 页面布局

```text
风险等级
│
风险知识点
│
风险行为
│
AI干预建议
```

---

## 风险等级

颜色：

- Green
- Yellow
- Orange
- Red

展示风险原因。

---

## AI 干预建议

输出：

- 推荐课程。
- 推荐实验。
- 推荐 Quiz。
- 推荐 Tutor。

---

# 页面 G6 —— 学习路径推荐（Learning Path）

路由：

```text
/growth/path
```

定位：

AI 学习路径生成器。

---

## 页面布局

```text
目标设置
│
学习路径
│
阶段目标
│
推荐资源
```

---

## 学习路径

例如：

```text
Python基础
   ↓
函数
   ↓
递归
   ↓
回溯
   ↓
项目实践
```

每一步展示：

- 学习目标。
- 推荐资料。
- 推荐实验。
- 推荐 Quiz。

---

## AI 推荐资源

来自：

- 知识库。
- Homework。
- Experiment。
- Tutor。

形成完整路径。

---

# Growth Center 页面索引

| 编号  | 页面                 |
| --- | ------------------ |
| G1  | Growth Dashboard   |
| G2  | Knowledge Mastery  |
| G3  | Learning HeatMap   |
| G4  | Behavior Analytics |
| G5  | Risk Prediction    |
| G6  | Learning Path      |

---

# AI Center × Growth Center 权限矩阵

| 页面               | Teacher | Student |
| ---------------- | ------- | ------- |
| AI Workspace     | ✅       | ✅       |
| AI Tutor         | ✅       | ✅       |
| AI Workflow      | ✅       | ❌       |
| Prompt Studio    | ✅       | ❌       |
| AI Settings      | ✅       | ✅       |
| Growth Dashboard | 查看班级    | 查看个人    |
| Risk Prediction  | 查看班级    | 查看个人    |
| Learning Path    | 查看班级建议  | 查看个人建议  |

---

## 页面设计规范（AI/Growth）

所有 AI、Growth 页面必须满足：

### AI 页面

- Markdown 输出
- Streaming 输出
- Citation 来源
- AI 历史记录
- Token 状态
- Loading Skeleton
- Retry

### Growth 页面

- 所有图表支持课程切换。
- 所有图表支持时间范围切换。
- 图表点击进入详情。
- 所有成长建议均支持跳转对应课程。

---

**Part 04 结束。**

下一部分（Part 05）进入 **第十一章 全局交互流程设计**，包括教师端完整业务流程、学生端完整学习闭环、多智能体 Workflow 流程、RAG 检索流程、成长状态流转流程，共 20+ 个 Mermaid 流程图，是整个 PRD 最重要的一章。
