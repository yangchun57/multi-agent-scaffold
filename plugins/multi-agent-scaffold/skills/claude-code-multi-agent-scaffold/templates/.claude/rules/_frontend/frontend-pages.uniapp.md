---
paths:
  - "src/pages/**/*.vue"
---

# 前端页面规范（uni-app + Vue 3）

## 技术栈
- uni-app + Vue 3 Composition API + TypeScript + Pinia
- 目标平台: H5 + 微信小程序

## 铁律
- 页面必须使用 `<script setup lang="ts">`，禁止 Options API
- 所有页面必须在 `pages.json` 中注册，禁止硬编码路径
- TabBar 页用 `uni.switchTab()`，非 TabBar 页用 `uni.navigateTo()`
- 禁止页面内直接写 `uni.request`，必须走 `api/` 层统一封装

## 路由配置
- 集中配置于 `pages.json`
- 新增页面三步: 创建 `.vue` → 注册 `pages.json` → 添加导航入口
- 导航栏标题: `"navigationBarTitleText"` 在 pages.json 中配置

## 目录结构
```
src/
├── api/          # 请求封装 + 接口定义（类型与函数同文件）
├── pages/        # 页面（按业务域分目录）
├── stores/       # Pinia 状态（setup 函数风格）
├── utils/        # 纯工具函数（禁止引入 store）
├── components/   # 跨页共享组件
├── pages.json    # 路由配置
└── manifest.json # 应用配置
```

## 依赖方向
`pages → stores → api → utils`（严格单向，禁止反向）

## 详细规范
@.claude/standards/topics/uni-app开发规范_v1.0/02-第-1-章-工程结构与分层.md
@.claude/standards/topics/uni-app开发规范_v1.0/03-第-2-章-页面与路由.md
