import { Card, Descriptions, Typography, Tag } from 'antd'
import yaml from 'js-yaml'
import type { AgentConfig } from '@/types'

const { Text } = Typography

interface ConfigPreviewProps {
  data: Partial<AgentConfig>
}

const ConfigPreview = ({ data }: ConfigPreviewProps) => {
  const configPreview = {
    agent_metadata: data.agent_metadata,
    model_config: {
      model_name: data.model_config?.model_name,
      temperature: data.model_config?.temperature,
      max_tokens: data.model_config?.max_tokens,
    },
    prompt_config: data.prompt_config,
  }

  const yamlContent = yaml.dump(configPreview, {
    indent: 2,
    lineWidth: -1,
    noRefs: true,
    sortKeys: false,
  })

  return (
    <Card size="small">
      <Descriptions column={2} size="small" bordered>
        <Descriptions.Item label="智能体名称">
          {data.agent_metadata?.agent_name || '-'}
        </Descriptions.Item>
        <Descriptions.Item label="智能体类型">
          <Tag color="blue">{data.agent_metadata?.agent_type}</Tag>
        </Descriptions.Item>
        <Descriptions.Item label="模型">
          {data.model_config?.model_name || '-'}
        </Descriptions.Item>
        <Descriptions.Item label="温度">
          {data.model_config?.temperature || '-'}
        </Descriptions.Item>
        <Descriptions.Item label="最大Tokens">
          {data.model_config?.max_tokens || '-'}
        </Descriptions.Item>
        <Descriptions.Item label="提示词长度">
          {data.prompt_config?.system_prompt?.length || 0} 字符
        </Descriptions.Item>
      </Descriptions>

      {data.prompt_config?.system_prompt && (
        <div style={{ marginTop: 16 }}>
          <Text strong>系统提示词预览：</Text>
          <Card
            size="small"
            style={{
              marginTop: 8,
              backgroundColor: '#f5f5f5',
              maxHeight: 200,
              overflow: 'auto',
            }}
          >
            <pre style={{ whiteSpace: 'pre-wrap', fontFamily: 'inherit', margin: 0 }}>
              {data.prompt_config.system_prompt.substring(0, 500)}
              {data.prompt_config.system_prompt.length > 500 ? '...' : ''}
            </pre>
          </Card>
        </div>
      )}

      <div style={{ marginTop: 16 }}>
        <Text strong>YAML配置：</Text>
        <Card
          size="small"
          style={{
            marginTop: 8,
            backgroundColor: '#f5f5f5',
            maxHeight: 300,
            overflow: 'auto',
          }}
        >
          <pre style={{ whiteSpace: 'pre', fontFamily: 'monospace', fontSize: 12, margin: 0 }}>
            {yamlContent}
          </pre>
        </Card>
      </div>
    </Card>
  )
}

export default ConfigPreview
