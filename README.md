# multi-agent-scaffold — Claude Code 插件市场

一个去中心化的 Claude Code **plugin marketplace**，内含插件 **multi-agent-scaffold**：
一套多 Agent 软件工程团队**项目脚手架生成器**，为不同技术栈的项目生成定制化的 `.claude` 配置。

## 定位

**仅用于新建项目**，不支持已有项目。

每个项目的技术栈、业务规则、多租户约束都不同，不存在"通用模板"能直接套用。本插件的价值在于：根据你选择的技术栈，生成一个**完全适配该项目**的起点，而不是安装一个"看起来能用但处处不匹配"的配置。

## 包含什么

安装插件后，你获得一个 **skill**：`claude-code-multi-agent-scaffold`。

运行脚手架生成器，一键生成完整项目结构：

```bash
python scaffold.py /path/to/project --backend python --frontend vue
```

生成的项目包含：

- **23 个专职 Agent**（五阶段：需求分析 / 任务规划 / 需求评审 / 开发实施 / 测试修复），含 8 个 `req-*` 需求评审团队与 functional-tester / bug-fixer，以及编码前的方案门禁 duo：`plan-risk-analyst`（失效点扫描）+ `plan-gatekeeper`（放行判定）
- **10 个斜杠命令**：`/product-discovery`、`/new-feature`、`/plan-gate`、`/review`、`/gen-tests`、`/gen-test-cases`、`/change-request`、`/fix-bug`、`/retro`、`/deploy`
- **护栏 hooks**：提交前跑构建+测试（`pre_commit_guard`），写实体后做多租户红线与敏感信息扫描（`tenant_guard`）
- **路径范围 rules**（v2.0 新增）：按技术栈自动加载的规范规则，编辑匹配文件时自动注入上下文，无需手动读取

## 技术栈支持

| 维度 | 选项 | 说明 |
|------|------|------|
| 后端 | `dotnet` | .NET 8 + ASP.NET Core Web API + SqlSugar + MySQL |
| 后端 | `python` | Python 3.10+ + FastAPI + SQLAlchemy 2.0 + Pydantic v2 |
| 前端 | `vue` | Vue 3 + Element Plus + Pinia + Vite + TypeScript |
| 前端 | `uniapp` | uni-app + Vue 3 + Pinia + TypeScript（H5 + 微信小程序） |

未指定技术栈时，脚手架会**交互式询问**，绝不静默默认。

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

## 路径范围 rules（v2.0 新增）

生成的项目包含 `.claude/rules/` 目录，按技术栈自动加载规范规则：

```
.claude/rules/
├── workflow.md              # 始终加载：工作流规范
├── database.md              # 始终加载：数据库与多租户隔离规范
├── git.md                   # 始终加载：Git 提交规范
├── backend-api.md           # 编辑后端 API 文件时自动加载
├── backend-domain.md        # 编辑后端领域层文件时自动加载
├── backend-infra.md         # 编辑后端基础设施文件时自动加载
├── frontend-pages.md        # 编辑前端页面文件时自动加载
└── frontend-state.md        # 编辑前端状态/API 层文件时自动加载
```

每个 rule 文件 < 50 行精华规则，通过 `paths` glob 匹配自动触发，编辑匹配文件时 Claude Code 自动注入上下文。完整规范仍保留在 `.claude/standards/` 供深层阅读。

## 安装

```bash
# 添加本市场（owner/repo 换成实际地址）
claude plugin marketplace add yangchun57/multi-agent-scaffold

# 安装插件
claude plugin install multi-agent-scaffold@multi-agent-scaffold
```

在 Claude Code 会话内等价命令：`/plugin marketplace add yangchun57/multi-agent-scaffold`、`/plugin install multi-agent-scaffold@multi-agent-scaffold`。

## 使用

安装后，在 Claude Code 中调用 skill：

```
/claude-code-multi-agent-scaffold /path/to/project --name "项目名称" --backend python --frontend vue
```

或直接运行脚本：

```bash
cd /path/to/plugin/skills/claude-code-multi-agent-scaffold/scripts
python scaffold.py /path/to/project --name "项目名称" --backend python --frontend vue
```

## 目录结构

```
multi-agent-scaffold/                     # 仓库根 = 一个 marketplace
├── .claude-plugin/marketplace.json       # 市场清单
└── plugins/multi-agent-scaffold/         # 插件本体
    ├── .claude-plugin/plugin.json         # 插件清单
    └── skills/
        └── claude-code-multi-agent-scaffold/  # 脚手架生成器 skill
            ├── SKILL.md
            ├── scripts/
            │   ├── scaffold.py            # 主生成器（按技术栈渲染）
            │   └── split-standards.py     # 规范拆分工具
            └── templates/
                ├── CLAUDE.md              # 项目记忆模板（含占位符）
                ├── .claude/
                │   ├── agents/            # 23 个 Agent 定义（含占位符）
                │   ├── commands/          # 10 个斜杠命令（含占位符）
                │   ├── hooks/             # 护栏钩子脚本
                │   ├── rules/             # 路径范围规则（按技术栈选择）
                │   │   ├── _always/       # 通用规则
                │   │   ├── _backend/      # 后端规则（dotnet/python 变体）
                │   │   └── _frontend/     # 前端规则（vue/uniapp 变体）
                │   ├── standards/         # 完整规范文档（按技术栈选择）
                │   └── settings.json      # 权限配置
                ├── code/                  # 代码工程模板（按技术栈选择）
                └── docs/                  # 项目文档模板
```

## 说明与注意

- **仅用于新建项目**：插件不包含可直接在已有项目中使用的 agents/commands，因为每个项目的技术栈和业务规则都不同
- **占位符渲染**：模板中的 `{{BACKEND_STACK}}`、`{{ENVELOPE}}`、`{{FIELD_MAPPING}}` 等占位符由 `scaffold.py` 按所选技术栈渲染，详见 `scaffold.py` 的 `BACKENDS[...]["tokens"]` 与 `FRONTS[...]["tokens"]`
- **权限黑名单**：拒绝 `git push`、删除命令、`drop table`、`truncate table` 等，属于项目级 `settings.json`，由生成器写入目标项目
- **Agent 定义业务无关**：项目红线请写在各项目自己的 `CLAUDE.md` 中
- **hook 脚本**：用 `$CLAUDE_PROJECT_DIR` 定位目标工程（默认 `src/backend/api`）

## 更新日志

### v2.0.0 — 精简架构 + 路径范围 rules

- **移除原生 agents/commands/hooks**：插件不再提供可直接在已有项目中使用的配置，仅保留脚手架生成器 skill
- **新增 `.claude/rules/` 路径范围规则**：按技术栈生成 13 个 rules 文件，编辑匹配文件时自动注入上下文
  - 通用规则（workflow/database/git）始终加载
  - 后端规则（backend-api/domain/infra）按 `--backend dotnet|python` 选择
  - 前端规则（frontend-pages/state）按 `--frontend vue|uniapp` 选择
- **更新 CLAUDE.md 模板**：引用新的 rules 自动加载机制，瘦身规范引用部分
- **scaffold.py 集成**：新增 `copy_rules()` 函数，按技术栈复制并渲染 rules 文件

### v1.4.0 — 方案放行门禁

- 新增 `plan-risk-analyst`（只读，opus）：对架构方案做 R1~R7 失效点扫描，重点覆盖多租户红线与 AI 易漏的异常边界
- 新增 `plan-gatekeeper`（只读，**sonnet**）：C1 清晰度 / C2 完整性 / C3 可验证性三重校验，输出 PASS / CONDITIONAL / REJECT
- 新增 `/plan-gate` 命令，可独立用于存量项目补门禁
- `/new-feature` 第三步插入强制闸门：architect 交卷后必须过门禁才能进编码
- 模型分级：`plan-gatekeeper` 下放 sonnet（判据固定、机械可核对，用流程约束换模型成本）

设计思路借鉴 Oh-My-OpenAgent 的规划三链（Metis 边界场景扫描 / Momus 三重校验），未引入其任何源码。

## 更新市场清单后

用户执行 `/plugin marketplace update` 刷新。
