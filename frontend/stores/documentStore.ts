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
          status: 'processing',
          created_at: new Date().toISOString()
        }
        set(state => ({
          documents: [newDoc, ...state.documents],
          uploadProgress: 100
        }))
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
  }
}))