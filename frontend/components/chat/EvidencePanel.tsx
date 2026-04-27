'use client'

import React, { useState } from 'react'
import { ChevronDown, ChevronUp, Shield, Database, TrendingUp, Layers, Zap, Brain, Target, AlertCircle } from 'lucide-react'
import { cn } from '@/lib/utils'
import { useTheme } from '@/contexts/ThemeContext'

interface ChunkInfo {
  id: string
  source?: string
  content_preview?: string
  full_content?: string
  score?: number
  rank?: number
  method?: string
  bm25_score?: number | null
  reranker_score?: number | null
  keyword_score?: number | null
  term_match_ratio?: number | null
  phrase_score?: number | null
  matched_terms?: string[]
}

interface EvidenceReport {
  confidence: number
  chunks_strategy?: string
  retrieval_method?: string
  rerank_model?: string
  rerank_before_score?: number | null
  rerank_after_score?: number | null
  top_similarity?: number
  avg_similarity?: number
  chunks?: ChunkInfo[]
  intent_match_ratio?: number | null
  topic_match?: boolean | null
  entity_match_score?: number | null
  term_match_score?: number | null
  matched_entities?: string[]
}

interface EvidencePanelProps {
  evidence: EvidenceReport | null | undefined
  isNoInfo?: boolean
}

function getConfidenceColor(conf: number, isDark: boolean) {
  if (conf >= 0.8) return { 
    bg: 'bg-gradient-to-br from-emerald-500 to-teal-600', 
    light: isDark ? 'bg-emerald-500/20' : 'bg-emerald-50',
    lightBorder: isDark ? 'border-emerald-500/30' : 'border-emerald-200',
    text: isDark ? 'text-emerald-300' : 'text-emerald-600',
    badge: 'bg-emerald-500',
    badgeLight: isDark ? 'bg-emerald-500/20 text-emerald-300' : 'bg-emerald-100 text-emerald-700',
  }
  if (conf >= 0.6) return { 
    bg: 'bg-gradient-to-br from-blue-500 to-indigo-600', 
    light: isDark ? 'bg-blue-500/20' : 'bg-blue-50',
    lightBorder: isDark ? 'border-blue-500/30' : 'border-blue-200',
    text: isDark ? 'text-blue-300' : 'text-blue-600',
    badge: 'bg-blue-500',
    badgeLight: isDark ? 'bg-blue-500/20 text-blue-300' : 'bg-blue-100 text-blue-700',
  }
  if (conf >= 0.4) return { 
    bg: 'bg-gradient-to-br from-amber-500 to-orange-600', 
    light: isDark ? 'bg-amber-500/20' : 'bg-amber-50',
    lightBorder: isDark ? 'border-amber-500/30' : 'border-amber-200',
    text: isDark ? 'text-amber-300' : 'text-amber-600',
    badge: 'bg-amber-500',
    badgeLight: isDark ? 'bg-amber-500/20 text-amber-300' : 'bg-amber-100 text-amber-700',
  }
  return { 
    bg: 'bg-gradient-to-br from-red-500 to-rose-600', 
    light: isDark ? 'bg-red-500/20' : 'bg-red-50',
    lightBorder: isDark ? 'border-red-500/30' : 'border-red-200',
    text: isDark ? 'text-red-300' : 'text-red-600',
    badge: 'bg-red-500',
    badgeLight: isDark ? 'bg-red-500/20 text-red-300' : 'bg-red-100 text-red-700',
  }
}

function getConfidenceLabel(conf: number) {
  if (conf >= 0.8) return '极高'
  if (conf >= 0.6) return '高'
  if (conf >= 0.4) return '中'
  if (conf >= 0.2) return '低'
  return '极低'
}

function getScoreColor(score: number, isDark: boolean) {
  if (score >= 0.7) return { 
    bg: isDark ? 'bg-emerald-500/20' : 'bg-emerald-50', 
    border: isDark ? 'border-emerald-500/30' : 'border-emerald-300', 
    text: isDark ? 'text-emerald-300' : 'text-emerald-700', 
    badge: isDark ? 'bg-emerald-500/30 text-emerald-300' : 'bg-emerald-100 text-emerald-700', 
    dot: 'bg-emerald-500' 
  }
  if (score >= 0.5) return { 
    bg: isDark ? 'bg-blue-500/20' : 'bg-blue-50', 
    border: isDark ? 'border-blue-500/30' : 'border-blue-300', 
    text: isDark ? 'text-blue-300' : 'text-blue-700', 
    badge: isDark ? 'bg-blue-500/30 text-blue-300' : 'bg-blue-100 text-blue-700', 
    dot: 'bg-blue-500' 
  }
  if (score >= 0.3) return { 
    bg: isDark ? 'bg-amber-500/20' : 'bg-amber-50', 
    border: isDark ? 'border-amber-500/30' : 'border-amber-300', 
    text: isDark ? 'text-amber-300' : 'text-amber-700', 
    badge: isDark ? 'bg-amber-500/30 text-amber-300' : 'bg-amber-100 text-amber-700', 
    dot: 'bg-amber-500' 
  }
  return { 
    bg: isDark ? 'bg-slate-500/20' : 'bg-gray-50', 
    border: isDark ? 'border-slate-500/30' : 'border-gray-300', 
    text: isDark ? 'text-slate-300' : 'text-gray-700', 
    badge: isDark ? 'bg-slate-500/30 text-slate-300' : 'bg-gray-100 text-gray-700', 
    dot: isDark ? 'bg-slate-400' : 'bg-gray-400' 
  }
}

function ChunkCard({ chunk, index, isDark }: { chunk: ChunkInfo; index: number; isDark: boolean }) {
  const [isExpanded, setIsExpanded] = useState(false)
  const score = chunk.score ?? 0
  const colors = getScoreColor(score, isDark)
  const isHighScore = score >= 0.3
  const hasDetailedScores = chunk.reranker_score != null || chunk.bm25_score != null || chunk.keyword_score != null
  const previewContent = chunk.content_preview || ''
  const fullContent = chunk.full_content || previewContent
  const isLongContent = fullContent.length > 500
  const displayContent = (isExpanded || !isLongContent) ? fullContent : previewContent
  
  const textColor = isDark ? "text-slate-300" : "text-gray-600"

  return (
    <div className={cn("border rounded-xl overflow-hidden transition-all duration-300", 
      isHighScore ? "hover:shadow-lg" : "opacity-75",
      colors.border
    )}>
      <div 
        className={cn("px-4 py-3 flex items-center justify-between cursor-pointer transition-colors", colors.bg)}
        onClick={() => setIsExpanded(!isExpanded)}
      >
        <div className="flex items-center gap-3 flex-1 min-w-0">
          <div className={cn("w-6 h-6 rounded-full flex items-center justify-center text-xs font-bold text-white", colors.badge)}>
            {index + 1}
          </div>
          <span className={cn("px-2 py-1 rounded-md text-xs font-semibold", colors.badge)}>
            {score.toFixed(3)}
          </span>
          <span className={cn("text-sm truncate font-medium", colors.text)}>
            {chunk.source || 'Unknown'}
          </span>
          {!isHighScore && (
            <span className={cn("flex items-center gap-1 text-xs", isDark ? "text-slate-500" : "text-gray-400")}>
              <AlertCircle className="w-3 h-3" />
              低相关
            </span>
          )}
        </div>
        {isExpanded ? (
          <ChevronUp className={cn("w-5 h-5 flex-shrink-0", isDark ? "text-slate-400" : "text-gray-400")} />
        ) : (
          <ChevronDown className={cn("w-5 h-5 flex-shrink-0", isDark ? "text-slate-400" : "text-gray-400")} />
        )}
      </div>
      
      {isExpanded && (
        <div className={cn("px-4 py-3 space-y-3", isDark ? "bg-slate-800/50" : "bg-white")}>
          <div className="relative">
            <p className={cn("text-sm leading-relaxed whitespace-pre-wrap break-words", textColor)}>
              {displayContent}
              {isLongContent && !isExpanded && '...'}
            </p>
            {isLongContent && (
              <button
                onClick={(e) => {
                  e.stopPropagation()
                  setIsExpanded(!isExpanded)
                }}
                className="mt-2 text-xs text-blue-500 hover:text-blue-600 font-medium"
              >
                {isExpanded ? '[收起]' : `[展开全部 (${fullContent.length}字)]`}
              </button>
            )}
          </div>
          
          {hasDetailedScores && (
            <div className="flex flex-wrap items-center gap-2">
              {chunk.reranker_score != null && (
                <span className={cn("px-2 py-1 rounded text-xs font-medium", isDark ? "bg-purple-500/20 text-purple-300" : "bg-purple-50 text-purple-600")}>
                  Reranker: {chunk.reranker_score.toFixed(4)}
                </span>
              )}
              {chunk.bm25_score != null && (
                <span className={cn("px-2 py-1 rounded text-xs font-medium", isDark ? "bg-blue-500/20 text-blue-300" : "bg-blue-50 text-blue-600")}>
                  BM25: {chunk.bm25_score.toFixed(4)}
                </span>
              )}
              {chunk.keyword_score != null && (
                <span className={cn("px-2 py-1 rounded text-xs font-medium", isDark ? "bg-green-500/20 text-green-300" : "bg-green-50 text-green-600")}>
                  Keyword: {chunk.keyword_score.toFixed(4)}
                </span>
              )}
            </div>
          )}
          
          {chunk.matched_terms && chunk.matched_terms.length > 0 && (
            <div className="flex flex-wrap items-center gap-1">
              <span className={cn("text-xs", isDark ? "text-slate-500" : "text-gray-500")}>匹配词:</span>
              {chunk.matched_terms.slice(0, 5).map((term, i) => (
                <span key={i} className={cn("px-2 py-0.5 rounded text-xs", isDark ? "bg-yellow-500/20 text-yellow-300" : "bg-yellow-50 text-yellow-700")}>
                  {term}
                </span>
              ))}
              {chunk.matched_terms.length > 5 && (
                <span className={cn("text-xs", isDark ? "text-slate-500" : "text-gray-400")}>+{chunk.matched_terms.length - 5}</span>
              )}
            </div>
          )}
        </div>
      )}
    </div>
  )
}

export function EvidencePanel({ evidence, isNoInfo }: EvidencePanelProps) {
  const [isExpanded, setIsExpanded] = useState(false)
  const { isDark } = useTheme()

  // 如果是"未找到相关信息"消息，不显示置信度面板
  if (isNoInfo) return null

  // 如果 evidence 不存在、为 null，完全不显示
  if (!evidence || evidence === null) return null

  const confidenceValue = evidence.confidence ?? 0
  const chunks = evidence.chunks || []
  const avgSim = evidence.avg_similarity ?? 0
  const topSim = evidence.top_similarity ?? 0

  // 当置信度很低（< 0.05）且没有 chunks 时，不显示可信度分析面板
  // 即使有 chunks 但置信度很低也不显示，避免显示误导性信息
  if (confidenceValue < 0.05 && chunks.length === 0) {
    return null
  }
  
  const rerankBefore = evidence.rerank_before_score
  const rerankAfter = evidence.rerank_after_score
  const hasRerankData = rerankBefore !== null || rerankAfter !== null
  const hasIntentData = evidence.intent_match_ratio !== null || evidence.topic_match !== null || evidence.entity_match_score !== null
  const highScoreChunks = chunks.filter(c => (c.score ?? 0) >= 0.3)
  const lowScoreChunks = chunks.filter(c => (c.score ?? 0) < 0.3)
  
  const colors = getConfidenceColor(confidenceValue, isDark)
  const confidenceLabel = getConfidenceLabel(confidenceValue)
  const progress = Math.min(confidenceValue * 100, 100)
  const circumference = 2 * Math.PI * 36
  const strokeDashoffset = circumference - (progress / 100) * circumference

  const headerBg = isDark ? "bg-slate-800/50" : "bg-gradient-to-r from-slate-50 via-white to-slate-50"
  const headerHoverBg = isDark ? "hover:from-slate-700/50 hover:to-slate-700/50" : "hover:from-slate-100 hover:to-slate-100"
  const cardBg = isDark ? "bg-slate-800/50" : "bg-white"
  const borderColor = isDark ? "border-white/10" : "border-gray-200"
  const textMuted = isDark ? "text-slate-400" : "text-gray-500"
  const textPrimary = isDark ? "text-white" : "text-gray-800"

  return (
    <div className={cn("mt-4 rounded-2xl border overflow-hidden shadow-lg", borderColor, isDark ? "bg-slate-800/80" : "bg-gradient-to-b from-white to-gray-50")}>
      <button
        onClick={() => setIsExpanded(!isExpanded)}
        className={cn("w-full px-5 py-4 flex items-center justify-between transition-all duration-300", headerBg, headerHoverBg)}
      >
        <div className="flex items-center gap-4">
          <div className="relative w-16 h-16">
            <svg className="w-16 h-16 transform -rotate-90" viewBox="0 0 72 72">
              <circle cx="36" cy="36" r="32" stroke={isDark ? "#334155" : "#e5e7eb"} strokeWidth="6" fill="none" />
              <circle
                cx="36" cy="36" r="32"
                stroke="url(#confidenceGradient)"
                strokeWidth="6"
                fill="none"
                strokeLinecap="round"
                strokeDasharray={circumference}
                strokeDashoffset={strokeDashoffset}
                className="transition-all duration-1000 ease-out"
              />
              <defs>
                <linearGradient id="confidenceGradient" x1="0%" y1="0%" x2="100%" y2="0%">
                  <stop offset="0%" stopColor={colors.badge} />
                  <stop offset="100%" stopColor={confidenceValue >= 0.6 ? '#4f46e5' : '#f59e0b'} />
                </linearGradient>
              </defs>
            </svg>
            <div className="absolute inset-0 flex items-center justify-center">
              <span className={cn("text-sm font-bold", textPrimary)}>{Math.round(confidenceValue * 100)}%</span>
            </div>
          </div>

          <div className="text-left">
            <div className="flex items-center gap-2">
              <Shield className={cn("w-5 h-5", textMuted)} />
              <p className={cn("text-base font-semibold", textPrimary)}>答案可信度分析</p>
            </div>
            <div className="flex items-center gap-2 mt-1">
              <span className={cn("px-2 py-0.5 rounded-full text-xs font-medium text-white", colors.badge)}>
                {confidenceLabel}
              </span>
              {chunks.length > 0 ? (
                <span className={cn("text-xs px-2 py-0.5 rounded", isDark ? "text-emerald-400 bg-emerald-500/20" : "text-green-600 bg-green-50")}>
                  已检索到 {chunks.length} 条相关
                </span>
              ) : (
                <span className={cn("text-xs px-2 py-0.5 rounded", isDark ? "text-red-400 bg-red-500/20" : "text-red-500 bg-red-50")}>
                  未检索到相关
                </span>
              )}
            </div>
          </div>
        </div>

        <div className="flex items-center gap-6">
          <div className="flex items-center gap-4">
            <div className="text-right">
              <p className={cn("text-xs uppercase tracking-wide", textMuted)}>Top</p>
              <p className={cn("text-lg font-bold", colors.text)}>{topSim.toFixed(4)}</p>
            </div>
            <div className={cn("w-px h-8", isDark ? "bg-slate-600" : "bg-slate-200")} />
            <div className="text-right">
              <p className={cn("text-xs uppercase tracking-wide", textMuted)}>Avg</p>
              <p className={cn("text-lg font-bold", isDark ? "text-slate-300" : "text-slate-600")}>{avgSim.toFixed(4)}</p>
            </div>
          </div>
          
          {isExpanded ? (
            <ChevronUp className={cn("w-6 h-6", textMuted)} />
          ) : (
            <ChevronDown className={cn("w-6 h-6", textMuted)} />
          )}
        </div>
      </button>

      {isExpanded && (
        <div className={cn("px-5 py-4 space-y-4 border-t", isDark ? "bg-slate-800/50 border-slate-700" : "bg-gradient-to-b from-slate-50 to-white border-slate-100")}>
          {chunks.length > 0 && (
            <div>
              <p className={cn("text-sm font-semibold mb-3 flex items-center gap-2", textPrimary)}>
                <Target className="w-4 h-4" />
                命中块详情 ({chunks.length})
                {highScoreChunks.length > 0 && (
                  <span className={cn("text-xs ml-2", isDark ? "text-emerald-400" : "text-emerald-600")}>
                    ✓ {highScoreChunks.length} 高相关
                  </span>
                )}
                {lowScoreChunks.length > 0 && (
                  <span className={cn("text-xs ml-2", isDark ? "text-amber-400" : "text-amber-600")}>
                    ⚠ {lowScoreChunks.length} 低相关
                  </span>
                )}
              </p>
              <div className="space-y-2 max-h-80 overflow-y-auto pr-1 scrollbar-thin">
                {chunks.map((chunk, index) => (
                  <ChunkCard key={chunk.id || index} chunk={chunk} index={index} isDark={isDark} />
                ))}
              </div>
            </div>
          )}
          
          {chunks.length === 0 && (
            <div className={cn("text-center py-4", textMuted)}>
              <Database className={cn("w-8 h-8 mx-auto mb-2", isDark ? "text-slate-600" : "text-slate-300")} />
              <p className="text-sm">未检索到相关文档</p>
            </div>
          )}
        </div>
      )}
    </div>
  )
}
