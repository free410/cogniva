import { create } from 'zustand'
import { api } from '@/lib/api'
import type { Document } from '@/lib/types'

interface DocumentState {
  documents: Document[]
  isLoading: boolean
  isUploading: boolean
  uploadProgress: number

  // Actions
  fetchDocuments: () => Promise<void>
  uploadDocument: (file: File) => Promise<Document>
  deleteDocument: (id: string) => Promise<void>
  pollDocumentStatus: (documentId: string) => Promise<void>
}

export const useDocumentStore = create<DocumentState>((set, get) => ({
  documents: [],
  isLoading: false,
  isUploading: false,
  uploadProgress: 0,

  fetchDocuments: async () => {
    set({ isLoading: true })
    try {
      const { data } = await api.get<Document[]>('/api/documents')
      if (data) {
        set({ documents: data })
      }
    } catch (error) {
      console.error('Failed to fetch documents:', error)
    }
    set({ isLoading: false })
  },

  uploadDocument: async (file: File) => {
    set({ isUploading: true, uploadProgress: 0 })

    // 模拟上传进度
    const progressInterval = setInterval(() => {
      set(state => ({
        uploadProgress: Math.min(state.uploadProgress + 10, 90)
      }))
    }, 200)

    try {
      const { data } = await api.upload<{
        id: string
        filename: string
        status: string
      }>('/api/documents/upload', file)

      clearInterval(progressInterval)

      if (data) {
        const newDoc: Document = {
          id: data.id,
          filename: data.filename,
          file_type: file.name.split('.').pop() || '',
          file_size: file.size,
          file_path: '',
          status: data.status as Document['status'],
          created_at: new Date().toISOString()
        }
        set(state => ({
          documents: [newDoc, ...state.documents],
          uploadProgress: 100
        }))
        // 后台上传处理是异步的，轮询直到完成/失败
        void get().pollDocumentStatus(data.id)
        return newDoc
      } else {
        throw new Error('Upload failed')
      }
    } catch (error: any) {
      clearInterval(progressInterval)
      set({ uploadProgress: 0 })
      throw error
    } finally {
      set({ isUploading: false, uploadProgress: 0 })
    }
  },

  deleteDocument: async (id: string) => {
    try {
      await api.delete(`/api/documents/${id}`)
      set(state => ({
        documents: state.documents.filter(d => d.id !== id)
      }))
    } catch (error) {
      console.error('Failed to delete document:', error)
      throw error
    }
  },

  pollDocumentStatus: async (documentId: string) => {
    // 轮询后端状态：每 2 秒一次，最多约 2 分钟
    for (let attempt = 0; attempt < 60; attempt++) {
      await new Promise(resolve => setTimeout(resolve, 2000))

      // 文档已被删除则停止轮询
      if (!get().documents.some(d => d.id === documentId)) return

      try {
        const { data } = await api.get<Document>(`/api/documents/${documentId}`)
        if (!data) return

        set(state => ({
          documents: state.documents.map(d =>
            d.id === documentId ? { ...d, ...data } : d
          )
        }))

        if (data.status === 'completed' || data.status === 'failed') return
      } catch (error) {
        console.error('Failed to poll document status:', error)
        return
      }
    }
  }
}))