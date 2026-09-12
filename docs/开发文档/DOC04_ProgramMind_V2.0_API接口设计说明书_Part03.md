# ProgramMind V2.0 API 接口设计说明书

# Part03 —— Courses 课程中心接口设计（完整版）

> 文档版本：V2.0
> 
> 对应模块：课程中心（Courses Center）
> 
> 开发负责人：Backend + Frontend
> 
> 数据来源：DOC03 数据库设计文档

---

# 第一章 模块说明

## 1.1 模块定位

课程中心是 ProgramMind 的业务核心模块。

所有学习、教学、RAG、成长画像都围绕课程展开。

负责：

- 教师创建课程
- 学生选课退课
- 课程广场推荐
- 课程详情
- 课程章节树
- 教材管理
- 课程资源管理
- 学生课程进度统计

所有其它模块（Homework、Quiz、KnowledgeBase）均依赖 CourseID。

---

## 1.2 Backend 目录结构

```
backend/app/api/courses.py

backend/app/services/course_service.py

backend/app/repositories/course_repository.py

backend/app/schemas/course_schema.py
```

---

## 1.3 Frontend 目录结构

```
frontend/src/api/course.ts

frontend/src/views/course/

CourseSquare.vue

MyCourses.vue

CourseDetail.vue

CourseEditor.vue

CourseResource.vue
```

---

## 1.4 数据库涉及数据表

| 数据表              | 说明          |
| ---------------- | ----------- |
| courses          | 课程信息        |
| course_chapters  | 章节树         |
| course_resources | 教材/PPT/实验指导 |
| enrollments      | 学生选课        |
| users            | 教师信息        |
| majors           | 专业信息        |

---

# 第二章 API 总览

| API     | Method | 描述       |
| ------- | ------ | -------- |
| API-201 | GET    | 获取课程广场   |
| API-202 | GET    | 获取我的课程   |
| API-203 | GET    | 获取课程详情   |
| API-204 | POST   | 教师创建课程   |
| API-205 | PATCH  | 修改课程     |
| API-206 | DELETE | 删除课程     |
| API-207 | POST   | 学生选课     |
| API-208 | DELETE | 学生退课     |
| API-209 | GET    | 获取课程学生列表 |
| API-210 | GET    | 获取章节树    |
| API-211 | POST   | 新建章节     |
| API-212 | PATCH  | 修改章节     |
| API-213 | DELETE | 删除章节     |
| API-214 | GET    | 获取课程资源   |
| API-215 | POST   | 上传课程资源   |
| API-216 | PATCH  | 修改课程资源   |
| API-217 | DELETE | 删除课程资源   |
| API-218 | GET    | 获取课程统计信息 |

共 **18 个接口**。

---

# 第三章 API-201 获取课程广场

## 接口信息

| 项      | 内容                    |
| ------ | --------------------- |
| URL    | `/api/courses/square` |
| Method | GET                   |
| 权限     | 登录用户                  |

---

## Query 参数

| 参数         | 类型     | 描述                       |
| ---------- | ------ | ------------------------ |
| page       | int    | 页码                       |
| page_size  | int    | 每页数量                     |
| keyword    | string | 搜索关键词                    |
| major_id   | uuid   | 专业过滤                     |
| teacher_id | uuid   | 教师过滤                     |
| sort       | string | newest/popular/recommend |

示例：

```
GET /api/courses/square?page=1&page_size=8&keyword=Python&sort=recommend
```

---

## 返回结构

```json
{
  "code":0,
  "data":{
    "list":[
      {
        "id":"uuid",
        "course_code":"AI1001",
        "course_name":"Python程序设计",
        "cover_url":"https://...",
        "teacher_name":"李老师",
        "teacher_avatar":"...",
        "major_name":"人工智能",
        "student_count":124,
        "chapter_count":12,
        "resource_count":38,
        "is_enrolled":false,
        "recommend_score":96
      }
    ],
    "pagination":{
      "page":1,
      "pages":5,
      "total":40
    }
  }
}
```

---

## Backend 流程

1. 查询 courses。
2. JOIN teacher。
3. JOIN enrollments 数量。
4. JOIN resources 数量。
5. 返回推荐排序。

---

## SQL 查询

涉及：

- courses
- users
- enrollments
- course_resources

---

## 前端调用页面

CourseSquare.vue

首页推荐课程。

工作台推荐课程。

---

# 第四章 API-202 获取我的课程

## URL

```
GET /api/courses/my
```

---

## 权限

学生：

返回已选课程。

教师：

返回教授课程。

---

## 返回示例

```json
{
  "code":0,
  "data":{
    "role":"student",
    "courses":[
      {
        "course_id":"uuid",
        "course_name":"Python程序设计",
        "progress":67,
        "teacher_name":"李老师",
        "next_task":"第一次实验"
      }
    ]
  }
}
```

---

## Backend

Role 判断。

Student JOIN enrollments。

Teacher 查询 teacher_id。

---

## 前端

MyCourses.vue。

Workspace。

---

# 第五章 API-203 获取课程详情

## URL

```
GET /api/courses/{course_id}
```

---

## 返回结构

```json
{
  "code":0,
  "data":{
    "course":{
      "id":"uuid",
      "course_code":"AI1001",
      "course_name":"Python程序设计",
      "description":"Python基础课程",
      "cover_url":"...",
      "teacher":{
        "id":"uuid",
        "name":"李老师",
        "avatar":"..."
      },
      "major":{
        "id":"uuid",
        "name":"人工智能"
      },
      "semester":"2026秋",
      "credits":3,
      "status":"published"
    }
  }
}
```

---

## 包含信息

课程简介。

教师简介。

课程统计。

章节数量。

教材数量。

实验数量。

---

# 第六章 API-204 教师创建课程

## URL

```
POST /api/courses
```

教师权限。

---

## 请求参数

```json
{
  "course_code":"AI1002",
  "course_name":"数据结构",
  "description":"程序设计核心课程",
  "major_id":"uuid",
  "semester":"2026秋",
  "credits":4
}
```

---

## Backend 流程

创建课程。

创建默认章节 Root。

初始化课程统计。

---

## 返回

课程信息。

---

## 数据库写入

courses。

course_chapters。

---

## 前端页面

CourseEditor.vue。

TeachCourse.vue。

---

# 第七章 API-205 修改课程信息

## URL

```
PATCH /api/courses/{course_id}
```

---

## 可修改字段

课程名。

简介。

封面。

学分。

状态。

---

## Backend 校验

教师必须拥有课程。

管理员拥有全部权限。

---

# 第八章 API-206 删除课程

## URL

```
DELETE /api/courses/{course_id}
```

---

## Backend 删除逻辑

逻辑删除。

status=deleted。

不真正删除资源。

---

## 联动影响

Homework。

Quiz。

Knowledge。

Enrollment。

全部失效。

---

# 第九章 API-207 学生选课

## URL

```
POST /api/courses/{course_id}/enroll
```

---

## 返回

```json
{
  "progress":0,
  "enrolled_at":"2026-09-01"
}
```

---

## Backend

创建 enrollments。

初始化 mastery。

初始化 growth_profile。

创建通知。

---

## 前端

课程广场按钮。

课程详情按钮。

---

# 第十章 API-208 学生退课

## URL

```
DELETE /api/courses/{course_id}/enroll
```

---

## Backend

删除 enrollments。

保留学习记录。

---

## 返回

204。

---

# 第十一章 API-209 获取课程学生列表

## URL

```
GET /api/courses/{course_id}/students
```

教师权限。

---

## Query

分页。

关键词。

班级。

学习状态。

---

## 返回

学生头像。

姓名。

学习进度。

最近学习时间。

掌握度。

---

## 前端页面

教师课程详情。

学生管理页面。

---

# 第十二章 API-210 获取章节树

## URL

```
GET /api/courses/{course_id}/chapters
```

---

## 返回

树结构。

```json
[
  {
    "id":"uuid",
    "title":"第一章 Python基础",
    "order_index":1,
    "children":[
      {
        "id":"uuid",
        "title":"变量与数据类型"
      }
    ]
  }
]
```

---

## Backend

course_chapters。

递归构建 Tree。

---

## 前端

课程详情左侧导航。

知识网络入口。

学习路径。

---

# 第十三章 API-211 新建章节

## URL

```
POST /api/courses/{course_id}/chapters
```

---

## Body

```json
{
  "parent_id":"uuid",
  "title":"循环结构",
  "description":"for while"
}
```

---

## Backend

新增章节。

计算 order_index。

---

# 第十四章 API-212 修改章节

## URL

```
PATCH /api/chapters/{chapter_id}
```

---

修改：

标题。

简介。

排序。

父章节。

---

# 第十五章 API-213 删除章节

## URL

```
DELETE /api/chapters/{chapter_id}
```

---

规则：

删除子章节。

删除知识点关联。

删除资源关联。

---

# 第十六章 API-214 获取课程资源列表

## URL

```
GET /api/courses/{course_id}/resources
```

---

## Query

| 参数         | 描述                          |
| ---------- | --------------------------- |
| type       | textbook/ppt/video/code/lab |
| chapter_id | 所属章节                        |

---

## 返回

资源数组。

每项：

标题。

类型。

大小。

更新时间。

下载次数。

---

## 前端页面

教材管理。

学习资料。

课程详情资源页。

---

# 第十七章 API-215 上传课程资源

## URL

```
POST /api/courses/{course_id}/resources
```

---

## FormData

| 字段         | 类型     |
| ---------- | ------ |
| file       | File   |
| title      | string |
| type       | string |
| chapter_id | string |

---

## 支持格式

PDF。

PPTX。

DOCX。

ZIP。

PNG。

MP4。

CSV。

---

## Backend 流程

上传 OSS。

写 resources。

更新课程资源数量。

记录上传日志。

---

# 第十八章 API-216 修改课程资源

## URL

```
PATCH /api/resources/{resource_id}
```

---

修改：

标题。

章节。

标签。

描述。

公开状态。

---

# 第十九章 API-217 删除课程资源

## URL

```
DELETE /api/resources/{resource_id}
```

---

删除 OSS。

删除数据库。

记录日志。

---

# 第二十章 API-218 获取课程统计信息

## URL

```
GET /api/courses/{course_id}/statistics
```

---

## 返回

```json
{
  "student_count":132,
  "chapter_count":14,
  "resource_count":36,
  "homework_count":8,
  "quiz_count":5,
  "experiment_count":4,
  "completion_rate":83.2,
  "avg_score":88.5
}
```

---

## Backend

聚合查询。

Redis 可缓存。

---

## 前端

教师工作台。

课程详情顶部统计卡片。

---

# 第二十一章 Pydantic Schema

## CreateCourseRequest

字段：

course_code。

course_name。

description。

major_id。

semester。

credits。

---

## UpdateCourseRequest

可选字段。

---

## ChapterRequest

章节标题。

父节点。

排序。

---

## ResourceUploadRequest

title。

type。

chapter_id。

description。

---

# 第二十二章 Repository 设计

## CourseRepository

方法：

- create_course
- update_course
- delete_course
- list_courses
- get_course

---

## EnrollmentRepository

方法：

- enroll_course
- quit_course
- list_students
- get_progress

---

## ChapterRepository

方法：

- create_chapter
- update_chapter
- delete_chapter
- build_tree

---

## ResourceRepository

方法：

- upload_resource
- list_resources
- delete_resource
- update_resource

---

# 第二十三章 Service 设计

## CourseService

负责：

课程生命周期。

推荐课程。

课程详情。

---

## EnrollmentService

负责：

学生选课。

学习进度初始化。

课程人数更新。

---

## ResourceService

负责：

教材资源上传。

OSS。

资源统计。

---

# 第二十四章 Frontend SDK

```
course.ts

getCourseSquare()

getMyCourses()

getCourseDetail()

createCourse()

updateCourse()

deleteCourse()

enrollCourse()

quitCourse()

getStudents()

getChapterTree()

createChapter()

updateChapter()

deleteChapter()

getResources()

uploadResource()

updateResource()

deleteResource()

getCourseStatistics()
```

统一 Axios。

---

# 第二十五章 Checklist

## Router

### Course

- [ ] GET /courses/square
- [ ] GET /courses/my
- [ ] GET /courses/{id}
- [ ] POST /courses
- [ ] PATCH /courses/{id}
- [ ] DELETE /courses/{id}

### Enrollment

- [ ] POST /courses/{id}/enroll
- [ ] DELETE /courses/{id}/enroll
- [ ] GET /courses/{id}/students

### Chapter

- [ ] GET /courses/{id}/chapters
- [ ] POST /courses/{id}/chapters
- [ ] PATCH /chapters/{id}
- [ ] DELETE /chapters/{id}

### Resource

- [ ] GET /courses/{id}/resources
- [ ] POST /courses/{id}/resources
- [ ] PATCH /resources/{id}
- [ ] DELETE /resources/{id}

### Statistics

- [ ] GET /courses/{id}/statistics

---

## Repository

- [ ] CourseRepository
- [ ] EnrollmentRepository
- [ ] ChapterRepository
- [ ] ResourceRepository

---

## Service

- [ ] CourseService
- [ ] EnrollmentService
- [ ] ResourceService

---

## Frontend 页面

- [ ] CourseSquare.vue
- [ ] MyCourses.vue
- [ ] CourseDetail.vue
- [ ] CourseEditor.vue
- [ ] CourseResource.vue

---

# 本章输出成果

课程中心接口设计完成。

Backend 完成本章节后，可以实现：

- 教师建课。
- 学生选课。
- 我的课程。
- 课程详情。
- 章节树。
- 教材/PPT 上传。
- 课程资源管理。
- 课程统计卡片。

下一章节进入 Learning Center（Homework / Quiz / Experiment）接口设计，共约 25 个接口，是整个项目业务量最大的一章。

---

**DOC04 Part03 完成。**
