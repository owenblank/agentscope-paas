import { Routes, Route, Navigate } from 'react-router-dom'
import { App as AntdApp } from 'antd'
import { ProtectedRoute, AuthProvider } from './components/Auth'
import { MainLayout } from './components/Layout'
import { Login, Register } from './pages/Auth'
import Dashboard from './pages/Dashboard'
import { AgentList, AgentCreate } from './pages/Agent'
import { TeamList, TeamCreate } from './pages/Team'
import Conversation from './pages/Conversation'
import Monitoring from './pages/Monitoring'
import Settings from './pages/Settings'

function App() {
  return (
    <AntdApp>
      <AuthProvider>
        <Routes>
          {/* Public routes */}
          <Route
            path="/login"
            element={
              <ProtectedRoute requireAuth={false}>
                <Login />
              </ProtectedRoute>
            }
          />
          <Route
            path="/register"
            element={
              <ProtectedRoute requireAuth={false}>
                <Register />
              </ProtectedRoute>
            }
          />

          {/* Protected routes */}
          <Route
            path="/"
            element={
              <ProtectedRoute>
                <MainLayout />
              </ProtectedRoute>
            }
          >
            <Route index element={<Navigate to="/dashboard" replace />} />
            <Route path="dashboard" element={<Dashboard />} />
            <Route path="agents" element={<AgentList />} />
            <Route path="agents/create" element={<AgentCreate />} />
            <Route path="agents/:agentId" element={<AgentList />} />
            <Route path="teams" element={<TeamList />} />
            <Route path="teams/create" element={<TeamCreate />} />
            <Route path="teams/:teamId" element={<TeamList />} />
            <Route path="conversation" element={<Conversation />} />
            <Route path="monitoring" element={<Monitoring />} />
            <Route path="settings" element={<Settings />} />
          </Route>

          {/* Fallback route */}
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </AuthProvider>
    </AntdApp>
  )
}

export default App
