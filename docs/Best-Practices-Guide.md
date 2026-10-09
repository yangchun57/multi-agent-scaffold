# 星枢使用指南 / starxhub Usage Guide

> 从零到一，用 23 个 Agent 和 11 个命令构建完整代码工程的最佳实践。
> From zero to one — best practices for building a complete codebase with 23 agents and 11 commands.

---

## 目录 / Table of Contents

1. [初始化后你得到了什么 / What You Get After Initialization](#1-初始化后你得到了什么)
2. [第一步：填写 CLAUDE.md / Step 1: Fill in CLAUDE.md](#2-第一步填写-claudemd)
3. [理解你的团队：23 个 Agent 全览 / Know Your Team: 23 Agents Overview](#3-理解你的团队23-个-agent-全览)
4. [理解你的工具箱：10 个命令详解 / Know Your Tools: 10 Commands Explained](#4-理解你的工具箱10-个命令详解)
5. [从零到一：完整开发流程 / Zero to One: Complete Development Workflow](#5-从零到一完整开发流程)
6. [关键约定与最佳实践 / Key Conventions & Best Practices](#6-关键约定与最佳实践)
7. [常见问题 / FAQ](#7-常见问题-faq)

---

## 1. 初始化后你得到了什么

### 新项目 (`/new-project`)

```
<项目根>/
├── CLAUDE.md                     # 项目集体记忆（需填写 TODO）
├── .claude/
│   ├── settings.json             # 权限配置 + hooks
│   ├── agents/                   # 23 个 Agent 定义
│   ├── commands/                 # 10 个斜杠命令
│   ├── hooks/                    # 2 个护栏脚本
│   ├── rules/                    # 路径范围规则（自动加载）
│   └── standards/                # 完整开发规范
├── src/backend/api/              # 后端工程
├── src/backend/web/              # 前端工程
├── docs/00-项目文档/              # 文档模板
├── scripts/ci.sh                 # 本地质量门禁
└── .github/workflows/ci.yml      # CI 流水线
```

### 已有项目 (`/onboard-project`)

```
<项目根>/
├── CLAUDE.md                     # 从代码推断预填（非 TODO）
├── .claude/                      # 同上（按匹配度生成 rules）
├── docs/01-技术规范/              # 迁移后的技术文档
├── docs/02-用户文档/              # 迁移后的用户文档
└── ...（原有代码不动）
```

---

## 2. 第一步：填写 CLAUDE.md

**这是最关键的一步。** 所有 Agent 都会先读 CLAUDE.md，它是整个团队的"集体记忆"和最高准则。

**This is the most critical step.** All agents read CLAUDE.md first — it's the team's collective memory and supreme guideline.

### 必填项 / Required Fields

| 字段 / Field | 说明 / Description | 示例 / Example |
|--------------|-------------------|---------------|
| 项目速览 | 这个项目是什么、做什么 / What this project is | "多租户会议室预约系统" |
| 技术栈 | 具体版本 / Specific versions | ".NET 8 + Vue 3 + MySQL 8" |
| **最高优先级约束** | 业务红线 / Business red lines | "所有查询必须带 tenant_id" |
| 常用命令 | 构建/测试/启动 / Build/test/start | `dotnet build`, `npm run dev` |

### 示例 / Example

```markdown
## 最高优先级约束（所有 Agent 必须遵守）

1. 多租户隔离：所有数据查询必须带 tenant_id 过滤，违反即红线
2. 响应格式：API 统一使用 ApiResult<T> 包装，禁止裸返回
3. 字段映射：前端列表字段必须是 pageIndex/items，禁止 page/pageSize
4. 类型生成：前端业务实体由 gen:api 从 Swagger 生成，禁止手写
5. 数据库：表结构变更走版本化迁移脚本，禁止手工改库
```

---

## 3. 理解你的团队：23 个 Agent 全览

你的项目现在有一支完整的开发团队。按 5 个阶段组织：

Your project now has a complete development team, organized in 5 phases:

### 阶段一：需求分析 / Phase 1: Requirements Analysis

| Agent | 角色 / Role | 何时调用 / When to Use |
|-------|------------|----------------------|
| `requirement-analyst` | 需求分析师 / Requirements Analyst | 模糊需求澄清、用户故事、验收标准 |
| `ux-researcher` | 用户研究员 / UX Researcher | 用户画像、用户旅程、竞品分析 |
| `product-designer` | 产品设计师 / Product Designer | 信息架构、交互流程、设计规范 |

### 阶段二：任务规划 / Phase 2: Task Planning

| Agent | 角色 / Role | 何时调用 / When to Use |
|-------|------------|----------------------|
| `pm` | 项目经理 / Project Manager | 需求拆解、任务计划、优先级排序 |

### 阶段三：需求评审 / Phase 3: Requirements Review

| Agent | 角色 / Role | 何时调用 / When to Use |
|-------|------------|----------------------|
| `req-coordinator` | 评审协调者 / Review Coordinator | 调度评审团队、汇总报告 |
| `req-quality-group-lead` | 质量组长 / Quality Group Lead | 调度质量专家和一致性专家 |
| `req-impl-group-lead` | 实现合规组长 / Implementation Group Lead | 调度变更影响、合规、测试覆盖专家 |
| `req-quality-reviewer` | 质量专家 / Quality Reviewer | 检查完整性、无歧义性、可测试性 |
| `req-consistency-reviewer` | 一致性专家 / Consistency Reviewer | 检查需求→API→DB→代码一致性 |
| `req-change-impact-reviewer` | 变更影响专家 / Change Impact Reviewer | 分析影响范围、连锁反应、回滚方案 |
| `req-compliance-reviewer` | 合规专家 / Compliance Reviewer | 检查分层边界、响应格式、字段映射 |
| `req-test-coverage-reviewer` | 测试覆盖专家 / Test Coverage Reviewer | 检查测试用例对验收标准的覆盖 |

### 阶段四：开发实施 / Phase 4: Development

| Agent | 角色 / Role | 何时调用 / When to Use |
|-------|------------|----------------------|
| `plan-risk-analyst` | 方案风险分析师 / Plan Risk Analyst | 架构方案失效点扫描（R1~R7），只读 |
| `plan-gatekeeper` | 方案门禁官 / Plan Gatekeeper | 方案放行判定（C1/C2/C3），只读 |
| `architect` | 架构师 / Architect | 架构设计、接口契约 |
| `db-engineer` | 数据库工程师 / DB Engineer | 表结构、SQL 迁移脚本 |
| `backend-dev` | 后端开发 / Backend Developer | 后端业务代码 |
| `frontend-dev` | 前端开发 / Frontend Developer | 前端页面和组件 |
| `tester` | 测试工程师 / Tester | 单元测试编写 |
| `reviewer` | 代码审查员 / Code Reviewer | 代码审查（只读） |
| `devops` | 运维工程师 / DevOps Engineer | CI/CD、部署配置 |

### 阶段五：测试修复 / Phase 5: Testing & Fixing

| Agent | 角色 / Role | 何时调用 / When to Use |
|-------|------------|----------------------|
| `functional-tester` | 功能测试员 / Functional Tester | 功能测试用例设计（文档驱动/代码逆向） |
| `bug-fixer` | Bug 修复师 / Bug Fixer | Bug 复现、根因定位、最小修复、回归验证 |

### 团队拓扑 / Team Topology

```
需求分析链 / Requirements Chain:
  requirement-analyst → ux-researcher → product-designer → pm

评审团队 / Review Team:
  req-coordinator
  ├── req-quality-group-lead
  │   ├── req-quality-reviewer
  │   └── req-consistency-reviewer
  └── req-impl-group-lead
      ├── req-change-impact-reviewer
      ├── req-compliance-reviewer
      └── req-test-coverage-reviewer

开发链 / Development Chain:
  architect → [plan-gate] → db-engineer → backend-dev → frontend-dev → tester → reviewer

修复链 / Fix Chain:
  functional-tester（用例设计）
  bug-fixer（五步闭环修复）
```

---

## 4. 理解你的工具箱：11 个命令详解

### 命令总览 / Commands Overview

| # | 命令 / Command | 用途 / Purpose | 触发时机 / When to Trigger |
|---|----------------|---------------|--------------------------|
| 1 | `/product-discovery` | 产品发现与需求设计 | 项目刚开始，只有模糊想法 |
| 2 | `/new-feature` | 新功能全流程开发 | 需求已明确，要落地开发 |
| 3 | `/review` | 代码审查 | 代码完成后、合并前 |
| 4 | `/gen-tests` | 生成单元测试 | Service 写好了但缺测试 |
| 5 | `/gen-test-cases` | 编写功能测试用例 | 验收前要完整测试用例 |
| 6 | `/change-request` | 需求变更闭环 | 代码已完成但需求要改 |
| 7 | `/fix-bug` | Bug 修复 + 知识沉淀 | 发现 Bug 需要修复 |
| 8 | `/retro` | 经验沉淀 / 复盘 | 一轮 review 后整改完成 |
| 9 | `/plan-gate` | 方案门禁（独立） | 对架构方案做独立评审 |
| 10 | `/req-review` | 需求评审（独立） | 评审需求/设计/实现/PR |
| 11 | `/deploy` | CI/部署配置 | 需要配置 CI 或部署 |

---

### 4.1 `/product-discovery` — 产品发现

**流程 / Flow**:

```
requirement-analyst（需求分析）
    → [停下等确认]
    → ux-researcher（用户研究）
    → product-designer（产品设计）
    → req-coordinator（需求评审）
        ├─ 有阻塞项 → requirement-analyst 修复 → 重新评审
        └─ 无阻塞项 → 汇总汇报
```

**产出 / Deliverables**:
- `requirements.md` — 结构化需求文档
- `personas.md` — 用户画像
- `user-journey.md` — 用户旅程
- `competitive-analysis.md` — 竞品分析
- `ia.md` — 信息架构
- `flows.md` — 交互流程
- `design-spec.md` — 设计规范
- 需求评审报告 — 阻塞项与建议项清单

**用法 / Usage**:

```bash
/product-discovery 设计一个多租户会议室预约功能
```

**最佳实践 / Best Practice**:
- 第二步会强停一次等你确认——需求错了后面全错，必须先对齐
- 第五步自动调用需求评审团队，确保需求质量后再进入开发
- / The second step forces a pause for your confirmation — get requirements right before moving on. Step 5 auto-invokes the requirements review team.

---

### 4.2 `/new-feature` — 新功能开发

**流程 / Flow**:

```
开发前置检查（六步门禁）
    → pm（任务规划）
    → [停下等确认]
    → architect（架构设计）
    → plan-risk-analyst（失效点扫描）
    → plan-gatekeeper（放行判定）
        ├─ PASS → db-engineer → backend-dev → frontend-dev → tester → reviewer
        ├─ CONDITIONAL → 逐条确认后继续
        └─ REJECT → 退回 architect 修订
```

**用法 / Usage**:

```bash
/new-feature 实现会议室预约功能
```

**最佳实践 / Best Practice**:
- 这是"全流程开发"命令，从规划一路到审查
- 每个交付物完成即提交，不攒到最后
- / This is the "full workflow" command — from planning to review. Each deliverable is committed immediately.

---

### 4.3 `/review` — 代码审查

**流程 / Flow**:

```
reviewer（只读）→ 检查 CLAUDE.md 约束 → 输出结构化报告
    ✅ 通过 / ❌ 问题（文件路径 + 行号 + 修复建议）
```

**用法 / Usage**:

```bash
/review
```

**最佳实践 / Best Practice**:
- reviewer 是只读角色，只提问题不改代码
- 发现问题修复后，再跑一次 `/review` 确认
- / reviewer is read-only. After fixing issues, run `/review` again to confirm.

---

### 4.4 `/gen-tests` — 生成单元测试

**流程 / Flow**:

```
tester → 为指定 Service 生成单元测试 → 覆盖正常/异常/边界 → 跑通后提交
```

**用法 / Usage**:

```bash
/gen-tests 给 RoomService 生成单元测试
```

**最佳实践 / Best Practice**:
- 适合补充式生成；`/new-feature` 流程里已内含 tester 环节
- 指定具体的 Service 名称，效果更好
- / Specify a concrete Service name for better results.

---

### 4.5 `/gen-test-cases` — 编写功能测试用例

**流程 / Flow**:

```
functional-tester → 判定工作模式
    ├─ 模式 A：文档驱动（有 requirements.md）
    ├─ 模式 B：代码逆向（只有代码工程）
    └─ 混合模式
→ 设计用例（5 种黑盒 + 7 种白盒）→ 落盘到 docs/00-项目文档/test-cases/
```

**用法 / Usage**:

```bash
/gen-test-cases 会议室预约
```

**最佳实践 / Best Practice**:
- 先用这个把"测什么"想清楚，再用 `/gen-tests` 把高价值用例自动化
- / Use this first to figure out "what to test", then use `/gen-tests` to automate high-value cases.

---

### 4.6 `/change-request` — 需求变更

**流程 / Flow**:

```
requirement-analyst（变更理解）
    → architect + requirement-analyst（影响分析）
    → pm（增量规划）
    → [停下等确认]
    → 实施（只改受影响部分）
    → reviewer（强制审查，强度按影响分级）
    → pm（归档）
```

**用法 / Usage**:

```bash
/change-request 把预约时长从 2 小时改成 4 小时
```

**最佳实践 / Best Practice**:
- 和 `/new-feature` 的关键区别：变更多了影响分析、增量规划、强制审查
- 不要直接改代码，走变更闭环
- / Key difference from `/new-feature`: change has impact analysis, incremental planning, and mandatory review. Don't modify code directly — use the change loop.

---

### 4.7 `/fix-bug` — Bug 修复

**流程 / Flow**:

```
bug-fixer → 五步闭环
    1. 复现（复现不出则汇报假设清单、停下等确认）
    2. 根因定位（禁止治标不治本）
    3. 最小修复（遵守红线、最小 diff）
    4. 回归验证（先补一条能失败的回归测试再修复）
    5. 知识沉淀（回写 lessons-learned.md）
```

**用法 / Usage**:

```bash
/fix-bug 预约时段跨越午夜时前端显示成负数时长
```

**最佳实践 / Best Practice**:
- 根因涉及架构/红线时会自动派 reviewer 专项审查
- 修复经验会沉淀到 `lessons-learned.md`，反哺规范
- / Fix experiences are captured in `lessons-learned.md` to improve standards over time.

---

### 4.8 `/retro` — 经验沉淀

**流程 / Flow**:

```
pm（收集问题）→ 三层分类
    ├─ 规范缺口 → 更新 .claude/standards/
    ├─ 项目坑 → 更新 CLAUDE.md 注意事项
    └─ 一次性问题 → 跳过不沉淀
→ 定向沉淀 → 汇报
```

**用法 / Usage**:

```bash
/retro
```

**最佳实践 / Best Practice**:
- 这是"自升级"机制——规范随时间进化，而不是静态文档
- 可选"回填 skill"：用户确认通用性后同步回模板
- / This is the "self-upgrade" mechanism — standards evolve over time instead of being static.

---

### 4.9 `/plan-gate` — 方案门禁（独立）

**流程 / Flow**:

```
plan-risk-analyst（R1~R7 失效点扫描）
    → plan-gatekeeper（C1 清晰度 / C2 完整性 / C3 可验证性）
    → PASS / CONDITIONAL / REJECT
```

**用法 / Usage**:

```bash
/plan-gate
```

**最佳实践 / Best Practice**:
- 可独立于 `/new-feature` 使用，适合存量项目补门禁
- / Can be used independently of `/new-feature`, ideal for existing projects.

---

### 4.10 `/req-review` — 需求评审（独立）

**流程 / Flow**:

```
req-coordinator（调度评审团队）
    → req-quality-group-lead（质量组）
        ├─ req-quality-reviewer（完整性/无歧义性/可测试性）
        └─ req-consistency-reviewer（需求→API→DB→代码一致性）
    → req-impl-group-lead（实现合规组）
        ├─ req-change-impact-reviewer（影响范围/连锁反应/回滚方案）
        ├─ req-compliance-reviewer（分层边界/响应格式/字段映射）
        └─ req-test-coverage-reviewer（测试用例覆盖度）
    → 评审报告（阻塞项 + 建议项）
    → 有阻塞项 → 修复 → 重新评审
```

**用法 / Usage**:

```bash
# 评审需求文档（默认）
/req-review

# 评审设计文档
/req-review design

# 评审实现符合性
/req-review implementation

# 评审 PR
/req-review pr
```

**最佳实践 / Best Practice**:
- 可独立于 `/product-discovery` 使用，适合存量项目补做需求评审
- 支持 4 个评审阶段：requirements / design / implementation / pr
- 与 `/plan-gate` 的区别：`/req-review` 评审需求质量，`/plan-gate` 评审架构方案
- / Can be used independently of `/product-discovery`, ideal for existing projects. Supports 4 review stages: requirements / design / implementation / pr.

---

### 4.11 `/deploy` — CI/部署

**流程 / Flow**:

```
devops → 基于内置部署文件按需扩展
    - .github/workflows/ci.yml
    - Dockerfile.api / Dockerfile.web
    - docker-compose.yml
```

**用法 / Usage**:

```bash
/deploy 给 CI 加上测试覆盖率报告
```

---

## 5. 从零到一：完整开发流程

### 场景 A：从零开始一个新功能

```bash
# 1. 从模糊想法开始 / Start with a fuzzy idea
/product-discovery 设计一个 XX 功能

# 2. 需求明确后，全流程开发 / After requirements are clear, full dev workflow
/new-feature 实现 XX 功能

# 3. 补充单元测试（如需要）/ Add unit tests if needed
/gen-tests 给 XXService 生成单元测试

# 4. 产出功能测试用例文档 / Produce functional test cases
/gen-test-cases XX 功能

# 5. 上线后复盘 / Post-release retrospective
/retro
```

### 场景 B：需求变了

```bash
# 走变更闭环，不要直接改代码 / Use the change loop, don't modify code directly
/change-request 把 XX 从 A 改成 B
```

### 场景 C：修 Bug

```bash
# 五步闭环修复 / 5-step closed-loop fix
/fix-bug 描述 Bug 现象
```

### 场景 D：已有项目接入

```bash
# 1. 接入项目 / Onboard
/onboard-project /path/to/existing-project

# 2. 填写 CLAUDE.md（从代码推断预填，补充业务红线）/ Fill CLAUDE.md

# 3. 补功能测试用例 / Add test cases
/gen-test-cases XX 模块

# 4. 开始开发 / Start development
/new-feature 实现 XX 功能
```

### 场景 E：对存量项目做方案评审

```bash
# 独立门禁 / Independent gate
/plan-gate
```

---

## 6. 关键约定与最佳实践

### 6.1 SubAgent 编排 / SubAgent Orchestration

角色工作（分析/设计/开发/审查）必须通过 Task 工具下发给 `.claude/agents/` 里的对应 SubAgent，不在主 Agent 里内联做。

Role work (analysis/design/dev/review) must be delegated to the corresponding SubAgent via the Task tool, not done inline.

### 6.2 阶段化提交 / Phased Commits

每个交付物落盘后立即 `git commit`，禁止攒到最后。commit message 遵循 Conventional Commits：

Commit immediately after each deliverable. Follow Conventional Commits:

```
docs: 需求分析文档
feat: 后端实现
test: 单元测试
fix: 审查问题修复
```

### 6.3 分支约定 / Branch Convention

```
main（干净可构建）
  └── feat/xxx（功能分支）
  └── change/xxx（变更分支）
```

- `main` 始终干净可构建 / `main` is always clean and buildable
- 完成后合回 `main` / Merge back when done

### 6.4 数据库迁移 / Database Migrations

```
sql/migrations/
├── V001__init_tables.sql
├── V002__add_room_table.sql
└── V003__add_booking_index.sql
```

- 表结构变更走版本化脚本，禁止手工改库
- Schema changes use versioned scripts. No manual DB changes.
- 只增不改、顺序执行、幂等优先 / Add-only, sequential, idempotent

### 6.5 前端类型生成 / Frontend Type Generation

```bash
npm run gen:api   # 从后端 Swagger 自动生成业务实体类型
```

- 业务实体类型由 Swagger 自动生成，禁止手写
- Business entity types are auto-generated from Swagger. No manual typing.

### 6.6 路径范围 rules / Path-Scoped Rules

编辑匹配文件时自动加载对应规范，无需手动读取：

Auto-loaded when editing matching files — no manual reading needed:

| 规则文件 / Rule File | 触发路径 / Trigger Paths |
|---------------------|------------------------|
| `workflow.md` | 始终加载 / Always loaded |
| `database.md` | 始终加载 / Always loaded |
| `git.md` | 始终加载 / Always loaded |
| `backend-api.md` | `src/backend/api/**` |
| `backend-domain.md` | `src/backend/domain/**` |
| `backend-infra.md` | `src/backend/infra/**` |
| `frontend-pages.md` | `src/web/src/views/**` |
| `frontend-state.md` | `src/web/src/stores/**`, `src/web/src/api/**` |

---

## 7. 常见问题 FAQ

**Q: 我可以直接改代码吗？/ Can I modify code directly?**

A: 可以，但建议通过 `/new-feature` 或 `/change-request` 走完整流程，确保所有 Agent 协作。

A: Yes, but it's recommended to use `/new-feature` or `/change-request` for the full workflow.

---

**Q: 门禁被 REJECT 了怎么办？/ What if the gate REJECTs my plan?**

A: 退回 `architect` 修订方案，然后重跑 `/plan-gate`。

A: Return to `architect` for revision, then re-run `/plan-gate`.

---

**Q: `/review` 和 `/gen-tests` 的区别？/ Difference between `/review` and `/gen-tests`?**

A: `/review` 是代码审查（检查规范遵守情况），`/gen-tests` 是生成单元测试代码。

A: `/review` checks code against standards. `/gen-tests` generates unit test code.

---

**Q: `/gen-tests` 和 `/gen-test-cases` 的区别？/ Difference between `/gen-tests` and `/gen-test-cases`?**

A: `/gen-tests` 生成可运行的单元测试代码（xUnit/pytest）。`/gen-test-cases` 产出测试用例文档（测什么、怎么测）。先用后者想清楚，再用前者自动化。

A: `/gen-tests` generates runnable unit test code. `/gen-test-cases` produces test case documents. Use the latter first to think clearly, then the former to automate.

---

**Q: `/retro` 和 `/fix-bug` 的区别？/ Difference between `/retro` and `/fix-bug`?**

A: `/fix-bug` 沉淀单个 Bug 的根因与教训。`/retro` 是对一整轮 review 暴露的共性问题做系统性沉淀。

A: `/fix-bug` captures lessons from a single bug. `/retro` systematically captures patterns from a round of reviews.

---

**Q: onboard-project 后原有代码会受影响吗？/ Will existing code be affected after onboard-project?**

A: 不会。onboard-project 只增不删，每步 git commit，方便回滚。

A: No. onboard-project only adds, never deletes. Each step is git committed for easy rollback.

---

## 一句话串起整个生命周期 / One Sentence Summary

```
/product-discovery → /new-feature → /review → /gen-tests
    → /gen-test-cases → /change-request → /fix-bug → /retro → /deploy
```

10 个命令各管一段，配合 23 个 SubAgent，构成一个能自我进化的闭环。

10 commands, each covering a phase, working with 23 SubAgents — forming a self-evolving closed loop.
