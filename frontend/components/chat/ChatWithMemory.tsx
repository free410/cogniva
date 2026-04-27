'use client'

import React, { useState } from 'react'
import { Chat } from '@/components/chat'
import { MessageSquare, FileText, Brain, Settings, Sparkles, ChevronRight } from 'lucide-react'
import { MemoryList, MemoryForm, MemoryStats } from '@/components/memory'
import { useTheme } from '@/contexts/ThemeContext'
import { cn } from '@/lib/utils'
import { getAccentGradient } from '@/contexts/themeUtils'

type ActiveView = 'chat' | 'documents' | 'memory' | 'settings'

// 长期记忆内容组件
function MemoryContent({ onClose }: { onClose: () => void }) {
  const [activeTab, setActiveTab] = useState<'list' | 'create' | 'stats'>('list')
  const { currentTheme, isDark, colors } = useTheme()
  const accentGradient = getAccentGradient(currentTheme.accentColor)

  // 模拟统计数据
  const stats = {
    total: 42,
    mastered: 28,
    dueToday: 0,
  }

  return (
    <div className="h-full flex flex-col">
      {/* 顶部标题栏 */}
      <div 
        className="flex-shrink-0 p-5 border-b"
        style={{ borderColor: colors.border }}
      >
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className={cn(
              "w-12 h-12 rounded-xl bg-gradient-to-br flex items-center justify-center shadow-lg",
              "from-amber-200 to-amber-300"
            )}>
              <Brain className="w-6 h-6 text-amber-700" />
            </div>
            <div>
              <h1 className={cn("text-xl font-bold", currentTheme.textPrimary)}>长期记忆</h1>
              <p className={cn("text-sm", currentTheme.textMuted)}>间隔重复学习系统</p>
            </div>
          </div>
          <button
            onClick={onClose}
            className={cn(
              "px-4 py-2 rounded-xl text-sm font-medium transition-all",
              isDark
                ? "bg-white/10 hover:bg-white/20 text-slate-300"
                : "bg-slate-100 hover:bg-slate-200 text-slate-600"
            )}
          >
            返回问答
          </button>
        </div>
      </div>

      {/* 统计卡片 */}
      <div className="flex-shrink-0 p-5">
        <div className="grid grid-cols-3 gap-3">
          <div className={cn(
            "p-4 rounded-xl border text-center"
          )}
          style={{
            background: colors.accentBg,
            borderColor: colors.accent + '30'
          }}
          >
            <p className={cn("text-2xl font-bold", currentTheme.textPrimary)}>{stats.total}</p>
            <p className={cn("text-xs", currentTheme.textMuted)}>记忆总数</p>
          </div>
          <div className={cn(
            "p-4 rounded-xl border text-center"
          )}
          style={{
            background: colors.cardBg,
            borderColor: colors.border
          }}
          >
            <p className="text-2xl font-bold" style={{ color: colors.accent }}>{stats.mastered}</p>
            <p className={cn("text-xs", currentTheme.textMuted)}>已掌握</p>
          </div>
          <div className={cn(
            "p-4 rounded-xl border text-center"
          )}
          style={{
            background: colors.cardBg,
            borderColor: colors.border
          }}
          >
            <p className="text-2xl font-bold" style={{ color: colors.accent }}>{stats.dueToday}</p>
            <p className={cn("text-xs", currentTheme.textMuted)}>待复习</p>
          </div>
        </div>
      </div>

      {/* 标签页 */}
      <div className="flex-shrink-0 px-5 pb-3">
        <div className={cn(
          "inline-flex gap-1 p-1.5 rounded-xl",
          isDark ? "bg-white/5" : "bg-slate-100"
        )}>
          {[
            { id: 'list', label: '记忆列表' },
            { id: 'create', label: '创建记忆' },
            { id: 'stats', label: '统计' },
          ].map(tab => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id as any)}
              className={cn(
                "flex items-center gap-2 px-5 py-2.5 rounded-lg text-sm font-medium transition-all duration-200",
                activeTab === tab.id
                  ? `bg-gradient-to-r ${accentGradient} text-white shadow-lg`
                  : currentTheme.textMuted
              )}
            >
              {tab.label}
            </button>
          ))}
        </div>
      </div>

      {/* 内容区域 */}
      <div className="flex-1 overflow-hidden">
        {activeTab === 'list' && (
          <div className="h-full overflow-y-auto px-5">
            <MemoryList />
          </div>
        )}
        {activeTab === 'create' && (
          <div className="h-full overflow-y-auto px-5 pb-5">
            <div className="max-w-2xl">
              <MemoryForm />
            </div>
          </div>
        )}
        {activeTab === 'stats' && (
          <div className="h-full overflow-y-auto px-5">
            <MemoryStats />
          </div>
        )}
      </div>
    </div>
  )
}

// 知识库内容组件
function DocumentsContent({ onClose }: { onClose: () => void }) {
  const { currentTheme, isDark, colors } = useTheme()
  const accentGradient = getAccentGradient(currentTheme.accentColor)

  return (
    <div className="h-full flex items-center justify-center">
      <div className="text-center max-w-md">
        <div className={cn(
          "w-20 h-20 mx-auto rounded-2xl bg-gradient-to-br flex items-center justify-center shadow-lg mb-4",
          accentGradient
        )}>
          <FileText className="w-10 h-10 text-white" />
        </div>
        <h2 className={cn("text-xl font-bold mb-2", currentTheme.textPrimary)}>知识库</h2>
        <p className={cn("text-sm mb-4", currentTheme.textMuted)}>
          点击或拖拽文件到此处上传
        </p>
        <p className={cn("text-xs", currentTheme.textMuted)}>
          支持 PDF、Word、Excel、文本文档等
        </p>
      </div>
    </div>
  )
}

// 设置内容组件
function SettingsContent({ onClose }: { onClose: () => void }) {
  const { currentTheme, isDark, colors } = useTheme()
  const accentGradient = getAccentGradient(currentTheme.accentColor)

  return (
    <div className="h-full flex items-center justify-center">
      <div className="text-center max-w-md">
        <div className={cn(
          "w-20 h-20 mx-auto rounded-2xl bg-gradient-to-br flex items-center justify-center shadow-lg mb-4",
          accentGradient
        )}>
          <Settings className="w-10 h-10 text-white" />
        </div>
        <h2 className={cn("text-xl font-bold mb-2", currentTheme.textPrimary)}>设置</h2>
        <p className={cn("text-sm mb-4", currentTheme.textMuted)}>
          配置您的偏好设置
        </p>
      </div>
    </div>
  )
}

// 主布局组件
export function ChatWithMemory() {
  const [activeView, setActiveView] = useState<ActiveView>('chat')
  const { currentTheme, isDark, colors } = useTheme()
  const accentGradient = getAccentGradient(currentTheme.accentColor)

  return (
    <div className="h-full flex">
      {/* 左侧边栏 */}
      <div 
        className={cn(
          "w-56 flex-shrink-0 border-r flex flex-col",
        )}
        style={{
          background: colors.bgSecondary,
          borderColor: colors.border
        }}
      >
        {/* Logo 区域 */}
        <div className={cn(
          "p-4 border-b",
        )}
        style={{ borderColor: colors.border }}
        >
          <div className="flex items-center gap-3">
            <div className={cn(
              "w-10 h-10 rounded-xl flex items-center justify-center shadow-lg",
              "from-amber-200 to-amber-300"
            )}>
              <Sparkles className="w-5 h-5 text-amber-700" />
            </div>
            <div>
              <h1 className={cn("text-base font-bold", currentTheme.textPrimary)}>Cogniva</h1>
              <p className={cn("text-xs", currentTheme.textMuted)}>智能知识问答平台</p>
            </div>
          </div>
        </div>

        {/* 导航菜单 */}
        <nav className="flex-1 p-3 space-y-1 overflow-y-auto">
          {/* 智能问答 */}
          <button
            onClick={() => setActiveView('chat')}
            className={cn(
              "w-full flex items-center gap-3 px-4 py-3 rounded-xl transition-all duration-200"
            )}
            style={{
              background: activeView === 'chat' ? colors.accentBg : 'transparent',
              color: activeView === 'chat' ? colors.accentText : colors.textSecondary,
              border: activeView === 'chat' ? `1px solid ${colors.accent}40` : '1px solid transparent'
            }}
          >
            <div className={cn(
              "w-8 h-8 rounded-lg flex items-center justify-center",
            )}
            style={{
              background: activeView === 'chat' ? colors.accent : colors.cardBg,
              color: activeView === 'chat' ? '#ffffff' : colors.textMuted
            }}
            >
              <MessageSquare className="w-4 h-4" />
            </div>
            <span className="font-medium text-sm">智能问答</span>
          </button>

          {/* 知识库 */}
          <button
            onClick={() => setActiveView('documents')}
            className={cn(
              "w-full flex items-center gap-3 px-4 py-3 rounded-xl transition-all duration-200"
            )}
            style={{
              background: activeView === 'documents' ? colors.accentBg : 'transparent',
              color: activeView === 'documents' ? colors.accentText : colors.textSecondary,
              border: activeView === 'documents' ? `1px solid ${colors.accent}40` : '1px solid transparent'
            }}
          >
            <div className={cn(
              "w-8 h-8 rounded-lg flex items-center justify-center",
            )}
            style={{
              background: activeView === 'documents' ? colors.accent : colors.cardBg,
              color: activeView === 'documents' ? '#ffffff' : colors.textMuted
            }}
            >
              <FileText className="w-4 h-4" />
            </div>
            <span className="font-medium text-sm">知识库</span>
          </button>

          {/* 长期记忆 */}
          <button
            onClick={() => setActiveView('memory')}
            className={cn(
              "w-full flex items-center gap-3 px-4 py-3 rounded-xl transition-all duration-200"
            )}
            style={{
              background: activeView === 'memory' ? colors.accentBg : 'transparent',
              color: activeView === 'memory' ? colors.accentText : colors.textSecondary,
              border: activeView === 'memory' ? `1px solid ${colors.accent}40` : '1px solid transparent'
            }}
          >
            <div className={cn(
              "w-8 h-8 rounded-lg flex items-center justify-center",
            )}
            style={{
              background: activeView === 'memory' ? colors.accent : colors.cardBg,
              color: activeView === 'memory' ? '#ffffff' : colors.textMuted
            }}
            >
              <Brain className="w-4 h-4" />
            </div>
            <span className="font-medium text-sm flex-1 text-left">长期记忆</span>
            {activeView === 'memory' && (
              <ChevronRight className={cn("w-4 h-4", currentTheme.textMuted)} />
            )}
          </button>

          {/* 设置 */}
          <button
            onClick={() => setActiveView('settings')}
            className={cn(
              "w-full flex items-center gap-3 px-4 py-3 rounded-xl transition-all duration-200"
            )}
            style={{
              background: activeView === 'settings' ? colors.accentBg : 'transparent',
              color: activeView === 'settings' ? colors.accentText : colors.textSecondary,
              border: activeView === 'settings' ? `1px solid ${colors.accent}40` : '1px solid transparent'
            }}
          >
            <div className={cn(
              "w-8 h-8 rounded-lg flex items-center justify-center",
            )}
            style={{
              background: activeView === 'settings' ? colors.accent : colors.cardBg,
              color: activeView === 'settings' ? '#ffffff' : colors.textMuted
            }}
            >
              <Settings className="w-4 h-4" />
            </div>
            <span className="font-medium text-sm">设置</span>
          </button>
        </nav>

        {/* 底部状态 */}
        <div className={cn(
          "p-4 border-t",
        )}
        style={{ borderColor: colors.border }}
        >
          <div className={cn(
            "rounded-xl p-3 text-center",
          )}
          style={{
            background: colors.cardBg,
            border: `1px solid ${colors.cardBorder}`
          }}
          >
            <div className="flex items-center justify-center gap-1.5 mb-1">
              <div className="w-1.5 h-1.5 rounded-full animate-pulse" style={{ backgroundColor: colors.accent }} />
              <span className={cn("text-xs font-medium", currentTheme.textSecondary)}>
                系统正常
              </span>
            </div>
            <p className={cn("text-[10px]", currentTheme.textMuted)}>基于 RAG 技术</p>
          </div>
        </div>
      </div>

      {/* 右侧主内容区 */}
      <div className="flex-1 overflow-hidden">
        {activeView === 'chat' && <Chat />}
        {activeView === 'documents' && <DocumentsContent onClose={() => setActiveView('chat')} />}
        {activeView === 'memory' && <MemoryContent onClose={() => setActiveView('chat')} />}
        {activeView === 'settings' && <SettingsContent onClose={() => setActiveView('chat')} />}
      </div>
    </div>
  )
}
