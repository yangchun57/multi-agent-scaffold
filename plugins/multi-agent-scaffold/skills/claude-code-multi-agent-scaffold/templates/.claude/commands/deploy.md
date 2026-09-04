---
description: 部署/CI 配置（启动 devops SubAgent：CI 流水线、容器化、部署脚本）
---

**编排原则**：部署和 CI 配置是角色工作，必须启动 devops SubAgent 完成，不要内联在主 Agent 做。

请启动 devops SubAgent 处理部署相关需求。脚手架已内置以下部署基础文件，devops 在其上按需扩展：

## 已内置文件

- `.github/workflows/ci.yml` — CI 流水线（push/PR 触发：后端 restore/build/test + 前端 install/build 含类型检查）
- `src/backend/api/Dockerfile.api` — 后端多阶段构建
- `src/backend/web/Dockerfile.web` — 前端 Vite 构建 + Nginx 托管
- `docker-compose.yml` — 本地编排（MySQL + API + Web）

## 典型任务

按用户需求让 devops 处理以下之一：
- 调整 CI（如加缓存、加测试覆盖率、加构建产物上传）
- 补部署目标（如 Docker 镜像发布、服务器部署脚本）
- 环境配置（dev/staging/prod 差异）

完成后主 Agent 提交：`chore: 部署/CI 配置`。
