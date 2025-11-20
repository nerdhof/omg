import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'

export default defineConfig({
  plugins: [vue()],
  base: process.env.GITHUB_PAGES === 'true' ? '/omg/' : '/',
  server: {
    port: 5173,
    proxy: {
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true
      }
    }
  },
  define: {
    __BASE_PATH__: JSON.stringify(process.env.GITHUB_PAGES === 'true' ? '/omg/' : '/')
  }
})

