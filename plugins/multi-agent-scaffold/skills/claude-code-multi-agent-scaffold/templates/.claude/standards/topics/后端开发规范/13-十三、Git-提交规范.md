# 后端开发规范 · 十三、Git 提交规范

> 拆分自《后端开发规范》第 13 节。需要全量上下文时读原文件。


### 13.1 提交信息格式

```
<type>(<scope>): <subject>

<body>

<footer>
```

### 13.2 Type 类型

| 类型 | 说明 | 示例 |
|------|------|------|
| feat | 新功能 | feat(service): 新增分摊计算服务 |
| fix | 修复 Bug | fix(controller): 修复费用计算接口参数校验 |
| docs | 文档更新 | docs: 更新后端开发规范 |
| style | 代码格式 | style: 统一代码缩进 |
| refactor | 重构 | refactor(service): 重构费用计算逻辑 |
| perf | 性能优化 | perf(query): 优化仪表查询性能 |
| test | 测试 | test(service): 添加部门服务单元测试 |
| chore | 构建/工具 | chore: 更新 NuGet 包版本 |

### 13.3 提交示例

```
feat(billing): 新增费用计算功能

- 新增 IBillingService 接口
- 实现 BillingService 费用计算逻辑
- 支持分摊比例计算
- 新增费用计算 API 接口

Closes #45
```

---

