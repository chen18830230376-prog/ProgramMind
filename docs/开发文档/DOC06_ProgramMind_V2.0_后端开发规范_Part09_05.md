# ProgramMind V2.0 后端开发规范

# Part09.5 —— Deployment Manual（服务器部署与运维手册）

> 文档版本：V2.0
> 更新时间：2026-09
> 模块负责人：Project Lead / DevOps
> 技术栈：Ubuntu 22.04 + Docker Compose + Nginx + MySQL + Redis + Ollama + MinIO

---

# 第一章 Deployment Manual 模块定位

## 1.1 文档职责

Deployment Manual 是 ProgramMind 的完整上线部署说明书。

适用于：

- 本地开发环境
- 挑战杯 Demo 环境
- Linux 云服务器
- Docker Compose 一键部署

目标是保证任何团队成员都能按照文档完成部署。

---

## 1.2 支持部署环境

| 环境          | 推荐方案                   |
| ----------- | ---------------------- |
| Windows 开发  | Docker Desktop         |
| macOS 开发    | Docker Desktop         |
| Ubuntu Demo | Docker Compose         |
| 阿里云 Ubuntu  | Docker Compose + Nginx |
| 宝塔 Linux    | Docker Compose + Nginx |

统一部署方式。

---

## 1.3 部署原则

- 环境配置全部来自 `.env`
- 数据持久化使用 Docker Volume
- 所有服务健康检查通过后上线
- 支持快速回滚

---

# 第二章 服务器配置建议

## 2.1 Challenge Cup Demo 推荐配置

| 配置项    | 推荐值       |
| ------ | --------- |
| CPU    | 4 Core    |
| 内存     | 8 GB      |
| SSD    | 80 GB     |
| Ubuntu | 22.04 LTS |

可同时运行 Ollama + MySQL + Redis。

---

## 2.2 最低配置

| 配置项 | 最低     |
| --- | ------ |
| CPU | 2 Core |
| 内存  | 4 GB   |
| SSD | 50 GB  |

适合演示。

---

## 2.3 推荐开放端口

| 端口    | 服务         |
| ----- | ---------- |
| 80    | HTTP       |
| 443   | HTTPS      |
| 9000  | MinIO（内网）  |
| 11434 | Ollama（内网） |
| 6379  | Redis（内网）  |
| 3306  | MySQL（内网）  |

数据库不对公网开放。

---

# 第三章 Linux 环境初始化

## 3.1 更新系统

更新 apt 软件源。

安装 curl、git、vim 等基础工具。

---

## 3.2 安装 Docker

安装 Docker Engine。

安装 Docker Compose Plugin。

配置 Docker 开机启动。

---

## 3.3 创建部署目录

推荐目录结构：

```text
/opt/programmind/

backend/

frontend/

deploy/

uploads/

logs/

backup/
```

统一部署位置。

---

# 第四章 项目目录部署规范

## 4.1 Git Clone

克隆 GitHub 仓库。

进入 deploy 目录。

切换 release 标签。

---

## 4.2 环境文件准备

复制：

`.env.demo`

生成：

`.env`

填写：

数据库密码。

JWT Secret。

MinIO Key。

Ollama 地址。

---

## 4.3 上传目录初始化

创建：

avatars/

knowledge/

courses/

reports/

temp/

赋予 Docker 用户权限。

---

# 第五章 Docker Compose 一键部署

## 5.1 Compose 文件

推荐：

docker-compose.demo.yml

作为比赛部署版本。

---

## 5.2 启动顺序

MySQL。

Redis。

MinIO。

Ollama。

Backend。

Worker。

Beat。

Frontend。

Nginx。

---

## 5.3 首次启动检查

检查所有容器状态。

确认全部 Healthy。

---

# 第六章 数据库初始化流程

## 6.1 Alembic Migration

执行：

最新 Migration。

创建全部表。

---

## 6.2 Seed 初始化

导入：

管理员账号。

课程分类。

默认角色。

系统配置。

---

## 6.3 初始化验证

检查：

users。

roles。

permissions。

courses。

knowledge_sources。

全部存在。

---

# 第七章 Ollama 模型初始化

## 7.1 模型检查

必须存在：

Qwen。

DeepSeek。

Embedding 模型。

---

## 7.2 首次下载模型

下载后保存 Docker Volume。

避免重复下载。

---

## 7.3 模型健康检查

调用：

/api/tags

确认模型加载成功。

---

# 第八章 MinIO 初始化

## 8.1 Bucket 创建

创建：

avatars

knowledge

courses

reports

---

## 8.2 AccessKey 配置

保存到：

.env

Backend 自动读取。

---

## 8.3 Bucket 权限

默认私有。

下载走 Backend API。

---

# 第九章 Nginx 配置上线

## 9.1 部署 Vue Dist

构建 dist。

复制到 nginx/html。

---

## 9.2 Backend Proxy

代理：

/api

/uploads

/storage

/healthz

---

## 9.3 HTTPS 配置

部署 SSL。

HTTP 自动跳 HTTPS。

---

# 第十章 上线检查清单（重点）

## 10.1 Backend 检查

- [ ] API 正常
- [ ] JWT 登录成功
- [ ] AI Chat 返回
- [ ] SSE Streaming 正常

---

## 10.2 AI 检查

- [ ] Ollama 在线
- [ ] AI Tutor 工作
- [ ] Recommendation 正常
- [ ] Memory 正常

---

## 10.3 RAG 检查

- [ ] PDF 上传
- [ ] Chunk 成功
- [ ] Embedding 成功
- [ ] Citation 返回

---

## 10.4 Growth 检查

- [ ] Mirror 更新
- [ ] Risk 更新
- [ ] Dashboard 更新
- [ ] Report 生成

---

# 第十一章 Docker 运维命令规范

## 常用操作

启动。

停止。

重启。

查看日志。

进入容器。

查看健康状态。

统一使用 docker compose。

---

## Worker 操作

查看 Queue。

重启 Worker。

查看 Beat 日志。

---

# 第十二章 Backup 与 Restore 运维

## 12.1 Backup 周期

每日：

MySQL。

每周：

FAISS。

MinIO。

每月：

完整 Backup。

---

## 12.2 Backup 目录

backup/

mysql/

faiss/

minio/

reports/

按日期保存。

---

## 12.3 Restore 流程

停止 Backend。

恢复数据库。

恢复对象存储。

恢复索引。

刷新 Cache。

启动服务。

---

# 第十三章 日志运维规范

## 日志目录

logs/

backend/

worker/

scheduler/

nginx/

mysql/

统一分类。

---

## 日志轮转

每天切分。

保留 30 天。

自动压缩历史日志。

---

## 故障定位顺序

Nginx。

Backend。

Worker。

Redis。

MySQL。

Ollama。

逐层排查。

---

# 第十四章 常见故障排查 SOP

## Backend 无法启动

检查：

.env。

数据库连接。

Redis。

Migration。

---

## Ollama 无响应

检查：

模型。

端口。

Docker Volume。

内存。

---

## SSE 中断

检查：

Nginx Buffer。

Timeout。

Backend Streaming。

---

## MinIO 上传失败

检查：

Bucket。

AccessKey。

Permission。

Storage Provider。

---

## Celery 不执行

检查：

Redis Broker。

Worker。

Beat。

Queue。

---

# 第十五章 Demo 环境快速恢复 SOP

## 比赛现场恢复流程（10 分钟）

1. 启动 Docker。
2. 启动 Compose。
3. Health Check。
4. 登录管理员。
5. 测试 AI Tutor。
6. 上传教材测试 RAG。
7. 打开 Dashboard。

完成 Demo。

---

## 离线 Demo 方案

预置：

Embedding。

FAISS。

Mirror。

Recommendation。

无需联网即可演示。

---

# 第十六章 Deployment Checklist（完整版）

## 环境准备

- [ ] Ubuntu 更新
- [ ] Docker 安装
- [ ] Docker Compose 安装

## 服务部署

- [ ] MySQL
- [ ] Redis
- [ ] MinIO
- [ ] Ollama
- [ ] Backend
- [ ] Worker
- [ ] Beat
- [ ] Frontend
- [ ] Nginx

## AI 功能

- [ ] AI Tutor
- [ ] RAG 检索
- [ ] Citation
- [ ] Growth Dashboard
- [ ] Weekly Report

## 运维

- [ ] Backup
- [ ] Restore
- [ ] Health Check
- [ ] Logs
- [ ] Monitoring

---

# 第十七章 本章开发成果

完成 Part09.5 后，ProgramMind Backend 将具备：

- Docker Compose 一键部署。
- Linux/宝塔部署流程。
- 数据库初始化规范。
- Ollama 与 MinIO 初始化规范。
- HTTPS 与 Nginx 上线流程。
- Backup & Restore SOP。
- Demo 环境快速恢复流程。
- 完整运维检查清单。
