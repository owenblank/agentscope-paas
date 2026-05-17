/**
 * Auth Provider Component - Simplified version
 */
import { useEffect } from 'react'
import { useAuthStore } from '@/store'

export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const { getCurrentUser, apiKey } = useAuthStore()

  useEffect(() => {
    // Only try to get current user if we have an API key
    if (apiKey) {
      getCurrentUser().catch(() => {
        // If getting user fails, just clear the error
        useAuthStore.getState().clearError()
      })
    } else {
      // No API key means not authenticated, set loading to false
      useAuthStore.setState({ isLoading: false })
    }
  }, [apiKey, getCurrentUser])

  return <>{children}</>
}