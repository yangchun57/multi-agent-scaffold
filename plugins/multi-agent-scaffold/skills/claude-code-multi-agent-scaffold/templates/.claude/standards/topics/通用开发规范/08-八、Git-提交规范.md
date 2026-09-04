# 通用开发规范 · 八、Git 提交规范

> 拆分自《通用开发规范》第 8 节。需要全量上下文时读原文件。


### 8.1 提交信息格式

```
<type>(<scope>): <subject>

<body>

<footer>
```

### 8.2 Type 类型

| 类型 | 说明 | 示例 |
|------|------|------|
| feat | 新功能 | feat(service): 新增分摊计算服务 |
| fix | 修复 Bug | fix(controller): 修复费用计算接口参数校验 |
| docs | 文档更新 | docs: 更新开发规范 |
| style | 代码格式 | style: 统一代码缩进 |
| refactor | 重构 | refactor(service): 重构费用计算逻辑 |
| perf | 性能优化 | perf(query): 优化仪表查询性能 |
| test | 测试 | test(service): 添加单元测试 |
| chore | 构建/工具 | chore: 更新 NuGet 包版本 |

### 8.3 示例

```
feat(billing): 新增费用计算功能

- 新增 IBillingService 接口
- 实现 BillingService 费用计算逻辑
- 支持分摊比例计算
- 新增费用计算 API 接口

Closes #45
```

---

