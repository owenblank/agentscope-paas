import React, { useState, useEffect } from 'react'
import { Form, Switch, Card, Space, InputNumber, Slider, Radio, Button, Divider, Row, Col, Statistic, Tag, Alert, Collapse, Progress, Select, Input } from 'antd'
import { CompressOutlined, SettingOutlined, ThunderboltOutlined, SafetyOutlined, DashboardOutlined } from '@ant-design/icons'

const { Option } = Select
const { TextArea } = Input
import { useAgentFormStore } from '@/store/agentFormStore'
import type { ContextCompressionConfig } from '@/types'
import { agentService } from '@/services/agentService'

const { Panel } = Collapse

interface ContextCompressionFormProps {
  className?: string
  style?: React.CSSProperties
}

const ContextCompressionForm: React.FC<ContextCompressionFormProps> = ({ className, style }) => {
  const { formData, updateFormData } = useAgentFormStore()
  const [form] = Form.useForm()
  const [compressionEnabled, setCompressionEnabled] = useState(false)
  const [activeStrategy, setActiveStrategy] = useState<string>('hybrid')
  const [analyzing, setAnalyzing] = useState(false)
  const [compressionPreview, setCompressionPreview] = useState<any>(null)

  const compressionConfig = formData.context_compression_config as ContextCompressionConfig | undefined

  useEffect(() => {
    if (compressionConfig) {
      setCompressionEnabled(compressionConfig.enabled)
      setActiveStrategy(compressionConfig.active_strategy || 'hybrid')
      form.setFieldsValue({
        compression_enabled: compressionConfig.enabled,
        active_strategy: compressionConfig.active_strategy || 'hybrid',
        trigger_conditions: compressionConfig.trigger_conditions,
        priority_config: compressionConfig.priority_config,
        quality_controls: compressionConfig.quality_controls
      })
    }
  }, [compressionConfig, form])

  const handleValuesChange = () => {
    const values = form.getFieldsValue()
    const newCompressionConfig: ContextCompressionConfig = {
      enabled: values.compression_enabled || false,
      strategies: compressionConfig?.strategies || {},
      active_strategy: values.active_strategy || 'hybrid',
      trigger_conditions: values.trigger_conditions || {},
      priority_config: values.priority_config,
      quality_controls: values.quality_controls
    }

    updateFormData({
      context_compression_config: newCompressionConfig
    })
  }

  const handleCompressionEnabledChange = (enabled: boolean) => {
    setCompressionEnabled(enabled)
    handleValuesChange()
  }

  const handleStrategyChange = (strategy: string) => {
    setActiveStrategy(strategy)
    handleValuesChange()
  }

  const updateStrategyConfig = (strategy: string, updates: any) => {
    const updatedStrategies = {
      ...(compressionConfig?.strategies || {}),
      [strategy]: {
        ...(compressionConfig?.strategies?.[strategy as keyof typeof compressionConfig.strategies] || {}),
        ...updates
      }
    }

    const updatedConfig = {
      ...(compressionConfig || { enabled: compressionEnabled, strategies: {}, active_strategy: strategy }),
      strategies: updatedStrategies
    }

    updateFormData({
      context_compression_config: updatedConfig
    })
  }

  const previewCompression = async () => {
    setAnalyzing(true)
    try {
      const sampleContext = [
        {
          role: 'system',
          content: 'You are a helpful AI assistant. Please provide detailed and accurate responses.',
          timestamp: new Date(Date.now() - 3600000).toISOString()
        },
        {
          role: 'user',
          content: 'Can you explain what artificial intelligence is?',
          timestamp: new Date(Date.now() - 3500000).toISOString()
        },
        {
          role: 'assistant',
          content: 'Artificial Intelligence (AI) refers to the simulation of human intelligence in machines that are programmed to think and learn like humans. It encompasses various subfields including machine learning, natural language processing, computer vision, and robotics.',
          timestamp: new Date(Date.now() - 3400000).toISOString()
        },
        {
          role: 'user',
          content: 'What are the main types of AI?',
          timestamp: new Date(Date.now() - 3300000).toISOString()
        },
        {
          role: 'assistant',
          content: 'The main types of AI include Narrow AI (designed for specific tasks), General AI (human-level intelligence across domains), and Superintelligent AI (surpassing human intelligence). Current AI systems are primarily Narrow AI.',
          timestamp: new Date(Date.now() - 3200000).toISOString()
        }
      ]

      const result = await agentService.previewCompression(sampleContext, compressionConfig || {
        enabled: compressionEnabled,
        strategies: {},
        active_strategy: activeStrategy
      })

      setCompressionPreview(result)
    } catch (error) {
      console.error('Compression preview failed:', error)
    } finally {
      setAnalyzing(false)
    }
  }

  const getStrategyDescription = (strategy: string) => {
    const descriptions = {
      semantic: '基于语义相似度的智能压缩，保留重要信息的同时合并相似内容',
      token_based: '基于Token计数的压缩，确保上下文长度在指定限制内',
      hybrid: '结合语义和Token优势的混合压缩策略，提供最佳综合效果'
    }
    return descriptions[strategy] || ''
  }

  const getStrategyIcon = (strategy: string) => {
    const icons = {
      semantic: '🧠',
      token_based: '📊',
      hybrid: '⚡'
    }
    return icons[strategy] || '📋'
  }

  const renderSemanticStrategyConfig = () => {
    const semanticConfig = compressionConfig?.strategies?.semantic || {}

    return (
      <Card size="small" title="语义压缩配置" style={{ marginBottom: 16 }}>
        <Space direction="vertical" style={{ width: '100%' }}>
          <div>
            <Space>
              <span>相似度阈值:</span>
              <Tag color="blue">{(semanticConfig.similarity_threshold || 0.75).toFixed(2)}</Tag>
            </Space>
            <Slider
              min={0.1}
              max={1.0}
              step={0.05}
              value={semanticConfig.similarity_threshold || 0.75}
              onChange={(value) => updateStrategyConfig('semantic', { similarity_threshold: value })}
              disabled={!compressionEnabled}
            />
            <p style={{ color: '#999', fontSize: '0.8em', margin: 0 }}>
              较高的阈值会保留更多消息，较低的阈值会进行更多压缩
            </p>
          </div>

          <div>
            <Space>
              <span>最小摘要长度:</span>
              <Tag color="green">{semanticConfig.min_summary_length || 100} 字符</Tag>
            </Space>
            <Slider
              min={50}
              max={500}
              step={50}
              value={semanticConfig.min_summary_length || 100}
              onChange={(value) => updateStrategyConfig('semantic', { min_summary_length: value })}
              disabled={!compressionEnabled}
            />
          </div>

          <div>
            <Space>
              <span>最大摘要长度:</span>
              <Tag color="orange">{semanticConfig.max_summary_length || 500} 字符</Tag>
            </Space>
            <Slider
              min={100}
              max={2000}
              step={100}
              value={semanticConfig.max_summary_length || 500}
              onChange={(value) => updateStrategyConfig('semantic', { max_summary_length: value })}
              disabled={!compressionEnabled}
            />
          </div>

          <div>
            <Space direction="vertical" style={{ width: '100%' }}>
              <span>保留关键词 (每行一个):</span>
              <Input.TextArea
                value={(semanticConfig.preserve_keywords || []).join('\n')}
                onChange={(e) => updateStrategyConfig('semantic', {
                  preserve_keywords: e.target.value.split('\n').filter(k => k.trim())
                })}
                placeholder="重要\n关键信息\n必须保留"
                rows={3}
                disabled={!compressionEnabled}
              />
            </Space>
          </div>

          <div>
            <Switch
              checked={semanticConfig.preserve_entities !== false}
              onChange={(checked) => updateStrategyConfig('semantic', { preserve_entities: checked })}
              disabled={!compressionEnabled}
            /> 保留实体信息（人名、地名、组织等）
          </div>
        </Space>
      </Card>
    )
  }

  const renderTokenBasedStrategyConfig = () => {
    const tokenConfig = compressionConfig?.strategies?.token_based || {}

    return (
      <Card size="small" title="Token压缩配置" style={{ marginBottom: 16 }}>
        <Space direction="vertical" style={{ width: '100%' }}>
          <div>
            <Space>
              <span>最大Token数:</span>
              <Tag color="blue">{tokenConfig.max_tokens || 2000} tokens</Tag>
            </Space>
            <Slider
              min={500}
              max={8000}
              step={500}
              value={tokenConfig.max_tokens || 2000}
              onChange={(value) => updateStrategyConfig('token_based', { max_tokens: value })}
              disabled={!compressionEnabled}
            />
            <p style={{ color: '#999', fontSize: '0.8em', margin: 0 }}>
              控制压缩后的上下文最大长度
            </p>
          </div>

          <div>
            <Space>
              <span>压缩比例:</span>
              <Tag color="purple">{Math.round((tokenConfig.compression_ratio || 0.5) * 100)}%</Tag>
            </Space>
            <Slider
              min={0.1}
              max={0.9}
              step={0.1}
              value={tokenConfig.compression_ratio || 0.5}
              onChange={(value) => updateStrategyConfig('token_based', { compression_ratio: value })}
              disabled={!compressionEnabled}
            />
            <p style={{ color: '#999', fontSize: '0.8em', margin: 0 }}>
              目标压缩比例，较高的值会保留更多内容
            </p>
          </div>

          <div>
            <Switch
              checked={tokenConfig.preserve_structure !== false}
              onChange={(checked) => updateStrategyConfig('token_based', { preserve_structure: checked })}
              disabled={!compressionEnabled}
            /> 保持消息结构（用户/助手角色交替）
          </div>

          <div>
            <Space direction="vertical" style={{ width: '100%' }}>
              <span>优先保留的部分:</span>
              <Select
                mode="tags"
                value={tokenConfig.priority_sections || []}
                onChange={(value) => updateStrategyConfig('token_based', { priority_sections: value })}
                placeholder="输入要优先保留的内容类型"
                disabled={!compressionEnabled}
                style={{ width: '100%' }}
              >
                <Option value="system">系统消息</Option>
                <Option value="user">用户消息</Option>
                <Option value="code">代码块</Option>
                <Option value="important">重要信息</Option>
              </Select>
            </Space>
          </div>
        </Space>
      </Card>
    )
  }

  const renderHybridStrategyConfig = () => {
    const hybridConfig = compressionConfig?.strategies?.hybrid || {}

    return (
      <Card size="small" title="混合策略配置" style={{ marginBottom: 16 }}>
        <Space direction="vertical" style={{ width: '100%' }}>
          <Row gutter={16}>
            <Col span={12}>
              <div>
                <Space>
                  <span>语义权重:</span>
                  <Tag color="blue">{Math.round((hybridConfig.semantic_weight || 0.6) * 100)}%</Tag>
                </Space>
                <Slider
                  min={0.0}
                  max={1.0}
                  step={0.1}
                  value={hybridConfig.semantic_weight || 0.6}
                  onChange={(value) => updateStrategyConfig('hybrid', { semantic_weight: value })}
                  disabled={!compressionEnabled}
                />
              </div>
            </Col>
            <Col span={12}>
              <div>
                <Space>
                  <span>Token权重:</span>
                  <Tag color="green">{Math.round((hybridConfig.token_weight || 0.4) * 100)}%</Tag>
                </Space>
                <Slider
                  min={0.0}
                  max={1.0}
                  step={0.1}
                  value={hybridConfig.token_weight || 0.4}
                  onChange={(value) => updateStrategyConfig('hybrid', { token_weight: value })}
                  disabled={!compressionEnabled}
                />
              </div>
            </Col>
          </Row>

          <Alert
            message="权重说明"
            description="语义权重控制相似度压缩的影响，Token权重控制长度限制的影响。两者之和应为1.0。"
            type="info"
            showIcon
            style={{ marginBottom: 12 }}
          />

          <div>
            <Space>
              <span>最小上下文长度:</span>
              <Tag color="orange">{hybridConfig.min_context_length || 1000} tokens</Tag>
            </Space>
            <Slider
              min={500}
              max={4000}
              step={500}
              value={hybridConfig.min_context_length || 1000}
              onChange={(value) => updateStrategyConfig('hybrid', { min_context_length: value })}
              disabled={!compressionEnabled}
            />
          </div>

          <div>
            <Space>
              <span>自适应阈值:</span>
              <Tag color="purple">{Math.round((hybridConfig.adaptive_threshold || 0.8) * 100)}%</Tag>
            </Space>
            <Slider
              min={0.1}
              max={1.0}
              step={0.1}
              value={hybridConfig.adaptive_threshold || 0.8}
              onChange={(value) => updateStrategyConfig('hybrid', { adaptive_threshold: value })}
              disabled={!compressionEnabled}
            />
            <p style={{ color: '#999', fontSize: '0.8em', margin: 0 }}>
              当上下文接近限制时，自动调整压缩强度
            </p>
          </div>
        </Space>
      </Card>
    )
  }

  const renderCompressionPreview = () => {
    if (!compressionPreview) return null

    const stats = compressionPreview.compression_stats
    const originalMessages = stats.original_messages
    const compressedMessages = stats.compressed_messages
    const compressionRatio = ((1 - stats.compression_ratio) * 100).toFixed(1)

    return (
      <Card
        title={<Space><CompressOutlined /> 压缩效果预览</Space>}
        style={{ marginTop: 16 }}
      >
        <Row gutter={16}>
          <Col span={8}>
            <Statistic
              title="原始消息数"
              value={originalMessages}
              suffix="条"
              valueStyle={{ color: '#999' }}
            />
          </Col>
          <Col span={8}>
            <Statistic
              title="压缩后消息数"
              value={compressedMessages}
              suffix="条"
              valueStyle={{ color: '#3f8600' }}
            />
          </Col>
          <Col span={8}>
            <Statistic
              title="压缩比例"
              value={compressionRatio}
              suffix="%"
              valueStyle={{ color: '#cf1322' }}
              prefix={<CompressOutlined />}
            />
          </Col>
        </Row>

        <Divider />

        <div>
          <Space>
            <span>质量评估:</span>
            <Progress
              type="circle"
              percent={Math.round((stats.validation?.coherence_score || 0.8) * 100)}
              width={80}
              status={(stats.validation?.validation_passed || stats.validation?.coherence_score >= 0.8) ? 'success' : 'exception'}
            />
          </Space>
          <p style={{ color: '#666', fontSize: '0.9em' }}>
            连贯性得分: {(stats.validation?.coherence_score || 0.8).toFixed(2)} / 1.0
          </p>
          <p style={{ color: '#666', fontSize: '0.9em' }}>
            信息损失: {((stats.validation?.information_loss || 0.2) * 100).toFixed(1)}%
          </p>
        </div>

        {stats.validation?.validation_passed === false && (
          <Alert
            message="质量警告"
            description="压缩后的内容可能不符合质量要求，建议调整压缩参数。"
            type="warning"
            showIcon
            style={{ marginTop: 12 }}
          />
        )}
      </Card>
    )
  }

  return (
    <div className={className} style={style}>
      <Form
        form={form}
        layout="vertical"
        onValuesChange={handleValuesChange}
        initialValues={{
          compression_enabled: false,
          active_strategy: 'hybrid',
          trigger_conditions: {
            max_context_length: 4000,
            token_threshold: 3000,
            trigger_on_each_turn: false
          },
          priority_config: {
            enabled: false,
            priority_rules: [],
            preservation_threshold: 0.8
          },
          quality_controls: {
            min_coherence_score: 0.8,
            max_information_loss: 0.2,
            enable_validation: true,
            compression_targets: {
              min_compression_ratio: 0.3,
              max_compression_ratio: 0.6
            }
          }
        }}
      >
        <Form.Item label="启用上下文压缩" valuePropName="checked">
          <Switch
            checked={compressionEnabled}
            onChange={handleCompressionEnabledChange}
            checkedChildren="启用"
            unCheckedChildren="禁用"
          />
        </Form.Item>

        {compressionEnabled && (
          <>
            <Card size="small" style={{ marginBottom: 16 }}>
              <Space direction="vertical" style={{ width: '100%' }}>
                <div>
                  <span style={{ fontWeight: 'bold' }}>选择压缩策略:</span>
                  <Radio.Group
                    value={activeStrategy}
                    onChange={(e) => handleStrategyChange(e.target.value)}
                    style={{ marginTop: 8, display: 'flex', flexDirection: 'column', gap: 8 }}
                  >
                    <Radio value="semantic">
                      <Space>
                        <span>{getStrategyIcon('semantic')}</span>
                        <span>语义压缩</span>
                        <Tag color="blue">智能</Tag>
                      </Space>
                      <p style={{ margin: '4px 0 0 24px', color: '#666', fontSize: '0.9em' }}>
                        {getStrategyDescription('semantic')}
                      </p>
                    </Radio>

                    <Radio value="token_based">
                      <Space>
                        <span>{getStrategyIcon('token_based')}</span>
                        <span>Token压缩</span>
                        <Tag color="green">精确</Tag>
                      </Space>
                      <p style={{ margin: '4px 0 0 24px', color: '#666', fontSize: '0.9em' }}>
                        {getStrategyDescription('token_based')}
                      </p>
                    </Radio>

                    <Radio value="hybrid">
                      <Space>
                        <span>{getStrategyIcon('hybrid')}</span>
                        <span>混合压缩</span>
                        <Tag color="purple">推荐</Tag>
                      </Space>
                      <p style={{ margin: '4px 0 0 24px', color: '#666', fontSize: '0.9em' }}>
                        {getStrategyDescription('hybrid')}
                      </p>
                    </Radio>
                  </Radio.Group>
                </div>
              </Space>
            </Card>

            {activeStrategy === 'semantic' && renderSemanticStrategyConfig()}
            {activeStrategy === 'token_based' && renderTokenBasedStrategyConfig()}
            {activeStrategy === 'hybrid' && renderHybridStrategyConfig()}

            <Collapse defaultActiveKey={['trigger', 'quality']} style={{ marginBottom: 16 }}>
              <Panel header="触发条件" key="trigger" extra={<ThunderboltOutlined />}>
                <Row gutter={16}>
                  <Col span={8}>
                    <Form.Item label="最大上下文长度">
                      <InputNumber
                        name={['trigger_conditions', 'max_context_length']}
                        min={1000}
                        max={16000}
                        step={1000}
                        style={{ width: '100%' }}
                        addonAfter="消息"
                      />
                    </Form.Item>
                  </Col>
                  <Col span={8}>
                    <Form.Item label="Token阈值">
                      <InputNumber
                        name={['trigger_conditions', 'token_threshold']}
                        min={1000}
                        max={8000}
                        step={1000}
                        style={{ width: '100%' }}
                        addonAfter="tokens"
                      />
                    </Form.Item>
                  </Col>
                  <Col span={8}>
                    <Form.Item label="每次触发">
                      <Form.Item
                        name={['trigger_conditions', 'trigger_on_each_turn']}
                        valuePropName="checked"
                        style={{ margin: 0 }}
                      >
                        <Switch />
                      </Form.Item>
                    </Form.Item>
                  </Col>
                </Row>
              </Panel>

              <Panel header="质量控制" key="quality" extra={<SafetyOutlined />}>
                <Row gutter={16}>
                  <Col span={12}>
                    <Form.Item label="最小连贯性得分">
                      <Slider
                        min={0.1}
                        max={1.0}
                        step={0.1}
                        name={['quality_controls', 'min_coherence_score']}
                        marks={{
                          0.1: '0.1',
                          0.5: '0.5',
                          1.0: '1.0'
                        }}
                      />
                    </Form.Item>
                  </Col>
                  <Col span={12}>
                    <Form.Item label="最大信息损失">
                      <Slider
                        min={0.0}
                        max={0.5}
                        step={0.1}
                        name={['quality_controls', 'max_information_loss']}
                        marks={{
                          0.0: '0%',
                          0.25: '25%',
                          0.5: '50%'
                        }}
                      />
                    </Form.Item>
                  </Col>
                </Row>

                <Form.Item
                  label="启用验证"
                  valuePropName="checked"
                  name={['quality_controls', 'enable_validation']}
                >
                  <Switch /> 启用压缩质量验证
                </Form.Item>
              </Panel>

              <Panel header="优先级配置" key="priority" extra={<DashboardOutlined />}>
                <Form.Item
                  label="启用优先级规则"
                  valuePropName="checked"
                  name={['priority_config', 'enabled']}
                >
                  <Switch /> 根据优先级规则保留重要内容
                </Form.Item>

                <Form.Item label="保留阈值">
                  <Slider
                    min={0.1}
                    max={1.0}
                    step={0.1}
                    name={['priority_config', 'preservation_threshold']}
                    marks={{
                      0.1: '10%',
                      0.5: '50%',
                      1.0: '100%'
                    }}
                  />
                  <p style={{ color: '#999', fontSize: '0.8em', margin: '8px 0 0 0' }}>
                    超过此阈值的内容将被优先保留
                  </p>
                </Form.Item>
              </Panel>
            </Collapse>

            <Card
              title={<Space><CompressOutlined /> 压缩预览</Space>}
              extra={
                <Button
                  type="primary"
                  icon={<CompressOutlined />}
                  onClick={previewCompression}
                  loading={analyzing}
                  size="small"
                >
                  测试压缩效果
                </Button>
              }
            >
              <Alert
                message="压缩预览说明"
                description="点击上方按钮将使用示例上下文测试当前压缩配置，预览压缩效果和质量评估。"
                type="info"
                showIcon
                style={{ marginBottom: 12 }}
              />

              {renderCompressionPreview()}
            </Card>
          </>
        )}
      </Form>
    </div>
  )
}

export default ContextCompressionForm