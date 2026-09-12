# ProgramMind V2.0 数据库设计说明书

# Part03 —— Course Domain（课程体系数据库设计）

> 文档版本：V2.0
> 更新时间：2026-09
> 对应模块：课程中心、教学中心、知识库、RAG、学习中心

---

# 第一章 Course Domain 模块说明

## 1.1 模块职责

Course Domain 是 ProgramMind 的课程中心。

负责整个高校课程体系的数据组织。

包括：

- 专业（Major）
- 课程（Course）
- 章节（Chapter）
- 知识点（Knowledge Point）
- 学生选课（Enrollment）

整个项目所有 AI、RAG、Learning Mirror 都依赖这一层。

---

## 1.2 数据库结构

Course Domain 共 **5 张核心表**。

| 表名                 | 功能   |
| ------------------ | ---- |
| majors             | 专业信息 |
| courses            | 课程信息 |
| course_chapters    | 课程章节 |
| knowledge_points   | 知识点  |
| course_enrollments | 学生选课 |

ER 关系：

```text
majors
   │1
   │
   ▼N
courses
   │1
   ▼N
course_chapters
   │1
   ▼N
knowledge_points

users
   │1
   ▼N
course_enrollments
   │
   ▼
courses
```

一门课程拥有多个章节。

一个章节拥有多个知识点。

一个学生可以选修多门课程。

一个教师可以教授多门课程。

---

# 第二章 majors 表（专业）

## 2.1 表定位

保存高校专业信息。

ProgramMind 所有课程都属于某个专业。

AI 推荐课程也依赖专业。

---

## 2.2 字段设计

| 字段           | 类型           | 说明   |
| ------------ | ------------ | ---- |
| id           | CHAR(36)     | UUID |
| major_code   | VARCHAR(20)  | 专业代码 |
| major_name   | VARCHAR(100) | 专业名称 |
| college_name | VARCHAR(120) | 学院名称 |
| description  | TEXT         | 专业简介 |
| icon         | VARCHAR(255) | 图标   |
| color        | VARCHAR(20)  | 品牌色  |
| created_at   | DATETIME     | 创建时间 |
| updated_at   | DATETIME     | 更新时间 |

---

## 2.3 MySQL DDL

```sql
CREATE TABLE majors (

    id CHAR(36) PRIMARY KEY,

    major_code VARCHAR(20) UNIQUE NOT NULL,

    major_name VARCHAR(100) NOT NULL,

    college_name VARCHAR(120) NOT NULL,

    description TEXT,

    icon VARCHAR(255),

    color VARCHAR(20),

    created_at DATETIME(6),

    updated_at DATETIME(6)
);
```

---

## 2.4 初始化专业（Seed）

初始化至少五个专业：

| 专业代码   | 专业         |
| ------ | ---------- |
| AI2405 | 人工智能       |
| CS2401 | 计算机科学与技术   |
| SE2402 | 软件工程       |
| DS2406 | 数据科学与大数据技术 |
| NE2407 | 网络工程       |

后续支持新增专业。

---

## 2.5 SQLAlchemy Model

```python
class Major(Base, BaseModel):

    __tablename__ = "majors"

    major_code = mapped_column(String(20), unique=True)

    major_name = mapped_column(String(100))

    college_name = mapped_column(String(120))

    description = mapped_column(Text)

    icon = mapped_column(String(255))

    color = mapped_column(String(20))

    courses = relationship("Course")
```

---

# 第三章 courses 表（课程）

## 3.1 表定位

保存课程信息。

整个平台最核心的数据表。

所有模块都依赖 courses。

---

## 3.2 字段设计（完整版）

| 字段            | 类型           | 说明                       |
| ------------- | ------------ | ------------------------ |
| id            | CHAR(36)     | UUID                     |
| course_code   | VARCHAR(30)  | 课程编号                     |
| course_name   | VARCHAR(120) | 课程名称                     |
| major_id      | CHAR(36)     | FK majors                |
| teacher_id    | CHAR(36)     | FK users                 |
| semester      | VARCHAR(30)  | 学期                       |
| credit        | DECIMAL(3,1) | 学分                       |
| cover_image   | VARCHAR(255) | 封面                       |
| description   | LONGTEXT     | 简介                       |
| difficulty    | ENUM         | easy/medium/hard         |
| course_type   | ENUM         | required/elective        |
| status        | ENUM         | draft/published/archived |
| student_count | INT          | 学生人数                     |
| chapter_count | INT          | 章节数量                     |
| created_at    | DATETIME     | 创建时间                     |
| updated_at    | DATETIME     | 更新时间                     |

---

## 3.3 DDL

```sql
CREATE TABLE courses (

    id CHAR(36) PRIMARY KEY,

    course_code VARCHAR(30) UNIQUE NOT NULL,

    course_name VARCHAR(120) NOT NULL,

    major_id CHAR(36) NOT NULL,

    teacher_id CHAR(36) NOT NULL,

    semester VARCHAR(30),

    credit DECIMAL(3,1),

    cover_image VARCHAR(255),

    description LONGTEXT,

    difficulty ENUM('easy','medium','hard'),

    course_type ENUM('required','elective'),

    status ENUM('draft','published','archived'),

    student_count INT DEFAULT 0,

    chapter_count INT DEFAULT 0,

    created_at DATETIME(6),

    updated_at DATETIME(6),

    FOREIGN KEY (major_id) REFERENCES majors(id),

    FOREIGN KEY (teacher_id) REFERENCES users(id)
);
```

---

## 3.4 SQLAlchemy Model

```python
class Course(Base, BaseModel):

    __tablename__ = "courses"

    course_code = mapped_column(String(30), unique=True)

    course_name = mapped_column(String(120))

    major_id = mapped_column(ForeignKey("majors.id"))

    teacher_id = mapped_column(ForeignKey("users.id"))

    semester = mapped_column(String(30))

    credit = mapped_column(Float)

    cover_image = mapped_column(String(255))

    description = mapped_column(Text)

    difficulty = mapped_column(Enum(Difficulty))

    course_type = mapped_column(Enum(CourseType))

    status = mapped_column(Enum(CourseStatus))

    teacher = relationship("User")

    major = relationship("Major")

    chapters = relationship("CourseChapter")
```

---

## 3.5 初始化课程（Seed）

ProgramMind V2 Demo 初始化三门课程。

| 编号     | 名称         |
| ------ | ---------- |
| AI1001 | Python程序设计 |
| AI2001 | 数据结构       |
| AI3001 | 计算机网络      |

每门课程绑定教师。

封面 SVG 保留 Demo 资源。

---

## 3.6 Repository

```
CourseRepository

create_course()

update_course()

publish_course()

archive_course()

list_courses()

get_course()

delete_course()

update_student_count()
```

---

# 第四章 course_chapters 表（课程章节）

## 4.1 表定位

保存课程目录。

课程知识树第一层。

---

## 4.2 字段设计

| 字段              | 类型           | 说明              |
| --------------- | ------------ | --------------- |
| id              | CHAR(36)     | UUID            |
| course_id       | CHAR(36)     | FK courses      |
| chapter_number  | INT          | 顺序              |
| chapter_title   | VARCHAR(150) | 标题              |
| description     | TEXT         | 描述              |
| estimated_hours | INT          | 学时              |
| knowledge_count | INT          | 知识点数量           |
| status          | ENUM         | published/draft |
| created_at      | DATETIME     | 创建时间            |
| updated_at      | DATETIME     | 更新时间            |

---

## 4.3 DDL

```sql
CREATE TABLE course_chapters (

    id CHAR(36) PRIMARY KEY,

    course_id CHAR(36) NOT NULL,

    chapter_number INT NOT NULL,

    chapter_title VARCHAR(150),

    description TEXT,

    estimated_hours INT,

    knowledge_count INT DEFAULT 0,

    status ENUM('draft','published'),

    created_at DATETIME(6),

    updated_at DATETIME(6),

    FOREIGN KEY(course_id)
        REFERENCES courses(id)
        ON DELETE CASCADE
);
```

---

## 4.4 SQLAlchemy

```python
class CourseChapter(Base, BaseModel):

    __tablename__ = "course_chapters"

    course_id = mapped_column(ForeignKey("courses.id"))

    chapter_number = mapped_column(Integer)

    chapter_title = mapped_column(String(150))

    estimated_hours = mapped_column(Integer)

    knowledge_count = mapped_column(Integer)

    course = relationship("Course")

    knowledge_points = relationship("KnowledgePoint")
```

---

## 4.5 初始化 Python 章节

| 顺序  | 标题       |
| --- | -------- |
| 1   | Python基础 |
| 2   | 变量与数据类型  |
| 3   | 流程控制     |
| 4   | 函数       |
| 5   | 列表与元组    |
| 6   | 字典与集合    |
| 7   | 文件操作     |
| 8   | 面向对象     |
| 9   | 异常处理     |
| 10  | 综合项目实践   |

数据结构、计网同理初始化。

---

# 第五章 knowledge_points 表（知识点）

## 5.1 表定位

课程知识树第二层。

Learning Mirror 与 RAG 都围绕知识点展开。

---

## 5.2 字段设计

| 字段                 | 类型           | 说明               |
| ------------------ | ------------ | ---------------- |
| id                 | CHAR(36)     | UUID             |
| chapter_id         | CHAR(36)     | FK chapter       |
| knowledge_code     | VARCHAR(30)  | 知识点编号            |
| knowledge_name     | VARCHAR(120) | 名称               |
| description        | TEXT         | 描述               |
| difficulty         | ENUM         | easy/medium/hard |
| importance         | ENUM         | low/medium/high  |
| prerequisite_id    | CHAR(36)     | 前置知识点            |
| learning_objective | TEXT         | 学习目标             |
| created_at         | DATETIME     | 创建时间             |
| updated_at         | DATETIME     | 更新时间             |

---

## 5.3 DDL

```sql
CREATE TABLE knowledge_points (

    id CHAR(36) PRIMARY KEY,

    chapter_id CHAR(36),

    knowledge_code VARCHAR(30),

    knowledge_name VARCHAR(120),

    description TEXT,

    difficulty ENUM('easy','medium','hard'),

    importance ENUM('low','medium','high'),

    prerequisite_id CHAR(36),

    learning_objective TEXT,

    created_at DATETIME(6),

    updated_at DATETIME(6),

    FOREIGN KEY(chapter_id)
        REFERENCES course_chapters(id)
        ON DELETE CASCADE
);
```

---

## 5.4 SQLAlchemy

```python
class KnowledgePoint(Base, BaseModel):

    __tablename__="knowledge_points"

    chapter_id = mapped_column(ForeignKey("course_chapters.id"))

    knowledge_code = mapped_column(String(30))

    knowledge_name = mapped_column(String(120))

    difficulty = mapped_column(Enum(Difficulty))

    importance = mapped_column(Enum(Importance))

    prerequisite_id = mapped_column(ForeignKey("knowledge_points.id"))

    learning_objective = mapped_column(Text)
```

---

## 5.5 Python 知识点初始化（示例）

章节《列表与元组》

| 编号     | 知识点             |
| ------ | --------------- |
| PY0501 | List 创建         |
| PY0502 | List 索引         |
| PY0503 | List 切片         |
| PY0504 | append / extend |
| PY0505 | List 推导式        |
| PY0506 | Tuple           |

---

## 5.6 前置知识关系

例如：

```
变量

↓

列表

↓

列表推导式

↓

生成器
```

形成 DAG。

Learning Path 推荐依赖这里。

---

# 第六章 course_enrollments 表（学生选课）

## 6.1 表定位

记录学生课程关系。

替代 Demo enrollments。

---

## 6.2 字段设计

| 字段                 | 类型           |
| ------------------ | ------------ |
| id                 | UUID         |
| student_id         | FK users     |
| course_id          | FK courses   |
| progress           | DECIMAL(5,2) |
| completed_chapters | INT          |
| learning_hours     | INT          |
| status             | ENUM         |
| joined_at          | DATETIME     |
| finished_at        | DATETIME     |

---

## 6.3 DDL

```sql
CREATE TABLE course_enrollments (

    id CHAR(36) PRIMARY KEY,

    student_id CHAR(36),

    course_id CHAR(36),

    progress DECIMAL(5,2) DEFAULT 0,

    completed_chapters INT DEFAULT 0,

    learning_hours INT DEFAULT 0,

    status ENUM(
        'learning',
        'completed',
        'dropped'
    ),

    joined_at DATETIME(6),

    finished_at DATETIME(6),

    FOREIGN KEY(student_id)
        REFERENCES users(id),

    FOREIGN KEY(course_id)
        REFERENCES courses(id)
);
```

---

## 6.4 SQLAlchemy

```python
class CourseEnrollment(Base, BaseModel):

    __tablename__="course_enrollments"

    student_id = mapped_column(ForeignKey("users.id"))

    course_id = mapped_column(ForeignKey("courses.id"))

    progress = mapped_column(Float)

    completed_chapters = mapped_column(Integer)

    learning_hours = mapped_column(Integer)

    status = mapped_column(Enum(EnrollmentStatus))
```

---

## 6.5 Progress 更新规则

Progress 来源：

- 作业
- 实验
- 测验
- 学习记录

计算：

```
Progress

=

完成章节 / 总章节 ×100
```

自动更新。

---

# 第七章 课程知识树设计（ProgramMind 核心）

课程结构采用三级树。

```text
Course

├── Chapter

│     ├── Knowledge Point

│     ├── Knowledge Point

│     └── Knowledge Point

└── Chapter
```

RAG 检索粒度：

Chunk 属于 Knowledge Point。

Knowledge Point 属于 Chapter。

Chapter 属于 Course。

---

## 示例（Python）

```text
Python程序设计

├── 第五章 列表

│   ├── List创建

│   ├── List索引

│   ├── List切片

│   ├── append()

│   └── 推导式
```

---

# 第八章 Course Service 设计

## CourseService

负责：

创建课程。

发布课程。

更新课程。

课程列表。

课程详情。

教师课程。

学生课程。

---

## ChapterService

负责：

章节 CRUD。

章节排序。

章节统计。

章节发布。

---

## KnowledgeService

负责：

知识点 CRUD。

知识点关系。

知识点搜索。

知识点推荐。

---

## EnrollmentService

负责：

学生选课。

退课。

更新进度。

学习统计。

---

# 第九章 Repository 设计

## MajorRepository

```
create()

list()

get()

update()
```

---

## CourseRepository

```
create()

publish()

archive()

list_teacher_courses()

list_student_courses()

update_student_count()
```

---

## ChapterRepository

```
create()

update()

reorder()

delete()

list_by_course()
```

---

## KnowledgeRepository

```
create()

update()

search()

list_by_chapter()

get_prerequisite()
```

---

## EnrollmentRepository

```
enroll()

drop()

get_progress()

update_progress()

list_students()
```

---

# 第十章 索引设计（Course Domain）

| 表                | 索引                            |
| ---------------- | ----------------------------- |
| courses          | course_code UNIQUE            |
| courses          | teacher_id INDEX              |
| courses          | major_id INDEX                |
| course_chapters  | course_id + chapter_number    |
| knowledge_points | chapter_id INDEX              |
| knowledge_points | prerequisite_id INDEX         |
| enrollments      | student_id + course_id UNIQUE |

保证课程查询效率。

---

# 第十一章 初始化数据（Seed）

初始化课程目录。

Python：

10章。

知识点约45个。

数据结构：

9章。

知识点约52个。

计算机网络：

8章。

知识点约48个。

总知识点：

145个左右。

这些知识点未来导入 RAG。

---

# 第十二章 Backend Checklist（Course Domain）

## Major

- [ ] majors表
- [ ] 专业Seed

## Course

- [ ] courses表
- [ ] 教师绑定
- [ ] 发布状态

## Chapter

- [ ] chapter CRUD
- [ ] 排序
- [ ] 学时统计

## Knowledge Point

- [ ] 知识点CRUD
- [ ] 前置依赖
- [ ] 搜索

## Enrollment

- [ ] 学生选课
- [ ] 更新学习进度
- [ ] 学习时长统计

---

# 本章开发成果

完成 Course Domain 后，ProgramMind 将具备：

- 多专业课程体系。
- 多教师课程管理。
- 章节目录系统。
- 知识点树。
- 学生选课关系。
- Learning、RAG、Growth 共用课程基础数据。
