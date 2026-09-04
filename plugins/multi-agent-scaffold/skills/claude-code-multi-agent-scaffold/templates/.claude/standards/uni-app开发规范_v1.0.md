# uni-app 移动端开发规范

> **版本**：V1.0 ｜ **日期**：2026-08-19 ｜ **状态**：基线 ｜ **适用**：uni-app（Vue 3 + TypeScript）跨端应用（H5 + 微信小程序）

---

## 目录

- [第 0 章 总则](#第-0-章-总则)
- [第 1 章 工程结构与分层](#第-1-章-工程结构与分层)
- [第 2 章 页面与路由](#第-2-章-页面与路由)
- [第 3 章 网络层与请求封装](#第-3-章-网络层与请求封装)
- [第 4 章 状态管理](#第-4-章-状态管理)
- [第 5 章 环境判断与条件编译](#第-5-章-环境判断与条件编译)
- [第 6 章 URL 参数传递](#第-6-章-url-参数传递)
- [第 7 章 认证与授权流程](#第-7-章-认证与授权流程)
- [第 8 章 开发环境配置](#第-8-章-开发环境配置)
- [第 9 章 样式与 UI 约定](#第-9-章-样式与-ui-约定)
- [第 10 章 错误处理与用户体验](#第-10-章-错误处理与用户体验)
- [第 11 章 附录](#第-11-章-附录)

---

## 第 0 章 总则

### 原则

本规范为 uni-app（Vue 3 + TypeScript）跨端应用提供统一技术约定。覆盖 H5 与微信小程序双端。目的有三：统一团队技术决策、传承工程经验、为 AI 编码助手提供代码生成约束。

### 适用范围

- 技术栈：uni-app + Vue 3（Composition API）+ TypeScript + Pinia
- 目标平台：H5（含微信浏览器）、微信小程序
- 不适用于：原生小程序（wxml/wxss）、Flutter、React Native

### 规范分级

| 级别 | 含义 | 违反后果 |
|------|------|----------|
| `MUST` | 强制规则 | PR 阻断 |
| `MUST NOT` | 明确反模式 | PR 阻断 |
| `SHOULD` | 强烈建议 | 偏离须在 PR 说明理由 |
| `MAY` | 可选优化 | 无强制要求 |

### 术语

- **条件编译**：uni-app 通过 `// #ifdef PLATFORM` 注释实现平台差异化代码，编译时剔除未命中分支。
- **hash 模式**：H5 路由模式，URL 形如 `/#/pages/xxx?param=value`，query 在 `#` 之后。
- **needAuth**：请求封装中标识接口是否需要 token 的参数。

---

## 第 1 章 工程结构与分层

### 原则

按职责分层，依赖单向流动。`api` 层封装网络请求，`stores` 层管理全局状态，`pages` 层组织页面，`utils` 层放纯工具函数。

### 抽象规则

- 顶层目录 `MUST` 划分为：`api/`（请求封装与接口定义）、`pages/`（按业务域组织页面）、`stores/`（Pinia 状态）、`utils/`（纯工具函数）、`components/`（跨页共享组件）。
- 依赖方向 `MUST` 为：`pages -> stores -> api -> utils`。
- `MUST NOT` 反向依赖（如 `api -> stores`、`utils -> api`）。
- 页面文件 `MUST` 使用 `.vue` 后缀，API/Store/Utils 文件 `MUST` 使用 `.ts` 后缀。
- 接口类型定义 `MUST` 与 API 函数放在同一文件（`api/xxx.ts`），`MUST NOT` 单独抽 `types/` 目录（减少文件跳转）。

### 目录结构示例

```
src/
├── api/                  # 请求封装与接口定义
│   ├── request.ts        # 统一请求封装
│   ├── auth.ts           # 认证接口 + 类型
│   └── [domain].ts       # 业务接口
├── pages/                # 页面（按业务域分目录）
│   ├── auth/             # 认证相关页面
│   ├── home/             # 首页
│   └── [domain]/         # 业务域页面
├── stores/               # Pinia 状态管理
├── utils/                # 纯工具函数
├── components/           # 跨页共享组件
├── pages.json            # 路由配置
├── manifest.json         # 应用配置
└── main.ts               # 入口
```

### 反模式

- 页面内直接写 `uni.request` -- 绕过统一拦截，无法统一处理 token/错误
- 工具函数引入 store -- 循环依赖、难测试
- 类型定义单独目录 -- 与 API 函数分离，增加文件跳转成本

---

## 第 2 章 页面与路由

### 原则

路由集中配置于 `pages.json`，导航使用 uni-app 内置 API，页面结构遵循 Vue 3 `<script setup>` 范式。

### 抽象规则

- 所有页面 `MUST` 在 `pages.json` 中注册，`MUST NOT` 硬编码路径字符串。
- TabBar 页 `MUST` 使用 `uni.switchTab()`，非 TabBar 页 `MUST` 使用 `uni.navigateTo()` 或 `uni.redirectTo()`。
- 页面组件 `MUST` 使用 `<script setup lang="ts">`，`MUST NOT` 使用 Options API。
- 页面模板顺序 `MUST` 为：`<template>` → `<script setup>` → `<style scoped>`。
- 新增页面 `MUST` 三步：创建 `.vue` 文件 → 注册到 `pages.json` → 在合适位置添加导航入口。

### 路由配置示例

```json
// pages.json
{
  "pages": [
    { "path": "pages/home/index", "style": { "navigationBarTitleText": "首页" } },
    { "path": "pages/auth/login", "style": { "navigationBarTitleText": "登录" } }
  ],
  "tabBar": {
    "list": [
      { "pagePath": "pages/home/index", "text": "首页" },
      { "pagePath": "pages/my/profile", "text": "我的" }
    ]
  }
}
```

### 反模式

- `uni.navigateTo({ url: '/pages/xxx' })` 路径硬编码散落各处 -- 改路径需全文搜索
- TabBar 页使用 `uni.navigateTo()` -- 不会切换 Tab，只会压栈
- 页面中使用 `ref` 命名与 DOM id 冲突 -- 运行时行为不确定

---

## 第 3 章 网络层与请求封装

### 原则

所有接口请求经由统一封装（`api/request.ts`），自动处理 token 注入、错误拦截、登录过期跳转。业务页面不直接调用 `uni.request`。

### 抽象规则

- 业务代码 `MUST` 通过 `get<T>()` / `post<T>()` / `put<T>()` / `del<T>()` 发起请求，`MUST NOT` 直接调用 `uni.request`。
- `post<T>()` `MUST` 支持 `options: { needAuth?: boolean }` 参数，默认为 `true`。
- **不需要认证的接口（登录、注册、OAuth 回调、验证码等）`MUST` 显式传 `{ needAuth: false }`。** 不传则拦截器在无 token 时直接跳转登录页，请求永远发不出去。
- `request<T>()` 返回 `Promise<T>`（已解包 `ApiResult.data`），调用方 `MUST NOT` 再访问 `res.code` / `res.data`。
- 错误提示 `MUST` 在拦截器统一处理（`uni.showToast`），页面 catch 块 `MUST NOT` 重复弹 toast（避免双重提示）。
- 接口类型 `MUST` 在 `api/xxx.ts` 中定义，与接口函数同文件。

### 请求封装核心结构

```typescript
// api/request.ts
async function request<T>(options: RequestOptions): Promise<T> {
  const { needAuth = true } = options
  const token = uni.getStorageSync('access_token')

  // 关键：needAuth=true 且无 token 时直接跳转，不发请求
  if (needAuth && !token) {
    redirectToLogin()
    throw new Error('未登录')
  }

  // ...uni.request 封装...
  // 成功：resolve(body.data) -- 直接返回 data，不返回完整 ApiResult
}

// 公开方法签名
export function post<T>(url: string, data?: unknown, options?: { needAuth?: boolean }) {
  return request<T>({ url, method: 'POST', data, needAuth: options?.needAuth })
}
```

### 接口调用示例

```typescript
// api/auth.ts
import { post } from './request'

// 正确：登录接口不需要 token，显式传 needAuth: false
export function usernameLogin(username: string, password: string, tenantCode: string) {
  return post<LoginResponse>('/auth/login', { username, password, tenantCode }, { needAuth: false })
}

// 正确：需要 token 的接口，默认 needAuth=true 无需显式传
export function getBookings() {
  return post<BookingList>('/booking/list')
}
```

### 页面调用示例

```typescript
// pages/xxx/index.vue
async function loadData() {
  try {
    const data = await getBookings()  // data 已是 BookingList 类型，非 ApiResult
    bookings.value = data.items
  } catch {
    // 错误已由拦截器 toast，此处无需重复提示
  }
}
```

### 反模式

- 页面直接调 `uni.request` -- 绕过 token 注入和错误拦截
- 登录接口不传 `needAuth: false` -- 拦截器在无 token 时直接跳转，API 请求永远发不出
- catch 块中重复 `uni.showToast` -- 与拦截器双重提示，用户体验差
- 调用方访问 `res.code` / `res.data` -- `request<T>` 已解包，res 就是 `T`

---

## 第 4 章 状态管理

### 原则

使用 Pinia（Composition API 风格）管理全局状态。页面局部状态用 `ref`，跨页面/需持久化的状态用 store。

### 抽象规则

- Store `MUST` 使用 `defineStore('name', () => { ... })` setup 函数风格，`MUST NOT` 使用 Options 风格。
- Token 和用户信息 `MUST` 存储于 `stores/user.ts`，通过 `uni.setStorageSync` 持久化。
- `MUST NOT` 在 `utils/` 或 `api/` 中直接读写 store（循环依赖）。
- Store 中的异步操作 `MUST` 返回 Promise，页面通过 `await` 消费。

### Store 示例

```typescript
// stores/user.ts
import { defineStore } from 'pinia'
import { ref } from 'vue'
import type { LoginResponse } from '../api/auth'
import { usernameLogin as usernameLoginApi } from '../api/auth'

export const useUserStore = defineStore('user', () => {
  const token = ref<string>('')
  const userInfo = ref<UserInfo | null>(null)

  async function usernameLogin(username: string, password: string, tenantCode: string) {
    const res = await usernameLoginApi(username, password, tenantCode)
    setLoginResult(res)
    return res
  }

  function setLoginResult(result: LoginResponse) {
    token.value = result.accessToken
    userInfo.value = result.user
    uni.setStorageSync('access_token', result.accessToken)
    uni.setStorageSync('refresh_token', result.refreshToken)
    uni.setStorageSync('user_info', JSON.stringify(result.user))
    uni.setStorageSync('tenant_id', result.user.tenantId)
  }

  function logout() {
    token.value = ''
    userInfo.value = null
    uni.removeStorageSync('access_token')
    uni.removeStorageSync('refresh_token')
    uni.removeStorageSync('user_info')
  }

  function isLoggedIn() {
    return !!token.value && !!userInfo.value
  }

  return { token, userInfo, usernameLogin, setLoginResult, logout, isLoggedIn }
})
```

### 反模式

- `utils/` 中引入 store -- 循环依赖，`utils` 被 `api` 引用时导致 store 初始化顺序不确定
- Store 中直接操作 DOM 或调用 `uni.navigateTo` -- 状态层不应有副作用导航
- 多个 store 相互引用 -- 难以预测初始化顺序，应通过页面层协调

---

## 第 5 章 环境判断与条件编译

### 原则

uni-app 通过条件编译（`// #ifdef`）实现平台差异化。条件编译仅用于**顶层声明和整个函数体**，`MUST NOT` 用于函数内部逻辑分支（编译时不会剔除，运行时仍会执行）。

### 抽象规则

- 条件编译 `MUST` 使用 `// #ifdef PLATFORM` / `// #endif` 语法，`MUST NOT` 使用运行时 `if (process.env.UNI_PLATFORM)` 判断平台。
- **`<script setup>` 函数体内的逻辑 `MUST NOT` 使用条件编译。** 原因：条件编译在 `<script setup>` 函数体内失效（不剔除代码，分支仍执行）。应改用运行时判断函数。
- H5 环境判断 `MUST` 用 `typeof location !== 'undefined'`（运行时），`MUST NOT` 用 `// #ifdef H5` 在 setup 函数体内。
- 微信浏览器判断 `SHOULD` 抽取为独立工具函数（如 `utils/wechat.ts` 的 `isWechatBrowser()`），不在页面内重复写 UA 检测。

### 条件编译正确用法

```typescript
// ✅ 正确：顶层声明可用条件编译
// #ifdef MP-WEIXIN
import wx from 'weixin-js-sdk'
// #endif

// ✅ 正确：整个方法体可用条件编译（方法作为顶层声明）
// #ifdef H5
function initWechatJSSDK() {
  // 微信 JSSDK 初始化
}
// #endif
```

### 条件编译错误用法

```typescript
// ❌ 错误：函数体内条件编译不剔除，运行时仍执行
function parseUrlTenant(): string {
  // #ifdef H5    <-- 在 setup 函数体内，条件编译失效！
  const match = location.href.match(/[?&]tenant=([^&]+)/)
  return match ? match[1] : ''
  // #endif
  return ''  // 小程序端也会走到这里，但 location 不存在会报错
}

// ✅ 正确：函数体内用运行时判断
function parseUrlTenant(): string {
  if (typeof location === 'undefined') return ''  // 运行时判断
  const match = location.href.match(/[?&]tenant=([^&]+)/)
  return match ? decodeURIComponent(match[1]) : ''
}
```

### 反模式

- `<script setup>` 函数体内使用 `// #ifdef` -- 不剔除，双端都执行，小程序端报 `location is not defined`
- 页面内重复写 `navigator.userAgent.includes('MicroMessenger')` -- 应抽取为 `isWechatBrowser()` 工具函数
- 用 `process.env.UNI_PLATFORM` 判断平台 -- 打包后环境变量不可靠，应用条件编译或运行时特征判断

---

## 第 6 章 URL 参数传递

### 原则

URL query 参数（如 `?tenant=xxx`）是外部入口传递上下文的关键通道。H5 hash 模式下，参数解析方式有特殊限制，必须使用可靠方案。

### 抽象规则

- **H5 hash 模式下，`MUST NOT` 依赖 `onLoad(options)` 获取 URL query 参数。** 根因：hash 模式下 query 在 `#` 后面，uni-app 路由解析不传入 `onLoad`。
- 获取 URL query 参数 `MUST` 在 `<script setup>` 体内同步执行解析函数，直接从 `location.href` 正则提取。
- 登录跳转 `MUST` 保留原始 URL 的 query 参数（如 `tenant`），`MUST NOT` 硬编码跳转路径丢弃参数。
- 路由参数中的 ID（雪花 ID）`MUST` 使用 `string` 类型，`MUST NOT` 使用 `Number()` 转换（精度丢失）。

### URL 参数解析正确方案

```typescript
// ✅ 正确：setup 体内同步解析，不依赖 onLoad
function parseUrlTenant(): string {
  if (typeof location === 'undefined') return ''
  const match = location.href.match(/[?&]tenant=([^&]+)/)
  return match ? decodeURIComponent(match[1]) : ''
}

const form = ref({
  tenantCode: parseUrlTenant()  // 初始化时同步读取
})
```

### URL 参数解析错误方案

```typescript
// ❌ 错误：onLoad 在 H5 hash 模式下拿不到 query 参数
onLoad((options) => {
  form.value.tenantCode = options?.tenant  // hash 模式下 options.tenant 是 undefined
})
```

### 登录跳转保留参数

```typescript
// ✅ 正确：保留当前 URL 的 query 参数
function redirectToLogin() {
  const currentQuery = location.hash.includes('?')
    ? location.hash.substring(location.hash.indexOf('?'))
    : location.search || ''
  uni.reLaunch({ url: '/pages/auth/login' + currentQuery })
}

// ❌ 错误：硬编码路径，丢失 tenant 参数
function redirectToLogin() {
  uni.reLaunch({ url: '/pages/auth/login' })  // ?tenant=xxx 被丢弃
}
```

### 反模式

- 依赖 `onLoad` 获取 H5 hash 模式 query 参数 -- 拿不到，表单初始化为空
- `redirectToLogin()` 硬编码路径 -- 租户标识丢失，登录页无法识别租户
- 雪花 ID 用 `Number(route.params.id)` 转换 -- 超出 JS 安全整数范围，精度丢失

---

## 第 7 章 认证与授权流程

### 原则

不同环境采用不同认证方式：微信浏览器走 OAuth，非微信 H5 走用户名密码，小程序走微信登录。token 统一管理，过期统一处理。

### 抽象规则

- 认证方式 `MUST` 按环境分流：微信浏览器 → OAuth，非微信 H5 → 用户名密码，小程序 → 微信登录 API。
- `redirectToLogin()` `MUST` 判断环境后分流，`MUST NOT` 统一跳同一页面。
- 不需要 token 的接口（登录、注册、OAuth 回调、绑定手机）**`MUST` 显式传 `{ needAuth: false }`**。
- token 存储 `MUST` 使用 `uni.setStorageSync('access_token', ...)`，`MUST NOT` 只存内存（刷新丢失）。
- 401 响应 `MUST` 在拦截器统一处理：清除 token → 跳转登录页，`MUST NOT` 在每个页面单独处理。

### 环境分流示例

```typescript
// api/request.ts
function redirectToLogin() {
  // #ifdef H5
  if (isWechatBrowser()) {
    // 微信浏览器：走 OAuth 流程
    const tenantId = uni.getStorageSync('tenant_id') || 'default'
    const redirectUri = encodeURIComponent(location.href)
    location.href = `/api/auth/wechat-h5-login?redirect=${redirectUri}&tenant=${tenantId}`
  } else {
    // 非微信 H5：跳本地登录页，保留 query 参数
    const currentQuery = location.hash.includes('?')
      ? location.hash.substring(location.hash.indexOf('?'))
      : location.search || ''
    uni.reLaunch({ url: '/pages/auth/login' + currentQuery })
  }
  // #endif

  // #ifndef H5
  uni.reLaunch({ url: '/pages/auth/callback' })
  // #endif
}
```

### 反模式

- 微信浏览器跳本地登录页 -- 微信环境应走 OAuth，跳本地登录页用户体验割裂
- 登录接口不传 `needAuth: false` -- 无 token 时拦截器直接跳走，登录 API 永远发不出
- 每个页面单独处理 401 -- 逻辑分散，遗漏时用户看到原始错误而非跳登录

---

## 第 8 章 开发环境配置

### 原则

开发环境配置须解决跨端差异和工具链兼容问题。H5 开发环境的 API 地址配置有特殊注意事项。

### 抽象规则

- **H5 开发环境 `BASE_URL` `MUST` 直连后端（如 `http://127.0.0.1:5157/api`），`MUST NOT` 依赖 vite proxy。** 根因：`@dcloudio/vite-plugin-uni`（alpha 版本）会拦截 `/api` 请求，导致 proxy 返回 500 空 body。
- `vite.config.ts` 中的 proxy 配置 `SHOULD` 保留（生产环境仍需要），但开发环境实际不走 proxy。
- `BASE_URL` 判断 `MUST` 用运行时特征（如 `location.hostname === 'localhost'`），`MUST NOT` 硬编码开发环境 URL 进生产包。
- 后端 CORS `MUST` 配置 `AllowAll`（开发环境直连需要跨域），生产环境由网关统一处理。

### BASE_URL 配置示例

```typescript
// api/request.ts
const BASE_URL = (() => {
  // H5 开发环境：直连后端（绕过 uni-app vite 插件对 proxy 的干扰）
  if (typeof location !== 'undefined' && location.hostname === 'localhost') {
    return 'http://127.0.0.1:5157/api'
  }
  // 生产环境 / 小程序：走相对路径（由网关或微信网关处理）
  return '/api'
})()
```

### 反模式

- 开发环境依赖 vite proxy -- `@dcloudio/vite-plugin-uni` alpha 拦截 `/api`，返回 500
- `BASE_URL` 硬编码 `http://127.0.0.1:5157/api` -- 生产环境也直连后端，跨域问题泄漏
- 不配 CORS -- 直连后端时浏览器拒绝跨域请求

---

## 第 9 章 样式与 UI 约定

### 原则

使用 rpx 单位保证跨端适配，样式使用 `<style scoped>` 防止污染，设计 Token 集中管理。

### 抽象规则

- 尺寸单位 `MUST` 使用 `rpx`（响应式像素），`MUST NOT` 使用 `px`（除 border 等 1px 场景）。
- 页面样式 `MUST` 使用 `<style scoped>`，`MUST NOT` 使用全局样式（除非在 `styles/` 目录统一定义）。
- 颜色、字号、间距 `SHOULD` 使用 CSS 变量或 SCSS 变量集中管理，`SHOULD NOT` 在页面内硬编码色值。
- 页面级 CSS `MUST` 放在对应 `.vue` 文件的 `<style>` 块，`MUST NOT` 单独引入 `.css` 文件（增加 HTTP 请求）。

### 样式示例

```vue
<style scoped>
.login-page {
  min-height: 100vh;
  background: linear-gradient(135deg, #1890ff, #096dd9);
  padding: 120rpx 32rpx 0;  /* rpx 单位 */
}

.input-wrapper {
  background: #f5f7fa;
  border-radius: 8rpx;
  padding: 20rpx 24rpx;
}
</style>
```

### 反模式

- 使用 `px` 单位 -- 不同屏幕尺寸下显示不一致
- 页面间复制粘贴样式代码 -- 改色值需多处同步，易遗漏
- `<style>` 不加 `scoped` -- 样式污染其他页面

---

## 第 10 章 错误处理与用户体验

### 原则

错误分层处理：网络错误由拦截器统一 toast，业务错误由页面按需展示，系统错误记录日志。用户始终有明确反馈。

### 抽象规则

- 网络错误（timeout、断网）`MUST` 在拦截器统一 `uni.showToast`，`MUST NOT` 在页面重复提示。
- 业务错误（`code !== 200`）`MUST` 在拦截器 `uni.showToast` 显示 `body.message`，页面 catch 块 `MUST NOT` 再次 toast。
- 表单校验错误 `MUST` 在页面内显式展示（字段级 error 文本），`MUST NOT` 用 toast 提示表单校验错误。
- 加载状态 `MUST` 用 `loading` ref 控制按钮 `:loading` / `:disabled`，防止重复提交。

### 页面错误处理示例

```typescript
// ✅ 正确：catch 块不重复提示
async function handleLogin() {
  loading.value = true
  try {
    await userStore.usernameLogin(form.value.username, form.value.password, form.value.tenantCode)
    uni.showToast({ title: '登录成功', icon: 'success' })
    setTimeout(() => {
      uni.switchTab({ url: '/pages/home/index' })
    }, 500)
  } catch {
    // 错误已由 request 拦截器统一 toast，此处无需额外处理
  } finally {
    loading.value = false
  }
}
```

### 反模式

- catch 块重复 `uni.showToast(error.message)` -- 拦截器已提示，双重 toast
- 表单校验失败用 `uni.showToast` -- 应内联显示字段级错误，用户才知道哪个字段有问题
- 按钮不设 `:disabled="loading"` -- 用户可重复点击，触发多次请求

---

## 第 11 章 附录

### 新增页面标准步骤 Checklist

1. 在 `pages/[domain]/` 创建 `.vue` 文件（`<template>` + `<script setup lang="ts">` + `<style scoped>`）
2. 在 `pages.json` 注册路由
3. 如需 API：在 `api/[domain].ts` 定义接口类型 + 导出函数（需要 token 用默认 `needAuth`，不需要显式传 `{ needAuth: false }`）
4. 如需全局状态：在 `stores/[domain].ts` 创建 Pinia store（setup 函数风格）
5. 页面内 `try/catch` 不重复 toast（拦截器已处理）
6. 页面样式使用 `rpx`，`<style scoped>`

### 命名速查表

| 对象 | 约定 | 示例 |
|------|------|------|
| 页面文件 | kebab-case `.vue` | `login.vue`、`booking-detail.vue` |
| API 文件 | camelCase `.ts` | `auth.ts`、`booking.ts` |
| Store 文件 | camelCase `.ts` | `user.ts`、`booking.ts` |
| 工具文件 | camelCase `.ts` | `wechat.ts`、`scan.ts` |
| 接口函数 | camelCase | `usernameLogin()`、`getBookings()` |
| 类型定义 | PascalCase | `LoginResponse`、`UserInfo` |
| URL 参数 | camelCase | `tenantCode`、`bookingId` |

### 已知坑索引（来自 CR-005）

| 编号 | 问题 | 规范章节 |
|------|------|----------|
| 1 | H5 hash 模式 `onLoad` 拿不到 query 参数 | 第 6 章 |
| 2 | `needAuth=true` 阻断登录请求 | 第 3 章、第 7 章 |
| 3 | `redirectToLogin()` 丢失 query 参数 | 第 6 章、第 7 章 |
| 4 | vite-plugin-uni alpha 干扰 proxy | 第 8 章 |

### 反模式索引

- Ch1：页面直接调 `uni.request`、工具函数引入 store、类型定义单独目录
- Ch2：路径硬编码、TabBar 页用 `navigateTo`、Options API
- Ch3：绕过封装调 `uni.request`、登录接口漏 `needAuth:false`、catch 重复 toast、访问 `res.code`
- Ch4：utils 引入 store、store 操作 DOM 导航、store 互相引用
- Ch5：setup 函数体内 `// #ifdef`、页面重复写 UA 检测、`process.env.UNI_PLATFORM`
- Ch6：依赖 `onLoad` 获取 hash query、`redirectToLogin` 硬编码路径、雪花 ID `Number()` 转换
- Ch7：微信浏览器跳本地登录、登录接口漏 `needAuth:false`、页面单独处理 401
- Ch8：依赖 vite proxy、硬编码开发 URL 进生产包、不配 CORS
- Ch9：`px` 单位、复制粘贴样式、不加 `scoped`
- Ch10：catch 重复 toast、表单校验用 toast、按钮不防重复提交

---

## 变更说明

| 版本 | 日期 | 变更 |
|------|------|------|
| V1.0 | 2026-08-19 | 首版发布，覆盖 Ch0–Ch11；整合 CR-005 经验（已知坑 #11-14） |

---

## 例外条款

- 已有代码与规范冲突时标注"历史遗留"。
- 新代码 `MUST` 遵循本规范。
- 存量代码按"接触即改"原则：修改时顺带迁移，不强制批量重构。
