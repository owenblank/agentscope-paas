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

  // 测试MCP服务器连接
  async testMCPConnection(serverConfig: any) {
    const response = await api.post<ApiResponse<any>>('/mcp/test-connection', {
      server_config: serverConfig
    })
    return response.data.data
  },

  // 获取内置工具注册表
  async getBuiltinToolsRegistry() {
    const response = await api.get<ApiResponse<any>>('/tools/builtin/registry')
    return response.data.data
  },

  // 配置内置工具
  async configureBuiltinTool(toolConfig: any) {
    const response = await api.post<ApiResponse<any>>('/tools/builtin/configure', {
      tool_config: toolConfig
    })
    return response.data.data
  },

  // 获取工具类别
  async getToolCategories() {
    const response = await api.get<ApiResponse<any>>('/tools/categories')
    return response.data.data
  },

  // 执行工具
  async executeTool(toolId: string, args: any, context?: any) {
    const response = await api.post<ApiResponse<any>>(`/tools/${toolId}/execute`, {
      arguments: args,
      context
    })
    return response.data.data
  },

  // 分析上下文压缩
  async analyzeContextCompression(context: any[], compressionConfig: any) {
    const response = await api.post<ApiResponse<any>>('/compression/analyze', {
      context,
      compression_config: compressionConfig
    })
    return response.data.data
  },

  // 预览压缩结果
  async previewCompression(context: any[], compressionConfig: any) {
    const response = await api.post<ApiResponse<any>>('/compression/preview', {
      context,
      compression_config: compressionConfig
    })
    return response.data.data
  },

  // 获取压缩策略
  async getCompressionStrategies() {
    const response = await api.get<ApiResponse<any>>('/compression/strategies')
    return response.data.data
  },
}
