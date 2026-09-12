# ProgramMind V2.0 API 接口设计说明书

# Part 02 —— Profile 用户中心接口设计（个人信息 / 头像 / 通知 / 收藏 / 设置）

> 文档版本：V2.0
> 
> 面向成员：Backend、Frontend
> 
> 技术栈：FastAPI + SQLAlchemy + JWT + MySQL

---

# 第八章 Profile 模块说明

## 8.1 模块定位

Profile 模块负责管理 ProgramMind 用户个人信息。

对应页面：

- 个人中心（Profile.vue）
- 顶部通知中心（NotificationDrawer.vue）
- 头像上传
- 收藏夹
- 系统设置

所有接口需要 JWT 登录。

---

## 8.2 模块目录（Backend）

```
backend/app/api/profile.py

backend/app/services/profile_service.py

backend/app/repositories/profile_repository.py

backend/app/schemas/profile_schema.py
```

---

## 8.3 前端目录

```
frontend/src/api/profile.ts

frontend/src/views/profile/

ProfilePage.vue

NotificationDrawer.vue

FavoritePage.vue

SettingsPage.vue
```

---

# 第九章 API-101 获取个人资料

## 接口信息

| 项      | 内容             |
| ------ | -------------- |
| URL    | `/api/profile` |
| Method | GET            |
| 权限     | 登录用户           |

---

## 请求 Header

```http
Authorization: Bearer <token>
```

---

## 返回示例

```json
{
  "code":0,
  "message":"success",
  "data":{
    "id":"uuid",
    "username":"student001",
    "role":"student",
    "name":"张三",
    "avatar_url":"https://...",
    "major":"人工智能",
    "school":"计算机学院",
    "grade":"2024级",
    "email":"123@example.com",
    "intro":"AI爱好者",
    "joined_at":"2026-09-01"
  }
}
```

---

## 数据来源

| 数据表              | 字段                  |
| ---------------- | ------------------- |
| users            | username、avatar_url |
| student_profiles | major、grade         |
| teacher_profiles | title               |
| users            | intro、email         |

---

## 前端调用位置

页面初始化。

Header Avatar。

Sidebar。

---

## Repository

```
get_user_profile(user_id)
```

---

## Service

ProfileService.get_profile()

---

# 第十章 API-102 修改个人资料

## 接口信息

| 项      | 内容             |
| ------ | -------------- |
| URL    | `/api/profile` |
| Method | PATCH          |
| 权限     | 登录用户           |

---

## 请求 Body

```json
{
  "name":"张三",
  "email":"abc@example.com",
  "intro":"ProgramMind开发成员"
}
```

---

## 可修改字段

| 字段         | 学生  | 教师  |
| ---------- | --- | --- |
| name       | √   | √   |
| email      | √   | √   |
| intro      | √   | √   |
| avatar_url | ×   | ×   |
| major      | ×   | ×   |
| role       | ×   | ×   |

---

## Backend 校验

- Email 格式。
- Intro ≤ 300 字。
- Name ≤ 30 字。

---

## 返回

修改后的 Profile。

---

## 数据库操作

users。

student_profiles。

teacher_profiles。

---

## 前端调用位置

Profile 编辑按钮。

---

# 第十一章 API-103 上传头像

## 接口信息

| 项            | 内容                    |
| ------------ | --------------------- |
| URL          | `/api/profile/avatar` |
| Method       | POST                  |
| Content-Type | multipart/form-data   |

---

## FormData

| 字段   | 类型    |
| ---- | ----- |
| file | Image |

---

## 支持格式

| 类型   |
| ---- |
| png  |
| jpg  |
| jpeg |
| webp |

最大：

5MB。

---

## Backend 流程

上传 OSS。

↓

生成 URL。

↓

更新 users.avatar_url。

---

## 返回

```json
{
  "code":0,
  "data":{
    "avatar_url":"https://..."
  }
}
```

---

## 前端

头像立即刷新。

---

## Repository

update_avatar()

---

# 第十二章 API-104 获取通知列表

## 接口信息

| 项      | 内容                           |
| ------ | ---------------------------- |
| URL    | `/api/profile/notifications` |
| Method | GET                          |

---

## Query

| 参数          | 描述    |
| ----------- | ----- |
| page        | 页码    |
| page_size   | 分页    |
| only_unread | 是否仅未读 |

---

## 返回示例

```json
{
  "code":0,
  "data":{
    "list":[
      {
        "id":"uuid",
        "title":"Python第一次作业已发布",
        "content":"截止时间9月20日",
        "type":"homework",
        "is_read":false,
        "created_at":"2026-09-01 12:30"
      }
    ],
    "pagination":{
      "page":1,
      "page_size":20,
      "total":32
    }
  }
}
```

---

## 通知类型

| 类型         |
| ---------- |
| homework   |
| quiz       |
| experiment |
| course     |
| system     |
| ai         |

---

## Repository

list_notifications()

---

## 前端

Header Bell。

Notification Drawer。

---

# 第十三章 API-105 标记通知已读

## URL

```
PATCH /api/profile/notifications/{notification_id}/read
```

---

## 返回

204。

---

## Backend

更新：

notifications.is_read。

---

## 前端

点击通知。

自动已读。

---

# 第十四章 API-106 全部已读

## URL

```
PATCH /api/profile/notifications/read-all
```

---

## Backend

当前用户全部通知：

is_read=True。

---

## 返回

```json
{
  "updated":18
}
```

---

# 第十五章 API-107 收藏资源

## URL

```
POST /api/profile/favorites
```

---

## 请求

```json
{
  "resource_id":"uuid"
}
```

---

## Backend

新增 favorites。

重复收藏返回成功。

---

## 返回

收藏对象。

---

## Repository

create_favorite()

---

# 第十六章 API-108 获取收藏列表

## URL

```
GET /api/profile/favorites
```

---

## Query

分页。

课程过滤。

资源类型过滤。

---

## 返回

课程。

教材。

PPT。

实验指导。

AI 推荐资料。

---

## 数据来源

favorites JOIN course_resources。

---

# 第十七章 API-109 取消收藏

## URL

```
DELETE /api/profile/favorites/{favorite_id}
```

---

## Backend

删除 favorites。

---

## 返回

204。

---

# 第十八章 API-110 用户设置

## URL

```
GET /api/profile/settings
```

---

## 返回

```json
{
  "theme":"dark",
  "language":"zh-CN",
  "email_notification":true,
  "system_notification":true,
  "ai_memory":true
}
```

---

## 设置项

| 字段                  | 描述       |
| ------------------- | -------- |
| theme               | 浅色/深色    |
| language            | 语言       |
| email_notification  | 邮件通知     |
| system_notification | 系统通知     |
| ai_memory           | AI长期记忆开关 |

---

# 第十九章 API-111 修改用户设置

## URL

```
PATCH /api/profile/settings
```

---

## 请求

```json
{
  "theme":"light",
  "ai_memory":false
}
```

---

## Backend

更新 user_settings。

---

## 返回

最新设置。

---

# 第二十章 API-112 修改密码

## URL

```
PATCH /api/profile/password
```

---

## 请求

```json
{
  "old_password":"12345678",
  "new_password":"87654321"
}
```

---

## Backend

流程：

校验旧密码。

↓

Hash 新密码。

↓

更新 users.password_hash。

---

## 返回

修改成功。

---

# 第二十一章 API-113 获取个人学习统计

## URL

```
GET /api/profile/statistics
```

---

## 返回

```json
{
  "learning_hours":126.5,
  "courses":3,
  "quizzes":28,
  "homeworks":12,
  "experiments":8,
  "avg_score":89.2
}
```

---

## 数据来源

Growth Profile。

---

## 前端

Profile Card。

---

# 第二十二章 API-114 上传背景图（可选）

## URL

```
POST /api/profile/background
```

---

头像背景。

课程主页背景。

最大：

10MB。

---

# 第二十三章 Pydantic Schema（Profile）

## ProfileUpdateRequest

字段：

- name
- email
- intro

---

## PasswordUpdateRequest

字段：

- old_password
- new_password

---

## SettingsUpdateRequest

字段：

- theme
- language
- ai_memory
- email_notification

---

# 第二十四章 Repository 设计（Profile）

## ProfileRepository

方法：

- get_profile()
- update_profile()
- update_avatar()

---

## NotificationRepository

方法：

- list_notifications()
- mark_read()
- mark_all_read()

---

## FavoriteRepository

方法：

- create_favorite()
- list_favorites()
- delete_favorite()

---

## SettingsRepository

方法：

- get_settings()
- update_settings()

---

# 第二十五章 Service 设计（Profile）

## ProfileService

负责：

个人信息。

头像。

密码。

统计。

---

## NotificationService

负责：

通知推送。

未读数量。

批量已读。

---

## FavoriteService

负责：

收藏资源。

取消收藏。

课程收藏。

---

## SettingsService

负责：

主题。

通知。

AI Memory 开关。

---

# 第二十六章 权限设计

## Student

允许：

- 修改自己资料。
- 查看自己通知。
- 收藏资源。

禁止：

- 修改其他用户资料。

---

## Teacher

增加：

- 教师头像。
- 教师简介。
- 教师统计。

其它一致。

---

# 第二十七章 Frontend SDK 设计

```
profile.ts

getProfile()

updateProfile()

uploadAvatar()

getNotifications()

readNotification()

readAllNotifications()

getFavorites()

favorite()

unFavorite()

getSettings()

updateSettings()

changePassword()

getStatistics()
```

统一封装 Axios。

---

# 第二十八章 Checklist（Profile 模块）

## Router

- [ ] GET /profile
- [ ] PATCH /profile
- [ ] POST /profile/avatar
- [ ] PATCH /profile/password

### Notification

- [ ] GET /notifications
- [ ] PATCH /notifications/{id}/read
- [ ] PATCH /notifications/read-all

### Favorite

- [ ] POST /favorites
- [ ] GET /favorites
- [ ] DELETE /favorites/{id}

### Settings

- [ ] GET /settings
- [ ] PATCH /settings

### Statistics

- [ ] GET /statistics

---

## Repository

- [ ] ProfileRepository
- [ ] NotificationRepository
- [ ] FavoriteRepository
- [ ] SettingsRepository

---

## Service

- [ ] ProfileService
- [ ] NotificationService
- [ ] FavoriteService
- [ ] SettingsService

---

## Frontend 页面

- [ ] ProfilePage.vue
- [ ] NotificationDrawer.vue
- [ ] FavoritePage.vue
- [ ] SettingsPage.vue

---

# 本章输出成果

用户中心接口设计完成。

Backend 成员完成本章节后，可实现：

- 个人资料管理。
- JWT 用户信息恢复。
- 通知中心。
- 收藏夹。
- 用户设置。
- 密码修改。
- 学习统计卡片。

下一章节进入 Courses 模块接口设计（课程 / 章节 / 资源 / 选课）。

---

**DOC04 Part02 完成。**
