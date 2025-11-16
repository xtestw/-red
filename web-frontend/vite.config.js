import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import { resolve } from 'path'

export default defineConfig({
  plugins: [vue()],
  resolve: {
    alias: {
      '@': resolve(__dirname, 'src')
    }
  },
  server: {
    port: 3002,  // 修改为3000端口
    host: true,  // 允许外部访问
    proxy: {
      '/api': {
        target: 'http://localhost:5001',
        changeOrigin: true,
      }
    }
  },
  // 生产环境构建配置
  base: '/',  // 如果部署在子路径，修改这里
  build: {
    outDir: 'dist',
    assetsDir: 'assets',
    sourcemap: false
  }
})

