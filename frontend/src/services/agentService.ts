import api from './api'
import type {
  Agent,
  AgentConfig,
  AgentListResponse,
  ApiResponse,
  ValidationResult,
  CostEstimate,
  ConnectionTestResult,
  PaginationParams,
} from '@/types'

// 智能体服务
export const agentService = {
  // 获取智能体列表
  async getAgents(params?: PaginationParams) {
    const response = await api.get<ApiResponse<AgentListResponse>>('/agents', {
      params,
    })
    return response.data.data
  },

  // 获取智能体详情
  async getAgent(agentId: string) {
    const response = await api.get<ApiResponse<Agent>>(`/agents/${agentId}`)
    return response.data.data
  },

  // 创建智能体
  async createAgent(config: AgentConfig) {
    const response = await api.post<ApiResponse<{ agent_id: string; status: string }>>(
      '/agents',
      { config }
    )
    return response.data.data
  },

  // 更新智能体
  async updateAgent(agentId: string, config: Partial<AgentConfig>) {
    const response = await api.put<ApiResponse<{ agent_id: string; status: string }>>(
      `/agents/${agentId}`,
      { config }
    )
    return response.data.data
  },

  // 删除智能体
  async deleteAgent(agentId: string) {
    const response = await api.delete<ApiResponse<void>>(`/agents/${agentId}`)
    return response.data
  },

  // 启动智能体
  async startAgent(agentId: string) {
    const response = await api.post<ApiResponse<{ agent_id: string; status: string }>>(
      `/agents/${agentId}/start`
    )
    return response.data.data
  },

  // 停止智能体
  async stopAgent(agentId: string) {
    const response = await api.post<ApiResponse<{ agent_id: string; status: string }>>(
      `/agents/${agentId}/stop`
    )
    return response.data.data
  },

  // 验证配置
  async validateConfig(config: AgentConfig) {
    const response = await api.post<ApiResponse<ValidationResult>>('/config/validate', {
      config,
    })
    return response.data.data
  },

  // 估算成本
  async estimateCost(
    config: { model_config: { model_name: string; max_tokens: number } },
    assumptions?: {
      daily_conversations?: number
      avg_turns_per_conversation?: number
    }
  ) {
    const response = await api.post<ApiResponse<CostEstimate>>('/config/estimate-cost', {
      config,
      usage_assumptions: assumptions,
    })
    return response.data.data
  },

  // 测试模型连接
  async testConnection(modelConfig: {
    model_name: string
    api_key: string
    base_url?: string
  }) {
    const response = await api.post<ApiResponse<ConnectionTestResult>>(
      '/config/test-connection',
      {
        model_config: modelConfig,
      }
    )
    return response.data.data
  },
}
