/**
 * Runtime Configuration Form Component
 *
 * Provides UI for configuring AgentScope Runtime deployment settings including
 * deployment mode selection, service configuration, health monitoring, and lifecycle management.
 */

import React, { useState, useEffect } from 'react'
import {
  Form,
  Select,
  InputNumber,
  Switch,
  Input,
  Card,
  Row,
  Col,
  Divider,
  Space,
  Tooltip,
  Typography,
  Alert,
  Collapse,
  Button,
  Tag,
  Badge
} from 'antd'
import {
  InfoCircleOutlined,
  ThunderboltOutlined,
  SyncOutlined,
  CloudServerOutlined,
  SettingOutlined,
  SafetyOutlined,
  RocketOutlined,
  CheckCircleOutlined,
  ExclamationCircleOutlined
} from '@ant-design/icons'
import type { RuntimeConfig } from '@/types/agent'

const { Option } = Select
const { TextArea } = Input
const { Title, Text, Paragraph } = Typography
const { Panel } = Collapse

interface RuntimeConfigFormProps {
  value?: RuntimeConfig
  onChange?: (config: RuntimeConfig) => void
  disabled?: boolean
  runtimeAvailable?: boolean
}

const RuntimeConfigForm: React.FC<RuntimeConfigFormProps> = ({
  value,
  onChange,
  disabled = false,
  runtimeAvailable = true
}) => {
  const [form] = Form.useForm()
  const [deploymentMode, setDeploymentMode] = useState<RuntimeConfig['deployment_mode']>(
    value?.deployment_mode || 'traditional'
  )

  useEffect(() => {
    if (value) {
      form.setFieldsValue(value)
      setDeploymentMode(value.deployment_mode)
    }
  }, [value, form])

  const handleValuesChange = (changedValues: Partial<RuntimeConfig>, allValues: RuntimeConfig) => {
    if (onChange) {
      onChange(allValues)
    }
  }

  const getDeploymentModeColor = (mode: RuntimeConfig['deployment_mode']) => {
    switch (mode) {
      case 'runtime':
        return 'blue'
      case 'hybrid':
        return 'purple'
      default:
        return 'default'
    }
  }

  const getDeploymentModeDescription = (mode: RuntimeConfig['deployment_mode']) => {
    switch (mode) {
      case 'runtime':
        return 'Deploy as HTTP service with full Runtime capabilities'
      case 'hybrid':
        return 'Support both traditional and Runtime modes'
      default:
        return 'Traditional in-memory execution'
    }
  }

  return (
    <div className="runtime-config-form">
      {!runtimeAvailable && (
        <Alert
          message="AgentScope Runtime Not Available"
          description="Runtime features require AgentScope Runtime installation. Install with: pip install agentscope-runtime"
          type="warning"
          showIcon
          style={{ marginBottom: 16 }}
        />
      )}

      <Form
        form={form}
        layout="vertical"
        initialValues={value || getDefaultRuntimeConfig()}
        onValuesChange={handleValuesChange}
        disabled={disabled || !runtimeAvailable}
      >
        {/* Deployment Mode Selection */}
        <Card
          title={
            <Space>
              <RocketOutlined />
              <span>Deployment Configuration</span>
            </Space>
          }
          extra={
            <Tooltip title="Choose how your agent should be deployed">
              <InfoCircleOutlined />
            </Tooltip>
          }
          className="mb-4"
        >
          <Form.Item
            label="Deployment Mode"
            name="deployment_mode"
            tooltip="Select the deployment mode for this agent"
          >
            <Select
              size="large"
              placeholder="Select deployment mode"
              onChange={(mode) => setDeploymentMode(mode)}
            >
              <Option value="traditional">
                <Space>
                  <Badge status="default" text="Traditional Mode" />
                  <Text type="secondary">- In-memory execution</Text>
                </Space>
              </Option>
              <Option value="runtime">
                <Space>
                  <Badge status="processing" text="Runtime Mode" />
                  <Text type="secondary">- HTTP service deployment</Text>
                </Space>
              </Option>
              <Option value="hybrid">
                <Space>
                  <Badge status="warning" text="Hybrid Mode" />
                  <Text type="secondary">- Flexible deployment</Text>
                </Space>
              </Option>
            </Select>
          </Form.Item>

          <Paragraph type="secondary" className="text-sm">
            {getDeploymentModeDescription(deploymentMode)}
          </Paragraph>
        </Card>

        {/* Service Configuration */}
        {deploymentMode !== 'traditional' && (
          <Card
            title={
              <Space>
                <CloudServerOutlined />
                <span>Service Configuration</span>
              </Space>
            }
            className="mb-4"
          >
            <Row gutter={[16, 16]}>
              <Col xs={24} sm={12}>
                <Form.Item
                  label="Service Host"
                  name={['service_config', 'host']}
                  tooltip="Hostname or IP address for the service"
                  rules={[{ required: true, message: 'Please enter service host' }]}
                >
                  <Input placeholder="localhost" />
                </Form.Item>
              </Col>
              <Col xs={24} sm={12}>
                <Form.Item
                  label="Service Port"
                  name={['service_config', 'port']}
                  tooltip="Port number for the service (1-65535)"
                  rules={[
                    { required: true, message: 'Please enter service port' },
                    { type: 'number', min: 1, max: 65535, message: 'Port must be between 1-65535' }
                  ]}
                >
                  <InputNumber placeholder="8080" className="w-full" />
                </Form.Item>
              </Col>
              <Col xs={24} sm={12}>
                <Form.Item
                  label="Max Concurrent Requests"
                  name={['service_config', 'max_concurrent_requests']}
                  tooltip="Maximum number of concurrent requests"
                  initialValue={10}
                >
                  <InputNumber min={1} max={1000} className="w-full" />
                </Form.Item>
              </Col>
              <Col xs={24} sm={12}>
                <Form.Item
                  label="Request Timeout (seconds)"
                  name={['service_config', 'request_timeout']}
                  tooltip="Request timeout in seconds"
                  initialValue={120}
                >
                  <InputNumber min={10} max={600} className="w-full" />
                </Form.Item>
              </Col>
            </Row>

            <Divider orientation="left">Advanced Service Settings</Divider>

            <Row gutter={[16, 16]}>
              <Col xs={24} sm={12}>
                <Form.Item
                  label="Enable CORS"
                  name={['service_config', 'enable_cors']}
                  valuePropName="checked"
                  initialValue={true}
                  tooltip="Enable Cross-Origin Resource Sharing"
                >
                  <Switch />
                </Form.Item>
              </Col>
              <Col xs={24} sm={12}>
                <Form.Item
                  label="Startup Timeout (seconds)"
                  name={['service_config', 'startup_timeout']}
                  tooltip="Maximum time for service startup"
                  initialValue={300}
                >
                  <InputNumber min={30} max={900} className="w-full" />
                </Form.Item>
              </Col>
            </Row>
          </Card>
        )}

        {/* Lifecycle Management */}
        {deploymentMode !== 'traditional' && (
          <Card
            title={
              <Space>
                <SettingOutlined />
                <span>Lifecycle Management</span>
              </Space>
            }
            className="mb-4"
          >
            <Row gutter={[16, 16]}>
              <Col xs={24} sm={12}>
                <Form.Item
                  label="Auto Start"
                  name={['lifecycle_config', 'auto_start']}
                  valuePropName="checked"
                  initialValue={true}
                  tooltip="Automatically start service on deployment"
                >
                  <Switch checkedChildren="ON" unCheckedChildren="OFF" />
                </Form.Item>
              </Col>
              <Col xs={24} sm={12}>
                <Form.Item
                  label="Auto Stop"
                  name={['lifecycle_config', 'auto_stop']}
                  valuePropName="checked"
                  initialValue={false}
                  tooltip="Automatically stop service when idle"
                >
                  <Switch checkedChildren="ON" unCheckedChildren="OFF" />
                </Form.Item>
              </Col>
              <Col xs={24} sm={12}>
                <Form.Item
                  label="Idle Timeout (minutes)"
                  name={['lifecycle_config', 'idle_timeout_minutes']}
                  tooltip="Idle time before auto-stop (if enabled)"
                  initialValue={30}
                >
                  <InputNumber min={5} max={240} className="w-full" />
                </Form.Item>
              </Col>
              <Col xs={24} sm={12}>
                <Form.Item
                  label="Graceful Shutdown Timeout (seconds)"
                  name={['lifecycle_config', 'graceful_shutdown_timeout']}
                  tooltip="Time allowed for graceful shutdown"
                  initialValue={60}
                >
                  <InputNumber min={10} max={300} className="w-full" />
                </Form.Item>
              </Col>
            </Row>

            <Divider orientation="left">Retry Configuration</Divider>

            <Row gutter={[16, 16]}>
              <Col xs={24} sm={12}>
                <Form.Item
                  label="Max Retries"
                  name={['lifecycle_config', 'max_retries']}
                  tooltip="Maximum number of retry attempts"
                  initialValue={3}
                >
                  <InputNumber min={0} max={10} className="w-full" />
                </Form.Item>
              </Col>
              <Col xs={24} sm={12}>
                <Form.Item
                  label="Retry Delay (seconds)"
                  name={['lifecycle_config', 'retry_delay_seconds']}
                  tooltip="Delay between retry attempts"
                  initialValue={5}
                >
                  <InputNumber min={1} max={60} className="w-full" />
                </Form.Item>
              </Col>
            </Row>
          </Card>
        )}

        {/* Health Monitoring */}
        {deploymentMode !== 'traditional' && (
          <Card
            title={
              <Space>
                <SyncOutlined />
                <span>Health Monitoring</span>
              </Space>
            }
            className="mb-4"
          >
            <Row gutter={[16, 16]}>
              <Col xs={24} sm={8}>
                <Form.Item
                  label="Enable Health Checks"
                  name={['health_check_config', 'enabled']}
                  valuePropName="checked"
                  initialValue={true}
                  tooltip="Enable periodic health monitoring"
                >
                  <Switch checkedChildren="ON" unCheckedChildren="OFF" />
                </Form.Item>
              </Col>
              <Col xs={24} sm={8}>
                <Form.Item
                  label="Check Interval (seconds)"
                  name={['health_check_config', 'interval_seconds']}
                  tooltip="Time between health checks"
                  initialValue={60}
                >
                  <InputNumber min={10} max={300} className="w-full" />
                </Form.Item>
              </Col>
              <Col xs={24} sm={8}>
                <Form.Item
                  label="Check Timeout (seconds)"
                  name={['health_check_config', 'timeout_seconds']}
                  tooltip="Health check timeout"
                  initialValue={10}
                >
                  <InputNumber min={5} max={60} className="w-full" />
                </Form.Item>
              </Col>
            </Row>

            <Divider orientation="left">Threshold Configuration</Divider>

            <Row gutter={[16, 16]}>
              <Col xs={24} sm={12}>
                <Form.Item
                  label="Failure Threshold"
                  name={['health_check_config', 'failure_threshold']}
                  tooltip="Consecutive failures before marking unhealthy"
                  initialValue={3}
                >
                  <InputNumber min={1} max={10} className="w-full" />
                </Form.Item>
              </Col>
              <Col xs={24} sm={12}>
                <Form.Item
                  label="Success Threshold"
                  name={['health_check_config', 'success_threshold']}
                  tooltip="Consecutive successes before marking healthy"
                  initialValue={1}
                >
                  <InputNumber min={1} max={10} className="w-full" />
                </Form.Item>
              </Col>
            </Row>
          </Card>
        )}

        {/* Streaming Configuration */}
        {deploymentMode === 'runtime' && (
          <Card
            title={
              <Space>
                <ThunderboltOutlined />
                <span>Streaming Configuration</span>
              </Space>
            }
            className="mb-4"
          >
            <Row gutter={[16, 16]}>
              <Col xs={24} sm={8}>
                <Form.Item
                  label="Enable Streaming"
                  name={['streaming_config', 'enabled']}
                  valuePropName="checked"
                  initialValue={true}
                  tooltip="Enable real-time streaming responses"
                >
                  <Switch checkedChildren="ON" unCheckedChildren="OFF" />
                </Form.Item>
              </Col>
              <Col xs={24} sm={8}>
                <Form.Item
                  label="Chunk Size"
                  name={['streaming_config', 'chunk_size']}
                  tooltip="Size of streaming chunks"
                  initialValue={1024}
                >
                  <InputNumber min={256} max={8192} className="w-full" />
                </Form.Item>
              </Col>
              <Col xs={24} sm={8}>
                <Form.Item
                  label="Timeout (seconds)"
                  name={['streaming_config', 'timeout_seconds']}
                  tooltip="Streaming response timeout"
                  initialValue={120}
                >
                  <InputNumber min={30} max={300} className="w-full" />
                </Form.Item>
              </Col>
            </Row>
          </Card>
        )}

        {/* Sandbox Configuration */}
        {deploymentMode === 'runtime' && (
          <Card
            title={
              <Space>
                <SafetyOutlined />
                <span>Sandbox Configuration</span>
              </Space>
            }
            className="mb-4"
          >
            <Row gutter={[16, 16]}>
              <Col xs={24} sm={12}>
                <Form.Item
                  label="Enable Sandbox"
                  name={['sandbox_config', 'enabled']}
                  valuePropName="checked"
                  initialValue={false}
                  tooltip="Enable secure code execution sandbox"
                >
                  <Switch checkedChildren="ON" unCheckedChildren="OFF" />
                </Form.Item>
              </Col>
              <Col xs={24} sm={12}>
                <Form.Item
                  label="Sandbox Type"
                  name={['sandbox_config', 'sandbox_type']}
                  tooltip="Type of sandbox environment"
                  initialValue="docker"
                >
                  <Select>
                    <Option value="docker">Docker</Option>
                    <Option value="process">Process</Option>
                    <Option value="thread">Thread</Option>
                    <Option value="none">None</Option>
                  </Select>
                </Form.Item>
              </Col>
            </Row>

            <Collapse ghost>
              <Panel header="Advanced Sandbox Settings" key="sandbox_advanced">
                <Row gutter={[16, 16]}>
                  <Col xs={24} sm={12}>
                    <Form.Item
                      label="Memory Limit (MB)"
                      name={['sandbox_config', 'memory_limit_mb']}
                      tooltip="Maximum memory usage"
                    >
                      <InputNumber min={128} max={8192} className="w-full" />
                    </Form.Item>
                  </Col>
                  <Col xs={24} sm={12}>
                    <Form.Item
                      label="CPU Limit"
                      name={['sandbox_config', 'cpu_limit']}
                      tooltip="Maximum CPU usage"
                    >
                      <InputNumber min={0.1} max={4.0} step={0.1} className="w-full" />
                    </Form.Item>
                  </Col>
                  <Col xs={24} sm={12}>
                    <Form.Item
                      label="Timeout (seconds)"
                      name={['sandbox_config', 'timeout_seconds']}
                      tooltip="Sandbox execution timeout"
                    >
                      <InputNumber min={10} max={600} className="w-full" />
                    </Form.Item>
                  </Col>
                  <Col xs={24} sm={12}>
                    <Form.Item
                      label="Docker Image"
                      name={['sandbox_config', 'image']}
                      tooltip="Docker image for sandbox"
                    >
                      <Input placeholder="python:3.10-slim" />
                    </Form.Item>
                  </Col>
                </Row>
              </Panel>
            </Collapse>
          </Card>
        )}

        {/* Advanced Configuration */}
        <Card
          title={
            <Space>
              <SettingOutlined />
              <span>Advanced Configuration</span>
            </Space>
          }
          className="mb-4"
        >
          <Collapse ghost>
            <Panel header="Monitoring Configuration" key="monitoring">
              <Row gutter={[16, 16]}>
                <Col xs={24} sm={8}>
                  <Form.Item
                    label="Enable Metrics"
                    name={['monitoring_config', 'enable_metrics']}
                    valuePropName="checked"
                    initialValue={true}
                  >
                    <Switch />
                  </Form.Item>
                </Col>
                <Col xs={24} sm={8}>
                  <Form.Item
                    label="Log Level"
                    name={['monitoring_config', 'log_level']}
                    initialValue="INFO"
                  >
                    <Select>
                      <Option value="DEBUG">Debug</Option>
                      <Option value="INFO">Info</Option>
                      <Option value="WARNING">Warning</Option>
                      <Option value="ERROR">Error</Option>
                    </Select>
                  </Form.Item>
                </Col>
                <Col xs={24} sm={8}>
                  <Form.Item
                    label="Metrics Port"
                    name={['monitoring_config', 'metrics_port']}
                    initialValue={9090}
                  >
                    <InputNumber min={1024} max={65535} className="w-full" />
                  </Form.Item>
                </Col>
              </Row>
            </Panel>

            <Panel header="Custom Decorators & Middleware" key="custom">
              <Form.Item
                label="Custom Decorators"
                name="custom_decorators"
                tooltip="List of custom decorator functions"
              >
                <Select mode="tags" placeholder="Enter decorator names" />
              </Form.Item>

              <Form.Item
                label="Middleware"
                name="middleware"
                tooltip="List of middleware functions"
              >
                <Select mode="tags" placeholder="Enter middleware names" />
              </Form.Item>

              <Form.Item
                label="Environment Variables"
                name="environment_variables"
                tooltip="Custom environment variables (JSON format)"
              >
                <TextArea
                  rows={4}
                  placeholder='{"KEY": "value"}'
                  style={{ fontFamily: 'monospace' }}
                />
              </Form.Item>
            </Panel>
          </Collapse>
        </Card>
      </Form>
    </div>
  )
}

// Helper function to get default Runtime configuration
export function getDefaultRuntimeConfig(): RuntimeConfig {
  return {
    deployment_mode: 'traditional',
    service_config: {
      host: 'localhost',
      port: 8080,
      max_concurrent_requests: 10,
      startup_timeout: 300,
      request_timeout: 120,
      enable_cors: true,
      cors_origins: ['*']
    },
    lifecycle_config: {
      auto_start: true,
      auto_stop: false,
      idle_timeout_minutes: 30,
      graceful_shutdown_timeout: 60,
      max_retries: 3,
      retry_delay_seconds: 5,
      health_check_on_failure: true
    },
    health_check_config: {
      enabled: true,
      interval_seconds: 60,
      timeout_seconds: 10,
      failure_threshold: 3,
      success_threshold: 1
    },
    streaming_config: {
      enabled: true,
      chunk_size: 1024,
      buffer_size: 8192,
      keepalive_interval: 30,
      timeout_seconds: 120
    },
    sandbox_config: {
      enabled: false,
      sandbox_type: 'docker',
      timeout_seconds: 120
    },
    monitoring_config: {
      enable_metrics: true,
      log_level: 'INFO',
      prometheus_enabled: false
    }
  }
}

export default RuntimeConfigForm