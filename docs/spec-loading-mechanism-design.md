# AI Coding Agent 规范实时加载与实践机制设计

> 基于 2025-2026 年最新实践文献的综合设计方案
> 日期：2026-10-08

---

## 一、问题定义

**核心矛盾**：规范文档写了，但 AI coding agent 在编码过程中不遵守、忘记遵守、或根本不知道要遵守。

### 根因分析（来自文献）

| 根因 | 表现 | 文献来源 |
|------|------|----------|
| **上下文窗口有限** | 规范太多装不下，agent 选择性忽略 | Anthropic 2026: CLAUDE.md 建议 <200 行 |
| **上下文腐烂 (Context Rot)** | 长会话中 agent 遗忘早期约束，性能 U 型衰减 | byteiota/Redis 研究: 中间信息召回率下降 30%+ |
| **规范太抽象** | "使用合适的命名" 这类规则 agent 无法执行 | SSOJet: 具体可验证的规则远优于模糊规则 |
| **规范与代码漂移** | 规范说一套，代码实际另一套 | Dre Dyson: drift detection 将成为 CI 标配 |
| **无反馈回路** | agent 声称完成但未验证 | Faros 2026: Victory declaration bias 是头号失败模式 |
| **一次性灌入** | 所有规范在会话开始全部加载，后续被遗忘 | Context Engineering Playbook: 应按需加载 |

---

## 二、理论基础：三代演进

```
Prompt Engineering (2023-2024)
    ↓  "怎么措辞"
Context Engineering (2025)
    ↓  "agent 此刻看到了什么"
Harness Engineering (2026)
       "agent 的整个操作环境怎么设计"
```

**核心公式**：`Agent = Model + Harness`（Mitchell Hashimoto, 2026.02）

> "每次发现 agent 犯了一个错误，就花时间工程化一个解决方案，让 agent 永远不再犯同样的错。" —— Mitchell Hashimoto

**关键认知转变**：模型能力已商品化，agent 的可靠性越来越取决于模型外部的运行时基础设施。LangChain 团队在 2026.03 仅通过优化 harness（不换模型）就将 Terminal Bench 2.0 排名从第 30 提升到第 5。

---

## 三、机制设计：四层规范加载架构

### 3.1 总体架构

```
┌─────────────────────────────────────────────────┐
│  L0: 核心规则层 (Always Loaded)                  │
│  CLAUDE.md / AGENTS.md                           │
│  < 200 行 · 始终在上下文中 · 项目级铁律            │
├─────────────────────────────────────────────────┤
│  L1: 路径范围规则层 (Path-Scoped, On-Demand)      │
│  .claude/rules/*.md                              │
│  按文件 glob 匹配触发 · 仅在编辑相关文件时加载      │
├─────────────────────────────────────────────────┤
│  L2: 任务规格层 (Task-Scoped)                     │
│  specs/*.md · design.md · tasks.md               │
│  按任务加载 · Spec-Driven Development 的产物       │
├─────────────────────────────────────────────────┤
│  L3: 技能/工作流层 (Skill-Triggered)              │
│  .claude/skills/*/SKILL.md                       │
│  名称+摘要常驻(60 token) · 完整内容按需加载(2500+) │
└─────────────────────────────────────────────────┘
```

### 3.2 各层详细设计

#### L0: 核心规则层

**定位**：项目的"宪法"——不可违反的铁律，始终在上下文中。

**文件**：`./CLAUDE.md`（或 `./AGENTS.md`，两者可互操作）

**设计原则**：
- **每条规则必须可追溯到一次真实失败**（Hashimoto 原则）
- **每条规则必须可验证**（能写出对应的 lint/test/assert）
- **总量控制在 150-200 行以内**（Anthropic 2026 实测：超过此数量遵从度急剧下降）

**模板**：

```markdown
# Project: [名称]

## 技术栈
- Python 3.12 / FastAPI / SQLAlchemy / Pydantic v2
- Vue 3 / TypeScript 5 / Vite

## 命令（唯一真相源）
- 构建: `pnpm build`
- 测试: `pnpm test`
- Lint: `pnpm lint`
- 类型检查: `npx tsc --noEmit`

## 铁律（每条对应一次真实失败）
- 永远不要在 `src/generated/` 下手动编辑
- 数据库 schema 变更必须先问
- 所有 API handler 必须有 Pydantic 入参校验
- 禁止 `from module import *`
- 测试必须 mock 外部服务，不 mock 内部模块

## 架构地图
- API 层: src/api/handlers/ → 参考 @docs/api-patterns.md
- 领域层: src/domain/ → 纯业务逻辑，零框架依赖
- 基础设施: src/infra/ → DB/缓存/外部服务适配

## 绝对不做
- 不提交 .env 或密钥
- 不在没有测试的情况下合并
- 不自行升级依赖版本
```

#### L1: 路径范围规则层

**定位**：按文件类型/目录自动触发的专项规范——"编辑 API 文件时自动加载 API 规范"。

**文件**：`.claude/rules/*.md`（Claude Code 原生支持）

**关键机制**：通过 YAML frontmatter 的 `paths` 字段实现 glob 匹配，**只在 agent 读取/编辑匹配文件时触发加载**。

**示例**：

```markdown
---
paths:
  - "src/api/**/*.ts"
---
# API 开发规范

- 所有端点必须有 OpenAPI 注释
- 错误响应统一格式: `{ code, message, details }`
- 认证: Bearer token via `@/middleware/auth`
- 分页: cursor-based, 默认 limit=20, max=100
- 必须包含输入校验（Zod schema）
```

```markdown
---
paths:
  - "src/domain/**/*.py"
---
# 领域层规范

- 纯 Python, 不依赖 FastAPI/SQLAlchemy
- 使用 Pydantic v2 的 BaseModel 定义领域对象
- 领域事件通过 EventBus 发布, 不直接调用 Repository
- 所有业务规则必须有单元测试覆盖
```

```markdown
---
paths:
  - "**/*.test.*", "**/*_test.*"
---
# 测试规范

- 测试文件与源文件同目录: `foo.ts` → `foo.test.ts`
- 命名: `test_<功能>_<场景>_<预期结果>`
- 使用 factory 创建测试数据, 不手写 fixture
- 每个测试只验证一个行为
- 禁止 snapshot 测试用于业务逻辑
```

**为什么有效**：
- 解决了"装不下"问题——只有相关规范进入上下文
- 解决了"遗忘"问题——每次编辑匹配文件时重新加载
- 上下文成本极低——不编辑 API 文件时，API 规范不占 token

#### L2: 任务规格层

**定位**：每个具体任务的"合同"——在动手之前明确要做什么、怎么做、怎么验证。

**核心思想**：Spec-Driven Development（Kiro/AWS 2026 实践）

**工作流**：

```
需求输入 → requirements.md (EARS 格式)
         → design.md (技术方案)
         → tasks.md (分解步骤)
         → 实现 → 验证 → 对照 spec 审计
```

**关键实践**：

1. **实现前**：agent 在 Plan Mode 下先读 spec，生成实现计划
2. **实现中**：agent 可随时回查 spec 作为 anchor
3. **实现后**：对照 spec 的 acceptance criteria 逐条验证

**Spec 文件结构**：

```markdown
# Feature: [功能名称]

## 需求 (requirements.md)
- REQ-001: 当 [前置条件] 时, 如果 [触发事件], 系统应 [预期行为]
- REQ-002: ...

## 设计 (design.md)
- 架构决策: [ADR-xxx]
- 涉及文件: src/api/users.py, src/domain/user.py
- 接口契约: POST /api/users → CreateUserResponse

## 任务 (tasks.md)
- [ ] Task 1: 创建 CreateUserRequest Pydantic model
- [ ] Task 2: 实现 user_service.create_user()
- [ ] Task 3: 添加 API endpoint
- [ ] Task 4: 编写测试覆盖 REQ-001, REQ-002

## 验证清单
- [ ] 所有 acceptance criteria 通过
- [ ] 测试覆盖率 > 80%
- [ ] lint 零警告
- [ ] 无 spec 中未提及的变更
```

#### L3: 技能/工作流层

**定位**：复杂多步骤工作流的封装——名称常驻上下文，完整内容按需加载。

**关键数据**：一个 2500 token 的 Skill，其 header（60 token）常驻上下文，**98% 的上下文成本延迟到实际触发时才支付**。

**示例 Skills**：

```
.claude/skills/
├── code-review/SKILL.md      # /review 命令触发
├── db-migration/SKILL.md     # 涉及 schema 变更时触发
├── api-endpoint/SKILL.md     # 新增 API 时触发
└── deploy-check/SKILL.md     # 部署前触发
```

---

## 四、实时实践保障机制

仅"加载"规范不够，需要闭环保障 agent 真正"实践"规范。

### 4.1 三道防线

```
┌──────────────────────────────────────────────────┐
│  防线 1: Pre-flight (编码前)                       │
│  ─────────────────────────                        │
│  • Plan Mode 探索 → 读取相关 spec 和 rules          │
│  • agent 生成实现计划, 列出将遵循的规范条目           │
│  • 人工审批计划后进入实现                             │
├──────────────────────────────────────────────────┤
│  防线 2: In-loop (编码中)                          │
│  ─────────────────────                            │
│  • Hooks: PostToolUse → 每次文件编辑后自动 lint     │
│  • Hooks: PreToolUse → 阻止编辑受保护文件           │
│  • /goal 设置验证条件, 每轮自动检查                  │
│  • Stop Hook: 任务结束前强制运行验证脚本             │
├──────────────────────────────────────────────────┤
│  防线 3: Post-task (编码后)                        │
│  ──────────────────────                           │
│  • Spec Audit: 对照 spec 逐条检查 acceptance       │
│  • Drift Check: 检测代码是否偏离规范                 │
│  • Correction Log: 记录违规, 反馈到 L0/L1 规则      │
│  • 验证子 agent: 用独立 model 实例复核结果           │
└──────────────────────────────────────────────────┘
```

### 4.2 Hooks 实现示例

```json
// .claude/settings.json
{
  "hooks": {
    "PostToolUse": [
      {
        "matcher": "write_file|edit_file",
        "command": "bash -c 'file=\"$1\"; if [[ \"$file\" == *.py ]]; then ruff check \"$file\" --fix; elif [[ \"$file\" == *.ts ]]; then eslint --fix \"$file\"; fi' _ {}"
      }
    ],
    "PreToolUse": [
      {
        "matcher": "write_file|edit_file",
        "command": "bash -c 'file=\"$1\"; if [[ \"$file\" == *generated* ]] || [[ \"$file\" == *migration* ]]; then echo \"BLOCKED: $file is protected\"; exit 1; fi' _ {}"
      }
    ],
    "Stop": [
      {
        "command": "bash scripts/pre-stop-verify.sh"
      }
    ]
  }
}
```

### 4.3 Drift Detection（规范漂移检测）

**核心思想**：规范文档和实际代码之间的一致性应该像测试一样可自动验证。

```bash
#!/bin/bash
# scripts/drift-check.sh — 检测规范与代码的漂移

DRIFT=0

# 1. 检查 CLAUDE.md 中引用的命令是否存在
grep -oP '`([^`]+)`' CLAUDE.md | grep -E '(npm|pnpm|make) run' | while read cmd; do
  script=$(echo "$cmd" | sed 's/`//g' | awk '{print $NF}')
  if ! grep -q "\"$script\"" package.json 2>/dev/null; then
    echo "DRIFT: CLAUDE.md references '$script' but not in package.json"
    DRIFT=1
  fi
done

# 2. 检查 .claude/rules/ 中引用的路径是否存在
grep -rP 'src/[a-zA-Z/]+' .claude/rules/ | grep -oP 'src/[a-zA-Z/]+' | sort -u | while read path; do
  if [ ! -d "$path" ] && [ ! -f "$path" ]; then
    echo "DRIFT: Rule references '$path' but it doesn't exist"
    DRIFT=1
  fi
done

# 3. 检查 spec 中的 acceptance criteria 是否有对应测试
grep -P '^\- REQ-' specs/*.md | while read req; do
  req_id=$(echo "$req" | grep -oP 'REQ-\d+')
  if ! grep -rq "$req_id" tests/ src/; then
    echo "DRIFT: $req_id has no corresponding test or implementation"
    DRIFT=1
  fi
done

exit $DRIFT
```

**集成到 CI**：

```yaml
# .github/workflows/spec-drift.yml
name: Spec Drift Check
on: [push, pull_request]
jobs:
  drift:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - run: bash scripts/drift-check.sh
```

---

## 五、反馈闭环：从失败到规则

这是整个机制中最关键的部分——**每一次 agent 违规都应该永久改善 harness**。

### 5.1 Correction Log

```markdown
# .claude/corrections.md
# 每次 agent 犯错, 记录并转化为规则

## 2026-10-07: agent 在未校验的 API handler 中直接使用 dict 参数
- 根因: L0 规则不够具体, 只说"要有输入校验"
- 修复: 在 L1 `rules/api.md` 中增加具体示例代码
- 状态: ✅ 已修复

## 2026-10-05: agent 在 domain 层 import 了 FastAPI
- 根因: L1 `rules/domain.md` 缺少"零框架依赖"的强调
- 修复: 在规则中加粗强调, 并添加反面示例
- 状态: ✅ 已修复

## 2026-10-03: agent 生成了 500 行的单文件
- 根因: 无文件长度约束
- 修复: L0 增加 "单文件不超过 300 行" 规则
- 状态: ✅ 已修复
```

### 5.2 规则演化流程

```
agent 犯错
  → 记录到 corrections.md
  → 分析根因（规则缺失？规则模糊？规则冲突？）
  → 修改对应层级的规则文件
  → 运行 drift-check 验证
  → 提交 PR, 团队 review
  → 规则永久生效
```

---

## 六、完整目录结构

```
project-root/
├── CLAUDE.md                    # L0: 核心规则 (<200行)
├── CLAUDE.local.md              # 个人本地规则 (gitignored)
├── .claude/
│   ├── settings.json            # Hooks + 权限配置
│   ├── rules/                   # L1: 路径范围规则
│   │   ├── api.md               #   paths: src/api/**
│   │   ├── domain.md            #   paths: src/domain/**
│   │   ├── testing.md           #   paths: **/*.test.*
│   │   ├── database.md          #   paths: src/infra/db/**
│   │   └── frontend/
│   │       ├── components.md    #   paths: src/components/**
│   │       └── state.md         #   paths: src/stores/**
│   ├── skills/                  # L3: 技能/工作流
│   │   ├── code-review/SKILL.md
│   │   ├── db-migration/SKILL.md
│   │   └── deploy-check/SKILL.md
│   └── corrections.md           # 纠错日志
├── specs/                       # L2: 任务规格
│   ├── feature-x/
│   │   ├── requirements.md
│   │   ├── design.md
│   │   └── tasks.md
│   └── feature-y/
│       └── ...
├── docs/
│   ├── adr/                     # 架构决策记录
│   └── api-patterns.md          # 被 CLAUDE.md @import 的参考文档
├── scripts/
│   ├── drift-check.sh           # 规范漂移检测
│   └── pre-stop-verify.sh       # 任务结束前验证
└── .github/
    └── workflows/
        └── spec-drift.yml       # CI 集成漂移检测
```

---

## 七、关键设计原则总结

| 原则 | 说明 | 文献依据 |
|------|------|----------|
| **地图而非领土** | 规则文件是指向深层文档的索引，不是文档本身 | Anthropic 2026 Memory Docs |
| **每条规则可追溯** | 每条规则对应一次真实失败，写在 corrections.md 中 | Hashimoto 2026 |
| **每条规则可验证** | 能写出对应的 lint/test/assert 才算合格 | SSOJet / Faros 2026 |
| **渐进式加载** | 不是一次灌入，而是按需、按路径、按任务加载 | Context Engineering Playbook |
| **删除优于添加** | Anthropic 2026.07 删除 80% system prompt 无性能损失 | byteiota 2026 |
| **验证闭环** | agent 不能自己声称完成，必须有独立验证手段 | Faros: Victory declaration bias |
| **漂移检测** | 规范与代码的一致性应像测试一样自动化 | Dre Dyson 2025 |
| **子 agent 隔离** | 长任务分解给子 agent，各自维护干净上下文 | Anthropic Subagent Patterns |

---

## 八、实施路线图

### Phase 1: 基础设施（1天）
- [ ] 运行 `/init` 生成初始 CLAUDE.md
- [ ] 创建 `.claude/rules/` 目录，按模块拆分规则
- [ ] 配置 Hooks（PostToolUse lint, PreToolUse 保护）
- [ ] 创建 `scripts/drift-check.sh`

### Phase 2: 规范沉淀（1周）
- [ ] 梳理现有规范文档，分配到 L0/L1/L2
- [ ] 为每个 L1 规则文件添加 `paths` frontmatter
- [ ] 编写 2-3 个关键 Skills
- [ ] 建立 corrections.md 并开始记录

### Phase 3: 闭环验证（持续）
- [ ] 将 drift-check 集成到 CI
- [ ] 建立"犯错→记录→修规则"的反馈循环
- [ ] 每月审查规则文件，删除过时/冲突条目
- [ ] 度量：跟踪 agent 违规频率，验证机制有效性

---

## 九、参考文献

1. Anthropic. "Best practices for Claude Code." 2025-2026. https://www.anthropic.com/engineering/claude-code-best-practices
2. Anthropic. "Claude 如何记住你的项目 — Memory 文档." https://code.claude.com/docs/zh-CN/memory
3. Hashimoto, Mitchell. "My AI Adoption Journey." February 2026. (Harness Engineering 概念提出)
4. AWS Builder Center. "Harness Engineering with Kiro: Spec-Driven Development for the Multi-Agent Era." 2026.
5. Faros AI. "Harness engineering: What makes AI coding agents work in 2026."
6. Dre Dyson. "The Hidden Truth About AI Coding Tool Context Management in 2025."
7. SSOJet. "10 Custom Instruction Templates for Claude Code." June 2026.
8. byteiota. "Context Engineering: The AI Coding Skill That Matters." 2026.
9. Wikantik Wiki. "Context Engineering for Coding Agents." 2026.
10. forcewake. "Managing AI Agents and Code Context in 2026." May 2026.
11. BeeX. "AIエージェント時代の開発手法: AI駆動開発の考え方と実践ポイント." 2026.
12. LatentView. "AI Coding Assistants in Software Development: A Practical Guide." 2025.
