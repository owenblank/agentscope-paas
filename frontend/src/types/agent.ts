// 智能体相关类型定义

export interface AgentMetadata {
  agent_id: string
  agent_name: string
  agent_type: AgentType
  description: string
  version: string
  tags: string[]
}

// 智能体类型 - 目前仅支持 ReActAgent
export type AgentType = 'ReActAgent'

export interface ModelConfig {
  model_name: string
  api_key: string
  base_url: string  // 根据配置文件模板，base_url 改为必填
  temperature?: number
  max_tokens?: number
  top_p?: number
  frequency_penalty?: number
  presence_penalty?: number
}

export interface PromptConfig {
  system_prompt: string
  user_prompt_template?: string
}

export interface MemoryConfig {
  short_term?: {
    enabled: boolean
    max_history_rounds: number
  }
  long_term?: {
    enabled: boolean
    storage_type: 'file' | 'database' | 'redis' | 'vector'
    storage_path?: string
    connection_string?: string
    vector_db_path?: string
    collection_name?: string
    vector_config?: {
      embedding_model?: string
      similarity_threshold?: number
      top_k?: number
    }
  }
  vector?: {
    enabled: boolean
    vector_db_path: string
    collection_name: string
    vector_config?: {
      embedding_model?: string
      similarity_threshold?: number
      top_k?: number
    }
  }
}

export interface Tool {
  tool_id: string
  tool_name: string
  tool_type: string
  description: string
  tool_config: Record<string, unknown>
  permissions?: {
    enabled: boolean
    max_calls_per_session?: number
  }
}

export interface ToolConfig {
  tools: Tool[]
}

export interface KnowledgeBase {
  knowledge_id: string
  knowledge_name: string
  knowledge_type: string
  description: string
  knowledge_config: {
    storage_type: string
    connection_info: {
      vector_db_path?: string
      collection_name?: string
      embedding_model?: string
      documents_path?: string
      connection_string?: string
      table_name?: string
      indexed_columns?: string[]
      api_endpoint?: string
      authentication?: {
        type: string
        token?: string
        update_interval?: number
      }
    }
    retrieval_config?: {
      similarity_threshold?: number
      top_k?: number
      search_type?: string
      max_results?: number
      query_type?: string
      cache_enabled?: boolean
      cache_ttl?: number
    }
    permissions?: {
      enabled: boolean
      max_queries_per_conversation?: number
      allowed_operations?: string[]
      read_only?: boolean
      rate_limit?: number
    }
  }
}

export interface KnowledgeConfig {
  knowledge_bases: KnowledgeBase[]
}

export interface Skill {
  skill_id: string
  skill_name: string
  skill_type: string
  description: string
  skill_config: {
    operations: Array<{
      operation_type: string
      enabled: boolean
      config: Record<string, unknown>
    }>
    performance_config?: {
      max_text_length?: number
      max_data_size?: string
      max_execution_time?: number
      max_code_length?: number
      timeout?: number
      batch_processing?: boolean
      retry_count?: number
    }
    permissions?: {
      enabled: boolean
      max_calls_per_conversation?: number
      execution_quota?: number
      security_level?: string
      data_retention?: boolean
      read_only?: boolean
    }
  }
}

// 技能上传配置类型（对齐skill-creator规范）
export interface SkillsUploadConfig {
  load_mode: 'upload'
  upload_config: {
    supported_upload_methods: Array<{
      method: 'single_file' | 'folder' | 'zip'
      enabled: boolean
      description: string
      max_size_mb: number
      max_files?: number
      supported_formats: string[]
      // SKILL.md文件结构要求（对齐skill-creator）
      skill_md_requirements?: {
        require_frontmatter: boolean
        required_frontmatter_fields: string[]
        optional_frontmatter_fields?: string[]
        require_markdown_body: boolean
        max_recommended_lines?: number
      }
      // 目录结构要求
      directory_structure_requirements?: {
        require_skill_md_root: boolean
        supported_subdirectories: string[]
        require_file_references: boolean
      }
      extraction_config?: {
        extract_root_only: boolean
        preserve_structure: boolean
        overwrite_existing: boolean
        zip_requirements?: {
          require_skill_md_in_root: boolean
          supported_structure: string[]
        }
      }
    }>
    max_file_size_mb: number
    max_total_size_mb: number
    max_files_per_upload: number
    max_zip_files?: number
    validation_config?: {
      validate_format: boolean
      validate_size: boolean
      validate_content: boolean
      validate_schema: boolean
      validate_frontmatter?: boolean
      validate_markdown?: boolean
      validate_directory_structure?: boolean
      allowed_encodings: string[]
      frontmatter_validation?: {
        name_pattern: string
        name_min_length: number
        name_max_length: number
        description_min_length: number
        description_max_length: number
        require_trigger_info: boolean
      }
    }
    security_config?: {
      enable_virus_scan: boolean
      enable_malware_scan: boolean
      verify_signature: boolean
      allowed_mime_types: string[]
    }
    storage_config?: {
      storage_type: 'local' | 's3' | 'oss' | 'cos'
      local_storage_path: string
      temp_storage_path: string
      skills_install_path?: string
      preserve_filename: boolean
      naming_rule: 'preserve_original' | 'uuid' | 'timestamp' | 'custom'
      backup_config?: {
        enabled: boolean
        backup_path: string
        backup_before_overwrite: boolean
      }
    }
    processing_config?: {
      auto_parse_skill_md: boolean
      extract_frontmatter: boolean
      validate_structure: boolean
      generate_preview: boolean
      index_content: boolean
      process_scripts?: boolean
      process_references?: boolean
      process_assets?: boolean
      generate_metadata?: boolean
      activation_config?: {
        auto_install_dependencies: boolean
        verify_compatibility: boolean
        create_backup: boolean
        backup_retention_days: number
      }
    }
  }
  execution_config?: {
    max_concurrent_skills: number
    skill_timeout: number
    failure_handling_strategy: 'continue' | 'stop' | 'retry'
    max_retries: number
    context_management?: {
      maintain_context: boolean
      context_window_size: number
      cache_outputs: boolean
    }
  }
  permissions?: {
    enabled: boolean
    max_skill_calls_per_conversation: number
    allowed_skill_categories: string[]
    security_level: 'low' | 'medium' | 'high'
    upload_permissions?: {
      allowed_roles: string[]
      require_moderation: boolean
      allow_overwrite: boolean
      allow_deletion: boolean
      version_control?: {
        enabled: boolean
        auto_version_on_update: boolean
        keep_version_history: boolean
        max_versions: number
      }
    }
  }
}

export interface SkillsConfig {
  skills?: Skill[]  // 保持向后兼容
  load_mode?: 'upload'  // 新增：上传模式
  upload_config?: SkillsUploadConfig['upload_config']  // 新增：上传配置
}

export interface BehaviorConfig {
  max_conversation_rounds?: number
  auto_reply?: boolean
  output_format?: {
    type: 'text' | 'json' | 'markdown' | 'xml'
    include_reasoning?: boolean
    require_citations?: boolean
  }
  safety_config?: {
    content_filter?: boolean
    refused_topics?: string[]
  }
}

export interface MonitoringConfig {
  log_level?: 'DEBUG' | 'INFO' | 'WARNING' | 'ERROR'
  log_path?: string
  enable_performance_tracking?: boolean
  save_conversation_history?: boolean
  conversation_history_path?: string
}

export interface ExtensionConfig {
  custom_fields?: Record<string, unknown>
  plugins?: Array<{
    plugin_name: string
    plugin_config: Record<string, unknown>
  }>
}

export interface AgentConfig {
  agent_metadata: AgentMetadata
  model_config: ModelConfig
  prompt_config: PromptConfig
  memory_config?: MemoryConfig
  tool_config?: ToolConfig
  knowledge_config?: KnowledgeConfig
  skills_config?: SkillsConfig
  behavior_config?: BehaviorConfig
  monitoring_config?: MonitoringConfig
  extension_config?: ExtensionConfig
}

export interface Agent {
  id: string
  agent_id: string
  agent_name: string
  agent_type: AgentType
  description: string
  status: AgentStatus
  config: AgentConfig
  statistics: AgentStatistics
  created_at: string
  updated_at: string
  tags?: string[]
}

export type AgentStatus = 'created' | 'running' | 'stopped' | 'error'

export interface AgentStatistics {
  total_conversations: number
  total_tokens_used: number
  total_cost: number
  average_response_time: number
  success_rate: number
}

export interface AgentListResponse {
  agents: Agent[]
  pagination: {
    total: number
    page: number
    limit: number
    pages: number
  }
}
