import { Card } from 'antd'
import { useParams } from 'react-router-dom'

const Conversation = () => {
  const { conversationId } = useParams()
  return <Card title="对话界面">对话界面 - {conversationId} - 开发中</Card>
}

export default Conversation
