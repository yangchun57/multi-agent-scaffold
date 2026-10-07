---
trigger: always
---

# Git 提交规范

## 分支模型
- **主分支**：`main`（始终可构建，禁止直接推送）
- **功能分支**：`feat/{功能名}`（从 main 切出，合并后删除）
- **修复分支**：`fix/{问题描述}`（从 main 切出，合并后删除）
- **发布分支**：`release/{版本号}`（可选，用于发布前冻结）

## 提交信息格式
使用 Conventional Commits 规范：

```
<type>(<scope>): <subject>

<body>

<footer>
```

### Type 类型
- `feat`: 新功能
- `fix`: 修复 bug
- `docs`: 文档变更
- `style`: 代码格式（不影响逻辑）
- `refactor`: 重构（非新功能、非修复）
- `test`: 测试相关
- `chore`: 构建/工具/依赖

### Scope（可选）
- 模块名：`auth`, `user`, `order`, `api`, `web`
- 影响范围：`backend`, `frontend`, `database`

### Subject
- 中文简述，不超过 50 字
- 使用祈使句（"添加用户登录功能"，非"添加了..."）

### Body（可选）
- 详细说明变更内容、原因、影响
- 每行不超过 72 字

### Footer（可选）
- 关联 Issue：`Closes #123`
- 破坏性变更：`BREAKING CHANGE: ...`

## 提交粒度
- 一个逻辑变更 = 一个 commit
- 禁止混合多个不相关变更
- 重构和功能变更分开提交

## 质量门禁
- 提交前必须通过：`bash scripts/ci.sh`
- 禁止使用 `--no-verify` 绕过检查
- 测试失败禁止提交

## 详细规范
@.claude/standards/通用开发规范.md#Git规范
