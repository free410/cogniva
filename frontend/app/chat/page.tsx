'use client'

import { useEffect, useState } from 'react'
import { Layout } from '@/components'
import { Chat } from '@/components/chat'
import { useAuth } from '@/contexts/AuthContext'
import { useChatStore } from '@/stores'
import { Loader2 } from 'lucide-react'
import { useTheme } from '@/contexts/ThemeContext'

export default function ChatPage() {
  const { isAuthenticated, isLoading, isReady, token } = useAuth()
  const { fetchConversations } = useChatStore()
  const [isInitialized, setIsInitialized] = useState(false)
  const [initError, setInitError] = useState<string | null>(null)
  const { currentTheme } = useTheme()
  const { colors } = currentTheme

  // 直接从 localStorage 检查是否已登录（后备机制）
  const hasToken = typeof window !== 'undefined' 
    ? localStorage.getItem('token') !== null 
    : false

  const showLoading = !isReady || isLoading
  const isLoggedIn = isAuthenticated || hasToken

  // 初始化：加载对话列表
  useEffect(() => {
    // 等待准备完成且已登录
    if (showLoading) return
    if (!isLoggedIn) return

    const initChat = async () => {
      try {
        setInitError(null)
        await fetchConversations()
        setIsInitialized(true)
      } catch (error) {
        console.error('初始化对话失败:', error)
        setInitError('加载对话失败，请刷新重试')
        setIsInitialized(true)
      }
    }

    initChat()
  }, [showLoading, isLoggedIn, token, fetchConversations])

  // 等待准备完成
  if (showLoading) {
    return (
      <Layout>
        <div className="flex items-center justify-center h-full">
          <div className="flex items-center gap-3">
            <Loader2 className="w-6 h-6 animate-spin" style={{ color: colors.accent }} />
            <span style={{ color: colors.textSecondary }}>加载中...</span>
          </div>
        </div>
      </Layout>
    )
  }

  // 未登录
  if (!isLoggedIn) {
    return (
      <Layout>
        <div className="flex items-center justify-center h-full">
          <div className="text-center">
            <p className="text-lg" style={{ color: colors.textPrimary }}>请先登录</p>
            <a href="/auth" className="mt-2 inline-block px-4 py-2 rounded-lg" style={{ background: colors.accent, color: '#fff' }}>
              去登录
            </a>
          </div>
        </div>
      </Layout>
    )
  }

  // 加载中
  if (!isInitialized) {
    return (
      <Layout>
        <div className="flex items-center justify-center h-full">
          <div className="flex flex-col items-center gap-3">
            <Loader2 className="w-8 h-8 animate-spin" style={{ color: colors.accent }} />
            <span style={{ color: colors.textSecondary }}>加载对话...</span>
            {initError && (
              <p className="text-sm" style={{ color: '#ef4444' }}>{initError}</p>
            )}
          </div>
        </div>
      </Layout>
    )
  }

  return (
    <Layout>
      <Chat />
    </Layout>
  )
}
