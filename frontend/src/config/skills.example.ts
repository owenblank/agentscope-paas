/**
 * AgentScope-PaaS 前端技能集成配置示例
 *
 * 本文件展示如何在前端项目中配置和使用技能上传功能
 * 完全对齐skill-creator规范
 */

import { SkillsUploadConfig } from '@/types/agent'

/**
 * 完整的技能上传配置示例
 * 对齐skill-creator规范的所有特性
 */
export const exampleSkillsUploadConfig: SkillsUploadConfig = {
  load_mode: 'upload',
  upload_config: {
    // 支持的三种上传方式
    supported_upload_methods: [
      // 1. 单个SKILL.md文件上传（主要方式）
      {
        method: 'single_file',
        enabled: true,
        description: '上传单个SKILL.md文件，必须符合skill-creator规范',
        max_size_mb: 3,
        supported_formats: ['.md'],
        skill_md_requirements: {
          require_frontmatter: true,
          required_frontmatter_fields: ['name', 'description'],
          optional_frontmatter_fields: ['compatibility', 'author', 'version'],
          require_markdown_body: true,
          max_recommended_lines: 500
        }
      },
      // 2. 文件夹上传（支持复杂技能结构）
      {
        method: 'folder',
        enabled: true,
        description: '上传包含技能文件的文件夹，支持完整skill-creator目录结构',
        max_size_mb: 3,
        max_files: 20,
        supported_formats: ['.md', '.py', '.js', '.txt'],
        directory_structure_requirements: {
          require_skill_md_root: true,
          supported_subdirectories: ['scripts', 'references', 'assets'],
          require_file_references: true
        }
      },
      // 3. ZIP压缩包上传（支持技能打包分发）
      {
        method: 'zip',
        enabled: true,
        description: '上传ZIP格式的技能压缩包，符合skill-creator打包规范',
        max_size_mb: 3,
        max_files: 50,
        supported_formats: ['.zip'],
        extraction_config: {
          extract_root_only: false,
          preserve_structure: true,
          overwrite_existing: false,
          zip_requirements: {
            require_skill_md_in_root: true,
            supported_structure: [
              'SKILL.md',
              'scripts/',
              'references/',
              'assets/',
              'evals/',
              'agents/'
            ]
          }
        }
      }
    ],

    // 文件大小限制（严格遵循3MB限制）
    max_file_size_mb: 3,
    max_total_size_mb: 10,
    max_files_per_upload: 20,
    max_zip_files: 50,

    // 文件验证配置（严格对齐skill-creator规范）
    validation_config: {
      validate_format: true,
      validate_size: true,
      validate_content: true,
      validate_schema: true,
      validate_frontmatter: true,
      validate_markdown: true,
      validate_directory_structure: true,
      allowed_encodings: ['utf-8', 'utf-8-sig', 'ascii'],
      frontmatter_validation: {
        name_pattern: '^[a-z0-9-]+$',
        name_min_length: 2,
        name_max_length: 50,
        description_min_length: 50,
        description_max_length: 500,
        require_trigger_info: true
      }
    },

    // 安全扫描配置
    security_config: {
      enable_virus_scan: false,
      enable_malware_scan: true,
      verify_signature: false,
      allowed_mime_types: [
        'text/markdown',
        'text/plain',
        'text/x-python',
        'text/javascript',
        'application/zip',
        'application/x-zip-compressed',
        'application/json',
        'application/x-yaml'
      ]
    },

    // 存储配置（对齐skill-creator技能存储结构）
    storage_config: {
      storage_type: 'local',
      local_storage_path: './uploads/skills/',
      temp_storage_path: './temp/skills/',
      skills_install_path: './installed_skills/',
      preserve_filename: true,
      naming_rule: 'preserve_original',
      backup_config: {
        enabled: true,
        backup_path: './backups/skills/',
        backup_before_overwrite: true
      }
    },

    // 处理配置（对齐skill-creator工作流程）
    processing_config: {
      auto_parse_skill_md: true,
      extract_frontmatter: true,
      validate_structure: true,
      generate_preview: true,
      index_content: true,
      process_scripts: true,
      process_references: true,
      process_assets: true,
      generate_metadata: true,
      activation_config: {
        auto_install_dependencies: false,
        verify_compatibility: true,
        create_backup: true,
        backup_retention_days: 30
      }
    }
  },

  // 技能执行配置（对齐skill-creator执行模式）
  execution_config: {
    max_concurrent_skills: 5,
    skill_timeout: 30,
    failure_handling_strategy: 'continue',
    max_retries: 2,
    context_management: {
      maintain_context: true,
      context_window_size: 5,
      cache_outputs: true
    }
  },

  // 技能权限配置（对齐skill-creator权限模型）
  permissions: {
    enabled: true,
    max_skill_calls_per_conversation: 50,
    allowed_skill_categories: [
      'text_analysis',
      'data_analysis',
      'general',
      'api_tool',
      'code_execution',
      'document_processing',
      'web_interaction'
    ],
    security_level: 'medium',
    upload_permissions: {
      allowed_roles: ['admin', 'developer', 'user'],
      require_moderation: false,
      allow_overwrite: true,
      allow_deletion: true,
      version_control: {
        enabled: true,
        auto_version_on_update: true,
        keep_version_history: true,
        max_versions: 10
      }
    }
  }
}

/**
 * 预设的技能类别配置
 * 用于不同角色的智能体
 */
export const presetSkillCategories = {
  // 产品经理角色
  project_manager: [
    'project_management',
    'communication',
    'coordination',
    'text_analysis',
    'general'
  ],

  // 开发者角色
  developer: [
    'code_execution',
    'api_tool',
    'text_analysis',
    'general'
  ],

  // 架构师角色
  architect: [
    'architecture',
    'code_analysis',
    'performance_analysis',
    'data_analysis',
    'general'
  ],

  // 数据分析师角色
  data_analyst: [
    'data_analysis',
    'general',
    'api_tool',
    'code_execution'
  ],

  // 客服角色
  customer_service: [
    'text_analysis',
    'general',
    'document_processing'
  ]
}

/**
 * 技能安全级别配置
 */
export const securityLevelConfigs = {
  low: {
    enabled: true,
    max_skill_calls_per_conversation: 100,
    allowed_skill_categories: ['general'],
    restrictions: []
  },

  medium: {
    enabled: true,
    max_skill_calls_per_conversation: 50,
    allowed_skill_categories: [
      'text_analysis',
      'data_analysis',
      'general',
      'api_tool'
    ],
    restrictions: ['no_external_network', 'log_all_calls']
  },

  high: {
    enabled: true,
    max_skill_calls_per_conversation: 20,
    allowed_skill_categories: [
      'text_analysis',
      'data_analysis',
      'code_execution'
    ],
    restrictions: [
      'no_external_network',
      'log_all_calls',
      'require_approval',
      'sandbox_execution'
    ]
  }
}

/**
 * 前端组件使用示例
 */
export const skillUploadUsageExample = {
  // React组件中的使用方式
  componentUsage: `
import { SkillsUploadForm } from '@/components/Agent/SkillsUploadForm'
import { useAgentFormStore } from '@/store/agentFormStore'

const MyAgentConfigPage = () => {
  const { formData, updateFormData } = useAgentFormStore()

  const handleSkillsUpload = (skillsConfig: SkillsUploadConfig) => {
    updateFormData({
      skills_config: skillsConfig
    })
  }

  return (
    <div>
      <h2>技能配置</h2>
      <SkillsUploadForm
        config={exampleSkillsUploadConfig}
        onChange={handleSkillsUpload}
      />
    </div>
  )
}
`,

  // API调用示例
  apiUsage: `
// 上传技能文件
const uploadSkillFile = async (file: File, method: 'single_file' | 'folder' | 'zip') => {
  const formData = new FormData()
  formData.append('file', file)
  formData.append('upload_method', method)

  const response = await fetch('/api/skills/upload', {
    method: 'POST',
    body: formData
  })

  return response.json()
}

// 验证SKILL.md文件
const validateSkillMd = async (content: string) => {
  const response = await fetch('/api/skills/validate', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ content })
  })

  return response.json()
}

// 获取已安装的技能列表
const getInstalledSkills = async () => {
  const response = await fetch('/api/skills')
  return response.json()
}
`,

  // 状态管理示例
  stateManagement: `
import { create } from 'zustand'

interface SkillStore {
  uploadedSkills: Skill[]
  uploadProgress: number
  validationErrors: ValidationError[]
  uploadSkill: (skill: Skill) => Promise<void>
  validateSkill: (content: string) => ValidationResult
  removeSkill: (skillId: string) => void
}

export const useSkillStore = create<SkillStore>((set, get) => ({
  uploadedSkills: [],
  uploadProgress: 0,
  validationErrors: [],

  uploadSkill: async (skill: Skill) => {
    set({ uploadProgress: 0, validationErrors: [] })

    try {
      // 上传逻辑
      const result = await uploadToServer(skill)

      // 更新状态
      set(state => ({
        uploadedSkills: [...state.uploadedSkills, result],
        uploadProgress: 100
      }))
    } catch (error) {
      set({ validationErrors: [error] })
    }
  },

  validateSkill: (content: string) => {
    // 验证SKILL.md文件内容
    const errors: ValidationError[] = []

    // 验证YAML frontmatter
    if (!content.startsWith('---')) {
      errors.push({ field: 'frontmatter', message: '必须以YAML frontmatter开始' })
    }

    // 验证必需字段
    const hasName = /name:\s*[a-z0-9-]+/.test(content)
    const hasDescription = /description:\s*.{50,500}/.test(content)

    if (!hasName) {
      errors.push({ field: 'name', message: '缺少name字段或格式不正确' })
    }

    if (!hasDescription) {
      errors.push({ field: 'description', message: 'description字段长度必须在50-500字符之间' })
    }

    return { valid: errors.length === 0, errors }
  },

  removeSkill: (skillId: string) => {
    set(state => ({
      uploadedSkills: state.uploadedFilters.filter(skill => skill.id !== skillId)
    }))
  }
}))
`
}

/**
 * 错误处理和验证
 */
export const skillValidationRules = {
  // SKILL.md frontmatter验证
  frontmatter: {
    requiredFields: ['name', 'description'],
    optionalFields: ['author', 'version', 'compatibility'],
    namePattern: /^[a-z0-9-]+$/,
    nameLength: { min: 2, max: 50 },
    descriptionLength: { min: 50, max: 500 }
  },

  // 文件大小验证
  fileSize: {
    maxFileSizeMB: 3,
    maxTotalSizeMB: 10,
    maxFilesPerUpload: 20,
    maxZipFiles: 50
  },

  // 目录结构验证
  directoryStructure: {
    requireSkillMdRoot: true,
    allowedSubdirectories: ['scripts', 'references', 'assets'],
    maxDepth: 3
  },

  // 安全验证
  security: {
    allowedExtensions: ['.md', '.py', '.js', '.txt', '.zip'],
    blockedPatterns: [
      /eval\s*\(/,        // 危险的eval函数
      /exec\s*\(/,        // 危险的exec函数
      /system\s*\(/,      // 系统调用
      /__import__/        // 动态导入
    ],
    maxFileSize: 3 * 1024 * 1024 // 3MB
  }
}

/**
 * 技能生命周期管理
 */
export const skillLifecycleManagement = {
  // 技能上传流程
  uploadFlow: [
    'file_selection',      // 文件选择
    'validation',          // 格式验证
    'security_check',      // 安全检查
    'parsing',             // 内容解析
    'installation',        // 安装部署
    'activation'           // 激活使用
  ],

  // 技能版本控制
  versionControl: {
    autoVersion: true,
    maxVersions: 10,
    backupBeforeUpdate: true,
    rollbackSupport: true
  },

  // 技能监控
  monitoring: {
    trackUsage: true,
    trackErrors: true,
    trackPerformance: true,
    logRetentionDays: 30
  }
}

/**
 * 导出所有配置
 */
export default {
  exampleSkillsUploadConfig,
  presetSkillCategories,
  securityLevelConfigs,
  skillUploadUsageExample,
  skillValidationRules,
  skillLifecycleManagement
}