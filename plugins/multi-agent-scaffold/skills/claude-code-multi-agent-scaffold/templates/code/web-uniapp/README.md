# {{PROJECT_NAME}} uni-app 前端（H5 + 微信小程序）

技术栈：{{FRONTEND_STACK}}

## 结构（依赖单向 pages -> stores -> api -> utils）

- `src/api/request.ts`：统一封装，token 注入、错误统一 toast、401 清 token 跳登录、`needAuth` 控制、按环境 `redirectToLogin`。
- `src/api/auth.ts`：认证接口 + 类型同文件（规范禁止单独 types 目录）。
- `src/stores/user.ts`：Pinia setup store，token/userInfo/tenant_id 经 `uni.setStorageSync` 持久化。
- `src/utils/wechat.ts`：`isWechatBrowser` / `parseUrlTenant`（H5 hash 模式取 query）。
- `src/pages.json` / `manifest.json`：路由与应用配置（H5 hash 模式）。

## 关键约定

- 登录/注册/OAuth 回调等接口必须显式 `{ needAuth: false }`。
- `<script setup>` 函数体内不要写 `// #ifdef`（失效），平台分支用运行时判断。
- 尺寸用 `rpx`，样式加 `scoped`，色值走 `uni.scss` Token。
- 开发环境 H5 直连后端 `{{BACKEND_ORIGIN}}/api`（uni-app vite 插件会干扰 proxy）。

## 运行

```bash
npm install
npm run dev:h5          # H5
npm run dev:mp-weixin   # 微信开发者工具导入 dist/dev/mp-weixin
```
