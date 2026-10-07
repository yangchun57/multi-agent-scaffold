# multi-agent-scaffold — Claude Code 插件市场

一个去中心化的 Claude Code **plugin marketplace**，内含插件 **multi-agent-scaffold**：
一套面向 .NET 8 + Vue 3 多租户项目的多 Agent 软件工程团队脚手架。

## 包含什么

安装插件后，你在任意项目里即刻获得：

- **23 个专职 Agent**（五阶段：需求分析 / 任务规划 / 需求评审 / 开发实施 / 测试修复），含 8 个 `req-*` 需求评审团队与 functional-tester / bug-fixer，以及编码前的方案门禁 duo：`plan-risk-analyst`（失效点扫描）+ `plan-gatekeeper`（放行判定）
- **10 个斜杠命令**：`/product-discovery`、`/new-feature`、`/plan-gate`、`/review`、`/gen-tests`、`/gen-test-cases`、`/change-request`、`/fix-bug`、`/retro`、`/deploy`
- **护栏 hooks**：提交前跑构建+测试（`pre_commit_guard`），写实体后做多租户红线与敏感信息扫描（`tenant_guard`）
- **附带生成器 skill** `claude-code-multi-agent-scaffold`：需要从零搭一个新项目骨架时调用它，一键生成带正确命名的 `.claude/` + `CLAUDE.md` + `docs/` + `src/backend` + CI + Docker；**技术栈可配置** `--backend dotnet|python`、`--frontend vue|uniapp`（未指定则交互式询问，绝不静默），并按栈渲染 Agent/CLAUDE.md、加载对应规范、切换 CI/Docker 变体

## 方案放行门禁

`/new-feature` 在 `architect` 产出架构方案之后、进入编码之前，强制经过一道门禁：

```
architect 交卷 → plan-risk-analyst 扫描（R1~R7 失效点）→ plan-gatekeeper 判定（C1 清晰度 / C2 完整性 / C3 可验证性）
              ├─ PASS           → 继续 db-engineer → 编码
              ├─ CONDITIONAL    → 逐条确认放行条件后继续
              └─ REJECT         → 停止流程，退回 architect 修订后重跑 /plan-gate
```

多租户红线阻塞项**一票否决**，不适用 CONDITIONAL。

`/plan-gate` 也可独立使用，便于存量项目补做门禁。

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
    ├── agents/                            # 23 个 subagent
    ├── commands/                          # 10 个斜杠命令
    ├── hooks/                             # hooks.json + 2 个守卫脚本
    └── skills/claude-code-multi-agent-scaffold/  # 一键脚手架生成器 skill
        ├── SKILL.md
        ├── scripts/   (scaffold.py / split-standards.py)
        └── templates/ (CLAUDE.md / .claude / docs / code)
```

> **改动注意**：`agents/` 与 `commands/` 在 `templates/.claude/` 下各有一份副本，逻辑需同步，但**不是简单复制**——模板版要把技术栈相关内容写成占位符（`{{ENVELOPE}}`、`{{FIELD_MAPPING}}` 等，由 `scaffold.py` 按所选技术栈渲染）。直接覆盖会导致 Python / uni-app 栈生成出 .NET 专属内容。详见 `scaffold.py` 的 `BACKENDS[...]["tokens"]` 与 `FRONTS[...]["tokens"]`。

## 说明与注意

- 插件原生 agents/commands 面向「已在开发的项目」；从零生成新项目请用附带 skill。
- 权限黑名单（拒绝 `git push`、删除命令、`drop table`、`truncate table` 等）属于**项目级 settings.json**，插件安装不会写入目标项目，需要时用生成器 skill 落地。
- Agent 定义业务无关，项目红线请写在各项目自己的 `CLAUDE.md`。
- hook 脚本用 `$CLAUDE_PROJECT_DIR` 定位目标工程（默认 `src/backend/api`）。

## 更新日志

### v1.4.0 — 方案放行门禁

- 新增 `plan-risk-analyst`（只读，opus）：对架构方案做 R1~R7 失效点扫描，重点覆盖多租户红线与 AI 易漏的异常边界
- 新增 `plan-gatekeeper`（只读，**sonnet**）：C1 清晰度 / C2 完整性 / C3 可验证性三重校验，输出 PASS / CONDITIONAL / REJECT
- 新增 `/plan-gate` 命令，可独立用于存量项目补门禁
- `/new-feature` 第三步插入强制闸门：architect 交卷后必须过门禁才能进编码
- 模型分级：`plan-gatekeeper` 下放 sonnet（判据固定、机械可核对，用流程约束换模型成本）

设计思路借鉴 Oh-My-OpenAgent 的规划三链（Metis 边界场景扫描 / Momus 三重校验），未引入其任何源码。

## 更新市场清单后

用户执行 `/plugin marketplace update` 刷新。
