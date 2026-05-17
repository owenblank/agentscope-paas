import { create } from 'zustand'
import { devtools } from 'zustand/middleware'
import type { AgentConfig, ValidationResult, CostEstimate } from '@/types'

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
