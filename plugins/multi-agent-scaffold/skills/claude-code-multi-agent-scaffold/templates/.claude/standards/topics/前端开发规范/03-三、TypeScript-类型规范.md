# 前端开发规范 · 三、TypeScript 类型规范

> 拆分自《前端开发规范》第 3 节。需要全量上下文时读原文件。


### 3.1 类型文件组织

按业务模块划分类型文件：

```
types/
├── api.d.ts       # 通用 API 响应类型
├── family.d.ts    # 家属区模块类型
├── meter.d.ts     # 仪表模块类型
└── enums.ts       # 枚举和常量
```

### 3.2 实体类型定义

每个实体定义三个类型：**Entity**（完整实体）、**Form**（表单）、**Query**（查询参数）

```typescript
// ===== Campus =====

// 完整实体（对应数据库记录）
export interface Campus {
  campusId: number
  campusName: string
  campusCode: string
  address?: string
  remark?: string
  createdAt: string
  updatedAt: string
}

// 表单类型（新建/编辑）
export interface CampusForm {
  campusId?: number           // 编辑时有值
  campusName: string          // 必填字段
  campusCode: string          // 必填字段
  address?: string            // 可选字段
  remark?: string
}

// 查询参数
export interface CampusQuery extends PageQuery {
  keyword?: string
  status?: number | null
}
```

### 3.3 API 响应类型

```typescript
// 通用响应
export interface ApiResult<T = any> {
  code: number
  message: string
  data: T
  timestamp: string
}

// 分页响应
export interface PageResult<T = any> {
  items: T[]
  total: number
  pageIndex: number
  pageSize: number
}

// 分页查询参数
export interface PageQuery {
  pageIndex?: number
  pageSize?: number
}
```

### 3.4 枚举定义

枚举应同时定义：**enum**（值）、**Label**（显示文本）、**Type**（标签样式）

```typescript
// 枚举值
export enum MeterStatus {
  Active = 1,
  Suspended = 2,
  Unused = 3,
  NewActive = 4,
}

// 显示文本
export const MeterStatusLabel: Record<number, string> = {
  [MeterStatus.Active]: '启用',
  [MeterStatus.Suspended]: '暂未抄',
  [MeterStatus.Unused]: '未用',
  [MeterStatus.NewActive]: '新启用',
}

// Element Plus Tag 类型
export const MeterStatusType: Record<number, 'success' | 'warning' | 'info' | 'danger' | undefined> = {
  [MeterStatus.Active]: 'success',
  [MeterStatus.Suspended]: 'warning',
  [MeterStatus.Unused]: 'info',
  [MeterStatus.NewActive]: undefined,
}
```

### 3.5 联合类型

使用字面量联合类型表示有限选项：

```typescript
// 仪表类型：1-水表，2-电表
meterType: 1 | 2

// 出租状态：0-自住，1-出租
isRented: 0 | 1

// 支付状态：0-未缴，1-已缴，2-减免
paymentStatus: 0 | 1 | 2
```

### 3.6 前后端字段映射约束

#### 3.6.1 字段名映射规则

前端 TypeScript 接口属性名必须严格对应后端 DTO 属性名的 `camelCase` 形式：

| 后端 C# 属性 | 前端 TS 属性 | 说明 |
|-------------|-------------|------|
| `RoomId` | `roomId` | 主键 |
| `RoomName` | `roomName` | 普通字段 |
| `BuildingId` | `buildingId` | 外键 |
| `QrCodeUrl` | `qrCodeUrl` | 缩写词遵循 camelCase |
| `Devices` | `devices` | 禁止改名为 `facilities` 等 |

**禁止事项**：
- 禁止将后端 `devices` 在前端命名为 `facilities`
- 禁止将后端 `pageIndex` 在前端命名为 `pageNum`
- 禁止将后端返回的 `items` 在前端读取为 `list`

#### 3.6.2 分页结构约束

分页查询和响应必须使用统一字段名，与后端 `PageResult<T>` 严格对应：

```typescript
// 分页查询参数（必须使用 pageIndex，禁止 pageNum/page）
export interface PageQuery {
  pageIndex: number
  pageSize: number
}

// 分页响应（必须使用 items，禁止 list/records/data）
export interface PageResult<T> {
  items: T[]
  total: number
  pageIndex: number
  pageSize: number
}
```

#### 3.6.3 类型同步规则

1. 新增前端类型时，必须逐个对照后端 DTO 字段进行同步
2. 后端 DTO 字段变更时，必须同步更新前端类型定义，并检查所有使用该类型的组件
3. 前端新增字段前，必须确认后端 DTO 已支持该字段
4. 更新请求必须包含所有必要字段（如 `buildingId`、`floorId` 等），不得遗漏

---

