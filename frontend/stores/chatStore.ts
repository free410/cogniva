import { create } from 'zustand'
import { persist, createJSONStorage } from 'zustand/middleware'
import { api } from '@/lib/api'
import type { Conversation, Message } from '@/lib/types'

// 聊天标签页
interface ChatTab {
  id: string
  conversationId: string
  title: string
  messages: Message[]
  createdAt: Date
}

interface ChatState {
  conversations: Conversation[]
  currentConversation: Conversation | null
  messages: Message[]
  isLoading: boolean
  isSending: boolean
  streamingContent: string
  availableProviders: any[]

  // 多标签页支持
  chatTabs: ChatTab[]
  activeTabId: string | null

  // Actions
  fetchConversations: () => Promise<void>
  createConversation: (title?: string) => Promise<Conversation>
  selectConversation: (id: string) => Promise<void>
  sendMessage: (content: string, provider?: string, useRag?: boolean, useMemory?: boolean, documentIds?: string[]) => Promise<void>
  sendStreamMessage: (content: string, provider?: string, useRag?: boolean, useMemory?: boolean, documentIds?: string[]) => Promise<void>
  updateConversationTitle: (id: string, title: string) => Promise<void>
  deleteConversation: (id: string) => Promise<void>
  clearAllConversations: () => Promise<void>
  clearCurrentConversation: () => void
  fetchAvailableProviders: () => Promise<void>
  saveMessageAsMemory: (messageId: string, content: string, category?: string, importance?: number) => Promise<boolean>

  // 标签页操作
  openTab: (conversationId: string, title: string) => void
  closeTab: (tabId: string) => void
  switchTab: (tabIdOrConvoId: string) => Promise<void>
  closeCurrentTab: () => void
  updateTabMessages: (tabId: string, messages: Message[]) => void
  appendTabMessage: (tabId: string, message: Message) => void
  loadMessagesForTab: (conversationId: string) => Promise<void>
}

export const useChatStore = create<ChatState>()(
  persist(
    (set, get) => ({
  conversations: [],
  currentConversation: null,
  messages: [],
  chatTabs: [],
  activeTabId: null,
  isLoading: false,
  isSending: false,
  streamingContent: '',
  availableProviders: [],

  // ===== 多标签页操作 =====
  openTab: async (conversationId: string, title: string) => {
    const state = get()
    // 检查是否已经打开
    const existingTab = state.chatTabs.find(t => t.conversationId === conversationId)
    if (existingTab) {
      set(state => ({
        activeTabId: existingTab.id,
        currentConversation: state.conversations.find(c => c.id === conversationId) || null,
        // 【修复】确保 messages 与标签页同步
        messages: existingTab.messages
      }))
      return existingTab
    }

    // 创建新标签
    const newTab: ChatTab = {
      id: `tab-${Date.now()}-${Math.random().toString(36).slice(2, 9)}`,
      conversationId,
      title,
      messages: [],
      createdAt: new Date()
    }

    // 加载对话消息
    try {
      const { data } = await api.get<Conversation & { messages: Message[] }>(`/api/conversations/${conversationId}`)
      if (data) {
        newTab.messages = data.messages || []
        set(state => ({
          chatTabs: [...state.chatTabs, newTab],
          activeTabId: newTab.id,
          currentConversation: data,
          // 【修复】确保 messages 与标签页同步
          messages: newTab.messages
        }))
      } else {
        // 如果API调用失败，仍然创建标签页，但消息为空
        set(state => ({
          chatTabs: [...state.chatTabs, newTab],
          activeTabId: newTab.id
        }))
      }
    } catch (error) {
      console.error('Failed to load conversation:', error)
      // 即使加载失败也创建标签页
      set(state => ({
        chatTabs: [...state.chatTabs, newTab],
        activeTabId: newTab.id
      }))
    }

    return newTab
  },

  closeTab: (tabId: string) => {
    const state = get()
    const tabIndex = state.chatTabs.findIndex(t => t.id === tabId)
    if (tabIndex === -1) return

    const newTabs = state.chatTabs.filter(t => t.id !== tabId)

    // 确定新的激活标签
    let newActiveId = state.activeTabId
    if (state.activeTabId === tabId) {
      if (newTabs.length > 0) {
        // 优先选择右边的标签，如果右边没有则选择左边的
        const rightTab = newTabs[tabIndex]
        const leftTab = newTabs[tabIndex - 1]
        newActiveId = rightTab ? rightTab.id : (leftTab ? leftTab.id : null)
      } else {
        newActiveId = null
      }
    }

    // 更新状态
    if (newActiveId) {
      const newActiveTab = newTabs.find(t => t.id === newActiveId)
      if (newActiveTab) {
        set({
          chatTabs: newTabs,
          activeTabId: newActiveId,
          currentConversation: state.conversations.find(c => c.id === newActiveTab.conversationId) || null,
          messages: newActiveTab.messages
        })
        return
      }
    }

    set({
      chatTabs: newTabs,
      activeTabId: newActiveId,
      currentConversation: null,
      messages: []
    })
  },

  // 加载对话消息的辅助函数
  loadMessagesForTab: async (conversationId: string) => {
    try {
      const response = await api.get<Conversation & { messages: Message[] }>(`/api/conversations/${conversationId}`)
      const convWithMessages = (response as any).data || response
      if (convWithMessages && convWithMessages.messages) {
        set(state => ({
          chatTabs: state.chatTabs.map(t =>
            t.conversationId === conversationId ? { ...t, messages: convWithMessages.messages } : t
          ),
          messages: convWithMessages.messages,
          currentConversation: convWithMessages
        }))
      }
    } catch (err) {
      console.error('Failed to load conversation messages:', err)
    }
  },

  switchTab: async (tabIdOrConvoId: string) => {
    // 情况1：直接通过 tabId 切换
    let state = get()
    const tab = state.chatTabs.find(t => t.id === tabIdOrConvoId)
    if (tab) {
      const conversation = state.conversations.find(c => c.id === tab.conversationId)
      set({
        activeTabId: tabIdOrConvoId,
        currentConversation: conversation || null,
        messages: tab.messages
      })
      return
    }

    // 情况2：通过 conversationId
    state = get()
    const conversation = state.conversations.find(c => c.id === tabIdOrConvoId)
    if (!conversation) return

    // 检查是否已有标签
    state = get()
    const existingTab = state.chatTabs.find(t => t.conversationId === tabIdOrConvoId)

    if (existingTab) {
      set({
        activeTabId: existingTab.id,
        currentConversation: conversation,
        messages: existingTab.messages
      })
      if (existingTab.messages.length === 0) {
        get().loadMessagesForTab(tabIdOrConvoId)
      }
    } else {
      // 创建新标签
      const newTabId = `tab-${Date.now()}-${Math.random().toString(36).slice(2, 9)}`
      const newTab: ChatTab = {
        id: newTabId,
        conversationId: conversation.id,
        title: conversation.title,
        messages: [],
        createdAt: new Date()
      }

      set({
        chatTabs: [...state.chatTabs, newTab],
        activeTabId: newTabId,
        currentConversation: conversation,
        messages: []
      })

      get().loadMessagesForTab(tabIdOrConvoId)
    }
  },

  closeCurrentTab: () => {
    const state = get()
    if (state.activeTabId) {
      get().closeTab(state.activeTabId)
    }
  },

  updateTabMessages: (tabId: string, messages: Message[]) => {
    set(state => ({
      chatTabs: state.chatTabs.map(t =>
        t.id === tabId ? { ...t, messages } : t
      )
    }))
  },

  appendTabMessage: (tabId: string, message: Message) => {
    set(state => ({
      chatTabs: state.chatTabs.map(t =>
        t.id === tabId
          ? { ...t, messages: [...t.messages, message] }
          : t
      )
    }))
  },

  // ===== 对话相关操作 =====
  fetchConversations: async () => {
    set({ isLoading: true })
    try {
      const response = await api.get<Conversation[]>('/api/conversations')
      const data = (response as any).data || response

      if (!data || data.length === 0) {
        set({ isLoading: false })
        return
      }

      // 使用 get() 获取最新状态
      const currentState = get()
      const localConversationIds = new Set(currentState.conversations.map((c: Conversation) => c.id))
      const newConversations = data.filter((c: Conversation) => !localConversationIds.has(c.id))
      const mergedConversations = [...currentState.conversations, ...newConversations]

      set({ conversations: mergedConversations })

      // 如果没有打开的标签页，自动打开第一个对话
      if (currentState.chatTabs.length === 0 && newConversations.length > 0) {
        const firstConvo = newConversations[0]
        const newTab: ChatTab = {
          id: `tab-${Date.now()}-${Math.random().toString(36).slice(2, 9)}`,
          conversationId: firstConvo.id,
          title: firstConvo.title,
          messages: [],
          createdAt: new Date()
        }

        set(state => ({
          chatTabs: [newTab],
          activeTabId: newTab.id,
          currentConversation: firstConvo,
          messages: []
        }))

        // 加载该对话的消息
        try {
          const resp = await api.get<Conversation & { messages: Message[] }>(`/api/conversations/${firstConvo.id}`)
          const convData = (resp as any).data || resp
          if (convData && convData.messages) {
            set(state => ({
              chatTabs: state.chatTabs.map(t =>
                t.conversationId === firstConvo.id ? { ...t, messages: convData.messages } : t
              ),
              messages: convData.messages,
              currentConversation: convData
            }))
          }
        } catch (err) {
          console.error('Failed to load first conversation messages:', err)
        }
      }
    } catch (error) {
      console.error('Failed to fetch conversations:', error)
    }
    set({ isLoading: false })
  },

  createConversation: async (title?: string) => {
    try {
      const response = await api.post<Conversation>('/api/conversations', { title })
      const data = (response as any).data || response
      
      if (data && data.id) {
        // 添加到对话列表
        const newConvs = [data, ...get().conversations]

        // 自动打开新标签页
        const newTabId = `tab-${Date.now()}-${Math.random().toString(36).slice(2, 9)}`
        const newTab: ChatTab = {
          id: newTabId,
          conversationId: data.id,
          title: data.title || '新对话',
          messages: [],
          createdAt: new Date()
        }

        set(state => ({
          conversations: newConvs,
          currentConversation: data,
          messages: [],
          chatTabs: [newTab, ...state.chatTabs],
          activeTabId: newTabId
        }))
        console.log('[createConversation] 对话已创建:', data.id)
        return data
      } else {
        console.error('[createConversation] API 返回空数据')
      }
    } catch (error) {
      console.error('[createConversation] 失败:', error)
    }
    throw new Error('Failed to create conversation')
  },

  selectConversation: async (id: string) => {
    const state = get()

    // 检查是否已经有该对话的标签页
    const existingTab = state.chatTabs.find(t => t.conversationId === id)
    if (existingTab) {
      // 直接切换到已有标签
      get().switchTab(existingTab.id)
      return
    }

    // 没有标签页，则加载对话并创建新标签
    set({ isLoading: true })
    try {
      const response = await api.get<Conversation & { messages: Message[] }>(`/api/conversations/${id}`)
      const data = (response as any).data || response
      if (data) {
        // 创建新标签
        const newTab: ChatTab = {
          id: `tab-${Date.now()}-${Math.random().toString(36).slice(2, 9)}`,
          conversationId: id,
          title: data.title,
          messages: data.messages || [],
          createdAt: new Date()
        }

        set(state => ({
          conversations: [data, ...state.conversations.filter(c => c.id !== id)],
          currentConversation: data,
          messages: data.messages || [],
          chatTabs: [...state.chatTabs, newTab],
          activeTabId: newTab.id,
          isLoading: false
        }))
      }
    } catch (error) {
      console.error('Failed to select conversation:', error)
      set({ isLoading: false })
    }
  },

  sendMessage: async (content: string, provider = 'deepseek', useRag = true, useMemory = true, documentIds?: string[]) => {
    // 在没有对话的情况下先创建
    if (!get().currentConversation) {
      await get().createConversation()
    }

    // 先添加用户消息
    const userMessage: Message = {
      id: `temp-${Date.now()}`,
      role: 'user',
      content,
      created_at: new Date().toISOString()
    }

    // 更新UI显示用户消息
    set(state => {
      // 更新后的消息列表
      const updatedMessages = [...state.messages, userMessage]
      const currentTabId = state.activeTabId

      return {
        // 更新顶级 messages
        messages: updatedMessages,
        // 同时更新当前标签页的 messages
        chatTabs: state.chatTabs.map(t =>
          t.id === currentTabId
            ? { ...t, messages: updatedMessages }
            : t
        ),
        isSending: true
      }
    })

    try {
      // 发送请求
      const response = await api.post(`/api/conversations/${get().currentConversation?.id}/messages`, {
        content,
        provider,
        use_rag: useRag,
        use_memory: useMemory,
        document_ids: documentIds && documentIds.length > 0 ? documentIds : null
      })

      // 添加助手回复
      const responseData = (response as any).data || response
      const assistantMessage: Message = {
        id: responseData.message_id || responseData.id || `assistant-${Date.now()}`,
        role: 'assistant',
        content: responseData.content || '',
        created_at: new Date().toISOString(),
        citations: responseData.citations,
        evidence: responseData.evidence
      }

      // 保留用户消息，添加助手回复
      set(state => {
        // 更新后的消息列表
        const updatedMessages = [
          ...state.messages.map(m =>
            m.id.startsWith('temp-')
              ? { ...m, id: m.id.replace('temp-', '') }
              : m
          ),
          assistantMessage
        ]
        const currentTabId = state.activeTabId

        return {
          // 更新顶级 messages
          messages: updatedMessages,
          // 同时更新当前标签页的 messages
          chatTabs: state.chatTabs.map(t =>
            t.id === currentTabId
              ? { ...t, messages: updatedMessages }
              : t
          ),
          isSending: false
        }
      })
    } catch (error) {
      console.error('Failed to send message:', error)
      set({ isSending: false })
    }
  },

  sendStreamMessage: async (content: string, provider = 'deepseek', useRag = true, useMemory = true, documentIds?: string[]) => {
    let conversation = get().currentConversation
    if (!conversation) {
      // 如果没有当前对话，尝试使用服务器返回的对话列表第一个
      const convs = get().conversations
      if (convs && convs.length > 0) {
        conversation = convs[0]
        set({ currentConversation: conversation })
      }
    }
    if (!conversation) {
      // 仍然没有，尝试创建新对话
      try {
        conversation = await get().createConversation()
      } catch (e) {
        console.error('[sendStreamMessage] 创建对话失败:', e)
        set({ isSending: false })
        return
      }
    }

    if (!conversation) {
      console.error('[sendStreamMessage] 无法获取有效对话')
      set({ isSending: false })
      return
    }

    // 生成固定的消息ID
    const assistantMessageId = `stream-${Date.now()}`
    const userMessageId = `user-${Date.now()}`

    let fullContent = ''
    let accumulatedCitations: any[] = []
    let accumulatedEvidence: any = null

    // 初始化：添加用户消息和空的助手消息占位
    set(state => {
      // 只清除 stream- 开头的残留消息（这些是未完成的助手消息）
      // 不要清除 user- 开头的消息，这些是已发送的用户消息
      const cleanMessages = state.messages.filter(m => !m.id.startsWith('stream-'))
      const userMsg: Message = {
        id: userMessageId,
        role: 'user' as const,
        content,
        created_at: new Date().toISOString()
      }
      const assistantMsg: Message = {
        id: assistantMessageId,
        role: 'assistant' as const,
        content: '',
        created_at: new Date().toISOString(),
        citations: undefined,
        evidence: undefined
      }
      const updatedMessages = [...cleanMessages, userMsg, assistantMsg]
      const currentTabId = state.activeTabId

      return {
        // 【修复】同步更新 messages 和当前标签页
        messages: updatedMessages,
        chatTabs: state.chatTabs.map(t =>
          t.id === currentTabId
            ? { ...t, messages: updatedMessages }
            : t
        ),
        isSending: true,
        streamingContent: ''
      }
    })

    try {
      const stream = await api.stream(`/api/conversations/${conversation.id}/messages/stream`, {
        content,
        provider,
        use_rag: useRag,
        use_memory: useMemory,
        document_ids: documentIds && documentIds.length > 0 ? documentIds : null
      })

      if (!stream) {
        throw new Error('Stream response is null')
      }

      console.log('[sendStreamMessage] 流式响应已接收，开始读取...')

      const reader = stream.getReader()
      const decoder = new TextDecoder()
      let buffer = '' // 未处理的缓冲区

      while (true) {
        const { done, value } = await reader.read()

        // 实时处理收到的数据
        if (value) {
          buffer += decoder.decode(value, { stream: true })
          
          // 处理缓冲区中的完整行
          while (true) {
            const newlineIndex = buffer.indexOf('\n')
            if (newlineIndex === -1) break
            
            const line = buffer.slice(0, newlineIndex).trim()
            buffer = buffer.slice(newlineIndex + 1)
            
            if (!line.startsWith('data:')) continue
            
            const jsonStr = line.slice(5).trim()
            if (!jsonStr || jsonStr === '[DONE]') continue
            
            try {
              const parsed = JSON.parse(jsonStr)
              
              if (parsed.type === 'chunk') {
                const chunkContent = parsed.content || ''
                fullContent += chunkContent
                set(state => {
                  const updatedMessages = state.messages.map(m =>
                    m.id === assistantMessageId ? { ...m, content: fullContent } : m
                  )
                  const currentTabId = state.activeTabId
                  return {
                    streamingContent: fullContent,
                    messages: updatedMessages,
                    chatTabs: state.chatTabs.map(t =>
                      t.id === currentTabId
                        ? { ...t, messages: updatedMessages }
                        : t
                    )
                  }
                })
              } else if (parsed.type === 'done') {
                if (parsed.citations) accumulatedCitations = parsed.citations
                if (parsed.evidence) accumulatedEvidence = parsed.evidence
              }
            } catch (e) {
              console.error('解析错误:', e, 'jsonStr:', jsonStr.slice(0, 100))
            }
          }
        }

        if (done) {
          console.log('[sendStreamMessage] 流式响应结束')
          break
        }
      }

      // 流式传输完成，用最终数据更新助手消息
      console.log('[sendStreamMessage] 流式传输完成，fullContent:', fullContent, 'citations:', accumulatedCitations, 'evidence:', accumulatedEvidence ? '有' : '无')
      
      // 【保护】如果 LLM 返回空响应，使用默认消息
      if (!fullContent || !fullContent.trim()) {
        fullContent = "未找到相关信息"
        console.log('[sendStreamMessage] LLM 返回空响应，使用默认消息')
      }
      
      set(state => {
        // 更新后的消息列表
        const updatedMessages = state.messages.map(m => {
          if (m.id === assistantMessageId) {
            return {
              ...m,
              id: m.id.replace('stream-', ''), // 移除 stream- 前缀，使用真实ID
              content: fullContent,
              citations: accumulatedCitations && accumulatedCitations.length > 0 ? accumulatedCitations : undefined,
              evidence: accumulatedEvidence || undefined
            }
          }
          return m
        })

        // 找到当前对话的标签页
        const currentTabId = state.activeTabId
        const currentTab = state.chatTabs.find(t => t.id === currentTabId)

        // 如果有当前标签页，同步更新
        if (currentTab) {
          return {
            // 更新顶级 messages
            messages: updatedMessages,
            // 更新当前标签页的 messages（确保两者引用同一个数组）
            chatTabs: state.chatTabs.map(t =>
              t.id === currentTabId
                ? { ...t, messages: updatedMessages }
                : t
            ),
            streamingContent: '',
            isSending: false
          }
        }

        // 如果没有标签页，仍然更新 messages
        return {
          messages: updatedMessages,
          streamingContent: '',
          isSending: false
        }
      })

    } catch (error) {
      console.error('流式对话失败:', error)
      // 发生错误时，清理消息列表
      set(state => ({
        messages: state.messages.filter(m => !m.id.startsWith('stream-') && !m.id.startsWith('user-')),
        streamingContent: '',
        isSending: false
      }))
    }
  },

  updateConversationTitle: async (id: string, title: string) => {
    try {
      await api.put(`/api/conversations/${id}`, { title })
      set(state => ({
        conversations: state.conversations.map(c =>
          c.id === id ? { ...c, title } : c
        ),
        currentConversation: state.currentConversation?.id === id
          ? { ...state.currentConversation, title }
          : state.currentConversation
      }))
    } catch (error) {
      console.error('Failed to update conversation title:', error)
    }
  },

  deleteConversation: async (id: string) => {
    try {
      await api.delete(`/api/conversations/${id}`)
      set(state => {
        // 关闭属于该对话的标签页
        const newTabs = state.chatTabs.filter(t => t.conversationId !== id)
        // 如果删除的是当前对话
        const isCurrentDeleted = state.currentConversation?.id === id
        // 确定新的激活标签
        let newActiveId = state.activeTabId
        if (isCurrentDeleted) {
          if (newTabs.length > 0) {
            newActiveId = newTabs[0].id
          } else {
            newActiveId = null
          }
        }
        return {
          conversations: state.conversations.filter(c => c.id !== id),
          currentConversation: isCurrentDeleted ? null : state.currentConversation,
          messages: isCurrentDeleted ? [] : state.messages,
          chatTabs: newTabs,
          activeTabId: newActiveId
        }
      })
    } catch (error) {
      console.error('Failed to delete conversation:', error)
    }
  },

  clearAllConversations: async () => {
    try {
      await api.delete('/api/conversations')
      set({
        conversations: [],
        chatTabs: [],
        activeTabId: null,
        currentConversation: null,
        messages: []
      })
    } catch (error) {
      console.error('Failed to clear all conversations:', error)
    }
  },

  clearCurrentConversation: () => {
    set({
      currentConversation: null,
      messages: []
    })
  },

  fetchAvailableProviders: async () => {
    try {
      const response = await api.get<{ providers: any[] }>('/api/llm/providers')
      const responseData = response as any
      set({ availableProviders: responseData.providers || responseData.data?.providers || [] })
    } catch (error) {
      console.error('Failed to fetch providers:', error)
    }
  },

  saveMessageAsMemory: async (messageId: string, content: string, category?: string, importance?: number) => {
    try {
      const { data } = await api.post('/api/memories', {
        content,
        source_message_id: messageId,
        category: category || 'general',
        importance: importance || 0.5
      })
      return !!data
    } catch (error) {
      console.error('Failed to save memory:', error)
      return false
    }
  }
}),
{
  name: 'chat-store',
  storage: createJSONStorage(() => localStorage),
  partialize: (state) => ({
    conversations: state.conversations,
    currentConversation: state.currentConversation,
    messages: state.messages,
    chatTabs: state.chatTabs,
    activeTabId: state.activeTabId,
  }),
  onRehydrateStorage: () => (state) => {
    if (state) {
      // 【关键修复】清空旧对话状态，避免使用已失效的旧对话 ID
      // 服务器端对话列表会在 fetchConversations 时重新加载
      state.conversations = []
      state.currentConversation = null
      state.messages = []
      state.chatTabs = []
      state.activeTabId = null
    }
  }
}
))

