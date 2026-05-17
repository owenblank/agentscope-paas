import { Card, Row, Col, Button, Tag, Typography, Space } from 'antd'
import { RocketOutlined, ThunderboltOutlined, CodeOutlined, CustomerServiceOutlined } from '@ant-design/icons'
import { useQuery } from '@tanstack/react-query'
import { templateService } from '@/services'
import { useAgentFormStore } from '@/store'
import type { Template } from '@/types'

const { Title, Text } = Typography

const TemplateSelector = () => {
  const { setSelectedTemplate, nextStep } = useAgentFormStore()

  const { data: templates, isLoading } = useQuery({
    queryKey: ['templates'],
    queryFn: () => templateService.getTemplates(),
  })

  const popularTemplates: Array<{
    id: string
    name: string
    description: string
    icon: React.ReactNode
    difficulty: 'beginner' | 'intermediate' | 'advanced'
    tags: string[]
  }> = [
    {
      id: 'simple_chatbot',
      name: '简单聊天机器人',
      description: '60行极简配置，适合新手入门',
      icon: <RocketOutlined style={{ fontSize: 32, color: '#52c41a' }} />,
      difficulty: 'beginner',
      tags: ['聊天', '对话', '新手'],
    },
    {
      id: 'customer_service',
      name: '智能客服助手',
      description: '200行生产级配置，包含工具集成',
      icon: <CustomerServiceOutlined style={{ fontSize: 32, color: '#1890ff' }} />,
      difficulty: 'intermediate',
      tags: ['客服', '工具', '生产级'],
    },
    {
      id: 'dev_team',
      name: '软件开发团队',
      description: '450行复杂配置，多智能体协作',
      icon: <CodeOutlined style={{ fontSize: 32, color: '#722ed1' }} />,
      difficulty: 'advanced',
      tags: ['开发', '团队', '协作'],
    },
  ]

  const handleSelectTemplate = (templateId: string) => {
    setSelectedTemplate(templateId)
    nextStep()
  }

  const handleSkipTemplate = () => {
    setSelectedTemplate(null)
    nextStep()
  }

  return (
    <div>
      <Title level={4}>选择一个模板快速开始</Title>
      <Text type="secondary">模板提供了预配置的设置，可以加快您的智能体创建过程</Text>

      <Row gutter={[16, 16]} style={{ marginTop: 24 }}>
        {popularTemplates.map((template) => (
          <Col xs={24} md={8} key={template.id}>
            <Card
              hoverable
              onClick={() => handleSelectTemplate(template.id)}
              style={{ height: '100%' }}
            >
              <div style={{ textAlign: 'center', marginBottom: 16 }}>
                {template.icon}
              </div>
              <Title level={4} style={{ textAlign: 'center' }}>
                {template.name}
              </Title>
              <Text type="secondary" style={{ display: 'block', textAlign: 'center', marginBottom: 16 }}>
                {template.description}
              </Text>
              <div style={{ textAlign: 'center', marginBottom: 16 }}>
                {template.tags.map((tag) => (
                  <Tag key={tag} color="blue" style={{ margin: 4 }}>
                    {tag}
                  </Tag>
                ))}
              </div>
              <div style={{ textAlign: 'center' }}>
                <Tag color={
                  template.difficulty === 'beginner' ? 'green' :
                  template.difficulty === 'intermediate' ? 'blue' : 'purple'
                }>
                  {template.difficulty === 'beginner' ? '⭐ 新手' :
                   template.difficulty === 'intermediate' ? '⭐⭐ 进阶' : '⭐⭐⭐ 高级'}
                </Tag>
              </div>
            </Card>
          </Col>
        ))}
      </Row>

      <div style={{ textAlign: 'center', marginTop: 24 }}>
        <Space>
          <Button type="default" onClick={handleSkipTemplate}>
            跳过，从零开始
          </Button>
        </Space>
      </div>
    </div>
  )
}

export default TemplateSelector
