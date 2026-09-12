# ProgramMind V2.0 后端开发规范

# Part09.2 —— Nginx Gateway（反向代理与网关层）

> 文档版本：V2.0
> 更新时间：2026-09
> 模块负责人：Backend Infrastructure / DevOps
> 技术栈：Nginx + Docker + FastAPI + Vue + SSE + HTTPS

---

# 第一章 Nginx Gateway 模块定位

## 1.1 Gateway 职责

Nginx 是 ProgramMind 所有客户端请求的统一入口。

负责：

- Vue 前端静态资源托管。
- FastAPI API 反向代理。
- AI Streaming（SSE）代理。
- 文件下载代理。
- HTTPS。
- Gzip/Brotli。
- Cache-Control。
- CORS。
- 安全 Header。

所有请求必须经过 Gateway。

---

## 1.2 Gateway 架构

Browser

↓

Nginx Gateway

↓

Frontend Dist

Backend API

Uploads

MinIO

SSE

WebSocket（预留）

---

## 1.3 Gateway 原则

ProgramMind Gateway 满足：

- 单入口。
- 高性能。
- 支持 Streaming。
- 安全默认开启。
- 静态资源缓存。

---

# 第二章 Nginx 目录规范

## 2.1 deploy/nginx/

nginx/

Dockerfile

nginx.conf

conf.d/

programmind.conf

ssl/

cert.pem

key.pem

logs/

access.log

error.log

mime.types

目录固定。

---

## 2.2 配置文件分类

| 文件               | 用途    |
| ---------------- | ----- |
| nginx.conf       | 主配置   |
| programmind.conf | 项目配置  |
| ssl/             | HTTPS |
| logs/            | 日志    |

---

## 2.3 Docker 挂载目录

Volume：

dist/

uploads/

logs/

ssl/

---

# 第三章 Vue 静态资源部署

## 3.1 Vue Dist

Frontend Build 后：

dist/

Nginx Root 指向 dist。

---

## 3.2 SPA 路由支持

Vue Router 使用 History 模式。

所有未知路径：

返回 index.html。

避免刷新404。

---

## 3.3 Static Resource 路径

assets/

images/

icons/

fonts/

缓存一年。

---

# 第四章 FastAPI API 反向代理

## 4.1 API Prefix

统一：

/api/v1/

代理 Backend。

---

## 4.2 Backend Upstream

Nginx Upstream：

backend:8000。

Docker Service Name。

---

## 4.3 Proxy Header

Forward：

Host。

IP。

Authorization。

Request ID。

保持 JWT 可用。

---

## 4.4 Timeout 配置

普通 API：

60 秒。

AI API：

300 秒。

SSE 单独配置。

---

# 第五章 SSE（AI Streaming）配置（核心）

## 5.1 为什么特殊配置 SSE

AI Tutor 使用：

Server-Sent Events。

持续输出 Token。

必须关闭 Buffer。

---

## 5.2 SSE 路由

/api/v1/ai/chat/stream

专门 Location。

---

## 5.3 SSE 必须配置

关闭：

proxy_buffering。

chunked_transfer。

缓存。

保持长连接。

---

## 5.4 SSE Timeout

AI Streaming：

600 秒。

避免回答中断。

---

## 5.5 SSE Header

Content-Type：

text/event-stream。

Connection：

keep-alive。

Cache-Control：

no-cache。

---

# 第六章 Upload 与 Storage 代理

## 6.1 Upload API

上传接口：

/api/v1/storage/upload

代理 Backend。

---

## 6.2 静态文件访问

/uploads/

代理 Local Uploads。

---

## 6.3 MinIO Proxy（Demo）

/storage/

代理 MinIO Bucket。

隐藏真实地址。

---

## 6.4 下载 Header

支持：

Content-Disposition。

Range。

大文件下载。

---

# 第七章 WebSocket 配置（预留）

## 7.1 WebSocket 场景

实时协同。

实验监控。

通知中心。

未来支持。

---

## 7.2 Upgrade Header

Upgrade。

Connection Upgrade。

HTTP1.1。

保留配置。

---

# 第八章 HTTPS 配置规范

## 8.1 HTTPS 定位

Demo 可 HTTP。

服务器部署必须 HTTPS。

---

## 8.2 SSL 目录

ssl/

cert.pem

key.pem

Docker Volume。

---

## 8.3 Let's Encrypt（生产）

支持自动续期。

Certbot。

---

## 8.4 HTTP 自动跳转 HTTPS

80。

↓

301。

↓

443。

统一 HTTPS。

---

# 第九章 Gzip 与 Brotli 压缩

## 9.1 Gzip 开启

压缩：

HTML。

CSS。

JS。

JSON。

SVG。

---

## 9.2 Brotli（可选）

生产开启。

Demo 可关闭。

---

## 9.3 压缩级别

Gzip：

Level 6。

兼顾性能。

---

# 第十章 Cache-Control 策略

## 10.1 静态资源缓存

assets。

图片。

字体。

缓存一年。

---

## 10.2 HTML

禁止缓存。

index.html 每次更新。

---

## 10.3 API

API 默认：

No Cache。

JWT 请求实时。

---

## 10.4 Upload 图片缓存

头像。

课程图片。

缓存30天。

---

# 第十一章 Security Header

## 11.1 必须开启 Header

X-Frame-Options。

X-Content-Type-Options。

Referrer-Policy。

Permissions-Policy。

---

## 11.2 CSP（预留）

Content Security Policy。

限制脚本来源。

---

## 11.3 Server Header

隐藏：

Nginx Version。

FastAPI Server。

---

# 第十二章 CORS 策略

## 12.1 CORS 原则

开发：

localhost。

Demo：

指定域名。

---

## 12.2 Allowed Origins

Vue。

Admin。

未来移动端。

---

## 12.3 Allowed Methods

GET。

POST。

PUT。

DELETE。

PATCH。

OPTIONS。

---

## 12.4 Credentials

JWT。

Authorization Header。

允许 Credentials。

---

# 第十三章 Request Size 配置

## 上传限制

PDF。

PPT。

ZIP。

最大：

200MB。

---

## AI Request Body

Markdown。

Prompt。

JSON。

限制：

2MB。

---

# 第十四章 Nginx 日志规范

## Access Log

记录：

IP。

User。

Request。

Duration。

Status。

---

## Error Log

记录：

Gateway Error。

Proxy Error。

SSL Error。

Timeout。

---

## AI Streaming Log

记录：

Conversation。

Latency。

Streaming Duration。

---

# 第十五章 Performance Optimization

## Keep Alive

开启 KeepAlive。

减少 TCP 建立。

---

## Worker Processes

自动 CPU 数量。

---

## Worker Connections

支持：

4096。

高并发。

---

## Sendfile

开启。

静态资源优化。

---

# 第十六章 Nginx Health Check

## Gateway Health API

GET /healthz

返回：

Nginx。

Backend。

Redis。

MySQL。

Ollama。

---

## Docker HealthCheck

Nginx 容器。

定时检查。

失败自动重启。

---

# 第十七章 Gateway Checklist

## Routing

- [ ] Frontend Dist
- [ ] API Proxy
- [ ] Upload Proxy
- [ ] Storage Proxy

## AI

- [ ] SSE Streaming
- [ ] Long Timeout
- [ ] No Buffer

## Security

- [ ] HTTPS
- [ ] Security Header
- [ ] CORS
- [ ] Cache-Control

## Performance

- [ ] Gzip
- [ ] KeepAlive
- [ ] Sendfile
- [ ] Worker Auto

---

# 第十八章 本章开发成果

完成 Part09.2 后，ProgramMind Backend 将具备：

- Nginx Gateway 单入口。
- Vue SPA 部署。
- FastAPI API 代理。
- AI Streaming SSE 支持。
- Upload 与 MinIO 代理。
- HTTPS。
- 安全 Header。
- Gzip/Brotli。
- 静态资源缓存策略。
- Gateway Health Check。
