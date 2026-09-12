# ProgramMind V2.0 API 接口设计说明书

# Part 01 —— API 基础规范 + 用户认证模块

> 文档版本：V2.0
> 
> 面向成员：Backend（FastAPI）、Frontend（Vue）、AI（调用接口）
> 
> 技术栈：FastAPI + SQLAlchemy + MySQL + JWT + Pydantic

---

# 第一章 文档说明

## 1.1 文档目标

本文档规定 ProgramMind V2.0 所有 REST API 的开发规范。

所有成员必须严格按照本规范开发接口，禁止自行修改字段名称、返回格式、错误码。

本文档对应：

- Backend FastAPI Router
- Frontend API SDK
- Swagger(OpenAPI)
- 数据库 DOC03

---

## 1.2 API 分层

ProgramMind 所有接口划分为 8 大模块。

| 模块             | 前缀               | 负责人          |
| -------------- | ---------------- | ------------ |
| 用户认证           | `/api/auth`      | Backend      |
| 用户中心           | `/api/profile`   | Backend      |
| 课程中心           | `/api/courses`   | Backend      |
| 学习中心           | `/api/learning`  | Backend      |
| 教学中心           | `/api/teaching`  | Backend      |
| AI Engine      | `/api/ai`        | AI + Backend |
| Knowledge Base | `/api/knowledge` | AI           |
| Growth Center  | `/api/growth`    | Backend + AI |

全部接口统一 `/api` 前缀。

---

## 1.3 URL 命名规范

统一 RESTful。

正确：

```
GET    /api/courses
GET    /api/courses/{course_id}
POST   /api/courses
PATCH  /api/courses/{course_id}
DELETE /api/courses/{course_id}
```

错误：

```
/getCourses
/createCourse
/updateCourse
```

禁止使用动词。

---

## 1.4 HTTP Method 规范

| Method | 用途            |
| ------ | ------------- |
| GET    | 查询资源          |
| POST   | 创建资源          |
| PATCH  | 更新部分资源        |
| PUT    | 全量更新（V2 暂不使用） |
| DELETE | 删除资源          |

禁止 GET 修改数据。

---

## 1.5 JSON 返回格式（统一）

所有接口返回统一结构。

成功：

```json
{
  "code":0,
  "message":"success",
  "data":{}
}
```

失败：

```json
{
  "code":40001,
  "message":"用户名不存在",
  "data":null
}
```

任何接口不得返回其它格式。

---

## 1.6 HTTP 状态码规范

| HTTP | 描述     |
| ---- | ------ |
| 200  | 请求成功   |
| 201  | 创建成功   |
| 204  | 删除成功   |
| 400  | 参数错误   |
| 401  | 未登录    |
| 403  | 权限不足   |
| 404  | 资源不存在  |
| 409  | 数据冲突   |
| 422  | 参数校验失败 |
| 500  | 服务异常   |

HTTP 与业务 Code 同时存在。

---

## 1.7 Business Code（业务错误码）

### Auth（10000）

| Code  | 描述      |
| ----- | ------- |
| 10001 | 用户名不存在  |
| 10002 | 密码错误    |
| 10003 | 用户名重复   |
| 10004 | JWT 已失效 |
| 10005 | JWT 非法  |

### Course（20000）

| Code  | 说明    |
| ----- | ----- |
| 20001 | 课程不存在 |
| 20002 | 课程未发布 |
| 20003 | 课程已选  |

### Homework（30000）

| Code  | 说明     |
| ----- | ------ |
| 30001 | 作业不存在  |
| 30002 | 超过截止时间 |
| 30003 | 重复提交   |

### Quiz（31000）

| Code  | 说明    |
| ----- | ----- |
| 31001 | 测验不存在 |
| 31002 | 考试结束  |
| 31003 | 答案为空  |

### AI（50000）

| Code  | 说明           |
| ----- | ------------ |
| 50001 | LLM不可用       |
| 50002 | RAG检索失败      |
| 50003 | Workflow执行失败 |

统一维护。

---

# 第二章 API 安全规范

## 2.1 JWT 鉴权流程

登录成功返回：

- Access Token
- Refresh Token

之后：

```
Authorization: Bearer <access_token>
```

Backend 自动解析。

---

## 2.2 Token 生命周期

| Token         | 生命周期 |
| ------------- | ---- |
| Access Token  | 2 小时 |
| Refresh Token | 7 天  |

支持刷新。

---

## 2.3 权限模型

| Role    | 权限   |
| ------- | ---- |
| student | 学习模块 |
| teacher | 教学模块 |
| admin   | 平台管理 |

Router 使用 Depends 校验。

---

## 2.4 Header 规范

所有接口：

```http
Content-Type: application/json

Authorization: Bearer xxx
```

上传接口例外。

---

## 2.5 分页规范

统一：

```http
GET /api/courses?page=1&page_size=10
```

返回：

```json
{
  "list":[],
  "pagination":{
    "page":1,
    "page_size":10,
    "total":123,
    "pages":13
  }
}
```

统一分页对象。

---

# 第三章 Auth 模块接口

---

## API-001 用户注册

### 接口信息

| 项      | 内容                   |
| ------ | -------------------- |
| URL    | `/api/auth/register` |
| Method | POST                 |
| 权限     | Public               |

---

### 请求参数

```json
{
  "username":"student001",
  "password":"12345678",
  "role":"student",
  "name":"张三",
  "major_id":"uuid"
}
```

---

### 字段说明

| 字段       | 类型              | 必填   |
| -------- | --------------- | ---- |
| username | string          | √    |
| password | string          | √    |
| role     | student/teacher | √    |
| name     | string          | √    |
| major_id | string          | 学生必填 |

---

### Backend 流程

1. 参数校验（Pydantic）
2. 检查用户名唯一。
3. 密码 Hash。
4. 创建 Users。
5. 创建 StudentProfile / TeacherProfile。
6. 返回 Token。

---

### 返回数据

```json
{
  "code":0,
  "message":"注册成功",
  "data":{
    "user_id":"uuid",
    "access_token":"jwt",
    "refresh_token":"jwt"
  }
}
```

---

### 数据库操作

- users
- student_profiles
- teacher_profiles

---

### 前端调用位置

```
frontend/src/api/auth.ts

views/Login.vue
```

负责人：Backend + Frontend。

---

## API-002 用户登录

### 接口信息

| 项      | 内容                |
| ------ | ----------------- |
| URL    | `/api/auth/login` |
| Method | POST              |

---

### 请求参数

```json
{
  "username":"teacher001",
  "password":"12345678"
}
```

---

### Backend 流程

- 查询用户
- 校验 Hash
- 创建 JWT
- 更新 last_login_time

---

### 返回

```json
{
  "code":0,
  "message":"登录成功",
  "data":{
    "user":{
      "id":"uuid",
      "role":"teacher",
      "name":"李老师",
      "avatar":"..."
    },
    "access_token":"jwt",
    "refresh_token":"jwt"
  }
}
```

---

### 错误码

| Code  | 描述    |
| ----- | ----- |
| 10001 | 用户不存在 |
| 10002 | 密码错误  |

---

### 数据库

users。

---

### 前端调用

store/auth.ts。

---

## API-003 获取当前用户信息

### URL

```
GET /api/auth/me
```

JWT 必须存在。

---

### 返回

```json
{
  "code":0,
  "data":{
    "id":"uuid",
    "role":"student",
    "username":"student001",
    "name":"张三",
    "avatar":"...",
    "major":"人工智能"
  }
}
```

---

### 数据来源

users。

student_profiles。

teacher_profiles。

---

### 前端

页面初始化调用一次。

恢复登录状态。

---

## API-004 Token 刷新

### URL

```
POST /api/auth/refresh
```

---

### Header

Refresh Token。

---

### 返回

新的 Access Token。

---

### 生命周期

刷新成功。

旧 Access Token 失效。

---

## API-005 用户退出登录

### URL

```
POST /api/auth/logout
```

---

### Backend

JWT 加入黑名单（Redis）。

删除 Refresh Token。

---

### 返回

204。

---

## API-006 获取专业列表

### URL

```
GET /api/auth/majors
```

公开接口。

---

### 返回

```json
{
  "code":0,
  "data":[
    {
      "id":"uuid",
      "major_name":"人工智能",
      "school_name":"计算机学院"
    }
  ]
}
```

---

### 数据来源

majors。

---

### 前端

注册页专业下拉。

课程推荐。

---

# 第四章 Pydantic Schema（Auth）

## RegisterRequest

字段：

- username
- password
- role
- name
- major_id

密码长度：

8~20。

---

## LoginRequest

字段：

username。

password。

---

## TokenResponse

字段：

user。

access_token。

refresh_token。

expires_in。

---

# 第五章 Repository 设计（Auth）

## UserRepository

方法：

- create_user()
- get_user_by_username()
- get_user_by_id()
- update_login_time()

---

## ProfileRepository

方法：

- create_student_profile()
- create_teacher_profile()
- get_profile()

---

# 第六章 Service 设计（Auth）

## AuthService

负责：

JWT。

密码 Hash。

登录。

注册。

刷新 Token。

---

## JWTService

负责：

生成 Token。

解析 Token。

刷新 Token。

失效 Token。

---

# 第七章 Auth Checklist

## Router

- [ ] POST /register
- [ ] POST /login
- [ ] GET /me
- [ ] POST /refresh
- [ ] POST /logout
- [ ] GET /majors

## Repository

- [ ] UserRepository
- [ ] ProfileRepository

## Service

- [ ] AuthService
- [ ] JWTService

## Frontend SDK

- [ ] login()
- [ ] register()
- [ ] me()
- [ ] logout()
- [ ] refresh()

---

# 本章输出成果

认证模块接口设计完成。

Backend 完成后，可实现：

- JWT 登录注册。
- Token 自动刷新。
- 登录状态恢复。
- 专业列表接口。

下一章节进入 Profile 用户中心接口设计（头像、资料、通知、收藏）。

---

**DOC04 Part01 完成。**
