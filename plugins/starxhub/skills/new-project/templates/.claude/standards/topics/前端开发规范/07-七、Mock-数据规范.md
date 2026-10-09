# 前端开发规范 · 七、Mock 数据规范

> 拆分自《前端开发规范》第 7 节。需要全量上下文时读原文件。


### 7.1 Mock 文件结构

```typescript
// mock/modules/family-base.mock.ts
import type { MockRoute } from '../index'
import { db, nextId } from '../_database'
import { wrapResponse, wrapError, wrapPageResponse, paginate, filterByKeyword } from '../_helpers'

export const familyBaseMocks: MockRoute[] = [
  // GET 列表
  {
    method: 'get',
    url: /\/api\/family\/campuses$/,
    handler() {
      return wrapResponse(db.campuses)
    },
  },
  // POST 新增
  {
    method: 'post',
    url: /\/api\/family\/campuses$/,
    handler(config) {
      const body = typeof config.data === 'string' ? JSON.parse(config.data) : config.data
      // 验证逻辑...
      const newItem = {
        id: nextId.campus++,
        ...body,
        createdAt: new Date().toISOString(),
      }
      db.campuses.push(newItem)
      return wrapResponse(newItem, '创建成功')
    },
  },
  // 其他接口...
]
```

### 7.2 数据库模拟

```typescript
// mock/_database.ts

// 静态数据
export const campuses: Campus[] = [...]
export const communities: Community[] = [...]

// 动态生成的数据
function genRooms(): Room[] { ... }
export const rooms = genRooms()

// 导出数据库对象
export const db = {
  campuses,
  communities,
  buildings,
  rooms,
  // ...
}

// ID 计数器
export let nextId = {
  campus: 3,
  community: 5,
  // ...
}
```

### 7.3 响应格式

```typescript
// 成功响应
wrapResponse(data, '操作成功')
// => { code: 200, message: '操作成功', data: {...}, timestamp: '...' }

// 错误响应
wrapError('错误信息', 400)
// => { code: 400, message: '错误信息', data: null, timestamp: '...' }

// 分页响应
wrapPageResponse(items, total, pageIndex, pageSize)
```

---

