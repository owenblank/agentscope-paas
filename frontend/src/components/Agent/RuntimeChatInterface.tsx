/**
 * Runtime Chat Interface Component
 *
 * Provides real-time streaming chat interface with Server-Sent Events (SSE)
 * support for Runtime agent conversations.
 */

import React, { useState, useRef, useEffect, useCallback } from 'react'
import {
  Card,
  Input,
  Button,
  Space,
  Typography,
  Alert,
  Tag,
  Divider,
  Tooltip,
  Badge,
  Switch,
  message,
  Spin,
  Progress
} from 'antd'
import {
  SendOutlined,
  ThunderboltOutlined,
  CloseCircleOutlined,
  CheckCircleOutlined,
  LoadingOutlined,
  ClearOutlined,
  PauseCircleOutlined,
  PlayCircleOutlined,
  RobotOutlined,
  UserOutlined
} from '@ant-design/icons'
import type { RuntimeChatResponse } from '@/types/agent'

const { TextArea } = Input
const { Text, Title, Paragraph } = Typography

interface Message {
  id: string
  role: 'user' | 'assistant' | 'system'
  content: string
  timestamp: Date
  status?: 'sending' | 'streaming' | 'completed' | 'error'
  metadata?: {
    agent_id?: string
    stream_position?: number
    error?: string
  }
}

interface RuntimeChatInterfaceProps {
  agentId: string
  agentName?: string
  deploymentUrl?: string
  runtimeAvailable?: boolean
  onSendMessage?: (message: string, stream: boolean) => Promise<string>
  className?: string
  disabled?: boolean
}

const RuntimeChatInterface: React.FC<RuntimeChatInterfaceProps> = ({
  agentId,
  agentName = 'Agent',
  deploymentUrl,
  runtimeAvailable = true,
  onSendMessage,
  className = '',
  disabled = false
}) => {
  const [messages, setMessages] = useState<Message[]>([])
  const [inputMessage, setInputMessage] = useState('')
  const [isStreaming, setIsStreaming] = useState(false)
  const [isPaused, setIsPaused] = useState(false)
  const [useStreaming, setUseStreaming] = useState(true)
  const [currentResponse, setCurrentResponse] = useState('')
  const [connectionStatus, setConnectionStatus] = useState<'disconnected' | 'connecting' | 'connected' | 'error'>('disconnected')
  const [streamProgress, setStreamProgress] = useState(0)

  const messagesEndRef = useRef<HTMLDivElement>(null)
  const eventSourceRef = useRef<EventSource | null>(null)
  const currentMessageIdRef = useRef<string | null>(null)

  // Auto-scroll to bottom
  const scrollToBottom = useCallback(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [])

  useEffect(() => {
    scrollToBottom()
  }, [messages, currentResponse, scrollToBottom])

  // Cleanup EventSource on unmount
  useEffect(() => {
    return () => {
      if (eventSourceRef.current) {
        eventSourceRef.current.close()
      }
    }
  }, [])

  const handleSendMessage = async () => {
    if (!inputMessage.trim() || isStreaming) {
      return
    }

    const userMessage: Message = {
      id: `user-${Date.now()}`,
      role: 'user',
      content: inputMessage,
      timestamp: new Date(),
      status: 'completed'
    }

    setMessages(prev => [...prev, userMessage])
    setInputMessage('')

    if (useStreaming && deploymentUrl) {
      await handleStreamingChat(userMessage)
    } else if (onSendMessage) {
      await handleRegularChat(userMessage)
    }
  }

  const handleStreamingChat = async (userMessage: Message) => {
    setIsStreaming(true)
    setConnectionStatus('connecting')
    setCurrentResponse('')
    setStreamProgress(0)

    const messageId = `assistant-${Date.now()}`
    currentMessageIdRef.current = messageId

    // Add placeholder for streaming response
    const assistantMessage: Message = {
      id: messageId,
      role: 'assistant',
      content: '',
      timestamp: new Date(),
      status: 'streaming',
      metadata: { agent_id: agentId }
    }

    setMessages(prev => [...prev, assistantMessage])

    try {
      // Create EventSource for SSE
      const sseUrl = `${deploymentUrl}/api/v1/agents/${agentId}/chat/runtime`

      const response = await fetch(sseUrl, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          message: userMessage.content,
          stream: true,
          user_id: 'web_user',
          session_id: `session_${Date.now()}`
        })
      })

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`)
      }

      setConnectionStatus('connected')

      const reader = response.body?.getReader()
      const decoder = new TextDecoder()

      if (!reader) {
        throw new Error('Response body is null')
      }

      let buffer = ''
      let chunkCount = 0
      const startTime = Date.now()

      while (true) {
        const { done, value } = await reader.read()

        if (done || isPaused) {
          break
        }

        buffer += decoder.decode(value, { stream: true })
        const lines = buffer.split('\n')
        buffer = lines.pop() || ''

        for (const line of lines) {
          if (line.startsWith('data: ')) {
            try {
              const data = JSON.parse(line.slice(6))

              if (data.type === 'connected') {
                setConnectionStatus('connected')
              } else if (data.type === 'chunk') {
                chunkCount++
                const newContent = data.content || ''
                setCurrentResponse(prev => prev + newContent)

                // Update progress estimation
                const elapsed = (Date.now() - startTime) / 1000
                setStreamProgress(Math.min(95, elapsed * 10)) // Estimation

                // Update message content
                setMessages(prev =>
                  prev.map(msg =>
                    msg.id === messageId
                      ? { ...msg, content: (msg.content || '') + newContent }
                      : msg
                  )
                )
              } else if (data.type === 'complete') {
                setStreamProgress(100)
                setMessages(prev =>
                  prev.map(msg =>
                    msg.id === messageId
                      ? { ...msg, status: 'completed' as const }
                      : msg
                  )
                )
              } else if (data.type === 'error') {
                throw new Error(data.error || 'Stream error')
              }
            } catch (parseError) {
              console.error('Error parsing SSE data:', parseError)
            }
          }
        }
      }

    } catch (error) {
      console.error('Streaming error:', error)
      setConnectionStatus('error')
      setMessages(prev =>
        prev.map(msg =>
          msg.id === messageId
            ? {
                ...msg,
                status: 'error' as const,
                metadata: {
                  ...msg.metadata,
                  error: error instanceof Error ? error.message : 'Unknown error'
                }
              }
            : msg
        )
      )
      message.error('Failed to connect to streaming service')
    } finally {
      setIsStreaming(false)
      setCurrentResponse('')
      currentMessageIdRef.current = null
      setStreamProgress(0)
    }
  }

  const handleRegularChat = async (userMessage: Message) => {
    setIsStreaming(true)

    const messageId = `assistant-${Date.now()}`

    const assistantMessage: Message = {
      id: messageId,
      role: 'assistant',
      content: '',
      timestamp: new Date(),
      status: 'sending',
      metadata: { agent_id: agentId }
    }

    setMessages(prev => [...prev, assistantMessage])

    try {
      const response = await onSendMessage!(userMessage.content, false)

      setMessages(prev =>
        prev.map(msg =>
          msg.id === messageId
            ? {
                ...msg,
                content: response,
                status: 'completed' as const
              }
            : msg
        )
      )
    } catch (error) {
      setMessages(prev =>
        prev.map(msg =>
          msg.id === messageId
            ? {
                ...msg,
                status: 'error' as const,
                metadata: {
                  ...msg.metadata,
                  error: error instanceof Error ? error.message : 'Unknown error'
                }
              }
            : msg
        )
      )
      message.error('Failed to send message')
    } finally {
      setIsStreaming(false)
    }
  }

  const handleClearChat = () => {
    setMessages([])
    setCurrentResponse('')
    setStreamProgress(0)
  }

  const handlePauseResume = () => {
    if (isPaused) {
      // Resume - trigger new request
      setIsPaused(false)
    } else {
      // Pause - will be handled in streaming loop
      setIsPaused(true)
      setConnectionStatus('disconnected')
    }
  }

  const getConnectionStatusIcon = () => {
    switch (connectionStatus) {
      case 'connected':
        return <CheckCircleOutlined style={{ color: '#52c41a' }} />
      case 'connecting':
        return <LoadingOutlined />
      case 'error':
        return <CloseCircleOutlined style={{ color: '#ff4d4f' }} />
      default:
        return <CloseCircleOutlined style={{ color: '#d9d9d9' }} />
    }
  }

  const renderMessage = (msg: Message) => {
    const isError = msg.status === 'error'
    const isStreaming = msg.status === 'streaming'

    return (
      <div
        key={msg.id}
        className={`message-item ${msg.role} ${isError ? 'error' : ''} ${isStreaming ? 'streaming' : ''}`}
        style={{
          display: 'flex',
          marginBottom: 16,
          justifyContent: msg.role === 'user' ? 'flex-end' : 'flex-start'
        }}
      >
        <div style={{ maxWidth: '70%' }}>
          <Space size={8} style={{ marginBottom: 4 }}>
            {msg.role === 'user' ? (
              <UserOutlined style={{ color: '#1890ff' }} />
            ) : (
              <RobotOutlined style={{ color: '#52c41a' }} />
            )}
            <Text type="secondary" style={{ fontSize: '12px' }}>
              {msg.role === 'user' ? 'You' : agentName}
            </Text>
            <Text type="secondary" style={{ fontSize: '12px' }}>
              {msg.timestamp.toLocaleTimeString()}
            </Text>
            {msg.status && (
              <Tag
                color={
                  msg.status === 'completed' ? 'success' :
                  msg.status === 'streaming' ? 'processing' :
                  msg.status === 'error' ? 'error' : 'default'
                }
                style={{ fontSize: '10px', margin: 0 }}
              >
                {msg.status}
              </Tag>
            )}
          </Space>

          <Card
            size="small"
            style={{
              backgroundColor: msg.role === 'user' ? '#e6f7ff' : '#f6ffed',
              borderColor: isError ? '#ff4d4f' : undefined
            }}
          >
            {isError ? (
              <Alert
                message="Error"
                description={msg.metadata?.error || 'Failed to process message'}
                type="error"
                size="small"
              />
            ) : (
              <Paragraph
                style={{ margin: 0, whiteSpace: 'pre-wrap' }}
                className={isStreaming ? 'streaming-text' : ''}
              >
                {msg.content || (isStreaming && <Spin size="small" />)}
              </Paragraph>
            )}
          </Card>
        </div>
      </div>
    )
  }

  return (
    <div className={`runtime-chat-interface ${className}`}>
      <Card
        title={
          <Space>
            <ThunderboltOutlined />
            <span>Chat with {agentName}</span>
            <Badge
              status={connectionStatus === 'connected' ? 'processing' : 'default'}
              text={
                <Text type="secondary" style={{ fontSize: '12px' }}>
                  {connectionStatus}
                </Text>
              }
            />
          </Space>
        }
        extra={
          <Space>
            <Tooltip title="Enable streaming responses">
              <Switch
                checked={useStreaming}
                onChange={setUseStreaming}
                disabled={isStreaming}
                checkedChildren="Streaming"
                unCheckedChildren="Regular"
              />
            </Tooltip>
            <Button
              type="text"
              icon={<ClearOutlined />}
              onClick={handleClearChat}
              disabled={isStreaming}
            >
              Clear
            </Button>
          </Space>
        }
        styles={{ body: { padding: 0 } }}
      >
        {/* Messages Area */}
        <div
          style={{
            height: '400px',
            overflowY: 'auto',
            padding: '16px',
            backgroundColor: '#fafafa'
          }}
        >
          {messages.length === 0 ? (
            <div
              style={{
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                height: '100%',
                flexDirection: 'column',
                color: '#999'
              }}
            >
              <RobotOutlined style={{ fontSize: 48, marginBottom: 16 }} />
              <Text type="secondary">Start a conversation with {agentName}</Text>
            </div>
          ) : (
            <>
              {messages.map(renderMessage)}
              {isStreaming && currentResponse && (
                <div className="message-item assistant streaming">
                  <div style={{ maxWidth: '70%' }}>
                    <Space size={8} style={{ marginBottom: 4 }}>
                      <RobotOutlined style={{ color: '#52c41a' }} />
                      <Text type="secondary" style={{ fontSize: '12px' }}>
                        {agentName}
                      </Text>
                      <Tag color="processing" style={{ fontSize: '10px', margin: 0 }}>
                        streaming
                      </Tag>
                    </Space>
                    <Card size="small" style={{ backgroundColor: '#f6ffed' }}>
                      <Paragraph style={{ margin: 0, whiteSpace: 'pre-wrap' }}>
                        {currentResponse}
                      </Paragraph>
                      {streamProgress > 0 && streamProgress < 100 && (
                        <Progress
                          percent={streamProgress}
                          size="small"
                          status="active"
                          style={{ marginTop: 8 }}
                        />
                      )}
                    </Card>
                  </div>
                </div>
              )}
              <div ref={messagesEndRef} />
            </>
          )}
        </div>

        {/* Input Area */}
        <Divider style={{ margin: 0 }} />

        <div style={{ padding: '16px' }}>
          {!runtimeAvailable && (
            <Alert
              message="Runtime Not Available"
              description="Streaming features require AgentScope Runtime installation."
              type="warning"
              closable
              style={{ marginBottom: 12 }}
            />
          )}

          <Space.Compact style={{ width: '100%' }}>
            <TextArea
              value={inputMessage}
              onChange={(e) => setInputMessage(e.target.value)}
              placeholder="Type your message..."
              autoSize={{ minRows: 1, maxRows: 4 }}
              disabled={disabled || isStreaming}
              onPressEnter={(e) => {
                if (e.shiftKey) {
                  return // Allow new lines with Shift+Enter
                }
                e.preventDefault()
                handleSendMessage()
              }}
            />
            <Button
              type="primary"
              icon={<SendOutlined />}
              onClick={handleSendMessage}
              disabled={!inputMessage.trim() || isStreaming || disabled}
              loading={isStreaming}
            >
              Send
            </Button>
          </Space.Compact>

          {isStreaming && (
            <div style={{ marginTop: 8 }}>
              <Space>
                <Button
                  size="small"
                  icon={isPaused ? <PlayCircleOutlined /> : <PauseCircleOutlined />}
                  onClick={handlePauseResume}
                >
                  {isPaused ? 'Resume' : 'Pause'}
                </Button>
                <Text type="secondary" style={{ fontSize: '12px' }}>
                  Streaming in progress...
                </Text>
                <Badge status="processing" text="" />
              </Space>
            </div>
          )}

          <div style={{ marginTop: 8 }}>
            <Text type="secondary" style={{ fontSize: '12px' }}>
              Press Enter to send, Shift+Enter for new line
            </Text>
          </div>
        </div>
      </Card>
    </div>
  )
}

export default RuntimeChatInterface