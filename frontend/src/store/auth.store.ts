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
        set({ isLoading: true, error: null })
        try {
          const response = await authService.login({ email, password })
          set({
            user: response.user,
            apiKey: response.api_key,
            isAuthenticated: true,
            isLoading: false,
          })
        } catch (error: any) {
          const errorMessage = error.response?.data?.detail || '登录失败'
          set({
            error: errorMessage,
            isLoading: false,
          })
          throw error
        }
      },

      // Register action
      register: async (username: string, email: string, password: string) => {
        set({ isLoading: true, error: null })
        try {
          const response = await authService.register({
            username,
            email,
            password,
          })
          set({
            user: response.user,
            apiKey: response.api_key,
            isAuthenticated: true,
            isLoading: false,
          })
        } catch (error: any) {
          const errorMessage = error.response?.data?.detail || '注册失败'
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