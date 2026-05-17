import { Row, Col, Card, Statistic, Button, List, Typography, Tag, Alert } from 'antd'
import {
  RobotOutlined,
  MessageOutlined,
  DollarOutlined,
  ArrowUpOutlined,
  PlusOutlined,
  CloudServerOutlined,
} from '@ant-design/icons'
import { useNavigate } from 'react-router-dom'
import { useQuery } from '@tanstack/react-query'
import { agentService } from '@/services'
import { useAppStore } from '@/store'

const { Title, Text, Paragraph } = Typography

const Dashboard = () => {
  const navigate = useNavigate()
  const { user } = useAppStore()

  // Mock数据用于演示
  const mockAgents = [
    {
      agent_id: 'demo_agent_001',
      agent_name: '示例客服助手',
      agent_type: 'ReActAgent',
      description: '这是一个演示用的智能客服助手',
      status: 'running',
      created_at: new Date().toISOString(),
      tags: ['示例', '客服'],
    },
    {
      agent_id: 'demo_agent_002',
      agent_name: '示例代码助手',
      agent_type: 'ReActAgent',
      description: '这是一个演示用的编程助手',
      status: 'stopped',
      created_at: new Date(Date.now() - 86400000).toISOString(),
      tags: ['示例', '编程'],
    },
  ]

  // 获取智能体列表，添加错误处理
  const { data: agentsData, error, isLoading } = useQuery({
    queryKey: ['agents', 'dashboard'],
    queryFn: async () => {
      try {
        return await agentService.getAgents({ limit: 5 })
      } catch (err) {
        console.log('使用示例数据演示')
        return { agents: mockAgents, pagination: { total: 2 } }
      }
    },
    refetchInterval: false,
    retry: false,
  })

  // 使用真实数据或mock数据
  const agents = error || !agentsData ? mockAgents : agentsData.agents
  const hasError = !!error

  // 统计数据
  const stats = {
    activeAgents: agents.filter((a) => a.status === 'running').length,
    totalConversations: 1234,
    todayTokens: 45678,
    todayCost: 12.34,
  }

  const quickActions = [
    {
      title: '创建智能体',
      icon: <RobotOutlined style={{ fontSize: 24, color: '#1890ff' }} />,
      description: '快速创建一个新的AI智能体',
      action: () => navigate('/agents/create'),
    },
    {
      title: '创建团队',
      icon: <MessageOutlined style={{ fontSize: 24, color: '#52c41a' }} />,
      description: '组建多智能体协作团队',
      action: () => navigate('/teams/create'),
    },
    {
      title: '查看监控',
      icon: <DollarOutlined style={{ fontSize: 24, color: '#faad14' }} />,
      description: '查看使用统计和成本分析',
      action: () => navigate('/monitoring'),
    },
  ]

  return (
    <div>
      <div style={{ marginBottom: 24 }}>
        <Title level={2}>欢迎回来，{user?.username || '用户'}！</Title>
        <Text type="secondary">这是您的AgentScope PaaS控制台</Text>
      </div>

      {/* 演示模式提示 */}
      {hasError && (
        <Alert
          message="演示模式"
          description="后端服务未连接，当前显示的是示例数据。启动后端服务以获取真实数据。"
          type="info"
          showIcon
          closable
          style={{ marginBottom: 24 }}
          icon={<CloudServerOutlined />}
        />
      )}

      {/* 统计卡片 */}
      <Row gutter={[16, 16]} style={{ marginBottom: 24 }}>
        <Col xs={24} sm={12} lg={6}>
          <Card>
            <Statistic
              title="活跃智能体"
              value={stats.activeAgents}
              prefix={<RobotOutlined />}
              valueStyle={{ color: '#3f8600' }}
            />
          </Card>
        </Col>
        <Col xs={24} sm={12} lg={6}>
          <Card>
            <Statistic
              title="总对话数"
              value={stats.totalConversations}
              prefix={<MessageOutlined />}
              suffix="次"
            />
          </Card>
        </Col>
        <Col xs={24} sm={12} lg={6}>
          <Card>
            <Statistic
              title="今日Tokens"
              value={stats.todayTokens}
              prefix={<ArrowUpOutlined />}
              valueStyle={{ color: '#1890ff' }}
            />
          </Card>
        </Col>
        <Col xs={24} sm={12} lg={6}>
          <Card>
            <Statistic
              title="今日成本"
              value={stats.todayCost}
              prefix={<DollarOutlined />}
              suffix="USD"
              precision={2}
              valueStyle={{ color: '#cf1322' }}
            />
          </Card>
        </Col>
      </Row>

      {/* 快速操作 */}
      <Row gutter={[16, 16]} style={{ marginBottom: 24 }}>
        <Col span={24}>
          <Card title="快速操作" extra={<Button type="link">更多</Button>}>
            <Row gutter={[16, 16]}>
              {quickActions.map((action, index) => (
                <Col xs={24} md={8} key={index}>
                  <Card
                    hoverable
                    onClick={action.action}
                    style={{ textAlign: 'center', height: '100%' }}
                  >
                    <div style={{ marginBottom: 16 }}>{action.icon}</div>
                    <Title level={4}>{action.title}</Title>
                    <Text type="secondary">{action.description}</Text>
                  </Card>
                </Col>
              ))}
            </Row>
          </Card>
        </Col>
      </Row>

      <Row gutter={[16, 16]}>
        {/* 最近使用的智能体 */}
        <Col xs={24} lg={12}>
          <Card
            title="最近使用的智能体"
            extra={
              <Button
                type="primary"
                icon={<PlusOutlined />}
                size="small"
                onClick={() => navigate('/agents/create')}
              >
                新建
              </Button>
            }
          >
            <List
              dataSource={agents.slice(0, 5)}
              renderItem={(agent: any) => (
                <List.Item
                  actions={[
                    <Button
                      type="link"
                      onClick={() => navigate(`/agents/${agent.agent_id}`)}
                    >
                      查看
                    </Button>,
                  ]}
                >
                  <List.Item.Meta
                    avatar={<RobotOutlined style={{ fontSize: 24, color: '#1890ff' }} />}
                    title={agent.agent_name}
                    description={
                      <div>
                        <Tag color={agent.status === 'running' ? 'green' : 'default'}>
                          {agent.status === 'running' ? '运行中' : '已停止'}
                        </Tag>
                        <Text type="secondary" style={{ marginLeft: 8 }}>
                          {agent.description}
                        </Text>
                      </div>
                    }
                  />
                </List.Item>
              )}
            />
          </Card>
        </Col>

        {/* 系统通知 */}
        <Col xs={24} lg={12}>
          <Card title="系统通知" extra={<Button type="link">全部</Button>}>
            <List
              dataSource={[
                {
                  title: '欢迎使用AgentScope PaaS',
                  description: '开始创建您的第一个AI智能体吧',
                  time: '刚刚',
                },
                {
                  title: '新功能上线',
                  description: '支持多智能体团队协作模式',
                  time: '1小时前',
                },
                {
                  title: '系统维护通知',
                  description: '系统将于今晚22:00-23:00进行维护',
                  time: '2小时前',
                },
              ]}
              renderItem={(item: any) => (
                <List.Item>
                  <List.Item.Meta
                    title={item.title}
                    description={
                      <div>
                        <div>{item.description}</div>
                        <Text type="secondary" style={{ fontSize: 12 }}>
                          {item.time}
                        </Text>
                      </div>
                    }
                  />
                </List.Item>
              )}
            />
          </Card>
        </Col>
      </Row>
    </div>
  )
}

export default Dashboard
