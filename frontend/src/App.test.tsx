import React from 'react'
import { Card, Button } from 'antd'

function TestApp() {
  return (
    <div style={{ padding: '50px', textAlign: 'center' }}>
      <Card title="AgentScope PaaS 前端测试" style={{ maxWidth: 600, margin: '0 auto' }}>
        <h1>🎉 React 应用运行正常！</h1>
        <p>如果你能看到这个页面，说明基本配置是正确的。</p>
        <Button type="primary">测试按钮</Button>
      </Card>
    </div>
  )
}

export default TestApp
