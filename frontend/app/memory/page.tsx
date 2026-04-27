'use client'

import React, { useState, useEffect, useRef } from 'react'
import { Layout } from '@/components/layout'
import { MemoryList, MemoryStats, MemoryReview } from '@/components/memory'
import { useTheme } from '@/contexts/ThemeContext'
import { useMemoryStore } from '@/stores'
import { cn } from '@/lib/utils'
import { Brain, Sparkles, BookOpen, RefreshCw } from 'lucide-react'

// 动态背景图标组件
function AnimatedIconBg({ children }: { children: React.ReactNode }) {
  const [animationOffset, setAnimationOffset] = useState(0)
  const frameRef = useRef<number>()
  
  useEffect(() => {
    let startTime = Date.now()
    const animate = () => {
      const elapsed = Date.now() - startTime
      setAnimationOffset(Math.sin(elapsed / 2000) * 0.5 + 0.5)
      frameRef.current = requestAnimationFrame(animate)
    }
    frameRef.current = requestAnimationFrame(animate)
    return () => {
      if (frameRef.current) cancelAnimationFrame(frameRef.current)
    }
  }, [])
  
  // 温暖的琥珀色渐变
  const colors = [
    '#FAF0DB', // 浅米色
    '#E8D5B5', // 深一点
    '#F5E6C8', // 暖黄
    '#EBD9B0', // 奶黄
  ]
  
  const color1 = colors[Math.floor(animationOffset * 2) % colors.length]
  const color2 = colors[(Math.floor(animationOffset * 2) + 1) % colors.length]
  const color3 = colors[(Math.floor(animationOffset * 2) + 2) % colors.length]
  
  return (
    <div
      style={{
        width: '2.75rem',
        height: '2.75rem',
        borderRadius: '0.75rem',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        boxShadow: `0 4px 15px rgba(194, 149, 74, ${0.3 + animationOffset * 0.2})`,
        backgroundImage: `linear-gradient(135deg, ${color1}, ${color2}, ${color3})`,
        backgroundSize: '300% 300%',
        animation: 'warm-flow 4s ease infinite',
      }}
    >
      {children}
    </div>
  )
}

function MemoryPageContent() {
  const [showReview, setShowReview] = useState(false)
  const { currentTheme, isDark } = useTheme()
  const { statistics, dueMemories, fetchStatistics, fetchDueMemories } = useMemoryStore()
  const { colors } = currentTheme

  useEffect(() => {
    fetchStatistics()
    fetchDueMemories()
  }, [])

  // 复习按钮组件
  const ReviewButton = () => (
    <button
      onClick={() => setShowReview(true)}
      className={cn(
        "flex items-center gap-2 px-4 py-2.5 rounded-xl text-sm font-medium transition-all shadow-lg",
        (statistics?.due_reviews || 0) > 0
          ? "bg-gradient-to-r from-amber-500 to-orange-500 text-white hover:shadow-xl animate-pulse"
          : isDark
            ? "bg-white/10 hover:bg-white/20 text-slate-300"
            : "bg-slate-100 hover:bg-slate-200 text-slate-600"
      )}
    >
      <RefreshCw className={cn("w-4 h-4", (statistics?.due_reviews || 0) > 0 ? "animate-spin" : "")} 
        style={{ animationDuration: (statistics?.due_reviews || 0) > 0 ? '3s' : '0s' }} />
      {(statistics?.due_reviews || 0) > 0 
        ? `复习 (${statistics.due_reviews})`
        : '开始复习'
      }
    </button>
  )

  // 如果显示复习模式
  if (showReview) {
    return (
      <div className="h-full flex flex-col">
        {/* 复习模式 header */}
        <div 
          className="px-6 border-b flex items-center justify-between h-16 flex-shrink-0"
          style={{ borderColor: colors.border }}
        >
          <div className="flex items-center gap-4">
            <AnimatedIconBg>
              <span className="text-xl">🧠</span>
            </AnimatedIconBg>
            <div>
              <h1 className="text-lg font-bold" style={{ color: colors.textPrimary }}>复习模式</h1>
              <p className="text-xs" style={{ color: colors.textMuted }}>间隔重复 · 智能复习</p>
            </div>
          </div>
          <button
            onClick={() => setShowReview(false)}
            className={cn(
              "px-4 py-2 rounded-xl text-sm font-medium transition-all",
              isDark
                ? "bg-white/10 hover:bg-white/20 text-slate-300"
                : "bg-slate-100 hover:bg-slate-200 text-slate-600"
            )}
          >
            退出复习
          </button>
        </div>
        <div className="flex-1 overflow-hidden">
          <div className="h-full overflow-y-auto p-6">
            <MemoryReview memories={dueMemories} />
          </div>
        </div>
      </div>
    )
  }

  return (
    <div className="h-full flex flex-col">
      {/* 顶部标题栏 */}
      <div 
        className="px-6 border-b flex items-center justify-between h-16 flex-shrink-0"
        style={{ borderColor: colors.border }}
      >
          <div className="flex items-center gap-4">
            <AnimatedIconBg>
              <span className="text-xl">🧠</span>
            </AnimatedIconBg>
          <div>
            <h1 className="text-lg font-bold" style={{ color: colors.textPrimary }}>长期记忆</h1>
            <p className="text-xs" style={{ color: colors.textMuted }}>间隔重复 · 智能复习</p>
          </div>
        </div>
        
        {/* 复习按钮 */}
        <ReviewButton />
      </div>

      {/* 主内容区 - 三栏布局 */}
      <div className="flex-1 overflow-hidden">
        <div className="h-full flex flex-col xl:flex-row gap-0">
          
          {/* 左侧：记忆列表 */}
          <div className="flex-1 xl:flex-none xl:w-[45%] h-full overflow-hidden border-r" style={{ borderColor: colors.border }}>
            <MemoryList />
          </div>

          {/* 右侧：创建 + 统计 */}
          <div className="flex-1 h-full overflow-hidden flex flex-col relative">
            {/* 装饰背景 */}
            <div className="absolute inset-0 pointer-events-none overflow-hidden">
              <div 
                className="absolute -top-20 -right-20 w-64 h-64 rounded-full blur-3xl opacity-20"
                style={{ background: `radial-gradient(circle, ${currentTheme.colors.accent}40 0%, transparent 70%)` }}
              />
              <div 
                className="absolute -bottom-32 -left-20 w-80 h-80 rounded-full blur-3xl opacity-15"
                style={{ background: 'linear-gradient(135deg, #f59e0b40, #ef444440)' }}
              />
            </div>

            {/* 顶部：快速统计卡片 */}
            <div 
              className="flex-shrink-0 p-4 border-b relative"
              style={{ borderColor: colors.border }}
            >
              <div className="flex items-center justify-between mb-3">
                <div className="flex items-center gap-2">
                  <Sparkles className="w-4 h-4" style={{ color: currentTheme.colors.accent }} />
                  <h3 className={cn("text-sm font-semibold", currentTheme.textPrimary)}>学习概览</h3>
                </div>
                
                {/* 复习快捷入口 */}
                {(statistics?.due_reviews || 0) > 0 && (
                  <button
                    onClick={() => setShowReview(true)}
                    className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-amber-500/20 text-amber-400 text-xs font-medium hover:bg-amber-500/30 transition-all hover:scale-105"
                  >
                    <RefreshCw className="w-3 h-3" />
                    立即复习
                  </button>
                )}
              </div>
              <div className="grid grid-cols-4 gap-3">
                <StatCard 
                  icon={<Brain className="w-4 h-4" />}
                  value={statistics?.total_memories || 0}
                  label="总记忆"
                  isDark={isDark}
                  currentTheme={currentTheme}
                />
                <StatCard 
                  icon={<BookOpen className="w-4 h-4" />}
                  value={statistics?.due_reviews || 0}
                  label="待复习"
                  isDark={isDark}
                  currentTheme={currentTheme}
                  highlight={(statistics?.due_reviews || 0) > 0}
                />
                <StatCard 
                  icon={<Sparkles className="w-4 h-4" />}
                  value={statistics?.total_reviews || 0}
                  label="总复习"
                  isDark={isDark}
                  currentTheme={currentTheme}
                />
                <StatCard 
                  icon={<span className="text-sm">📊</span>}
                  value={statistics?.average_review_count || 0}
                  label="平均"
                  isDark={isDark}
                  currentTheme={currentTheme}
                />
              </div>
            </div>

            {/* 分类分布 */}
            <div 
              className="flex-shrink-0 px-4 py-3 border-b relative"
              style={{ borderColor: colors.border }}
            >
              <CategoryBar 
                categories={statistics?.categories || {}} 
                total={statistics?.total_memories || 0}
                isDark={isDark}
                currentTheme={currentTheme}
              />
            </div>

            {/* 下方：创建表单 + 完整统计 */}
            <div className="flex-1 overflow-y-auto scrollbar-thin relative">
              <div className="p-4 space-y-4">
                {/* 创建记忆表单 */}
                <div className={cn(
                  "rounded-2xl border p-4 backdrop-blur-sm transition-all hover:shadow-lg",
                  isDark 
                    ? "bg-white/5 border-white/10 hover:bg-white/[0.07]" 
                    : "bg-white/80 border-slate-200 hover:bg-white/90"
                )}>
                  <MemoryFormInline 
                    isDark={isDark} 
                    currentTheme={currentTheme}
                  />
                </div>

                {/* 完整统计 */}
                <MemoryStats />
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}

function StatCard({ 
  icon, 
  value, 
  label, 
  isDark, 
  currentTheme, 
  highlight 
}: { 
  icon: React.ReactNode
  value: number
  label: string
  isDark: boolean
  currentTheme: any
  highlight?: boolean
}) {
  const borderColor = currentTheme.colors.border
  
  return (
    <div className={cn(
      "p-3 rounded-xl border transition-all hover:scale-[1.03] hover:shadow-lg group relative overflow-hidden",
      isDark 
        ? "bg-white/5 border-white/10 hover:border-white/20" 
        : "bg-white/80 border-slate-200 hover:border-slate-300"
    )}>
      {/* 悬停时的渐变背景 */}
      <div className={cn(
        "absolute inset-0 opacity-0 group-hover:opacity-100 transition-opacity duration-300",
        isDark ? "bg-gradient-to-br from-white/5 to-transparent" : "bg-gradient-to-br from-slate-50/50 to-transparent"
      )} />
      
      <div className="relative">
        <div className="flex items-center gap-2 mb-1">
          <div 
            className={cn(
              "w-7 h-7 rounded-lg flex items-center justify-center transition-transform group-hover:scale-110",
            )}
            style={{ 
              background: isDark 
                ? `linear-gradient(135deg, ${currentTheme.colors.accent}30, ${currentTheme.colors.accent}10)` 
                : `linear-gradient(135deg, ${currentTheme.colors.accent}20, ${currentTheme.colors.accent}05)`,
              border: `1px solid ${isDark ? 'rgba(255,255,255,0.1)' : 'rgba(0,0,0,0.08)'}`,
              color: currentTheme.colors.accent
            }}
          >
            {icon}
          </div>
          <span className={cn("text-xs", currentTheme.textMuted)}>{label}</span>
        </div>
        <p className={cn(
          "text-xl font-bold transition-colors",
          highlight 
            ? "text-amber-400" 
            : currentTheme.textPrimary
        )}>
          {value}
        </p>
      </div>
    </div>
  )
}

function CategoryBar({ 
  categories, 
  total, 
  isDark, 
  currentTheme 
}: { 
  categories: Record<string, number>
  total: number
  isDark: boolean
  currentTheme: any
}) {
  const categoryColors: Record<string, string> = {
    general: 'bg-gradient-to-r from-blue-500 to-cyan-500',
    conversation_insight: 'bg-gradient-to-r from-purple-500 to-pink-500',
    note: 'bg-gradient-to-r from-emerald-500 to-teal-500',
    fact: 'bg-gradient-to-r from-amber-500 to-orange-500',
    concept: 'bg-gradient-to-r from-indigo-500 to-violet-500',
    term: 'bg-gradient-to-r from-rose-500 to-red-500',
  }

  const categoryLabels: Record<string, string> = {
    general: '通用',
    conversation_insight: '洞察',
    note: '笔记',
    fact: '事实',
    concept: '概念',
    term: '术语',
  }

  const entries = Object.entries(categories)
  if (entries.length === 0) return null

  return (
    <div className="space-y-3">
      <div className="flex items-center justify-between">
        <span className={cn("text-xs font-medium", currentTheme.textMuted)}>分类分布</span>
        <span className={cn("text-xs font-medium", currentTheme.textMuted)}>共 {total} 条</span>
      </div>
      <div className="flex items-center gap-3">
        <div className="flex-1 flex h-2.5 rounded-full overflow-hidden bg-white/10 gap-0.5 shadow-inner">
          {entries.map(([cat, count]) => {
            const width = total > 0 ? ((count as number) / total) * 100 : 0
            return (
              <div
                key={cat}
                className={cn("h-full rounded-full transition-all duration-500", categoryColors[cat] || 'bg-slate-500')}
                style={{ width: `${width}%` }}
                title={`${categoryLabels[cat] || cat}: ${count}`}
              />
            )
          })}
        </div>
      </div>
      <div className="flex gap-3 flex-wrap">
        {entries.map(([cat, count]) => (
          <span key={cat} className={cn("flex items-center gap-1.5 text-xs", currentTheme.textMuted)}>
            <span className={cn("w-2 h-2 rounded-full", categoryColors[cat] || 'bg-slate-500')} />
            <span>{categoryLabels[cat] || cat}</span>
            <span className={cn("font-medium", currentTheme.textPrimary)}>{count}</span>
          </span>
        ))}
      </div>
    </div>
  )
}

function MemoryFormInline({ 
  isDark, 
  currentTheme
}: { 
  isDark: boolean
  currentTheme: any
}) {
  const [content, setContent] = React.useState('')
  const [category, setCategory] = React.useState('general')
  const [importance, setImportance] = React.useState(0.5)
  const [isSubmitting, setIsSubmitting] = React.useState(false)
  const { createMemory, fetchMemories, fetchStatistics } = useMemoryStore()

  const categories = [
    { value: 'general', label: '通用', color: 'from-blue-500 to-cyan-500' },
    { value: 'conversation_insight', label: '洞察', color: 'from-purple-500 to-pink-500' },
    { value: 'note', label: '笔记', color: 'from-emerald-500 to-teal-500' },
    { value: 'fact', label: '事实', color: 'from-amber-500 to-orange-500' },
    { value: 'concept', label: '概念', color: 'from-indigo-500 to-violet-500' },
    { value: 'term', label: '术语', color: 'from-rose-500 to-red-500' },
  ]

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!content.trim() || isSubmitting) return
    
    setIsSubmitting(true)
    try {
      await createMemory(content.trim(), category, importance)
      setContent('')
      setCategory('general')
      setImportance(0.5)
      // 刷新数据
      await Promise.all([fetchMemories(), fetchStatistics()])
    } catch (error) {
      console.error('Failed to create memory:', error)
    } finally {
      setIsSubmitting(false)
    }
  }

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2">
          <div 
            className="w-6 h-6 rounded-md flex items-center justify-center"
            style={{ background: `${currentTheme.colors.accent}20`, color: currentTheme.colors.accent }}
          >
            <Sparkles className="w-3.5 h-3.5" />
          </div>
          <h3 className={cn("text-sm font-semibold", currentTheme.textPrimary)}>快速创建记忆</h3>
        </div>
        
        {/* 分类快捷选择 */}
        <div className="flex gap-1">
          {categories.slice(0, 3).map(cat => (
            <button
              key={cat.value}
              type="button"
              onClick={() => setCategory(cat.value)}
              className={cn(
                "px-2 py-1 rounded-md text-xs font-medium transition-all",
                category === cat.value
                  ? `bg-gradient-to-r ${cat.color} text-white shadow-md`
                  : isDark
                    ? "bg-white/5 text-slate-400 hover:bg-white/10"
                    : "bg-slate-100 text-slate-500 hover:bg-slate-200"
              )}
            >
              {cat.label}
            </button>
          ))}
        </div>
      </div>
      
      <div className="relative">
        <textarea
          value={content}
          onChange={(e) => setContent(e.target.value)}
          placeholder="输入想要记住的内容..."
          className={cn(
            "w-full p-4 rounded-xl resize-none focus:outline-none focus:ring-2 text-sm transition-all",
            "placeholder:text-slate-400 dark:placeholder:text-slate-500"
          )}
          style={{
            background: isDark ? 'rgba(255,255,255,0.03)' : 'rgba(0,0,0,0.02)',
            border: `1px solid ${isDark ? 'rgba(255,255,255,0.08)' : 'rgba(0,0,0,0.08)'}`,
            color: isDark ? '#cbd5e1' : '#334155',
            '--tw-ring-color': currentTheme.colors.accent + '40'
          } as any}
          rows={4}
        />
        
        {/* 字符计数 */}
        <span className={cn(
          "absolute bottom-3 right-3 text-xs",
          currentTheme.textMuted
        )}>
          {content.length}/500
        </span>
      </div>

      <div className="flex items-center gap-4">
        <div className="flex items-center gap-3 flex-1">
          <div className={cn(
            "px-2 py-1 rounded-lg text-xs font-medium",
            isDark ? "bg-white/5" : "bg-slate-100"
          )}>
            <span className={cn("mr-1.5", currentTheme.textMuted)}>重要:</span>
          </div>
          <input
            type="range"
            min="0.1"
            max="1"
            step="0.1"
            value={importance}
            onChange={(e) => setImportance(parseFloat(e.target.value))}
            className="flex-1 h-2 rounded-full accent-indigo-500"
          />
          <div 
            className={cn(
              "px-2.5 py-1 rounded-lg text-xs font-bold min-w-[3rem] text-center",
              isDark ? "bg-white/10" : "bg-slate-100"
            )}
            style={{ color: currentTheme.colors.accent }}
          >
            {importance.toFixed(1)}
          </div>
        </div>
        
        <button
          type="submit"
          disabled={!content.trim() || isSubmitting}
          className={cn(
            "px-5 py-2.5 rounded-xl text-sm font-medium transition-all disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2 hover:scale-[1.02]",
            isDark
              ? "bg-gradient-to-r from-indigo-500 to-purple-500 hover:from-indigo-400 hover:to-purple-400 text-white shadow-lg shadow-indigo-500/30"
              : "bg-gradient-to-r from-indigo-500 to-purple-500 hover:from-indigo-600 hover:to-purple-600 text-white shadow-lg shadow-indigo-500/20"
          )}
        >
          {isSubmitting ? (
            <>
              <div className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin" />
              添加中...
            </>
          ) : (
            <>
              <Sparkles className="w-4 h-4" />
              添加记忆
            </>
          )}
        </button>
      </div>
    </form>
  )
}

export default function MemoryPage() {
  return (
    <Layout>
      <MemoryPageContent />
    </Layout>
  )
}
