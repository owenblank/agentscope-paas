import { useState, useCallback } from 'react'
import { Form, Upload, Button, Card, Space, Typography, Alert, Tabs, Progress, Tag, message, Modal, Divider, Row, Col } from 'antd'
import { InboxOutlined, FileOutlined, FolderOutlined, FileZipOutlined, CheckCircleOutlined, LoadingOutlined, DeleteOutlined } from '@ant-design/icons'
import type { UploadFile, UploadProps } from 'antd'
import { useAgentFormStore } from '@/store'

const { Text, Paragraph, Title } = Typography
const { Dragger } = Upload
const { TabPane } = Tabs

interface SkillFile {
  uid: string
  name: string
  size: number
  type: string
  status: 'uploading' | 'done' | 'error'
  url?: string
  response?: any
  skillName?: string
  skillDescription?: string
}

const SkillsUploadForm = () => {
  const { formData, updateFormData } = useAgentFormStore()
  const [fileList, setFileList] = useState<SkillFile[]>([])
  const [uploading, setUploading] = useState(false)
  const [uploadProgress, setUploadProgress] = useState(0)
  const [uploadedSkills, setUploadedSkills] = useState<any[]>([])

  // 更新表单数据
  const updateSkillsConfig = useCallback((skills: any[]) => {
    updateFormData({
      skills_config: {
        load_mode: 'upload',
        upload_config: {
          supported_upload_methods: [
            {
              method: 'single_file',
              enabled: true,
              description: '上传单个SKILL.md文件',
              max_size_mb: 3,
              supported_formats: ['.md']
            },
            {
              method: 'folder',
              enabled: true,
              description: '上传包含技能文件的文件夹',
              max_size_mb: 3,
              supported_formats: ['.md']
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
                overwrite_existing: false
              }
            }
          ],
          max_file_size_mb: 3,
          max_total_size_mb: 10,
          max_files_per_upload: 20,
          validation_config: {
            validate_format: true,
            validate_size: true,
            validate_content: true,
            validate_schema: true,
            allowed_encodings: ['utf-8', 'utf-8-sig', 'ascii']
          },
          security_config: {
            enable_virus_scan: false,
            enable_malware_scan: true,
            verify_signature: false,
            allowed_mime_types: ['text/markdown', 'text/plain', 'application/zip']
          },
          storage_config: {
            storage_type: 'local',
            local_storage_path: './uploads/skills/',
            temp_storage_path: './temp/skills/',
            preserve_filename: true,
            naming_rule: 'preserve_original'
          },
          processing_config: {
            auto_parse_skill_md: true,
            extract_frontmatter: true,
            validate_structure: true,
            generate_preview: true,
            index_content: true
          }
        },
        execution_config: {
          max_concurrent_skills: 5,
          skill_timeout: 30,
          failure_handling_strategy: 'continue',
          max_retries: 2
        },
        permissions: {
          enabled: true,
          max_skill_calls_per_conversation: 50,
          allowed_skill_categories: ['text_analysis', 'data_analysis', 'general', 'api_tool', 'code_execution'],
          security_level: 'medium',
          upload_permissions: {
            allowed_roles: ['admin', 'developer', 'user'],
            require_moderation: false,
            allow_overwrite: true,
            allow_deletion: true
          }
        }
      }
    })
  }, [updateFormData])

  // 验证文件大小
  const validateFileSize = (file: File): boolean => {
    const maxSize = 3 * 1024 * 1024 // 3MB
    if (file.size > maxSize) {
      message.error(`文件 ${file.name} 大小超过3MB限制`)
      return false
    }
    return true
  }

  // 验证文件类型
  const validateFileType = (file: File, uploadType: string): boolean => {
    const validExtensions = uploadType === 'zip' ? ['.zip'] : ['.md']
    const fileExtension = '.' + file.name.split('.').pop()?.toLowerCase()

    if (!validExtensions.includes(fileExtension)) {
      message.error(`不支持的文件类型：${fileExtension}，请上传 ${validExtensions.join(' 或 ')} 文件`)
      return false
    }
    return true
  }

  // 模拟文件上传
  const mockUpload = (file: SkillFile): Promise<SkillFile> => {
    return new Promise((resolve) => {
      let progress = 0
      const interval = setInterval(() => {
        progress += 10
        setUploadProgress(progress)

        if (progress >= 100) {
          clearInterval(interval)
          // 模拟解析SKILL.md文件
          const mockSkill = {
            name: file.name.replace('.md', '').replace('.zip', ''),
            description: `从 ${file.name} 解析的技能`,
            status: 'done'
          }
          resolve({
            ...file,
            status: 'done',
            skillName: mockSkill.name,
            skillDescription: mockSkill.description
          })
        }
      }, 200)
    })
  }

  // 单个文件上传处理
  const handleSingleFileUpload: UploadProps['customRequest'] = async (options) => {
    const { file, onSuccess, onError } = options

    if (!validateFileSize(file as File) || !validateFileType(file as File, 'single')) {
      onError?.(new Error('文件验证失败'))
      return
    }

    setUploading(true)
    try {
      const result = await mockUpload(file as SkillFile)
      setUploadedSkills(prev => [...prev, result])
      onSuccess?.(result)
      message.success('技能文件上传成功')
    } catch (error) {
      onError?.(error as Error)
      message.error('技能文件上传失败')
    } finally {
      setUploading(false)
      setUploadProgress(0)
    }
  }

  // 文件夹上传处理
  const handleFolderUpload: UploadProps['customRequest'] = async (options) => {
    const { file, onSuccess, onError } = options

    if (!validateFileSize(file as File) || !validateFileType(file as File, 'folder')) {
      onError?.(new Error('文件验证失败'))
      return
    }

    setUploading(true)
    try {
      const result = await mockUpload(file as SkillFile)
      setUploadedSkills(prev => [...prev, result])
      onSuccess?.(result)
      message.success('技能文件夹上传成功')
    } catch (error) {
      onError?.(error as Error)
      message.error('技能文件夹上传失败')
    } finally {
      setUploading(false)
      setUploadProgress(0)
    }
  }

  // ZIP压缩包上传处理
  const handleZipUpload: UploadProps['customRequest'] = async (options) => {
    const { file, onSuccess, onError } = options

    if (!validateFileSize(file as File) || !validateFileType(file as File, 'zip')) {
      onError?.(new Error('文件验证失败'))
      return
    }

    setUploading(true)
    try {
      const result = await mockUpload(file as SkillFile)
      setUploadedSkills(prev => [...prev, result])
      onSuccess?.(result)
      message.success('技能压缩包上传成功')
    } catch (error) {
      onError?.(error as Error)
      message.error('技能压缩包上传失败')
    } finally {
      setUploading(false)
      setUploadProgress(0)
    }
  }

  // 删除技能
  const handleDeleteSkill = (uid: string) => {
    setUploadedSkills(prev => prev.filter(skill => skill.uid !== uid))
    message.success('技能删除成功')
  }

  // 格式化文件大小
  const formatFileSize = (bytes: number): string => {
    if (bytes === 0) return '0 B'
    const k = 1024
    const sizes = ['B', 'KB', 'MB', 'GB']
    const i = Math.floor(Math.log(bytes) / Math.log(k))
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
  }

  return (
    <Space direction="vertical" style={{ width: '100%' }} size="large">
      {/* 上传说明 */}
      <Alert
        message="技能上传配置"
        description="支持上传符合skill-creator规范的SKILL.md文件。文件大小限制为3MB，支持单个文件、文件夹和ZIP压缩包三种上传方式。"
        type="info"
        showIcon
      />

      {/* 上传方式选择 */}
      <Card title="选择上传方式" size="small">
        <Tabs defaultActiveKey="single">
          {/* 单个文件上传 */}
          <TabPane tab={
            <Space>
              <FileOutlined />
              单个文件
            </Space>
          } key="single">
            <Space direction="vertical" style={{ width: '100%' }} size="middle">
              <Paragraph>
                <Text strong>上传单个SKILL.md文件</Text>
                <br />
                <Text type="secondary">文件必须符合skill-creator规范，包含YAML frontmatter和Markdown body</Text>
              </Paragraph>

              <Dragger
                accept=".md"
                multiple={false}
                customRequest={handleSingleFileUpload}
                disabled={uploading}
                showUploadList={false}
              >
                <p className="ant-upload-drag-icon">
                  <InboxOutlined />
                </p>
                <p className="ant-upload-text">点击或拖拽SKILL.md文件到此区域上传</p>
                <p className="ant-upload-hint">
                  支持单个.md文件上传，文件大小不超过3MB
                </p>
              </Dragger>

              {uploading && (
                <Progress percent={uploadProgress} status="active" />
              )}
            </Space>
          </TabPane>

          {/* 文件夹上传 */}
          <TabPane tab={
            <Space>
              <FolderOutlined />
              文件夹
            </Space>
          } key="folder">
            <Space direction="vertical" style={{ width: '100%' }} size="middle">
              <Paragraph>
                <Text strong>上传包含技能文件的文件夹</Text>
                <br />
                <Text type="secondary">文件夹必须包含SKILL.md文件，可选择包含scripts/、references/、assets/目录</Text>
              </Paragraph>

              <Dragger
                accept=".md"
                multiple
                directory
                customRequest={handleFolderUpload}
                disabled={uploading}
                showUploadList={false}
              >
                <p className="ant-upload-drag-icon">
                  <FolderOutlined />
                </p>
                <p className="ant-upload-text">点击或拖拽文件夹到此区域上传</p>
                <p className="ant-upload-hint">
                  支持文件夹上传，总大小不超过3MB，最多20个文件
                </p>
              </Dragger>

              {uploading && (
                <Progress percent={uploadProgress} status="active" />
              )}
            </Space>
          </TabPane>

          {/* ZIP压缩包上传 */}
          <TabPane tab={
            <Space>
              <FileZipOutlined />
              ZIP压缩包
            </Space>
          } key="zip">
            <Space direction="vertical" style={{ width: '100%' }} size="middle">
              <Paragraph>
                <Text strong>上传ZIP格式的技能压缩包</Text>
                <br />
                <Text type="secondary">压缩包根目录必须包含SKILL.md文件，可选择包含其他资源文件</Text>
              </Paragraph>

              <Dragger
                accept=".zip"
                multiple={false}
                customRequest={handleZipUpload}
                disabled={uploading}
                showUploadList={false}
              >
                <p className="ant-upload-drag-icon">
                  <FileZipOutlined />
                </p>
                <p className="ant-upload-text">点击或拖拽ZIP文件到此区域上传</p>
                <p className="ant-upload-hint">
                  支持ZIP格式，文件大小不超过3MB，最多包含50个文件
                </p>
              </Dragger>

              {uploading && (
                <Progress percent={uploadProgress} status="active" />
              )}
            </Space>
          </TabPane>
        </Tabs>
      </Card>

      {/* 已上传技能列表 */}
      {uploadedSkills.length > 0 && (
        <Card title="已上传技能" size="small">
          <Space direction="vertical" style={{ width: '100%' }} size="middle">
            {uploadedSkills.map((skill) => (
              <Card
                key={skill.uid}
                size="small"
                style={{ backgroundColor: '#f0f5ff' }}
                extra={
                  <Button
                    type="text"
                    danger
                    icon={<DeleteOutlined />}
                    onClick={() => handleDeleteSkill(skill.uid)}
                  >
                    删除
                  </Button>
                }
              >
                <Space direction="vertical" style={{ width: '100%' }}>
                  <Space>
                    <CheckCircleOutlined style={{ color: '#52c41a' }} />
                    <Text strong>{skill.skillName || skill.name}</Text>
                    <Tag color="success">已上传</Tag>
                  </Space>
                  <Text type="secondary">{skill.skillDescription}</Text>
                  <Text type="secondary" style={{ fontSize: 12 }}>
                    文件大小: {formatFileSize(skill.size)}
                  </Text>
                </Space>
              </Card>
            ))}
          </Space>

          <Divider />

          <Space>
            <Text strong>总计:</Text>
            <Text>{uploadedSkills.length} 个技能</Text>
            <Text type="secondary">
              ({uploadedSkills.reduce((acc, skill) => acc + skill.size, 0) > 0
                ? formatFileSize(uploadedSkills.reduce((acc, skill) => acc + skill.size, 0))
                : '0 B'})
            </Text>
          </Space>
        </Card>
      )}

      {/* 技能配置说明 */}
      <Card title="配置说明" size="small">
        <Row gutter={[16, 16]}>
          <Col span={8}>
            <Card size="small" type="inner" title="📄 单个文件">
              <Paragraph style={{ margin: 0 }}>
                适合简单的技能配置。只需上传一个符合规范的SKILL.md文件，系统会自动解析并配置。
              </Paragraph>
            </Card>
          </Col>
          <Col span={8}>
            <Card size="small" type="inner" title="📁 文件夹">
              <Paragraph style={{ margin: 0 }}>
                适合包含多个文件的复杂技能。可以包含脚本、参考文档和资源文件。
              </Paragraph>
            </Card>
          </Col>
          <Col span={8}>
            <Card size="small" type="inner" title="📦 ZIP压缩包">
              <Paragraph style={{ margin: 0 }}>
                适合技能打包分发。将整个技能目录压缩为ZIP文件上传，系统会自动解压。
              </Paragraph>
            </Card>
          </Col>
        </Row>

        <Divider />

        <Space direction="vertical" style={{ width: '100%' }}>
          <Text strong>SKILL.md 文件规范：</Text>
          <Paragraph>
            <Text>• 必须包含 YAML frontmatter（name 和 description 字段）</Text>
            <br />
            <Text>• name: 技能标识符（小写字母、数字、连字符）</Text>
            <br />
            <Text>• description: 技能描述（50-500字符）</Text>
            <br />
            <Text>• Markdown body: 技能的具体指令和说明</Text>
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
  )
}

export default SkillsUploadForm