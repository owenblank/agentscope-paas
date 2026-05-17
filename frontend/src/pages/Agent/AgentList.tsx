import { useState } from 'react'
import {
  Card,
  Table,
  Button,
  Input,
  Space,
  Tag,
  Popconfirm,
  message,
  Typography,
  Tooltip,
  Alert,
} from 'antd'
import {
  PlusOutlined,
  SearchOutlined,
  PlayCircleOutlined,
  StopOutlined,
  DeleteOutlined,
  EyeOutlined,
  EditOutlined,
  CloudServerOutlined,
} from '@ant-design/icons'
import { useNavigate } from 'react-router-dom'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { agentService } from '@/services'
import type { Agent, AgentStatus } from '@/types'
import { useAppStore } from '@/store'
import dayjs from 'dayjs'
import relativeTime from 'dayjs/plugin/relativeTime'
import 'dayjs/locale/zh-cn'

dayjs.extend(relativeTime)
dayjs.locale('zh-cn')

const { Search } = Input
const { Text } = Typography

const AgentList = () => {
  const navigate = useNavigate()
  const queryClient = useQueryClient()
  const { user } = useAppStore()
  const [searchText, setSearchText] = useState('')
  const [pagination, setPagination] = useState({ current: 1, pageSize: 10 })

  // Mock数据
  const mockAgents: Agent[] = [
    {
      id: '1',
      agent_id: 'demo_agent_001',
      agent_name: '示例客服助手',
      agent_type: 'ReActAgent',
      description: '这是一个演示用的智能客服助手',
      status: 'running',
      config: {} as any,
      statistics: {
        total_conversations: 156,
        total_tokens_used: 123456,
        total_cost: 2.34,
        average_response_time: 1.2,
        success_rate: 98.5,
      },
      created_at: new Date().toISOString(),
      updated_at: new Date().toISOString(),
    },
    {
      id: '2',
      agent_id: 'demo_agent_002',
      agent_name: '示例代码助手',
      agent_type: 'ReActAgent',
      description: '这是一个演示用的编程助手',
      status: 'stopped',
      config: {} as any,
      statistics: {
        total_conversations: 89,
        total_tokens_used: 67890,
        total_cost: 1.23,
        average_response_time: 0.8,
        success_rate: 95.0,
      },
      created_at: new Date(Date.now() - 86400000).toISOString(),
      updated_at: new Date(Date.now() - 86400000).toISOString(),
    },
    {
      id: '3',
      agent_id: 'demo_agent_003',
      agent_name: '示例数据分析助手',
      agent_type: 'ReActAgent',
      description: '这是一个演示用的数据分析助手',
      status: 'created',
      config: {} as any,
      statistics: {
        total_conversations: 0,
        total_tokens_used: 0,
        total_cost: 0,
        average_response_time: 0,
        success_rate: 0,
      },
      created_at: new Date(Date.now() - 172800000).toISOString(),
      updated_at: new Date(Date.now() - 172800000).toISOString(),
    },
  ]

  // 获取智能体列表，添加错误处理
  const { data: agentsData, error, isLoading } = useQuery({
    queryKey: ['agents', pagination.current, pagination.pageSize],
    queryFn: async () => {
      try {
        return await agentService.getAgents({
          page: pagination.current,
          limit: pagination.pageSize,
        })
      } catch (err) {
        console.log('使用示例数据')
        return { agents: mockAgents, pagination: { total: 3, page: 1, limit: 10, pages: 1 } }
      }
    },
    refetchInterval: false,
    retry: false,
  })

  // 使用真实数据或mock数据
  const agents = error || !agentsData ? mockAgents : agentsData.agents
  const hasError = !!error

  // 启动智能体
  const startMutation = useMutation({
    mutationFn: agentService.startAgent,
    onSuccess: () => {
      message.success('智能体启动成功')
      queryClient.invalidateQueries({ queryKey: ['agents'] })
    },
    onError: () => {
      message.error('智能体启动失败')
    },
  })

  // 停止智能体
  const stopMutation = useMutation({
    mutationFn: agentService.stopAgent,
    onSuccess: () => {
      message.success('智能体停止成功')
      queryClient.invalidateQueries({ queryKey: ['agents'] })
    },
    onError: () => {
      message.error('智能体停止失败')
    },
  })

  // 删除智能体
  const deleteMutation = useMutation({
    mutationFn: agentService.deleteAgent,
    onSuccess: () => {
      message.success('智能体删除成功')
      queryClient.invalidateQueries({ queryKey: ['agents'] })
    },
    onError: () => {
      message.error('智能体删除失败')
    },
  })

  const handleStart = (agentId: string) => {
    startMutation.mutate(agentId)
  }

  const handleStop = (agentId: string) => {
    stopMutation.mutate(agentId)
  }

  const handleDelete = (agentId: string) => {
    deleteMutation.mutate(agentId)
  }

  const getStatusColor = (status: AgentStatus) => {
    const colors = {
      running: 'green',
      stopped: 'default',
      created: 'blue',
      error: 'red',
    }
    return colors[status] || 'default'
  }

  const getStatusText = (status: AgentStatus) => {
    const texts = {
      running: '运行中',
      stopped: '已停止',
      created: '已创建',
      error: '错误',
    }
    return texts[status] || status
  }

  const columns = [
    {
      title: '智能体名称',
      dataIndex: 'agent_name',
      key: 'agent_name',
      render: (text: string, record: Agent) => (
        <Space>
          <span>{text}</span>
          {record.tags?.map((tag) => (
            <Tag key={tag} color="blue">
              {tag}
            </Tag>
          ))}
        </Space>
      ),
    },
    {
      title: '类型',
      dataIndex: 'agent_type',
      key: 'agent_type',
      render: (type: string) => {
        const typeMap: Record<string, string> = {
          ReActAgent: '推理行动智能体',
        }
        return typeMap[type] || type
      },
    },
    {
      title: '状态',
      dataIndex: 'status',
      key: 'status',
      render: (status: AgentStatus) => (
        <Tag color={getStatusColor(status)}>{getStatusText(status)}</Tag>
      ),
    },
    {
      title: '模型',
      dataIndex: ['config', 'model_config', 'model_name'],
      key: 'model_name',
    },
    {
      title: '对话数',
      dataIndex: ['statistics', 'total_conversations'],
      key: 'conversations',
      render: (count: number) => count?.toLocaleString() || 0,
    },
    {
      title: '创建时间',
      dataIndex: 'created_at',
      key: 'created_at',
      render: (date: string) => (
        <Tooltip title={dayjs(date).format('YYYY-MM-DD HH:mm:ss')}>
          <Text>{dayjs(date).fromNow()}</Text>
        </Tooltip>
      ),
    },
    {
      title: '操作',
      key: 'actions',
      render: (_: unknown, record: Agent) => (
        <Space>
          <Button
            type="text"
            icon={<EyeOutlined />}
            onClick={() => navigate(`/agents/${record.agent_id}`)}
          >
            查看
          </Button>
          <Button
            type="text"
            icon={<EditOutlined />}
            onClick={() => navigate(`/agents/${record.agent_id}/edit`)}
          >
            编辑
          </Button>
          {record.status === 'running' ? (
            <Button
              type="text"
              danger
              icon={<StopOutlined />}
              onClick={() => handleStop(record.agent_id)}
              loading={stopMutation.isPending}
            >
              停止
            </Button>
          ) : (
            <Button
              type="text"
              icon={<PlayCircleOutlined />}
              onClick={() => handleStart(record.agent_id)}
              loading={startMutation.isPending}
            >
              启动
            </Button>
          )}
          <Popconfirm
            title="确定要删除这个智能体吗？"
            onConfirm={() => handleDelete(record.agent_id)}
            okText="确定"
            cancelText="取消"
          >
            <Button
              type="text"
              danger
              icon={<DeleteOutlined />}
              loading={deleteMutation.isPending}
            >
              删除
            </Button>
          </Popconfirm>
        </Space>
      ),
    },
  ]

  return (
    <div>
      {/* 演示模式提示 */}
      {hasError && (
        <Alert
          message="演示模式"
          description="后端服务未连接，当前显示的是示例数据。启动后端服务以获取真实数据。"
          type="info"
          showIcon
          closable
          style={{ marginBottom: 16 }}
          icon={<CloudServerOutlined />}
        />
      )}
      <Card
      title="我的智能体"
      extra={
        <Button
          type="primary"
          icon={<PlusOutlined />}
          onClick={() => navigate('/agents/create')}
        >
          创建智能体
        </Button>
      }
    >
      <Space style={{ marginBottom: 16 }} size="middle">
        <Search
          placeholder="搜索智能体名称或标签"
          allowClear
          style={{ width: 300 }}
          onSearch={setSearchText}
        />
      </Space>

      <Table
        columns={columns}
        dataSource={agents}
        loading={isLoading}
        rowKey="agent_id"
        pagination={{
          current: pagination.current,
          pageSize: pagination.pageSize,
          total: agentsData?.pagination.total || 0,
          showSizeChanger: true,
          showQuickJumper: true,
          showTotal: (total) => `共 ${total} 个智能体`,
          onChange: (page, pageSize) =>
            setPagination({ current: page, pageSize: pageSize || 10 }),
        }}
      />
    </Card>
    </div>
  )
}

export default AgentList
