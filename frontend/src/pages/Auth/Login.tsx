/**
 * User login page
 */
import { useState } from 'react'
import { Form, Input, Button, Card, Typography, App, Space } from 'antd'
import { UserOutlined, LockOutlined } from '@ant-design/icons'
import { useNavigate, useLocation } from 'react-router-dom'
import { useAuthStore } from '@/store'

const { Title, Text } = Typography

interface LoginFormData {
  email: string
  password: string
}

export const Login: React.FC = () => {
  const navigate = useNavigate()
  const location = useLocation()
  const { login, isLoading } = useAuthStore()
  const { message } = App.useApp()
  const [form] = Form.useForm()

  const from = (location.state as any)?.from?.pathname || '/'

  const onFinish = async (values: LoginFormData) => {
    try {
      await login(values.email, values.password)
      message.success('登录成功')
      setTimeout(() => {
        navigate(from, { replace: true })
      }, 100)
    } catch (error) {
      // Error is handled by the store
      message.error('登录失败，请检查邮箱和密码')
    }
  }

  return (
    <div
      style={{
        display: 'flex',
        justifyContent: 'center',
        alignItems: 'center',
        minHeight: '100vh',
        background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
      }}
    >
      <Card
        style={{
          width: 400,
          boxShadow: '0 4px 12px rgba(0,0,0,0.15)',
        }}
      >
        <div style={{ textAlign: 'center', marginBottom: 24 }}>
          <Title level={2}>AgentScope PaaS</Title>
          <Text type="secondary">登录您的账户</Text>
        </div>

        <Form
          form={form}
          name="login"
          onFinish={onFinish}
          autoComplete="off"
          size="large"
        >
          <Form.Item
            name="email"
            rules={[
              { required: true, message: '请输入邮箱' },
              { type: 'email', message: '请输入有效的邮箱地址' },
            ]}
          >
            <Input
              prefix={<UserOutlined />}
              placeholder="邮箱"
            />
          </Form.Item>

          <Form.Item
            name="password"
            rules={[{ required: true, message: '请输入密码' }]}
          >
            <Input.Password
              prefix={<LockOutlined />}
              placeholder="密码"
            />
          </Form.Item>

          <Form.Item>
            <Button
              type="primary"
              htmlType="submit"
              loading={isLoading}
              block
            >
              登录
            </Button>
          </Form.Item>

          <div style={{ textAlign: 'center' }}>
            <Space>
              <Text>还没有账户？</Text>
              <a onClick={() => navigate('/register')}>立即注册</a>
            </Space>
          </div>
        </Form>
      </Card>
    </div>
  )
}