import { useEffect, useRef, useState } from 'react'
import AutoAwesomeRoundedIcon from '@mui/icons-material/AutoAwesomeRounded'
import AddRoundedIcon from '@mui/icons-material/AddRounded'
import ArrowForwardRoundedIcon from '@mui/icons-material/ArrowForwardRounded'
import ChatBubbleOutlineRoundedIcon from '@mui/icons-material/ChatBubbleOutlineRounded'
import CompareArrowsRoundedIcon from '@mui/icons-material/CompareArrowsRounded'
import ScienceOutlinedIcon from '@mui/icons-material/ScienceOutlined'
import HistoryRoundedIcon from '@mui/icons-material/HistoryRounded'
import VerifiedOutlinedIcon from '@mui/icons-material/VerifiedOutlined'
import DescriptionOutlinedIcon from '@mui/icons-material/DescriptionOutlined'
import HelpOutlineRoundedIcon from '@mui/icons-material/HelpOutlineRounded'
import RefreshRoundedIcon from '@mui/icons-material/RefreshRounded'
import SendRoundedIcon from '@mui/icons-material/SendRounded'
import CloseRoundedIcon from '@mui/icons-material/CloseRounded'
import {
  Alert, Button, CardActionArea, Dialog, DialogContent,
  DialogTitle, IconButton, MenuItem, Paper, TextField,
  Tooltip, Typography,
} from '@mui/material'
import './App.css'
import { ChatPanel } from './features/chat/ChatPanel'
import { useChat } from './features/chat/useChat'

const modes = [
  { id: 'ask', label: '科普问答', icon: ChatBubbleOutlineRoundedIcon, title: '从一个问题，开始了解', description: '概念、术语与作用机制，都可以从这里开始。', prompts: ['什么是癌症免疫疗法？', 'PD-1 和 PD-L1 有什么关系？', 'CAR-T 细胞如何识别癌细胞？'] },
  { id: 'compare', label: '疗法比较', icon: CompareArrowsRoundedIcon, title: '把不同疗法，放在一起看', description: '明确比较对象与维度，更容易理解它们的区别。', prompts: ['CAR-T 和 TCR-T 在作用机制上有什么不同？', 'CAR-T 和免疫检查点抑制剂如何分别发挥作用？', 'CAR-T 和 TCR-T 的研究背景有哪些不同？'] },
  { id: 'research', label: '研究进展', icon: ScienceOutlinedIcon, title: '理解进展，也看清研究边界', description: '关注资料日期、研究阶段与适用条件。', prompts: ['已收录资料中，CAR-T 主要研究用于哪些癌症？', '如何理解免疫疗法的临床研究阶段？', '研究结果与获批适应证有什么区别？'] },
] as const

const therapies = ['CAR-T', 'TCR-T', '免疫检查点抑制剂']
const dimensions = ['作用机制', '研究背景', '资料所述适用条件']

type Mode = (typeof modes)[number]['id']
type ServiceStatus = 'checking' | 'online' | 'offline'

function App() {
  const [mode, setMode] = useState<Mode>('ask')
  const [draft, setDraft] = useState('')
  const [leftTherapy, setLeftTherapy] = useState<string>(therapies[0])
  const [rightTherapy, setRightTherapy] = useState<string>(therapies[2])
  const [dimension, setDimension] = useState<string>(dimensions[0])
  const [dialog, setDialog] = useState<'guide' | 'sources' | null>(null)
  const [serviceStatus, setServiceStatus] = useState<ServiceStatus>('checking')
  const [healthAttempt, setHealthAttempt] = useState(0)
  const inputRef = useRef<HTMLTextAreaElement>(null)
  const chat = useChat()
  const currentMode = modes.find((item) => item.id === mode)!
  const sameTherapy = leftTherapy === rightTherapy

  useEffect(() => {
    let active = true
    const controller = new AbortController()
    const timeout = window.setTimeout(() => controller.abort(), 6000)
    async function checkHealth() {
      try {
        const response = await fetch('/health', { signal: controller.signal })
        if (!response.ok) throw new Error('Health request failed')
        const health = await response.json()
        if (active) {
          setServiceStatus(health?.status === 'ok' && health?.service === 'imm-agent' ? 'online' : 'offline')
        }
      } catch {
        if (active) setServiceStatus('offline')
      } finally {
        window.clearTimeout(timeout)
      }
    }
    void checkHealth()
    return () => {
      active = false
      controller.abort()
      window.clearTimeout(timeout)
    }
  }, [healthAttempt])

  function fillQuestion(question: string) {
    setDraft(question)
    inputRef.current?.focus()
  }

  function newConversation() {
    chat.reset()
    setDraft('')
    setMode('ask')
    setLeftTherapy(therapies[0])
    setRightTherapy(therapies[2])
    setDimension(dimensions[0])
  }

  async function sendQuestion() {
    if (await chat.send(draft)) setDraft('')
  }

  async function retryQuestion() {
    if (await chat.retry()) setDraft('')
  }

  const statusLabel = serviceStatus === 'checking' ? '正在检查服务' : serviceStatus === 'online' ? '服务正常' : '服务未连接'

  return (
    <div className="workspace">
      <a className="skip-link" href="#main-content">跳到主要内容</a>
      <aside className="sidebar" aria-label="工作区导航">
        <div className="brand">
          <span className="brand-icon"><AutoAwesomeRoundedIcon /></span>
          <div><strong>Imm-Agent</strong><span>免疫疗法知识助手</span></div>
        </div>
        <Button className="new-conversation" variant="contained" disableElevation startIcon={<AddRoundedIcon />} onClick={newConversation}>新建会话</Button>
        <p className="section-label">探索知识</p>
        <nav className="mode-navigation" aria-label="选择提问方式">
          {modes.map(({ id, label, icon: Icon }) => (
            <Button key={id} className={mode === id ? 'navigation-item selected' : 'navigation-item'} startIcon={<Icon />} aria-pressed={mode === id} onClick={() => setMode(id)}>{label}</Button>
          ))}
        </nav>
        <div className="conversation-area">
          <p className="section-label">当前会话</p>
          <div className="draft-summary"><ChatBubbleOutlineRoundedIcon fontSize="small" /><span>{chat.turns[0]?.question || draft.trim() || '开始你的第一个问题'}</span></div>
          <p className="draft-hint">本页已回答 {chat.turns.length} 个问题</p>
          <div className="history-empty"><HistoryRoundedIcon /><span>当前页面中的对话</span><small>新建会话会开始独立的对话；刷新页面会清除本页记录。</small></div>
        </div>
        <div className="sidebar-note">
          <VerifiedOutlinedIcon /><strong>从知识出发，以证据为依据</strong>
          <p>了解一般科普信息。具体诊疗问题，请与专业医生讨论。</p>
        </div>
        <Button className="guide-button" startIcon={<HelpOutlineRoundedIcon />} onClick={() => setDialog('guide')}>使用指南与能力边界</Button>
      </aside>

      <div className="main-shell">
        <header className="topbar">
          <div className="breadcrumb"><span>知识工作台</span><span>/</span><strong>{currentMode.label}</strong></div>
          <div className="service-status">
            <span className={'status-dot ' + serviceStatus} />
            <span role="status" aria-live="polite">{statusLabel}</span>
            <Tooltip title="重新检查服务"><span><IconButton size="small" aria-label="重新检查服务" disabled={serviceStatus === 'checking'} onClick={() => { setServiceStatus('checking'); setHealthAttempt((value) => value + 1) }}><RefreshRoundedIcon fontSize="small" /></IconButton></span></Tooltip>
          </div>
        </header>

        <main id="main-content">
          <div className="workspace-content" tabIndex={0} role="region" aria-label="对话与资料来源">
            <section className="hero" aria-labelledby="hero-title">
              <div className="hero-copy">
                <span className="eyebrow"><span />让复杂知识，更容易理解</span>
                <Typography component="h1" id="hero-title">探索免疫疗法，<span>每一步都有据可循。</span></Typography>
                <p>从一个概念，到不同疗法的比较。<br className="desktop-break" />用通俗解释理解知识，用原文来源核查信息。</p>
                <div className="hero-tags"><span><ChatBubbleOutlineRoundedIcon />通俗解释</span><span><CompareArrowsRoundedIcon />多角度比较</span><span><VerifiedOutlinedIcon />来源可追溯</span></div>
              </div>
              <div className="knowledge-orbit" aria-hidden="true">
                <div className="orbit-ring outer" /><div className="orbit-ring inner" />
                <div className="orbit-center"><AutoAwesomeRoundedIcon /></div>
                <span className="orbit-node node-one"><DescriptionOutlinedIcon /></span>
                <span className="orbit-node node-two"><ScienceOutlinedIcon /></span>
                <span className="orbit-node node-three"><VerifiedOutlinedIcon /></span>
                <i className="orbit-dot dot-one" /><i className="orbit-dot dot-two" />
                <span className="orbit-caption">连接问题与知识</span>
              </div>
            </section>

            {serviceStatus === 'offline' && <Alert severity="warning" className="connection-alert">服务暂未连接，你仍可以编辑问题草稿。稍后可在右上角重新检查。</Alert>}

            <div className="content-grid">
              <div className="question-column">
                <section className="conversation-intro" aria-label="开始对话">
                  <Typography component="h2" variant="subtitle1">{currentMode.title}</Typography>
                  <p className="muted composer-description">{currentMode.description}</p>
                </section>
                <ChatPanel turns={chat.turns} sending={chat.sending} error={chat.error} onRetry={() => void retryQuestion()} getCredentials={chat.getCredentials} />

                {mode === 'compare' && (
                  <div className="comparison-builder">
                    <div className="comparison-pair">
                      <TextField select label="疗法 A" size="small" value={leftTherapy} onChange={(event) => setLeftTherapy(event.target.value)}>{therapies.map((therapy) => <MenuItem key={therapy} value={therapy}>{therapy}</MenuItem>)}</TextField>
                      <CompareArrowsRoundedIcon className="compare-icon" />
                      <TextField select label="疗法 B" size="small" value={rightTherapy} error={sameTherapy} onChange={(event) => setRightTherapy(event.target.value)}>{therapies.map((therapy) => <MenuItem key={therapy} value={therapy}>{therapy}</MenuItem>)}</TextField>
                    </div>
                    <TextField select fullWidth label="比较维度" size="small" value={dimension} onChange={(event) => setDimension(event.target.value)}>{dimensions.map((item) => <MenuItem key={item} value={item}>{item}</MenuItem>)}</TextField>
                    {sameTherapy && <p className="field-error" role="alert">请选择两种不同的疗法。</p>}
                    <Button size="small" endIcon={<ArrowForwardRoundedIcon />} disabled={sameTherapy} onClick={() => fillQuestion(leftTherapy + ' 和' + rightTherapy + '在' + dimension + '上有什么不同？')}>整理为问题</Button>
                  </div>
                )}
                {mode === 'research' && <Alert severity="info" icon={<ScienceOutlinedIcon />} className="research-note">研究进展将以已收录资料的日期和研究阶段为准。</Alert>}

                <section className="prompt-section" aria-labelledby="prompt-title">
                  <div className="section-heading"><Typography id="prompt-title" component="h2" variant="subtitle1">试着从这些问题开始</Typography><span>点击填入提问框</span></div>
                  <div className="prompt-grid">
                    {currentMode.prompts.map((question, index) => (
                      <Paper variant="outlined" key={question} className="prompt-card">
                        <CardActionArea onClick={() => fillQuestion(question)}>
                          <span className={'prompt-number tone-' + index}>0{index + 1}</span>
                          <Typography component="p">{question}</Typography>
                          <ArrowForwardRoundedIcon className="prompt-arrow" fontSize="small" />
                        </CardActionArea>
                      </Paper>
                    ))}
                  </div>
                </section>

                <section className="workflow-strip" aria-label="问答处理流程">
                  <div className="workflow-title"><AutoAwesomeRoundedIcon /><strong>一份可追溯的回答</strong></div>
                  <div className="workflow-steps">{['理解问题', '检索已发布资料', '解释并附上来源'].map((step, index) => <div key={step}><span>{index + 1}</span>{step}{index < 2 && <ArrowForwardRoundedIcon fontSize="small" />}</div>)}</div>
                </section>
              </div>

              <aside className="evidence-column" aria-label="资料来源预览">
                <Paper variant="outlined" className="evidence-card">
                  <div className="evidence-title"><span className="evidence-icon"><DescriptionOutlinedIcon /></span><div><Typography component="h2" variant="subtitle1">资料来源</Typography><p>从结论，回到原文</p></div></div>
                  <div className="evidence-content">
                    <div className="empty-state source-empty"><DescriptionOutlinedIcon /><strong>{chat.turns.length ? '来源随回答展示' : '暂无引用资料'}</strong><p>{chat.turns.length ? '点击回答下方的来源卡片，可查看支持结论、原文位置和原始链接。' : '收到回答后，可在回答下方展开每条引用的原文片段。'}</p><Button size="small" onClick={() => setDialog('sources')}>来源包含哪些信息？</Button></div>
                  </div>
                </Paper>
                <Paper variant="outlined" className="evidence-legend">
                  <div className="legend-heading"><VerifiedOutlinedIcon /><strong>看懂证据状态</strong></div>
                  <p className="muted">以下是回答时可能出现的状态。</p>
                  <div><span className="legend-dot sufficient" /><strong>证据充足</strong><span>关键结论有资料支持</span></div>
                  <div><span className="legend-dot insufficient" /><strong>证据不足</strong><span>明确说明资料的缺口</span></div>
                  <div><span className="legend-dot conflicting" /><strong>资料冲突</strong><span>分别呈现不同来源观点</span></div>
                </Paper>
              </aside>
            </div>
            <footer className="workspace-footer"><span>Imm-Agent · 癌症免疫疗法科普</span><span>科普信息不能替代专业医生的诊疗建议。</span></footer>
          </div>
          <Paper variant="outlined" className="composer" component="section" aria-label="输入问题">
            <TextField className="question-input" fullWidth multiline size="small" minRows={1} maxRows={4} value={draft}
              inputRef={inputRef} label="你想了解什么？" placeholder="例如：PD-1 和 PD-L1 有什么关系？"
              onChange={(event) => setDraft(event.target.value)}
              onKeyDown={(event) => { if (event.key === 'Enter' && (event.ctrlKey || event.metaKey)) { event.preventDefault(); void sendQuestion() } }}
              slotProps={{ htmlInput: { maxLength: 500, 'aria-describedby': 'draft-notice' } }}
            />
            <div className="composer-bottom"><span className="draft-counter">{draft.length} / 500</span><Button variant="contained" disabled={chat.sending || draft.trim().length < 2} onClick={() => void sendQuestion()} endIcon={<SendRoundedIcon />} disableElevation>{chat.sending ? '正在回答' : '发送问题'}</Button></div>
            <div className="draft-notice" id="draft-notice"><span className="small-dot" />仅提供一般科普，不替代专业诊疗。按 Ctrl/⌘ + Enter 发送。</div>
          </Paper>
        </main>
      </div>

      <Dialog open={dialog !== null} onClose={() => setDialog(null)} maxWidth="sm" fullWidth aria-labelledby="guide-title">
        <DialogTitle id="guide-title" sx={{ pr: 7 }}>{dialog === 'sources' ? '让每一条引用都可核查' : '如何使用 Imm-Agent'}<IconButton aria-label="关闭说明" onClick={() => setDialog(null)} sx={{ position: 'absolute', right: 12, top: 12 }}><CloseRoundedIcon /></IconButton></DialogTitle>
        <DialogContent className="guide-content">
          {dialog === 'sources' ? <><p>来源卡片包含标题、发布机构、资料日期和支持的结论。展开后可查看原文片段、位置和原始链接。</p><p>资料撤回后，来源接口会停止展示该片段。</p></> : <><p>选择科普问答、疗法比较或研究进展，点击示例问题，或在底部输入框编写问题。疗法比较可以先选择两个对象与比较维度。</p><p>问题与回答按顺序显示，来源在每条回答下方。失败后草稿会保留，可点击重试。新建会话会使用独立凭据，刷新页面会清除本页记录。</p><p>回答以已审核资料为依据，不提供个体化诊断、治疗选择或剂量建议。</p></>}
        </DialogContent>
      </Dialog>
    </div>
  )
}

export default App
