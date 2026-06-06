import React, { useState, useEffect } from 'react'
import { Form, Input, Switch, Button, Card, Space, Select, InputNumber, message, Collapse, Tag, Tooltip, Divider, Radio } from 'antd'
import { PlusOutlined, DeleteOutlined, ApiOutlined, InfoCircleOutlined } from '@ant-design/icons'
import { useAgentFormStore } from '@/store/agentFormStore'
import type { MCPConfig, MCPServerConfig, MCPConnectionConfig } from '@/types'
import { agentService } from '@/services/agentService'

const { Option } = Select
const { TextArea } = Input
const { Panel } = Collapse

interface MCPConfigFormProps {
  className?: string
  style?: React.CSSProperties
}

const MCPConfigForm: React.FC<MCPConfigFormProps> = ({ className, style }) => {
  const { formData, updateFormData } = useAgentFormStore()
  const [form] = Form.useForm()
  const [testingConnection, setTestingConnection] = useState(false)
  const [mcpEnabled, setMcpEnabled] = useState(false)

  const mcpConfig = formData.mcp_config as MCPConfig | undefined

  useEffect(() => {
    if (mcpConfig) {
      setMcpEnabled(mcpConfig.enabled)
      form.setFieldsValue({
        mcp_enabled: mcpConfig.enabled,
        global_settings: mcpConfig.global_settings
      })
    }
  }, [mcpConfig, form])

  const handleValuesChange = () => {
    const values = form.getFieldsValue()
    const newMcpConfig: MCPConfig = {
      enabled: values.mcp_enabled || false,
      servers: mcpConfig?.servers || [],
      global_settings: values.global_settings || {
        connection_timeout: 30,
        max_concurrent_connections: 5,
        enable_tool_logging: true,
        retry_config: {
          max_retries: 3,
          backoff_multiplier: 2.0,
          initial_delay_ms: 1000
        }
      }
    }

    updateFormData({
      mcp_config: newMcpConfig
    })
  }

  const handleMcpEnabledChange = (enabled: boolean) => {
    setMcpEnabled(enabled)
    handleValuesChange()
  }

  const addServer = () => {
    const newServer: MCPServerConfig = {
      server_id: `mcp_server_${Date.now()}`,
      server_name: '',
      description: '',
      connection: {
        connection_type: 'stdio',
        timeout: 30
      },
      tools: [],
      resources: {
        max_memory_mb: 512,
        timeout_seconds: 30
      },
      permissions: {
        enabled: true,
        max_calls_per_session: 100,
        security_level: 'medium'
      }
    }

    const updatedConfig = {
      ...(mcpConfig || { enabled: mcpEnabled, servers: [], global_settings: {} }),
      servers: [...(mcpConfig?.servers || []), newServer]
    }

    updateFormData({
      mcp_config: updatedConfig
    })
  }

  const removeServer = (serverId: string) => {
    const updatedConfig = {
      ...(mcpConfig || { enabled: mcpEnabled, servers: [], global_settings: {} }),
      servers: (mcpConfig?.servers || []).filter(server => server.server_id !== serverId)
    }

    updateFormData({
      mcp_config: updatedConfig
    })
  }

  const updateServer = (serverId: string, updates: Partial<MCPServerConfig>) => {
    const updatedServers = (mcpConfig?.servers || []).map(server =>
      server.server_id === serverId ? { ...server, ...updates } : server
    )

    const updatedConfig = {
      ...(mcpConfig || { enabled: mcpEnabled, servers: [], global_settings: {} }),
      servers: updatedServers
    }

    updateFormData({
      mcp_config: updatedConfig
    })
  }

  const testConnection = async (server: MCPServerConfig) => {
    setTestingConnection(true)
    try {
      const result = await agentService.testMCPConnection(server)
      if (result.success) {
        message.success(`连接测试成功: ${result.data.latency_ms}ms`)
      } else {
        message.error(`连接测试失败: ${result.data.error || '未知错误'}`)
      }
    } catch (error) {
      message.error('连接测试失败')
    } finally {
      setTestingConnection(false)
    }
  }

  const renderConnectionForm = (server: MCPServerConfig) => {
    const connectionType = server.connection?.connection_type || 'stdio'

    return (
      <Space direction="vertical" style={{ width: '100%' }}>
        <Form.Item label="连接类型" required>
          <Select
            value={connectionType}
            onChange={(value) => updateServer(server.server_id, {
              connection: { ...server.connection, connection_type: value }
            })}
            style={{ width: '100%' }}
          >
            <Option value="stdio">标准输入输出 (stdio)</Option>
            <Option value="sse">服务器发送事件 (SSE)</Option>
            <Option value="http">HTTP 请求</Option>
          </Select>
        </Form.Item>

        {connectionType === 'stdio' && (
          <>
            <Form.Item label="命令" required>
              <Input
                value={server.connection?.command || ''}
                onChange={(e) => updateServer(server.server_id, {
                  connection: { ...server.connection, command: e.target.value }
                })}
                placeholder="例如: npx, python, node"
              />
            </Form.Item>
            <Form.Item label="参数">
              <Input
                value={server.connection?.args?.join(' ') || ''}
                onChange={(e) => updateServer(server.server_id, {
                  connection: {
                    ...server.connection,
                    args: e.target.value.split(' ').filter(arg => arg.length > 0)
                  }
                })}
                placeholder="例如: -y @modelcontextprotocol/server-filesystem /path"
              />
            </Form.Item>
          </>
        )}

        {(connectionType === 'sse' || connectionType === 'http') && (
          <Form.Item label="服务器 URL" required>
            <Input
              value={server.connection?.url || ''}
              onChange={(e) => updateServer(server.server_id, {
                connection: { ...server.connection, url: e.target.value }
              })}
              placeholder="https://your-mcp-server.com"
            />
          </Form.Item>
        )}

        <Form.Item label="连接超时 (秒)">
          <InputNumber
            value={server.connection?.timeout || 30}
            onChange={(value) => updateServer(server.server_id, {
              connection: { ...server.connection, timeout: value || 30 }
            })}
            min={1}
            max={300}
            style={{ width: '100%' }}
          />
        </Form.Item>
      </Space>
    )
  }

  const renderServerCard = (server: MCPServerConfig) => (
    <Card
      key={server.server_id}
      size="small"
      title={
        <Space>
          <span>{server.server_name || '未命名服务器'}</span>
          <Tag color={server.connection?.connection_type === 'stdio' ? 'blue' : 'green'}>
            {server.connection?.connection_type}
          </Tag>
        </Space>
      }
      extra={
        <Space>
          <Button
            type="link"
            size="small"
            icon={<ApiOutlined />}
            onClick={() => testConnection(server)}
            loading={testingConnection}
            disabled={!mcpEnabled}
          >
            测试连接
          </Button>
          <Button
            type="link"
            danger
            size="small"
            icon={<DeleteOutlined />}
            onClick={() => removeServer(server.server_id)}
            disabled={!mcpEnabled}
          >
            删除
          </Button>
        </Space>
      }
      style={{ marginBottom: 16 }}
    >
      <Space direction="vertical" style={{ width: '100%' }} size="small">
        <Form.Item label="服务器名称" required>
          <Input
            value={server.server_name}
            onChange={(e) => updateServer(server.server_id, { server_name: e.target.value })}
            placeholder="例如: 文件系统服务器"
            disabled={!mcpEnabled}
          />
        </Form.Item>

        <Form.Item label="描述">
          <TextArea
            value={server.description}
            onChange={(e) => updateServer(server.server_id, { description: e.target.value })}
            placeholder="服务器功能描述"
            rows={2}
            disabled={!mcpEnabled}
          />
        </Form.Item>

        <Divider orientation="left">连接配置</Divider>
        {renderConnectionForm(server)}

        <Divider orientation="left">工具配置</Divider>
        <Form.Item
          label={
            <Space>
              提供的工具
              <Tooltip title="此服务器提供的工具名称列表">
                <InfoCircleOutlined />
              </Tooltip>
            </Space>
          }
        >
          <Select
            mode="tags"
            value={server.tools}
            onChange={(value) => updateServer(server.server_id, { tools: value })}
            placeholder="输入工具名称并按回车添加"
            disabled={!mcpEnabled}
            style={{ width: '100%' }}
          />
        </Form.Item>

        <Divider orientation="left">资源限制</Divider>
        <Space>
          <Form.Item label="最大内存 (MB)">
            <InputNumber
              value={server.resources?.max_memory_mb || 512}
              onChange={(value) => updateServer(server.server_id, {
                resources: { ...server.resources, max_memory_mb: value || 512 }
              })}
              min={64}
              max={8192}
              disabled={!mcpEnabled}
            />
          </Form.Item>
          <Form.Item label="超时时间 (秒)">
            <InputNumber
              value={server.resources?.timeout_seconds || 30}
              onChange={(value) => updateServer(server.server_id, {
                resources: { ...server.resources, timeout_seconds: value || 30 }
              })}
              min={5}
              max={300}
              disabled={!mcpEnabled}
            />
          </Form.Item>
        </Space>

        <Divider orientation="left">权限配置</Divider>
        <Form.Item label="启用权限控制">
          <Switch
            checked={server.permissions?.enabled}
            onChange={(checked) => updateServer(server.server_id, {
              permissions: { ...server.permissions, enabled: checked }
            })}
            disabled={!mcpEnabled}
          />
        </Form.Item>

        {server.permissions?.enabled && (
          <>
            <Form.Item label="每会话最大调用次数">
              <InputNumber
                value={server.permissions?.max_calls_per_session || 100}
                onChange={(value) => updateServer(server.server_id, {
                  permissions: { ...server.permissions, max_calls_per_session: value || 100 }
                })}
                min={1}
                max={10000}
                disabled={!mcpEnabled}
              />
            </Form.Item>

            <Form.Item label="安全级别">
              <Select
                value={server.permissions?.security_level || 'medium'}
                onChange={(value) => updateServer(server.server_id, {
                  permissions: { ...server.permissions, security_level: value }
                })}
                disabled={!mcpEnabled}
                style={{ width: '100%' }}
              >
                <Option value="low">低 - 基础工具</Option>
                <Option value="medium">中 - 标准工具</Option>
                <Option value="high">高 - 敏感操作工具</Option>
              </Select>
            </Form.Item>
          </>
        )}
      </Space>
    </Card>
  )

  return (
    <div className={className} style={style}>
      <Form
        form={form}
        layout="vertical"
        onValuesChange={handleValuesChange}
        initialValues={{
          mcp_enabled: false,
          global_settings: {
            connection_timeout: 30,
            max_concurrent_connections: 5,
            enable_tool_logging: true
          }
        }}
      >
        <Form.Item label="启用 MCP 配置" valuePropName="checked">
          <Switch
            checked={mcpEnabled}
            onChange={handleMcpEnabledChange}
            checkedChildren="启用"
            unCheckedChildren="禁用"
          />
        </Form.Item>

        {mcpEnabled && (
          <>
            <Collapse defaultActiveKey={['global']} style={{ marginBottom: 16 }}>
              <Panel header="全局设置" key="global">
                <Space direction="vertical" style={{ width: '100%' }}>
                  <Form.Item label="连接超时 (秒)">
                    <InputNumber
                      name={['global_settings', 'connection_timeout']}
                      min={5}
                      max={300}
                      style={{ width: '100%' }}
                    />
                  </Form.Item>

                  <Form.Item label="最大并发连接数">
                    <InputNumber
                      name={['global_settings', 'max_concurrent_connections']}
                      min={1}
                      max={50}
                      style={{ width: '100%' }}
                    />
                  </Form.Item>

                  <Form.Item
                    label="启用工具日志"
                    valuePropName="checked"
                    name={['global_settings', 'enable_tool_logging']}
                  >
                    <Switch />
                  </Form.Item>
                </Space>
              </Panel>
            </Collapse>

            <div style={{ marginBottom: 16 }}>
              <Space>
                <Button
                  type="dashed"
                  icon={<PlusOutlined />}
                  onClick={addServer}
                  block
                >
                  添加 MCP 服务器
                </Button>
              </Space>
            </div>

            {mcpConfig?.servers.map(server => renderServerCard(server))}

            {(!mcpConfig?.servers || mcpConfig.servers.length === 0) && (
              <Card style={{ textAlign: 'center', padding: '40px 0' }}>
                <p style={{ color: '#999', marginBottom: 16 }}>
                  尚未配置 MCP 服务器
                </p>
                <Button type="primary" icon={<PlusOutlined />} onClick={addServer}>
                  添加第一个服务器
                </Button>
              </Card>
            )}
          </>
        )}
      </Form>
    </div>
  )
}

export default MCPConfigForm