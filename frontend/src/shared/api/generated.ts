// Types mirrored from the backend OpenAPI contracts for task 23.
export type ResultType = 'answer' | 'clarify' | 'insufficient' | 'refuse' | 'out_of_scope' | 'emergency'
export type EvidenceStatus = 'sufficient' | 'insufficient' | 'conflicting' | 'not_applicable'

export interface Citation {
  chunk_id: string
  claim: string
}

export interface SourceSummary {
  chunk_id: string
  title: string
  organization: string
  source_url: string
  published_at: string | null
}

export interface ChatResponse {
  request_id: string
  conversation_id: string | null
  conversation_token: string | null
  result_type: ResultType
  answer: string
  citations: Citation[]
  evidence_status: EvidenceStatus
  follow_up_question: string | null
  sources: SourceSummary[]
}

export interface SourceResponse extends SourceSummary {
  document_id: string
  version_id: string
  text: string
  title_path: string
  char_start: number
  char_end: number
}

export interface ErrorEnvelope {
  error: { code: string; message: string; request_id: string }
}

export type FeedbackRating = 'helpful' | 'not_helpful'

export interface FeedbackResponse {
  request_id: string
  rating: FeedbackRating
  note: string | null
}
