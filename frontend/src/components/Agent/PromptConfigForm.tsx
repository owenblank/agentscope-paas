import { Form, Input, Button, Space, Card, Typography, Alert } from 'antd'
import { BulbOutlined } from '@ant-design/icons'
import { useAgentFormStore } from '@/store'

const { TextArea } = Input
const { Text } = Typography

const PromptConfigForm = () => {
  const { formData, updateFormData } = useAgentFormStore()
  const [form] = Form.useForm()

  const promptTemplates = [
    {
      name: '客户服务',
      template: `你是一个专业的客户服务代表，为用户提供优质的售前售后服务。

你的职责包括：
1. 产品咨询：详细介绍产品功能、规格、价格等信息
2. 订单查询：帮助用户查询订单状态、物流信息
3. 售后支持：处理退换货、投诉、技术问题等

服务原则：
- 始终保持专业、友好、耐心的态度
- 快速响应用户需求，不推诿责任
- 对于无法解决的问题，及时转人工客服`,
    },
    {
      name: '代码助手',
      template: `你是一个专业的编程助手，精通多种编程语言和技术框架。

你的职责：
1. 代码编写：根据需求编写高质量的代码
2. 代码审查：检查代码质量，提供改进建议
3. 问题调试：帮助分析和解决代码问题
4. 技术咨询：回答编程相关问题

编程原则：
- 编写清晰、可维护的代码
- 遵循最佳实践和设计模式
- 注重代码安全和性能`,
    },
    {
      name: '内容创作',
      template: `你是一个创意内容创作者，擅长各类文案写作。

你的职责：
1. 文案撰写：撰写吸引人的营销文案
2. 内容策划：规划内容结构和要点
3. 文案优化：改进现有文案效果
4. 创意建议：提供内容创作建议

创作原则：
- 内容原创，避免抄袭
- 符合目标受众喜好
- 注重阅读体验`,
    },
  ]

  const handleUseTemplate = (template: string) => {
    form.setFieldValue('system_prompt', template)
    updateFormData({
      prompt_config: {
        ...formData.prompt_config,
        system_prompt: template,
      },
    })
  }

  const handleValuesChange = () => {
    const values = form.getFieldsValue()
    updateFormData({
      prompt_config: {
        ...formData.prompt_config,
        ...values,
      },
    })
  }

  const wordCount = form.getFieldValue('system_prompt')?.length || 0

  return (
    <div>
      <Form
        form={form}
        layout="vertical"
        initialValues={formData.prompt_config}
        onValuesChange={handleValuesChange}
      >
        <Form.Item
          label="系统提示词"
          name="system_prompt"
          rules={[{ required: true, message: '请输入系统提示词' }]}
          extra={
            <Space>
              <Text type="secondary">
                设定智能体的角色、职责和行为准则，字数：{wordCount}/10000
              </Text>
            </Space>
          }
        >
          <TextArea
            rows={12}
            placeholder="输入智能体的角色设定和行为准则..."
            showCount
            maxLength={10000}
          />
        </Form.Item>

        <Card title="快速模板" size="small" style={{ marginBottom: 16 }}>
          <Space direction="vertical" style={{ width: '100%' }}>
            {promptTemplates.map((template) => (
              <Button
                key={template.name}
                onClick={() => handleUseTemplate(template.template)}
                block
              >
                <BulbOutlined /> 使用"{template.name}"模板
              </Button>
            ))}
          </Space>
        </Card>

        <Form.Item
          label="用户提示词模板（可选）"
          name="user_prompt_template"
          extra="定义用户输入的格式，可以使用 {user_input} 作为占位符"
        >
          <TextArea
            rows={3}
            placeholder="例如：用户咨询：{user_input}"
            maxLength={500}
          />
        </Form.Item>

        <Alert
          message="提示词建议"
          description="好的提示词应该包含：1.明确的角色定义 2.具体的职责描述 3.行为准则和约束条件 4.输出格式要求"
          type="info"
          showIcon
        />
      </Form>
    </div>
  )
}

export default PromptConfigForm
