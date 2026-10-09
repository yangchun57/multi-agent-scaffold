# 星枢（starxhub）

**为 Claude Code 打造的多 Agent 开发团队配置中心**

一句话搞定 24 个专职 Agent、10 个斜杠命令、护栏 hooks 和路径范围 rules——从零搭建新项目，或让已有项目接入多 Agent 工作流。

## 为什么选择星枢

每个项目的技术栈、业务规则、多租户约束都不同，不存在"通用模板"能直接套用。星枢的价值在于：根据你的技术栈，生成**完全适配该项目**的起点，而不是安装一个"看起来能用但处处不匹配"的配置。

## 两个 Skill，覆盖项目全生命周期

| Skill | 用途 | 适用场景 |
|-------|------|----------|
| **new-project** | 新建项目脚手架 | 从零开始，一键生成完整多 Agent 团队配置 |
| **onboard-project** | 接入已有项目 | 自动探测技术栈，纳入多 Agent 工作流 |

### new-project：从零搭建

```bash
/new-project /path/to/project --name "项目名称" --backend python --frontend vue
```

生成的项目包含：

- **24 个专职 Agent**（五阶段：需求分析 / 任务规划 / 需求评审 / 开发实施 / 测试修复）
  - 8 个需求评审专家（`req-*`），形成完整评审团队
  - 方案门禁 duo：`plan-risk-analyst`（失效点扫描）+ `plan-gatekeeper`（放行判定）
  - 测试修复 duo：`functional-tester`（用例设计）+ `bug-fixer`（五步闭环修复）
  - HTML 原型设计师：`html-prototyper`（将设计方案转化为可交互原型）
- **11 个斜杠命令**：覆盖从模糊想法到上线复盘的完整生命周期
- **护栏 hooks**：提交前跑构建+测试，写实体后做多租户红线扫描
- **路径范围 rules**：按技术栈自动加载规范，编辑匹配文件时自动注入上下文

### onboard-project：接入已有项目

```bash
/onboard-project /path/to/existing-project
```

自动探测技术栈、重组目录结构、生成 `.claude/` 配置和 `CLAUDE.md`。支持未知技术栈的骨架 rules 生成。

## 技术栈支持

| 维度 | 选项 | 说明 |
|------|------|------|
| 后端 | `dotnet` | .NET 8 + ASP.NET Core Web API + SqlSugar + MySQL |
| 后端 | `python` | Python 3.10+ + FastAPI + SQLAlchemy 2.0 + Pydantic v2 |
| 前端 | `vue` | Vue 3 + Element Plus + Pinia + Vite + TypeScript |
| 前端 | `uniapp` | uni-app + Vue 3 + Pinia + TypeScript（H5 + 微信小程序） |

未指定技术栈时，脚手架会**交互式询问**，绝不静默默认。

## 快速开始

### 安装

```bash
# 添加插件市场
claude plugin marketplace add yangchun57/starxhub

# 安装插件
claude plugin install starxhub@starxhub
```

### 使用

在 Claude Code 中调用 skill：

```bash
# 新建项目
/new-project /path/to/project --name "电商系统" --backend dotnet --frontend vue

# 接入已有项目
/onboard-project /path/to/existing-project
```

或直接运行脚本：

```bash
cd /path/to/plugin/skills/new-project/scripts
python scaffold.py /path/to/project --name "电商系统" --backend dotnet --frontend vue
```

## 核心机制

### 方案放行门禁

`/new-feature` 在架构方案完成后、进入编码前，强制经过一道门禁：

```
architect 交卷 → plan-risk-analyst 扫描（R1~R7 失效点）→ plan-gatekeeper 判定
              ├─ PASS           → 继续编码
              ├─ CONDITIONAL    → 逐条确认放行条件后继续
              └─ REJECT         → 退回修订
```

多租户红线阻塞项**一票否决**。`/plan-gate` 也可独立使用。

### 路径范围 rules

生成的项目包含 `.claude/rules/` 目录，按技术栈自动加载规范：

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

每个 rule 文件 < 50 行精华规则，通过 `paths` glob 匹配自动触发。完整规范保留在 `.claude/standards/` 供深层阅读。

## 目录结构

```
starxhub/                              # 仓库根 = 插件市场
├── .claude-plugin/marketplace.json   # 市场清单
└── plugins/starxhub/                 # 插件本体（星枢）
    ├── .claude-plugin/plugin.json     # 插件清单
    └── skills/
        ├── new-project/              # 新建项目脚手架
        │   ├── SKILL.md
        │   ├── scripts/
        │   │   ├── scaffold.py        # 主生成器
        │   │   └── split-standards.py # 规范拆分工具
        │   └── templates/
        │       ├── CLAUDE.md          # 项目记忆模板
        │       ├── .claude/
        │       │   ├── agents/        # 24 个 Agent 定义
        │       │   ├── commands/      # 10 个斜杠命令
        │       │   ├── hooks/         # 护栏钩子脚本
        │       │   ├── rules/         # 路径范围规则
        │       │   ├── standards/     # 完整规范文档
        │       │   └── settings.json  # 权限配置
        │       ├── code/              # 代码工程模板
        │       └── docs/              # 项目文档模板
        └── onboard-project/          # 接入已有项目
            ├── SKILL.md
            └── scripts/
                └── detect_stack.py    # 技术栈探测脚本
```

## 注意事项

- **占位符渲染**：模板中的 `{{BACKEND_STACK}}`、`{{ENVELOPE}}` 等占位符由 `scaffold.py` 按技术栈渲染
- **权限黑名单**：拒绝 `git push`、删除命令、`drop table` 等，由生成器写入项目级 `settings.json`
- **Agent 定义业务无关**：项目红线请写在各项目自己的 `CLAUDE.md` 中
- **hook 脚本**：用 `$CLAUDE_PROJECT_DIR` 定位目标工程

## 更新日志

### v2.1.0 — 品牌升级：starxhub（星枢）

- 插件重命名：`multi-agent-scaffold` → `starxhub`（星枢）
- Skill 重命名：
  - `claude-code-multi-agent-scaffold` → `new-project`
  - `claude-code-project-onboard` → `onboard-project`
- 新增 `onboard-project` skill：已有项目可自动探测技术栈并纳入多 Agent 工作流

### v2.0.0 — 精简架构 + 路径范围 rules

- 新增 `.claude/rules/` 路径范围规则，按技术栈生成 13 个 rules 文件
- 移除原生 agents/commands/hooks，仅保留脚手架生成器 skill

### v1.4.0 — 方案放行门禁

- 新增 `plan-risk-analyst` + `plan-gatekeeper` 方案门禁 duo
- 新增 `/plan-gate` 命令，可独立用于存量项目补门禁

## 许可

MIT License
