export interface Message {
  id: string
  role: 'user' | 'assistant' | 'system'
  content: string
  created_at: string
  citations?: Citation[]
  evidence?: EvidenceReport
  metadata?: {
    provider?: string
    used_rag?: boolean
    used_memory?: boolean
    retrieved_chunks_count?: number
    memories_count?: number
    error?: boolean
  }
}

export interface ChunkInfo {
  id: string
  source: string
  content_preview: string
  score: number
  rank: number
  method: string
  bm25_score: number | null
  reranker_score?: number | null
  keyword_score?: number | null
  term_match_ratio?: number | null
  matched_terms?: string[]
}

export interface EvidenceReport {
  confidence: number
  confidence_level: string
  relevance_verified: boolean
  chunks_strategy: string
  retrieval_method: string
  rerank_model: string
  rerank_before_score: number | null
  rerank_after_score: number | null
  top_similarity: number
  avg_similarity: number
  intent_match_ratio?: number | null
  topic_match?: boolean | null
  entity_match_score?: number | null
  term_coverage?: number
  chunks: ChunkInfo[]
}

export interface Conversation {
  id: string
  title: string
  updated_at: string
  created_at?: string
  messages?: Message[]
}

export interface Document {
  id: string
  filename: string
  file_type: string
  file_size: number
  file_path: string
  status: 'pending' | 'processing' | 'completed' | 'failed'
  metadata?: Record<string, any>
  created_at: string
}

export interface Memory {
  id: string
  content: string
  category: string
  importance: number
  review_count: number
  next_review?: string
  created_at: string
  extra_metadata?: Record<string, any>
}

export interface Citation {
  chunk_id: string
  content: string
  similarity: number
  document_id: string
  document_title?: string
  chunk_index?: number
  metadata?: Record<string, any>
}

export interface SearchResult {
  chunk_id: string
  content: string
  document_id: string
  similarity: number
  document_title?: string
  chunk_index?: number
  metadata?: Record<string, any>
}

export interface LLMProvider {
  name: string
  display_name: string
  models: string[]
  default_model: string
  available: boolean
  supports_streaming: boolean
  supports_function_calling: boolean
}

export interface MemoryStats {
  total_memories: number
  due_reviews: number
  categories: Record<string, number>
  total_reviews: number
  average_review_count: number
}

export interface ReviewPlan {
  memory_id: string
  content: string
  category: string
  review_date: string
  days_until: number
  review_count: number
  importance: number
}
