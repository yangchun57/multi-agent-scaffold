---
paths:
  - "src/views/**/*.vue"
  - "src/pages/**/*.vue"
---

# 前端页面规范（Vue 3 + Element Plus）

## 技术栈
- Vue 3 Composition API + `<script setup lang="ts">`
- Element Plus + Pinia + Vue Router + Axios + Vite + TypeScript

## 铁律
- 页面组件必须使用 `<script setup lang="ts">`，禁止 Options API
- 模板顺序: `<template>` → `<script setup>` → `<style scoped>`
- 所有页面必须懒加载: `component: () => import('@/views/...')`
- 样式必须使用 `scoped`，禁止全局污染

## 目录结构
- 页面: `src/views/{module}/` 按业务模块划分
- 布局: `src/layouts/DefaultLayout.vue`
- 公共组件: `src/components/` PascalCase 命名

## 命名
- 页面文件: PascalCase（`MeterList.vue`, `FamilyBillingList.vue`）
- 路由名: PascalCase（`MeterList`, `Dashboard`）
- meta 字段: `{ title, icon?, roles?, hidden?, requiresAuth? }`

## 样式
- 全局重置: `body { margin: 0; }` 必须在全局样式中
- 类名: kebab-case（`.card-header`, `.search-form`）
- 选择器宽度统一: 160px / 日期 150px / 输入框 180px

## 详细规范
@.claude/standards/topics/前端开发规范/01-一、项目结构规范.md
@.claude/standards/topics/前端开发规范/05-五、样式规范.md
@.claude/standards/topics/前端开发规范/06-六、路由规范.md
