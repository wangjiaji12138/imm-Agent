import { useState } from 'react'
import { Alert, Button, TextField } from '@mui/material'
import { postFeedback } from '../../shared/api/client'
import type { FeedbackRating } from '../../shared/api/generated'

interface Props {
  requestId: string
  getCredentials: () => { id: string; token: string } | null
}

export function FeedbackForm({ requestId, getCredentials }: Props) {
  const [rating, setRating] = useState<FeedbackRating | null>(null)
  const [note, setNote] = useState('')
  const [editing, setEditing] = useState(false)
  const [pending, setPending] = useState(false)
  const [error, setError] = useState<string | null>(null)

  async function submit(selected: FeedbackRating) {
    const credentials = getCredentials()
    if (!credentials || pending) return
    setPending(true)
    setError(null)
    try {
      await postFeedback(requestId, selected, note.trim() || null, credentials.id, credentials.token)
      setRating(selected)
      setEditing(false)
    } catch (cause) {
      setError(cause instanceof Error ? cause.message : '反馈提交失败，请重试。')
    } finally {
      setPending(false)
    }
  }

  return <div className="feedback-form" aria-label="回答反馈">
    <span>{rating ? '感谢反馈，可以修改' : '这条回答有帮助吗？'}</span>
    <Button size="small" disabled={pending} variant={rating === 'helpful' ? 'contained' : 'text'}
      onClick={() => void submit('helpful')}>有帮助</Button>
    <Button size="small" disabled={pending} variant={rating === 'not_helpful' ? 'contained' : 'text'}
      onClick={() => void submit('not_helpful')}>没帮助</Button>
    <Button size="small" onClick={() => setEditing((value) => !value)}>{editing ? '收起备注' : '添加备注'}</Button>
    {editing && <div className="feedback-note">
      <TextField label="备注（可选）" size="small" multiline fullWidth value={note}
        onChange={(event) => setNote(event.target.value)} slotProps={{ htmlInput: { maxLength: 500 } }} />
      <Button size="small" disabled={pending || !rating} onClick={() => rating && void submit(rating)}>保存反馈</Button>
      <small>{note.length} / 500</small>
    </div>}
    {error && <Alert severity="error" role="alert">{error}</Alert>}
  </div>
}
