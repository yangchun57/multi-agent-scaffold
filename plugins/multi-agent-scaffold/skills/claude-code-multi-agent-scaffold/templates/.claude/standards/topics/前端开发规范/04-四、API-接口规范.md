# 前端开发规范 · 四、API 接口规范

> 拆分自《前端开发规范》第 4 节。需要全量上下文时读原文件。


### 4.1 API 文件组织

按业务模块划分 API 文件：

```typescript
// api/family-base.ts
import request from './request'
import type { ApiResult, PageResult } from '@/types/api.d'
import type { Campus, CampusForm, Room, RoomForm, RoomQuery } from '@/types/family.d'

// ===== Campuses =====
export function getCampuses(): Promise<ApiResult<Campus[]>> {
  return request.get('/family/campuses')
}

export function createCampus(data: CampusForm): Promise<ApiResult<Campus>> {
  return request.post('/family/campuses', data)
}

export function updateCampus(id: string, data: CampusForm): Promise<ApiResult<Campus>> {
  return request.put(`/family/campuses/${id}`, data)
}

export function deleteCampus(id: string): Promise<ApiResult<null>> {
  return request.delete(`/family/campuses/${id}`)
}
```

### 4.2 命名规范

| 操作 | 命名 | 示例 |
|------|------|------|
| 获取列表 | get{Entity}s | `getCampuses` |
| 获取详情 | get{Entity}ById | `getMeterById` |
| 获取分页列表 | get{Entity}s | `getRooms(params)` |
| 新增 | create{Entity} | `createCampus` |
| 更新 | update{Entity} | `updateCampus` |
| 删除 | delete{Entity} | `deleteCampus` |
| 批量操作 | batch{Action}{Entity}s | `batchSaveReadings` |

### 4.3 RESTful API 规范

```
GET    /api/family/campuses      # 获取列表
GET    /api/family/campuses/:id  # 获取详情
POST   /api/family/campuses      # 新增
PUT    /api/family/campuses/:id  # 更新
DELETE /api/family/campuses/:id  # 删除
```

---

