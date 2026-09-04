# multi-agent-scaffold — Claude Code 插件市场

一个去中心化的 Claude Code **plugin marketplace**，内含插件 **multi-agent-scaffold**：
一套面向 .NET 8 + Vue 3 多租户项目的多 Agent 软件工程团队脚手架。

## 包含什么

安装插件后，你在任意项目里即刻获得：

- **21 个专职 Agent**（五阶段：需求分析 / 任务规划 / 需求评审 / 开发实施 / 测试修复），含 8 个 `req-*` 需求评审团队与 functional-tester / bug-fixer
- **9 个斜杠命令**：`/product-discovery`、`/new-feature`、`/review`、`/gen-tests`、`/gen-test-cases`、`/change-request`、`/fix-bug`、`/retro`、`/deploy`
- **护栏 hooks**：提交前跑构建+测试（`pre_commit_guard`），写实体后做多租户红线与敏感信息扫描（`tenant_guard`）
- **附带生成器 skill** `claude-code-multi-agent-scaffold`：需要从零搭一个新项目骨架时调用它，一键生成带正确命名的 `.claude/` + `CLAUDE.md` + `docs/` + `src/backend`（dotnet new + create-vite）+ CI + Docker

## 安装

```bash
# 添加本市场（owner/repo 换成实际地址）
claude plugin marketplace add yangchun57/multi-agent-scaffold

# 安装插件
claude plugin install multi-agent-scaffold@multi-agent-scaffold
```

在 Claude Code 会话内等价命令：`/plugin marketplace add yangchun57/multi-agent-scaffold`、`/plugin install multi-agent-scaffold@multi-agent-scaffold`。

## 目录结构

```
multi-agent-scaffold/                     # 仓库根 = 一个 marketplace
├── .claude-plugin/marketplace.json       # 市场清单
└── plugins/multi-agent-scaffold/         # 插件本体
    ├── .claude-plugin/plugin.json         # 插件清单
    ├── agents/                            # 21 个 subagent
    ├── commands/                          # 9 个斜杠命令
    ├── hooks/                             # hooks.json + 2 个守卫脚本
    └── skills/claude-code-multi-agent-scaffold/  # 一键脚手架生成器 skill
        ├── SKILL.md
        ├── scripts/   (scaffold.py / split-standards.py)
        └── templates/ (CLAUDE.md / .claude / docs / code)
```

## 说明与注意

- 插件原生 agents/commands 面向「已在开发的项目」；从零生成新项目请用附带 skill。
- 权限黑名单（拒绝 `git push`、删除命令、`drop table`、`truncate table` 等）属于**项目级 settings.json**，插件安装不会写入目标项目，需要时用生成器 skill 落地。
- Agent 定义业务无关，项目红线请写在各项目自己的 `CLAUDE.md`。
- hook 脚本用 `$CLAUDE_PROJECT_DIR` 定位目标工程（默认 `src/backend/api`）。

## 更新市场清单后

用户执行 `/plugin marketplace update` 刷新。
