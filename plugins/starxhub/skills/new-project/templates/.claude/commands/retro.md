---
description: 经验沉淀/复盘（收集 review 问题→三层分类→更新规范与注意事项，自升级）
---

请按以下流程做经验沉淀，全程遵循 CLAUDE.md。本命令在「大量 review 问题整改完成后」使用，把踩过的坑沉淀成规范和注意事项，避免下次重复。

**编排原则**：收集、分类、沉淀这些角色工作启动 pm SubAgent 完成；汇报留在主 Agent。每个交付物落盘后主 Agent 立即提交（遵循 CLAUDE.md 提交约定）。

## 第一步：收集问题（启动 pm SubAgent）
启动 pm，让它汇总本次迭代的 review 问题（读 task-plan.md、change-log.md、review 报告），去重归类。

## 第二步：三层分类（pm SubAgent）
启动 pm，让它把问题分成三类：规范缺口（更新 .claude/standards/）、项目坑（更新 CLAUDE.md 注意事项）、一次性问题（跳过）。

## 第三步：定向沉淀（启动 pm SubAgent）
启动 pm，让它把规范缺口写回对应规范、项目坑写回 CLAUDE.md、全部记录到 docs/00-项目文档/lessons-learned.md
→ 立即提交：`docs: 经验沉淀`

## 第三步补充：规范瘦身（与沉淀同时进行）
沉淀新规则的同时，对 `.claude/standards/` 做有进有出的整理：
1. **合并重复**：同一规则在多处出现的，合并为一处
2. **删除过时**：已被新规则替代或项目已不用的，删除
3. **拆分超大**：单文件超过 500 行时，按主题拆分并重跑 `python scripts/split-standards.py .claude/standards` 重新生成 topics/
规范只进不出必然膨胀，瘦身是每次 retro 的固定动作。

## 第四步（可选）：回填 skill（主 Agent，需用户确认）
把「通用性」规范缺口同步回 skill 模板，让下个新项目直接受益：
- 询问用户哪些沉淀具有跨项目通用性
- 用户确认后，同步到 skill 模板对应文件（如 `~/.qwenworkcn/skills/claude-code-multi-agent-scaffold/templates/.claude/standards/` 或 `templates/.claude/agents/`）
- 项目特有的坑**不回填**（会污染通用模板）

## 第五步：汇报（主 Agent）
主 Agent 向用户汇报：沉淀了多少条规范/注意事项、更新了哪些文件、哪些判定为一次性（及理由）。
