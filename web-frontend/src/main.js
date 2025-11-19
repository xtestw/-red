import { createApp } from 'vue'
import { createPinia } from 'pinia'
import Antd from 'ant-design-vue'
import 'ant-design-vue/dist/reset.css'
import App from './App.vue'
import router from './router'
import './style.css'
import { useUserStore } from './stores/user'

const app = createApp(App)
const pinia = createPinia()

app.use(pinia)
app.use(router)
app.use(Antd)

// 错误处理
app.config.errorHandler = (err, instance, info) => {
  console.error('Vue Error:', err)
  console.error('Error Info:', info)
}

// 初始化用户认证
const initAuth = async () => {
  const userStore = useUserStore()
  // 检查URL中是否有微信回调的code
  const urlParams = new URLSearchParams(window.location.search)
  const code = urlParams.get('code')
  const state = urlParams.get('state')
  
  if (code) {
    // 处理微信登录回调
    try {
      // 这里应该调用后端API处理回调，但由于是前端回调，实际应该由后端重定向处理
      // 前端只需要检查是否有token返回
      await userStore.fetchUserInfo()
    } catch (error) {
      console.error('处理登录回调失败:', error)
    }
  } else {
    // 正常初始化，检查本地token
    await userStore.initAuth()
  }
}

// 挂载应用
try {
  app.mount('#app')
  console.log('Vue app mounted successfully')
  // 初始化认证
  initAuth()
} catch (error) {
  console.error('Failed to mount Vue app:', error)
}

