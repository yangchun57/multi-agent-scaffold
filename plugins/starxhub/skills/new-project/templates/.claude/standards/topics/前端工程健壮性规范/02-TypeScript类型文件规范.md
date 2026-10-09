# 前端工程健壮性规范 · TypeScript 类型文件规范

> 对应问题：C-4（前端 `.d.ts` 包含运行时代码）

## 强制规则

### 1. `.d.ts` 文件只能包含类型声明

```typescript
// ✅ 正确：vite-env.d.ts 只声明类型
/// <reference types="vite/client" />

declare module '*.vue' {
  import type { DefineComponent } from 'vue'
  const component: DefineComponent<{}, {}, any>
  export default component
}

// 环境变量类型
interface ImportMetaEnv {
  readonly VITE_API_BASE_URL: string
  readonly VITE_APP_TITLE: string
}

interface ImportMeta {
  readonly env: ImportMetaEnv
}
```

```typescript
// ❌ 错误：.d.ts 包含运行时代码
// vite-env.d.ts
export const API_BASE_URL = import.meta.env.VITE_API_BASE_URL  // 错误！

export function formatDate(date: Date): string {
  return date.toLocaleDateString()  // 错误！
}

export enum Status {  // 错误！enum 是运行时代码
  Active = 1,
  Inactive = 0
}
```

### 2. 运行时代码必须放在 `.ts` 文件

```typescript
// ✅ 正确：constants.ts（运行时代码）
export const API_BASE_URL = import.meta.env.VITE_API_BASE_URL

export function formatDate(date: Date): string {
  return date.toLocaleDateString()
}

// ✅ 正确：enums.ts（运行时代码）
export enum Status {
  Active = 1,
  Inactive = 0
}

// ✅ 正确：types.ts（类型定义）
export interface User {
  id: string
  name: string
  status: Status  // 引用 enum
}
```

### 3. 文件命名规范

```
types/
├── api.d.ts          # 只包含类型声明
├── user.d.ts         # 只包含类型声明
├── constants.ts      # 运行时常量
├── enums.ts          # 运行时代码（enum）
└── utils.ts          # 运行时工具函数
```

### 4. 使用 `const` 枚举替代 `enum`（可选）

如果确实需要在 `.d.ts` 中定义枚举-like 的值，使用 `const` 对象：

```typescript
// ✅ 正确：使用 const 对象（可以放在 .d.ts）
export const Status = {
  Active: 1,
  Inactive: 0
} as const

export type Status = typeof Status[keyof typeof Status]

// 使用
const status: Status = Status.Active
```

## 检查方法

```bash
# 查找 .d.ts 中的运行时代码
grep -r "export const\|export function\|export enum" --include="*.d.ts" .

# 应该只看到类型声明
# 如果看到运行时代码，需要重命名为 .ts
```

## 检查清单

- [ ] `.d.ts` 文件只包含 `interface`、`type`、`declare`
- [ ] 运行时常量放在 `.ts` 文件
- [ ] 运行时函数放在 `.ts` 文件
- [ ] `enum` 放在 `.ts` 文件（或使用 `const` 对象替代）
