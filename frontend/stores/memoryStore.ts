import { create } from 'zustand'
import { api } from '@/lib/api'
import type { Memory } from '@/lib/types'

interface MemoryState {
  memories: Memory[]
  dueMemories: Memory[]
  upcomingReviews: any[]
  statistics: any
  isLoading: boolean
  currentCategory: string | null

  // Actions
  fetchMemories: (category?: string, includeDue?: boolean) => Promise<void>
  fetchDueMemories: () => Promise<void>
  fetchUpcomingReviews: (days?: number) => Promise<void>
  fetchStatistics: () => Promise<void>
  createMemory: (content: string, category?: string, importance?: number) => Promise<Memory>
  reviewMemory: (id: string, quality: number) => Promise<void>
  updateMemory: (id: string, content?: string, category?: string, importance?: number) => Promise<void>
  deleteMemory: (id: string) => Promise<void>
  extractFromConversation: (conversationId: string, count?: number) => Promise<void>
  setCategory: (category: string | null) => void
}

export const useMemoryStore = create<MemoryState>((set, get) => ({
  memories: [],
  dueMemories: [],
  upcomingReviews: [],
  statistics: null,
  isLoading: false,
  currentCategory: null,

  fetchMemories: async (category?: string, includeDue = false) => {
    set({ isLoading: true })
    try {
      const params = new URLSearchParams()
      if (category) params.append('category', category)
      if (includeDue) params.append('include_due', 'true')
      const endpoint = `/api/memories${params.toString() ? '?' + params.toString() : ''}`

      const { data } = await api.get<Memory[]>(endpoint)
      if (data) {
        set({ memories: data })
      }
    } catch (error) {
      console.error('Failed to fetch memories:', error)
    }
    set({ isLoading: false })
  },

  fetchDueMemories: async () => {
    try {
      const { data } = await api.get<Memory[]>('/api/memories/due')
      if (data) {
        set({ dueMemories: data })
      }
    } catch (error) {
      console.error('Failed to fetch due memories:', error)
    }
  },

  fetchUpcomingReviews: async (days = 7) => {
    try {
      const { data } = await api.get<any[]>(`/api/memories/upcoming?days=${days}`)
      if (data) {
        set({ upcomingReviews: data })
      }
    } catch (error) {
      console.error('Failed to fetch upcoming reviews:', error)
    }
  },

  fetchStatistics: async () => {
    try {
      const { data } = await api.get<any>('/api/memories/statistics')
      if (data) {
        set({ statistics: data })
      }
    } catch (error) {
      console.error('Failed to fetch statistics:', error)
    }
  },

  createMemory: async (content: string, category = 'general', importance = 0.5) => {
    try {
      const { data } = await api.post<Memory>('/api/memories', {
        content,
        category,
        importance
      })
      if (data) {
        set(state => ({ memories: [data, ...state.memories] }))
        return data
      }
    } catch (error) {
      console.error('Failed to create memory:', error)
      throw error
    }
    throw new Error('Failed to create memory')
  },

  reviewMemory: async (id: string, quality: number) => {
    try {
      const { data } = await api.post<{
        id: string
        review_count: number
        next_review: string
        quality_desc: string
      }>(`/api/memories/${id}/review?quality=${quality}`)

      if (data) {
        // 从待复习列表移除
        set(state => ({
          dueMemories: state.dueMemories.filter(m => m.id !== id),
          memories: state.memories.map(m =>
            m.id === id
              ? {
                  ...m,
                  review_count: data.review_count,
                  next_review: data.next_review
                }
              : m
          )
        }))
      }
    } catch (error) {
      console.error('Failed to review memory:', error)
      throw error
    }
  },

  updateMemory: async (id: string, content?: string, category?: string, importance?: number) => {
    try {
      const updateData: any = {}
      if (content !== undefined) updateData.content = content
      if (category !== undefined) updateData.category = category
      if (importance !== undefined) updateData.importance = importance

      const { data } = await api.put<Memory>(`/api/memories/${id}`, updateData)
      if (data) {
        set(state => ({
          memories: state.memories.map(m => m.id === id ? data : m),
          dueMemories: state.dueMemories.map(m => m.id === id ? data : m)
        }))
      }
    } catch (error) {
      console.error('Failed to update memory:', error)
      throw error
    }
  },

  deleteMemory: async (id: string) => {
    try {
      await api.delete(`/api/memories/${id}`)
      set(state => ({
        memories: state.memories.filter(m => m.id !== id),
        dueMemories: state.dueMemories.filter(m => m.id !== id)
      }))
    } catch (error) {
      console.error('Failed to delete memory:', error)
      throw error
    }
  },

  extractFromConversation: async (conversationId: string, count = 3) => {
    try {
      const { data } = await api.post<{
        extracted_count: number
        memories: Memory[]
      }>(`/api/memories/extract-from-conversation?conversation_id=${conversationId}&extract_count=${count}`)

      if (data && data.memories) {
        set(state => ({
          memories: [...data.memories, ...state.memories]
        }))
      }
    } catch (error) {
      console.error('Failed to extract memories:', error)
    }
  },

  setCategory: (category: string | null) => {
    set({ currentCategory: category })
  }
}))