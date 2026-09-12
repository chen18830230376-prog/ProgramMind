# ProgramMind V2.0 后端开发规范

# Part08.2 —— File Upload Engine（文件上传与对象存储引擎）

> 文档版本：V2.0
> 更新时间：2026-09
> 模块负责人：Backend Infrastructure
> 技术栈：FastAPI + MinIO + Alibaba OSS + Local Storage + SQLAlchemy

---

# 第一章 File Upload Engine 模块定位

## 1.1 模块职责

File Upload Engine 是 ProgramMind Backend 的统一文件管理中心。

负责：

- 用户头像上传
- 教材上传
- PPT 上传
- PDF 上传
- Word 上传
- 图片上传
- 实验资源上传
- RAG 文档上传
- 文件权限管理
- 文件删除与版本管理

统一通过 Storage Service 管理。

---

## 1.2 文件系统在平台中的位置

Vue Upload

↓

Storage Router

↓

Storage Service

↓

Local / MinIO / OSS

↓

MySQL File Metadata

↓

Knowledge Parser（RAG）

---

## 1.3 支持的文件类型

| 文件类型      | 用途         |
| --------- | ---------- |
| PDF       | 教材、论文、实验指导 |
| DOCX      | 教案、课程文档    |
| PPTX      | 教学 PPT     |
| TXT / MD  | RAG 文档     |
| PNG / JPG | 图片资源       |
| WEBP      | 图片优化       |
| ZIP（管理员）  | 批量课程资源     |

---

# 第二章 Storage Engine 总体架构

## 2.1 Storage 模块目录

```text
storage/

storage_service.py

storage_manager.py

local_storage.py

minio_storage.py

oss_storage.py

file_validator.py

file_hash.py

image_processor.py

permission_manager.py
```

所有上传逻辑统一走 StorageService。

---

## 2.2 Storage Provider 架构

Storage Service

↓

Storage Provider

↓

Local Storage

↓

MinIO Storage

↓

OSS Storage

Provider 可切换。

---

## 2.3 环境策略

| 环境                 | Provider      |
| ------------------ | ------------- |
| Development        | Local Storage |
| Challenge Cup Demo | MinIO         |
| Production（预留）     | Alibaba OSS   |

统一配置 ENV。

---

# 第三章 上传目录规范（核心）

## 3.1 根目录结构

```text
uploads/

avatars/

courses/

knowledge/

assignments/

experiments/

reports/

temp/
```

目录职责固定。

---

## 3.2 avatars/

保存：

用户头像。

教师头像。

管理员头像。

自动压缩。

---

## 3.3 knowledge/

保存：

教材。

PDF。

PPT。

Markdown。

TXT。

RAG Parser 自动监听。

---

## 3.4 courses/

保存课程资源：

实验指导书。

课件。

附件。

图片。

视频（预留）。

---

## 3.5 reports/

保存 AI 自动生成：

成长报告。

教师报告。

PDF。

Markdown。

---

# 第四章 File Metadata 数据库设计

## 4.1 uploaded_files 表

数据库保存：

文件元信息。

不保存文件本身。

---

## 4.2 字段设计

| 字段               | 描述              |
| ---------------- | --------------- |
| file_id          | UUID            |
| filename         | 原始名称            |
| storage_name     | 存储名称            |
| storage_provider | local/minio/oss |
| file_size        | 文件大小            |
| file_hash        | SHA256          |
| mime_type        | MIME            |
| uploader_id      | 上传者             |
| permission       | 权限              |
| created_at       | 上传时间            |

---

## 4.3 JSON Schema

```json
{
 "filename":"Python基础.pdf",
 "storage_provider":"minio",
 "file_hash":"..."
}
```

---

# 第五章 File Validator（文件校验）

## 5.1 Validator 职责

上传前统一校验：

格式。

大小。

MIME。

权限。

病毒扫描（预留）。

---

## 5.2 文件大小限制

| 类型     | 最大大小  |
| ------ | ----- |
| Avatar | 5MB   |
| PDF    | 50MB  |
| PPT    | 100MB |
| DOCX   | 30MB  |
| ZIP    | 200MB |

后台统一配置。

---

## 5.3 MIME 校验

禁止仅判断扩展名。

同时验证：

Content-Type。

Magic Number。

提升安全性。

---

# 第六章 File Hash 去重机制

## 6.1 为什么 Hash 去重

相同教材无需重复上传。

节省存储。

---

## 6.2 Hash 算法

SHA256。

整个文件计算。

---

## 6.3 去重流程

上传。

↓

计算 Hash。

↓

数据库查询。

存在。

↓

直接返回已有文件。

不存在。

↓

继续上传。

---

## 6.4 Hash 字段用途

文件版本。

缓存。

RAG Embedding。

重复检测。

---

# 第七章 Local Storage Provider

## 7.1 开发环境目录

```text
backend/uploads/

avatars/

knowledge/

courses/
```

Docker 挂载。

---

## 7.2 文件命名规范

UUID + 原扩展名。

例如：

uuid.pdf。

避免重名。

---

## 7.3 URL 映射

Static Files。

统一：

/uploads/**

FastAPI StaticFiles 提供访问。

---

# 第八章 MinIO Storage Provider

## 8.1 MinIO 定位

Challenge Cup Demo 推荐。

本地对象存储。

---

## 8.2 Bucket 规划

| Bucket        | 内容    |
| ------------- | ----- |
| avatars       | 用户头像  |
| knowledge     | 教材知识库 |
| course-assets | 课程资源  |
| reports       | AI 报告 |

Bucket 固定。

---

## 8.3 上传流程

Storage Service

↓

MinIO Client

↓

Bucket

↓

Object URL

↓

数据库 Metadata。

---

## 8.4 MinIO URL

数据库保存：

Object Name。

Public URL（可选）。

Presigned URL（下载）。

---

# 第九章 Alibaba OSS Provider（预留）

## 9.1 OSS 定位

生产部署。

云对象存储。

---

## 9.2 Bucket 分类

与 MinIO 保持一致。

支持平滑迁移。

---

## 9.3 CDN 支持（预留）

头像。

图片。

PDF。

静态资源 CDN。

---

# 第十章 Image Processor

## 10.1 图片处理职责

头像裁剪。

压缩。

缩略图。

WebP 转换。

---

## 10.2 Avatar 处理流程

上传。

↓

裁剪。

↓

256×256。

↓

压缩。

↓

WebP。

↓

保存。

---

## 10.3 教材图片处理

生成：

Thumbnail。

Preview。

原图。

供 Dashboard 使用。

---

# 第十一章 文档上传到 RAG（核心）

## 11.1 上传流程

PDF 上传

↓

Storage Save

↓

Knowledge Parser

↓

Chunk

↓

Embedding

↓

FAISS Index

↓

Knowledge Metadata

自动进入知识库。

---

## 11.2 支持解析格式

PDF。

DOCX。

Markdown。

TXT。

PPT（文本提取）。

---

## 11.3 Parser 输出

Chunk。

Metadata。

Embedding Queue。

Citation。

---

# 第十二章 File Permission Manager

## 12.1 权限模型

| 文件类型            | 权限                |
| --------------- | ----------------- |
| Avatar          | Owner             |
| Course Resource | Course Members    |
| Knowledge       | Teacher/Admin     |
| Report          | Owner             |
| Assignment      | Student + Teacher |

---

## 12.2 Permission Levels

private。

course。

teacher。

admin。

public（预留）。

---

## 12.3 下载权限

Storage Router 校验 JWT。

禁止直接访问对象存储。

统一通过 API。

---

# 第十三章 文件删除与版本管理

## 13.1 删除策略

软删除 Metadata。

对象存储异步删除。

---

## 13.2 Version 管理

教材更新。

保留 Version。

RAG 自动重新索引。

---

## 13.3 Garbage Collector

每天凌晨：

删除：

临时文件。

失效版本。

孤立对象。

---

# 第十四章 Upload API 设计

## API 列表

| API                           | 描述   |
| ----------------------------- | ---- |
| POST /storage/upload/avatar   | 上传头像 |
| POST /storage/upload/document | 上传文档 |
| POST /storage/upload/image    | 上传图片 |
| GET /storage/file/{id}        | 获取文件 |
| DELETE /storage/file/{id}     | 删除文件 |
| GET /storage/download/{id}    | 下载文件 |

DOC04 API 对应。

---

## 上传响应

返回：

file_id。

filename。

size。

provider。

url。

---

# 第十五章 Storage Service Checklist

## Upload

- [ ] Avatar Upload
- [ ] Document Upload
- [ ] Image Upload
- [ ] PPT Upload
- [ ] PDF Upload

## Provider

- [ ] Local Storage
- [ ] MinIO Storage
- [ ] OSS Storage

## Security

- [ ] MIME Validation
- [ ] File Size Validation
- [ ] Permission Validation
- [ ] Hash Deduplication

## RAG

- [ ] Auto Parser
- [ ] Auto Chunk
- [ ] Auto Embedding
- [ ] Auto Index

---

# 第十六章 本章开发成果

完成 Part08.2 后，ProgramMind Backend 将具备：

- 多 Provider 文件存储架构。
- Local / MinIO / OSS 三套方案。
- 文件 Hash 去重机制。
- 图片压缩与头像处理。
- RAG 文档自动入库流程。
- 文件权限管理。
- 文件版本管理与垃圾回收。
- Upload API 完整规范。
