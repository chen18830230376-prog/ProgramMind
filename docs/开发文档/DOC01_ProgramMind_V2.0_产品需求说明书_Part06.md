# ProgramMind V2.0 产品需求说明书（PRD）

# Part 06 —— 第十二章 页面交互规范（UI / UX Specification）

> 本章节定义 ProgramMind 全部页面统一交互规范、组件规范、状态规范、设计规范，是 Vue 前端开发唯一 UI 标准。

---

# 第十二章 页面交互规范（UI / UX Specification）

## 12.1 UI 设计原则

ProgramMind UI 遵循五项原则。

### AI Native（AI 原生）

AI 不作为一个聊天窗口存在，而是嵌入每个页面。

例如：

- Homework 页面有 AI Tutor。
- Experiment 页面有 AI Debug。
- Analytics 页面有 AI Summary。

AI 永远作为当前任务助手存在。

---

### Workspace First（工作台优先）

登录后直接进入工作台。

工作台承担：

- 今日任务
- AI 推荐
- 通知
- 快捷入口

所有页面都可以回到 Workspace。

---

### Card First（卡片式设计）

页面全部采用 Card Layout。

禁止复杂弹窗堆叠。

统一：

- Card Header
- Card Body
- Card Footer

---

### Progressive Disclosure（渐进展示）

复杂信息默认折叠。

例如：

- AI Citation 默认折叠。
- Prompt 默认隐藏。
- Workflow 日志默认折叠。

---

### Dark / Light 双主题

所有页面必须支持：

- Light Theme
- Dark Theme

主题切换即时生效。

---

# 第一部分 页面布局规范

## 12.2 全局页面布局

ProgramMind 全局布局固定。

```text
App Layout
│
├── Sidebar
├── Header
├── Breadcrumb
├── Page Container
└── Footer（可选）
```

页面宽度：

- 最大 1440px
- 默认内容宽度 1280px

---

## 12.3 Sidebar 规范

宽度：

```text
Collapsed：72px

Expanded：248px
```

菜单层级：

一级菜单：

- Workspace
- Learning
- Teaching
- AI Center
- Growth
- Profile

二级菜单展开。

支持折叠。

---

### Sidebar 行为

Hover 展开 Tooltip。

点击一级菜单展开。

支持记忆状态（LocalStorage）。

---

## 12.4 Header 规范

Header 包含：

```text
Logo

Search

Notification

Theme Switch

Avatar Menu
```

高度：

72px。

固定顶部。

---

### Header Search

支持搜索：

- Course
- Homework
- Experiment
- Quiz
- AI History
- Knowledge Base

实时搜索。

---

### Notification Icon

显示 Badge。

点击 Drawer。

Drawer 内容：

- 全部通知。
- 分类通知。
- 已读。

---

### Avatar Menu

菜单项：

- Profile
- AI Settings
- Theme
- Logout

---

## 12.5 Breadcrumb

格式：

```text
Workspace / Learning / Homework
```

自动生成。

支持点击返回。

---

# 第二部分 通用组件规范

## 12.6 Button（按钮规范）

按钮统一四种类型。

| 类型        | 用途    |
| --------- | ----- |
| Primary   | 主操作   |
| Secondary | 次操作   |
| Success   | 完成/提交 |
| Danger    | 删除    |

统一尺寸：

- Large
- Default
- Small

禁止自定义颜色。

---

### Loading Button

点击后：

显示 Spinner。

禁止重复点击。

自动恢复。

---

## 12.7 Card 组件规范

统一 Card。

Header：

标题、副标题、操作按钮。

Body：

内容区域。

Footer：

统计信息。

统一圆角：

24px。

---

## 12.8 Dialog 规范

Dialog 最大宽度：

960px。

必须支持：

- ESC
- 点击遮罩关闭（危险操作除外）
- Loading
- Confirm

---

### 常见 Dialog

| Dialog    |
| --------- |
| 创建课程      |
| 创建作业      |
| 创建实验      |
| 创建 Quiz   |
| 编辑 Prompt |

---

## 12.9 Drawer 规范

Drawer 用于展示详情。

例如：

- Homework Detail
- Experiment Detail
- Notification Detail
- Citation Detail

宽度：

520px。

---

## 12.10 Tabs 规范

统一 Tabs。

支持：

- Underline Style
- Segment Style

默认缓存状态。

---

## 12.11 Table 规范

统一 Table。

支持：

- 排序
- 搜索
- 筛选
- 分页
- Empty State

行点击进入详情。

---

## 12.12 Form 规范

所有 Form 使用统一组件。

字段状态：

- Default
- Focus
- Error
- Disabled
- Success

提交失败必须定位错误字段。

---

# 第三部分 AI 页面交互规范

## 12.13 AI Chat Window

聊天窗口布局：

```text
Message List

Streaming Message

Citation Drawer

Input Box
```

---

### Message 类型

| 类型        |
| --------- |
| User      |
| Assistant |
| System    |

支持头像。

支持时间。

---

### Streaming 输出

逐 Token 输出。

状态：

- Thinking
- Searching
- Generating
- Finished

支持 Stop。

---

## 12.14 Citation 展示规范

AI 回答下方展示来源。

样式：

```text
📚 Python教材 第四章

PPT 第12页

实验指导 第二节
```

点击打开 Drawer。

Drawer 展示 Chunk。

---

## 12.15 Prompt Drawer

教师模式支持查看 Prompt。

Drawer 内容：

- System Prompt
- User Prompt
- Context
- Chunk

仅教师可见。

---

## 12.16 AI Workflow Timeline

Workflow 页面展示 Timeline。

步骤：

- Waiting
- Running
- Success
- Failed

每一步显示：

- Agent
- Duration
- Token
- Retry

---

## 12.17 AI Markdown Renderer

AI 输出支持：

- Markdown
- Code Highlight
- Table
- MathJax
- Mermaid（预留）

禁止使用 v-html 原始渲染。

统一 Markdown Renderer。

---

# 第四部分 上传组件规范

## 12.18 Upload 组件

统一 Upload。

支持拖拽。

显示上传进度。

限制：

| 类型  | 大小   |
| --- | ---- |
| 图片  | 5MB  |
| PDF | 20MB |
| PPT | 30MB |
| ZIP | 50MB |

---

### 上传状态

- Waiting
- Uploading
- Success
- Failed

失败支持 Retry。

---

## 12.19 File Preview

图片支持：

- Zoom
- Rotate
- Fullscreen

PDF：

页码浏览。

PPT：

缩略图浏览。

Markdown：

代码高亮。

---

# 第五部分 图表规范

## 12.20 图表统一规范

所有图表使用 ECharts。

统一封装。

禁止页面重复初始化。

---

### 图表颜色

Primary：

ProgramMind Blue。

Success：

Green。

Warning：

Orange。

Danger：

Red。

---

## 12.21 Radar Chart

Growth Dashboard。

统一六维能力。

Hover 显示数值。

---

## 12.22 HeatMap

学习热力图。

支持：

- 年份切换。
- Hover 日期详情。

颜色连续变化。

---

## 12.23 Knowledge Graph

知识图谱。

支持：

- Zoom
- Drag
- Highlight Neighbor
- Click Node

点击节点打开 Drawer。

---

## 12.24 Analytics Dashboard

教师分析页面。

图表：

- Completion Bar
- Mastery Radar
- Score Distribution
- Behavior Pie
- Risk Scatter

统一 Tooltip。

---

# 第六部分 Loading / Empty / Error 状态规范

## 12.25 Skeleton

所有页面必须有 Skeleton。

类型：

- Card Skeleton
- Table Skeleton
- Chart Skeleton
- Chat Skeleton

---

## 12.26 Empty State

统一 Empty 页面。

展示：

- Illustration
- Title
- Description
- Action Button

例如：

暂无课程。

去课程广场。

---

## 12.27 Error State

统一 Error 页面。

支持：

- Retry
- Back Workspace

错误类型：

- Network
- Permission
- Server
- Unknown

---

## 12.28 Loading State Machine

统一生命周期。

```text
Loading

↓

Success

↓

Refresh

↓

Loading
```

Error 不覆盖页面数据。

---

# 第七部分 页面状态规范

## 12.29 Homework 页面状态

状态：

- Not Started
- Draft
- Submitted
- Graded
- Returned

颜色统一。

---

## 12.30 Experiment 状态

状态：

- Locked
- Available
- Draft
- Submitted
- Graded

支持 Deadline Countdown。

---

## 12.31 Quiz 状态

状态：

- Upcoming
- Available
- Running
- Submitted
- Finished

Running 显示 Timer。

---

## 12.32 AI 页面状态

状态：

- Idle
- Typing
- Searching
- Streaming
- Completed
- Error

顶部展示 AI Status Badge。

---

# 第八部分 Growth 页面交互规范

## 12.33 Growth Dashboard

组件：

- Level Card
- Radar
- Timeline
- Badge Wall

点击 Badge 查看详情。

---

## 12.34 Mastery Tree

知识树支持展开。

颜色：

- Master
- Good
- Learning
- Weak

Hover 查看来源。

---

## 12.35 Learning Timeline

时间轴按天展示。

事件颜色区分：

Homework。

Quiz。

Experiment。

AI。

---

## 12.36 Risk Center

风险学生列表。

教师支持：

点击学生进入分析。

学生只能查看自己。

---

## 12.37 Learning Path

路径节点展示：

- 学习目标
- 推荐资料
- 推荐实验
- 推荐 Quiz

点击跳转页面。

---

# 第九部分 搜索体验规范

## 12.38 Global Search

输入实时联想。

分类：

- Courses
- Homework
- Quiz
- Experiment
- AI History
- Knowledge

键盘上下选择。

Enter 跳转。

---

## 12.39 Filter Panel

支持筛选：

课程。

时间。

标签。

状态。

---

# 第十部分 响应式规范

## 12.40 Breakpoint

| Breakpoint | Width |
| ---------- | ----- |
| XL         | ≥1440 |
| LG         | ≥1200 |
| MD         | ≥992  |
| SM         | ≥768  |
| XS         | ＜768  |

---

### Sidebar 响应

MD 以下折叠。

Drawer 全屏。

---

### Table 响应

移动端自动转 Card。

---

### Chart 响应

Resize Observer 自动更新。

---

# 第十一部分 动效规范

## 12.41 Page Transition

页面进入：

Fade + Slide。

持续：

240ms。

---

## 12.42 Card Hover

Hover：

Elevation + Shadow。

禁止 Scale 超过 1.02。

---

## 12.43 AI Streaming Cursor

输出末尾显示 Cursor。

完成自动消失。

---

## 12.44 Workflow Animation

Agent 节点依次点亮。

失败节点红色。

成功节点绿色。

---

# 第十二部分 可访问性规范

## 12.45 Keyboard Navigation

支持：

- Tab
- Shift+Tab
- Enter
- ESC

---

## 12.46 Focus Style

统一 Focus Ring。

蓝色描边。

---

## 12.47 ARIA

Icon Button 必须有 aria-label。

Dialog 必须有标题。

---

# 第十三部分 页面设计 Token（Design Token）

## 12.48 Color Token

品牌色：

- Primary
- Success
- Warning
- Danger
- Info

统一 CSS Variables。

---

## 12.49 Radius Token

统一：

- XS
- SM
- MD
- LG
- XL
- 2XL

Card 使用 XL。

---

## 12.50 Shadow Token

统一三级阴影。

禁止页面自定义。

---

## 12.51 Typography Token

字体等级：

H1。

H2。

H3。

Body。

Caption。

Code。

---

## 12.52 Space Token

统一间距系统：

4。

8。

12。

16。

24。

32。

48。

64。

---

# 第十四部分 页面开发 Checklist

## 12.53 每个页面必须包含

- Breadcrumb。
- Page Header。
- Loading。
- Empty。
- Error。
- Permission。
- Retry。
- Responsive。

---

## 12.54 AI 页面必须包含

- Streaming。
- Citation。
- History。
- Token。
- Retry。
- Stop Generate。

---

## 12.55 Growth 页面必须包含

- Course Filter。
- Time Filter。
- Chart Resize。
- Detail Drawer。

---

## 12.56 Teacher 页面必须包含

- Permission Verify。
- Publish Flow。
- Draft Save。
- Notification Trigger。

---

## 12.57 Student 页面必须包含

- Deadline。
- Progress。
- Growth Update。
- AI Recommendation。

---

# 本章总结

本章节统一定义 ProgramMind V2.0 全部 UI / UX 标准：

- 全局布局规范。
- Sidebar/Header/Breadcrumb。
- Card/Dialog/Drawer/Table/Form。
- AI Chat 规范。
- Workflow Timeline。
- Markdown Renderer。
- Upload/File Preview。
- ECharts 图表规范。
- Loading/Empty/Error 状态机。
- Growth Center 交互规范。
- Search 规范。
- Responsive 规范。
- Animation Token。
- Design Token。
- Page Checklist。

所有 Vue 页面必须严格遵循本章节规范开发。

---

# DOC01 完成说明

《DOC01 ProgramMind V2.0 产品需求说明书》至此全部完成，共 **6 个 Part**：

| Part   | 内容                                                |
| ------ | ------------------------------------------------- |
| Part01 | 项目背景、产品定位、用户体系、信息架构（57页面）                         |
| Part02 | Learning Center 全部页面规格（18页面）                      |
| Part03 | Teaching Center 全部页面规格（22页面）                      |
| Part04 | AI Center（11页面）+ Growth Center（6页面）规格             |
| Part05 | 全局业务流程（Teacher/Student/RAG/Workflow/State Engine） |
| Part06 | UI/UX 页面交互规范、组件规范、状态规范、Design Token               |

整个 DOC01 是 **ProgramMind V2.0 唯一产品设计文档（完整版 PRD）**，约 120 页 Markdown，可直接作为团队开发依据。
