'use client'

import React, { useEffect } from 'react'
import { useMemoryStore } from '@/stores'
import { Brain, TrendingUp, Calendar, Target, Sparkles, BarChart3 } from 'lucide-react'
import { cn } from '@/lib/utils'
import { useTheme } from '@/contexts/ThemeContext'

export function MemoryStats() {
  const { statistics, fetchStatistics } = useMemoryStore()
  const { currentTheme, isDark } = useTheme()

  useEffect(() => {
    fetchStatistics()
  }, [])

  if (!statistics) {
    return null
  }

  const translateCategory = (category: string): string => {
    const translations: Record<string, string> = {
      general: '通用',
      conversation_insight: '对话洞察',
      note: '笔记',
      fact: '事实',
      concept: '概念',
      term: '术语'
    }
    return translations[category] || category
  }

  const categoryColors: Record<string, { gradient: string; text: string; bg: string }> = {
    general: { gradient: 'from-blue-500 to-cyan-500', text: 'text-blue-400', bg: 'bg-blue-500' },
    conversation_insight: { gradient: 'from-purple-500 to-pink-500', text: 'text-purple-400', bg: 'bg-purple-500' },
    note: { gradient: 'from-emerald-500 to-teal-500', text: 'text-emerald-400', bg: 'bg-emerald-500' },
    fact: { gradient: 'from-amber-500 to-orange-500', text: 'text-amber-400', bg: 'bg-amber-500' },
    concept: { gradient: 'from-indigo-500 to-violet-500', text: 'text-indigo-400', bg: 'bg-indigo-500' },
    term: { gradient: 'from-rose-500 to-red-500', text: 'text-rose-400', bg: 'bg-rose-500' },
  }

  const categories = Object.entries(statistics.categories || {})
  const maxCount = Math.max(...categories.map(([, count]) => count as number), 1)

  return (
    <div className="space-y-4">
      {/* 分类分布详情 */}
      <div className={cn(
        "p-5 rounded-2xl border backdrop-blur-sm transition-all hover:shadow-lg",
        isDark 
          ? "bg-white/[0.03] border-white/10 hover:bg-white/[0.05]" 
          : "bg-white/80 border-slate-200 hover:bg-white/90"
      )}>
        <h3 className={cn("text-sm font-semibold mb-4 flex items-center gap-2", currentTheme.textPrimary)}>
          <div 
            className="w-6 h-6 rounded-md flex items-center justify-center"
            style={{ background: `${currentTheme.colors.accent}20`, color: currentTheme.colors.accent }}
          >
            <BarChart3 className="w-3.5 h-3.5" />
          </div>
          分类详情
        </h3>
        
        {categories.length === 0 ? (
          <div className="text-center py-8">
            <div className="w-16 h-16 mx-auto mb-3 rounded-2xl bg-gradient-to-br from-slate-100 to-slate-200 dark:from-slate-800/50 dark:to-slate-800 flex items-center justify-center">
              <Brain className="w-8 h-8 text-slate-400" />
            </div>
            <p className={cn("text-sm", currentTheme.textMuted)}>暂无分类数据</p>
            <p className={cn("text-xs mt-1", currentTheme.textMuted)}>创建第一个记忆开始学习</p>
          </div>
        ) : (
          <div className="space-y-4">
            {categories.map(([category, count]) => {
              const colors = categoryColors[category] || categoryColors.general
              const percentage = ((count as number) / maxCount) * 100
              
              return (
                <div key={category} className="group">
                  <div className="flex items-center justify-between mb-2">
                    <div className="flex items-center gap-2.5">
                      <div className={cn(
                        "w-8 h-8 rounded-xl bg-gradient-to-br flex items-center justify-center shadow-md transition-transform group-hover:scale-110",
                        colors.gradient
                      )}>
                        <Brain className="w-4 h-4 text-white" />
                      </div>
                      <div>
                        <span className={cn("text-sm font-medium", currentTheme.textPrimary)}>{translateCategory(category)}</span>
                        <p className={cn("text-xs", currentTheme.textMuted)}>记忆数量</p>
                      </div>
                    </div>
                    <div className="text-right">
                      <span className={cn("text-lg font-bold", colors.text)}>{String(count)}</span>
                      <p className={cn("text-xs", currentTheme.textMuted)}>{Math.round((count as number / (statistics.total_memories || 1)) * 100)}%</p>
                    </div>
                  </div>
                  <div className={cn(
                    "w-full rounded-full h-2.5 overflow-hidden shadow-inner",
                    isDark ? "bg-white/5" : "bg-slate-100"
                  )}>
                    <div
                      className={cn(
                        "h-2.5 rounded-full transition-all duration-700 bg-gradient-to-r shadow-md",
                        colors.gradient
                      )}
                      style={{ width: `${percentage}%` }}
                    />
                  </div>
                </div>
              )
            })}
          </div>
        )}
      </div>

      {/* 学习建议 */}
      {statistics.due_reviews > 0 && (
        <div className={cn(
          "p-5 rounded-2xl border backdrop-blur-sm overflow-hidden relative",
          isDark 
            ? "bg-gradient-to-br from-amber-500/10 to-orange-500/10 border-amber-500/20" 
            : "bg-gradient-to-br from-amber-50 to-orange-50 border-amber-200"
        )}>
          {/* 装饰背景 */}
          <div 
            className="absolute top-0 right-0 w-40 h-40 rounded-full blur-2xl opacity-30"
            style={{ background: 'linear-gradient(135deg, #f59e0b, #ef4444)' }}
          />
          
          <div className="flex items-start gap-4 relative">
            <div className="w-12 h-12 rounded-2xl bg-gradient-to-br from-amber-500 to-orange-500 flex items-center justify-center shadow-lg shadow-amber-500/30 flex-shrink-0">
              <Sparkles className="w-6 h-6 text-white" />
            </div>
            <div className="flex-1">
              <p className={cn("font-bold text-base mb-1", isDark ? "text-amber-200" : "text-amber-800")}>
                有 {statistics.due_reviews} 条记忆等待复习
              </p>
              <p className={cn("text-sm", currentTheme.textMuted)}>
                定期复习可以有效巩固记忆，使用间隔重复算法让学习更高效
              </p>
              <button
                onClick={() => {
                  const event = new CustomEvent('startMemoryReview')
                  window.dispatchEvent(event)
                }}
                className={cn(
                  "mt-3 px-4 py-2 rounded-xl text-xs font-medium transition-all hover:scale-105",
                  isDark 
                    ? "bg-amber-500/20 hover:bg-amber-500/30 text-amber-300" 
                    : "bg-amber-100 hover:bg-amber-200 text-amber-700"
                )}
              >
                立即开始复习
              </button>
            </div>
          </div>
        </div>
      )}

      {/* 学习小贴士 */}
      <div className={cn(
        "p-4 rounded-2xl border backdrop-blur-sm",
        isDark 
          ? "bg-white/[0.02] border-white/10" 
          : "bg-white/60 border-slate-200"
      )}>
        <div className="flex items-start gap-3">
          <div className={cn(
            "w-8 h-8 rounded-lg flex items-center justify-center flex-shrink-0",
            isDark ? "bg-white/10" : "bg-slate-100"
          )}>
            <Target className="w-4 h-4" style={{ color: currentTheme.colors.accent }} />
          </div>
          <div>
            <p className={cn("text-xs font-medium mb-1", currentTheme.textPrimary)}>记忆技巧</p>
            <p className={cn("text-xs leading-relaxed", currentTheme.textMuted)}>
              尝试将新知识与已有知识建立联系，使用自己的话复述，定期回顾能显著提升长期记忆效果。
            </p>
          </div>
        </div>
      </div>
    </div>
  )
}
