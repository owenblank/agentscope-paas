/**
 * API client with authentication
 */
import axios, { AxiosError, InternalAxiosRequestConfig, AxiosResponse } from 'axios'
import { useAuthStore } from '@/store'

// Create axios instance
const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL || '/api/v1', // Use relative path for Vite proxy
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
    console.log('API Request:', config.method?.toUpperCase(), config.url, config.data)
    return config
  },
  (error: AxiosError) => {
    console.error('API Request error:', error)
    return Promise.reject(error)
  }
)

// Response interceptor - handle authentication errors
api.interceptors.response.use(
  (response: AxiosResponse) => {
    console.log('API Response:', response.config.method?.toUpperCase(), response.config.url, response.status, response.data)
    return response
  },
  (error: AxiosError) => {
    console.error('API Error:', error.config?.url, error.response?.status, error.message)
    if (error.response) {
      console.error('Error response data:', error.response.data)
    }

    // Handle 401 Unauthorized - clear auth state and redirect to login
    if (error.response?.status === 401) {
      console.log('401 Unauthorized, logging out...')
      const authStore = useAuthStore.getState()
      authStore.logout()

      // Only redirect if we're in a browser environment and not already on login page
      if (typeof window !== 'undefined' && !window.location.pathname.includes('/login')) {
        console.log('Redirecting to login...')
        window.location.href = '/login'
      }
    }

    return Promise.reject(error)
  }
)

export default api
