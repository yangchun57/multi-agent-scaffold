// ===== 通用 API 类型 =====

// 统一响应
export interface ApiResult<T = any> {
  code: number
  message: string
  data: T
  timestamp: string
}

// 分页响应（字段固定，与后端 PageResult<T> 严格对应）
export interface PageResult<T = any> {
  items: T[]
  total: number
  pageIndex: number
  pageSize: number
}

// 分页查询参数（字段固定，禁止使用 pageNum/page/currentPage）
export interface PageQuery {
  pageIndex: number
  pageSize: number
}
