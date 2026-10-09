# 星枢最佳实践指南 / starxhub Getting Started Guide

> 从零到一，用多 Agent 团队把想法变成可交付的代码工程。
> From zero to one — turn an idea into a deliverable codebase with a multi-agent team.

---

## 第一步：初始化项目 / Step 1: Initialize Your Project

### 新项目 / New Project

```bash
/new-project /path/to/project --name "电商系统" --backend dotnet --frontend vue
```

### 已有项目 / Existing Project

```bash
/onboard-project /path/to/existing-project
```

初始化完成后，你会得到一个包含 `.claude/` 目录的完整项目结构。

After initialization, you'll have a complete project structure with a `.claude/` directory.

---

## 第二步：填写 CLAUDE.md / Step 2: Fill in CLAUDE.md

**这是最关键的一步。** CLAUDE.md 是所有 Agent 的"集体记忆"和最高准则。

**This is the most critical step.** CLAUDE.md is the "collective memory" and supreme guideline for all agents.

打开 `CLAUDE.md`，填写以下 TODO 占位符：

Open `CLAUDE.md` and fill in these TODO placeholders:

| 必填项 / Required | 说明 / Description |
|-------------------|-------------------|
| 项目速览 | 这个项目是什么、做什么 / What this project is and does |
| 技术栈 | 后端/前端/数据库的具体版本 / Backend/frontend/database versions |
| 最高优先级约束 | 业务红线（多租户隔离、字段映射、分层边界等）/ Business red lines (tenant isolation, field mapping, layer boundaries, etc.) |
| 常用命令 | 构建/测试/启动命令 / Build/test/start commands |

**示例 / Example**:

```markdown
## 最高优先级约束
1. 所有数据查询必须带 tenant_id 过滤，违反即红线
2. API 响应统一使用 ApiResult<T> 包装
3. 前端业务实体类型由 gen:api 从 Swagger 生成，禁止手写
```

---

## 第三步：验证工程 / Step 3: Verify the Project

```bash
# 后端构建 / Backend build
cd src/backend/api && dotnet build

# 前端安装依赖 / Frontend install dependencies
cd src/backend/web && npm install

# 前端启动 / Frontend start
cd src/backend/web && npm run dev
```

确保一切正常后，进入 Claude Code：

Once everything works, enter Claude Code:

```bash
cd <项目根目录>
claude
```

---

## 第四步：使用命令的最佳时机 / Step 4: When to Use Each Command

星枢提供 10 个命令，覆盖从模糊想法到上线复盘的完整生命周期。以下是推荐的使用顺序和最佳实践。

starxhub provides 10 commands covering the full lifecycle from fuzzy idea to post-release retrospective. Here's the recommended order and best practices.

### 生命周期总览 / Lifecycle Overview

```
/product-discovery  →  /new-feature  →  /review  →  /gen-tests
        ↓                    ↓              ↓            ↓
   需求+设计            开发实施         代码审查      补单元测试
        ↓                    ↓              ↓            ↓
/gen-test-cases  →  /change-request  →  /fix-bug  →  /retro  →  /deploy
        ↓                    ↓              ↓            ↓
   功能测试用例          需求变更         Bug修复      经验沉淀    CI/部署
```

---

### 1. `/product-discovery` — 从模糊想法到需求文档

**When to use / 何时使用**: 项目刚开始，只有一句模糊想法，还没写需求文档。

**Best practice / 最佳实践**:
- 让 Agent 先做需求分析，再用户研究，最后产品设计
- 第二步会强停一次等你确认——这是刻意设计，需求错了后面全错
- 产出：`requirements.md`、`personas.md`、`user-journey.md`、`competitive-analysis.md`、`ia.md`、`flows.md`、`design-spec.md`

```bash
/product-discovery 设计一个多租户会议室预约功能
```

---

### 2. `/new-feature` — 新功能开发全流程

**When to use / 何时使用**: 需求已明确（`requirements.md` 存在），要落地开发某个功能。

**Best practice / 最佳实践**:
- 这是"全流程开发"命令，从规划一路到审查
- 架构方案完成后会过门禁（plan-risk-analyst + plan-gatekeeper），确保方案可行
- 每个交付物完成即提交，不攒到最后

```bash
/new-feature 实现会议室预约功能
```

**流程 / Flow**:
```
开发前置检查 → 任务规划(pm) → [确认] → architect → plan-gate → db-engineer
→ backend-dev → frontend-dev → tester → reviewer
```

---

### 3. `/review` — 代码审查

**When to use / 何时使用**: 代码改动完成后、合并前，想做一次合规审查。

**Best practice / 最佳实践**:
- reviewer 是只读角色，只提问题不改代码
- 发现问题后手动修复，再跑一次 `/review` 确认

```bash
/review
```

---

### 4. `/gen-tests` — 生成单元测试

**When to use / 何时使用**: 某个 Service 逻辑写好了，但缺测试。

**Best practice / 最佳实践**:
- 适合补充式生成；`/new-feature` 流程里已内含 tester 环节
- 指定具体的 Service 名称，效果更好

```bash
/gen-tests 给 RoomService 生成单元测试
```

---

### 5. `/gen-test-cases` — 编写功能测试用例

**When to use / 何时使用**: 要为某个功能产出完整的功能测试用例文档（验收前、或存量项目补测试）。

**Best practice / 最佳实践**:
- 先用这个把"测什么"想清楚，再用 `/gen-tests` 把高价值用例自动化
- 支持两种模式：文档驱动（有需求文档）或代码逆向（只有代码工程）

```bash
/gen-test-cases 会议室预约
```

---

### 6. `/change-request` — 需求变更

**When to use / 何时使用**: 代码已经完成甚至验收了，但需求要改。这是**变更**，不是新功能。

**Best practice / 最佳实践**:
- 和 `/new-feature` 的关键区别：变更多了影响分析、增量规划、强制审查
- 影响分级（高/中/低）决定审查强度

```bash
/change-request 把预约时长从 2 小时改成 4 小时
```

**流程 / Flow**:
```
变更理解 → 影响分析 → 增量规划 → [确认] → 实施 → 审查(强制) → 归档
```

---

### 7. `/fix-bug` — 修复 Bug

**When to use / 何时使用**: 需要修复缺陷、排查线上异常、处理回归 Bug。

**Best practice / 最佳实践**:
- 五步闭环：复现 → 根因定位 → 最小修复 → 回归验证 → 知识沉淀
- 复现不出时会自动汇报假设清单、停下等确认

```bash
/fix-bug 预约时段跨越午夜时前端显示成负数时长
```

---

### 8. `/retro` — 经验沉淀 / 复盘

**When to use / 何时使用**: 一轮 review 找出一堆问题、整改完成后，把踩过的坑沉淀成知识。

**Best practice / 最佳实践**:
- 这是"自升级"机制——把问题反向沉淀到规范和注意事项里
- 三层分类：规范缺口（更新 standards）、项目坑（更新 CLAUDE.md）、一次性问题（跳过）

```bash
/retro
```

---

### 9. `/plan-gate` — 方案门禁（独立使用）

**When to use / 何时使用**: 存量项目补做门禁，或对某个架构方案做独立评审。

**Best practice / 最佳实践**:
- 可独立于 `/new-feature` 使用
- 对方案做 R1~R7 失效点扫描 + C1/C2/C3 三重校验

```bash
/plan-gate
```

---

### 10. `/deploy` — 部署 / CI 配置

**When to use / 何时使用**: 需要配置或调整 CI 流水线、容器化、部署脚本、环境配置。

**Best practice / 最佳实践**:
- 基于脚手架内置的部署文件按需扩展
- 典型任务：加缓存、测试覆盖率、镜像发布、环境差异配置

```bash
/deploy 给 CI 加上测试覆盖率报告
```

---

## 推荐工作流 / Recommended Workflow

### 场景 A：从零开始一个新功能 / Scenario A: Building a New Feature from Scratch

```bash
# 1. 从模糊想法开始
/product-discovery 设计一个 XX 功能

# 2. 需求明确后，全流程开发
/new-feature 实现 XX 功能

# 3. 补充单元测试（如需要）
/gen-tests 给 XXService 生成单元测试

# 4. 产出功能测试用例文档
/gen-test-cases XX 功能

# 5. 上线后复盘
/retro
```

### 场景 B：需求变了 / Scenario B: Requirements Changed

```bash
# 走变更闭环，不要直接改代码
/change-request 把 XX 从 A 改成 B
```

### 场景 C：修 Bug / Scenario C: Fixing a Bug

```bash
# 五步闭环修复
/fix-bug 描述 Bug 现象
```

### 场景 D：已有项目接入 / Scenario D: Onboarding an Existing Project

```bash
# 1. 接入项目
/onboard-project /path/to/existing-project

# 2. 填写 CLAUDE.md
# 3. 补功能测试用例
/gen-test-cases XX 模块

# 4. 开始开发
/new-feature 实现 XX 功能
```

---

## 关键约定 / Key Conventions

### 1. SubAgent 编排 / SubAgent Orchestration

角色工作（分析/设计/开发/审查）必须通过 Task 工具下发给 `.claude/agents/` 里的对应 SubAgent，不在主 Agent 里内联做。

Role work (analysis/design/dev/review) must be delegated to the corresponding SubAgent in `.claude/agents/` via the Task tool, not done inline in the main agent.

### 2. 阶段化提交 / Phased Commits

每个交付物落盘后立即 `git commit`，禁止攒到最后。commit message 遵循 Conventional Commits。

Commit immediately after each deliverable is saved. No batching. Follow Conventional Commits.

### 3. 分支约定 / Branch Convention

- `main` 始终干净可构建 / `main` is always clean and buildable
- 功能在 `feat/xxx` 分支 / Features in `feat/xxx` branches
- 变更在 `change/xxx` 分支 / Changes in `change/xxx` branches
- 完成后合回 `main` / Merge back to `main` when done

### 4. 数据库迁移 / Database Migrations

表结构变更走 `sql/migrations/V00N__xxx.sql` 版本化脚本，禁止手工改库。

Schema changes use versioned scripts `sql/migrations/V00N__xxx.sql`. No manual DB changes.

### 5. 前端类型生成 / Frontend Type Generation

业务实体类型由 `npm run gen:api` 从后端 Swagger 自动生成，禁止手写。

Business entity types are auto-generated from backend Swagger via `npm run gen:api`. No manual typing.

---

## 常见问题 / FAQ

**Q: 我可以直接改代码吗？/ Can I modify code directly?**

A: 可以，但建议通过 `/new-feature` 或 `/change-request` 走完整流程，确保所有 Agent 协作。

A: Yes, but it's recommended to use `/new-feature` or `/change-request` for the full workflow to ensure all agents collaborate.

**Q: 门禁被 REJECT 了怎么办？/ What if the gate REJECTs my plan?**

A: 退回 `architect` 修订方案，然后重跑 `/plan-gate`。

A: Return to `architect` for revision, then re-run `/plan-gate`.

**Q: onboard-project 后原有代码会受影响吗？/ Will existing code be affected after onboard-project?**

A: 不会。onboard-project 只增不删，每步 git commit，方便回滚。

A: No. onboard-project only adds, never deletes. Each step is git committed for easy rollback.

---

## 一句话串起整个生命周期 / One Sentence to Summarize the Lifecycle

```
/product-discovery（模糊想法→需求+设计）
    → /new-feature（开发新功能）
    → /review、/gen-tests（审查、补单元测试）
    → /gen-test-cases（产出功能测试用例文档）
    → /change-request（需求变了，走变更闭环）
    → /fix-bug（修 Bug + 沉淀教训）
    → /retro（整改后沉淀经验，反哺规范和注意事项）
    → /deploy（配置 CI/容器化/部署）
```

10 个命令各管一段，配合 23 个 SubAgent、阶段化提交、版本化数据库迁移和 Swagger 类型生成，构成一个能自我进化的闭环。

10 commands, each covering a phase, working with 23 SubAgents, phased commits, versioned database migrations, and Swagger type generation — forming a self-evolving closed loop.
