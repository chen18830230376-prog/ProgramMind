# ProgramMind V2.0 后端开发规范

# Part02 —— JWT 登录认证与 RBAC 权限控制（完整版）

> 文档版本：V2.0
> 更新时间：2026-09
> 模块负责人：Backend（认证模块）
> 技术栈：FastAPI + JWT + OAuth2 + SQLAlchemy + Redis（可选）

---

# 第一章 模块定位

## 1.1 Auth 模块职责

Auth 模块负责整个 ProgramMind 的身份认证与权限管理。

包括：

- 用户注册
- 登录
- JWT Access Token
- Refresh Token
- Token 校验
- RBAC 权限控制
- 登录状态管理
- 用户身份注入
- 权限依赖（Depends）

所有业务 API 必须经过 Auth。

---

## 1.2 登录认证架构

用户登录

↓

Password Verify（BCrypt）

↓

生成 JWT Access Token

↓

生成 Refresh Token

↓

返回前端

↓

前端保存 Token

↓

Authorization Header

↓

JWT Middleware

↓

Current User

↓

RBAC Permission

↓

Business API

---

# 第二章 JWT 认证方案

## 2.1 Token 类型

ProgramMind 使用双 Token。

| Token         | 用途              | 生命周期 |
| ------------- | --------------- | ---- |
| Access Token  | 接口认证            | 2 小时 |
| Refresh Token | 刷新 Access Token | 7 天  |

原则：

Access Token 短期。

Refresh Token 长期。

---

## 2.2 JWT Payload

```json
{
  "sub":"user_uuid",
  "username":"student_demo",
  "role":"student",
  "type":"access",
  "exp":1781200000,
  "iat":1781192800
}
```

字段说明：

| 字段       | 含义               |
| -------- | ---------------- |
| sub      | 用户 UUID          |
| username | 用户账号             |
| role     | 用户角色             |
| type     | access / refresh |
| exp      | 过期时间             |
| iat      | 签发时间             |

禁止存储密码。

---

## 2.3 Token 生命周期

Access Token：

2 小时。

Refresh Token：

7 天。

刷新后：

新的 Access Token。

Refresh Token 保持不变（V2.0）。

---

## 2.4 Secret Key 管理

.env

SECRET_KEY=xxxxxxxxxxxxxxxxxxxxxxxx

JWT_ALGORITHM=HS256

JWT_ACCESS_EXPIRE_HOURS=2

JWT_REFRESH_EXPIRE_DAYS=7

禁止写入 GitHub。

---

# 第三章 Password 安全规范

## 3.1 BCrypt

密码统一 BCrypt Hash。

数据库：

password_hash VARCHAR(255)

禁止保存明文密码。

---

## 3.2 Password Policy

密码必须满足：

- 长度 8~32 位
- 至少一位数字
- 至少一位字母
- 推荐特殊字符

---

## 3.3 注册流程

输入密码

↓

BCrypt Hash

↓

保存 password_hash

登录：

输入密码

↓

Verify Hash

↓

JWT

---

# 第四章 登录接口设计

## 4.1 登录接口

POST /api/v1/auth/login

请求：

email/username

password

返回：

user_info

access_token

refresh_token

expires_in

---

## 4.2 登录业务流程

验证账号存在。

↓

验证状态 active。

↓

BCrypt 校验密码。

↓

更新 last_login_at。

↓

login_count+1。

↓

生成 JWT。

↓

返回。

---

## 4.3 登录失败处理

| 场景       | HTTP |
| -------- | ---- |
| 用户不存在    | 404  |
| 密码错误     | 401  |
| 用户禁用     | 403  |
| Token 异常 | 401  |

统一异常返回。

---

# 第五章 注册接口设计

## 5.1 注册接口

POST /api/v1/auth/register

字段：

username

email

password

real_name

major

grade

---

## 5.2 注册流程

校验邮箱。

↓

用户名唯一。

↓

邮箱唯一。

↓

Hash Password。

↓

创建 users。

↓

创建 profile。

↓

创建 mirror。

↓

返回 Token。

注册后自动登录。

---

# 第六章 Refresh Token 实现

## 6.1 Refresh API

POST /api/v1/auth/refresh

请求：

refresh_token

返回：

新的 access_token。

---

## 6.2 Refresh 校验

检查：

JWT 是否过期。

type 是否 refresh。

用户状态是否 active。

通过：

生成新的 access token。

---

## 6.3 Logout

POST /api/v1/auth/logout

V2：

客户端删除 Token。

Redis 黑名单（预留）。

---

# 第七章 OAuth2PasswordBearer 配置

## 7.1 OAuth2

统一：

Authorization: Bearer Token

Header：

Authorization: Bearer eyJ...

---

## 7.2 Depends 注入

所有登录接口：

Depends(get_current_user)

自动解析 JWT。

---

# 第八章 CurrentUser Dependency

## 8.1 get_current_user

职责：

读取 JWT。

解析 Payload。

查询数据库。

返回 User ORM。

---

## 8.2 校验流程

Header。

↓

JWT Decode。

↓

检查 exp。

↓

查询 User。

↓

status=active。

↓

返回 User。

---

## 8.3 CurrentUser 返回对象

User ORM。

包含：

id

role

username

email

profile

无需再次查询数据库。

---

# 第九章 RBAC 权限模型

## 9.1 三层角色

| Role    | 描述  |
| ------- | --- |
| student | 学生  |
| teacher | 教师  |
| admin   | 管理员 |

未来：

assistant。

reviewer。

---

## 9.2 权限矩阵

| API              | Student | Teacher | Admin |
| ---------------- | ------- | ------- | ----- |
| 查看课程             | ✅       | ✅       | ✅     |
| 提交作业             | ✅       | ❌       | ✅     |
| 发布作业             | ❌       | ✅       | ✅     |
| AI Tutor         | ✅       | ❌       | ✅     |
| AI Lesson Plan   | ❌       | ✅       | ✅     |
| Growth Dashboard | ✅       | ✅       | ✅     |
| Admin 用户管理       | ❌       | ❌       | ✅     |

---

# 第十章 Permission Dependency

## 10.1 require_student

允许：

student

admin

---

## 10.2 require_teacher

允许：

teacher

admin

---

## 10.3 require_admin

允许：

admin。

否则返回：

403 Forbidden。

---

## 10.4 多角色支持

允许：

teacher + assistant。

RBAC 支持多个角色。

user_roles 表提供能力。

---

# 第十一章 JWT Middleware

## 11.1 Middleware 职责

拦截请求。

↓

读取 Authorization。

↓

解析 JWT。

↓

写入 request.state.user。

↓

继续请求。

---

## 11.2 白名单接口

无需 Token：

/login

/register

/docs

/openapi.json

/health

/public/*

---

## 11.3 黑名单接口（预留）

Redis 保存 Token。

Logout 后加入黑名单。

Middleware 校验。

---

# 第十二章 Permission Middleware

部分接口权限统一控制。

例如：

/admin/*

↓

Admin Middleware。

/teacher/*

↓

Teacher Middleware。

减少 Router 重复代码。

---

# 第十三章 Token 安全策略

## Access Token

保存在前端内存。

推荐 Pinia Store。

---

## Refresh Token

HttpOnly Cookie（生产）。

开发环境可返回 JSON。

---

## Token Rotation（预留）

Refresh Token 使用一次更新一次。

防重放攻击。

---

# 第十四章 Redis Session（预留）

Redis 保存：

Refresh Token。

登录状态。

验证码。

限流次数。

AI 会话缓存。

TTL：

7 天。

---

# 第十五章 Auth Service 设计

## AuthService

职责：

register()

login()

logout()

refresh()

change_password()

verify_email()

---

## PasswordService

职责：

hash_password()

verify_password()

password_strength()

---

## TokenService

职责：

create_access_token()

create_refresh_token()

decode_token()

verify_token()

---

# 第十六章 Repository 设计

## UserRepository

find_by_username()

find_by_email()

update_login_time()

update_password()

update_status()

---

## RoleRepository

list_roles()

grant_role()

revoke_role()

has_permission()

---

# 第十七章 Auth API Checklist

## Login

- [ ] JWT Access Token
- [ ] Refresh Token
- [ ] Login Count
- [ ] Last Login Time

## Register

- [ ] Hash Password
- [ ] Profile 创建
- [ ] Mirror 创建

## Permission

- [ ] Student
- [ ] Teacher
- [ ] Admin

## Middleware

- [ ] JWT Middleware
- [ ] Permission Middleware
- [ ] Auth Dependency

---

# 第十八章 本章开发成果

完成 Auth 模块后，ProgramMind Backend 将具备：

- JWT 双 Token 登录认证。
- OAuth2 Bearer Token。
- BCrypt 密码加密。
- RBAC 权限控制。
- Depends 权限注入。
- Refresh Token 自动续期。
- 后续 150+ API 全部可以统一鉴权。
