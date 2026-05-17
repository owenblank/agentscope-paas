import api from './api'
import type {
  Conversation,
  Message,
  CreateConversationRequest,
  SendMessageRequest,
  SendMessageResponse,
  ApiResponse,
} from '@/types'

// 对话服务
export const conversationService = {
  // 创建对话会话
  async createConversation(request: CreateConversationRequest) {
    const response = await api.post<ApiResponse<Conversation>>(
      `/agents/${request.agent_id}/conversations`,
      {
        user_id: request.user_id,
        metadata: request.metadata,
      }
    )
    return response.data.data
  },

  // 获取对话详情
  async getConversation(conversationId: string) {
    const response = await api.get<ApiResponse<Conversation>>(
      `/conversations/${conversationId}`
    )
    return response.data.data
  },

  // 获取对话消息列表
  async getMessages(conversationId: string, page = 1, limit = 50) {
    const response = await api.get<ApiResponse<{ messages: Message[] }>>(
      `/conversations/${conversationId}/messages`,
      { params: { page, limit } }
    )
    return response.data.data.messages
  },

  // 发送消息
  async sendMessage(conversationId: string, request: SendMessageRequest) {
    const response = await api.post<ApiResponse<SendMessageResponse>>(
      `/conversations/${conversationId}/messages`,
      request
    )
    return response.data.data
  },

  // 完成对话
  async completeConversation(conversationId: string) {
    const response = await api.post<ApiResponse<void>>(
      `/conversations/${conversationId}/complete`
    )
    return response.data
  },

  // 评价对话
  async rateConversation(
    conversationId: string,
    rating: number,
    feedback?: string
  ) {
    const response = await api.post<ApiResponse<void>>(
      `/conversations/${conversationId}/rate`,
      { user_satisfaction: rating, user_feedback: feedback }
    )
    return response.data
  },
}
