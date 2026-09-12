# ProgramMind V2.0 系统总体设计说明书（SDS）

# Part 02 —— 前端架构设计（Frontend Architecture Specification）

> 面向开发成员：前端负责人（Vue 开发）
> 
> 技术栈：Vue3 + Vite + Pinia + Vue Router + Element Plus + Axios + ECharts + TailwindCSS

---

# 第九章 前端总体架构

## 9.1 前端设计目标

ProgramMind V2.0 前端需要满足以下目标：

| 目标           | 描述                                     |
| ------------ | -------------------------------------- |
| 页面组件化        | 所有页面采用 Vue SFC（Single File Component）。 |
| 模块独立         | Learning、Teaching、AI、Growth 四大模块互不影响。  |
| 状态统一         | Pinia 管理全局状态。                          |
| API 解耦       | 所有请求统一 Axios，不允许页面直接 fetch。            |
| UI 统一        | Design Token、主题、颜色、间距全部统一。             |
| AI Streaming | 所有 AI 页面统一 Streaming Renderer。         |
| 可扩展          | 新课程、新 Agent、新页面无需修改底层 Layout。          |

---

## 9.2 Vue 前端架构图

```text
src/
│
├── App.vue
│
├── router/
│
├── layouts/
│
├── views/
│
├── components/
│
├── stores/
│
├── api/
│
├── composables/
│
├── utils/
│
├── styles/
│
└── assets/
```

数据流：

```text
View

↓

Pinia Store

↓

Axios API

↓

FastAPI Backend

↓

Response

↓

Store 更新

↓

View 自动刷新
```

---

# 第十章 前端目录设计（完整版）

## 10.1 src 完整目录树

```text
src/

├── api/
│   ├── auth.ts
│   ├── workspace.ts
│   ├── course.ts
│   ├── homework.ts
│   ├── experiment.ts
│   ├── quiz.ts
│   ├── ai.ts
│   ├── growth.ts
│   ├── profile.ts
│   ├── upload.ts
│   └── analytics.ts
│
├── assets/
│   ├── icons/
│   ├── images/
│   ├── logos/
│   └── textbooks/
│
├── components/
│   ├── common/
│   ├── layout/
│   ├── charts/
│   ├── ai/
│   ├── upload/
│   ├── markdown/
│   └── growth/
│
├── composables/
│   ├── useAuth.ts
│   ├── useAI.ts
│   ├── useChart.ts
│   ├── useUpload.ts
│   ├── usePagination.ts
│   ├── useTheme.ts
│   └── useNotification.ts
│
├── layouts/
│   ├── WorkspaceLayout.vue
│   ├── AuthLayout.vue
│   └── EmptyLayout.vue
│
├── router/
│   ├── index.ts
│   ├── guards.ts
│   └── routes.ts
│
├── stores/
│   ├── auth.ts
│   ├── workspace.ts
│   ├── course.ts
│   ├── ai.ts
│   ├── growth.ts
│   ├── notification.ts
│   ├── profile.ts
│   └── app.ts
│
├── styles/
│   ├── variables.css
│   ├── reset.css
│   ├── theme.css
│   ├── animation.css
│   └── markdown.css
│
├── utils/
│   ├── request.ts
│   ├── constants.ts
│   ├── formatter.ts
│   ├── markdown.ts
│   ├── storage.ts
│   └── permission.ts
│
├── views/
│
└── App.vue
```

---

## 10.2 views 页面目录（57 页面）

### Workspace

```text
views/workspace/

TeacherWorkspace.vue

StudentWorkspace.vue
```

---

### Learning Center（18 页面）

```text
views/learning/

LearningDashboard.vue

CourseCenter.vue

CourseDetail.vue

TodayLearning.vue

HomeworkCenter.vue

HomeworkDetail.vue

ExperimentCenter.vue

ExperimentDetail.vue

QuizCenter.vue

QuizDetail.vue

QuizImport.vue

MaterialCenter.vue

RecordCenter.vue

AITutor.vue

AIDebug.vue

AIReview.vue

LearningSearch.vue

CourseCatalog.vue
```

---

### Teaching Center（22 页面）

```text
views/teaching/

CourseManager.vue

CreateCourse.vue

LessonCenter.vue

LessonEditor.vue

PPTCenter.vue

PPTEditor.vue

TextbookCenter.vue

KnowledgeGraph.vue

KnowledgeDocument.vue

HomeworkManager.vue

HomeworkEditor.vue

HomeworkGrade.vue

ExperimentManager.vue

ExperimentEditor.vue

ExperimentGrade.vue

QuizManager.vue

QuizEditor.vue

AnalyticsDashboard.vue

AnalyticsStudent.vue

AISummary.vue

StudentManagement.vue

ResourceManager.vue
```

---

### AI Center（11 页面）

```text
views/ai/

AIWorkspace.vue

AITutor.vue

AIDocument.vue

WorkflowCenter.vue

LessonAgent.vue

PPTAgent.vue

QuizAgent.vue

SummaryAgent.vue

PromptStudio.vue

ConversationHistory.vue

AISettings.vue
```

---

### Growth Center（6 页面）

```text
views/growth/

GrowthDashboard.vue

KnowledgeMastery.vue

LearningHeatMap.vue

BehaviorAnalytics.vue

RiskPrediction.vue

LearningPath.vue
```

---

### Profile

```text
views/profile/

ProfileCenter.vue

AccountSecurity.vue

NotificationCenter.vue

FavoriteCenter.vue
```

---

# 第十一章 Layout 架构设计

## 11.1 WorkspaceLayout.vue

所有登录后页面统一 Layout。

布局如下：

```text
WorkspaceLayout

Sidebar

Header

Breadcrumb

PageContainer

NotificationDrawer

ThemeProvider
```

所有页面插槽进入：

```vue
<WorkspaceLayout>

<router-view/>

</WorkspaceLayout>
```

---

## 11.2 Header Layout

Header 包含：

```text
Logo

Global Search

Notification

Theme Switch

Avatar Menu
```

功能全部封装组件。

组件目录：

```text
components/layout/header/
```

---

## 11.3 Sidebar Layout

Sidebar 数据来源：

Pinia App Store。

菜单 JSON 驱动。

```ts
[
{
title:"Workspace",
icon:"HomeFilled",
children:[]
}
]
```

教师学生菜单动态生成。

---

# 第十二章 Pinia 状态管理设计

## 12.1 Pinia Store 总览

| Store        | 职责            |
| ------------ | ------------- |
| auth         | 登录状态。         |
| app          | Theme/Layout。 |
| workspace    | 工作台数据。        |
| course       | 当前课程状态。       |
| ai           | AI Streaming。 |
| growth       | 成长数据。         |
| notification | 通知。           |
| profile      | 用户资料。         |

---

## 12.2 auth Store

负责：

```text
User

Role

Token

Login Status

Permission
```

Actions：

- login()
- logout()
- fetchProfile()
- refreshToken()

---

## 12.3 workspace Store

负责：

今日任务。

最近课程。

AI 推荐。

统计卡片。

通知 Badge。

进入工作台一次加载。

---

## 12.4 course Store

负责：

当前课程。

章节。

教材。

实验。

Homework。

Quiz。

切换课程自动刷新。

---

## 12.5 ai Store

负责：

Streaming 内容。

Conversation。

Current Agent。

Workflow 状态。

Citation。

Token 使用量。

---

## 12.6 growth Store

负责：

Mastery。

HeatMap。

Timeline。

Risk。

Recommendation。

---

## 12.7 notification Store

负责：

通知列表。

未读数量。

轮询更新。

已读状态。

---

# 第十三章 Axios 请求架构

## 13.1 request.ts

统一 Axios Instance。

功能：

- BaseURL。
- JWT。
- Timeout。
- Error Interceptor。
- Refresh Token。

页面禁止直接 Axios.create。

---

## 13.2 API 模块划分

例如：

course.ts：

```text
listCourse()

courseDetail()

createCourse()

updateCourse()
```

每个模块对应一个后端 Router。

---

## 13.3 请求生命周期

统一：

Loading。

Success。

Error。

Toast。

Retry。

页面不处理 HTTP Status。

统一 request.ts。

---

# 第十四章 Composable 设计

## 14.1 useAI()

统一 AI Streaming Hook。

返回：

```ts
message

loading

streaming

stop()

retry()
```

所有 AI 页面复用。

---

## 14.2 useChart()

统一初始化 ECharts。

负责：

- init。
- resize。
- dispose。
- theme。

禁止页面重复写 initChart。

---

## 14.3 useUpload()

统一上传逻辑。

返回：

- upload()
- progress
- cancel
- retry

所有 Upload 组件复用。

---

## 14.4 useTheme()

负责：

Light。

Dark。

System。

LocalStorage。

自动切换 Element Plus Theme。

---

## 14.5 useNotification()

负责：

获取通知。

标记已读。

轮询暂停。

页面隐藏暂停轮询。

---

# 第十五章 公共组件设计（42 个组件）

## 15.1 Layout Components

```text
AppSidebar

AppHeader

Breadcrumb

ThemeSwitch

AvatarDropdown

NotificationDrawer
```

---

## 15.2 Common Components

```text
StatCard

SectionTitle

EmptyState

LoadingSkeleton

ErrorState

StatusBadge

PageHeader

ConfirmDialog

SearchBar

TagGroup
```

---

## 15.3 AI Components

```text
AIChatWindow

AIMessage

CitationCard

StreamingCursor

TokenCounter

WorkflowTimeline

PromptViewer

MarkdownRenderer
```

---

## 15.4 Upload Components

```text
UploadCard

UploadProgress

FilePreview

ImageViewer

PDFViewer

MarkdownPreview
```

---

## 15.5 Growth Components

```text
MasteryRadar

HeatMapChart

TimelineCard

RiskCard

RecommendationCard

LearningPathTree
```

---

## 15.6 Chart Components

```text
RadarChart

LineChart

BarChart

PieChart

KnowledgeGraphChart

HeatMapChart
```

统一 useChart()。

---

# 第十六章 Design Token 设计

## 16.1 CSS Variables

统一变量。

```css
--pm-primary

--pm-success

--pm-warning

--pm-danger

--pm-radius-xl

--pm-shadow-md
```

禁止页面写颜色。

---

## 16.2 Theme Token

Light Theme。

Dark Theme。

Element Plus Token 同步。

---

## 16.3 Typography

统一：

H1。

H2。

H3。

Body。

Caption。

Code。

---

## 16.4 Space Token

统一：

4。

8。

12。

16。

24。

32。

48。

64。

---

# 第十七章 Markdown 渲染规范

## 17.1 MarkdownRenderer

支持：

- Markdown。
- Highlight。
- Math。
- Mermaid（预留）。

AI 页面统一组件。

---

## 17.2 Code Highlight

支持：

Python。

Java。

C++。

SQL。

JSON。

Shell。

---

## 17.3 Citation Card

Markdown 中引用自动识别。

展示 Citation Card。

---

# 第十八章 页面开发顺序（必须遵循）

## 第一阶段（基础框架）

- Layout。
- Router。
- Pinia。
- Axios。
- Theme。

---

## 第二阶段（Workspace）

- Teacher Workspace。
- Student Workspace。
- Notification。

---

## 第三阶段（Learning）

依次完成：

Course → Homework → Experiment → Quiz → AI Tutor → Materials → Records。

---

## 第四阶段（Teaching）

Course → Lesson → PPT → Knowledge → Homework → Experiment → Analytics。

---

## 第五阶段（AI Center）

AI Workspace。

Workflow。

Prompt Studio。

Conversation。

Settings。

---

## 第六阶段（Growth）

Mastery。

HeatMap。

Behavior。

Risk。

Learning Path。

---

# 第十九章 前端开发 Checklist（必须完成）

## 基础工程

- [ ] Vue3 + Vite 初始化
- [ ] Element Plus 按需引入
- [ ] Pinia 初始化
- [ ] Vue Router 初始化
- [ ] Axios Instance 完成
- [ ] Theme Provider 完成

## Layout

- [ ] Sidebar
- [ ] Header
- [ ] Breadcrumb
- [ ] Notification Drawer

## 公共组件

- [ ] Loading Skeleton
- [ ] Empty State
- [ ] Error State
- [ ] Markdown Renderer
- [ ] Upload Component
- [ ] AI Chat Window
- [ ] Workflow Timeline

## 页面开发

- [ ] Workspace（2）
- [ ] Learning（18）
- [ ] Teaching（22）
- [ ] AI（11）
- [ ] Growth（6）
- [ ] Profile（4）

共 **63 个 Vue 页面组件**。

---

# 本章输出成果

本章节定义了 ProgramMind V2.0 前端完整开发规范：

- Vue 工程目录（100% 固定）。
- 57 页面目录拆分。
- Pinia 状态管理。
- Axios 请求规范。
- Composable 设计。
- 42 个公共组件。
- Design Token。
- Markdown Renderer。
- AI Streaming Renderer。
- 图表组件规范。
- 前端开发顺序与 Checklist。

---

**DOC02 Part 02 完成。**
