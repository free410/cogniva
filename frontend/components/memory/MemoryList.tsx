'use client'

import React, { useState, useEffect } from 'react'
import {
  Trash2,
  Edit2,
  Calendar,
  Star,
  Tag,
  Brain,
  RefreshCw
} from 'lucide-react'
import { useMemoryStore } from '@/stores'
import type { Memory } from '@/lib/types'
import { cn } from '@/lib/utils'
import { useTheme } from '@/contexts/ThemeContext'

export function MemoryList() {
  const { memories, fetchMemories, deleteMemory, updateMemory, currentCategory, fetchStatistics } = useMemoryStore()
  const { currentTheme, isDark } = useTheme()
  const [editingId, setEditingId] = useState<string | null>(null)
  const [editContent, setEditContent] = useState('')
  const [editCategory, setEditCategory] = useState('general')
  const [editImportance, setEditImportance] = useState(0.5)

  useEffect(() => {
    fetchMemories(currentCategory || undefined)
  }, [currentCategory])

  const handleEdit = (memory: Memory) => {
    setEditingId(memory.id)
    setEditContent(memory.content)
    setEditCategory(memory.category)
    setEditImportance(memory.importance)
  }

  const handleSave = async (id: string) => {
    try {
      await updateMemory(id, editContent, editCategory, editImportance)
      setEditingId(null)
      await fetchStatistics()
    } catch (error) {
      console.error('Failed to update memory:', error)
    }
  }

  const handleDelete = async (id: string) => {
    if (confirm('确定要删除这条记忆吗？')) {
      await deleteMemory(id)
      await fetchStatistics()
    }
  }

  const getImportanceStars = (importance: number) => {
    const stars = Math.round(importance * 5)
    return Array.from({ length: 5 }, (_, i) => i < stars)
  }

  const getCategoryConfig = (category: string) => {
    const configs: Record<string, { gradient: string; bg: string; text: string }> = {
      general: { gradient: 'from-blue-500 to-cyan-500', bg: 'bg-blue-500', text: 'text-blue-400' },
      conversation_insight: { gradient: 'from-purple-500 to-pink-500', bg: 'bg-purple-500', text: 'text-purple-400' },
      note: { gradient: 'from-emerald-500 to-teal-500', bg: 'bg-emerald-500', text: 'text-emerald-400' },
      fact: { gradient: 'from-amber-500 to-orange-500', bg: 'bg-amber-500', text: 'text-amber-400' },
      concept: { gradient: 'from-indigo-500 to-violet-500', bg: 'bg-indigo-500', text: 'text-indigo-400' },
      term: { gradient: 'from-rose-500 to-red-500', bg: 'bg-rose-500', text: 'text-rose-400' },
    }
    return configs[category] || configs.general
  }

  const getCategoryLabel = (category: string) => {
    const labels: Record<string, string> = {
      general: '通用',
      conversation_insight: '洞察',
      note: '笔记',
      fact: '事实',
      concept: '概念',
      term: '术语'
    }
    return labels[category] || category
  }

  const renderEmptyState = () => (
    <div className="flex flex-col items-center justify-center py-16 text-center relative">
      <div className="relative mb-6">
        <div
          className="absolute inset-0 rounded-full blur-xl opacity-30"
          style={{ background: currentTheme.colors.accent }}
        />
        <div
          className={cn(
            "w-24 h-24 rounded-2xl flex items-center justify-center relative",
            isDark ? "bg-white/5" : "bg-slate-100"
          )}
          style={{
            boxShadow: `0 8px 32px ${currentTheme.colors.accent}20`
          }}
        >
          <Brain className="w-12 h-12" style={{ color: currentTheme.colors.accent }} />
        </div>
      </div>
      <h3 className={cn("text-base font-bold mb-2", currentTheme.textPrimary)}>暂无记忆</h3>
      <p className={cn("text-xs max-w-[200px]", currentTheme.textMuted)}>在右侧创建你的第一条记忆，开启学习之旅</p>
      <div className={cn("absolute right-8 top-1/2 -translate-y-1/2 rotate-12 opacity-50", currentTheme.textMuted)}>
        <svg width="40" height="40" viewBox="0 0 40 40" fill="none">
          <path
            d="M5 20H35M35 20L25 10M35 20L25 30"
            stroke="currentColor"
            strokeWidth="2"
            strokeLinecap="round"
          />
        </svg>
      </div>
    </div>
  )

  const renderMemoryItem = (memory: Memory, index: number) => {
    const categoryConfig = getCategoryConfig(memory.category)
    const isEditing = editingId === memory.id

    return (
      <div
        key={memory.id}
        className="rounded-xl transition-all duration-200 animate-fade-in group relative overflow-hidden"
        style={{
          animationDelay: `${index * 50}ms`,
        }}
      >
        <div
          className={cn(
            "absolute inset-0 opacity-0 group-hover:opacity-100 transition-opacity duration-300",
            isDark ? "bg-gradient-to-br from-white/5 to-transparent" : "bg-gradient-to-br from-slate-50/50 to-transparent"
          )}
        />
        <div
          className="relative"
          style={{
            background: isEditing
              ? (isDark ? 'rgba(255,255,255,0.1)' : 'rgba(0,0,0,0.05)')
              : (isDark ? 'rgba(255,255,255,0.03)' : 'rgba(0,0,0,0.01)'),
            border: isEditing
              ? `2px solid ${currentTheme.colors.accent}`
              : (isDark ? '1px solid rgba(255,255,255,0.08)' : '1px solid rgba(0,0,0,0.06)'),
            padding: '14px',
            borderRadius: '12px'
          }}
        >
          <div
            className={cn(
              "absolute left-0 top-3 bottom-3 w-1 rounded-r-full bg-gradient-to-b",
              categoryConfig.gradient
            )}
          />
          <div className="flex items-start justify-between gap-3 pl-2">
            <div className="flex-1 min-w-0">
              <div className="flex items-center gap-2 mb-2.5">
                <div className={cn(
                  "inline-flex items-center gap-1 px-2.5 py-1 rounded-lg text-xs font-medium bg-gradient-to-r text-white shadow-md",
                  categoryConfig.gradient
                )}>
                  <Tag className="w-3 h-3" />
                  {getCategoryLabel(memory.category)}
                </div>
                {memory.importance >= 0.5 && (
                  <div className="flex items-center gap-0.5">
                    {getImportanceStars(memory.importance).map((filled, i) => (
                      <Star
                        key={i}
                        className={cn(
                          "w-2.5 h-2.5 transition-transform",
                          filled
                            ? "text-amber-400 fill-amber-400"
                            : isDark ? "text-slate-600" : "text-slate-300"
                        )}
                      />
                    ))}
                  </div>
                )}
              </div>

              {isEditing ? (
                <div className="space-y-3 pl-2">
                  <textarea
                    value={editContent}
                    onChange={(e) => setEditContent(e.target.value)}
                    className={cn(
                      "w-full p-3 rounded-xl resize-none focus:outline-none focus:ring-2 text-sm",
                      isDark
                        ? "bg-white/5 border border-white/15 text-slate-200"
                        : "bg-slate-50 border border-slate-200 text-slate-700"
                    )}
                    rows={3}
                    autoFocus
                  />
                  <div className="flex flex-wrap items-center gap-2">
                    <select
                      value={editCategory}
                      onChange={(e) => setEditCategory(e.target.value)}
                      className={cn(
                        "px-3 py-1.5 rounded-lg text-xs",
                        isDark
                          ? "bg-white/10 border border-white/15 text-slate-300"
                          : "bg-slate-50 border border-slate-200 text-slate-700"
                      )}
                    >
                      <option value="general">通用</option>
                      <option value="conversation_insight">洞察</option>
                      <option value="note">笔记</option>
                      <option value="fact">事实</option>
                      <option value="concept">概念</option>
                      <option value="term">术语</option>
                    </select>
                    <div className="flex items-center gap-2 text-xs">
                      <span className={currentTheme.textMuted}>重要:</span>
                      <input
                        type="range"
                        min="0.1"
                        max="1"
                        step="0.1"
                        value={editImportance}
                        onChange={(e) => setEditImportance(parseFloat(e.target.value))}
                        className="w-20 accent-indigo-500"
                      />
                      <span className={cn("font-medium min-w-[2rem]", currentTheme.textPrimary)}>{editImportance.toFixed(1)}</span>
                    </div>
                    <div className="flex gap-1.5 ml-auto">
                      <button
                        onClick={() => handleSave(memory.id)}
                        className="px-4 py-1.5 bg-gradient-to-r from-indigo-500 to-purple-500 text-white rounded-lg text-xs font-medium shadow-md hover:shadow-lg transition-shadow"
                      >
                        保存
                      </button>
                      <button
                        onClick={() => setEditingId(null)}
                        className={cn(
                          "px-3 py-1.5 rounded-lg text-xs",
                          isDark
                            ? "bg-white/10 hover:bg-white/15 text-slate-300"
                            : "bg-slate-100 hover:bg-slate-200 text-slate-600"
                        )}
                      >
                        取消
                      </button>
                    </div>
                  </div>
                </div>
              ) : (
                <>
                  <p className={cn("text-sm leading-relaxed line-clamp-3 pl-2", currentTheme.textSecondary)}>
                    {memory.content}
                  </p>
                  <div className={cn(
                    "flex items-center gap-4 mt-3 pt-2.5 border-t text-[11px] pl-2",
                    currentTheme.textMuted,
                    isDark ? "border-white/8" : "border-slate-100"
                  )}>
                    <div className="flex items-center gap-1.5">
                      <RefreshCw className="w-3 h-3" />
                      <span>复习 {memory.review_count}</span>
                    </div>
                    <div className="flex items-center gap-1.5">
                      <Calendar className="w-3 h-3" />
                      <span>{formatNextReview(memory.next_review)}</span>
                    </div>
                  </div>
                </>
              )}
            </div>

            {!isEditing && (
              <div className="flex items-center gap-1 opacity-0 group-hover:opacity-100 transition-all transform translate-x-2 group-hover:translate-x-0 flex-shrink-0">
                <button
                  onClick={() => handleEdit(memory)}
                  className={cn(
                    "p-2 rounded-xl transition-all",
                    isDark ? "bg-white/10 hover:bg-white/15" : "bg-slate-100 hover:bg-slate-200"
                  )}
                >
                  <Edit2 className={cn("w-4 h-4", currentTheme.textMuted)} />
                </button>
                <button
                  onClick={() => handleDelete(memory.id)}
                  className={cn(
                    "p-2 rounded-xl transition-all",
                    isDark ? "hover:bg-red-500/20" : "hover:bg-red-50"
                  )}
                >
                  <Trash2 className={cn(
                    "w-4 h-4",
                    isDark ? "text-slate-400 hover:text-red-400" : "text-slate-500 hover:text-red-500"
                  )} />
                </button>
              </div>
            )}
          </div>
        </div>
      </div>
    )
  }

  return (
    <div className="h-full overflow-y-auto p-4 scrollbar-thin relative">
      <div
        className="absolute top-0 left-0 w-40 h-40 rounded-full blur-3xl opacity-10 pointer-events-none"
        style={{ background: `radial-gradient(circle, ${currentTheme.colors.accent} 0%, transparent 70%)` }}
      />
      <div className="space-y-3 relative">
        {memories.length === 0 ? renderEmptyState() : memories.map((memory, index) => renderMemoryItem(memory, index))}
      </div>
    </div>
  )
}

function formatNextReview(nextReview?: string | null): string {
  if (!nextReview) return '未设置'
  const date = new Date(nextReview)
  const now = new Date()
  const diff = date.getTime() - now.getTime()
  const days = Math.ceil(diff / (1000 * 60 * 60 * 24))

  if (days < 0) return `过期${Math.abs(days)}天`
  if (days === 0) return '今天'
  if (days === 1) return '明天'
  if (days <= 7) return `${days}天后`
  return `${Math.ceil(days / 7)}周后`
}
