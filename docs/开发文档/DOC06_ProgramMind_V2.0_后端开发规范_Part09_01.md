# ProgramMind V2.0 后端开发规范

# Part09.1 —— Docker Architecture（容器化架构设计）

> 文档版本：V2.0
> 更新时间：2026-09
> 模块负责人：Backend Infrastructure / DevOps
> 技术栈：Docker + Docker Compose + FastAPI + Vue + Redis + MySQL + Ollama + MinIO

---

# 第一章 Docker Architecture 模块定位

## 1.1 为什么使用 Docker

ProgramMind 是多服务 AI 平台。

包含：

- Vue 前端
- FastAPI Backend
- MySQL
- Redis
- Ollama
- MinIO
- Celery Worker
- Celery Beat
- Nginx

Docker 保证所有成员环境一致。

---

## 1.2 Docker 架构目标

ProgramMind Docker 满足：

- 一键启动全部服务。
- 本地开发一致。
- Demo 环境快速部署。
- 后续服务器部署一致。
- 服务隔离。

---

## 1.3 容器架构图

Frontend (Vue + Nginx)

↓

Nginx Gateway

↓

FastAPI Backend

↓

Redis

↓

MySQL

↓

MinIO

↓

Ollama

↓

Celery Worker

↓

Celery Beat

全部位于 Docker Network。

---

# 第二章 Docker 总体目录规范

## 2.1 deploy 目录

```text
deploy/

docker/

backend/

frontend/

nginx/

mysql/

redis/

ollama/

minio/

scripts/

.env.dev

.env.demo

.env.prod

docker-compose.dev.yml

docker-compose.demo.yml

docker-compose.prod.yml
```

开发、Demo、生产环境分离。

---

## 2.2 Dockerfile 分类

| Dockerfile           | 用途            |
| -------------------- | ------------- |
| Dockerfile.backend   | FastAPI       |
| Dockerfile.frontend  | Vue           |
| Dockerfile.worker    | Celery Worker |
| Dockerfile.scheduler | Celery Beat   |

每个服务一个 Dockerfile。

---

# 第三章 Docker Network 设计

## 3.1 网络规划

统一网络：

programmind-network

所有服务加入同一网络。

---

## 3.2 网络拓扑

Nginx

↓

Backend

↓

Redis

MySQL

MinIO

Ollama

Celery Worker

Celery Beat

服务之间通过 Service Name 通信。

---

## 3.3 网络命名规范

固定 Service Name：

backend

frontend

mysql

redis

minio

ollama

worker

beat

禁止 localhost 通信。

---

# 第四章 Backend Docker 容器规范

## 4.1 Backend 容器职责

运行：

FastAPI API。

AI Router。

RAG API。

Growth API。

Storage API。

---

## 4.2 Dockerfile.backend

包含：

Python。

Poetry/Pip。

Requirements。

Uvicorn。

Environment。

---

## 4.3 Backend Volume

挂载：

uploads/

logs/

knowledge/

避免容器删除数据。

---

## 4.4 Backend Environment

加载：

.env.dev。

.env.demo。

.env.prod。

配置隔离。

---

# 第五章 Frontend Docker 容器规范

## 5.1 Frontend 容器职责

Vue3 Build。

静态资源。

Nginx 提供访问。

---

## 5.2 Build 流程

Node Build。

↓

dist/

↓

Nginx Image。

---

## 5.3 Volume

静态资源无需挂载。

生产镜像仅包含 dist。

---

# 第六章 MySQL Docker 容器

## 6.1 MySQL 配置

MySQL8。

UTF8MB4。

Asia/Shanghai。

---

## 6.2 Volume

保存：

mysql-data/

永久数据。

---

## 6.3 初始化 SQL

启动时执行：

init.sql。

seed.sql（可选）。

---

## 6.4 Backup Volume

backup/mysql/

自动备份。

---

# 第七章 Redis Docker 容器

## 7.1 Redis 配置

Redis7。

AppendOnly。

Persistence。

---

## 7.2 Volume

redis-data/

保存持久化数据。

---

## 7.3 Redis Database 划分

| DB  | 用途            |
| --- | ------------- |
| 0   | Celery Broker |
| 1   | Celery Result |
| 2   | Cache         |
| 3   | Session       |
| 4   | Rate Limit    |

统一管理。

---

# 第八章 Ollama Docker 容器

## 8.1 Ollama 职责

本地 AI 模型服务。

---

## 8.2 模型目录

ollama-models/

Volume 挂载。

避免重复下载。

---

## 8.3 模型初始化

启动检查：

Qwen3。

DeepSeek。

BGE-M3。

不存在提示下载。

---

## 8.4 GPU 支持（预留）

支持 NVIDIA Runtime。

CPU 自动降级。

---

# 第九章 MinIO Docker 容器

## 9.1 MinIO 职责

对象存储。

教材。

头像。

AI 报告。

---

## 9.2 Bucket 初始化

avatars

knowledge

courses

reports

自动创建。

---

## 9.3 Volume

minio-data/

永久保存对象。

---

# 第十章 Celery Worker Docker

## 10.1 Worker 职责

执行：

AI。

RAG。

Mirror。

Storage。

Report。

---

## 10.2 Worker Queue

监听多个 Queue。

可扩展多个 Worker。

---

## 10.3 Worker Volume

共享：

knowledge/

uploads/

logs/

---

# 第十一章 Celery Beat Docker

## 11.1 Beat 职责

Scheduler。

每日。

每周。

每月任务。

---

## 11.2 Beat Volume

共享配置。

日志。

无需数据库。

---

# 第十二章 Docker Compose（核心）

## 12.1 Compose 服务列表

| Service  | 作用        |
| -------- | --------- |
| backend  | API       |
| frontend | Vue       |
| mysql    | 数据库       |
| redis    | 缓存        |
| minio    | 文件        |
| ollama   | AI        |
| worker   | Celery    |
| beat     | Scheduler |
| nginx    | 网关        |

---

## 12.2 启动顺序

MySQL

↓

Redis

↓

MinIO

↓

Ollama

↓

Backend

↓

Worker

↓

Beat

↓

Frontend

↓

Nginx

---

## 12.3 Depends On

Backend 等待：

MySQL。

Redis。

MinIO。

Worker 等待 Backend。

---

# 第十三章 Environment 配置规范

## 13.1 环境文件

.env.dev

.env.demo

.env.prod

禁止写入 Git。

---

## 13.2 Backend ENV 分类

DATABASE_URL

REDIS_URL

MINIO_URL

OLLAMA_URL

SECRET_KEY

JWT_SECRET

---

## 13.3 Frontend ENV

VITE_API_BASE

VITE_UPLOAD_BASE

VITE_STORAGE_BASE

统一代理。

---

# 第十四章 Docker Volume 设计

## Volume 列表

| Volume          | 内容    |
| --------------- | ----- |
| mysql-data      | 数据库   |
| redis-data      | Redis |
| minio-data      | MinIO |
| ollama-models   | AI模型  |
| backend-uploads | 上传文件  |
| backend-logs    | 日志    |

全部持久化。

---

## Volume 生命周期

删除容器。

数据保留。

升级镜像。

数据不丢失。

---

# 第十五章 Docker Health Check

## Backend Health

GET /system/health

---

## MySQL Health

mysqladmin ping

---

## Redis Health

redis-cli ping

---

## Ollama Health

/api/tags

检查模型状态。

---

## MinIO Health

Bucket Ping。

---

# 第十六章 Docker Compose 环境划分

## Development

热更新。

Volume 挂载源码。

Debug 开启。

---

## Demo

关闭 Debug。

启用 MinIO。

启用 Ollama。

适合挑战杯演示。

---

## Production（预留）

HTTPS。

OSS。

GPU。

多 Worker。

---

# 第十七章 Docker 部署 Checklist

## Containers

- [ ] Backend
- [ ] Frontend
- [ ] MySQL
- [ ] Redis
- [ ] Ollama
- [ ] MinIO
- [ ] Worker
- [ ] Beat
- [ ] Nginx

## Network

- [ ] programmind-network
- [ ] Health Check
- [ ] Depends On

## Storage

- [ ] Volume
- [ ] Bucket
- [ ] Logs
- [ ] Uploads

---

# 第十八章 本章开发成果

完成 Part09.1 后，ProgramMind Backend 将具备：

- Docker 多容器架构。
- Docker Compose 一键启动。
- Backend / Frontend / AI 服务解耦。
- MySQL、Redis、MinIO、Ollama 持久化。
- Celery Worker 与 Beat 容器化。
- 开发 / Demo / 生产三套环境配置。
