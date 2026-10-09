---
name: onboard-project
description: 接入已有项目到多 Agent 工作流。自动探测技术栈、重组目录结构（代码→src/、文档→docs/）、生成 .claude/ 配置和 CLAUDE.md。支持未知技术栈的骨架 rules 生成。当用户想让现有项目使用多 Agent 协作模式时使用。
---

# 项目接入（Onboard）— 星枢 starxhub

## 目的

将已有项目纳入 multi-agent 工作流，生成标准化的 `.claude/` 配置、`CLAUDE.md`、`docs/` 文档结构。

**核心约束**：
- 只增不删（除非用户明确确认目录重组）
- 每步 git commit，方便回滚
- 不触碰业务代码逻辑

## 三阶段流程

### Phase 1: 探测（只读）

运行探测脚本，获取项目结构分析：

```bash
python scripts/detect_stack.py <project-root>
```

输出 JSON 包含：
- `stack`: 技术栈识别（语言/框架/ORM/数据库）
- `code_locations`: 代码目录位置（是否在标准位置）
- `doc_locations`: 文档文件扫描与分类
- `references_to_update`: 需更新的引用（旧路径）
- `stack_match`: 匹配度评估（Level 1/2/3）

### Phase 2: 生成重组提案（只读 + 确认）

基于探测结果，生成人类可读的重组提案：

```markdown
=== 项目探测结果 ===
语言: Python 3.12
框架: FastAPI 0.115
ORM: SQLAlchemy 2.0
前端: Vue 3 + Element Plus
分层: api/services/models（三层）
测试: pytest
多租户: 是（检测到 tenant_id 全局过滤器）

=== 将生成的配置 ===
rules:
  - backend-api.md   (paths: app/routers/**/*.py)
  - backend-domain.md (paths: app/services/**/*.py)
  - backend-infra.md  (paths: app/models/**/*.py)
  - frontend-pages.md (paths: src/views/**/*.vue)
  - frontend-state.md (paths: src/stores/**/*.ts, src/api/**/*.ts)
  - workflow.md, database.md, git.md

agents: 23 个（全量）
commands: 10 个（全量）
hooks: pre_commit_guard（pytest）+ tenant_guard

=== 不触碰的文件 ===
所有业务代码、配置文件、git 历史保持不变
```

**关键**：向用户确认提案后再执行。

### Phase 3: 执行（写入）

按以下顺序执行，每步 git commit：

#### Step 1: 文档迁移（低风险）

```bash
# 创建目标目录
mkdir -p docs/01-技术规范 docs/02-用户文档

# 迁移文档
mv docs/architecture.md docs/01-技术规范/ 2>/dev/null || true
mv wiki/user-guide.md docs/02-用户文档/ 2>/dev/null || true

# 提交
git add docs/
git commit -m "docs: 重组文档目录结构"
```

#### Step 2: 代码迁移（需更新引用）

**如果代码已在标准位置**（`src/backend/api`、`src/web`），跳过此步。

**如果需要迁移**：

```bash
# 1. 先更新所有引用文件的内容
# 例如：.github/workflows/ci.yml 中的 cd frontend → cd src/web

# 2. 再移动目录
mv frontend/ src/web/

# 3. 提交
git add -A
git commit -m "refactor: 迁移前端代码到 src/web/"
```

#### Step 3: 生成 .claude/ + CLAUDE.md

根据匹配度生成不同级别的 rules：

**Level 1（完全匹配）**：使用预定义 rules 模板

**Level 2（部分匹配）**：生成骨架 rules + 待补充清单

**Level 3（不匹配）**：只生成通用 rules（workflow/database/git）

```bash
# 复制 agents/commands/hooks
cp -r templates/.claude/agents .claude/
cp -r templates/.claude/commands .claude/
cp -r templates/.claude/hooks .claude/

# 生成 rules（按匹配度）
# ...（由 Claude Code 根据探测结果动态生成）

# 生成 CLAUDE.md（从代码推断预填）
# ...（由 Claude Code 根据探测结果动态生成）

# 提交
git add .claude/ CLAUDE.md
git commit -m "chore: 添加 multi-agent 配置"
```

## 匹配度策略

### Level 1: 完全匹配

技术栈在预定义范围内（dotnet/python × vue/uniapp）：
- 使用预定义 rules 模板
- 开箱即用

### Level 2: 部分匹配

能识别分层模式，但技术栈不在预定义内（如 Go + Gin）：
- 生成"骨架 rules"：paths 正确，但技术细节留空
- 留 `待补充` 清单，让 LLM 或用户后续填充

示例骨架 rule：

```markdown
---
paths:
  - "handlers/**/*.go"
---

# 后端 API 层规范（Go + Gin）

## 技术栈
- Go 1.21 + Gin + GORM
- 统一返回: `Response{Code, Message, Data}`

## 铁律
- 所有 handler 必须有参数校验（binding tag）
- 禁止 handler 内含业务逻辑，一律委托 service 层

## 待补充（请根据实际代码填充）
- [ ] 响应格式的具体结构
- [ ] 错误处理的标准方式
- [ ] 认证/授权的具体实现
```

### Level 3: 不匹配

项目结构完全不标准（无明确分层）：
- 只生成通用 rules（workflow/database/git）
- 提示用户手动创建技术栈相关的 rules

## CLAUDE.md 预填策略

对于已有项目，CLAUDE.md 不应是 TODO 占位符，而应从代码推断预填：

```markdown
# CLAUDE.md — {项目名}

## 项目速览
{从 README.md 或代码推断}

## 技术栈
- 后端: {探测结果}
- 前端: {探测结果}
- 数据库: {探测结果}

## 最高优先级约束
{从代码中的多租户过滤器、认证中间件等推断}

## 常用命令
- 构建: {从 package.json / Makefile 推断}
- 测试: {从 pytest.ini / package.json 推断}
- 启动: {从 main.py / app.py 推断}
```

## 关键约束

1. **每步 git commit**：文档迁移一个 commit，代码迁移一个 commit，配置生成一个 commit
2. **引用修复先于移动**：先更新所有引用文件的内容，再移动目录
3. **根目录 README.md 保留**：不动，但可以添加指向 `docs/` 的链接
4. **已有 .gitignore 合并**：不覆盖，追加新规则
5. **已有 CI 更新而非替换**：在现有 workflow 基础上修改路径，不重建

## 使用示例

```
用户: 帮我把这个项目纳入 multi-agent 工作流

Claude Code:
1. 运行 detect_stack.py 探测项目结构
2. 生成重组提案，向用户确认
3. 按确认后的方案执行迁移
4. 生成 .claude/ + CLAUDE.md
5. 提示用户填写 CLAUDE.md 中的业务 TODO
```

## 与脚手架生成器的区别

| 维度 | 脚手架生成器 | 项目接管器（本 skill） |
|------|------------|-------------------|
| 输入 | 用户选择技术栈 | 自动探测技术栈 |
| CLAUDE.md | 含 TODO 占位符 | 从代码推断预填 |
| rules paths | 按约定路径 | 按实际目录结构 |
| 代码工程 | dotnet new / create-vite | **不生成，只分析** |
| docs/ | 空模板 | 从代码推断初始内容 |
| git | git init + 初始提交 | **不动 git 历史** |
