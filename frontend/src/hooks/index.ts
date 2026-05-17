// 自定义Hooks
// 这个目录用于存放自定义的React Hooks

/**
 * 使用防抖Hook
 */
export function useDebounce<T>(value: T, delay: number): T {
  // 实现防抖逻辑
  return value
}

/**
 * 使用节流Hook
 */
export function useThrottle<T>(value: T, limit: number): T {
  // 实现节流逻辑
  return value
}

// 更多自定义Hooks可以在这里添加
