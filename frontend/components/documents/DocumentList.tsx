'use client'

import React, { useCallback, useState } from 'react'
import { Upload, FileText, Trash2, X, Loader2, File, Sparkles, FolderOpen } from 'lucide-react'
import { useDocumentStore } from '@/stores'
import { cn, formatFileSize, formatDate } from '@/lib/utils'
import { useTheme } from '@/contexts/ThemeContext'

const FILE_TYPE_ICONS: Record<string, React.ReactNode> = {
  pdf: <FileText className="w-6 h-6 text-red-400" />,
  docx: <FileText className="w-6 h-6 text-blue-400" />,
  doc: <FileText className="w-6 h-6 text-blue-400" />,
  txt: <File className="w-6 h-6 text-slate-400" />,
  md: <FileText className="w-6 h-6 text-emerald-400" />,
  xlsx: <FileText className="w-6 h-6 text-green-400" />,
  xls: <FileText className="w-6 h-6 text-green-400" />,
  csv: <FileText className="w-6 h-6 text-green-400" />,
}

const accentGradients: Record<string, string> = {
  indigo: 'from-indigo-500 to-purple-600',
  purple: 'from-purple-500 to-pink-600',
  sky: 'from-sky-500 to-blue-600',
  emerald: 'from-emerald-500 to-teal-600',
  orange: 'from-orange-500 to-amber-600',
  violet: 'from-violet-500 to-purple-600',
  pink: 'from-pink-500 to-rose-600',
}

const accentGlow: Record<string, string> = {
  indigo: 'shadow-indigo-500/20',
  purple: 'shadow-purple-500/20',
  sky: 'shadow-sky-500/20',
  emerald: 'shadow-emerald-500/20',
  orange: 'shadow-orange-500/20',
  violet: 'shadow-violet-500/20',
  pink: 'shadow-pink-500/20',
}

export function DocumentList() {
  const { documents, uploadDocument, deleteDocument, isUploading, uploadProgress } = useDocumentStore()
  const { currentTheme, isDark } = useTheme()
  const [dragActive, setDragActive] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const accent = accentGradients[currentTheme.accentColor] || accentGradients.indigo
  const glow = accentGlow[currentTheme.accentColor] || accentGlow.indigo

  React.useEffect(() => {
    useDocumentStore.getState().fetchDocuments()
  }, [])

  const handleDrag = useCallback((e: React.DragEvent) => {
    e.preventDefault()
    e.stopPropagation()
    if (e.type === "dragenter" || e.type === "dragover") {
      setDragActive(true)
    } else if (e.type === "dragleave") {
      setDragActive(false)
    }
  }, [])

  const handleDrop = useCallback(async (e: React.DragEvent) => {
    e.preventDefault()
    e.stopPropagation()
    setDragActive(false)
    setError(null)

    const files = Array.from(e.dataTransfer.files)
    if (files.length === 0) return

    const file = files[0]
    const allowedTypes = ['pdf', 'docx', 'doc', 'txt', 'md', 'xlsx', 'xls', 'csv']
    const ext = file.name.split('.').pop()?.toLowerCase() || ''

    if (!allowedTypes.includes(ext)) {
      setError('不支持的文件格式，请上传 PDF、Word、Excel 或文本文件')
      return
    }

    try {
      await uploadDocument(file)
    } catch (err: any) {
      setError(err.message || '上传失败')
    }
  }, [uploadDocument])

  const handleFileInput = async (e: React.ChangeEvent<HTMLInputElement>) => {
    setError(null)
    const file = e.target.files?.[0]
    if (!file) return

    try {
      await uploadDocument(file)
    } catch (err: any) {
      setError(err.message || '上传失败')
    }
    
    e.target.value = ''
  }

  const handleDelete = async (id: string) => {
    if (confirm('确定要删除这个文档吗？')) {
      await deleteDocument(id)
    }
  }

  const getStatusBadge = (status: string) => {
    const statusMap = {
      pending: { 
        bg: isDark ? 'bg-slate-500/20' : 'bg-slate-200', 
        text: isDark ? 'text-slate-300' : 'text-slate-600', 
        label: '等待中', 
        dot: isDark ? 'bg-slate-400' : 'bg-slate-500' 
      },
      processing: { 
        bg: isDark ? 'bg-amber-500/20' : 'bg-amber-100', 
        text: isDark ? 'text-amber-300' : 'text-amber-600', 
        label: '处理中', 
        dot: isDark ? 'bg-amber-400 animate-pulse' : 'bg-amber-500 animate-pulse' 
      },
      completed: { 
        bg: isDark ? 'bg-emerald-500/20' : 'bg-emerald-100', 
        text: isDark ? 'text-emerald-300' : 'text-emerald-600', 
        label: '已完成', 
        dot: isDark ? 'bg-emerald-400' : 'bg-emerald-500' 
      },
      failed: { 
        bg: isDark ? 'bg-red-500/20' : 'bg-red-100', 
        text: isDark ? 'text-red-300' : 'text-red-600', 
        label: '失败', 
        dot: isDark ? 'bg-red-400' : 'bg-red-500' 
      }
    }
    const s = statusMap[status as keyof typeof statusMap] || statusMap.pending
    return (
      <span className={cn(
        "px-3 py-1 rounded-full text-xs font-medium border flex items-center gap-1.5", 
        s.bg, s.text,
        isDark ? "border-white/10" : "border-slate-200"
      )}>
        <span className={cn("w-1.5 h-1.5 rounded-full", s.dot)} />
        {s.label}
      </span>
    )
  }

  return (
    <div className="h-full flex flex-col p-6">
      {/* 页面标题区域 */}
      <div className="flex items-center justify-between mb-6">
        <div className="flex items-center gap-3">
          <h2 className={cn("text-lg font-semibold", currentTheme.textPrimary)}>知识库</h2>
          <div className={cn(
            "px-3 py-1 rounded-full border text-xs",
            isDark ? "bg-white/5 border-white/10" : "bg-white/80 border-slate-200"
          )}>
            <span className={cn("font-medium", currentTheme.textMuted)}>{documents.length}</span>
            <span className={cn("ml-1", currentTheme.textMuted)}>个文档</span>
          </div>
        </div>
        
        {/* 选择文件按钮 */}
        <input
          type="file"
          id="file-upload"
          className="hidden"
          onChange={handleFileInput}
          accept=".pdf,.docx,.doc,.txt,.md,.xlsx,.xls,.csv"
          disabled={isUploading}
        />
        <label 
          htmlFor="file-upload" 
          className={cn(
            "cursor-pointer flex items-center gap-2 px-4 py-2 rounded-xl text-sm font-medium transition-all duration-200",
            isDark 
              ? "bg-white/10 hover:bg-white/15 border border-white/10" 
              : "bg-white hover:bg-slate-50 shadow-sm border border-slate-200"
          )}
        >
          <Upload className={cn("w-4 h-4", currentTheme.textMuted)} />
          <span className={currentTheme.textSecondary}>选择文件</span>
        </label>
      </div>

      {/* 上传区域 - 拖拽专用 */}
      <div
        onDragEnter={handleDrag}
        onDragLeave={handleDrag}
        onDragOver={handleDrag}
        onDrop={handleDrop}
        className="relative border-2 border-dashed rounded-2xl p-8 text-center transition-all duration-300 overflow-hidden"
        style={{
          borderColor: dragActive ? currentTheme.colors.accent : (isDark ? 'rgba(255,255,255,0.15)' : '#e2e8f0'),
          background: dragActive ? `${currentTheme.colors.accent}10` : (isDark ? 'rgba(255,255,255,0.02)' : 'rgba(255,255,255,0.5)')
        }}
      >
        {/* 背景装饰 */}
        <div 
          className="absolute inset-0 pointer-events-none"
          style={{
            background: `linear-gradient(135deg, ${currentTheme.colors.accent}05 0%, transparent 50%)`
          }}
        />
        
        {isUploading ? (
          <div className="flex flex-col items-center">
            <div className={cn(
              "w-16 h-16 rounded-2xl bg-gradient-to-br flex items-center justify-center mb-4 shadow-lg animate-pulse",
              accent,
              glow
            )}>
              <Loader2 className="w-8 h-8 text-white animate-spin" />
            </div>
            <p className={cn("font-medium", currentTheme.textSecondary)}>上传中...</p>
            <p className={cn("text-lg font-bold mt-2", isDark ? `text-${currentTheme.accentColor}-400` : `text-${currentTheme.accentColor}-600`)}>{uploadProgress}%</p>
            <div className={cn(
              "w-64 h-2 rounded-full mt-4 overflow-hidden",
              isDark ? "bg-white/10" : "bg-slate-200"
            )}>
              <div
                className={cn("h-full rounded-full transition-all duration-300 bg-gradient-to-r", accent)}
                style={{ width: `${uploadProgress}%` }}
              />
            </div>
          </div>
        ) : (
          <div className="flex flex-col items-center">
            <div className={cn(
              "w-20 h-20 mx-auto rounded-2xl flex items-center justify-center mb-6 transition-all duration-300 shadow-lg",
              dragActive
                ? `bg-${currentTheme.accentColor}-500/20 scale-110`
                : isDark ? "bg-white/10" : "bg-slate-100/80 backdrop-blur-sm"
            )}>
              <Upload className={cn(
                "w-10 h-10 transition-colors",
                dragActive
                  ? isDark ? `text-${currentTheme.accentColor}-400` : `text-${currentTheme.accentColor}-600`
                  : currentTheme.textMuted
              )} />
            </div>
            <p className={cn("font-semibold text-base mb-2", currentTheme.textSecondary)}>
              {dragActive ? "释放文件上传" : "拖拽文件到此处上传"}
            </p>
            <p className={cn("text-sm", currentTheme.textMuted)}>支持 PDF、Word、Excel、文本文件</p>
          </div>
        )}
      </div>

      {error && (
        <div className={cn(
          "mt-4 p-4 rounded-xl text-sm flex items-center gap-3 animate-fade-in",
          isDark ? "bg-red-500/10 border border-red-500/30 text-red-300" : "bg-red-50 border border-red-200 text-red-600"
        )}>
          <div className={cn(
            "w-8 h-8 rounded-lg flex items-center justify-center",
            isDark ? "bg-red-500/20" : "bg-red-100"
          )}>
            <X className="w-4 h-4" />
          </div>
          {error}
        </div>
      )}

      {/* 文档列表 */}
      <div className="mt-6 flex-1 overflow-y-auto scrollbar-thin">
        {documents.length > 0 && (
          <h3 className={cn("text-base font-semibold flex items-center gap-2 mb-4", currentTheme.textSecondary)}>
            <FileText className={cn("w-4 h-4", isDark ? `text-${currentTheme.accentColor}-400` : `text-${currentTheme.accentColor}-500`)} />
            已上传文档
          </h3>
        )}
        
        {documents.length === 0 ? (
          <div className="text-center py-12 animate-fade-in">
            <div className={cn(
              "w-16 h-16 mx-auto rounded-2xl flex items-center justify-center mb-4 shadow-inner",
              isDark ? "bg-white/5" : "bg-slate-100"
            )}>
              <FileText className={cn("w-8 h-8", isDark ? "text-slate-600" : "text-slate-400")} />
            </div>
            <p className={cn("font-medium text-sm", isDark ? "text-slate-500" : "text-slate-500")}>暂无已上传的文档</p>
            <p className={cn("text-xs mt-1", isDark ? "text-slate-600" : "text-slate-400")}>上传文档后即可开始智能问答</p>
          </div>
        ) : (
          <div className="space-y-3">
            {documents.map((doc, index) => (
              <div
                key={doc.id}
                style={{ animationDelay: `${index * 50}ms` }}
                className={cn(
                  "flex items-center gap-4 p-4 rounded-2xl transition-all duration-300 group animate-fade-in border",
                  isDark 
                    ? "bg-white/[0.03] hover:bg-white/[0.06] border-white/[0.06]" 
                    : "bg-white/70 hover:bg-white/90 shadow-sm border-slate-200/80"
                )}
              >
                <div className={cn(
                  "w-12 h-12 rounded-xl flex items-center justify-center transition-colors flex-shrink-0",
                  isDark ? "bg-white/[0.06] group-hover:bg-white/[0.1]" : "bg-slate-100 group-hover:bg-slate-200"
                )}>
                  {FILE_TYPE_ICONS[doc.file_type] || <File className="w-5 h-5 text-slate-400" />}
                </div>
                <div className="flex-1 min-w-0">
                  <p className={cn(
                    "font-semibold text-sm truncate transition-colors",
                    currentTheme.textPrimary,
                    isDark ? "group-hover:text-indigo-300" : "group-hover:text-indigo-600"
                  )}>{doc.filename}</p>
                  <div className={cn("flex items-center gap-3 mt-1.5 text-xs", currentTheme.textMuted)}>
                    <span>{formatFileSize(doc.file_size)}</span>
                    <span>·</span>
                    <span>{formatDate(doc.created_at)}</span>
                    <span className="ml-1">{getStatusBadge(doc.status)}</span>
                  </div>
                </div>
                <button
                  onClick={() => handleDelete(doc.id)}
                  className={cn(
                    "p-2.5 rounded-xl transition-all opacity-0 group-hover:opacity-100 flex-shrink-0",
                    isDark ? "hover:bg-red-500/20" : "hover:bg-red-50"
                  )}
                  title="删除"
                >
                  <Trash2 className={cn(
                    "w-4 h-4 transition-colors",
                    isDark ? "text-slate-500 hover:text-red-400" : "text-slate-400 hover:text-red-500"
                  )} />
                </button>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  )
}
