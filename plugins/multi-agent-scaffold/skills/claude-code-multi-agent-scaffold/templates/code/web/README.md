# {{PROJECT_NAME}} — 与业务无关的前端代码工程

本工程是遵循 `.claude/standards/前端开发规范.md` 的**业务无关** Vue 3 前端骨架。不含任何业务页面或组件，只有可复用的基础设施，作为新项目前端的起点。

## 技术栈

- Vue 3（Composition API + `<script setup>`）
- Vite + TypeScript
- Element Plus（UI 组件库）
- Pinia（状态管理）
- Vue Router（路由）
- Axios（HTTP 客户端）

## 目录结构

```
src/
├── api/                  # API 接口定义
│   └── request.ts        # Axios 实例（请求/响应拦截器）
├── components/           # 公共组件（{Component}.vue / {Xxx}Selector.vue）
├── layouts/              # 布局组件
│   └── DefaultLayout.vue # 侧边栏 + 顶栏 + 主内容
├── mock/                 # Mock 数据
│   └── modules/          # 按模块划分
├── router/               # 路由配置
│   └── index.ts
├── stores/               # Pinia 状态管理
│   └── user.ts
├── styles/               # 全局样式
│   └── variables.scss
├── types/                # TypeScript 类型定义
│   └── api.d.ts          # ApiResult / PageResult / PageQuery
├── utils/                # 工具函数
└── views/                # 页面组件
    └── dashboard/
        └── DashboardView.vue
```

## 已内置的基础设施（业务无关）

- **`@` 路径别名**：`@/` 指向 `src/`（vite.config.ts + tsconfig.app.json 已配置）
- **路由骨架**：`router/index.ts` 含默认布局 + 首页看板路由
- **状态管理**：`stores/user.ts`（token/username）
- **HTTP 客户端**：`api/request.ts`（Axios 实例 + 请求/响应拦截器）
- **统一类型**：`types/api.d.ts`（ApiResult / PageResult / PageQuery，与后端严格对应）
- **全局样式变量**：`styles/variables.scss`

## 如何接入业务

1. **类型**：在 `types/` 按模块新增 `{module}.d.ts`（Entity/Form/Query 三类型）
2. **API**：在 `api/` 按模块新增 `{module}.ts`（get/create/update/delete 函数）
3. **页面**：在 `views/{module}/` 新增 `{PageName}.vue`
4. **路由**：在 `router/index.ts` 注册路由（懒加载 + meta 标题）
5. **组件**：公共选择器等放 `components/`

## 命名规范速查

| 类型 | 规则 | 示例 |
|------|------|------|
| 页面组件 | PascalCase + 功能 | EntityList.vue |
| 公共组件 | PascalCase + Selector | CategorySelector.vue |
| API 文件 | kebab-case.ts | entity.ts |
| API 函数 | get{Entity}s / create{Entity} / update{Entity} / delete{Entity} | getEntities |
| 类型 | Entity / EntityForm / EntityQuery | Entity / EntityForm / EntityQuery |

## 字段映射（与后端严格对应，禁止改名）

- 后端 `EntityName` → 前端 `entityName`（camelCase）
- 分页参数 `pageIndex`/`pageSize`（禁止 pageNum/page）
- 分页响应 `items`/`total`/`pageIndex`/`pageSize`（禁止 list/records）

## 启动与构建

```bash
npm install       # 安装依赖
npm run dev       # 开发模式
npm run build     # 类型检查 + 构建
npm run preview   # 预览构建产物
```
