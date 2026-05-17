import { Layout as AntLayout, Menu, Dropdown, Avatar } from 'antd'
import {
  HomeOutlined,
  RobotOutlined,
  TeamOutlined,
  MessageOutlined,
  DashboardOutlined,
  SettingOutlined,
  UserOutlined,
  LogoutOutlined,
} from '@ant-design/icons'
import { useNavigate, useLocation } from 'react-router-dom'
import { useAuthStore } from '@/store'

const { Header, Sider, Content } = AntLayout

export const MainLayout: React.FC<{ children?: React.ReactNode }> = ({
  children,
}) => {
  const navigate = useNavigate()
  const location = useLocation()
  const { user, logout } = useAuthStore()

  const menuItems = [
    {
      key: '/dashboard',
      icon: <HomeOutlined />,
      label: '仪表板',
      onClick: () => navigate('/dashboard'),
    },
    {
      key: '/agents',
      icon: <RobotOutlined />,
      label: '智能体管理',
      onClick: () => navigate('/agents'),
    },
    {
      key: '/teams',
      icon: <TeamOutlined />,
      label: '团队管理',
      onClick: () => navigate('/teams'),
    },
    {
      key: '/conversation',
      icon: <MessageOutlined />,
      label: '对话',
      onClick: () => navigate('/conversation'),
    },
    {
      key: '/monitoring',
      icon: <DashboardOutlined />,
      label: '监控中心',
      onClick: () => navigate('/monitoring'),
    },
    {
      key: '/settings',
      icon: <SettingOutlined />,
      label: '设置',
      onClick: () => navigate('/settings'),
    },
  ]

  const userMenuItems = [
    {
      key: 'profile',
      icon: <UserOutlined />,
      label: '个人信息',
      onClick: () => navigate('/settings'),
    },
    {
      key: 'logout',
      icon: <LogoutOutlined />,
      label: '退出登录',
      onClick: () => {
        logout()
        navigate('/login')
      },
    },
  ]

  return (
    <Layout style={{ minHeight: '100vh' }}>
      <Sider theme="dark" width={240}>
        <div
          style={{
            height: 64,
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            color: 'white',
            fontSize: 18,
            fontWeight: 'bold',
          }}
        >
          AgentScope PaaS
        </div>
        <Menu
          theme="dark"
          mode="inline"
          selectedKeys={[location.pathname]}
          items={menuItems}
        />
      </Sider>
      <Layout>
        <Header
          style={{
            background: '#fff',
            padding: '0 24px',
            display: 'flex',
            justifyContent: 'space-between',
            alignItems: 'center',
            borderBottom: '1px solid #f0f0f0',
          }}
        >
          <div />
          <Dropdown
            menu={{ items: userMenuItems }}
            placement="bottomRight"
          >
            <div
              style={{
                cursor: 'pointer',
                display: 'flex',
                alignItems: 'center',
                gap: 8,
              }}
            >
              <Avatar icon={<UserOutlined />} />
              <span>{user?.username || '用户'}</span>
            </div>
          </Dropdown>
        </Header>
        <Content style={{ margin: '24px 16px 0' }}>
          <div
            style={{
              padding: 24,
              minHeight: 360,
              background: '#fff',
              borderRadius: 4,
            }}
          >
            {children}
          </div>
        </Content>
      </Layout>
    </Layout>
  )
}

