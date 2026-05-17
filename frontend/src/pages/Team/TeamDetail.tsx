import { Card } from 'antd'
import { useParams } from 'react-router-dom'

const TeamDetail = () => {
  const { teamId } = useParams()
  return <Card title="团队详情">团队详情页面 - {teamId} - 开发中</Card>
}

export default TeamDetail
