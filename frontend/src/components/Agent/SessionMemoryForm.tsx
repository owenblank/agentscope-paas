import React, { useState } from 'react'
import { Form, Switch, Select, InputNumber, Input, Button, Card, Typography, Space, message, Divider } from 'antd'
import { CheckCircleOutlined, CloseCircleOutlined, LoadingOutlined } from '@ant-design/icons'
import type { SessionMemoryConfig, RedisConnectionConfig } from '@/types'

const { Option } = Select
const { Text } = Typography

interface SessionMemoryFormProps {
  value?: SessionMemoryConfig
  onChange?: (config: SessionMemoryConfig) => void
  disabled?: boolean
}

export const SessionMemoryForm: React.FC<SessionMemoryFormProps> = ({ value, onChange, disabled }) => {
  const [testResult, setTestResult] = useState<'success' | 'error' | 'testing' | null>(null)
  const [testMessage, setTestMessage] = useState<string>('')

  const handleEnabledChange = (enabled: boolean) => {
    const newConfig: SessionMemoryConfig = {
      ...(value || getDefaultConfig()),
      enabled,
    }
    onChange?.(newConfig)
  }

  const handleStorageTypeChange = (storageType: 'redis' | 'memory' | 'file') => {
    const newConfig: SessionMemoryConfig = {
      ...(value || getDefaultConfig()),
      storage_type: storageType,
      // 如果切换到Redis，确保有默认配置
      redis_config: storageType === 'redis' ? (value?.redis_config || getDefaultRedisConfig()) : undefined,
    }
    onChange?.(newConfig)
  }

  const handleRedisConfigChange = (field: keyof RedisConnectionConfig, configValue: any) => {
    const newConfig: SessionMemoryConfig = {
      ...(value || getDefaultConfig()),
      storage_type: 'redis',
      redis_config: {
        ...(value?.redis_config || getDefaultRedisConfig()),
        [field]: configValue,
      },
    }
    onChange?.(newConfig)
  }

  const handleConfigChange = (field: keyof SessionMemoryConfig, configValue: any) => {
    const newConfig: SessionMemoryConfig = {
      ...(value || getDefaultConfig()),
      [field]: configValue,
    }
    onChange?.(newConfig)
  }

  const handleTestConnection = async () => {
    if (!value?.redis_config) {
      message.error('请先配置Redis连接信息')
      return
    }

    setTestResult('testing')
    setTestMessage('正在测试连接...')

    try {
      const response = await fetch('/api/v1/test-redis', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ redis_config: value.redis_config }),
      })

      const result = await response.json()

      if (result.success) {
        setTestResult('success')
        setTestMessage('Redis连接成功！')
        message.success('Redis连接测试成功')
      } else {
        setTestResult('error')
        setTestMessage(result.message || 'Redis连接失败')
        message.error('Redis连接测试失败')
      }
    } catch (error) {
      setTestResult('error')
      setTestMessage('连接测试失败，请检查网络连接')
      message.error('连接测试失败')
    }
  }

  const currentConfig = value || getDefaultConfig()
  const isRedisEnabled = currentConfig.storage_type === 'redis'

  return (
    <Space direction="vertical" style={{ width: '100%' }} size="large">
      <Card title="会话记忆设置" size="small">
        <Form layout="vertical" disabled={disabled}>
          <Form.Item label="启用会话记忆">
            <Switch
              checked={currentConfig.enabled}
              onChange={handleEnabledChange}
              checkedChildren="启用"
              unCheckedChildren="禁用"
            />
            <div style={{ marginTop: 8, color: '#666', fontSize: 12 }}>
              启用后，智能体将记住同一会话中的对话历史，提供更连贯的交互体验
            </div>
          </Form.Item>

          {currentConfig.enabled && (
            <>
              <Form.Item label="存储类型">
                <Select
                  value={currentConfig.storage_type}
                  onChange={handleStorageTypeChange}
                  style={{ width: '100%' }}
                >
                  <Option value="redis">Redis（推荐）</Option>
                  <Option value="memory">内存存储</Option>
                  <Option value="file">文件存储</Option>
                </Select>
                <div style={{ marginTop: 8, color: '#666', fontSize: 12 }}>
                  {isRedisEnabled ? 'Redis存储支持分布式部署和高可用性' : '内存存储适用于单机环境，重启后数据丢失'}
                </div>
              </Form.Item>

              <Form.Item label={`会话过期时间 (TTL): ${currentConfig.ttl}秒`}>
                <InputNumber
                  value={currentConfig.ttl}
                  onChange={(value) => handleConfigChange('ttl', value || 3600)}
                  min={60}
                  max={86400}
                  step={60}
                  style={{ width: '100%' }}
                />
                <div style={{ marginTop: 8, color: '#666', fontSize: 12 }}>
                  会话记忆的保存时间，过期后将自动清除。60秒-86400秒（1天）
                </div>
              </Form.Item>

              <Form.Item label={`最大保存消息数: ${currentConfig.max_messages}条`}>
                <InputNumber
                  value={currentConfig.max_messages}
                  onChange={(value) => handleConfigChange('max_messages', value || 100)}
                  min={10}
                  max={1000}
                  step={10}
                  style={{ width: '100%' }}
                />
                <div style={{ marginTop: 8, color: '#666', fontSize: 12 }}>
                  单个会话最多保存的消息数量，超出后将删除最早的消息
                </div>
              </Form.Item>

              <Form.Item label="记忆键前缀">
                <Input
                  value={currentConfig.memory_key_prefix}
                  onChange={(e) => handleConfigChange('memory_key_prefix', e.target.value)}
                  placeholder="session_memory"
                />
                <div style={{ marginTop: 8, color: '#666', fontSize: 12 }}>
                  Redis存储时使用的键前缀，用于区分不同的应用或环境
                </div>
              </Form.Item>
            </>
          )}
        </Form>
      </Card>

      {currentConfig.enabled && isRedisEnabled && (
        <Card
          title="Redis连接配置"
          size="small"
          extra={
            <Button
              type="primary"
              size="small"
              onClick={handleTestConnection}
              loading={testResult === 'testing'}
              icon={
                testResult === 'success' ? (
                  <CheckCircleOutlined />
                ) : testResult === 'error' ? (
                  <CloseCircleOutlined />
                ) : testResult === 'testing' ? (
                  <LoadingOutlined />
                ) : null
              }
            >
              {testResult === 'testing' ? '测试中...' : '测试连接'}
            </Button>
          }
        >
          <Form layout="vertical" disabled={disabled}>
            <Form.Item label="主机地址">
              <Input
                value={currentConfig.redis_config?.host}
                onChange={(e) => handleRedisConfigChange('host', e.target.value)}
                placeholder="localhost"
              />
            </Form.Item>

            <Form.Item label="端口">
              <InputNumber
                value={currentConfig.redis_config?.port}
                onChange={(value) => handleRedisConfigChange('port', value || 6379)}
                min={1}
                max={65535}
                style={{ width: '100%' }}
              />
            </Form.Item>

            <Form.Item label="数据库编号">
              <InputNumber
                value={currentConfig.redis_config?.db}
                onChange={(value) => handleRedisConfigChange('db', value || 0)}
                min={0}
                max={15}
                style={{ width: '100%' }}
              />
            </Form.Item>

            <Form.Item label="密码（可选）">
              <Input.Password
                value={currentConfig.redis_config?.password}
                onChange={(e) => handleRedisConfigChange('password', e.target.value)}
                placeholder="留空表示无密码"
              />
            </Form.Item>

            <Divider orientation="left" plain>高级设置</Divider>

            <Form.Item label={`连接池大小: ${currentConfig.redis_config?.connection_pool_size}`}>
              <InputNumber
                value={currentConfig.redis_config?.connection_pool_size}
                onChange={(value) => handleRedisConfigChange('connection_pool_size', value || 10)}
                min={1}
                max={100}
                style={{ width: '100%' }}
              />
            </Form.Item>

            <Form.Item label={`Socket超时: ${currentConfig.redis_config?.socket_timeout}秒`}>
              <InputNumber
                value={currentConfig.redis_config?.socket_timeout}
                onChange={(value) => handleRedisConfigChange('socket_timeout', value || 5)}
                min={1}
                max={60}
                style={{ width: '100%' }}
              />
            </Form.Item>

            <Form.Item label={`连接超时: ${currentConfig.redis_config?.socket_connect_timeout}秒`}>
              <InputNumber
                value={currentConfig.redis_config?.socket_connect_timeout}
                onChange={(value) => handleRedisConfigChange('socket_connect_timeout', value || 5)}
                min={1}
                max={60}
                style={{ width: '100%' }}
              />
            </Form.Item>

            {testResult && (
              <div style={{ marginTop: 16 }}>
                <Text
                  type={testResult === 'success' ? 'success' : 'danger'}
                  style={{
                    display: 'block',
                    padding: '8px 12px',
                    background: testResult === 'success' ? '#f6ffed' : '#fff1f0',
                    border: `1px solid ${testResult === 'success' ? '#b7eb8f' : '#ffccc7'}`,
                    borderRadius: 4
                  }}
                >
                  {testMessage}
                </Text>
              </div>
            )}
          </Form>
        </Card>
      )}
    </Space>
  )
}

// 默认配置函数
function getDefaultConfig(): SessionMemoryConfig {
  return {
    enabled: false,
    storage_type: 'redis',
    redis_config: getDefaultRedisConfig(),
    ttl: 3600,
    max_messages: 100,
    memory_key_prefix: 'session_memory',
  }
}

function getDefaultRedisConfig(): RedisConnectionConfig {
  return {
    host: 'localhost',
    port: 6379,
    db: 0,
    password: '',
    connection_pool_size: 10,
    socket_timeout: 5,
    socket_connect_timeout: 5,
  }
}

export default SessionMemoryForm