/**
 * API client with authentication
 */
import axios, { AxiosError, InternalAxiosRequestConfig, AxiosResponse } from 'axios'
import { useAuthStore } from '@/store'

// Create axios instance
const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1',
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
})

// Request interceptor - add authentication header
api.interceptors.request.use(
  (config: InternalAxiosRequestConfig) => {
    const { apiKey } = useAuthStore.getState()
    if (apiKey && config.headers) {
      config.headers['X-API-Key'] = apiKey
    }
    return config
  },
  (error: AxiosError) => {
    return Promise.reject(error)
  }
)

// Response interceptor - handle authentication errors
api.interceptors.response.use(
  (response: AxiosResponse) => response,
  (error: AxiosError) => {
    // Handle 401 Unauthorized - clear auth state and redirect to login
    if (error.response?.status === 401) {
      const authStore = useAuthStore.getState()
      authStore.logout()

      // Only redirect if we're in a browser environment
      if (typeof window !== 'undefined') {
        window.location.href = '/login'
      }
    }

    return Promise.reject(error)
  }
)

export default api
