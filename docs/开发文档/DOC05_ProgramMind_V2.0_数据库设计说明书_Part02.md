# ProgramMind V2.0 数据库设计说明书

# Part02 —— User Domain（用户系统数据库设计）

> 文档版本：V2.0
> 模块负责人：Backend（数据库）
> 对应模块：登录、注册、权限、个人中心、通知、AI身份识别

---

# 第一章 User Domain 模块说明

## 1.1 模块职责

User Domain 是整个 ProgramMind 的身份中心（Identity Center）。

负责：

- 用户登录认证
- 用户角色权限
- 教师/学生身份区分
- 个人资料
- 学院专业信息
- AI Agent 身份识别
- 通知接收对象

所有业务模块都依赖 User Domain。

---

## 1.2 数据表设计

User Domain 共 **3 张核心表**。

| 表名            | 功能        |
| ------------- | --------- |
| users         | 登录账号与认证信息 |
| user_profiles | 用户详细资料    |
| user_roles    | 用户角色与权限   |

数据库关系：

```text
users
 │
 │1:1
 ▼
user_profiles

users
 │
 │1:N
 ▼
user_roles
```

说明：

- 一个账号只有一份 Profile。
- 一个账号可以拥有多个 Role（预留管理员）。

---

# 第二章 users 表（账号表）

## 2.1 表定位

保存所有登录认证信息。

**不保存业务信息。**

---

## 2.2 字段设计（完整版）

| 字段            | 类型           | 是否为空 | 说明                          |
| ------------- | ------------ | ---- | --------------------------- |
| id            | CHAR(36)     | 否    | UUID 主键                     |
| username      | VARCHAR(50)  | 否    | 登录账号（唯一）                    |
| email         | VARCHAR(120) | 否    | 邮箱（唯一）                      |
| password_hash | VARCHAR(255) | 否    | BCrypt 哈希密码                 |
| role          | ENUM         | 否    | teacher / student / admin   |
| status        | ENUM         | 否    | active / disabled / pending |
| last_login_at | DATETIME     | 是    | 最后登录时间                      |
| login_count   | INT          | 否    | 登录次数                        |
| avatar_url    | VARCHAR(255) | 是    | 头像地址                        |
| created_at    | DATETIME(6)  | 否    | 创建时间                        |
| updated_at    | DATETIME(6)  | 否    | 更新时间                        |
| deleted_at    | DATETIME(6)  | 是    | 软删除                         |

---

## 2.3 MySQL DDL

```sql
CREATE TABLE users (
    id CHAR(36) PRIMARY KEY,

    username VARCHAR(50) NOT NULL UNIQUE,
    email VARCHAR(120) NOT NULL UNIQUE,

    password_hash VARCHAR(255) NOT NULL,

    role ENUM('teacher','student','admin') NOT NULL DEFAULT 'student',

    status ENUM('active','disabled','pending') NOT NULL DEFAULT 'active',

    last_login_at DATETIME NULL,

    login_count INT NOT NULL DEFAULT 0,

    avatar_url VARCHAR(255),

    created_at DATETIME(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6),

    updated_at DATETIME(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6)
        ON UPDATE CURRENT_TIMESTAMP(6),

    deleted_at DATETIME NULL
);
```

---

## 2.4 SQLAlchemy Model

```python
class User(Base, BaseModel):

    __tablename__ = "users"

    username = mapped_column(String(50), unique=True)

    email = mapped_column(String(120), unique=True)

    password_hash = mapped_column(String(255))

    role = mapped_column(Enum(UserRole))

    status = mapped_column(Enum(UserStatus))

    avatar_url = mapped_column(String(255))

    last_login_at = mapped_column(DateTime)

    login_count = mapped_column(Integer, default=0)

    profile = relationship("UserProfile")

    roles = relationship("UserRoleMapping")
```

---

## 2.5 Repository 接口

```
UserRepository

create_user()

get_user()

get_user_by_email()

get_user_by_username()

update_password()

update_login_time()

disable_user()

delete_user()
```

所有登录接口调用 Repository。

---

# 第三章 Password 安全规范（必须实现）

## 3.1 密码存储

禁止保存明文密码。

Demo 中：

```python
password="123456"
```

必须废弃。

---

## 3.2 BCrypt 哈希流程

```python
generate_password_hash(password)

check_password_hash(hash,password)
```

流程：

用户输入密码。

↓

Hash。

↓

数据库保存 Hash。

登录：

输入密码。

↓

Check Hash。

---

## 3.3 Password Policy

| 项目   | 要求  |
| ---- | --- |
| 最短长度 | 8   |
| 最大长度 | 32  |
| 至少数字 | 是   |
| 至少字母 | 是   |
| 特殊字符 | 推荐  |

---

# 第四章 user_profiles 表（用户资料）

## 4.1 表定位

保存个人资料。

登录表不保存这些字段。

---

## 4.2 字段设计

| 字段             | 类型           | 说明                  |
| -------------- | ------------ | ------------------- |
| id             | CHAR(36)     | UUID                |
| user_id        | CHAR(36)     | FK users.id         |
| real_name      | VARCHAR(50)  | 姓名                  |
| gender         | ENUM         | male/female/unknown |
| school         | VARCHAR(120) | 学校                  |
| college        | VARCHAR(120) | 学院                  |
| major          | VARCHAR(120) | 专业                  |
| grade          | VARCHAR(30)  | 年级                  |
| student_number | VARCHAR(30)  | 学号                  |
| teacher_number | VARCHAR(30)  | 工号                  |
| title          | VARCHAR(50)  | 职称                  |
| bio            | TEXT         | 简介                  |
| interests      | JSON         | 兴趣标签                |
| do_not_disturb | BOOLEAN      | AI免打扰               |
| created_at     | DATETIME     | 创建时间                |
| updated_at     | DATETIME     | 更新时间                |

---

## 4.3 MySQL DDL

```sql
CREATE TABLE user_profiles (

    id CHAR(36) PRIMARY KEY,

    user_id CHAR(36) NOT NULL UNIQUE,

    real_name VARCHAR(50),

    gender ENUM('male','female','unknown'),

    school VARCHAR(120),

    college VARCHAR(120),

    major VARCHAR(120),

    grade VARCHAR(30),

    student_number VARCHAR(30),

    teacher_number VARCHAR(30),

    title VARCHAR(50),

    bio TEXT,

    interests JSON,

    do_not_disturb BOOLEAN DEFAULT FALSE,

    created_at DATETIME(6),

    updated_at DATETIME(6),

    CONSTRAINT fk_profile_user
        FOREIGN KEY(user_id)
        REFERENCES users(id)
        ON DELETE CASCADE
);
```

---

## 4.4 SQLAlchemy Model

```python
class UserProfile(Base, BaseModel):

    __tablename__ = "user_profiles"

    user_id = mapped_column(ForeignKey("users.id"))

    real_name = mapped_column(String(50))

    gender = mapped_column(Enum(Gender))

    school = mapped_column(String(120))

    college = mapped_column(String(120))

    major = mapped_column(String(120))

    grade = mapped_column(String(30))

    student_number = mapped_column(String(30))

    teacher_number = mapped_column(String(30))

    title = mapped_column(String(50))

    bio = mapped_column(Text)

    interests = mapped_column(JSON)

    do_not_disturb = mapped_column(Boolean, default=False)
```

---

## 4.5 Interests JSON 示例

```json
[
  "Python",
  "机器学习",
  "计算机视觉"
]
```

支持 AI 推荐。

---

# 第五章 user_roles 表（权限表）

## 5.1 为什么单独建表

Demo 中：

role 一个字段。

V2：

支持：

- 学生
- 教师
- 管理员
- 助教（未来）
- AI Reviewer（未来）

因此单独建权限映射。

---

## 5.2 字段设计

| 字段               | 类型          | 说明                    |
| ---------------- | ----------- | --------------------- |
| id               | CHAR(36)    | UUID                  |
| user_id          | CHAR(36)    | FK users              |
| role_name        | ENUM        | teacher/student/admin |
| permission_group | VARCHAR(50) | teacher_default       |
| granted_by       | CHAR(36)    | 授权人                   |
| created_at       | DATETIME    | 创建时间                  |

---

## 5.3 MySQL DDL

```sql
CREATE TABLE user_roles (

    id CHAR(36) PRIMARY KEY,

    user_id CHAR(36) NOT NULL,

    role_name ENUM(
        'student',
        'teacher',
        'admin',
        'assistant'
    ) NOT NULL,

    permission_group VARCHAR(50),

    granted_by CHAR(36),

    created_at DATETIME(6),

    CONSTRAINT fk_role_user
        FOREIGN KEY(user_id)
        REFERENCES users(id)
        ON DELETE CASCADE
);
```

---

## 5.4 Permission Group

| 权限组               | 描述     |
| ----------------- | ------ |
| student_default   | 学生默认权限 |
| teacher_default   | 教师默认权限 |
| admin_default     | 管理员权限  |
| assistant_default | 助教权限   |

后续 RBAC 使用。

---

# 第六章 Role Permission Matrix（权限矩阵）

## 6.1 模块权限矩阵

| 模块       | Student | Teacher | Admin |
| -------- | ------- | ------- | ----- |
| 登录       | ✅       | ✅       | ✅     |
| 我的课程     | ✅       | ✅       | ✅     |
| 学习中心     | ✅       | ❌       | ✅     |
| AI Tutor | ✅       | ❌       | ✅     |
| 教案生成     | ❌       | ✅       | ✅     |
| 作业发布     | ❌       | ✅       | ✅     |
| 学情分析     | ❌       | ✅       | ✅     |
| 知识库管理    | ❌       | ✅       | ✅     |
| 用户管理     | ❌       | ❌       | ✅     |
| 系统配置     | ❌       | ❌       | ✅     |

---

## 6.2 Backend Depends

FastAPI：

```python
Depends(get_current_user)

Depends(require_teacher)

Depends(require_admin)
```

三层权限。

---

# 第七章 登录 Session / JWT 设计

## 7.1 登录流程

```text
Login

↓

Verify Password

↓

JWT Token

↓

Refresh Token

↓

Redis(Session 可选)
```

---

## 7.2 JWT Payload

```json
{
  "sub":"user_uuid",
  "role":"teacher",
  "exp":1726052000
}
```

---

## 7.3 Token 生命周期

| Token        | 时间   |
| ------------ | ---- |
| AccessToken  | 2 小时 |
| RefreshToken | 7 天  |

---

## 7.4 Refresh Token

接口：

```
POST /api/auth/refresh
```

刷新 Access Token。

---

# 第八章 登录日志（预留）

后续新增：

login_logs。

记录：

设备。

IP。

浏览器。

登录时间。

失败原因。

当前版本预留。

---

# 第九章 用户头像规范

头像统一 OSS。

数据库仅保存 URL。

禁止 Base64。

上传接口：

```
POST /api/profile/avatar
```

返回 URL。

---

# 第十章 Repository 设计

## UserRepository

```python
create()

update()

delete()

find_by_id()

find_by_email()

find_by_username()

update_password()

update_status()
```

---

## ProfileRepository

```python
create_profile()

update_profile()

get_profile()

update_avatar()

update_interest()

update_dnd()
```

---

## RoleRepository

```python
grant_role()

revoke_role()

list_roles()

check_permission()
```

---

# 第十一章 Service 设计

## AuthService

负责：

注册。

登录。

Token。

密码。

邮箱校验。

---

## ProfileService

负责：

个人资料。

头像。

兴趣。

免打扰。

---

## PermissionService

负责：

权限校验。

角色判断。

RBAC。

---

# 第十二章 Alembic Migration

生成顺序：

```
001_create_users

002_create_profiles

003_create_roles
```

外键依赖 users。

---

# 第十三章 Seed 数据设计

初始化插入：

## Teacher

| 用户名          | 角色      |
| ------------ | ------- |
| teacher_demo | teacher |

## Student

| 用户名          | 角色      |
| ------------ | ------- |
| student_demo | student |

密码统一 Hash。

---

## 默认学院

计算机学院。

人工智能学院。

软件学院。

数据科学学院。

网络空间安全学院。

---

# 第十四章 User Domain Checklist

## Users

- [ ] users 表
- [ ] BCrypt Password
- [ ] JWT 登录
- [ ] Refresh Token

## Profiles

- [ ] 用户资料
- [ ] 兴趣标签
- [ ] AI免打扰
- [ ] 头像上传

## Roles

- [ ] RBAC
- [ ] Teacher
- [ ] Student
- [ ] Admin

## Repository

- [ ] UserRepository
- [ ] ProfileRepository
- [ ] RoleRepository

## Migration

- [ ] users
- [ ] profiles
- [ ] roles

---

# 本章开发成果

完成 User Domain 后，ProgramMind V2.0 将具备：

- 安全登录认证系统。
- JWT 身份验证。
- RBAC 权限模型。
- 用户资料中心。
- 教师/学生身份隔离。
- AI 身份识别基础。
- SQLAlchemy Model 与 Repository 开发规范。
