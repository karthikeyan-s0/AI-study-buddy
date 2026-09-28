import react from '@vitejs/plugin-react'
import { defineConfig } from 'vite'

// https://vite.dev/config/
export default defineConfig({
  plugins: [react()],
  server: {
    host: true,
    port: 5173,
    allowedHosts: true,
    proxy: {
      '/auth': 'http://localhost:8000',
      '/profile': 'http://localhost:8000',
      '/subjects': 'http://localhost:8000',
      '/topics': 'http://localhost:8000',
      '/study-plans': 'http://localhost:8000',
      '/ai': 'http://localhost:8000',
      '/quizzes': 'http://localhost:8000',
      '/progress': 'http://localhost:8000',
      '/analytics': 'http://localhost:8000',
      '/health': 'http://localhost:8000',
    }
  }
})
