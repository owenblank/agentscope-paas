import { useEffect } from 'react'
import { Card, Steps, Button, Space, message, Result } from 'antd'
import { useNavigate } from 'react-router-dom'
import { useMutation } from '@tanstack/react-query'
import { agentService, templateService } from '@/services'
import { useAgentFormStore } from '@/store'
import TemplateSelector from '@/components/Agent/TemplateSelector'
import BasicInfoForm from '@/components/Agent/BasicInfoForm'
import ModelConfigForm from '@/components/Agent/ModelConfigForm'
import PromptConfigForm from '@/components/Agent/PromptConfigForm'
import AdvancedConfigForm from '@/components/Agent/AdvancedConfigForm'
import MCPConfigForm from '@/components/Agent/MCPConfigForm'
import BuiltInToolsForm from '@/components/Agent/BuiltInToolsForm'
import ContextCompressionForm from '@/components/Agent/ContextCompressionForm'
import ConfigPreview from '@/components/Agent/ConfigPreview'

const { Step } = Steps

const AgentCreate = () => {
  const navigate = useNavigate()
  const {
    currentStep,
    formData,
    resetFormData,
    nextStep,
    prevStep,
    setCurrentStep,
  } = useAgentFormStore()

  // 创建智能体
  const createMutation = useMutation({
    mutationFn: agentService.createAgent,
    onSuccess: (data) => {
      message.success('智能体创建成功！')
      resetFormData()
      navigate(`/agents/${data.agent_id}`)
    },
    onError: (error) => {
      message.error('智能体创建失败，请检查配置')
      console.error('Create agent error:', error)
    },
  })

  const handleNext = async () => {
    // 这里可以添加步骤验证逻辑
    nextStep()
  }

  const handlePrev = () => {
    prevStep()
  }

  const handleSubmit = () => {
    // 验证必填字段
    if (!formData.agent_metadata?.agent_id || !formData.agent_metadata?.agent_name) {
      message.error('请填写完整的智能体信息')
      return
    }
    if (!formData.model_config?.api_key) {
      message.error('请配置API密钥')
      return
    }
    if (!formData.prompt_config?.system_prompt) {
      message.error('请填写系统提示词')
      return
    }

    createMutation.mutate(formData as any)
  }

  const steps = [
    {
      title: '选择模板',
      description: '选择一个合适的模板',
      component: TemplateSelector,
    },
    {
      title: '基础信息',
      description: '配置智能体基本信息',
      component: BasicInfoForm,
    },
    {
      title: '模型配置',
      description: '选择和配置大模型',
      component: ModelConfigForm,
    },
    {
      title: '提示词配置',
      description: '设定智能体的角色和行为',
      component: PromptConfigForm,
    },
    {
      title: '高级配置',
      description: '配置工具、记忆和行为控制',
      component: AdvancedConfigForm,
    },
    {
      title: 'MCP配置',
      description: '配置Model Context Protocol服务器',
      component: MCPConfigForm,
    },
    {
      title: '内置工具',
      description: '配置和管理内置工具',
      component: BuiltInToolsForm,
    },
    {
      title: '上下文压缩',
      description: '配置上下文压缩策略',
      component: ContextCompressionForm,
    },
  ]

  const CurrentStepComponent = steps[currentStep].component

  return (
    <div>
      <Card title="创建智能体" className="mb-4">
        <Steps current={currentStep} size="small">
          {steps.map((step, index) => (
            <Step key={index} title={step.title} description={step.description} />
          ))}
        </Steps>
      </Card>

      <Card>
        <CurrentStepComponent />

        <div style={{ marginTop: 24, textAlign: 'right' }}>
          <Space>
            {currentStep > 0 && (
              <Button onClick={handlePrev} disabled={createMutation.isPending}>
                上一步
              </Button>
            )}
            {currentStep < steps.length - 1 ? (
              <Button type="primary" onClick={handleNext}>
                下一步
              </Button>
            ) : (
              <Button
                type="primary"
                onClick={handleSubmit}
                loading={createMutation.isPending}
              >
                创建智能体
              </Button>
            )}
            <Button onClick={() => navigate('/agents')} disabled={createMutation.isPending}>
              取消
            </Button>
          </Space>
        </div>
      </Card>

      {/* 配置预览 */}
      {currentStep > 0 && currentStep < steps.length - 1 && (
        <Card title="配置预览" style={{ marginTop: 16 }}>
          <ConfigPreview data={formData} />
        </Card>
      )}
    </div>
  )
}

export default AgentCreate
