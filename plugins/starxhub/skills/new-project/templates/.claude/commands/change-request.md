---
description: 需求变更（变更理解→影响分析→增量规划→确认→实施→回归→审查→归档）
---

请按以下流程处理需求变更，全程遵循 CLAUDE.md。本命令用于「已有功能/需求需要修改」的场景，区别于 /new-feature（全新功能开发）。

**编排原则**：每个角色步骤都要启动对应的 SubAgent（通过 Task 工具下发给 `.claude/agents/` 里的角色），不要把角色工作内联在主 Agent 里做；只有澄清、确认、汇报这些编排动作留在主 Agent。每个交付物落盘后主 Agent 立即提交（遵循 CLAUDE.md 提交约定）。

## 第一步：变更理解（启动 requirement-analyst SubAgent）
启动 requirement-analyst，让它澄清变更内容、分类（新增/修改/删除/延期），更新 docs/00-项目文档/requirements.md（标记状态 + 版本号 +0.1 + 变更记录）
→ 立即提交：`docs: 需求变更分析`

变更内容不明确时，主 Agent 停下向用户确认后再继续。

## 第二步：影响分析（启动 architect SubAgent；需求层并行启动 requirement-analyst）
产出三层影响分析报告：需求层（requirement-analyst）、设计层+代码层（architect，对照 architecture/api-contracts/database-design 用 Grep 定位受影响代码）
→ 立即提交：`docs: 变更影响分析`

**影响分级**（决定后续审查强度）：
- 高：涉及红线、数据库结构、接口契约
- 中：涉及业务逻辑、页面
- 低：仅文案、配置

## 第三步：增量规划（启动 pm SubAgent）
启动 pm，基于影响分析只规划受影响任务，产出变更任务计划
→ 立即提交：`docs: 增量任务计划`

主 Agent 把计划完整展示给用户，**停下等确认**，未确认禁止实施。

## 第四步：按计划实施（依次/并行启动下游 SubAgent）
按任务依赖顺序启动对应 SubAgent，每个交付物完成后主 Agent 立即提交：
- architect / db-engineer / backend-dev / frontend-dev 完成 → `feat: 变更实施`
- **涉及表结构变更时**：db-engineer 必须产出版本化迁移脚本（sql/migrations/V00N__xxx.sql，禁止手工改库），单独提交 `docs: 迁移脚本 V00N`
- tester 完成 → `test: 回归测试`

## 第五步：审查（启动 reviewer SubAgent，强制关卡，不可跳过）
启动 reviewer，审查变更代码，重点看是否引入回归、是否遵守 CLAUDE.md 最高优先级约束。

按第二步的影响分级决定审查强度：
- 高影响（红线/库表/契约）：全面审查
- 中影响（业务逻辑/页面）：正常审查
- 低影响（仅文案/配置）：快速审查（只查改动点）

审查发现的问题修复后 → 立即提交：`fix: 变更审查修复`

## 第六步：归档（启动 pm SubAgent）
启动 pm，更新 backlog.md / task-plan.md，变更记录写入 change-log.md
→ 立即提交：`docs: 变更记录归档`

主 Agent 向用户汇报：变更内容、影响范围、测试结果、审查结果、遗留风险。