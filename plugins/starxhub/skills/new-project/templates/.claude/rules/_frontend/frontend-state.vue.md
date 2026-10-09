---
paths:
  - "src/stores/**/*.ts"
  - "src/api/**/*.ts"
---

# 前端状态与 API 层规范（Vue 3 + Element Plus）

## 状态管理（Pinia）
- 使用 `defineStore('name', () => { ... })` setup 函数风格
- Token/用户信息存储于 `stores/user.ts`
- 禁止在 `utils/` 或 `api/` 中直接读写 store（循环依赖）
- Store 异步操作返回 Promise，页面通过 `await` 消费

## API 层
- 统一请求封装: `src/api/request.ts`（Axios 实例 + 拦截器）
- 按模块划分 API 文件: `src/api/{module}.ts`
- 类型定义与 API 函数放在同一文件，禁止单独抽 `types/` 目录

## 类型生成
- 业务实体 TS 类型优先从后端 Swagger 自动生成: `npm run gen:api`
- 生成物为唯一事实源，手写仅限 Form/Query 等前端形态

## 命名
- Store 文件: camelCase（`user.ts`, `order.ts`）
- API 文件: kebab-case（`family-base.ts`, `family-meter.ts`）
- 类型文件: kebab-case.d.ts（`family.d.ts`, `api.d.ts`）

## 详细规范
@.claude/standards/topics/前端开发规范/07-七、Mock-数据规范.md
@.claude/standards/topics/前端开发规范/08-八、错误处理规范.md
