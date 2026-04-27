'use client'

import React from 'react'
import { FileText } from 'lucide-react'
import { cn } from '@/lib/utils'
import { useTheme } from '@/contexts/ThemeContext'

interface Citation {
  chunk_id: string
  document_id?: string
  document_title?: string
  similarity?: number
  content_preview?: string
}

interface SourcesPanelProps {
  citations: Citation[]
  className?: string
  isNoInfo?: boolean
}

export function SourcesPanel({ citations, className, isNoInfo }: SourcesPanelProps) {
  const { isDark, currentTheme } = useTheme()

  // 如果是"未找到相关信息"消息，不显示来源面板
  if (isNoInfo) return null

  // 【修复】如果 citations 不存在、为 null 或为空数组，不显示
  if (!citations || citations === null || citations.length === 0) {
    return null
  }

  const filteredCitations = citations.filter(c => c.similarity !== undefined && c.similarity > 0)

  if (filteredCitations.length === 0) {
    return null
  }

  const uniqueDocs = filteredCitations.reduce((acc, curr) => {
    const docId = curr.document_id || curr.chunk_id
    if (!acc.find(c => (c.document_id || c.chunk_id) === docId)) {
      acc.push(curr)
    }
    return acc
  }, [] as Citation[])

  return (
    <div className={cn("mt-3 pt-3 border-t", isDark ? "border-white/10" : "border-gray-100", className)}>
      <div className="flex items-center gap-2 mb-2">
        <FileText className={cn("w-3.5 h-3.5", isDark ? "text-slate-400" : "text-gray-400")} />
        <p className={cn("text-xs font-medium", isDark ? "text-slate-400" : "text-gray-500")}>参考来源</p>
      </div>
      <div className="space-y-1.5">
        {uniqueDocs.map((citation, i) => (
          <div
            key={i}
            className={cn(
              "flex items-center justify-between rounded-lg px-3 py-2 text-sm",
              isDark ? "bg-white/5" : "bg-gray-50"
            )}
          >
            <div className="flex items-center gap-2 min-w-0 flex-1">
              <span className="w-5 h-5 rounded text-xs font-medium flex items-center justify-center flex-shrink-0"
                style={{
                  background: `${currentTheme.colors.accent}30`,
                  color: currentTheme.colors.accent
                }}
              >
                {i + 1}
              </span>
              <span className={cn(
                "truncate",
                isDark ? "text-slate-300" : "text-gray-700"
              )}>
                {citation.document_title || '未知文档'}
              </span>
            </div>
            <span className={cn(
              "text-xs ml-2 flex-shrink-0",
              isDark ? "text-slate-500" : "text-gray-400"
            )}>
              {citation.similarity !== undefined
                ? `${(citation.similarity * 100).toFixed(0)}%`
                : ''}
            </span>
          </div>
        ))}
      </div>
    </div>
  )
}
