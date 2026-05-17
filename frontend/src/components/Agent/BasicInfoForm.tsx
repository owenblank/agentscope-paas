import { Form, Input, Select, Space, message, Card, Typography } from 'antd'
import { useAgentFormStore } from '@/store'
import type { AgentType } from '@/types'

const { TextArea } = Input
const { Option } = Select
const { Text } = Typography

const BasicInfoForm = () => {
  const { formData, updateFormData } = useAgentFormStore()
  const [form] = Form.useForm()

  // 固定智能体类型为 ReActAgent
  const fixedAgentType: AgentType = 'ReActAgent'

  const handleFinish = (values: any) => {
    updateFormData({
      agent_metadata: {
        ...formData.agent_metadata,
        ...values,
        agent_type: fixedAgentType, // 固定为 ReActAgent
      },
    })
    message.success('基础信息保存成功')
  }

  const handleValuesChange = () => {
    const values = form.getFieldsValue()
    updateFormData({
      agent_metadata: {
        ...formData.agent_metadata,
        ...values,
        agent_type: fixedAgentType, // 固定为 ReActAgent
      },
    })
  }

  return (
    <Form
      form={form}
      layout="vertical"
      initialValues={{
        ...formData.agent_metadata,
        agent_type: fixedAgentType, // 固定为 ReActAgent
      }}
      onFinish={handleFinish}
      onValuesChange={handleValuesChange}
    >
      <Form.Item
        label="智能体名称"
        name="agent_name"
        rules={[{ required: true, message: '请输入智能体名称' }]}
      >
        <Input placeholder="例如：智能客服助手" />
      </Form.Item>

      <Form.Item
        label="智能体ID"
        name="agent_id"
        rules={[
          { required: true, message: '请输入智能体ID' },
          { pattern: /^[a-z0-9_]+$/, message: '只能包含小写字母、数字和下划线' },
        ]}
      >
        <Input placeholder="例如：customer_service_001" />
      </Form.Item>

      {/* 智能体类型 - 固定显示 */}
      <Form.Item label="智能体类型">
        <Card size="small" style={{ backgroundColor: '#f0f5ff' }}>
          <Space direction="vertical" style={{ width: '100%' }}>
            <Space>
              <Text strong>ReActAgent</Text>
              <Text type="success" style={{ fontSize: 12 }}>（推荐）</Text>
            </Space>
            <Text type="secondary" style={{ fontSize: 12 }}>
              推理行动智能体，具备复杂推理能力，适合多步骤问题解决。支持工具调用、知识库检索等高级功能。
            </Text>
          </Space>
        </Card>
        <Form.Item name="agent_type" initialValue={fixedAgentType} style={{ display: 'none' }}>
          <Input type="hidden" />
        </Form.Item>
      </Form.Item>

      <Form.Item
        label="功能描述"
        name="description"
        rules={[{ required: true, message: '请输入功能描述' }]}
      >
        <TextArea
          rows={3}
          placeholder="请描述智能体的主要功能和用途"
          maxLength={500}
          showCount
        />
      </Form.Item>

      <Form.Item label="标签" name="tags">
        <Select
          mode="tags"
          placeholder="输入标签后按回车添加"
          style={{ width: '100%' }}
          maxTagCount={5}
        >
          <Option value="客服">客服</Option>
          <Option value="中文">中文</Option>
          <Option value="英文">英文</Option>
          <Option value="代码">代码</Option>
          <Option value="分析">分析</Option>
          <Option value="推理">推理</Option>
          <Option value="工具">工具</Option>
        </Select>
      </Form.Item>
    </Form>
  )
}

export default BasicInfoForm
