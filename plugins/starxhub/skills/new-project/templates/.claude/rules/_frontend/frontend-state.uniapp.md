---
paths:
  - "src/stores/**/*.ts"
  - "src/api/**/*.ts"
---

# 前端状态与 API 层规范（uni-app + Vue 3）

## 状态管理（Pinia）
- 使用 `defineStore('name', () => { ... })` setup 函数风格，禁止 Options 风格
- Token/用户信息存储于 `stores/user.ts`，通过 `uni.setStorageSync` 持久化
- 禁止在 `utils/` 或 `api/` 中直接读写 store（循环依赖）
- Store 中禁止直接操作 DOM 或调用 `uni.navigateTo`（状态层不应有副作用导航）

## API 层
- 统一请求封装: `src/api/request.ts`（uni.request 封装 + 拦截器）
- 按模块划分 API 文件: `src/api/{domain}.ts`
- 类型定义与 API 函数放在同一文件，禁止单独抽 `types/` 目录
- 禁止页面内直接写 `uni.request`，必须走 `api/` 层

## 持久化
- Token: `uni.setStorageSync('access_token', ...)`
- 用户信息: `uni.setStorageSync('user_info', JSON.stringify(...))`
- 租户 ID: `uni.setStorageSync('tenant_id', ...)`
- 登出时: `uni.removeStorageSync(...)` 清除所有持久化数据

## 命名
- Store 文件: camelCase（`user.ts`, `order.ts`）
- API 文件: camelCase（`auth.ts`, `familyBase.ts`）

## 详细规范
@.claude/standards/topics/uni-app开发规范_v1.0/05-第-4-章-状态管理.md
@.claude/standards/topics/uni-app开发规范_v1.0/04-第-3-章-网络层与请求封装.md
