// 对话相关类型定义

export interface Message {
  id: string
  message_id: string
  conversation_id: string
  role: 'user' | 'assistant' | 'system'
  content: string
  content_type: string
  input_tokens: number
  output_tokens: number
  total_tokens: number
  response_time: number
  created_at: string
}

export interface Conversation {
  id: string
  conversation_id: string
  agent_id: string
  team_id?: string
  user_id?: string
  status: ConversationStatus
  total_messages: number
  total_tokens_used: number
  total_cost: number
  average_response_time: number
  user_satisfaction?: number
  user_feedback?: string
  started_at: string
  completed_at?: string
  last_activity_at: string
}

export type ConversationStatus = 'active' | 'completed' | 'failed' | 'archived'

export interface CreateConversationRequest {
  agent_id: string
  user_id?: string
  metadata?: {
    source?: string
    user_agent?: string
  }
}

export interface SendMessageRequest {
  content: string
  message_type?: string
  metadata?: {
    timestamp?: string
  }
}

export interface SendMessageResponse {
  message_id: string
  conversation_id: string
  content: string
  role: 'user' | 'assistant' | 'system'
  created_at: string
  tokens_used: {
    input: number
    output: number
    total: number
  }
  response_time: number
}
