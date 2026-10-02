import { useState } from 'react'
import { Button, Link } from '@mui/material'
import { getSource } from '../../shared/api/client'
import type { Citation, SourceResponse, SourceSummary } from '../../shared/api/generated'

interface Props { citation: Citation; summary: SourceSummary }

export function SourceCard({ citation, summary }: Props) {
  const [open, setOpen] = useState(false)
  const [loading, setLoading] = useState(false)
  const [details, setDetails] = useState<SourceResponse | null>(null)
  const [error, setError] = useState<string | null>(null)

  async function loadDetails() {
    if (details || loading) return
    setLoading(true)
    setError(null)
    try { setDetails(await getSource(citation.chunk_id)) }
    catch (cause) { setError(cause instanceof Error ? cause.message : '来源加载失败。') }
    finally { setLoading(false) }
  }

  function toggle() {
    if (open) { setOpen(false); return }
    setOpen(true)
    void loadDetails()
  }

  return <article className="source-card">
    <strong>{summary.title}</strong>
    <p className="source-meta">{summary.organization} · {summary.published_at || '日期未注明'}</p>
    <p className="source-claim">支持结论：{citation.claim}</p>
    <Button size="small" onClick={() => void toggle()} aria-expanded={open}>
      {open ? '收起原文' : '展开原文'}
    </Button>
    {open && <div className="source-detail">
      {loading && <p role="status">正在加载原文…</p>}
      {error && <><p role="alert">{error}</p><Button size="small" onClick={() => void loadDetails()}>重试加载</Button></>}
      {details && <>
        <p>{details.text}</p>
        <small>原文位置：{details.title_path || '正文'}，字符 {details.char_start}–{details.char_end}</small>
        <Link href={details.source_url} target="_blank" rel="noopener noreferrer">打开原始来源</Link>
      </>}
    </div>}
  </article>
}
