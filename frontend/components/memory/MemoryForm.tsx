'use client'

import React, { useState } from 'react'
import { Plus, Sparkles, BookOpen, Lightbulb, FileText, Star, Atom, Code, Check } from 'lucide-react'
import { useMemoryStore } from '@/stores'
import { cn } from '@/lib/utils'
import { useTheme } from '@/contexts/ThemeContext'
import { getAccentGradient, getAccentRgba } from '@/contexts/themeUtils'

export function MemoryForm() {
  const [content, setContent] = useState('')
  const [category, setCategory] = useState('general')
  const [importance, setImportance] = useState(0.5)
  const { createMemory } = useMemoryStore()
  const { currentTheme, isDark } = useTheme()
  const accentGradient = getAccentGradient(currentTheme.accentColor)
  const accentColor = currentTheme.accentColor

  const categories = [
    { value: 'general', label: '通用', icon: BookOpen, color: 'from-blue-500 to-cyan-500' },
    { value: 'conversation_insight', label: '对话洞察', icon: Lightbulb, color: 'from-purple-500 to-pink-500' },
    { value: 'note', label: '笔记', icon: FileText, color: 'from-emerald-500 to-teal-500' },
    { value: 'fact', label: '事实', icon: Star, color: 'from-amber-500 to-orange-500' },
    { value: 'concept', label: '概念', icon: Atom, color: 'from-indigo-500 to-violet-500' },
    { value: 'term', label: '术语', icon: Code, color: 'from-rose-500 to-red-500' },
  ]

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!content.trim()) return

    try {
      await createMemory(content.trim(), category, importance)
      setContent('')
      setCategory('general')
      setImportance(0.5)
    } catch (error) {
      console.error('Failed to create memory:', error)
    }
  }

  const getImportanceLevel = () => {
    if (importance >= 0.8) return { text: '高', color: 'text-red-400', bg: 'bg-red-500' }
    if (importance >= 0.5) return { text: '中', color: 'text-amber-400', bg: 'bg-amber-500' }
    return { text: '低', color: 'text-green-400', bg: 'bg-green-500' }
  }

  const importanceLevel = getImportanceLevel()

  return (
    <div className="h-full overflow-y-auto p-6 scrollbar-thin">
      <div className="max-w-2xl mx-auto">
        {/* 标题区域 */}
        <div className="flex items-center gap-4 mb-8">
          <div className={cn(
            "w-14 h-14 rounded-2xl bg-gradient-to-br flex items-center justify-center shadow-xl",
            accentGradient
          )}>
            <Sparkles className="w-7 h-7 text-white" />
          </div>
          <div>
            <h3 className={cn("text-xl font-bold", currentTheme.textPrimary)}>创建新记忆</h3>
            <p className={cn("text-sm", currentTheme.textMuted)}>添加重要的知识点到长期记忆库</p>
          </div>
        </div>

        <form onSubmit={handleSubmit} className="space-y-8">
          {/* 记忆内容 */}
          <div className={cn(
            "p-6 rounded-2xl border",
            isDark 
              ? "bg-white/5 border-white/10" 
              : "bg-white/80 border-slate-200"
          )}>
            <label className={cn("block text-sm font-semibold mb-3", currentTheme.textPrimary)}>
              记忆内容
            </label>
            <textarea
              value={content}
              onChange={(e) => setContent(e.target.value)}
              placeholder="输入要记忆的内容，例如：重要的概念、公式、事实..."
                  className={cn(
                    "w-full p-4 rounded-xl resize-none focus:outline-none focus:ring-2 text-sm"
                  )}
                  style={{
                    background: isDark ? 'rgba(255,255,255,0.05)' : 'rgba(0,0,0,0.02)',
                    border: `1px solid ${isDark ? 'rgba(255,255,255,0.1)' : 'rgba(0,0,0,0.1)'}`,
                    color: isDark ? '#cbd5e1' : '#334155',
                    '--tw-ring-color': currentTheme.colors.accent + '60'
                  } as React.CSSProperties}
                  rows={5}
                />
          </div>

          {/* 分类选择 */}
          <div className={cn(
            "p-6 rounded-2xl border",
            isDark 
              ? "bg-white/5 border-white/10" 
              : "bg-white/80 border-slate-200"
          )}>
            <label className={cn("block text-sm font-semibold mb-4", currentTheme.textPrimary)}>
              选择分类
            </label>
            <div className="grid grid-cols-3 gap-3">
              {categories.map((cat) => {
                const Icon = cat.icon
                const isSelected = category === cat.value
                return (
                  <button
                    key={cat.value}
                    type="button"
                    onClick={() => setCategory(cat.value)}
                    className={cn(
                      "relative flex flex-col items-center gap-2 p-4 rounded-xl border-2 transition-all duration-200 overflow-hidden",
                      isSelected
                        ? "border-transparent shadow-lg scale-[1.02]"
                        : isDark
                          ? "bg-white/5 border-white/10 text-slate-400 hover:border-white/20 hover:bg-white/10"
                          : "bg-slate-50 border-slate-200 text-slate-600 hover:border-slate-300 hover:bg-slate-100"
                    )}
                  >
                    {isSelected && (
                      <div 
                        className={cn("absolute inset-0 bg-gradient-to-br opacity-90", cat.color)}
                      />
                    )}
                    <Icon className={cn("w-6 h-6 relative z-10", isSelected ? "text-white" : "")} />
                    <span className={cn("text-xs font-semibold relative z-10", isSelected ? "text-white" : "")}>
                      {cat.label}
                    </span>
                    {isSelected && (
                      <div className="absolute top-1 right-1 w-5 h-5 rounded-full bg-white/30 flex items-center justify-center">
                        <Check className="w-3 h-3 text-white" />
                      </div>
                    )}
                  </button>
                )
              })}
            </div>
          </div>

          {/* 重要性滑块 */}
          <div className={cn(
            "p-6 rounded-2xl border",
            isDark 
              ? "bg-white/5 border-white/10" 
              : "bg-white/80 border-slate-200"
          )}>
            <div className="flex items-center justify-between mb-4">
              <label className={cn("text-sm font-semibold", currentTheme.textPrimary)}>
                重要性等级
              </label>
              <div className={cn(
                "px-4 py-1.5 rounded-full text-sm font-bold text-white",
                importanceLevel.bg
              )}>
                {importanceLevel.text}
              </div>
            </div>
            
            <div className="relative mb-4">
              <div className={cn(
                "h-4 rounded-full overflow-hidden",
                isDark ? "bg-white/10" : "bg-slate-200"
              )}>
                <div
                  className={cn("h-full rounded-full transition-all duration-300 bg-gradient-to-r", accentGradient)}
                  style={{ width: `${importance * 100}%` }}
                />
              </div>
              <input
                type="range"
                min="0.1"
                max="1"
                step="0.1"
                value={importance}
                onChange={(e) => setImportance(parseFloat(e.target.value))}
                className="absolute inset-0 w-full opacity-0 cursor-pointer h-4"
              />
              {/* 自定义滑块指示器 */}
              <div 
                className="absolute top-1/2 -translate-y-1/2 w-6 h-6 rounded-full shadow-lg bg-white transition-all duration-100 pointer-events-none"
                style={{ left: `calc(${importance * 100}% - 12px)`, border: `3px solid ${currentTheme.colors.accent}` }}
              />
            </div>
            
            <div className={cn("flex justify-between text-xs", currentTheme.textMuted)}>
              <span>普通信息</span>
              <span>关键知识</span>
            </div>
          </div>

          {/* 按钮 */}
          <div className="flex gap-4">
            <button
              type="submit"
              disabled={!content.trim()}
              className={cn(
                "flex-1 flex items-center justify-center gap-3 px-6 py-4 rounded-2xl font-semibold shadow-lg transition-all duration-200 disabled:cursor-not-allowed",
                content.trim()
                  ? `bg-gradient-to-r ${accentGradient} hover:shadow-xl text-white active:scale-[0.98]`
                  : isDark
                    ? "bg-slate-700 text-slate-500 cursor-not-allowed"
                    : "bg-slate-300 text-slate-500 cursor-not-allowed"
              )}
              style={content.trim() ? { boxShadow: `0 10px 25px ${getAccentRgba(accentColor, 0.3)}` } : {}}
            >
              <Plus className="w-5 h-5" />
              创建记忆
            </button>
            <button
              type="button"
              onClick={() => { setContent(''); setCategory('general'); setImportance(0.5); }}
              className={cn(
                "px-6 py-4 font-medium rounded-2xl transition-colors border-2",
                isDark 
                  ? "bg-white/5 hover:bg-white/10 border-white/10 text-slate-400" 
                  : "bg-slate-50 hover:bg-slate-100 border-slate-200 text-slate-600"
              )}
            >
              重置
            </button>
          </div>
        </form>
      </div>
    </div>
  )
}
