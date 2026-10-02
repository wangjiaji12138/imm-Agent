import React from 'react'
import { afterEach, expect, it, vi } from 'vitest'
import { cleanup, render, screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import App from '../src/App'
import type { ChatResponse, SourceResponse } from '../src/shared/api/generated'

const chat: ChatResponse = {
  request_id: 'request-1', conversation_id: null, conversation_token: null, result_type: 'answer',
  answer: '免疫疗法帮助免疫系统对抗癌症。', evidence_status: 'sufficient', follow_up_question: null,
  citations: [{ chunk_id: 'chunk-1', claim: '帮助免疫系统对抗癌症' }],
  sources: [{ chunk_id: 'chunk-1', title: 'NCI 资料', organization: 'NCI',
    source_url: 'https://example.org/nci', published_at: '2024-01-01' }],
}

const source: SourceResponse = {
  ...chat.sources[0], document_id: 'doc-1', version_id: 'version-1',
  text: '原文说明免疫系统可以对抗癌症。', title_path: '概述', char_start: 10, char_end: 28,
}

function json(body: unknown, status = 200) {
  return new Response(JSON.stringify(body), { status, headers: { 'Content-Type': 'application/json' } })
}

afterEach(() => { cleanup(); vi.unstubAllGlobals() })

it('sends a question and expands every citation to the original source', async () => {
  const fetchMock = vi.fn(async (input: RequestInfo | URL) => {
    if (input === '/health') return json({ status: 'ok', service: 'imm-agent' })
    if (input === '/api/chat') return json(chat)
    if (input === '/api/sources/chunk-1') return json(source)
    throw new Error('unexpected request')
  })
  vi.stubGlobal('fetch', fetchMock)
  const user = userEvent.setup()
  render(<App />)
  await user.type(screen.getByRole('textbox', { name: '你想了解什么？' }), '什么是癌症免疫疗法？')
  await user.click(screen.getByRole('button', { name: '发送问题' }))
  expect(await screen.findByText(chat.answer)).toBeTruthy()
  expect(screen.getByText('支持结论：帮助免疫系统对抗癌症')).toBeTruthy()
  await user.click(screen.getByRole('button', { name: '展开原文' }))
  expect(await screen.findByText(source.text)).toBeTruthy()
  expect(screen.getByRole('link', { name: '打开原始来源' }).getAttribute('href')).toBe(source.source_url)
  expect(fetchMock).toHaveBeenCalledWith('/api/chat', expect.anything())
})

it('shows evidence insufficiency without inventing a source', async () => {
  vi.stubGlobal('fetch', vi.fn(async (input: RequestInfo | URL) => input === '/health'
    ? json({ status: 'ok', service: 'imm-agent' })
    : json({ ...chat, result_type: 'insufficient', answer: '当前资料不足以回答这个问题。',
      evidence_status: 'insufficient', citations: [], sources: [] })))
  const user = userEvent.setup()
  render(<App />)
  await user.type(screen.getByRole('textbox', { name: '你想了解什么？' }), '资料不足的问题？')
  await user.click(screen.getByRole('button', { name: '发送问题' }))
  expect(await screen.findByText('当前资料不足以回答这个问题。')).toBeTruthy()
  expect(screen.queryByRole('button', { name: '展开原文' })).toBeNull()
})

it('retains the draft after service failure and retries once', async () => {
  let calls = 0
  vi.stubGlobal('fetch', vi.fn(async (input: RequestInfo | URL) => {
    if (input === '/health') return json({ status: 'ok', service: 'imm-agent' })
    calls += 1
    return calls === 1 ? json({ error: { code: 'dependency_unavailable', message: '依赖暂不可用',
      request_id: 'error-1' } }, 503) : json(chat)
  }))
  const user = userEvent.setup()
  render(<App />)
  const textbox = screen.getByRole('textbox', { name: '你想了解什么？' }) as HTMLInputElement
  await user.type(textbox, '什么是癌症免疫疗法？')
  await user.click(screen.getByRole('button', { name: '发送问题' }))
  expect(await screen.findByText('依赖暂不可用')).toBeTruthy()
  expect(textbox.value).toBe('什么是癌症免疫疗法？')
  await user.click(screen.getByRole('button', { name: '重试' }))
  await waitFor(() => expect(calls).toBe(2))
  expect(await screen.findByText(chat.answer)).toBeTruthy()
  expect(textbox.value).toBe('')
})

it('submits and updates feedback with the issued conversation credential', async () => {
  const submissions: Array<{ rating: string; note: string | null }> = []
  const fetchMock = vi.fn(async (input: RequestInfo | URL, init?: RequestInit) => {
    if (input === '/health') return json({ status: 'ok', service: 'imm-agent' })
    if (input === '/api/chat') return json({ ...chat, conversation_id: 'conversation-1',
      conversation_token: 'secret-token', citations: [], sources: [] })
    if (input === '/api/feedback') {
      expect((init?.headers as Record<string, string>)['X-Conversation-Token']).toBe('secret-token')
      const body = JSON.parse(init?.body as string)
      submissions.push(body)
      return json(body)
    }
    throw new Error('unexpected request')
  })
  vi.stubGlobal('fetch', fetchMock)
  const user = userEvent.setup()
  render(<App />)
  await user.type(screen.getByRole('textbox', { name: '你想了解什么？' }), '什么是癌症免疫疗法？')
  await user.click(screen.getByRole('button', { name: '发送问题' }))
  await screen.findByText(chat.answer)
  await user.click(screen.getByRole('button', { name: '有帮助' }))
  await waitFor(() => expect(submissions).toHaveLength(1))
  await user.click(screen.getByRole('button', { name: '添加备注' }))
  await user.type(screen.getByRole('textbox', { name: '备注（可选）' }), '<script>alert(1)</script>')
  await user.click(screen.getByRole('button', { name: '保存反馈' }))
  await waitFor(() => expect(submissions).toHaveLength(2))
  await user.click(screen.getByRole('button', { name: '没帮助' }))
  await waitFor(() => expect(submissions).toHaveLength(3))
  expect(submissions.map((item) => item.rating)).toEqual(['helpful', 'helpful', 'not_helpful'])
  expect(submissions[2].note).toBe('<script>alert(1)</script>')
  expect(screen.queryByText('alert(1)')).toBeNull()
})
