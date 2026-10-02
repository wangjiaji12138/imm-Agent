import react from '@vitejs/plugin-react'
import { defineConfig } from 'vitest/config'

// https://vite.dev/config/
export default defineConfig({
  plugins: [react()],
  server: {
    host: '0.0.0.0',
    port: 5173,
    strictPort: true,
    proxy: {
      '/health': 'http://backend:8000',
      '/api': 'http://backend:8000',
    },
  },
  test: { environment: 'jsdom' },
})
