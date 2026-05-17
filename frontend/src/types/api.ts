// API通用类型定义

export interface ApiResponse<T> {
  success: boolean
  data: T
  message?: string
}

export interface ApiError {
  success: false
  error: {
    code: string
    message: string
    details?: Array<{
      field: string
      message: string
      severity: 'error' | 'warning'
    }>
    timestamp: string
    request_id: string
  }
}

export interface ValidationResult {
  valid: boolean
  errors?: Array<{
    field: string
    message: string
    severity: 'error' | 'warning'
  }>
  warnings?: Array<{
    field: string
    message: string
    suggestion?: string
  }>
  quality_score?: number
}

export interface CostEstimate {
  model_name: string
  pricing: {
    input_price: number
    output_price: number
    currency: string
  }
  estimates: {
    per_message: {
      average_cost: number
      min_cost: number
      max_cost: number
    }
    daily: {
      conversations: number
      tokens: number
      cost: number
    }
    monthly: {
      conversations: number
      tokens: number
      cost: number
    }
  }
  optimization_tips?: Array<{
    tip: string
    potential_savings: number
  }>
}

export interface Template {
  template_id: string
  template_name: string
  template_description: string
  template_type: 'single_agent' | 'multi_agent'
  category?: string
  difficulty?: 'beginner' | 'intermediate' | 'advanced'
  tags: string[]
  thumbnail?: string
  demo_url?: string
  usage_count: number
  popularity_score: number
  user_rating?: number
  is_official: boolean
  is_featured: boolean
  created_at: string
}

export interface TemplateListResponse {
  templates: Template[]
}

export interface ConnectionTestResult {
  connection_status: 'success' | 'failed'
  response_time: number
  model_available: boolean
  test_message: string
  timestamp: string
}
