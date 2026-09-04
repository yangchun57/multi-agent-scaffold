# 前端开发规范 · 十、Git 提交规范

> 拆分自《前端开发规范》第 10 节。需要全量上下文时读原文件。


### 10.1 提交信息格式

```
<type>(<scope>): <subject>

<body>

<footer>
```

### 10.2 Type 类型

| 类型 | 说明 | 示例 |
|------|------|------|
| feat | 新功能 | feat(family): 新增小区管理功能 |
| fix | 修复 Bug | fix(meter): 修复仪表状态显示错误 |
| docs | 文档更新 | docs: 更新开发规范 |
| style | 代码格式 | style: 统一缩进格式 |
| refactor | 重构 | refactor(api): 重构 API 调用方式 |
| perf | 性能优化 | perf(list): 优化列表渲染性能 |
| test | 测试 | test: 添加单元测试 |
| chore | 构建/工具 | chore: 更新构建配置 |

### 10.3 示例

```
feat(family): 新增小区管理功能

- 新增 CommunitySelector 组件
- 新增小区管理页面 CampusManage.vue
- 更新数据库设计，新增 res_community 表
- 更新相关类型定义和 API 接口

Closes #123
```

---

