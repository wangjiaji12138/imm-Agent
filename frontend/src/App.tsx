import { useEffect, useState } from 'react'
import AutoAwesomeOutlinedIcon from '@mui/icons-material/AutoAwesomeOutlined'
import HealthAndSafetyOutlinedIcon from '@mui/icons-material/HealthAndSafetyOutlined'
import SendRoundedIcon from '@mui/icons-material/SendRounded'
import {
  Alert,
  AppBar,
  Box,
  Button,
  Chip,
  Container,
  Paper,
  Stack,
  TextField,
  Toolbar,
  Typography,
} from '@mui/material'

type ServiceStatus = 'checking' | 'online' | 'offline'

interface HealthResponse {
  status: 'ok'
  service: 'imm-agent'
}

function App() {
  const [serviceStatus, setServiceStatus] =
    useState<ServiceStatus>('checking')

  useEffect(() => {
    const controller = new AbortController()

    async function checkHealth() {
      try {
        const response = await fetch('/health', { signal: controller.signal })
        if (!response.ok) {
          throw new Error('Health request failed')
        }

        const health = (await response.json()) as HealthResponse
        setServiceStatus(
          health.status === 'ok' && health.service === 'imm-agent'
            ? 'online'
            : 'offline',
        )
      } catch (error) {
        if (!(error instanceof DOMException && error.name === 'AbortError')) {
          setServiceStatus('offline')
        }
      }
    }

    void checkHealth()
    return () => controller.abort()
  }, [])

  const serviceOnline = serviceStatus === 'online'
  const statusLabel =
    serviceStatus === 'checking'
      ? '正在检查服务'
      : serviceOnline
        ? '服务正常'
        : '服务未连接'

  return (
    <Box sx={{ minHeight: '100vh', bgcolor: 'background.default' }}>
      <AppBar
        position="static"
        color="transparent"
        elevation={0}
        sx={{ borderBottom: 1, borderColor: 'divider' }}
      >
        <Toolbar sx={{ minHeight: 72 }}>
          <AutoAwesomeOutlinedIcon color="primary" sx={{ mr: 1.5 }} />
          <Typography variant="h6" component="div" sx={{ flexGrow: 1 }}>
            Imm-Agent
          </Typography>
          <Chip
            icon={<HealthAndSafetyOutlinedIcon />}
            label={statusLabel}
            color={serviceOnline ? 'success' : 'default'}
            variant="outlined"
          />
        </Toolbar>
      </AppBar>

      <Container maxWidth="md" sx={{ py: { xs: 5, md: 9 } }}>
        <Stack spacing={4} sx={{ alignItems: 'center' }}>
          <Stack
            spacing={1.5}
            sx={{ textAlign: 'center', alignItems: 'center' }}
          >
            <Typography
              component="h1"
              variant="h2"
              sx={{ fontWeight: 700, letterSpacing: '-0.04em' }}
            >
              读懂癌症免疫疗法
            </Typography>
            <Typography
              color="text.secondary"
              sx={{ maxWidth: 620, fontSize: { xs: '1rem', md: '1.125rem' } }}
            >
              基于已审核资料解释概念、比较疗法并展示原文来源。
            </Typography>
          </Stack>

          <Paper
            elevation={0}
            sx={{
              width: '100%',
              p: { xs: 2.5, sm: 4 },
              border: 1,
              borderColor: 'divider',
              borderRadius: 4,
            }}
          >
            <Stack spacing={2.5}>
              <Box>
                <Typography variant="h5" component="h2" gutterBottom>
                  向 Imm-Agent 提问
                </Typography>
                <Typography color="text.secondary">
                  问答功能正在建设中，当前页面用于确认前后端连接状态。
                </Typography>
              </Box>

              <TextField
                disabled
                fullWidth
                multiline
                minRows={3}
                label="输入关于癌症免疫疗法的问题"
                placeholder="例如：PD-1 和 PD-L1 有什么关系？"
              />

              <Stack direction={{ xs: 'column', sm: 'row' }} spacing={2}>
                <Button
                  disabled
                  variant="contained"
                  endIcon={<SendRoundedIcon />}
                  sx={{ px: 3 }}
                >
                  发送问题
                </Button>
                <Typography
                  variant="body2"
                  color="text.secondary"
                  sx={{ alignSelf: 'center' }}
                >
                  本服务只提供科普信息，不提供诊断或个体化治疗建议。
                </Typography>
              </Stack>
            </Stack>
          </Paper>

          {serviceStatus === 'offline' && (
            <Alert severity="warning" sx={{ width: '100%' }}>
              无法连接后端服务，请确认 Docker 中的 backend 服务正在运行。
            </Alert>
          )}
        </Stack>
      </Container>
    </Box>
  )
}

export default App
