import React, { useState, useEffect } from 'react'
import { Form, Switch, Card, Space, Select, InputNumber, Tag, Checkbox, Divider, Row, Col, Statistic, Input, message, Collapse, Empty } from 'antd'
import { ToolOutlined, SafetyOutlined, SettingOutlined, DatabaseOutlined } from '@ant-design/icons'
import { useAgentFormStore } from '@/store/agentFormStore'
import type { BuiltInToolsConfig, BuiltInTool, ToolCategory } from '@/types'
import { agentService } from '@/services/agentService'

const { Panel } = Collapse

interface BuiltInToolsFormProps {
  className?: string
  style?: React.CSSProperties
}

const BuiltInToolsForm: React.FC<BuiltInToolsFormProps> = ({ className, style }) => {
  const { formData, updateFormData } = useAgentFormStore()
  const [form] = Form.useForm()
  const [toolsEnabled, setToolsEnabled] = useState(false)
  const [availableTools, setAvailableTools] = useState<BuiltInTool[]>([])
  const [categories, setCategories] = useState<ToolCategory[]>([])
  const [selectedCategory, setSelectedCategory] = useState<string>('all')
  const [searchTerm, setSearchTerm] = useState('')
  const [loadingTools, setLoadingTools] = useState(true)

  const toolsConfig = formData.built_in_tools_config as BuiltInToolsConfig | undefined

  useEffect(() => {
    loadToolsAndCategories()
  }, [])

  useEffect(() => {
    if (toolsConfig) {
      setToolsEnabled(toolsConfig.enabled)
      form.setFieldsValue({
        tools_enabled: toolsConfig.enabled,
        global_restrictions: toolsConfig.global_restrictions
      })
    }
  }, [toolsConfig, form])

  const loadToolsAndCategories = async () => {
    setLoadingTools(true)
    try {
      const [toolsData, categoriesData] = await Promise.all([
        agentService.getBuiltinToolsRegistry(),
        agentService.getToolCategories()
      ])

      setAvailableTools(toolsData.tools || [])
      setCategories(Object.values(categoriesData.categories || {}))
    } catch (error) {
      message.error('加载工具列表失败')
      console.error('Failed to load tools:', error)
    } finally {
      setLoadingTools(false)
    }
  }

  const handleValuesChange = () => {
    const values = form.getFieldsValue()
    const newToolsConfig: BuiltInToolsConfig = {
      enabled: values.tools_enabled || false,
      available_tools: toolsConfig?.available_tools || [],
      categories: categories,
      global_restrictions: values.global_restrictions || {
        allowed_categories: [],
        max_total_calls_per_conversation: 50,
        execution_timeout: 60,
        require_user_approval: false
      }
    }

    updateFormData({
      built_in_tools_config: newToolsConfig
    })
  }

  const handleToolsEnabledChange = (enabled: boolean) => {
    setToolsEnabled(enabled)
    handleValuesChange()
  }

  const toggleTool = (toolId: string) => {
    const currentTools = toolsConfig?.available_tools || []
    const existingTool = currentTools.find(tool => tool.tool_id === toolId)

    let updatedTools: BuiltInTool[]

    if (existingTool) {
      // Remove tool
      updatedTools = currentTools.filter(tool => tool.tool_id !== toolId)
    } else {
      // Add tool
      const toolToAdd = availableTools.find(tool => tool.tool_id === toolId)
      if (toolToAdd) {
        updatedTools = [...currentTools, toolToAdd]
      } else {
        return
      }
    }

    const updatedConfig = {
      ...(toolsConfig || { enabled: toolsEnabled, available_tools: [], categories: [] }),
      available_tools: updatedTools
    }

    updateFormData({
      built_in_tools_config: updatedConfig
    })
  }

  const updateToolConfig = (toolId: string, updates: Partial<BuiltInTool>) => {
    const updatedTools = (toolsConfig?.available_tools || []).map(tool =>
      tool.tool_id === toolId ? { ...tool, ...updates } : tool
    )

    const updatedConfig = {
      ...(toolsConfig || { enabled: toolsEnabled, available_tools: [], categories: [] }),
      available_tools: updatedTools
    }

    updateFormData({
      built_in_tools_config: updatedConfig
    })
  }

  const getEnabledToolsCount = () => {
    return toolsConfig?.available_tools?.length || 0
  }

  const filterTools = () => {
    return availableTools.filter(tool => {
      const matchesCategory = selectedCategory === 'all' || tool.category === selectedCategory
      const matchesSearch = !searchTerm ||
        tool.tool_name.toLowerCase().includes(searchTerm.toLowerCase()) ||
        tool.description.toLowerCase().includes(searchTerm.toLowerCase())
      return matchesCategory && matchesSearch
    })
  }

  const renderToolCard = (tool: BuiltInTool) => {
    const isEnabled = (toolsConfig?.available_tools || []).some(t => t.tool_id === tool.tool_id)
    const enabledTool = (toolsConfig?.available_tools || []).find(t => t.tool_id === tool.tool_id)

    const categoryInfo = categories.find(cat => cat.category_id === tool.category)

    return (
      <Card
        key={tool.tool_id}
        size="small"
        title={
          <Space>
            <ToolOutlined />
            <span>{tool.tool_name}</span>
            <Tag color={categoryInfo ? 'blue' : 'default'}>
              {categoryInfo?.category_name || tool.category}
            </Tag>
          </Space>
        }
        extra={
          <Switch
            checked={isEnabled}
            onChange={() => toggleTool(tool.tool_id)}
            disabled={!toolsEnabled}
            checkedChildren="启用"
            unCheckedChildren="禁用"
          />
        }
        style={{ marginBottom: 12 }}
        headStyle={{ backgroundColor: isEnabled ? '#f0f8ff' : '#fafafa' }}
      >
        {isEnabled && enabledTool && (
          <>
            <p style={{ marginBottom: 16 }}>{tool.description}</p>

            <Collapse ghost style={{ marginBottom: 12 }}>
              <Panel header="工具参数" key="parameters" extra={<SettingOutlined />}>
                <Space direction="vertical" style={{ width: '100%' }}>
                  {tool.parameters.map(param => (
                    <div key={param.name}>
                      <Space>
                        <Tag color={param.required ? 'red' : 'green'}>
                          {param.type}
                        </Tag>
                        <strong>{param.name}</strong>
                        {!param.required && <span style={{ color: '#999' }}>(可选)</span>}
                      </Space>
                      <p style={{ marginLeft: 24, color: '#666', fontSize: '0.9em' }}>
                        {param.description}
                      </p>
                    </div>
                  ))}
                </Space>
              </Panel>

              <Panel header="执行配置" key="execution">
                <Row gutter={16}>
                  <Col span={8}>
                    <Form.Item label="超时时间 (秒)">
                      <InputNumber
                        value={enabledTool.execution_config?.timeout || tool.execution_config.timeout}
                        onChange={(value) => updateToolConfig(tool.tool_id, {
                          execution_config: { ...tool.execution_config, timeout: value || 30 }
                        })}
                        min={1}
                        max={300}
                        disabled={!toolsEnabled}
                        style={{ width: '100%' }}
                      />
                    </Form.Item>
                  </Col>
                  <Col span={8}>
                    <Form.Item label="重试次数">
                      <InputNumber
                        value={enabledTool.execution_config?.retry_count || tool.execution_config.retry_count}
                        onChange={(value) => updateToolConfig(tool.tool_id, {
                          execution_config: { ...tool.execution_config, retry_count: value || 1 }
                        })}
                        min={0}
                        max={10}
                        disabled={!toolsEnabled}
                        style={{ width: '100%' }}
                      />
                    </Form.Item>
                  </Col>
                  <Col span={8}>
                    <Form.Item label="内存限制 (MB)">
                      <InputNumber
                        value={enabledTool.execution_config?.memory_limit_mb || tool.execution_config.memory_limit_mb}
                        onChange={(value) => updateToolConfig(tool.tool_id, {
                          execution_config: { ...tool.execution_config, memory_limit_mb: value || 512 }
                        })}
                        min={64}
                        max={8192}
                        disabled={!toolsEnabled}
                        style={{ width: '100%' }}
                      />
                    </Form.Item>
                  </Col>
                </Row>
              </Panel>

              <Panel header="权限配置" key="permissions" extra={<SafetyOutlined />}>
                <Space direction="vertical" style={{ width: '100%' }}>
                  <Form.Item label="每会话最大调用次数">
                    <InputNumber
                      value={enabledTool.permissions?.max_calls_per_conversation || tool.permissions.max_calls_per_conversation}
                      onChange={(value) => updateToolConfig(tool.tool_id, {
                        permissions: { ...tool.permissions, max_calls_per_conversation: value || 20 }
                      })}
                      min={1}
                      max={1000}
                      disabled={!toolsEnabled}
                      style={{ width: '100%' }}
                    />
                  </Form.Item>

                  <Form.Item label="安全级别">
                    <Select
                      value={enabledTool.permissions?.security_level || tool.permissions.security_level}
                      onChange={(value) => updateToolConfig(tool.tool_id, {
                        permissions: { ...tool.permissions, security_level: value }
                      })}
                      disabled={!toolsEnabled}
                      style={{ width: '100%' }}
                    >
                      <Option value="low">低 - 基础工具</Option>
                      <Option value="medium">中 - 标准工具</Option>
                      <Option value="high">高 - 敏感操作工具</Option>
                    </Select>
                  </Form.Item>

                  <Form.Item label="需要用户确认">
                    <Switch
                      checked={enabledTool.permissions?.require_user_confirmation ?? false}
                      onChange={(checked) => updateToolConfig(tool.tool_id, {
                        permissions: { ...tool.permissions, require_user_confirmation: checked }
                      })}
                      disabled={!toolsEnabled}
                    />
                  </Form.Item>
                </Space>
              </Panel>
            </Collapse>

            <Divider style={{ margin: '12px 0' }} />

            <Row gutter={16}>
              <Col span={12}>
                <Statistic
                  title="版本"
                  value={tool.version}
                  prefix={<Tag color="blue">{tool.category}</Tag>}
                  valueStyle={{ fontSize: '0.9em' }}
                />
              </Col>
              <Col span={12}>
                <Statistic
                  title="参数数量"
                  value={tool.parameters.length}
                  suffix="个"
                  valueStyle={{ fontSize: '0.9em' }}
                />
              </Col>
            </Row>
          </>
        )}

        {!isEnabled && (
          <p style={{ color: '#999', marginBottom: 0 }}>{tool.description}</p>
        )}
      </Card>
    )
  }

  const renderCategoryFilter = () => {
    const categoryOptions = [
      { category_id: 'all', category_name: '全部工具', icon: '📦' },
      ...categories
    ]

    return (
      <Space style={{ marginBottom: 16, flexWrap: 'wrap' }}>
        {categoryOptions.map(category => (
          <Tag.CheckableTag
            key={category.category_id}
            checked={selectedCategory === category.category_id}
            onChange={(checked) => setSelectedCategory(checked ? category.category_id : 'all')}
            style={{
              padding: '4px 12px',
              fontSize: '0.9em',
              cursor: 'pointer',
              borderRadius: '4px'
            }}
          >
            {category.icon} {category.category_name}
          </Tag.CheckableTag>
        ))}
      </Space>
    )
  }

  const filteredTools = filterTools()

  return (
    <div className={className} style={style}>
      <Form
        form={form}
        layout="vertical"
        onValuesChange={handleValuesChange}
        initialValues={{
          tools_enabled: false,
          global_restrictions: {
            allowed_categories: [],
            max_total_calls_per_conversation: 50,
            execution_timeout: 60,
            require_user_approval: false
          }
        }}
      >
        <Form.Item label="启用内置工具" valuePropName="checked">
          <Switch
            checked={toolsEnabled}
            onChange={handleToolsEnabledChange}
            checkedChildren="启用"
            unCheckedChildren="禁用"
          />
        </Form.Item>

        {toolsEnabled && (
          <>
            <Collapse defaultActiveKey={['restrictions']} style={{ marginBottom: 16 }}>
              <Panel header="全局限制" key="restrictions" extra={<SafetyOutlined />}>
                <Row gutter={16}>
                  <Col span={12}>
                    <Form.Item label="每会话最大调用次数">
                      <InputNumber
                        name={['global_restrictions', 'max_total_calls_per_conversation']}
                        min={1}
                        max={10000}
                        style={{ width: '100%' }}
                      />
                    </Form.Item>
                  </Col>
                  <Col span={12}>
                    <Form.Item label="执行超时时间 (秒)">
                      <InputNumber
                        name={['global_restrictions', 'execution_timeout']}
                        min={5}
                        max={300}
                        style={{ width: '100%' }}
                      />
                    </Form.Item>
                  </Col>
                </Row>

                <Form.Item
                  label="允许的工具类别"
                  name={['global_restrictions', 'allowed_categories']}
                >
                  <Select
                    mode="multiple"
                    placeholder="选择允许的工具类别，留空表示全部允许"
                    style={{ width: '100%' }}
                  >
                    {categories.map(category => (
                      <Option key={category.category_id} value={category.category_id}>
                        {category.icon} {category.category_name}
                      </Option>
                    ))}
                  </Select>
                </Form.Item>

                <Form.Item
                  label="需要用户批准"
                  valuePropName="checked"
                  name={['global_restrictions', 'require_user_approval']}
                >
                  <Switch />
                </Form.Item>
              </Panel>

              <Panel header="工具统计" key="stats" extra={<DatabaseOutlined />}>
                <Row gutter={16}>
                  <Col span={6}>
                    <Statistic
                      title="可用工具"
                      value={availableTools.length}
                      suffix="个"
                    />
                  </Col>
                  <Col span={6}>
                    <Statistic
                      title="已启用工具"
                      value={getEnabledToolsCount()}
                      suffix="个"
                      valueStyle={{ color: '#3f8600' }}
                    />
                  </Col>
                  <Col span={6}>
                    <Statistic
                      title="工具类别"
                      value={categories.length}
                      suffix="个"
                    />
                  </Col>
                  <Col span={6}>
                    <Statistic
                      title="最大调用次数"
                      value={form.getFieldValue(['global_restrictions', 'max_total_calls_per_conversation']) || 50}
                      suffix="次/会话"
                    />
                  </Col>
                </Row>
              </Panel>
            </Collapse>

            <Input.Search
              placeholder="搜索工具名称或描述..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              style={{ marginBottom: 16 }}
              allowClear
            />

            {renderCategoryFilter()}

            <div style={{ marginTop: 16 }}>
              {loadingTools ? (
                <Card loading style={{ textAlign: 'center', padding: '40px 0' }}>
                  加载工具列表...
                </Card>
              ) : filteredTools.length > 0 ? (
                filteredTools.map(tool => renderToolCard(tool))
              ) : (
                <Card style={{ textAlign: 'center', padding: '40px 0' }}>
                  <Empty
                    description={
                      searchTerm ? '未找到匹配的工具' : '暂无可用工具'
                    }
                    image={Empty.PRESENTED_IMAGE_SIMPLE}
                  />
                </Card>
              )}
            </div>
          </>
        )}
      </Form>
    </div>
  )
}

export default BuiltInToolsForm