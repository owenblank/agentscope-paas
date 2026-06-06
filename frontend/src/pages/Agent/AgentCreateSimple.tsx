/**
 * Simplified Agent Creation Page for Testing
 * Basic form without complex dependencies
 */
import { useState } from 'react'
import { Card, Form, Input, Button, message } from 'antd'
import { useNavigate } from 'react-router-dom'

const AgentCreateSimple = () => {
  const navigate = useNavigate()
  const [form] = Form.useForm()
  const [loading, setLoading] = useState(false)

  const onFinish = async (values: any) => {
    setLoading(true)
    try {
      console.log('Creating agent with values:', values)

      // Basic API call to test
      const response = await fetch('http://localhost:8000/api/v1/agents', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-API-Key': localStorage.getItem('auth-storage') || ''
        },
        body: JSON.stringify(values)
      })

      if (response.ok) {
        message.success('智能体创建成功！')
        navigate('/agents')
      } else {
        const error = await response.json()
        message.error(`创建失败: ${error.detail || '未知错误'}`)
      }
    } catch (error) {
      console.error('Error creating agent:', error)
      message.error('创建失败，请检查网络连接')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div style={{ padding: '24px' }}>
      <Card title="创建智能体（简化版）" style={{ maxWidth: 800, margin: '0 auto' }}>
        <Form
          form={form}
          layout="vertical"
          onFinish={onFinish}
          initialValues={{
            agent_id: `test_agent_${Date.now()}`,
            agent_name: '测试智能体',
            agent_description: '这是一个测试智能体'
          }}
        >
          <Form.Item
            label="智能体ID"
            name="agent_id"
            rules={[{ required: true, message: '请输入智能体ID' }]}
          >
            <Input placeholder="test_agent_123" />
          </Form.Item>

          <Form.Item
            label="智能体名称"
            name="agent_name"
            rules={[{ required: true, message: '请输入智能体名称' }]}
          >
            <Input placeholder="我的智能体" />
          </Form.Item>

          <Form.Item
            label="描述"
            name="agent_description"
            rules={[{ required: true, message: '请输入描述' }]}
          >
            <Input.TextArea rows={4} placeholder="智能体描述" />
          </Form.Item>

          <Form.Item
            label="API密钥"
            name="api_key"
            rules={[{ required: true, message: '请输入API密钥' }]}
          >
            <Input.Password placeholder="your-api-key" />
          </Form.Item>

          <Form.Item
            label="系统提示词"
            name="system_prompt"
            rules={[{ required: true, message: '请输入系统提示词' }]}
          >
            <Input.TextArea rows={6} placeholder="你是一个有用的助手..." />
          </Form.Item>

          <Form.Item>
            <Button type="primary" htmlType="submit" loading={loading} block>
              创建智能体
            </Button>
          </Form.Item>

          <Form.Item>
            <Button onClick={() => navigate('/agents')} block>
              取消
            </Button>
          </Form.Item>
        </Form>
      </Card>
    </div>
  )
}

export default AgentCreateSimple