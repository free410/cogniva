'use client'

import React, { useState, useRef, useEffect, useCallback } from 'react'
import { Send, Bot, User, Loader2, Copy, CheckCheck, BookmarkPlus, Sparkles, Settings2, ChevronDown, ChevronUp, Trash2 } from 'lucide-react'
import { useChatStore } from '@/stores'
import { MessageContent, SourcesPanel, EvidencePanel } from '@/components/chat'
import { DocumentSelector } from './DocumentSelector'
import { useTheme } from '@/contexts/ThemeContext'
import { API_BASE_URL } from '@/lib/api'

export function Chat() {
  const {
    messages,
    isSending,
    streamingContent,
    sendMessage,
    sendStreamMessage,
    saveMessageAsMemory,
    clearCurrentConversation,
    createConversation
  } = useChatStore()
  const { currentTheme } = useTheme()
  const [input, setInput] = useState('')
  const [copiedId, setCopiedId] = useState<string | null>(null)
  const [provider, setProvider] = useState('deepseek')
  const [useRag, setUseRag] = useState(true)
  const [useStream, setUseStream] = useState(true)
  const [savedMessageIds, setSavedMessageIds] = useState<string[]>([])
  const [useMemory, setUseMemory] = useState(true)
  const [showSettings, setShowSettings] = useState(false)
  const [selectedDocumentIds, setSelectedDocumentIds] = useState<string[]>([])
  const [isRestoring, setIsRestoring] = useState(true)
  const messagesEndRef = useRef<HTMLDivElement>(null)
  const inputRef = useRef<HTMLTextAreaElement>(null)

  const { colors } = currentTheme

  // 从后端加载默认模型设置
  useEffect(() => {
    const loadDefaultProvider = async () => {
      try {
        const response = await fetch(`${API_BASE_URL}/api/settings/`)
        if (response.ok) {
          const data = await response.json()
          if (data.default_provider) {
            setProvider(data.default_provider)
          }
        }
      } catch (error) {
        console.error('加载默认模型失败:', error)
      }
    }
    loadDefaultProvider()
  }, [])

  useEffect(() => {
    const timer = setTimeout(() => setIsRestoring(false), 1000)
    return () => clearTimeout(timer)
  }, [messages.length])

  const scrollToBottom = useCallback(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [])

  useEffect(() => {
    scrollToBottom()
  }, [messages, streamingContent, scrollToBottom])

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!input.trim() || isSending) return

    const message = input.trim()
    setInput('')

    try {
      if (useStream) {
        await sendStreamMessage(message, provider, useRag, useMemory, selectedDocumentIds)
      } else {
        await sendMessage(message, provider, useRag, useMemory, selectedDocumentIds)
      }
    } catch (err) {
      console.error('Failed to send message:', err)
      alert(`Send failed: ${err}`)
    }
  }

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      handleSubmit(e)
    }
  }

  const copyMessage = async (content: string, id: string) => {
    await navigator.clipboard.writeText(content)
    setCopiedId(id)
    setTimeout(() => setCopiedId(null), 2000)
  }

  const handleSaveAsMemory = async (content: string, messageId: string) => {
    const success = await saveMessageAsMemory(messageId, content)
    if (success && !savedMessageIds.includes(messageId)) {
      setSavedMessageIds(prev => [...prev, messageId])
    }
  }

  return (
    <div className="flex flex-col h-full relative">
      {/* 固定顶部工具栏 - 64px 高度 */}
      <div
        className="px-4 border-b flex items-center justify-between flex-shrink-0 relative z-30"
        style={{
          background: colors.chatBarBg,
          borderColor: colors.border,
          height: '64px'
        }}
      >
        {/* 左侧工具 */}
        <div className="flex items-center gap-3">
          <button
            onClick={() => setShowSettings(!showSettings)}
            className="flex items-center gap-2 px-4 py-2 rounded-xl border transition-all text-sm"
            style={{
              background: colors.cardBg,
              borderColor: colors.border,
              color: colors.textSecondary
            }}
          >
            <Settings2 className="w-4 h-4" />
            <span>Settings</span>
            {showSettings ? <ChevronUp className="w-3 h-3" /> : <ChevronDown className="w-3 h-3" />}
          </button>
          
          {useRag && (
            <DocumentSelector
              selectedIds={selectedDocumentIds}
              onSelectionChange={setSelectedDocumentIds}
            />
          )}
        </div>

        {/* 右侧工具 */}
        <div className="flex items-center gap-3">
          {/* 清空对话按钮 */}
          {messages.length > 0 && (
            <button
              onClick={async () => {
                if (confirm('确定要清空当前对话吗？')) {
                  await createConversation()
                }
              }}
              className="flex items-center gap-2 px-3 py-2 border rounded-lg transition-all text-sm h-10"
              style={{
                background: colors.cardBg,
                borderColor: colors.border,
                color: colors.textSecondary
              }}
              title="新建对话"
            >
              <Trash2 className="w-4 h-4" />
              <span>清空</span>
            </button>
          )}

          <select
            value={provider}
            onChange={(e) => setProvider(e.target.value)}
            className="px-3 py-2 border rounded-lg text-sm focus:outline-none focus:ring-2 h-10"
            style={{
              background: colors.inputBg,
              borderColor: colors.inputBorder,
              color: colors.chatInputText
            }}
          >
            <option value="deepseek" style={{ background: colors.bgPrimary }}>DeepSeek</option>
            <option value="openai" style={{ background: colors.bgPrimary }}>OpenAI</option>
            <option value="anthropic" style={{ background: colors.bgPrimary }}>Claude</option>
            <option value="ollama" style={{ background: colors.bgPrimary }}>Ollama</option>
          </select>

          <button
            type="button"
            onClick={() => setUseRag(!useRag)}
            className="flex items-center gap-2 px-3 py-2 border rounded-lg transition-all text-sm h-10"
            style={{
              background: useRag ? colors.accentBg : colors.cardBg,
              borderColor: useRag ? colors.accent : colors.border,
              color: useRag ? colors.accentText : colors.textSecondary
            }}
          >
            <input
              type="checkbox"
              checked={useRag}
              onChange={(e) => setUseRag(e.target.checked)}
              className="sr-only"
            />
            <Sparkles className="w-4 h-4" />
            <span>RAG</span>
          </button>

          <button
            type="button"
            onClick={() => setUseStream(!useStream)}
            className="flex items-center gap-2 px-3 py-2 border rounded-lg transition-all text-sm h-10"
            style={{
              background: useStream ? colors.accentBg : colors.cardBg,
              borderColor: useStream ? colors.accent : colors.border,
              color: useStream ? colors.accentText : colors.textSecondary
            }}
          >
            <input
              type="checkbox"
              checked={useStream}
              onChange={(e) => setUseStream(e.target.checked)}
              className="sr-only"
            />
            <span>Stream</span>
          </button>
        </div>
      </div>

      {/* 设置展开面板 - 绝对定位在工具栏下方 */}
      {showSettings && (
        <div
          className="absolute left-0 right-0 p-4 shadow-lg z-40 animate-fade-in"
          style={{ 
            top: '64px',
            background: colors.chatBarBg,
            borderBottom: `1px solid ${colors.border}`
          }}
        >
          <div className="flex items-center gap-3">
            <button
              type="button"
              onClick={() => setUseMemory(!useMemory)}
              className="flex items-center gap-2 text-sm cursor-pointer p-2 rounded-lg transition-all"
              style={{
                background: useMemory ? colors.accentBg : 'transparent',
                color: useMemory ? colors.accentText : colors.textSecondary
              }}
            >
              <input
                type="checkbox"
                checked={useMemory}
                onChange={(e) => setUseMemory(e.target.checked)}
                className="sr-only"
              />
              <div 
                className="w-4 h-4 rounded border flex items-center justify-center"
                style={{ 
                  background: useMemory ? colors.accent : 'transparent',
                  borderColor: useMemory ? colors.accent : colors.border
                }}
              >
                {useMemory && (
                  <svg className="w-3 h-3 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={3} d="M5 13l4 4L19 7" />
                  </svg>
                )}
              </div>
              Use Memory
            </button>
          </div>
        </div>
      )}

      <div className="flex-1 overflow-y-auto p-4 space-y-6 scrollbar-thin">
        {messages.length === 0 ? (
          <div className="flex flex-col items-center justify-center h-full space-y-4">
            {isRestoring ? (
              <>
                <Loader2 className="w-8 h-8 animate-spin" style={{ color: colors.accent }} />
                <p className="text-sm" style={{ color: colors.textMuted }}>Restoring conversation...</p>
              </>
            ) : (
              <>
                <div
                  className="w-20 h-20 rounded-3xl flex items-center justify-center shadow-2xl animate-float"
                  style={{ 
                    background: colors.chatBubbleUser,
                    boxShadow: `0 0 40px ${colors.accent}40`
                  }}
                >
                  <Bot className="w-10 h-10 text-white" />
                </div>
                <div className="text-center">
                  <p className="text-lg font-medium" style={{ color: colors.textPrimary }}>Start a new conversation</p>
                  <p className="text-sm mt-1" style={{ color: colors.textMuted }}>Upload documents for intelligent Q&A</p>
                  {useRag && selectedDocumentIds.length > 0 && (
                    <p className="text-xs mt-2" style={{ color: colors.accentText }}>
                      {selectedDocumentIds.length} documents selected
                    </p>
                  )}
                </div>
              </>
            )}
          </div>
        ) : (
          <div className="space-y-6">
            {messages.map((message, index) => {
              const isEmptyAssistant = message.role === 'assistant' && !message.content
              if (isEmptyAssistant) return null
              
              return (
                <div
                  key={message.id || index}
                  className="flex gap-4 animate-fade-in"
                  style={{ flexDirection: message.role === 'user' ? 'row-reverse' : 'row' }}
                >
                  <div
                    className="w-11 h-11 rounded-2xl flex items-center justify-center shadow-lg"
                    style={{ background: message.role === 'user' ? colors.chatBubbleUser : 'linear-gradient(135deg, #FAF0DB, #E8D5B5)' }}
                  >
                    {message.role === 'user' ? (
                      <User className="w-5 h-5 text-white" />
                    ) : (
                      <Bot className="w-5 h-5" style={{ color: '#8B6914' }} />
                    )}
                  </div>

                  <div
                    className="max-w-[85%] rounded-3xl px-6 py-4 shadow-lg"
                    style={{ 
                      background: message.role === 'user' ? colors.chatBubbleUser : colors.chatBubbleAi,
                      border: message.role === 'user' ? 'none' : `1px solid ${colors.chatBubbleAiBorder}`,
                      borderTopLeftRadius: message.role === 'user' ? '4px' : undefined,
                      borderTopRightRadius: message.role === 'user' ? undefined : '4px',
                      color: message.role === 'user' ? '#ffffff' : colors.chatBubbleAiText
                    }}
                  >
                    {message.role === 'assistant' ? (
                      <MessageContent content={message.content} className="leading-relaxed" />
                    ) : (
                      <p className="leading-relaxed whitespace-pre-wrap">{message.content}</p>
                    )}

                    {message.role === 'assistant' && index === messages.length - 1 && isSending && streamingContent && (
                      <span
                        className="inline-block w-2 h-4 ml-1 animate-pulse rounded"
                        style={{ backgroundColor: colors.accent }}
                      />
                    )}

                    {/* 只有在消息发送完成后才显示来源和置信度面板 */}
                    {!isSending && message.role === 'assistant' && message.content && message.content.trim() && (
                      <>
                        <SourcesPanel 
                          citations={message.citations || []} 
                          isNoInfo={
                            message.content.includes('未找到') || 
                            message.content.includes('没有找到') || 
                            message.content.includes('检索失败') ||
                            message.content.includes('未能')
                          } 
                        />
                        <EvidencePanel 
                          evidence={message.evidence} 
                          isNoInfo={
                            message.content.includes('未找到') || 
                            message.content.includes('没有找到') || 
                            message.content.includes('检索失败') ||
                            message.content.includes('未能')
                          } 
                        />
                      </>
                    )}

                    <div 
                      className="flex items-center gap-1 mt-3 pt-3 border-t"
                      style={{ borderColor: message.role === 'user' ? 'rgba(255,255,255,0.2)' : colors.border }}
                    >
                      <button
                        onClick={() => copyMessage(message.content, message.id)}
                        className="p-2 rounded-xl transition-all"
                        style={{ background: 'transparent' }}
                        title="Copy"
                      >
                        {copiedId === message.id ? (
                          <CheckCheck className="w-4 h-4" style={{ color: colors.accent }} />
                        ) : (
                          <Copy className="w-4 h-4" style={{ color: message.role === 'user' ? 'rgba(255,255,255,0.6)' : colors.textMuted }} />
                        )}
                      </button>

                      {message.role === 'assistant' && (
                        <button
                          onClick={() => handleSaveAsMemory(message.content, message.id)}
                          disabled={savedMessageIds.includes(message.id)}
                          className="p-2 rounded-xl transition-all"
                          style={{
                            color: savedMessageIds.includes(message.id) ? colors.accent : colors.textMuted
                          }}
                          title={savedMessageIds.includes(message.id) ? "Saved" : "Save to memory"}
                        >
                          <BookmarkPlus className={`w-4 h-4 ${savedMessageIds.includes(message.id) ? 'fill-current' : ''}`} />
                        </button>
                      )}
                    </div>
                  </div>
                </div>
              );
            })}
          </div>
        )}

        {/* 发送消息后、收到第一个响应前显示加载动画 */}
        {isSending && !streamingContent && (
          <div className="flex gap-4 animate-fade-in">
            <div className="w-11 h-11 rounded-2xl flex items-center justify-center shadow-lg" style={{ background: 'linear-gradient(135deg, #FAF0DB, #E8D5B5)' }}>
              <Bot className="w-5 h-5" style={{ color: '#8B6914' }} />
            </div>
            <div
              className="rounded-3xl px-6 py-4"
              style={{
                background: colors.chatBubbleAi,
                border: `1px solid ${colors.chatBubbleAiBorder}`
              }}
            >
              <div className="flex items-center gap-3">
                <div className="flex gap-1">
                  <span className="w-2 h-2 rounded-full animate-bounce" style={{ backgroundColor: colors.accent, animationDelay: '0ms' }} />
                  <span className="w-2 h-2 rounded-full animate-bounce" style={{ backgroundColor: colors.accent, animationDelay: '150ms' }} />
                  <span className="w-2 h-2 rounded-full animate-bounce" style={{ backgroundColor: colors.accent, animationDelay: '300ms' }} />
                </div>
                <span className="text-sm" style={{ color: colors.textMuted }}>AI is thinking...</span>
              </div>
            </div>
          </div>
        )}

        <div ref={messagesEndRef} />
      </div>

      <form
        onSubmit={handleSubmit}
        className="flex-shrink-0 px-6 pt-4 pb-5"
        style={{
          background: colors.chatBarBg,
          borderTop: `1px solid ${colors.border}`,
          height: '145px'
        }}
      >
        {useRag && selectedDocumentIds.length > 0 && (
          <div
            className="mb-2 px-3 py-1.5 rounded-lg text-xs flex items-center gap-2"
            style={{
              background: colors.accentBg,
              color: colors.accentText,
              border: `1px solid ${colors.accent}40`
            }}
          >
            <Sparkles className="w-3.5 h-3.5" />
            {selectedDocumentIds.length} documents selected, precise retrieval enabled
          </div>
        )}
        
        <div className="flex gap-3 items-stretch">
          <div className="flex-1 relative">
            <textarea
              ref={inputRef}
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={handleKeyDown}
              placeholder="Type your question..."
              className="w-full resize-none border rounded-2xl px-4 py-3 transition-all focus:outline-none focus:ring-2 focus:border-opacity-100"
              style={{
                background: colors.chatInputBg,
                borderColor: colors.chatInputBorder,
                color: colors.chatInputText,
                maxHeight: '80px',
                minHeight: '56px',
                height: '90px',
                boxShadow: 'inset 0 1px 3px rgba(0,0,0,0.05)',
                '--tw-ring-color': colors.accent + '30'
              } as React.CSSProperties}
              rows={2}
            />
          </div>
          <button
            type="submit"
            disabled={!input.trim() || isSending}
            className="px-4 rounded-2xl flex items-center justify-center gap-2 font-semibold transition-all duration-200 border hover:scale-105 active:scale-95 disabled:scale-100"
            style={{
              background: input.trim() && !isSending ? colors.accent : colors.cardBg,
              borderColor: input.trim() && !isSending ? colors.accent : colors.inputBorder,
              color: input.trim() && !isSending ? '#ffffff' : colors.textMuted,
              cursor: !input.trim() || isSending ? 'not-allowed' : 'pointer',
              boxShadow: input.trim() && !isSending ? `0 4px 14px ${colors.accent}40` : 'none',
              height: '80px',
              minWidth: '100px'
            }}
          >
            {isSending ? (
              <>
                <Loader2 className="w-5 h-5 animate-spin" />
                <span>Sending</span>
              </>
            ) : (
              <>
                <Send className="w-5 h-5" style={{ color: input.trim() && !isSending ? '#ffffff' : colors.textMuted }} />
                <span>Send</span>
              </>
            )}
          </button>
        </div>
        <div className="flex items-center justify-between mt-1.5 text-xs" style={{ color: colors.textMuted }}>
          <span>Enter to send, Shift + Enter for new line</span>
          <span className="flex items-center gap-1">
            <Sparkles className="w-3 h-3" />
            {useRag 
              ? selectedDocumentIds.length > 0 
                ? `Retrieving from ${selectedDocumentIds.length} documents` 
                : "Retrieving from all documents"
              : "RAG disabled"
            }
          </span>
        </div>
      </form>
    </div>
  )
}