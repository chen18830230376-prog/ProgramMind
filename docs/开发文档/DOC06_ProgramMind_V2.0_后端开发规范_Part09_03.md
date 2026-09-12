# ProgramMind V2.0 后端开发规范

# Part09.3 —— CI/CD Pipeline（持续集成与持续部署）

> 文档版本：V2.0
> 更新时间：2026-09
> 模块负责人：Project Lead / DevOps
> 技术栈：GitHub + GitHub Actions + Docker + Alembic + Linux SSH

---

# 第一章 CI/CD Pipeline 模块定位

## 1.1 什么是 CI/CD

CI（Continuous Integration）持续集成。

CD（Continuous Deployment）持续部署。

ProgramMind 采用 GitHub Actions 自动完成：

- 自动测试。
- 自动构建。
- 自动部署。
- 自动生成 Release。

---

## 1.2 Pipeline 在项目中的位置

Developer Push

↓

GitHub

↓

GitHub Actions

↓

Build

↓

Test

↓

Docker Image

↓

Deploy Server

↓

Health Check

---

## 1.3 Pipeline 目标

ProgramMind Pipeline 保证：

- 四人协作统一流程。
- 每次 Push 自动测试。
- 自动生成 Docker 镜像。
- Demo 环境自动更新。
- 可快速回滚。

---

# 第二章 Git 分支管理规范（重点）

## 2.1 四人团队推荐 Git Flow（ProgramMind）

固定五类分支：

| 分支        | 用途            |
| --------- | ------------- |
| main      | 稳定版本（比赛 Demo） |
| develop   | 日常集成开发        |
| feature/* | 功能开发          |
| release/* | 发布准备          |
| hotfix/*  | 紧急修复          |

任何成员禁止直接修改 `main`。

---

## 2.2 分工对应分支

| 成员    | 分支示例                       |
| ----- | -------------------------- |
| AI（你） | feature/ai-engine          |
| 前端    | feature/frontend-dashboard |
| 后端    | feature/backend-auth       |
| RAG   | feature/rag-knowledge      |

功能完成后 PR 到 `develop`。

---

## 2.3 分支生命周期

feature

↓

Pull Request

↓

develop

↓

release/v1.0

↓

main

↓

tag v1.0.0

形成版本闭环。

---

# 第三章 Git Commit Message 规范

## 3.1 Commit 格式

采用 Conventional Commits。

格式：

type(scope): description

---

## 3.2 Type 列表

| Type     | 含义     |
| -------- | ------ |
| feat     | 新功能    |
| fix      | Bug 修复 |
| docs     | 文档     |
| refactor | 重构     |
| style    | 样式     |
| test     | 测试     |
| chore    | 配置修改   |
| perf     | 性能优化   |

---

## 3.3 示例

feat(ai): add tutor workflow

fix(auth): refresh token validation

docs(api): update growth api

统一团队规范。

---

# 第四章 Pull Request（PR）规范

## 4.1 PR 流程

Feature Branch

↓

Push

↓

Pull Request

↓

Code Review

↓

Merge Develop

---

## 4.2 PR 必须填写内容

开发内容。

影响模块。

测试情况。

截图（前端）。

Checklist。

---

## 4.3 Merge 规则

至少：

1 人 Review（团队互查）。

CI 必须通过。

禁止直接 Merge Main。

---

# 第五章 GitHub Actions 总体架构

## 5.1 .github/workflows/

workflows/

backend-ci.yml

frontend-ci.yml

docker-build.yml

deploy-demo.yml

deploy-prod.yml

release.yml

每个流程职责单一。

---

## 5.2 Workflow 分类

| Workflow     | 职责         |
| ------------ | ---------- |
| backend-ci   | Backend 测试 |
| frontend-ci  | Vue 构建     |
| docker-build | Docker 镜像  |
| deploy-demo  | Demo 自动部署  |
| release      | 自动发布       |

---

# 第六章 Backend CI Workflow

## 6.1 Trigger

Push。

Pull Request。

develop/main。

---

## 6.2 Pipeline 步骤

Checkout

↓

Python Install

↓

Install Dependencies

↓

Lint

↓

Pytest

↓

Coverage

↓

Build Success

---

## 6.3 Pytest 内容

测试：

Auth。

Repository。

AI。

RAG。

Growth。

API。

全部自动执行。

---

# 第七章 Frontend CI Workflow

## 7.1 Trigger

Push frontend。

PR frontend。

---

## 7.2 Pipeline

Checkout

↓

Node Install

↓

npm install

↓

ESLint

↓

Type Check

↓

Vite Build

↓

Artifact Upload

---

## 7.3 Build Artifact

保存 dist。

供 Docker Build 使用。

---

# 第八章 Docker Build Workflow

## 8.1 自动构建镜像

Backend。

Frontend。

Worker。

Nginx。

四个镜像。

---

## 8.2 Build 顺序

Backend

↓

Frontend

↓

Worker

↓

Compose Test

---

## 8.3 镜像 Tag

dev-latest

demo-latest

v1.0.0

日期 Tag。

统一命名。

---

# 第九章 Demo 自动部署 Workflow

## 9.1 Deploy Trigger

Merge develop。

自动部署 Demo。

---

## 9.2 SSH 部署流程

GitHub Actions

↓

SSH Linux

↓

git pull

↓

docker compose pull

↓

docker compose up -d

↓

Health Check

---

## 9.3 Health Check

部署完成：

调用：

/system/health。

成功才结束 Workflow。

---

# 第十章 Production Deployment Workflow（预留）

## Release Trigger

Tag。

↓

Build。

↓

Deploy。

↓

Migration。

↓

Health Check。

↓

Notify。

---

## Rollback

保留上一版本镜像。

一键 rollback。

---

# 第十一章 Alembic Migration Workflow

## 11.1 Migration 流程

Model 更新

↓

Alembic Revision

↓

Migration Script

↓

Git Commit

↓

Deploy Execute

---

## 11.2 自动执行 Migration

部署 Backend 前：

alembic upgrade head

保证数据库一致。

---

## 11.3 Migration Checklist

新增表。

新增字段。

索引。

外键。

默认值。

全部版本化。

---

# 第十二章 Secrets 管理规范

## GitHub Secrets

保存：

DATABASE_URL。

SSH_KEY。

JWT_SECRET。

MINIO_KEY。

OSS_KEY（预留）。

---

## 环境隔离

Demo Secrets。

Prod Secrets。

开发环境不用 Secrets。

---

## 禁止提交内容

.env

密钥。

Token。

SSH。

数据库密码。

加入 .gitignore。

---

# 第十三章 Release Version 规范

## 13.1 Version 格式

v1.0.0

Major.Minor.Patch

---

## 13.2 Version 更新规则

| 类型    | 示例     |
| ----- | ------ |
| Major | v2.0.0 |
| Minor | v1.1.0 |
| Patch | v1.0.1 |

---

## 13.3 Release 内容

Git Tag。

Release Note。

更新日志。

下载 Docker Image（预留）。

---

# 第十四章 Rollback Strategy

## 14.1 Rollback 场景

部署失败。

Migration 失败。

AI 服务异常。

快速恢复。

---

## 14.2 Rollback 流程

停止服务。

↓

恢复上一镜像。

↓

恢复 Backup。

↓

Health Check。

---

## 14.3 Rollback Checklist

Docker Image。

数据库 Backup。

FAISS Backup。

MinIO Backup。

Redis Cache 清理。

---

# 第十五章 Code Quality Gate

## Lint

Backend：

Ruff / Black。

Frontend：

ESLint。

TypeScript Check（预留）。

---

## Coverage

Backend：

80%。

Frontend：

70%。

目标覆盖率。

---

## Build Gate

CI 必须：

全部成功。

否则不能 Merge。

---

# 第十六章 Team Collaboration Checklist

## 开发流程

- [ ] Feature Branch
- [ ] Commit 规范
- [ ] Pull Request
- [ ] Review
- [ ] Merge Develop

## CI

- [ ] Backend Test
- [ ] Frontend Build
- [ ] Docker Build
- [ ] Health Check

## CD

- [ ] Demo Deploy
- [ ] Migration
- [ ] Rollback
- [ ] Release Tag

---

# 第十七章 本章开发成果

完成 Part09.3 后，ProgramMind Backend 将具备：

- Git Flow 四人团队协作规范。
- Commit Message 规范。
- Pull Request Review 流程。
- GitHub Actions 自动测试。
- Backend / Frontend 自动构建。
- Docker 自动构建。
- Demo 自动部署。
- Alembic 自动 Migration。
- Release Version 管理。
- Rollback 回滚机制。
