'use client'

import React, { createContext, useContext, useState, useCallback } from 'react'

const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

interface User {
  id: string
  username: string
  email?: string
  name?: string
}

interface AuthContextType {
  user: User | null
  token: string | null
  isLoading: boolean
  isReady: boolean
  login: (username: string, password: string) => Promise<void>
  logout: () => void
  isAuthenticated: boolean
}

const AuthContext = createContext<AuthContextType | undefined>(undefined)

// 同步获取初始状态（避免 hydration 问题）
function getInitialAuth(): { user: User | null; token: string | null } {
  if (typeof window === 'undefined') {
    return { user: null, token: null }
  }
  try {
    const savedToken = localStorage.getItem('token')
    const savedUser = localStorage.getItem('user')
    if (savedToken && savedUser) {
      return {
        token: savedToken,
        user: JSON.parse(savedUser)
      }
    }
  } catch (e) {
    console.error('Failed to read auth from localStorage:', e)
  }
  return { user: null, token: null }
}

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const initialAuth = getInitialAuth()
  const [user, setUser] = useState<User | null>(initialAuth.user)
  const [token, setToken] = useState<string | null>(initialAuth.token)

  const login = useCallback(async (username: string, password: string) => {
    const response = await fetch(`${API_BASE}/api/auth/login`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ username, password })
    })

    if (!response.ok) {
      const data = await response.json()
      throw new Error(data.detail || '登录失败')
    }

    const data = await response.json()
    localStorage.setItem('token', data.access_token)
    localStorage.setItem('user', JSON.stringify(data.user))
    setToken(data.access_token)
    setUser(data.user)
  }, [])

  const logout = useCallback(() => {
    localStorage.removeItem('token')
    localStorage.removeItem('user')
    setToken(null)
    setUser(null)
  }, [])

  return (
    <AuthContext.Provider value={{
      user,
      token,
      isLoading: false,
      isReady: true,
      login,
      logout,
      isAuthenticated: !!token
    }}>
      {children}
    </AuthContext.Provider>
  )
}

export function useAuth() {
  const context = useContext(AuthContext)
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider')
  }
  return context
}

// API 请求辅助函数 - 自动添加 token
export async function authFetch(url: string, options: RequestInit = {}) {
  const token = localStorage.getItem('token')

  const headers: Record<string, string> = {
    ...(options.headers as Record<string, string> || {}),
    'Content-Type': 'application/json'
  }

  if (token) {
    headers['Authorization'] = `Bearer ${token}`
  }

  const response = await fetch(url, {
    ...options,
    headers
  })

  // 如果是 401，可能是 token 过期
  if (response.status === 401) {
    localStorage.removeItem('token')
    localStorage.removeItem('user')
    window.location.href = '/auth'
    throw new Error('登录已过期，请重新登录')
  }

  return response
}
