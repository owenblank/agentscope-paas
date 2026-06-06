import { create } from 'zustand'
import { devtools } from 'zustand/middleware'
import type { AgentConfig, ValidationResult, CostEstimate, MCPConfig, BuiltInToolsConfig, ContextCompressionConfig, SessionMemoryConfig, RuntimeConfig } from '@/types'
import { getDefaultRuntimeConfig } from '@/components/Agent/RuntimeConfigForm'

interface AgentFormState {
  // 当前步骤
  currentStep: number

  // 表单数据
  formData: Partial<AgentConfig>

  // 选择的模板
  selectedTemplate: string | null

  // 验证结果
  validationResult: ValidationResult | null

  // 成本估算
  costEstimate: CostEstimate | null

  // 操作
  setCurrentStep: (step: number) => void
  nextStep: () => void
  prevStep: () => void

  setFormData: (data: Partial<AgentConfig>) => void
  updateFormData: (data: Partial<AgentConfig>) => void
  resetFormData: () => void

  setSelectedTemplate: (templateId: string | null) => void

  setValidationResult: (result: ValidationResult | null) => void
  setCostEstimate: (estimate: CostEstimate | null) => void

  // 获取初始表单数据
  getInitialFormData: () => Partial<AgentConfig>
}

const initialFormData: Partial<AgentConfig> = {
  agent_metadata: {
    agent_id: '',
    agent_name: '',
    agent_type: 'ReActAgent', // 固定为 ReActAgent
    description: '',
    version: '1.0.0',
    tags: [],
  },
  model_config: {
    model_name: 'gpt-4o',
    api_key: '',
    base_url: 'https://api.openai.com/v1',  // 设置默认的 API 端点
    temperature: 0.7,
    max_tokens: 2000,
  },
  prompt_config: {
    system_prompt: '',
    user_prompt_template: '用户咨询：{user_input}',
  },
  knowledge_config: {
    knowledge_bases: [],
  },
  skills_config: {
    skills: [],
  },
  memory_config: {
    short_term: {
      enabled: true,
      max_history_rounds: 10,
    },
    long_term: {
      enabled: false,
      storage_type: 'file',
    },
    vector: {
      enabled: false,
      vector_db_path: './data/vector_memory',
      collection_name: 'agent_memories',
    },
  },
  behavior_config: {
    max_conversation_rounds: 20,
    auto_reply: true,
    output_format: {
      type: 'text',
    },
  },
  monitoring_config: {
    log_level: 'INFO',
    enable_performance_tracking: true,
    save_conversation_history: true,
  },
  // New configuration extensions
  mcp_config: {
    enabled: false,
    servers: [],
    global_settings: {
      connection_timeout: 30,
      max_concurrent_connections: 5,
      enable_tool_logging: true,
      retry_config: {
        max_retries: 3,
        backoff_multiplier: 2.0,
        initial_delay_ms: 1000
      }
    }
  },
  built_in_tools_config: {
    enabled: false,
    available_tools: [],
    categories: [],
    global_restrictions: {
      allowed_categories: [],
      max_total_calls_per_conversation: 50,
      execution_timeout: 60,
      require_user_approval: false
    }
  },
  context_compression_config: {
    enabled: false,
    strategies: {
      semantic: {
        enabled: true,
        similarity_threshold: 0.75,
        preserve_entities: true,
        preserve_keywords: [],
        min_summary_length: 100,
        max_summary_length: 500
      },
      token_based: {
        enabled: false,
        max_tokens: 2000,
        preserve_structure: true,
        priority_sections: [],
        compression_ratio: 0.5
      },
      hybrid: {
        enabled: true,
        semantic_weight: 0.6,
        token_weight: 0.4,
        min_context_length: 1000,
        adaptive_threshold: 0.8
      }
    },
    active_strategy: 'hybrid',
    trigger_conditions: {
      max_context_length: 4000,
      token_threshold: 3000,
      trigger_on_each_turn: false
    },
    priority_config: {
      enabled: false,
      priority_rules: [],
      preservation_threshold: 0.8
    },
    quality_controls: {
      min_coherence_score: 0.8,
      max_information_loss: 0.2,
      enable_validation: true,
      compression_targets: {
        min_compression_ratio: 0.3,
        max_compression_ratio: 0.6
      }
    }
  },
  session_memory_config: {
    enabled: false,
    storage_type: 'redis',
    redis_config: {
      host: 'localhost',
      port: 6379,
      db: 0,
      password: '',
      connection_pool_size: 10,
      socket_timeout: 5,
      socket_connect_timeout: 5,
    },
    ttl: 3600,
    max_messages: 100,
    memory_key_prefix: 'session_memory',
  },
  // Runtime configuration for agent deployment
  runtime_config: getDefaultRuntimeConfig()
}

export const useAgentFormStore = create<AgentFormState>()(
  devtools((set) => ({
    currentStep: 0,
    formData: initialFormData,
    selectedTemplate: null,
    validationResult: null,
    costEstimate: null,

    setCurrentStep: (step) => set({ currentStep: step }),
    nextStep: () => set((state) => ({ currentStep: state.currentStep + 1 })),
    prevStep: () => set((state) => ({ currentStep: state.currentStep - 1 })),

    setFormData: (data) => set({ formData: data }),
    updateFormData: (data) =>
      set((state) => ({
        formData: {
          ...state.formData,
          ...data,
        },
      })),
    resetFormData: () => set({ formData: initialFormData }),

    setSelectedTemplate: (templateId) => set({ selectedTemplate: templateId }),

    setValidationResult: (result) => set({ validationResult: result }),
    setCostEstimate: (estimate) => set({ costEstimate: estimate }),

    getInitialFormData: () => initialFormData,
  }))
)
