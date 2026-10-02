import { Alert, Button, Paper } from '@mui/material'
import { SourceCard } from '../sources/SourceCard'
import { FeedbackForm } from '../feedback/FeedbackForm'
import type { ChatTurn } from './useChat'

interface Props {
  turns: ChatTurn[]
  sending: boolean
  error: string | null
  onRetry: () => void
  getCredentials: () => { id: string; token: string } | null
}

export function ChatPanel({ turns, sending, error, onRetry, getCredentials }: Props) {
  return <section className="chat-panel" aria-label="问答记录" aria-live="polite">
    {turns.map(({ question, response }) => <Paper variant="outlined" className="chat-turn" key={response.request_id}>
      <p className="chat-question">{question}</p>
      <div className="chat-answer">
        <span className={`answer-status ${response.evidence_status}`}>{response.result_type === 'insufficient' ? '证据不足' : response.evidence_status === 'conflicting' ? '资料存在冲突' : response.result_type === 'answer' ? '有来源的回答' : '请求说明'}</span>
        <p>{response.answer}</p>
        {response.follow_up_question && <small>请先明确上述问题，再继续提问。</small>}
      </div>
      {response.citations.length > 0 && <div className="turn-sources">
        <strong>支持结论的来源</strong>
        {response.citations.map((citation) => {
          const summary = response.sources.find((item) => item.chunk_id === citation.chunk_id)
          return summary ? <SourceCard key={citation.chunk_id} citation={citation} summary={summary} /> : null
        })}
      </div>}
      {response.conversation_id && <FeedbackForm requestId={response.request_id} getCredentials={getCredentials} />}
    </Paper>)}
    {sending && <Alert severity="info" role="status">正在检索已发布资料并整理回答…</Alert>}
    {error && <Alert severity="error" role="alert" action={<Button color="inherit" size="small" onClick={onRetry}>重试</Button>}>{error}</Alert>}
  </section>
}
