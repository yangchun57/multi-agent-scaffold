# 星枢（starxhub）— new-project skill 使用说明

## 快速上手：从初始化项目目录开始

### 第 0 步：环境要求

| 依赖 | 用途 | 版本要求 |
|------|------|----------|
| Python | 运行脚手架脚本 | 3.8+ |
| .NET SDK | 生成后端 API 工程 | 8.0+ |
| Node.js / npm | 生成前端 Web 工程 | 18+ / 9+ |
| git | 版本管理（脚手架自动 git init） | 任意现代版本 |
| Claude Code CLI | 启动多 Agent 团队 | 最新版 |

### 第 1 步：初始化项目目录

**方式一：通过千问办公（推荐）**

对千问办公说：

> 初始化一个 Claude Code 多 Agent 项目，叫「电商系统」，代码名 Ecommerce，放到 D:/projects/ecommerce

**方式二：直接运行脚手架脚本**

```bash
python ~/.qwenworkcn/skills/claude-code-multi-agent-scaffold/scripts/scaffold.py \
  <目标目录> \
  --name "电商系统" \
  --desc "B2C 电商平台" \
  --code-name "Ecommerce" \
  --backend dotnet --frontend vue
```

参数说明：

| 参数 | 说明 | 默认值 |
|------|------|--------|
| `--name` | 中文显示名，用于 CLAUDE.md/README 标题 | 新项目 |
| `--desc` | 一句话项目描述 | 空 |
| `--code-name` | 代码工程名（英文 PascalCase），决定解决方案与前端工程命名 | App |
| `--backend` | 后端技术栈：`dotnet`（.NET 8+SqlSugar）或 `python`（FastAPI+SQLAlchemy） | 交互式询问，默认 dotnet |
| `--frontend` | 前端技术栈：`vue`（Vue3+Element Plus）或 `uniapp`（uni-app H5+小程序） | 交互式询问，默认 vue |
| `--standards` | 自定义开发规范源目录（覆盖内置规范；缺省按所选栈加载对应规范子集） | 内置规范 |

> 技术栈可配置：命令行传了就用；**没传且处于交互终端时会逐项列选项让你选**，绝不静默。非交互（CI/脚本）下未传则报错要求显式指定。所选栈会渲染进 Agent 定义与 CLAUDE.md，并只加载对应的开发规范（后端 .NET/Python、前端 Vue/uni-app + 通用），CI 与 Dockerfile 也随之切换变体。

脚本会一次性生成（含 git init + 初始提交）：

```
<项目根目录>/
├── CLAUDE.md                     ← 项目集体记忆（含 TODO，需填写）
├── .claude/                      ← 21 个 Agent + 9 个命令 + hooks + 7 份规范
├── .github/                      ← CI workflow（复用 ci.sh）+ dependabot
├── scripts/ci.sh + .githooks/    ← 本地优先质量门禁（fmt+build+test+前端构建；pre-push 推送前自动跑）
├── docs/00-项目文档/              ← 文档模板 + 变更/经验记录
├── src/backend/
│   ├── api/                      ← 后端工程（dotnet=.NET 8 分层+迁移+集成测试基类；python=FastAPI+SQLAlchemy 结构骨架）
│   └── web/                      ← 前端工程（vue=Vue3+Element Plus+prettier+gen:api；uniapp=uni-app 跨端）
├── docker-compose.yml            ← 本地编排（MySQL + API + Web）
├── .editorconfig / .gitattributes
└── .mcp.json / .gitignore
```

### 第 2 步：填写 CLAUDE.md（接入业务的关键一步）

打开项目根目录的 `CLAUDE.md`，把 TODO 占位符换成真实内容：

1. **项目速览**：这个项目是什么、技术栈
2. **最高优先级约束**（最重要）：这个项目的业务红线，如隔离要求、字段映射、分层边界、响应格式——所有 Agent 都以此为最高准则
3. **常用命令**：构建/测试/启动命令

### 第 3 步：构建验证代码工程

```bash
cd src/backend/api && dotnet build      # 后端（首次会还原依赖）
cd src/backend/web && npm install       # 前端依赖安装
cd src/backend/web && npm run dev       # 前端启动验证
```

### 第 4 步：启动 Claude Code

```bash
cd <项目根目录>      # 必须是根目录（含 CLAUDE.md 的目录），不是 src/ 子目录
claude
```

Claude Code 自动读取 CLAUDE.md 和 .claude/agents/，团队就绪。

### 第 5 步：开始使用（按生命周期顺序）

```bash
# ① 从模糊想法开始：产出需求 + 设计文档
/product-discovery 设计一个 XX 功能

# ② 需求明确后开发：规划→实施→测试→审查
/new-feature 实现 XX 功能

# ③ 代码完成后：独立审查 / 补测试
/review
/gen-tests 给 XXService 生成单元测试

# ④ 需求变了：变更闭环（影响分析→增量规划→强制审查）
/change-request 把 XX 从 A 改成 B

# ⑤ review 整改完：经验沉淀，反哺规范
/retro

# ⑥ 配置 CI/部署
/deploy 给 CI 加上测试覆盖率
```

### 第 6 步：关联远程仓库（可选）

```bash
git remote add origin <远程地址>
git push -u origin main
```

push 后 CI（.github/workflows/ci.yml）自动运行：后端 build+test、前端 build。

---

# 命令详解

这个 skill 有 9 个命令，覆盖从"模糊想法"到"上线复盘"的完整生命周期。先讲通用约定，再逐个展开。

## 所有命令共有的三条约定

1. **SubAgent 编排**：角色工作（分析/设计/开发/审查）必须通过 Task 工具下发给 `.claude/agents/` 里的对应 SubAgent，不在主 Agent 里内联做；只有澄清、确认、汇报这些编排动作留在主 Agent。
2. **阶段化提交**：每个交付物落盘后立即 `git commit`，禁止攒到最后；commit message 遵循 Conventional Commits（`docs:`/`feat:`/`fix:`/`test:`/`chore:`）。
3. **全程遵循 CLAUDE.md**：所有角色先读 CLAUDE.md 和 `docs/00-项目文档/` 里的上游产出，不靠对话传上下文。
4. **分支约定**：main 始终干净可构建；功能在 `feat/xxx`、变更在 `change/xxx` 分支进行，阶段化提交落在功能分支，完成后合回 main。

---

## 1. `/product-discovery` — 产品发现与需求设计

**触发时机**：项目刚开始，只有一句模糊想法，还没写需求文档。

**五步流程**：

1. **需求分析**（启动 requirement-analyst）→ 产出结构化需求文档，写回 `requirements.md`，然后提交 `docs: 需求分析文档`
2. **需求确认**（主 Agent）→ 把需求摘要展示给你，**停下等拍板**，你确认后才继续
3. **用户研究**（启动 ux-researcher）→ 产出用户画像 `personas.md`、用户旅程 `user-journey.md`、竞品分析 `competitive-analysis.md`，提交 `docs: 用户研究`
4. **产品设计**（启动 product-designer）→ 产出信息架构 `ia.md`、交互流程 `flows.md`、设计规范 `design-spec.md`，提交 `docs: 产品设计`
5. **汇总**（主 Agent）→ 汇报需求、研究、设计产出清单和下一步建议

**用法示例**：
```
/product-discovery 设计一个多租户会议室预约功能
```

**注意**：第二步会强停一次等你确认，这是刻意设计——需求错了后面全错，所以必须先对齐。

---

## 2. `/new-feature` — 新功能开发

**触发时机**：需求已明确（`requirements.md` 存在），要落地开发某个功能。

**四步流程**：

1. **开发前置检查**（主 Agent，六步门禁）→ 读 CLAUDE.md → 确认需求文档 → 确认设计文档 → 字段映射预检（pageIndex/items 红线）→ Git 分支检查（main 则建 feat/xxx 分支，禁止在 main 直接实施）→ 输出 ✅/⚠️ 检查结果，全部通过才进入规划（吸收自原全局 dev-start skill）
2. **任务规划**（启动 pm）→ 把需求拆成可执行任务，写回 `task-plan.md`，提交 `docs: 任务计划`
3. **计划确认**（主 Agent）→ 把任务计划展示给你，**停下等拍板**
4. **按计划派发**（依次启动下游 SubAgent）→ 每个交付物完成即提交：
   - architect → `docs: 架构与接口契约`
   - db-engineer → `docs: 数据库设计`
   - backend-dev → `feat: 后端实现`
   - frontend-dev → `feat: 前端实现`
   - tester → `test: 单元测试`
   - reviewer → `fix: 审查问题修复`

**用法示例**：
```
/new-feature 实现会议室预约功能
```

**注意**：这是"全流程开发"命令，从规划一路到审查。如果只是想补某个环节（比如只审查、只补测试），用下面的 `/review` 或 `/gen-tests`。

---

## 3. `/review` — 触发代码审查

**触发时机**：想对最近的代码变更做一次合规审查（改动完成后、合并前）。

**流程**：启动 reviewer SubAgent（只读），检查是否遵守 CLAUDE.md 的最高优先级约束（隔离、字段映射、分层边界、响应格式），输出结构化报告（✅ 通过 / ❌ 问题 + 文件路径 + 行号 + 修复建议）。

**用法示例**：
```
/review
```

**注意**：reviewer 是只读角色，只提问题不改代码。发现问题修复后提交 `fix: 审查问题修复`。

---

## 4. `/gen-tests` — 生成单元测试

**触发时机**：某个 Service 逻辑写好了，但缺测试。

**流程**：启动 tester SubAgent，为指定 Service 生成单元测试，覆盖正常、异常、边界三类场景，跑通后提交 `test: 单元测试`。

**用法示例**：
```
/gen-tests 给 RoomService 生成单元测试
```

**注意**：适合补充式生成；`/new-feature` 流程里已经内含了 tester 环节，独立测试用它。

---

## 5. `/change-request` — 需求变更

**触发时机**：代码已经完成甚至验收了，但需求要改（改行为、改字段、删功能、调优先级）。这是**变更**，不是新功能，所以用这个而不是 `/new-feature`。

**六步流程**（重点是有独立审查关卡）：

1. **变更理解**（启动 requirement-analyst）→ 澄清改什么/为什么/新验收标准，分类（新增/修改/删除/延期），更新 `requirements.md` 版本号和变更记录，提交 `docs: 需求变更分析`
2. **影响分析**（启动 architect + requirement-analyst 并行）→ 三层影响：需求层/设计层/代码层，并给出**影响分级**（高=红线/库表/契约，中=业务逻辑/页面，低=文案/配置），提交 `docs: 变更影响分析`
3. **增量规划**（启动 pm）→ 只规划受影响任务，**停下等确认**
4. **按计划实施**（下游 SubAgent）→ 只改受影响部分，tester 做回归测试，提交 `feat: 变更实施` + `test: 回归测试`
5. **审查**（启动 reviewer，**强制关卡不可跳过**）→ 审查强度按影响分级：高=全面审查、中=正常审查、低=快速审查，提交 `fix: 变更审查修复`
6. **归档**（启动 pm）→ 更新 backlog/task-plan/change-log，提交 `docs: 变更记录归档`

**用法示例**：
```
/change-request 把预约时长从 2 小时改成 4 小时
```

**注意**：和 `/new-feature` 的关键区别——变更是"改已有的"，所以多了影响分析、增量规划（避免全量重做）、和按影响分级定强度的强制审查，回归风险是这里的核心关注。

---

## 6. `/retro` — 经验沉淀 / 复盘（自升级）

**触发时机**：一轮 review 找出一堆问题、整改完成后，把踩过的坑沉淀成知识，避免下次重复。

**四步流程**：

1. **收集问题**（启动 pm）→ 汇总 review 问题、task-plan、change-log，去重归类
2. **三层分类**（pm）→ 分成三类：
   - **规范缺口**（规范没写清导致）→ 更新 `.claude/standards/`
   - **项目坑**（项目特有遗留）→ 更新 `CLAUDE.md` 注意事项
   - **一次性问题**（偶发）→ 跳过不沉淀
3. **定向沉淀**（pm）→ 写回规范/注意事项/`lessons-learned.md`，提交 `docs: 经验沉淀`
4. **汇报**（主 Agent）→ 沉淀了多少条、改了哪些文件、哪些判定为一次性

**用法示例**：
```
/retro
```

**注意**：这是"自升级"机制——它把 review 暴露的问题反向沉淀到规范和注意事项里，让规范随时间进化，而不是静态文档。第四步还有可选的「回填 skill」：用户确认哪些沉淀具有跨项目通用性后，同步回 skill 模板（standards/agents），让下个新项目直接受益；项目特有的坑不回填。

---

## 7. `/deploy` — 部署 / CI 配置

**触发时机**：需要配置或调整 CI 流水线、容器化、部署脚本、环境配置时。这是 devops Agent 的命令入口。

**流程**：启动 devops SubAgent，基于脚手架内置的部署文件按需扩展：

- `.github/workflows/ci.yml` — CI（push/PR：后端 build+test、前端 build 含类型检查）
- `Dockerfile.api` / `Dockerfile.web` — 前后端多阶段容器构建
- `docker-compose.yml` — 本地编排（MySQL + API + Web）

典型任务：加缓存/测试覆盖率、镜像发布、服务器部署脚本、dev/staging/prod 环境差异。

**用法示例**：
```
/deploy 给 CI 加上测试覆盖率报告
```

**注意**：表结构变更走 `sql/migrations/V00N__xxx.sql` 版本化脚本（只增不改、顺序执行、幂等优先），禁止手工改库；前端业务实体类型优先 `npm run gen:api` 从后端 Swagger 自动生成，生成物为唯一事实源。

---

## 8. `/gen-test-cases` — 编写功能测试用例

**触发时机**：要为某个功能范围产出完整、详细的功能测试用例文档（新功能验收前、或存量项目补测试）。

**四步流程**：

1. **派发用例设计**（启动 functional-tester）→ SubAgent 自行判定工作模式：`requirements.md` 有真实验收标准 → 模式 A（文档驱动）；只有代码工程或文档全是 `{TODO}` → 模式 B（代码逆向还原功能再设计）；部分覆盖 → 混合模式逐条标注来源。用 5 种黑盒 + 7 种白盒方法设计用例，落盘到 `docs/00-项目文档/test-cases/`
2. **提交**（主 Agent）→ 用例落盘即提交 `docs: {功能范围}功能测试用例`
3. **存疑确认**（主 Agent，仅模式 B / 混合）→ 把 SubAgent 的存疑清单展示给你，**停下等拍板**；需修正则出 v0.2 版本（不覆盖旧版）再提交
4. **汇报**（主 Agent）→ 用例统计（总数、优先级分布、模式占比）、存疑处理结果、后续建议（如派 tester 落地为自动化测试）

**用法示例**：
```
/gen-test-cases 会议室预约
```

**注意**：这里的 functional-tester 产出的是**测试用例文档**（黑盒/白盒设计），与 `/gen-tests`（tester 生成可运行的 xUnit 单元测试代码）是两个层次——先用前者把"测什么"想清楚，再用后者把高价值用例自动化。

---

## 9. `/fix-bug` — 修复 Bug（五步闭环 + 知识沉淀）

**触发时机**：需要修复缺陷、排查线上异常、处理回归 Bug，且希望修复经验能沉淀下来。

**四步流程**：

1. **派发修复**（启动 bug-fixer）→ SubAgent 执行五步闭环：① 复现优先（复现不出则汇报假设清单、停下等确认）② 根因定位（禁止治标不治本）③ 最小修复（遵守红线、最小 diff）④ 回归验证（先补一条能失败的回归测试再修复，全量测试通过）⑤ 知识沉淀（回写 `lessons-learned.md`，规范类教训同步更新 `.claude/standards/`）
2. **提交**（主 Agent）→ 修复+测试通过后提交 `fix: {Bug 简述}`；若更新了规范，追加 `docs: {规范名}补充{教训点}`
3. **审查**（主 Agent 按需）→ 根因涉及架构/红线（tenant_id、认证授权、字段映射）或多文件改动时派 reviewer 专项审查；单点小修复可跳过
4. **汇报**（主 Agent）→ 根因结论、修改清单、验证结果、沉淀记录摘要；若 bug-fixer 提请新增 CLAUDE.md 红线，**停下等确认后再写入**

**用法示例**：
```
/fix-bug 预约时段跨越午夜时前端显示成负数时长
```

**注意**：与 `/retro` 的分工——`/fix-bug` 沉淀的是**单个 Bug 的根因与教训**（就地写回 lessons/规范），`/retro` 是对**一整轮 review/变更暴露的共性问题**做三层分类后的系统性沉淀。两者都遵循"先失败测试后修复"，绝不为了绿而改测试。

---

## 一句话串起整个生命周期

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

9 个命令各管一段，配合 21 个 SubAgent（含需求评审团队与测试修复角色）、阶段化提交、版本化数据库迁移和 Swagger 类型生成，构成一个能自我进化的闭环。
