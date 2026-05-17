import api from './api'
import type { Template, TemplateListResponse, ApiResponse } from '@/types'

// 模板服务
export const templateService = {
  // 获取模板列表
  async getTemplates(params?: {
    type?: 'single_agent' | 'multi_agent'
    category?: string
    difficulty?: 'beginner' | 'intermediate' | 'advanced'
    tags?: string[]
  }) {
    const response = await api.get<ApiResponse<TemplateListResponse>>('/templates', {
      params,
    })
    return response.data.data.templates
  },

  // 获取模板详情
  async getTemplate(templateId: string) {
    const response = await api.get<ApiResponse<Template>>(`/templates/${templateId}`)
    return response.data.data
  },

  // 从模板创建智能体
  async createFromTemplate(
    templateId: string,
    customizations: {
      agent_metadata?: {
        agent_name: string
        description?: string
        tags?: string[]
      }
      model_config?: {
        model_name: string
        api_key: string
        base_url?: string
      }
      prompt_config?: {
        system_prompt: string
        user_prompt_template?: string
      }
    }
  ) {
    const response = await api.post<ApiResponse<{ agent_id: string }>>(
      `/templates/${templateId}/create`,
      { customizations }
    )
    return response.data.data
  },
}
