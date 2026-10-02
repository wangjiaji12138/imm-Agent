import { useCallback, useRef, useState } from 'react'
import { postChat } from '../../shared/api/client'
import type { ChatResponse } from '../../shared/api/generated'

export interface ChatTurn { question: string; response: ChatResponse }

export function useChat() {
  const [turns, setTurns] = useState<ChatTurn[]>([])
  const [sending, setSending] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const pending = useRef(false)
  const failedQuestion = useRef<string | null>(null)
  const epoch = useRef(0)
  const conversation = useRef<{ id: string; token: string } | null>(null)

  const send = useCallback(async (question: string): Promise<boolean> => {
    const cleaned = question.trim()
    if (pending.current || cleaned.length < 2 || cleaned.length > 500) return false
    pending.current = true
    const currentEpoch = epoch.current
    setSending(true)
    setError(null)
    try {
      const response = await postChat(cleaned, conversation.current?.id ?? null, conversation.current?.token ?? null)
      if (epoch.current !== currentEpoch) return false
      if (response.conversation_id && response.conversation_token) {
        conversation.current = { id: response.conversation_id, token: response.conversation_token }
      }
      setTurns((old) => [...old, { question: cleaned, response }])
      failedQuestion.current = null
      return true
    } catch (cause) {
      if (epoch.current !== currentEpoch) return false
      failedQuestion.current = cleaned
      setError(cause instanceof Error ? cause.message : '请求失败，请重试。')
      return false
    } finally {
      if (epoch.current === currentEpoch) {
        pending.current = false
        setSending(false)
      }
    }
  }, [])

  const retry = useCallback(() => failedQuestion.current ? send(failedQuestion.current) : Promise.resolve(false), [send])

  const reset = useCallback(() => {
    epoch.current += 1
    pending.current = false
    failedQuestion.current = null
    conversation.current = null
    setTurns([])
    setError(null)
    setSending(false)
  }, [])

  const getCredentials = useCallback(() => conversation.current, [])

  return { turns, sending, error, send, retry, reset, getCredentials }
}
