'use client'

import React, { useEffect } from 'react'
import { Plus, MessageSquare, Trash2 } from 'lucide-react'
import { useChatStore } from '@/stores'
import { cn, formatDate } from '@/lib/utils'
import { useTheme } from '@/contexts/ThemeContext'

const accentGradients: Record<string, string> = {
  indigo: 'from-indigo-500 to-purple-500',
  purple: 'from-purple-500 to-pink-500',
  sky: 'from-sky-500 to-blue-500',
  emerald: 'from-emerald-500 to-teal-500',
  orange: 'from-orange-500 to-amber-500',
  violet: 'from-violet-500 to-purple-500',
  pink: 'from-pink-500 to-rose-500',
}

export function ConversationList() {
  const { 
    conversations, 
    currentConversation, 
    selectConversation, 
    createConversation,
    deleteConversation,
    isLoading 
  } = useChatStore()
  const { currentTheme, isDark } = useTheme()
  const accent = accentGradients[currentTheme.accentColor] || accentGradients.indigo

  useEffect(() => {
    useChatStore.getState().fetchConversations()
  }, [])

  const handleNewChat = async () => {
    await createConversation()
  }

  const handleDelete = async (e: React.MouseEvent, id: string) => {
    e.stopPropagation()
    if (confirm('确定要删除这个对话吗？')) {
      await deleteConversation(id)
    }
  }

  return (
    <div className="h-full flex flex-col">
      {/* 新建对话按钮 */}
      <div className="p-4">
        <button
          onClick={handleNewChat}
          className="w-full flex items-center justify-center gap-2 px-4 py-3 rounded-xl font-semibold transition-all duration-200 shadow-lg"
          style={{
            background: currentTheme.colors.accent,
            color: '#ffffff',
            boxShadow: `0 4px 15px ${currentTheme.colors.accent}40`
          }}
        >
          <Plus className="w-5 h-5" />
          <span>新建对话</span>
        </button>
      </div>

      {/* 对话列表 */}
      <div className="flex-1 overflow-y-auto px-4 pb-4 space-y-2">
        {isLoading ? (
          <div className={cn("text-center py-8", currentTheme.textMuted)}>加载中...</div>
        ) : conversations.length === 0 ? (
          <div className={cn("text-center py-8", currentTheme.textMuted)}>
            <MessageSquare className="w-12 h-12 mx-auto mb-2 opacity-50" />
            <p>暂无对话记录</p>
          </div>
        ) : (
          conversations.map((conv) => (
            <div
              key={conv.id}
              onClick={() => selectConversation(conv.id)}
              className={cn(
                "w-full text-left p-3 rounded-xl transition-colors group cursor-pointer",
                currentConversation?.id === conv.id
                  ? isDark
                    ? `${currentTheme.accentColor}-500/20 border border-${currentTheme.accentColor}-500/30`
                    : `${currentTheme.accentColor}-100 border border-${currentTheme.accentColor}-300`
                  : isDark 
                    ? "hover:bg-white/5" 
                    : "hover:bg-slate-100"
              )}
            >
              <div className="flex items-center justify-between">
                <div className="flex-1 min-w-0">
                  <p className={cn("font-medium truncate", currentTheme.textPrimary)}>{conv.title}</p>
                  <p className={cn("text-xs mt-1", currentTheme.textMuted)}>{formatDate(conv.updated_at)}</p>
                </div>
                <div className="flex items-center gap-1 opacity-0 group-hover:opacity-100 transition-opacity">
                  <button
                    onClick={(e) => handleDelete(e, conv.id)}
                    className={cn(
                      "p-1.5 rounded-lg transition-colors",
                      isDark 
                        ? "hover:bg-white/10" 
                        : "hover:bg-slate-200"
                    )}
                    title="删除"
                  >
                    <Trash2 className={cn("w-4 h-4", currentTheme.textMuted)} />
                  </button>
                </div>
              </div>
            </div>
          ))
        )}
      </div>
    </div>
  )
}
