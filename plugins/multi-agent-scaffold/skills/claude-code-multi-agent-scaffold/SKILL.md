---
name: claude-code-multi-agent-scaffold
description: Scaffolds a complete Claude Code multi-agent team project. Creates the .claude/ directory (21 role agents across 5 lifecycle phases, 9 slash commands, 2 guardrail hooks, dev standards), CLAUDE.md, docs/00-项目文档, and a self-contained generator script with a configurable tech stack (backend dotnet|python, frontend vue|uniapp). Use when the user wants to set up a Claude Code multi-agent project, an AI engineering team, or an automated software-engineering workflow.
---

# Claude Code Multi-Agent Team Scaffold

## Purpose

Generate a complete Claude Code multi-agent team covering the full software-engineering lifecycle: 需求分析 → 产品设计 → 任务规划 → 开发实施。

## Core principle: role template vs business context separation

- `.claude/` holds ONLY abstract, cross-project reusable content: agents (how to work), commands (workflows), hooks (guardrails), standards (how to write code)
- `docs/00-项目文档/` holds business-specific content: requirements, architecture, task plans
- `CLAUDE.md` is the connection point (接线点): project overview + red lines + doc index
- Agent definitions MUST NOT contain business nouns or rules — those live in CLAUDE.md. Agents reference "遵守 CLAUDE.md 的最高优先级约束" instead of duplicating rules.

## Directory structure to create

```
<root>/
├── CLAUDE.md                  # project memory (TODO placeholders for business)
├── .claude/
│   ├── settings.json          # permissions + hooks
│   ├── agents/                # 21 role agents
│   ├── commands/              # 9 slash commands
│   ├── hooks/                 # 2 guardrail scripts
│   └── standards/             # dev standards (abstract, reusable)
├── .mcp.json
├── .gitignore
├── init-agent-team.py         # self-contained generator
├── docs/00-项目文档/          # 12 business doc templates
├── docs/README.md             # 文档管理规范（命名/编号原则）
└── src/
    └── backend/
        ├── api/               # .NET 8 分层 API 骨架（业务无关）
        └── web/               # Vue 3 前端骨架（业务无关）
```

## Agent roster (21 agents, 5 phases)

| Phase | Agent | Role | Model |
|-------|-------|------|-------|
| 需求分析 | requirement-analyst | 需求澄清、用户故事、验收标准 | opus |
| 需求分析 | ux-researcher | 用户画像、用户旅程、竞品分析 | opus |
| 需求分析 | product-designer | 信息架构、交互流程、设计规范 | opus |
| 任务规划 | pm | 需求拆解、任务计划、优先级 | opus |
| 需求评审 | req-coordinator | 需求评审协调者，调度评审团队、汇总报告 | opus |
| 需求评审 | req-quality-group-lead | 需求质量评审组长，调度质量专家和一致性专家 | opus |
| 需求评审 | req-impl-group-lead | 实现合规评审组长，调度变更影响、合规、测试覆盖专家 | opus |
| 需求评审 | req-quality-reviewer | 需求质量评审专家，检查完整性、无歧义性、可测试性 | opus |
| 需求评审 | req-consistency-reviewer | 上下游一致性评审专家，检查需求→API→DB→代码一致性 | opus |
| 需求评审 | req-change-impact-reviewer | 变更影响评审专家，分析影响范围、连锁反应、回滚方案 | opus |
| 需求评审 | req-compliance-reviewer | 红线合规评审专家，检查分层边界、响应格式、字段映射、SDK锁定 | opus |
| 需求评审 | req-test-coverage-reviewer | 测试覆盖度评审专家，检查测试用例对验收标准的覆盖 | opus |
| 开发实施 | architect | 架构设计、接口契约 | opus |
| 开发实施 | db-engineer | 表结构、SQL | sonnet |
| 开发实施 | backend-dev | 后端代码 | sonnet |
| 开发实施 | frontend-dev | 前端代码 | sonnet |
| 开发实施 | tester | 单元测试 | sonnet |
| 开发实施 | reviewer | 代码审查（只读） | opus |
| 开发实施 | devops | CI/CD、部署（/deploy 命令入口） | sonnet |
| 测试修复 | functional-tester | 功能测试用例设计（文档驱动 / 代码逆向） | opus |
| 测试修复 | bug-fixer | Bug 复现、根因定位、最小修复、回归验证、知识沉淀 | opus |

Flow: 模糊需求 → requirement-analyst → ux-researcher → product-designer → pm → req-coordinator（评审团队把关）→ 开发 agents → reviewer → functional-tester（用例）/ bug-fixer（修复）

### 需求评审团队拓扑

```
req-coordinator                     （协调者）
├── req-quality-group-lead          （需求质量组长）
│   ├── req-quality-reviewer        （需求质量专家）
│   └── req-consistency-reviewer    （上下游一致性专家）
└── req-impl-group-lead             （实现合规组长）
    ├── req-change-impact-reviewer  （变更影响专家）
    ├── req-compliance-reviewer     （红线合规专家）
    └── req-test-coverage-reviewer  （测试覆盖度专家）
```

## Scaffolding workflow

1. Ask the user for: project name, one-line description, target directory, and tech stack — backend `dotnet` (default) or `python`, frontend `vue` (default) or `uniapp`. If a stack is not specified, the generator prompts interactively; never silently pick.
2. Run the generator: `python scripts/scaffold.py <target-dir> --name "名称" --desc "描述" --code-name "CodeName" [--backend dotnet|python] [--frontend vue|uniapp] [--standards <规范源目录>]`
3. The script generates: .claude/（agents/commands/hooks/settings）、CLAUDE.md、docs/ 整目录（00-项目文档 md 工作文件模板 + README 三轨格式规范 + common.css + md2html.py 转换器 + _模板与规范 裸HTML模板与图标速查），src/backend 代码工程（dotnet new .NET 8 分层 API 含集成测试基类 + npm create vite Vue 3 web 含 prettier），外加 sql/migrations 迁移目录、gen:api 类型生成、.editorconfig、CI workflow + Dockerfile x2 + docker-compose + dependabot。CLAUDE.md 内置分支约定（trunk-based：main 干净可构建 + feat/change 分支）。docs 三轨格式约定：README/Agent 工作文件=md，01/02 交付物=HTML（裸HTML 引 common.css，用 md2html.py 转换）。包含 8 个需求评审 Agent（req-*），形成完整的需求评审团队；另含 functional-tester / bug-fixer 两个测试修复 Agent（对应 /gen-test-cases、/fix-bug 命令）。
4. `--standards` 指向自定义规范源目录时，脚本覆盖 `.claude/standards/`；未提供时使用内置的 7 份默认规范（含按主题拆分的 `topics/` 索引——Agent 优先读 topics/INDEX.md 定位主题，禁止无目的整读大规范）。规范更新后可重跑 `python scripts/split-standards.py <standards目录>` 重新生成 topics。
5. 脚本自动 `git init` 并创建初始提交（`chore: 初始化项目脚手架`）；git 未安装或未配置 user.name/email 时只 git init、跳过提交。
6. Remind the user: fill CLAUDE.md TODO placeholders, add `git remote add origin <url>`, then run `claude` at the project ROOT (not a subdirectory).

## Agent definition pattern

Each `.claude/agents/{name}.md`:

```markdown
---
name: {name}
description: {role}. Use when {trigger keywords}.
tools: {minimal tool set}
model: {opus|sonnet}
---

你是{role}。

## 职责
1. ...

## 必须遵守（最高优先级）
1. 严格遵守 CLAUDE.md 的最高优先级约束

## 工作方式
1. 先读 CLAUDE.md 和相关文档

## 禁止事项
- 只写 docs/00-项目文档/ 下的文档
```

Rules:
- `tools` minimal: reviewer is read-only (Read, Glob, Grep); others add Write/Edit/Bash as needed; researchers add WebSearch.
- `model`: opus for architect/requirement-analyst/ux-researcher/product-designer/pm/reviewer, sonnet for the rest.
- No business nouns in agent definitions — use {Entity}/{模块} placeholders in examples.

## Post-scaffold checklist

- [ ] CLAUDE.md TODO filled (project overview, red lines, tech stack, commands)
- [ ] Dev standards bundled by default in .claude/standards/ (override with --standards if needed)
- [ ] `claude` runs at project root
- [ ] `/product-discovery` starts the workflow
- [ ] 需求评审团队 Agent 已包含（req-* 共 8 个）
- [ ] 功能测试与 Bug 修复命令可用（`/gen-test-cases`、`/fix-bug`）

## Skill layout

```
claude-code-multi-agent-scaffold/
├── SKILL.md
├── .skill-metadata.yaml
├── templates/              ← 模板文件（可直接编辑，无需改脚本）
│   ├── CLAUDE.md           ← 含 {{PROJECT_NAME}} {{PROJECT_DESC}} 占位符
│   ├── README.md           ← 含占位符
│   ├── .mcp.json
│   ├── .gitignore
│   ├── .claude/            ← agents/commands/hooks/settings + standards（7 份规范）
│   │   └── agents/         ← 21 个 Agent 模板（含 8 个需求评审 + 2 个测试修复 Agent）
│   ├── docs/00-项目文档/   ← 12 个文档模板
│   ├── docs/README.md      ← 文档管理规范
│   └── code/               ← 自定义基础设施（CLI 生成骨架后写入）
│       ├── api/            ← ApiResult/PageResult/GlobalExceptionFilter 等（{{CodeName}} 占位）
│       └── web/            ← request.ts/router/layouts/types 等（{{PROJECT_NAME}} 占位）
└── scripts/
    └── scaffold.py         ← 复制模板 + CLI 生成代码工程 + 替换占位符
```

## References

- Template files: templates/（直接编辑 .md/.json/.py，脚本无需改动）
- Generator script: scripts/scaffold.py
