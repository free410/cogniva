'use client'

import React, { useState, useEffect, useRef } from 'react'
import { FileText, X, Check, Search, Database, Sparkles, BookOpen, Layers, ChevronRight } from 'lucide-react'
import { useDocumentStore } from '@/stores'
import { cn } from '@/lib/utils'
import { useTheme } from '@/contexts/ThemeContext'
import { getAccentGradient, getAccentRgba } from '@/contexts/themeUtils'

interface DocumentSelectorProps {
  selectedIds: string[]
  onSelectionChange: (ids: string[]) => void
}

export function DocumentSelector({ selectedIds, onSelectionChange }: DocumentSelectorProps) {
  const { documents } = useDocumentStore()
  const { currentTheme, isDark } = useTheme()
  const [isOpen, setIsOpen] = useState(false)
  const [searchQuery, setSearchQuery] = useState('')
  const panelRef = useRef<HTMLDivElement>(null)

  const accentGradient = getAccentGradient(currentTheme.accentColor)

  useEffect(() => {
    useDocumentStore.getState().fetchDocuments()
  }, [])

  // 点击外部关闭
  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (panelRef.current && !panelRef.current.contains(event.target as Node)) {
        setIsOpen(false)
      }
    }
    if (isOpen) {
      document.addEventListener('mousedown', handleClickOutside)
      return () => document.removeEventListener('mousedown', handleClickOutside)
    }
  }, [isOpen])

  // 过滤文档
  const filteredDocs = documents.filter(doc => 
    doc.filename.toLowerCase().includes(searchQuery.toLowerCase())
  )

  // 已完成的文档
  const completedDocs = filteredDocs.filter(doc => doc.status === 'completed')

  const toggleDocument = (docId: string) => {
    if (selectedIds.includes(docId)) {
      onSelectionChange(selectedIds.filter(id => id !== docId))
    } else {
      onSelectionChange([...selectedIds, docId])
    }
  }

  const selectAll = () => {
    onSelectionChange(completedDocs.map(d => d.id))
  }

  const clearAll = () => {
    onSelectionChange([])
  }

  const selectedCount = selectedIds.length
  const totalCount = completedDocs.length

  // 获取选中文档的名称（显示前两个）
  const selectedDocs = documents.filter(d => selectedIds.includes(d.id))
  const displayNames = selectedDocs.slice(0, 2).map(d => d.filename.replace(/\.[^/.]+$/, ''))
  const moreCount = selectedDocs.length - 2

  return (
    <div className="relative" ref={panelRef}>
      {/* 触发按钮 - 与其他控件统一高度 */}
      <button
        onClick={() => setIsOpen(!isOpen)}
        className={cn(
          "flex items-center gap-2 px-3 py-2 rounded-lg border transition-all duration-200 h-10"
        )}
        style={{
          background: selectedCount > 0 ? currentTheme.colors.accentBg : currentTheme.colors.cardBg,
          borderColor: selectedCount > 0 ? currentTheme.colors.accent : currentTheme.colors.border,
          color: selectedCount > 0 ? currentTheme.colors.accentText : currentTheme.colors.textSecondary
        }}
      >
        <Database className={cn("w-4 h-4")} style={{ color: selectedCount > 0 ? currentTheme.colors.accent : currentTheme.colors.textMuted }} />
        <span className="text-sm font-medium">
          {selectedCount > 0 
            ? `${selectedCount} 个文档` 
            : '选择文档'
          }
        </span>
        <ChevronRight className={cn(
          "w-4 h-4 transition-transform duration-200",
          isOpen ? "rotate-90" : "",
        )}
        style={{ color: currentTheme.colors.textMuted }}
        />
      </button>

      {/* 展开面板 - 更大更美观 */}
      {isOpen && (
        <div 
          className={cn(
            "absolute top-full left-0 mt-3 w-[480px] rounded-2xl border-2 shadow-2xl z-50 overflow-hidden animate-scale-in",
            isDark 
              ? "bg-slate-900/98 border-white/20" 
              : "bg-white/98 border-slate-200 shadow-xl"
          )}
        >
          {/* 顶部标题栏 */}
          <div 
            className="px-5 py-4 border-b"
            style={{ 
              background: `linear-gradient(135deg, ${getAccentRgba(currentTheme.accentColor, 0.1)} 0%, transparent 100%)`,
              borderColor: isDark ? 'rgba(255,255,255,0.1)' : 'rgba(0,0,0,0.05)'
            }}
          >
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-3">
                <div className={cn(
                  "w-12 h-12 rounded-xl flex items-center justify-center",
                  `bg-gradient-to-br ${accentGradient}`
                )}>
                  <BookOpen className="w-6 h-6 text-white" />
                </div>
                <div>
                  <h3 className={cn("text-lg font-bold", currentTheme.textPrimary)}>知识文档选择</h3>
                  <p className={cn("text-sm", currentTheme.textMuted)}>选择要检索的文档来源</p>
                </div>
              </div>
              <button
                onClick={() => setIsOpen(false)}
                className={cn(
                  "w-8 h-8 rounded-lg flex items-center justify-center transition-colors",
                  isDark 
                    ? "bg-white/10 hover:bg-white/20 text-slate-400" 
                    : "bg-slate-100 hover:bg-slate-200 text-slate-500"
                )}
              >
                <X className="w-4 h-4" />
              </button>
            </div>
          </div>

          {/* 搜索框 */}
          <div className="px-5 py-3">
            <div             className={cn(
              "flex items-center gap-3 px-4 py-3 rounded-xl border-2 transition-all"
            )}
            style={{
              background: isDark ? 'rgba(255,255,255,0.05)' : 'rgba(0,0,0,0.02)',
              borderColor: currentTheme.colors.border
            }}
          >
              <Search className={cn("w-5 h-5", isDark ? "text-slate-500" : "text-slate-400")} />
              <input
                type="text"
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                placeholder="搜索文档名称..."
                className={cn(
                  "flex-1 bg-transparent outline-none text-sm",
                  isDark ? "text-white placeholder-slate-500" : "text-slate-700 placeholder-slate-400"
                )}
              />
            </div>
          </div>

          {/* 快捷操作栏 */}
          <div className="px-5 py-2 flex items-center justify-between">
            <div className="flex items-center gap-2">
              <span className={cn(
                "px-3 py-1 rounded-full text-xs font-medium",
                isDark ? "bg-white/10 text-slate-300" : "bg-slate-100 text-slate-600"
              )}>
                {completedDocs.length} 个可用文档
              </span>
              {selectedCount > 0 && (
                <span                   className={cn(
                  "px-3 py-1 rounded-full text-xs font-medium flex items-center gap-1"
                )}
                style={{
                  background: currentTheme.colors.accentBg,
                  color: currentTheme.colors.accentText
                }}
                >
                  <Check className="w-3 h-3" />
                  已选 {selectedCount} 个
                </span>
              )}
            </div>
            <div className="flex items-center gap-3">
              <button
                onClick={selectAll}
                className="text-xs transition-colors font-medium"
                style={{ color: currentTheme.colors.accentText }}
              >
                全选
              </button>
              <span className={cn("text-slate-500", isDark ? "" : "")}>|</span>
              <button
                onClick={clearAll}
                className="text-xs text-slate-400 hover:text-slate-300 transition-colors"
              >
                清空
              </button>
            </div>
          </div>

          {/* 文档列表 */}
          <div className="max-h-80 overflow-y-auto px-3 pb-3">
            {completedDocs.length === 0 ? (
              <div className="py-12 text-center">
                <div className={cn(
                  "w-16 h-16 mx-auto mb-4 rounded-2xl flex items-center justify-center",
                  isDark ? "bg-white/5" : "bg-slate-100"
                )}>
                  <FileText className={cn("w-8 h-8", isDark ? "text-slate-600" : "text-slate-400")} />
                </div>
                <p className={cn("font-medium", currentTheme.textMuted)}>暂无已完成的文档</p>
                <p className={cn("text-sm mt-1", isDark ? "text-slate-500" : "text-slate-400")}>请先上传并处理文档</p>
              </div>
            ) : (
              <div className="space-y-2">
                {completedDocs.map(doc => {
                  const isSelected = selectedIds.includes(doc.id)
                  return (
                    <button
                      key={doc.id}
                      onClick={() => toggleDocument(doc.id)}
                      className={cn(
                        "w-full flex items-center gap-4 px-4 py-3.5 rounded-xl transition-all duration-200 text-left group"
                      )}
                      style={{
                        background: isSelected ? currentTheme.colors.accentBg : (isDark ? 'rgba(255,255,255,0.05)' : 'rgba(0,0,0,0.02)'),
                        border: `2px solid ${isSelected ? currentTheme.colors.accent : 'transparent'}`
                      }}
                    >
                      {/* 选择指示器 */}
                      <div className={cn(
                        "w-10 h-10 rounded-xl flex items-center justify-center flex-shrink-0 transition-all duration-200",
                        isSelected
                          ? `bg-gradient-to-br ${accentGradient} shadow-lg`
                          : isDark
                            ? "bg-white/10 group-hover:bg-white/15"
                            : "bg-white group-hover:bg-slate-200"
                      )}>
                        {isSelected ? (
                          <Check className="w-5 h-5 text-white" />
                        ) : (
                          <FileText className={cn(
                            "w-5 h-5",
                            isDark ? "text-slate-500" : "text-slate-400"
                          )} />
                        )}
                      </div>
                      
                      {/* 文件信息 */}
                      <div className="flex-1 min-w-0">
                        <p className={cn(
                          "text-sm font-semibold truncate",
                          isSelected 
                            ? currentTheme.textPrimary
                            : currentTheme.textSecondary
                        )}>
                          {doc.filename}
                        </p>
                        <div className="flex items-center gap-3 mt-1">
                          <span className={cn(
                            "px-2 py-0.5 rounded text-xs font-medium",
                            isDark 
                              ? "bg-white/10 text-slate-400" 
                              : "bg-slate-200 text-slate-600"
                          )}>
                            {doc.file_type?.toUpperCase()}
                          </span>
                          <span className={cn("text-xs", currentTheme.textMuted)}>
                            {formatFileSize(doc.file_size)}
                          </span>
                          <span className={cn(
                            "flex items-center gap-1 text-xs",
                            isDark ? "text-emerald-400" : "text-emerald-600"
                          )}>
                            <span className="w-1.5 h-1.5 rounded-full bg-emerald-400" />
                            已就绪
                          </span>
                        </div>
                      </div>

                      {/* 右侧图标 */}
                      {isSelected && (
                        <div className="flex-shrink-0">
                          <Sparkles className={cn(
                            "w-5 h-5 animate-pulse"
                          )}
                          style={{ color: currentTheme.colors.accent }}
                          />
                        </div>
                      )}
                    </button>
                  )
                })}
              </div>
            )}
          </div>

          {/* 底部提示栏 */}
          <div 
            className="px-5 py-3 border-t"
            style={{ 
              background: isDark ? 'rgba(255,255,255,0.02)' : 'rgba(0,0,0,0.02)',
              borderColor: isDark ? 'rgba(255,255,255,0.05)' : 'rgba(0,0,0,0.05)'
            }}
          >
            <p className={cn("text-xs flex items-center gap-2", currentTheme.textMuted)}>
              <Sparkles className="w-3.5 h-3.5 text-amber-500" />
              {selectedCount > 0 
                ? `已选择 ${selectedCount} 个文档，系统将只从这些文档中检索答案`
                : "未选择文档时，系统将从所有可用文档中检索答案"
              }
            </p>
          </div>
        </div>
      )}
    </div>
  )
}

// 辅助函数
function formatFileSize(bytes: number): string {
  if (bytes < 1024) return bytes + ' B'
  if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + ' KB'
  return (bytes / (1024 * 1024)).toFixed(1) + ' MB'
}
