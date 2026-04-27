'use client'

import React, { useState } from 'react'
import Link from 'next/link'
import { usePathname, useRouter } from 'next/navigation'
import { MessageSquare, FileText, Brain, Settings, Sparkles, Palette, LogOut, User } from 'lucide-react'
import { useTheme, themes, ThemeId } from '@/contexts/ThemeContext'
import { useAuth } from '@/contexts/AuthContext'

const NAV_ITEMS = [
  { href: '/chat', label: '智能问答', icon: MessageSquare },
  { href: '/documents', label: '知识库', icon: FileText },
  { href: '/memory', label: '长期记忆', icon: Brain },
  { href: '/settings', label: '设置', icon: Settings },
]

export function Sidebar() {
  const pathname = usePathname()
  const router = useRouter()
  const { currentTheme, setCurrentTheme } = useTheme()
  const { user, logout } = useAuth()
  const [showThemePanel, setShowThemePanel] = useState(false)

  const { colors } = currentTheme

  const handleLogout = () => {
    logout()
    router.push('/auth')
  }

  return (
    <div
      className="w-72 h-screen flex flex-col shadow-2xl border-r relative"
      style={{
        background: colors.bgSecondary,
        borderColor: colors.border
      }}
    >
      {/* Logo - 固定高度 64px，和右侧 header 对齐 */}
      <div
        className="h-16 pl-6 pr-6 border-b flex items-center flex-shrink-0"
        style={{ borderColor: colors.border }}
      >
        <div className="flex items-center gap-3">
          <div
            className="w-10 h-10 rounded-xl flex items-center justify-center shadow-lg flex-shrink-0"
            style={{
              background: colors.chatBubbleUser,
              boxShadow: `0 4px 15px ${colors.accent}40`
            }}
          >
            <Sparkles className="w-5 h-5 text-white" />
          </div>
          <div className="min-w-0">
            <h1 className="text-lg font-bold tracking-tight truncate" style={{ color: colors.textPrimary }}>
              Cogniva
            </h1>
            <p className="text-xs truncate" style={{ color: colors.textMuted }}>智能知识问答平台</p>
          </div>
        </div>
      </div>

      {/* 导航 */}
      <nav className="flex-1 p-3 space-y-1 overflow-y-auto">
        {NAV_ITEMS.map(item => {
          const Icon = item.icon
          const isActive = pathname === item.href

          return (
            <Link
              key={item.href}
              href={item.href}
              className="flex items-center gap-3 px-4 py-3 rounded-xl transition-all duration-200 group"
              style={{
                background: isActive ? colors.accentBg : 'transparent',
                color: isActive ? colors.accentText : colors.textSecondary,
                border: isActive ? `1px solid ${colors.accent}40` : '1px solid transparent'
              }}
            >
              <div
                className="w-9 h-9 rounded-lg flex items-center justify-center transition-all"
                style={{
                  background: isActive ? colors.accent : colors.cardBg,
                  color: isActive ? '#ffffff' : colors.textMuted
                }}
              >
                <Icon className="w-4 h-4" />
              </div>
              <span className="font-medium">
                {item.label}
              </span>
              {isActive && (
                <div
                  className="ml-auto w-1.5 h-1.5 rounded-full animate-pulse"
                  style={{ backgroundColor: colors.accent }}
                />
              )}
            </Link>
          )
        })}
      </nav>

      {/* 主题切换 */}
      <div className="p-3 flex-shrink-0">
        <div className="relative">
          <button
            onClick={() => setShowThemePanel(!showThemePanel)}
            className="w-full flex items-center gap-2 px-3 py-2.5 rounded-xl transition-all duration-200 text-sm"
            style={{
              background: colors.cardBg,
              color: colors.textSecondary,
              border: `1px solid ${colors.border}`
            }}
          >
            <Palette className="w-4 h-4" />
            <span className="flex-1 text-left">{currentTheme.icon} {currentTheme.name}</span>
          </button>

          {/* 主题选择面板 */}
          {showThemePanel && (
            <div
              className="absolute bottom-full left-0 right-0 mb-2 p-3 rounded-xl shadow-xl z-50"
              style={{
                background: colors.bgPrimary,
                border: `1px solid ${colors.border}`
              }}
            >
              <p className="text-[10px] font-semibold mb-2 px-1" style={{ color: colors.textMuted }}>
                选择主题
              </p>
              <div className="grid grid-cols-2 gap-1.5">
                {themes.map((theme) => {
                  const isSelected = currentTheme.id === theme.id

                  return (
                    <button
                      key={theme.id}
                      onClick={() => {
                        setCurrentTheme(theme.id as ThemeId)
                        setShowThemePanel(false)
                      }}
                      className="flex items-center gap-2 p-2 rounded-lg transition-all duration-150 text-xs"
                      style={{
                        background: isSelected ? colors.accentBg : 'transparent',
                        color: isSelected ? colors.accentText : colors.textSecondary
                      }}
                    >
                      <div
                        className="w-5 h-5 rounded"
                        style={{ background: theme.colors.bgPrimary }}
                      />
                      <span className="truncate">{theme.icon} {theme.name}</span>
                    </button>
                  )
                })}
              </div>
            </div>
          )}
        </div>
      </div>

      {/* 用户信息 - 底部对齐，美化样式 */}
      <div
        className="border-t flex-shrink-0"
        style={{ borderColor: colors.border }}
      >
        <div className="px-6 py-4">
          <div
            className="rounded-xl p-3 transition-all"
            style={{
              background: colors.cardBg,
              border: `1px solid ${colors.border}`
            }}
          >
            {/* 第一行：头像 + 用户信息 */}
            <div className="flex items-center gap-3">
              <div
                className="w-9 h-9 rounded-full flex items-center justify-center flex-shrink-0"
                style={{
                  background: colors.accent,
                  boxShadow: `0 0 0 2px ${colors.accent}30`
                }}
              >
                <User className="w-4 h-4 text-white" />
              </div>
              <div className="flex-1 min-w-0">
                <p className="text-sm font-semibold truncate" style={{ color: colors.textPrimary }}>
                  {user?.username || '未登录'}
                </p>
                <p className="text-xs truncate" style={{ color: colors.textMuted }}>
                  {user?.email || '请先登录'}
                </p>
              </div>
            </div>

            {/* 第二行：状态 + 操作 */}
            <div className="flex items-center justify-between mt-3 pt-3" style={{ borderTop: `1px solid ${colors.border}` }}>
              {user ? (
                <>
                  <div
                    className="flex items-center gap-1.5 px-2 py-1 rounded-full text-xs"
                    style={{ background: colors.accentBg, color: colors.accent }}
                  >
                    <div className="w-1.5 h-1.5 rounded-full animate-pulse" style={{ backgroundColor: colors.accent }} />
                    <span>已登录</span>
                  </div>
                  <button
                    onClick={handleLogout}
                    className="flex items-center gap-1.5 px-2.5 py-1 rounded-lg transition-all duration-200 text-xs font-medium"
                    style={{
                      color: '#dc2626',
                      background: '#fef2f2',
                      border: '1px solid #fecaca'
                    }}
                    title="退出登录"
                  >
                    <LogOut className="w-3.5 h-3.5" />
                    <span>退出</span>
                  </button>
                </>
              ) : (
                <div className="flex items-center gap-1.5 px-2 py-1 rounded-full text-xs" style={{ background: '#fef3c7', color: '#92400e' }}>
                  <span>未登录</span>
                </div>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
