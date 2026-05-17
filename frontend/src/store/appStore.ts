import { create } from 'zustand'
import { devtools, persist } from 'zustand/middleware'
import { useAuthStore } from './auth.store'

interface AppState {
  // 全局加载状态
  isLoading: boolean

  // 侧边栏状态
  sidebarCollapsed: boolean

  // 主题设置
  theme: 'light' | 'dark'

  // 操作
  setLoading: (loading: boolean) => void
  toggleSidebar: () => void
  setTheme: (theme: 'light' | 'dark') => void
}

// You can also add selectors for convenience
export const useUser = () => useAuthStore((state) => state.user)
export const useIsAuthenticated = () => useAuthStore((state) => state.isAuthenticated)

export const useAppStore = create<AppState>()(
  devtools(
    persist(
      (set) => ({
        isLoading: false,
        sidebarCollapsed: false,
        theme: 'light',

        setLoading: (isLoading) => set({ isLoading }),
        toggleSidebar: () => set((state) => ({ sidebarCollapsed: !state.sidebarCollapsed })),
        setTheme: (theme) => set({ theme }),
      }),
      {
        name: 'app-storage',
        partialize: (state) => ({
          theme: state.theme,
          sidebarCollapsed: state.sidebarCollapsed,
        }),
      }
    )
  )
)
