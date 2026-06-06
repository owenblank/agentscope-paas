/**
 * Runtime Status Panel Component
 *
 * Displays comprehensive deployment status, health monitoring, and activity
 * information for Runtime-deployed agents.
 */

import React, { useState, useEffect } from 'react'
import {
  Card,
  Badge,
  Tag,
  Space,
  Typography,
  Row,
  Col,
  Statistic,
  Progress,
  Alert,
  Button,
  Tooltip,
  Divider,
  Timeline,
  Descriptions,
  Spin
} from 'antd'
import {
  CheckCircleOutlined,
  ExclamationCircleOutlined,
  CloseCircleOutlined,
  ClockCircleOutlined,
  ThunderboltOutlined,
  SyncOutlined,
  CloudServerOutlined,
  ReloadOutlined,
  StopOutlined,
  PlayCircleOutlined,
  WarningOutlined
} from '@ant-design/icons'
import type { RuntimeDeploymentStatus } from '@/types/agent'
import { formatDuration, formatDate } from '@/utils/format'

const { Text, Title, Paragraph } = Typography

interface RuntimeStatusPanelProps {
  agentId: string
  deploymentStatus: RuntimeDeploymentStatus | null
  loading?: boolean
  onRefresh?: () => void
  onStop?: () => void
  onRestart?: () => void
  onDeploy?: () => void
  className?: string
}

const RuntimeStatusPanel: React.FC<RuntimeStatusPanelProps> = ({
  agentId,
  deploymentStatus,
  loading = false,
  onRefresh,
  onStop,
  onRestart,
  onDeploy,
  className = ''
}) => {
  const [currentTime, setCurrentTime] = useState(new Date())

  useEffect(() => {
    const timer = setInterval(() => setCurrentTime(new Date()), 1000)
    return () => clearInterval(timer)
  }, [])

  if (!deploymentStatus) {
    return (
      <Card className={`runtime-status-panel ${className}`}>
        <Alert
          message="No Deployment Information"
          description="Runtime deployment status is not available for this agent."
          type="info"
          showIcon
        />
      </Card>
    )
  }

  const getStatusIcon = (status: RuntimeDeploymentStatus['deployment_status']) => {
    switch (status) {
      case 'deployed':
        return <CheckCircleOutlined style={{ color: '#52c41a' }} />
      case 'deploying':
        return <LoadingOutlined />
      case 'stopping':
        return <LoadingOutlined />
      case 'stopped':
        return <CloseCircleOutlined style={{ color: '#faad14' }} />
      case 'error':
        return <ExclamationCircleOutlined style={{ color: '#ff4d4f' }} />
      default:
        return <ClockCircleOutlined style={{ color: '#d9d9d9' }} />
    }
  }

  const getStatusColor = (status: RuntimeDeploymentStatus['deployment_status']) => {
    switch (status) {
      case 'deployed':
        return 'success'
      case 'deploying':
        return 'processing'
      case 'stopping':
        return 'warning'
      case 'stopped':
        return 'default'
      case 'error':
        return 'error'
      default:
        return 'default'
    }
  }

  const getHealthStatusIcon = (health: RuntimeDeploymentStatus['health_status']) => {
    switch (health) {
      case 'healthy':
        return <SyncOutlined style={{ color: '#52c41a' }} />
      case 'unhealthy':
        return <WarningOutlined style={{ color: '#faad14' }} />
      case 'error':
        return <CloseCircleOutlined style={{ color: '#ff4d4f' }} />
      default:
        return <ExclamationCircleOutlined style={{ color: '#d9d9d9' }} />
    }
  }

  const calculateUptimePercentage = () => {
    if (deploymentStatus.uptime_minutes && deploymentStatus.idle_timeout_minutes) {
      return Math.min(
        ((deploymentStatus.idle_timeout_minutes - deploymentStatus.idle_minutes || 0) /
          deploymentStatus.idle_timeout_minutes) * 100,
        100
      )
    }
    return 100
  }

  const isRuntimeAvailable = deploymentStatus.runtime_available
  const isDeployed = deploymentStatus.deployment_status === 'deployed'
  const isHealthy = deploymentStatus.health_status === 'healthy'

  return (
    <div className={`runtime-status-panel ${className}`}>
      {!isRuntimeAvailable && (
        <Alert
          message="AgentScope Runtime Not Available"
          description="Runtime features require AgentScope Runtime installation."
          type="warning"
          showIcon
          closable
          style={{ marginBottom: 16 }}
        />
      )}

      <Card
        title={
          <Space>
            <CloudServerOutlined />
            <span>Runtime Deployment Status</span>
          </Space>
        }
        extra={
          <Space>
            <Tooltip title="Refresh status">
              <Button
                type="text"
                icon={<ReloadOutlined />}
                onClick={onRefresh}
                loading={loading}
              />
            </Tooltip>
          </Space>
        }
        loading={loading}
      >
        {/* Main Status Display */}
        <Row gutter={[16, 16]}>
          <Col xs={24} sm={8}>
            <Card size="small" className="text-center">
              <Space direction="vertical" size={4}>
                <div style={{ fontSize: '32px' }}>
                  {getStatusIcon(deploymentStatus.deployment_status)}
                </div>
                <Badge
                  status={getStatusColor(deploymentStatus.deployment_status)}
                  text={
                    <Text strong style={{ textTransform: 'capitalize' }}>
                      {deploymentStatus.deployment_status.replace('_', ' ')}
                    </Text>
                  }
                />
              </Space>
            </Card>
          </Col>

          <Col xs={24} sm={8}>
            <Card size="small" className="text-center">
              <Space direction="vertical" size={4}>
                <div style={{ fontSize: '32px' }}>
                  {getHealthStatusIcon(deploymentStatus.health_status)}
                </div>
                <Badge
                  status={deploymentStatus.health_status === 'healthy' ? 'success' : 'error'}
                  text={
                    <Text strong style={{ textTransform: 'capitalize' }}>
                      {deploymentStatus.health_status}
                    </Text>
                  }
                />
              </Space>
            </Card>
          </Col>

          <Col xs={24} sm={8}>
            <Card size="small" className="text-center">
              <Space direction="vertical" size={4}>
                <Statistic
                  title="Uptime"
                  value={deploymentStatus.uptime_minutes || 0}
                  suffix="min"
                  precision={0}
                />
                {deploymentStatus.last_activity && (
                  <Text type="secondary" style={{ fontSize: '12px' }}>
                    Last activity: {formatDate(deploymentStatus.last_activity)}
                  </Text>
                )}
              </Space>
            </Card>
          </Col>
        </Row>

        {/* Deployment Information */}
        <Divider orientation="left">Deployment Information</Divider>

        <Descriptions size="small" column={{ xs: 1, sm: 2 }}>
          <Descriptions.Item label="Agent ID">
            <Text code>{agentId}</Text>
          </Descriptions.Item>
          <Descriptions.Item label="Runtime Available">
            <Badge
              status={isRuntimeAvailable ? 'success' : 'error'}
              text={isRuntimeAvailable ? 'Yes' : 'No'}
            />
          </Descriptions.Item>
          {deploymentStatus.deployment_url && (
            <Descriptions.Item label="Deployment URL" span={2}>
              <Text code copyable>
                {deploymentStatus.deployment_url}
              </Text>
            </Descriptions.Item>
          )}
          {deploymentStatus.deployment_port && (
            <Descriptions.Item label="Port">
              <Tag color="blue">{deploymentStatus.deployment_port}</Tag>
            </Descriptions.Item>
          ))}
          <Descriptions.Item label="Auto Start">
            <Badge
              status={deploymentStatus.auto_start ? 'success' : 'default'}
              text={deploymentStatus.auto_start ? 'Enabled' : 'Disabled'}
            />
          </Descriptions.Item>
          <Descriptions.Item label="Idle Timeout">
            {deploymentStatus.idle_timeout_minutes} minutes
          </Descriptions.Item>
          {deploymentStatus.last_health_check && (
            <Descriptions.Item label="Last Health Check" span={2}>
              {formatDate(deploymentStatus.last_health_check)}
            </Descriptions.Item>
          )}
        </Descriptions>

        {/* Activity and Performance */}
        {isDeployed && (
          <>
            <Divider orientation="left">Activity & Performance</Divider>

            <Row gutter={[16, 16]}>
              <Col xs={24} sm={12}>
                <Card size="small" title="Idle Time">
                  <Progress
                    percent={calculateUptimePercentage()}
                    status={calculateUptimePercentage() < 20 ? 'exception' : 'active'}
                    format={(percent) => `${Math.round(percent)}%`}
                  />
                  <div style={{ marginTop: 8 }}>
                    <Text type="secondary">
                      {deploymentStatus.idle_minutes?.toFixed(1)} / {deploymentStatus.idle_timeout_minutes} minutes
                    </Text>
                  </div>
                </Card>
              </Col>

              <Col xs={24} sm={12}>
                <Card size="small" title="Configuration">
                  <Space direction="vertical" size={4}>
                    <div>
                      <Text type="secondary">Deployment Mode: </Text>
                      <Tag color="blue">Runtime</Tag>
                    </div>
                    <div>
                      <Text type="secondary">Health Checks: </Text>
                      <Badge
                        status={deploymentStatus.auto_start ? 'success' : 'default'}
                        text={deploymentStatus.auto_start ? 'Enabled' : 'Disabled'}
                      />
                    </div>
                  </Space>
                </Card>
              </Col>
            </Row>
          </>
        )}

        {/* Control Actions */}
        <Divider orientation="left">Control Actions</Divider>

        <Space wrap>
          {isDeployed ? (
            <>
              <Button
                type="primary"
                danger
                icon={<StopOutlined />}
                onClick={onStop}
                disabled={!isRuntimeAvailable}
              >
                Stop Agent
              </Button>
              <Button
                icon={<ReloadOutlined />}
                onClick={onRestart}
                disabled={!isRuntimeAvailable}
              >
                Restart Agent
              </Button>
            </>
          ) : (
            <Button
              type="primary"
              icon={<PlayCircleOutlined />}
              onClick={onDeploy}
              disabled={!isRuntimeAvailable}
            >
              Deploy Agent
            </Button>
          )}
          <Button
            icon={<ReloadOutlined />}
            onClick={onRefresh}
            loading={loading}
          >
            Refresh Status
          </Button>
        </Space>

        {/* Health Timeline */}
        {isDeployed && deploymentStatus.last_health_check && (
          <>
            <Divider orientation="left">Recent Activity</Divider>

            <Timeline>
              <Timeline.Item
                dot={<CheckCircleOutlined style={{ fontSize: '16px' }} />}
                color="green"
              >
                <Text>Agent deployed successfully</Text>
                <br />
                <Text type="secondary" style={{ fontSize: '12px' }}>
                  {deploymentStatus.deployment_url}
                </Text>
              </Timeline.Item>

              {isHealthy && (
                <Timeline.Item
                  dot={<SyncOutlined style={{ fontSize: '16px' }} />}
                  color="green"
                >
                  <Text>Health check passed</Text>
                  <br />
                  <Text type="secondary" style={{ fontSize: '12px' }}>
                    {formatDate(deploymentStatus.last_health_check)}
                  </Text>
                </Timeline.Item>
              )}

              {deploymentStatus.last_activity && (
                <Timeline.Item
                  dot={<ThunderboltOutlined style={{ fontSize: '16px' }} />}
                  color="blue"
                >
                  <Text>Last agent activity</Text>
                  <br />
                  <Text type="secondary" style={{ fontSize: '12px' }}>
                    {formatDate(deploymentStatus.last_activity)}
                  </Text>
                </Timeline.Item>
              )}
            </Timeline>
          </>
        )}
      </Card>
    </div>
  )
}

// Helper component for loading state
const LoadingOutlined: React.FC = () => (
  <Spin size="small" indicator={<ReloadOutlined spin />} />
)

export default RuntimeStatusPanel

// Utility functions
export const formatDuration = (minutes: number): string => {
  if (minutes < 60) {
    return `${Math.round(minutes)}m`
  } else if (minutes < 1440) {
    const hours = Math.floor(minutes / 60)
    const mins = Math.round(minutes % 60)
    return `${hours}h ${mins}m`
  } else {
    const days = Math.floor(minutes / 1440)
    const hours = Math.round((minutes % 1440) / 60)
    return `${days}d ${hours}h`
  }
}

export const formatDate = (dateString: string): string => {
  const date = new Date(dateString)
  const now = new Date()
  const diff = now.getTime() - date.getTime()

  if (diff < 60000) { // Less than 1 minute
    return 'just now'
  } else if (diff < 3600000) { // Less than 1 hour
    return `${Math.floor(diff / 60000)} minutes ago`
  } else if (diff < 86400000) { // Less than 1 day
    return `${Math.floor(diff / 3600000)} hours ago`
  } else {
    return date.toLocaleString()
  }
}