import type { ChatResponse, ErrorEnvelope, FeedbackRating, FeedbackResponse, SourceResponse } from './generated'

export class ApiError extends Error {
  readonly code: string
  readonly requestId: string | null

  constructor(message: string, code: string, requestId: string | null) {
    super(message)
    this.code = code
    this.requestId = requestId
  }
}

async function request<T>(path: string, init: RequestInit = {}, timeoutMs = 120_000): Promise<T> {
  const controller = new AbortController()
  const timeout = window.setTimeout(() => controller.abort(), timeoutMs)
  try {
    const response = await fetch(path, { ...init, signal: controller.signal })
    const body: unknown = await response.json()
    if (!response.ok) {
      const error = (body as Partial<ErrorEnvelope>)?.error
      throw new ApiError(error?.message || '请求未完成，请稍后重试。', error?.code || 'request_failed',
        error?.request_id || response.headers.get('X-Request-ID'))
    }
    return body as T
  } catch (error) {
    if (error instanceof ApiError) throw error
    if (controller.signal.aborted) throw new ApiError('请求超时，请重试。', 'timeout', null)
    throw new ApiError('服务暂时无法连接，请重试。', 'network_error', null)
  } finally {
    window.clearTimeout(timeout)
  }
}

export function postChat(message: string, conversationId: string | null = null, token: string | null = null): Promise<ChatResponse> {
  return request<ChatResponse>('/api/chat', {
    method: 'POST', headers: { 'Content-Type': 'application/json', ...(token ? { 'X-Conversation-Token': token } : {}) },
    body: JSON.stringify({ message, conversation_id: conversationId }),
  })
}

export function getSource(chunkId: string): Promise<SourceResponse> {
  return request<SourceResponse>(`/api/sources/${encodeURIComponent(chunkId)}`, {}, 15_000)
}

export function postFeedback(requestId: string, rating: FeedbackRating, note: string | null,
  conversationId: string, token: string): Promise<FeedbackResponse> {
  return request<FeedbackResponse>('/api/feedback', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json', 'X-Conversation-ID': conversationId,
      'X-Conversation-Token': token },
    body: JSON.stringify({ request_id: requestId, rating, note }),
  }, 15_000)
}
