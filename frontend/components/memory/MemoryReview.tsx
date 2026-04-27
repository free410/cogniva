'use client'

import React, { useState, useEffect, useCallback } from 'react'
import { Sparkles, Brain } from 'lucide-react'
import { useMemoryStore } from '@/stores'
import { cn } from '@/lib/utils'
import { useTheme } from '@/contexts/ThemeContext'

export function MemoryReview({ memories: propMemories }: { memories?: any[] }) {
  const [currentIndex, setCurrentIndex] = useState(0)
  const [localMemories, setLocalMemories] = useState<any[]>([])
  const { dueMemories, reviewMemory, fetchDueMemories, fetchStatistics, fetchMemories } = useMemoryStore()
  const { currentTheme, isDark } = useTheme()

  // 初始化记忆列表
  useEffect(() => {
    const mems = propMemories || dueMemories
    setLocalMemories(mems)
    setCurrentIndex(0)
  }, [propMemories, dueMemories])

  // 没有记忆时显示
  if (localMemories.length === 0) {
    return (
      <div className="text-center py-16 animate-fade-in">
        <div className={cn(
          "w-24 h-24 mx-auto rounded-3xl flex items-center justify-center mb-6 shadow-2xl",
          isDark ? "bg-white/5" : "bg-slate-100"
        )}>
          <Sparkles className={cn("w-12 h-12", isDark ? "text-emerald-400" : "text-emerald-500")} />
        </div>
        <h3 className={cn("text-xl font-bold mb-2", currentTheme.textPrimary)}>没有待复习的记忆</h3>
        <p className={cn("mb-6", currentTheme.textMuted)}>太棒了！当前没有需要复习的记忆。</p>
        <button
          onClick={fetchDueMemories}
          className={cn(
            "px-6 py-3 rounded-xl border transition-all",
            isDark 
              ? "bg-white/5 hover:bg-white/10 border-white/10 text-slate-300" 
              : "bg-slate-100 hover:bg-slate-200 border-slate-200 text-slate-600"
          )}
        >
          刷新列表
        </button>
      </div>
    )
  }

  // 确保索引有效
  const safeIndex = Math.min(currentIndex, localMemories.length - 1)
  const currentMemory = localMemories[safeIndex]

  // 如果当前记忆不存在，重新检查
  if (!currentMemory) {
    return (
      <div className="text-center py-16 animate-fade-in">
        <div className={cn(
          "w-24 h-24 mx-auto rounded-3xl flex items-center justify-center mb-6 shadow-2xl",
          isDark ? "bg-white/5" : "bg-slate-100"
        )}>
          <Sparkles className={cn("w-12 h-12", isDark ? "text-emerald-400" : "text-emerald-500")} />
        </div>
        <h3 className={cn("text-xl font-bold mb-2", currentTheme.textPrimary)}>复习完成</h3>
        <p className={cn("mb-6", currentTheme.textMuted)}>太棒了！你已经复习完所有记忆。</p>
        <button
          onClick={fetchDueMemories}
          className={cn(
            "px-6 py-3 rounded-xl border transition-all",
            isDark 
              ? "bg-white/5 hover:bg-white/10 border-white/10 text-slate-300" 
              : "bg-slate-100 hover:bg-slate-200 border-slate-200 text-slate-600"
          )}
        >
          刷新列表
        </button>
      </div>
    )
  }

  const handleReview = async (quality: number) => {
    try {
      await reviewMemory(currentMemory.id, quality)
      
      // 更新本地列表
      const newMemories = localMemories.filter(m => m.id !== currentMemory.id)
      setLocalMemories(newMemories)
      
      // 刷新全局数据
      await Promise.all([fetchDueMemories(), fetchStatistics(), fetchMemories()])
      
      // 如果还有记忆，重置索引
      if (newMemories.length > 0) {
        setCurrentIndex(0)
      } else {
        setCurrentIndex(0)
      }
    } catch (error) {
      console.error('Review failed:', error)
    }
  }

  const qualityOptions = [
    { quality: 0, label: '完全忘记', desc: '想不起来', icon: '✗', color: 'from-red-500/20 to-rose-500/20 border-red-500/30 hover:border-red-500/50' },
    { quality: 1, label: '几乎忘记', desc: '很模糊', icon: '~', color: 'from-orange-500/20 to-amber-500/20 border-orange-500/30 hover:border-orange-500/50' },
    { quality: 2, label: '记忆模糊', desc: '勉强记得', icon: '~', color: 'from-amber-500/20 to-yellow-500/20 border-amber-500/30 hover:border-amber-500/50' },
    { quality: 3, label: '基本记住', desc: '大致记得', icon: '✓', color: 'from-lime-500/20 to-green-500/20 border-lime-500/30 hover:border-lime-500/50' },
    { quality: 4, label: '记住', desc: '比较清晰', icon: '✓', color: 'from-green-500/20 to-emerald-500/20 border-green-500/30 hover:border-green-500/50' },
    { quality: 5, label: '完全记住', desc: '轻松回忆', icon: '✓', color: 'from-emerald-500/20 to-teal-500/20 border-emerald-500/30 hover:border-emerald-500/50' },
  ]

  return (
    <div className="space-y-6 max-w-3xl mx-auto">
      {/* 进度指示器 */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-4">
          <span className={cn("text-sm", currentTheme.textMuted)}>
            复习进度: <span className={cn("font-medium", currentTheme.textPrimary)}>1</span> / {localMemories.length}
          </span>
          <span className={cn(
            "px-3 py-1 rounded-full text-sm font-medium border",
            isDark 
              ? "bg-amber-500/20 text-amber-400 border-amber-500/30" 
              : "bg-amber-100 text-amber-600 border-amber-200"
          )}>
            待复习: {localMemories.length}
          </span>
        </div>
      </div>

      {/* 记忆卡片 */}
      <div className={cn(
        "p-8 rounded-2xl border shadow-2xl animate-fade-in",
        isDark ? "bg-white/5 border-white/10" : "bg-white/90 border-slate-200"
      )} style={!isDark ? { backdropFilter: 'blur(12px)' } : {}}>
        <div className="text-center mb-8">
          <div className="flex items-center justify-center gap-3 mb-4">
            <div className="w-12 h-12 rounded-xl flex items-center justify-center" 
              style={{ 
                background: currentTheme.colors.accent,
                boxShadow: `0 4px 15px ${currentTheme.colors.accent}40`
              }}
            >
              <Brain className="w-6 h-6 text-white" />
            </div>
            <span className={cn("text-xl font-bold", currentTheme.textPrimary)}>间隔重复复习</span>
          </div>
          <p className={cn("text-sm", currentTheme.textMuted)}>
            根据你的记忆质量，系统会自动安排下次复习时间
          </p>
        </div>

        {/* 记忆内容 */}
        <div className={cn(
          "p-6 rounded-xl border mb-8"
        )}
        style={{ 
          background: currentTheme.colors.accentBg,
          borderColor: `${currentTheme.colors.accent}30`
        }}
        >
          <p className={cn("text-lg leading-relaxed text-center mb-4", currentTheme.textSecondary)}>
            {currentMemory.content}
          </p>
          <div className={cn("flex items-center justify-center gap-6 text-sm", currentTheme.textMuted)}>
            <span className="flex items-center gap-2">
              <span className="w-2 h-2 rounded-full" style={{ backgroundColor: currentTheme.colors.accent }}></span>
              类别: {currentMemory.category || 'general'}
            </span>
            <span className="flex items-center gap-2">
              <span className="w-2 h-2 rounded-full bg-emerald-500"></span>
              已复习 {currentMemory.review_count} 次
            </span>
          </div>
        </div>

        {/* 复习质量选择 */}
        <div>
          <label className={cn("block text-sm font-medium mb-4 text-center", currentTheme.textSecondary)}>
            你回忆这个内容的难度如何？
          </label>
          <div className="grid grid-cols-3 gap-3">
            {qualityOptions.map(({ quality, label, desc, icon, color }) => (
              <button
                key={quality}
                onClick={() => handleReview(quality)}
                className={cn(
                  "p-4 rounded-xl border transition-all duration-200 hover:scale-[1.02] active:scale-[0.98] bg-gradient-to-br",
                  color
                )}
              >
                <div className="text-2xl mb-1">{icon}</div>
                <div className={cn("font-semibold text-sm", currentTheme.textPrimary)}>{label}</div>
                <div className={cn("text-xs mt-1", currentTheme.textMuted)}>{desc}</div>
              </button>
            ))}
          </div>
        </div>
      </div>
    </div>
  )
}
