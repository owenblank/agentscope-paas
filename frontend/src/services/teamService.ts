import api from './api'
import type {
  Team,
  TeamConfig,
  TeamListResponse,
  ApiResponse,
  PaginationParams,
} from '@/types'

// 团队服务
export const teamService = {
  // 获取团队列表
  async getTeams(params?: PaginationParams) {
    const response = await api.get<ApiResponse<TeamListResponse>>('/teams', { params })
    return response.data.data
  },

  // 获取团队详情
  async getTeam(teamId: string) {
    const response = await api.get<ApiResponse<Team>>(`/teams/${teamId}`)
    return response.data.data
  },

  // 创建团队
  async createTeam(config: TeamConfig) {
    const response = await api.post<ApiResponse<{ team_id: string; status: string }>>(
      '/teams',
      { config }
    )
    return response.data.data
  },

  // 更新团队
  async updateTeam(teamId: string, config: Partial<TeamConfig>) {
    const response = await api.put<ApiResponse<{ team_id: string; status: string }>>(
      `/teams/${teamId}`,
      { config }
    )
    return response.data.data
  },

  // 删除团队
  async deleteTeam(teamId: string) {
    const response = await api.delete<ApiResponse<void>>(`/teams/${teamId}`)
    return response.data
  },

  // 启动团队
  async startTeam(teamId: string) {
    const response = await api.post<ApiResponse<{ team_id: string; status: string }>>(
      `/teams/${teamId}/start`
    )
    return response.data.data
  },

  // 停止团队
  async stopTeam(teamId: string) {
    const response = await api.post<ApiResponse<{ team_id: string; status: string }>>(
      `/teams/${teamId}/stop`
    )
    return response.data.data
  },
}
