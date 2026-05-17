import { useState } from 'react'
import {
  Form,
  Input,
  Select,
  Slider,
  Button,
  Space,
  Card,
  Typography,
  Divider,
  message,
  Tag,
  Alert,
} from 'antd'
import { CheckCircleOutlined, CloseCircleOutlined } from '@ant-design/icons'
import { useAgentFormStore } from '@/store'
import { agentService } from '@/services'

const { Option } = Select
const { Text } = Typography

const ModelConfigForm = () => {
  const { formData, updateFormData, setCostEstimate } = useAgentFormStore()
  const [connectionStatus, setConnectionStatus] = useState<'idle' | 'testing' | 'success' | 'failed'>('idle')
  const [testing, setTesting] = useState(false)

  const [form] = Form.useForm()

  const modelProviders = [
    {
      name: 'OpenAI',
      models: [
        { name: 'gpt-4o', label: 'GPT-4o', recommended: true },
        { name: 'gpt-4o-mini', label: 'GPT-4o Mini', cost_effective: true },
        { name: 'gpt-4-turbo', label: 'GPT-4 Turbo' },
        { name: 'gpt-3.5-turbo', label: 'GPT-3.5 Turbo' },
      ],
      baseUrl: 'https://api.openai.com/v1',
    },
    {
      name: 'Anthropic',
      models: [
        { name: 'claude-3-5-sonnet-20241022', label: 'Claude 3.5 Sonnet', recommended: true },
        { name: 'claude-3-opus-20240229', label: 'Claude 3 Opus' },
        { name: 'claude-3-sonnet-20240229', label: 'Claude 3 Sonnet', cost_effective: true },
      ],
      baseUrl: 'https://api.anthropic.com',
    },
    {
      name: '通义千问',
      models: [
        { name: 'qwen-turbo', label: '通义千问 Turbo', cost_effective: true, recommended: true },
        { name: 'qwen-plus', label: '通义千问 Plus' },
        { name: 'qwen-max', label: '通义千问 Max' },
      ],
      baseUrl: 'https://dashscope.aliyuncs.com/compatible-mode/v1',
    },
  ]

  const selectedProvider = Form.useWatch('provider', form)

  const handleTestConnection = async () => {
    const values = form.getFieldsValue()
    if (!values.api_key) {
      message.error('请先输入API密钥')
      return
    }

    setTesting(true)
    setConnectionStatus('testing')

    try {
      const result = await agentService.testConnection({
        model_name: values.model_name,
        api_key: values.api_key,
        base_url: values.base_url,
      })

      if (result.connection_status === 'success') {
        setConnectionStatus('success')
        message.success('连接测试成功')
      } else {
        setConnectionStatus('failed')
        message.error('连接测试失败')
      }
    } catch (error) {
      setConnectionStatus('failed')
      message.error('连接测试失败')
    } finally {
      setTesting(false)
    }
  }

  const handleEstimateCost = async () => {
    const values = form.getFieldsValue()
    if (!values.model_name) {
      message.error('请先选择模型')
      return
    }

    try {
      const estimate = await agentService.estimateCost(
        {
          model_config: {
            model_name: values.model_name,
            max_tokens: values.max_tokens,
          },
        },
        {
          daily_conversations: 100,
          avg_turns_per_conversation: 10,
        }
      )
      setCostEstimate(estimate)
    } catch (error) {
      message.error('成本估算失败')
    }
  }

  const handleValuesChange = () => {
    const values = form.getFieldsValue()
    updateFormData({
      model_config: {
        ...formData.model_config,
        ...values,
      },
    })

    // 当模型或tokens改变时重新估算成本
    if (values.model_name && values.max_tokens) {
      handleEstimateCost()
    }
  }

  const currentProvider = modelProviders.find((p) => p.name === selectedProvider)

  return (
    <Form
      form={form}
      layout="vertical"
      initialValues={formData.model_config}
      onValuesChange={handleValuesChange}
    >
      <Form.Item label="模型服务商" name="provider" initialValue="OpenAI">
        <Select>
          {modelProviders.map((provider) => (
            <Option key={provider.name} value={provider.name}>
              {provider.name}
            </Option>
          ))}
        </Select>
      </Form.Item>

      <Form.Item label="模型版本" name="model_name" rules={[{ required: true, message: '请选择模型' }]}>
        <Select placeholder="选择模型版本">
          {currentProvider?.models.map((model) => (
            <Option key={model.name} value={model.name}>
              <Space>
                {model.label}
                {model.recommended && <Tag color="green">推荐</Tag>}
                {model.cost_effective && <Tag color="blue">经济</Tag>}
              </Space>
            </Option>
          ))}
        </Select>
      </Form.Item>

      <Form.Item
        label="API密钥"
        name="api_key"
        rules={[{ required: true, message: '请输入API密钥' }]}
        extra={
          <Space>
            <Button size="small" onClick={handleTestConnection} loading={testing}>
              测试连接
            </Button>
            {connectionStatus === 'success' && (
              <Text type="success">
                <CheckCircleOutlined /> 连接成功
              </Text>
            )}
            {connectionStatus === 'failed' && (
              <Text type="danger">
                <CloseCircleOutlined /> 连接失败
              </Text>
            )}
          </Space>
        }
      >
        <Input.Password placeholder="sk-..." />
      </Form.Item>

      <Form.Item
        label="API端点"
        name="base_url"
        initialValue={modelProviders[0].baseUrl}
        rules={[{ required: true, message: '请输入API端点' }]}
        extra="从模型服务商获取的API基础地址"
      >
        <Input placeholder="https://api.openai.com/v1" />
      </Form.Item>

      <Divider />

      <Card title="高级参数" size="small" style={{ marginBottom: 16 }}>
        <Form.Item
          label={
            <Space>
              <span>温度</span>
              <Text type="secondary">({Form.useWatch('temperature', form)})</Text>
            </Space>
          }
          name="temperature"
          initialValue={0.7}
          extra="控制输出随机性，0.0为确定性，1.0为平衡，2.0为高创造性"
        >
          <Slider min={0} max={2} step={0.1} marks={{ 0: '精确', 1: '平衡', 2: '创意' }} />
        </Form.Item>

        <Form.Item
          label={
            <Space>
              <span>最大Token数</span>
              <Text type="secondary">({Form.useWatch('max_tokens', form)})</Text>
            </Space>
          }
          name="max_tokens"
          initialValue={2000}
          extra="单次回复的最大长度"
        >
          <Slider min={100} max={8000} step={100} marks={{ 500: '短', 2000: '中', 4000: '长' }} />
        </Form.Item>

        <Form.Item label="Top-P" name="top_p" initialValue={0.9}>
          <Slider min={0} max={1} step={0.05} />
        </Form.Item>
      </Card>

      {formData.model_config?.model_name && (
        <Alert
          message="成本提示"
          description="每次对话的成本会根据选择的模型和设置有所不同"
          type="info"
          showIcon
        />
      )}
    </Form>
  )
}

export default ModelConfigForm
