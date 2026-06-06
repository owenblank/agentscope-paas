/**
 * Authentication state management
 */
import { create } from 'zustand'
import { persist, createJSONStorage } from 'zustand/middleware'
import type { User, ApiKey } from '@/types'
import { authService } from '@/services'

interface AuthState {
  // State
  user: User | null
  apiKey: string | null
  isAuthenticated: boolean
  isLoading: boolean
  error: string | null

  // Actions
  login: (email: string, password: string) => Promise<void>
  register: (username: string, email: string, password: string) => Promise<void>
  logout: () => void
  getCurrentUser: () => Promise<void>
  setApiKey: (apiKey: string) => void
  clearError: () => void
}

export const useAuthStore = create<AuthState>()(
  persist(
    (set, get) => ({
      // Initial state
      user: null,
      apiKey: null,
      isAuthenticated: false,
      isLoading: false,
      error: null,

      // Login action
      login: async (email: string, password: string) => {
        console.log('Starting login process for:', email)
        set({ isLoading: true, error: null })
        try {
          console.log('Calling authService.login with:', { email })
          const response = await authService.login({ email, password })
          console.log('Login response received:', response)

          // Handle different response formats
          const token = response.access_token || response.api_key || response.token
          const user = response.user || response.data?.user

          console.log('Extracted token:', !!token, 'Extracted user:', !!user)

          if (!token) {
            console.error('No token in response:', response)
            throw new Error('No token received from server')
          }

          set({
            user: user || response,
            apiKey: token,
            isAuthenticated: true,
            isLoading: false,
          })

          console.log('Login successful, auth state updated:', {
            isAuthenticated: true,
            hasUser: !!user,
            hasApiKey: !!token
          })
        } catch (error: any) {
          console.error('Login error:', error)
          const errorMessage = error.response?.data?.detail || error.message || '登录失败'
          set({
            error: errorMessage,
            isLoading: false,
            isAuthenticated: false,
          })
          throw error
        }
      },

      // Register action
      register: async (username: string, email: string, password: string) => {
        console.log('Starting registration process for:', username)
        set({ isLoading: true, error: null })
        try {
          console.log('Calling authService.register with:', { username, email })
          const response = await authService.register({
            username,
            email,
            password,
          })
          console.log('Registration response:', response)

          const token = response.api_key || response.access_token
          if (!token) {
            throw new Error('No API key received from server')
          }

          set({
            user: response.user,
            apiKey: token,
            isAuthenticated: true,
            isLoading: false,
          })
          console.log('Registration successful, auth state updated')
        } catch (error: any) {
          console.error('Registration error:', error)
          const errorMessage = error.response?.data?.detail || error.message || '注册失败'
          set({
            error: errorMessage,
            isLoading: false,
          })
          throw error
        }
      },

      // Logout action
      logout: () => {
        authService.logout()
        set({
          user: null,
          apiKey: null,
          isAuthenticated: false,
        })
      },

      // Get current user action
      getCurrentUser: async () => {
        set({ isLoading: true, error: null })
        try {
          const user = await authService.getCurrentUser()
          set({ user, isLoading: false })
        } catch (error: any) {
          const errorMessage = error.response?.data?.detail || '获取用户信息失败'
          set({
            error: errorMessage,
            isLoading: false,
          })
          // If getting user fails, clear auth state
          get().logout()
        }
      },

      // Set API key action
      setApiKey: (apiKey: string) => {
        set({ apiKey })
      },

      // Clear error action
      clearError: () => {
        set({ error: null })
      },
    }),
    {
      name: 'auth-storage',
      storage: createJSONStorage(() => localStorage),
      // Only persist user info and API key
      partialize: (state) => ({
        user: state.user,
        apiKey: state.apiKey,
        isAuthenticated: state.isAuthenticated,
      }),
    }
  )
)