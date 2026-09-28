# CLAUDE.md — {{PROJECT_NAME}}项目记忆

本文件是项目内所有 Agent（含主对话和 Subagent）共享的集体记忆与最高规范。任何 Agent 开工前必须先读取本文件。

## 项目速览

{{PROJECT_DESC}}

## 技术栈

- **后端**：{{BACKEND_STACK}}
- **前端**：{{FRONTEND_STACK}}
- **多租户**：共享数据库 + `tenant_id` 字段隔离（业务表实体必须携带租户字段，查询经全局过滤器）

<!-- 若与本项目的实际栈不符，请就地修改本节。 -->

## 最高优先级约束（违反即返工，任何情况下不得妥协）

<!-- TODO: 填写本项目的业务红线，这是最关键的部分。示例（脚手架已按所选栈预填通用部分，业务约束请补充）：
1. **【隔离红线】** 所有业务表实体必须包含租户隔离字段 tenant_id，所有查询必须经过全局过滤器。
2. **【字段映射红线】** {{FIELD_MAPPING}}，前端禁止自行改名。
3. **【分层边界红线】** 接口层禁含业务逻辑；业务层禁操作 Web 上下文；模型层禁含业务方法；通用层禁反向依赖业务层。
4. **【响应格式红线】** 统一返回 {{ENVELOPE}}。
-->

## 开发规范引用（按需读取，不要复制全文到记忆）

| 规范 | 路径 | 何时读 |
|------|------|--------|
| 后端规范 | `{{BACKEND_STANDARDS_FILE}}` | 写任何后端代码前 |
| 前端规范 | `{{FRONTEND_STANDARDS_FILE}}` | 写任何前端代码前 |
| 通用开发规范 | `.claude/standards/通用开发规范.md` | 涉及数据库、字段映射、代码审查时 |


**规范加载约定**：
1. 优先读 `.claude/standards/topics/INDEX.md` 定位主题，只读相关主题文件；或 Grep 定位后局部读取
2. 禁止无目的整读大规范（>20KB）
3. **规则上浮/下沉标准**：一条规则若在近期任务中反复用到（三次里两次），上浮到本文件「最高优先级约束」或速查表；一年用不到一次的，只留在 standards 深处——本文件是每次自动加载的，只装 80% 场景用到的 20% 规则

## 项目内文档（下游 Agent 的上下文来源）

| 文档 | 内容 | 维护者 | 阶段 |
|------|------|--------|------|
| `docs/00-项目文档/requirements.md` | 需求分析 | requirement-analyst | 需求 |
| `docs/00-项目文档/personas.md` | 用户画像 | ux-researcher | 需求 |
| `docs/00-项目文档/user-journey.md` | 用户旅程图 | ux-researcher | 需求 |
| `docs/00-项目文档/competitive-analysis.md` | 竞品分析 | ux-researcher | 需求 |
| `docs/00-项目文档/ia.md` | 信息架构 | product-designer | 设计 |
| `docs/00-项目文档/flows.md` | 交互流程 | product-designer | 设计 |
| `docs/00-项目文档/design-spec.md` | 设计规范 | product-designer | 设计 |
| `docs/00-项目文档/backlog.md` | 待办清单 | pm | 规划 |
| `docs/00-项目文档/task-plan.md` | 任务计划 | pm | 规划 |
| `docs/00-项目文档/lessons-learned.md` | 经验教训库 | pm | 复盘 |
| `docs/00-项目文档/change-log.md` | 需求变更记录 | pm | 变更 |
| `docs/00-项目文档/architecture.md` | 系统架构 | architect | 开发 |
| `docs/00-项目文档/api-contracts.md` | 接口契约 | architect | 开发 |
| `docs/00-项目文档/database-design.md` | 数据库设计 | db-engineer | 开发 |

**约定**：上游 Agent 的产出必须落盘到 docs/00-项目文档/，下游 Agent 通过读取文档获取上下文。

## Agent 阵容（21 个专职 Agent，五阶段）

| 阶段 | Agent | 角色 |
|------|-------|------|
| 需求分析 | requirement-analyst / ux-researcher / product-designer | 需求、研究、设计 |
| 任务规划 | pm | 任务拆解、计划 |
| 需求评审 | req-coordinator / req-quality-group-lead / req-impl-group-lead / req-quality-reviewer / req-consistency-reviewer / req-change-impact-reviewer / req-compliance-reviewer / req-test-coverage-reviewer | 需求与契约评审 |
| 开发实施 | architect / db-engineer / backend-dev / frontend-dev / tester / reviewer / devops | 开发 |
| 测试修复 | functional-tester / bug-fixer | 功能测试用例、缺陷修复 |

**协作流程**：模糊需求 → requirement-analyst → ux-researcher → product-designer → pm → req-coordinator（需求评审团队把关，评审通过后再派发）→ 开发 agents → reviewer

**命令入口**：`/product-discovery`（需求+设计）、`/new-feature`（开发）、`/change-request`（变更）、`/gen-test-cases`（功能测试用例）、`/fix-bug`（Bug 修复+知识沉淀）、`/retro`（复盘）、`/deploy`（部署/CI）

## 工作约定

1. 需求先行：先有需求+设计文档，再开发
2. 规划先行：计划经确认后再实施
3. 契约先行：先有架构/契约/数据库设计，再有实现
4. 审查兜底：所有代码经 reviewer 审查
5. 不确定就问：禁止臆测需求
6. 单一职责：一次只让一个 Agent 完成一个明确交付物
7. 代码语言：代码和注释统一中文



## 数据库与类型生成约定

1. **数据库迁移**：表结构变更必须通过 `src/backend/api/sql/migrations/V{三位序号}__{描述}.sql` 版本化脚本（只增不改、顺序执行、幂等优先），禁止手工改库，详见该目录 README
2. **前端类型生成**：业务实体 TS 类型优先 `cd src/backend/web && npm run gen:api` 从后端 Swagger 自动生成（swagger-typescript-api），生成物为唯一事实源；手写仅限 Form/Query 等前端形态
3. **CI**：push/PR 自动触发 `.github/workflows/ci.yml`（后端 build+test、前端 build），本地提交前先确保可通过

## 分支与质量约定

1. **分支模型**（简化 trunk-based）：`main` 始终干净可构建（CI 绿）；功能性工作在 `feat/xxx`、变更在 `change/xxx` 分支进行，完成后合回 main
2. **禁止直接污染 main**：/new-feature、/change-request 的实施阶段应基于分支进行，阶段化提交落在功能分支上
3. **并行开发**：命令交错时（如 /new-feature 进行中来了 /change-request），各自独立分支，避免互相覆盖
4. **静态检查**：后端 `{{BACKEND_LINT}}`（CI 校验）、前端 `prettier`（`npm run format` / `format:check`）、根目录 `.editorconfig` 统一基础格式
5. **集成测试**：红线类约束（隔离、认证授权）优先用集成测试锁死（后端用栈内建应用测试宿主——.NET 为 WebApplicationFactory、Python 为 fastapi TestClient），比文档更硬
6. **依赖更新**：dependabot 每周提 minor/patch 升级 PR，main 分支合并前跑 CI 确认不破坏

## 提交约定（阶段化提交）

1. 每个角色交付物落盘后**立即 git commit**，禁止攒到最后一次性提交
2. 提交粒度：一个角色交付物 = 一个 commit
3. commit message 遵循 Conventional Commits，中文简述：
   - `docs: xxx`   文档（需求/设计/契约/记录）
   - `feat: xxx`   新功能
   - `fix: xxx`    修复
   - `test: xxx`   测试
   - `chore: xxx`  配置/杂项
4. 验证通过才提交（构建失败/测试失败不 commit）
5. 提交由主 Agent 在各阶段交付物落盘后执行

## 常用命令

- 后端构建：`{{BACKEND_BUILD}}`
- 后端测试：`{{BACKEND_TEST}}`
- 前端启动：`cd src/backend/web && npm run dev`
- 前端构建：`cd src/backend/web && npm run build`

<!-- 若所选栈的命令不同（如 uni-app 用 npm run dev:h5），请就地修改。 -->
