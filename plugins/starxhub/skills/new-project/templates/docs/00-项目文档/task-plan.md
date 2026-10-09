# 任务计划

> 由 pm Agent 维护。

## 当前任务计划：暂无

## 任务计划模板

| 任务ID | 任务 | 负责Agent | 前置依赖 | 验收标准 | 优先级 |
|--------|------|-----------|----------|----------|--------|
| T1 | 数据库设计 | db-engineer | - | 建表SQL符合 CLAUDE.md 约束 | P0 |
| T2 | 接口契约 | architect | - | 更新 api-contracts.md | P0 |
| T3 | 后端实现 | backend-dev | T1,T2 | 接口可用+单测通过 | P0 |
| T4 | 前端实现 | frontend-dev | T2 | 页面可用 | P0 |
| T5 | 单元测试 | tester | T3 | 测试通过 | P0 |
| T6 | 代码审查 | reviewer | T3,T4 | 审查无红线问题 | P0 |
