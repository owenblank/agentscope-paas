import { Card, Descriptions, Button, Space, Tag, Typography } from 'antd'
import { useParams, useNavigate } from 'react-router-dom'
import { useQuery } from '@tanstack/react-query'
import { agentService } from '@/services'
import dayjs from 'dayjs'

const { Title, Paragraph } = Typography

const AgentDetail = () => {
  const { agentId } = useParams<{ agentId: string }>()
  const navigate = useNavigate()

  const { data: agent, isLoading } = useQuery({
    queryKey: ['agent', agentId],
    queryFn: () => agentService.getAgent(agentId!),
    enabled: !!agentId,
  })

  if (isLoading) {
    return <Card loading />
  }

  if (!agent) {
    return (
      <Card>
        <div>智能体不存在</div>
      </Card>
    )
  }

  return (
    <div>
      <Card>
        <div className="flex justify-between items-center mb-4">
          <Title level={2}>{agent.agent_name}</Title>
          <Space>
            <Button onClick={() => navigate(`/agents/${agentId}/edit`)}>编辑</Button>
            <Button type="primary">开始对话</Button>
          </Space>
        </div>

        <Descriptions column={2} bordered>
          <Descriptions.Item label="智能体ID">{agent.agent_id}</Descriptions.Item>
          <Descriptions.Item label="状态">
            <Tag color={agent.status === 'running' ? 'green' : 'default'}>
              {agent.status === 'running' ? '运行中' : '已停止'}
            </Tag>
          </Descriptions.Item>
          <Descriptions.Item label="类型">{agent.agent_type}</Descriptions.Item>
          <Descriptions.Item label="模型">{agent.config.model_config.model_name}</Descriptions.Item>
          <Descriptions.Item label="描述" span={2}>
            {agent.description}
          </Descriptions.Item>
          <Descriptions.Item label="标签" span={2}>
            {agent.config.agent_metadata.tags?.map((tag) => (
              <Tag key={tag} color="blue">
                {tag}
              </Tag>
            ))}
          </Descriptions.Item>
          <Descriptions.Item label="创建时间">
            {dayjs(agent.created_at).format('YYYY-MM-DD HH:mm:ss')}
          </Descriptions.Item>
          <Descriptions.Item label="更新时间">
            {dayjs(agent.updated_at).format('YYYY-MM-DD HH:mm:ss')}
          </Descriptions.Item>
        </Descriptions>

        <div className="mt-4">
          <Title level={4}>统计信息</Title>
          <Descriptions column={4}>
            <Descriptions.Item label="总对话数">
              {agent.statistics.total_conversations}
            </Descriptions.Item>
            <Descriptions.Item label="总Tokens">
              {agent.statistics.total_tokens_used}
            </Descriptions.Item>
            <Descriptions.Item label="总成本">
              ${agent.statistics.total_cost.toFixed(2)}
            </Descriptions.Item>
            <Descriptions.Item label="成功率">
              {(agent.statistics.success_rate * 100).toFixed(1)}%
            </Descriptions.Item>
          </Descriptions>
        </div>

        <div className="mt-4">
          <Title level={4}>系统提示词</Title>
          <Card>
            <pre style={{ whiteSpace: 'pre-wrap', fontFamily: 'inherit' }}>
              {agent.config.prompt_config.system_prompt}
            </pre>
          </Card>
        </div>
      </Card>
    </div>
  )
}

export default AgentDetail
