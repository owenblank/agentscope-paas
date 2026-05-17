/**
 * Authentication related type definitions
 */

export interface User {
  user_id: string
  username: string
  email: string
  role: 'user' | 'admin'
  created_at: string
  updated_at: string
  is_active: boolean
}

export interface ApiKey {
  key_id: string
  user_id: string
  api_key: string
  name: string
  scopes: string[]
  last_used?: string
  expires_at?: string
  created_at: string
  is_active: boolean
}

export interface RegisterRequest {
  username: string
  email: string
  password: string
}

export interface LoginRequest {
  email: string
  password: string
}

export interface AuthResponse {
  user: User
  api_key: string
  message: string
}

export interface RegisterFormData {
  username: string
  email: string
  password: string
  confirmPassword: string
}

export interface LoginFormData {
  email: string
  password: string
}

export interface CreateApiKeyRequest {
  name: string
  scopes: string[]
}

export interface CreateApiKeyResponse {
  api_key: ApiKey
  key: string
  message: string
}