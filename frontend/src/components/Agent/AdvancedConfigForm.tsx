import { Form, InputNumber, Switch, Card, Typography, Collapse, Select, Input, Space, Checkbox, Divider, Button, Tag, Alert, message } from 'antd'
import { InfoCircleOutlined, PlusOutlined, DatabaseOutlined, ToolOutlined, BugOutlined, CloudUploadOutlined } from '@ant-design/icons'
import { useAgentFormStore } from '@/store'
import SkillsUploadForm from './SkillsUploadForm'

const { Text, Paragraph } = Typography
const { Panel } = Collapse
const { Option } = Select
const { TextArea } = Input

const AdvancedConfigForm = () => {
  const { formData, updateFormData } = useAgentFormStore()
  const [form] = Form.useForm()

  const handleValuesChange = () => {
    const values = form.getFieldsValue()
    updateFormData({
      memory_config: values.memory_config,
      knowledge_config: values.knowledge_config,
      skills_config: values.skills_config,
      behavior_config: values.behavior_config,
      monitoring_config: values.monitoring_config,
    })
  }

  return (
    <Form
      form={form}
      layout="vertical"
      initialValues={{
        memory_config: {
          short_term: {
            enabled: true,
            max_history_rounds: 10,
          },
          long_term: {
            enabled: false,
            storage_type: 'file',
          },
          vector: {
            enabled: false,
          },
        },
        knowledge_config: {
          platform_knowledge: {
            enabled: true,
            platform_url: 'https://knowledge.example.com/api/v1',
            connection_config: {
              authentication: {
                type: 'bearer_token',
                token: '',
              },
              timeout: 30,
            },
            retrieval_config: {
              retrieval_mode: 'semantic',
              similarity_threshold: 0.75,
              top_k: 5,
              enable_context_enhancement: true,
              context_window_size: 3,
            },
            permissions: {
              enabled: true,
              max_queries_per_conversation: 20,
              allowed_operations: ['search', 'retrieve', 'summarize'],
            },
          },
        },
        skills_config: {
          load_mode: 'upload',
          upload_config: {
            supported_upload_methods: [
              {
                method: 'single_file',
                enabled: true,
                description: '上传单个SKILL.md文件',
                max_size_mb: 3,
                supported_formats: ['.md'],
              },
              {
                method: 'folder',
                enabled: true,
                description: '上传包含技能文件的文件夹',
                max_size_mb: 3,
                supported_formats: ['.md'],
              },
              {
                method: 'zip',
                enabled: true,
                description: '上传ZIP格式的技能压缩包',
                max_size_mb: 3,
                max_files: 50,
                supported_formats: ['.zip'],
                extraction_config: {
                  extract_root_only: false,
                  preserve_structure: true,
                  overwrite_existing: false,
                },
              },
            ],
            max_file_size_mb: 3,
            max_total_size_mb: 10,
            max_files_per_upload: 20,
          },
          execution_config: {
            max_concurrent_skills: 5,
            skill_timeout: 30,
            failure_handling_strategy: 'continue',
            max_retries: 2,
          },
          permissions: {
            enabled: true,
            max_skill_calls_per_conversation: 50,
            allowed_skill_categories: ['text_analysis', 'data_analysis', 'general'],
            security_level: 'medium',
          },
        },
        behavior_config: formData.behavior_config,
        monitoring_config: formData.monitoring_config,
      }}
      onValuesChange={handleValuesChange}
    >
      <Collapse defaultActiveKey={['memory']}>
        {/* 记忆配置 */}
        <Panel header="记忆配置" key="memory">
          <Space direction="vertical" style={{ width: '100%' }} size="large">
            {/* 短期记忆 */}
            <Card
              size="small"
              title={
                <Space>
                  <Checkbox
                    checked={Form.useWatch(['memory_config', 'short_term', 'enabled'], form)}
                    onChange={(e) => {
                      form.setFieldValue(['memory_config', 'short_term', 'enabled'], e.target.checked)
                    }}
                  >
                    短期记忆（当前会话）
                  </Checkbox>
                  <Text type="secondary">- 保存当前对话的上下文</Text>
                </Space>
              }
            >
              <Form.Item
                label="最大对话轮次"
                name={['memory_config', 'short_term', 'max_history_rounds']}
                initialValue={10}
                extra="最多保存的对话轮次，建议5-20轮"
              >
                <InputNumber min={1} max={100} disabled={!Form.useWatch(['memory_config', 'short_term', 'enabled'], form)} />
              </Form.Item>
            </Card>

            {/* 长期记忆 */}
            <Card
              size="small"
              title={
                <Space>
                  <Checkbox
                    checked={Form.useWatch(['memory_config', 'long_term', 'enabled'], form)}
                    onChange={(e) => {
                      form.setFieldValue(['memory_config', 'long_term', 'enabled'], e.target.checked)
                    }}
                  >
                    长期记忆（持久化存储）
                  </Checkbox>
                  <Text type="secondary">- 跨会话持久化存储</Text>
                </Space>
              }
            >
              <Form.Item
                label="存储类型"
                name={['memory_config', 'long_term', 'storage_type']}
                initialValue="file"
                extra="选择长期记忆的存储方式"
              >
                <Select disabled={!Form.useWatch(['memory_config', 'long_term', 'enabled'], form)}>
                  <Option value="file">文件存储</Option>
                  <Option value="database">数据库</Option>
                  <Option value="redis">Redis</Option>
                  <Option value="vector">向量数据库</Option>
                </Select>
              </Form.Item>

              <Form.Item
                label="存储路径"
                name={['memory_config', 'long_term', 'storage_path']}
                initialValue="./memory/agent_memory.json"
                extra="文件存储路径"
                style={{ marginBottom: 8 }}
              >
                <Input disabled={!Form.useWatch(['memory_config', 'long_term', 'enabled'], form)} />
              </Form.Item>

              <Form.Item
                label="数据库连接"
                name={['memory_config', 'long_term', 'connection_string']}
                extra="数据库连接字符串（storage_type为database时）"
                style={{ marginBottom: 8 }}
              >
                <Input disabled={!Form.useWatch(['memory_config', 'long_term', 'enabled'], form)} placeholder="postgresql://user:pass@localhost:5432/dbname" />
              </Form.Item>

              <Form.Item
                label="相似度阈值"
                name={['memory_config', 'long_term', 'vector_config', 'similarity_threshold']}
                initialValue={0.75}
                extra="检索相似度的最低阈值，0-1之间"
              >
                <InputNumber
                  min={0}
                  max={1}
                  step={0.05}
                  disabled={!Form.useWatch(['memory_config', 'long_term', 'enabled'], form)}
                />
              </Form.Item>

              <Form.Item
                label="返回结果数"
                name={['memory_config', 'long_term', 'vector_config', 'top_k']}
                initialValue={3}
                extra="返回最相关的记忆数量"
              >
                <InputNumber min={1} max={10} disabled={!Form.useWatch(['memory_config', 'long_term', 'enabled'], form)} />
              </Form.Item>
            </Card>

            <Card size="small" style={{ backgroundColor: '#f0f5ff' }}>
              <Space>
                <InfoCircleOutlined style={{ color: '#1890ff' }} />
                <Text>
                  可以同时启用多种记忆类型。智能体会按照：短期记忆 → 长期记忆 → 向量记忆的顺序检索信息。
                </Text>
              </Space>
            </Card>
          </Space>
        </Panel>

        {/* 知识库配置 */}
        <Panel header="知识库配置" key="knowledge">
          <Space direction="vertical" style={{ width: '100%' }} size="large">
            <Alert
              message="平台知识库配置"
              description="统一使用平台知识库服务，提供标准化的知识检索和管理功能。配置知识库服务的URL和认证信息。"
              type="info"
              showIcon
            />

            <Card
              size="small"
              title="知识库服务配置"
            >
              <Form.Item
                label="启用平台知识库"
                name={['knowledge_config', 'platform_knowledge', 'enabled']}
                initialValue={true}
                valuePropName="checked"
                extra="是否启用平台知识库服务"
              >
                <Switch />
              </Form.Item>

              <Form.Item
                label="平台知识库URL"
                name={['knowledge_config', 'platform_knowledge', 'platform_url']}
                initialValue="https://knowledge.example.com/api/v1"
                extra="平台知识库服务的API地址"
              >
                <Input disabled={!Form.useWatch(['knowledge_config', 'platform_knowledge', 'enabled'], form)} placeholder="https://knowledge.example.com/api/v1" />
              </Form.Item>

              <Form.Item
                label="认证方式"
                name={['knowledge_config', 'platform_knowledge', 'connection_config', 'authentication', 'type']}
                initialValue="bearer_token"
                extra="选择平台知识库的认证方式"
              >
                <Select disabled={!Form.useWatch(['knowledge_config', 'platform_knowledge', 'enabled'], form)}>
                  <Option value="bearer_token">Bearer Token</Option>
                  <Option value="api_key">API Key</Option>
                  <Option value="oauth2">OAuth 2.0</Option>
                </Select>
              </Form.Item>

              <Form.Item
                label="认证令牌"
                name={['knowledge_config', 'platform_knowledge', 'connection_config', 'authentication', 'token']}
                extra="平台知识库访问令牌"
              >
                <Input.Password disabled={!Form.useWatch(['knowledge_config', 'platform_knowledge', 'enabled'], form)} placeholder="输入访问令牌" />
              </Form.Item>

              <Form.Item
                label="超时时间(秒)"
                name={['knowledge_config', 'platform_knowledge', 'connection_config', 'timeout']}
                initialValue={30}
                extra="知识库请求的超时时间"
              >
                <InputNumber min={5} max={300} disabled={!Form.useWatch(['knowledge_config', 'platform_knowledge', 'enabled'], form)} />
              </Form.Item>
            </Card>

            <Card size="small" title="检索配置">
              <Form.Item
                label="检索模式"
                name={['knowledge_config', 'platform_knowledge', 'retrieval_config', 'retrieval_mode']}
                initialValue="semantic"
                extra="选择知识库的检索模式"
              >
                <Select disabled={!Form.useWatch(['knowledge_config', 'platform_knowledge', 'enabled'], form)}>
                  <Option value="semantic">语义搜索</Option>
                  <Option value="keyword">关键词搜索</Option>
                  <Option value="hybrid">混合搜索</Option>
                </Select>
              </Form.Item>

              <Form.Item
                label="相似度阈值"
                name={['knowledge_config', 'platform_knowledge', 'retrieval_config', 'similarity_threshold']}
                initialValue={0.75}
                extra="检索相似度的最低阈值，0-1之间"
              >
                <InputNumber
                  min={0}
                  max={1}
                  step={0.05}
                  disabled={!Form.useWatch(['knowledge_config', 'platform_knowledge', 'enabled'], form)}
                />
              </Form.Item>

              <Form.Item
                label="返回结果数"
                name={['knowledge_config', 'platform_knowledge', 'retrieval_config', 'top_k']}
                initialValue={5}
                extra="返回最相关的知识数量"
              >
                <InputNumber min={1} max={20} disabled={!Form.useWatch(['knowledge_config', 'platform_knowledge', 'enabled'], form)} />
              </Form.Item>

              <Form.Item
                label="启用上下文增强"
                name={['knowledge_config', 'platform_knowledge', 'retrieval_config', 'enable_context_enhancement']}
                initialValue={true}
                valuePropName="checked"
                extra="是否启用上下文增强功能"
              >
                <Switch disabled={!Form.useWatch(['knowledge_config', 'platform_knowledge', 'enabled'], form)} />
              </Form.Item>

              <Form.Item
                label="上下文窗口大小"
                name={['knowledge_config', 'platform_knowledge', 'retrieval_config', 'context_window_size']}
                initialValue={3}
                extra="上下文增强的窗口大小"
              >
                <InputNumber min={1} max={10} disabled={!Form.useWatch(['knowledge_config', 'platform_knowledge', 'enabled'], form)} />
              </Form.Item>
            </Card>

            <Card size="small" title="权限配置">
              <Form.Item
                label="启用权限控制"
                name={['knowledge_config', 'platform_knowledge', 'permissions', 'enabled']}
                initialValue={true}
                valuePropName="checked"
                extra="是否启用知识库权限控制"
              >
                <Switch disabled={!Form.useWatch(['knowledge_config', 'platform_knowledge', 'enabled'], form)} />
              </Form.Item>

              <Form.Item
                label="每会话最大查询次数"
                name={['knowledge_config', 'platform_knowledge', 'permissions', 'max_queries_per_conversation']}
                initialValue={20}
                extra="单次会话中知识库的最大查询次数"
              >
                <InputNumber min={1} max={1000} disabled={!Form.useWatch(['knowledge_config', 'platform_knowledge', 'permissions', 'enabled'], form)} />
              </Form.Item>

              <Form.Item
                label="允许的操作"
                name={['knowledge_config', 'platform_knowledge', 'permissions', 'allowed_operations']}
                initialValue={['search', 'retrieve', 'summarize']}
                extra="限制对知识库的操作类型"
              >
                <Select
                  mode="multiple"
                  disabled={!Form.useWatch(['knowledge_config', 'platform_knowledge', 'permissions', 'enabled'], form)}
                >
                  <Option value="search">搜索</Option>
                  <Option value="retrieve">检索</Option>
                  <Option value="summarize">摘要</Option>
                </Select>
              </Form.Item>
            </Card>

            {/* 知识库配置说明 */}
            <Card size="small" title="配置说明">
              <Space direction="vertical" style={{ width: '100%' }}>
                <Text strong>🔍 语义搜索</Text>
                <Paragraph style={{ margin: 0 }}>
                  基于向量相似度的智能搜索，能理解语义相关性，找到概念相似的知识内容。
                </Paragraph>

                <Text strong>🔤 关键词搜索</Text>
                <Paragraph style={{ margin: 0 }}>
                  基于关键词匹配的传统搜索，适合精确查找特定术语或专有名词。
                </Paragraph>

                <Text strong>🔄 混合搜索</Text>
                <Paragraph style={{ margin: 0 }}>
                  结合语义搜索和关键词搜索的优势，提供更全面和准确的检索结果。
                </Paragraph>

                <Divider />

                <Text strong>平台知识库优势：</Text>
                <Paragraph>
                  <Text>• 统一的知识管理平台，便于维护和更新</Text>
                  <br />
                  <Text>• 标准化的API接口，易于集成</Text>
                  <br />
                  <Text>• 支持多种认证方式，安全可靠</Text>
                  <br />
                  <Text>• 灵活的检索配置，满足不同需求</Text>
                </Paragraph>
              </Space>
            </Card>

            {/* 快速配置建议 */}
            <Card size="small" style={{ backgroundColor: '#f0f5ff' }}>
              <Space>
                <InfoCircleOutlined style={{ color: '#1890ff' }} />
                <Text>
                  建议根据智能体的具体用途配置检索模式。客服类智能体推荐使用语义搜索，技术类智能体可使用混合搜索以获得更准确的结果。
                </Text>
              </Space>
            </Card>
          </Space>
        </Panel>

        {/* 技能配置 */}
        <Panel header="技能配置" key="skills">
          <Space direction="vertical" style={{ width: '100%' }} size="large">
            <Card
              size="small"
              title={
                <Space>
                  <CloudUploadOutlined />
                  技能上传配置
                </Space>
              }
            >
              <Alert
                message="技能上传方式"
                description="支持通过前端页面上传技能配置文件，符合skill-creator规范的SKILL.md格式。支持单个文件、文件夹和ZIP压缩包三种上传方式。"
                type="info"
                showIcon
                style={{ marginBottom: 16 }}
              />

              <SkillsUploadForm />
            </Card>

            {/* 技能执行配置 */}
            <Card size="small" title="执行配置">
              <Form.Item
                label="最大并发技能数"
                name={['skills_config', 'execution_config', 'max_concurrent_skills']}
                initialValue={5}
                extra="同时执行的最大技能数量"
              >
                <InputNumber min={1} max={20} />
              </Form.Item>

              <Form.Item
                label="单个技能超时时间(秒)"
                name={['skills_config', 'execution_config', 'skill_timeout']}
                initialValue={30}
                extra="单个技能执行的最大时间"
              >
                <InputNumber min={5} max={300} />
              </Form.Item>

              <Form.Item
                label="失败处理策略"
                name={['skills_config', 'execution_config', 'failure_handling_strategy']}
                initialValue="continue"
                extra="技能执行失败时的处理方式"
              >
                <Select>
                  <Option value="continue">继续执行</Option>
                  <Option value="stop">停止执行</Option>
                  <Option value="retry">重试</Option>
                </Select>
              </Form.Item>

              <Form.Item
                label="最大重试次数"
                name={['skills_config', 'execution_config', 'max_retries']}
                initialValue={2}
                extra="技能执行失败时的重试次数"
              >
                <InputNumber min={0} max={10} />
              </Form.Item>
            </Card>

            {/* 技能权限配置 */}
            <Card size="small" title="权限配置">
              <Form.Item
                label="启用权限控制"
                name={['skills_config', 'permissions', 'enabled']}
                initialValue={true}
                valuePropName="checked"
                extra="是否启用技能权限控制"
              >
                <Switch />
              </Form.Item>

              <Form.Item
                label="每会话最大调用次数"
                name={['skills_config', 'permissions', 'max_skill_calls_per_conversation']}
                initialValue={50}
                extra="单次会话中技能的最大调用次数"
              >
                <InputNumber min={1} max={1000} disabled={!Form.useWatch(['skills_config', 'permissions', 'enabled'], form)} />
              </Form.Item>

              <Form.Item
                label="安全级别"
                name={['skills_config', 'permissions', 'security_level']}
                initialValue="medium"
                extra="技能的安全级别"
              >
                <Select disabled={!Form.useWatch(['skills_config', 'permissions', 'enabled'], form)}>
                  <Option value="low">低</Option>
                  <Option value="medium">中</Option>
                  <Option value="high">高</Option>
                  <Option value="critical">严重</Option>
                </Select>
              </Form.Item>

              <Form.Item
                label="允许的技能类别"
                name={['skills_config', 'permissions', 'allowed_skill_categories']}
                initialValue={['text_analysis', 'data_analysis', 'general']}
                extra="限制可使用的技能类别"
              >
                <Select
                  mode="tags"
                  disabled={!Form.useWatch(['skills_config', 'permissions', 'enabled'], form)}
                  placeholder="输入技能类别"
                >
                  <Option value="text_analysis">文本分析</Option>
                  <Option value="data_analysis">数据分析</Option>
                  <Option value="general">通用</Option>
                  <Option value="api_tool">API工具</Option>
                  <Option value="code_execution">代码执行</Option>
                  <Option value="communication">通信协作</Option>
                </Select>
              </Form.Item>
            </Card>

            {/* 技能配置说明 */}
            <Card size="small" title="配置说明">
              <Space direction="vertical" style={{ width: '100%' }}>
                <Text strong>📄 单个文件上传</Text>
                <Paragraph style={{ margin: 0 }}>
                  适合简单的技能配置。只需上传一个符合规范的SKILL.md文件，系统会自动解析并配置。
                </Paragraph>

                <Text strong>📁 文件夹上传</Text>
                <Paragraph style={{ margin: 0 }}>
                  适合包含多个文件的复杂技能。可以包含脚本、参考文档和资源文件，支持更丰富的功能。
                </Paragraph>

                <Text strong>📦 ZIP压缩包上传</Text>
                <Paragraph style={{ margin: 0 }}>
                  适合技能打包分发。将整个技能目录压缩为ZIP文件上传，系统会自动解压并验证文件结构。
                </Paragraph>

                <Divider />

                <Text strong>SKILL.md 文件规范：</Text>
                <Paragraph>
                  <Text>• 必须包含 YAML frontmatter（name 和 description 字段）</Text>
                  <br />
                  <Text>• name: 技能标识符（小写字母、数字、连字符）</Text>
                  <br />
                  <Text>• description: 技能描述（50-500字符，说明何时触发）</Text>
                  <br />
                  <Text>• Markdown body: 技能的具体指令和说明</Text>
                  <br />
                  <Text>• 符合 skill-creator 规范</Text>
                </Paragraph>
              </Space>
            </Card>

            {/* 限制说明 */}
            <Alert
              message="上传限制"
              description={
                <Space direction="vertical" style={{ width: '100%' }}>
                  <Text>• 单个文件大小限制: 3MB</Text>
                  <Text>• 总上传大小限制: 10MB</Text>
                  <Text>• 文件数量限制: 20个（文件夹模式）</Text>
                  <Text>• ZIP包内文件数: 50个</Text>
                  <Text>• 支持的文件格式: .md (SKILL.md), .zip</Text>
                </Space>
              }
              type="warning"
              showIcon
            />
          </Space>
        </Panel>

        {/* 行为控制 */}
        <Panel header="行为控制" key="behavior">
          <Card size="small">
            <Form.Item
              label="最大对话轮次"
              name={['behavior_config', 'max_conversation_rounds']}
              initialValue={20}
              extra="限制单次会话的交互次数"
            >
              <InputNumber min={1} max={100} />
            </Form.Item>

            <Form.Item
              label="自动回复"
              name={['behavior_config', 'auto_reply']}
              initialValue={true}
              valuePropName="checked"
              extra="是否自动响应用户消息"
            >
              <Switch />
            </Form.Item>

            <Form.Item
              label="输出格式"
              name={['behavior_config', 'output_format', 'type']}
              initialValue="text"
            >
              <Space>
                <Text>纯文本</Text>
              </Space>
            </Form.Item>
          </Card>
        </Panel>

        {/* 监控与日志 */}
        <Panel header="监控与日志" key="monitoring">
          <Card size="small">
            <Form.Item
              label="日志级别"
              name={['monitoring_config', 'log_level']}
              initialValue="INFO"
            >
              <Space>
                <Text>INFO</Text>
              </Space>
            </Form.Item>

            <Form.Item
              label="性能监控"
              name={['monitoring_config', 'enable_performance_tracking']}
              initialValue={true}
              valuePropName="checked"
            >
              <Switch />
            </Form.Item>

            <Form.Item
              label="保存对话历史"
              name={['monitoring_config', 'save_conversation_history']}
              initialValue={true}
              valuePropName="checked"
            >
              <Switch />
            </Form.Item>
          </Card>
        </Panel>
      </Collapse>
    </Form>
  )
}

export default AdvancedConfigForm