<template>
  <div class="auth-callback-container">
    <a-spin :spinning="loading" tip="正在登录...">
      <div class="callback-content">
        <h2 v-if="loading">正在处理登录...</h2>
        <h2 v-else-if="error">{{ error }}</h2>
        <h2 v-else>登录成功！</h2>
      </div>
    </a-spin>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useUserStore } from '../stores/user'
import { message } from 'ant-design-vue'

const router = useRouter()
const route = useRoute()
const userStore = useUserStore()
const loading = ref(true)
const error = ref('')

onMounted(async () => {
  try {
    const token = route.query.token
    const refreshToken = route.query.refresh_token
    
    if (!token) {
      error.value = '缺少登录凭证'
      loading.value = false
      setTimeout(() => {
        router.push('/login')
      }, 2000)
      return
    }
    
    // 保存token
    userStore.setToken(token, refreshToken)
    
    // 获取用户信息
    await userStore.fetchUserInfo()
    
    if (userStore.isLoggedIn) {
      message.success('登录成功')
      // 清除URL中的token参数
      router.replace('/')
    } else {
      error.value = '登录失败，请重试'
      setTimeout(() => {
        router.push('/login')
      }, 2000)
    }
  } catch (err) {
    console.error('处理登录回调失败:', err)
    error.value = '登录失败，请重试'
    setTimeout(() => {
      router.push('/login')
    }, 2000)
  } finally {
    loading.value = false
  }
})
</script>

<style scoped>
.auth-callback-container {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #f0f2f5;
}

.callback-content {
  text-align: center;
  padding: 40px;
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.callback-content h2 {
  margin: 0;
  color: #1890ff;
}
</style>

