/**
 * Authentication API service
 */
import api from './api'
import type {
  User,
  ApiKey,
  RegisterRequest,
  LoginRequest,
  AuthResponse,
  CreateApiKeyRequest,
  CreateApiKeyResponse,
  ApiResponse,
} from '@/types'

export const authService = {
  /**
   * User registration
   */
  async register(data: RegisterRequest): Promise<AuthResponse> {
    const response = await api.post<ApiResponse<AuthResponse>>(
      '/auth/register',
      data
    )
    return response.data.data
  },

  /**
   * User login
   */
  async login(data: LoginRequest): Promise<AuthResponse> {
    const response = await api.post<ApiResponse<AuthResponse>>(
      '/auth/login',
      data
    )
    return response.data.data
  },

  /**
   * Get current user information
   */
  async getCurrentUser(): Promise<User> {
    const response = await api.get<ApiResponse<{ user: User }>>(
      '/auth/me'
    )
    return response.data.data.user
  },

  /**
   * Get user's API keys
   */
  async getApiKeys(): Promise<ApiKey[]> {
    const response = await api.get<ApiResponse<{ api_keys: ApiKey[] }>>(
      '/auth/api-keys'
    )
    return response.data.data.api_keys
  },

  /**
   * Create new API key
   */
  async createApiKey(data: CreateApiKeyRequest): Promise<CreateApiKeyResponse> {
    const response = await api.post<ApiResponse<CreateApiKeyResponse>>(
      '/auth/api-keys',
      data
    )
    return response.data.data
  },

  /**
   * Delete API key
   */
  async deleteApiKey(keyId: string): Promise<void> {
    const response = await api.delete<ApiResponse<void>>(
      `/auth/api-keys/${keyId}`
    )
    return response.data
  },

  /**
   * Client-side logout (clears local storage)
   */
  logout(): void {
    localStorage.removeItem('auth-storage')
  },
}