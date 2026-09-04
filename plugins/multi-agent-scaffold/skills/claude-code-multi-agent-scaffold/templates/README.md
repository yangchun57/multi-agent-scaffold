# {{PROJECT_NAME}}

{{PROJECT_DESC}}

## 多 Agent 团队

本项目使用 Claude Code 多 Agent 团队（11 个专职 Agent，四阶段生命周期），通过 `.claude/agents/` 定义。

## 快速开始

1. 填写 `CLAUDE.md` 中的 TODO（项目速览、红线、技术栈、常用命令）
2. 用 Claude Code 打开本目录：`claude`
3. 输入 `/product-discovery 描述你的需求`
4. 需求明确后 `/new-feature 实现功能`

## 目录结构

```
├── CLAUDE.md           ← 项目集体记忆
├── .claude/            ← 11 Agent + 命令 + hooks + standards
├── docs/00-项目文档/   ← 需求、设计、架构、契约文档
└── src/                ← 代码
```
