import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  server: {
    port: 3000,
    host: true,
    proxy: {
      '/api': {
        target: 'http://localhost:8080',
        changeOrigin: true,
        secure: false,
        // Fix the incorrect /users/me endpoint the frontend uses
        rewrite: (path) => {
          return path
            .replace('/api/v1/users/me/', '/api/v1/users/users/me/')
            .replace('/api/v1/users/me', '/api/v1/users/users/me')
        }
      }
    }
  },
  build: {
    outDir: '../apps/static/frontend',
    emptyOutDir: true,
  }
})

