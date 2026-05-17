// 团队相关类型定义
import type { AgentConfig } from './agent'

export interface TeamMetadata {
  team_id: string
  team_name: string
  collaboration_mode: CollaborationMode
  team_goal: string
  termination_conditions: TerminationConditions
  description?: string
  version: string
}

export type CollaborationMode = 'SequentialChat' | 'RoundRobinChat' | 'ManagerProxy' | 'FreeChat'

export interface TerminationConditions {
  max_rounds: number
  success_criteria?: string[]
  failure_criteria?: string[]
}

export interface TeamConfig {
  team_metadata: TeamMetadata
  global_model_config?: {
    model_name: string
    api_key: string
    base_url?: string
    temperature?: number
    max_tokens?: number
  }
  agents: AgentConfig[]
  collaboration_config: CollaborationConfig
  task_context?: TaskContext
}

export interface CollaborationConfig {
  speaking_order?: string[]
  initial_speaker: string
  max_conversation_rounds: number
  allow_active_speaking?: boolean
  collaboration_timeout?: number
}

export interface TaskContext {
  task_description?: string
  constraints?: string[]
  output_format?: {
    deliverables?: string[]
    format_standard?: string
    quality_requirements?: string[]
  }
  reference_context?: string[]
}

export interface Team {
  id: string
  team_id: string
  team_name: string
  collaboration_mode: CollaborationMode
  description: string
  status: 'created' | 'running' | 'stopped' | 'error'
  config: TeamConfig
  total_agents: number
  total_conversations: number
  created_at: string
  updated_at: string
}

export interface TeamListResponse {
  teams: Team[]
  pagination: {
    total: number
    page: number
    limit: number
    pages: number
  }
}
