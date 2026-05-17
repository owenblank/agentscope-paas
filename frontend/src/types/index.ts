// 统一导出所有类型
export * from './agent'
export * from './team'
export * from './conversation'
export * from './api'
export * from './auth'  // Add this line

// 通用工具类型
export interface PaginationParams {
  page?: number
  limit?: number
  sort?: string
  order?: 'asc' | 'desc'
}

export interface FilterParams {
  status?: string
  tags?: string[]
  search?: string
  date_from?: string
  date_to?: string
}
