---
description: 新功能开发（规划→确认→架构→数据库→后端→前端→测试→审查）
---

请按以下流程完成新功能开发，全程遵循 CLAUDE.md。

**编排原则**：每个角色步骤启动对应 SubAgent（通过 Task 工具下发），不要内联在主 Agent 做；确认、汇总等编排动作留在主 Agent。每个交付物落盘后主 Agent 立即提交（遵循 CLAUDE.md 提交约定）。

## 第零步：开发前置检查（主 Agent，六步门禁）
开发动手前逐项完成以下检查，任何一项 ⚠️ 未处理不得进入规划：

1. **读项目上下文**：读 CLAUDE.md（技术栈、红线、文档位置、常用命令）
2. **需求文档确认**：本次开发对应 `docs/00-项目文档/requirements.md` 中哪些用户故事？不存在则先建议运行 /product-discovery
3. **设计文档确认**：本次涉及的表结构 / 接口是否已在 database-design.md、api-contracts.md 中定义？缺失项明确列出并补齐后再继续
4. **字段映射预检**：对照本次功能涉及的后端 DTO（PascalCase）与前端类型（camelCase）——分页参数必须 `pageIndex`/`pageSize`、响应必须 `items`/`total`，发现不一致先纠正
5. **Git 分支检查**：`git branch --show-current`——在 main → 建 `feat/xxx`（变更类建 `change/xxx`）；已在 feat/* 或 change/* 可直接继续；禁止在 main 上直接实施
6. **输出前置检查结果**：按 ✅/⚠️ 逐项汇报（需求文档 / 设计文档 / 字段映射 / 分支），⚠️ 项处理完才算通过

## 第一步：任务规划（启动 pm SubAgent）
启动 pm，让它拆解任务、产出任务计划，写回 docs/00-项目文档/task-plan.md
→ 立即提交：`docs: 任务计划`

## 第二步：计划确认（主 Agent）
主 Agent 把任务计划完整展示给用户，停下等拍板，确认后再继续。

## 第三步：按计划派发 worker（依次启动下游 SubAgent）
按任务依赖顺序启动对应 SubAgent，每个交付物完成后主 Agent 立即提交：
- architect 完成 → `docs: 架构与接口契约`
- db-engineer 完成 → `docs: 数据库设计`
- backend-dev 完成 → `feat: 后端实现`
- frontend-dev 完成 → `feat: 前端实现`
- tester 完成 → `test: 单元测试`
- reviewer 修复完成 → `fix: 审查问题修复`

## 第四步：汇总（主 Agent）
主 Agent 向用户汇报：交付清单、测试结果、审查问题、遗留风险。
