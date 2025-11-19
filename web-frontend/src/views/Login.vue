<template>
  <div class="login-container">
    <div class="login-box">
      <div class="login-header">
        <h1>📈 Red-Stock</h1>
        <p>专业的A股数据分析平台</p>
      </div>
      
      <div class="login-content">
        <a-button 
          type="primary" 
          size="large" 
          block 
          :loading="loading"
          @click="handleWechatLogin"
          class="wechat-login-btn"
        >
          <template #icon>
            <span style="font-size: 20px;">💬</span>
          </template>
          微信登录
        </a-button>
        
        <div class="login-tips">
          <p>使用微信登录，享受个性化服务</p>
          <p>登录后可收藏股票、查看个人数据</p>
        </div>
      </div>
    </div>

    <!-- 登录对话框 -->
    <a-modal
      v-model:open="loginModalVisible"
      title="微信扫码登录"
      :footer="null"
      :maskClosable="false"
      :closable="true"
      width="400px"
      @cancel="handleModalCancel"
    >
      <div class="qr-login-content">
        <div v-if="qrCodeUrl" class="qr-code-container">
          <div class="qr-code-wrapper">
            <img :src="qrCodeUrl" alt="微信登录二维码" class="qr-code-image" />
          </div>
          <p class="qr-tips">{{ statusMessage }}</p>
        </div>
        <div v-else class="loading-container">
          <a-spin size="large" />
          <p>正在生成二维码...</p>
        </div>
      </div>
    </a-modal>
  </div>
</template>

<script setup>
import { ref, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import { authAPI } from '../api'
import { message } from 'ant-design-vue'
import { useUserStore } from '../stores/user'

const router = useRouter()
const userStore = useUserStore()
const loading = ref(false)
const loginModalVisible = ref(false)
const qrCodeUrl = ref('')
const loginState = ref('')
const statusMessage = ref('请使用微信扫码登录')
let pollTimer = null

// 生成二维码（使用在线API）
const generateQRCode = async (url) => {
  try {
    // 使用在线二维码生成服务
    const encodedUrl = encodeURIComponent(url)
    // 使用 qr-server.com 的API生成二维码
    const qrApiUrl = `https://api.qrserver.com/v1/create-qr-code/?size=256x256&data=${encodedUrl}`
    return qrApiUrl
  } catch (error) {
    console.error('生成二维码失败:', error)
    throw error
  }
}

// 轮询检查登录状态
const pollLoginStatus = async () => {
  if (!loginState.value) return
  
  try {
    const result = await authAPI.checkLoginStatus(loginState.value)
    if (result.code === 0 && result.data) {
      const { status, token, refresh_token, message: msg } = result.data
      
      if (status === 'success' && token) {
        // 登录成功
        statusMessage.value = '登录成功！'
        clearInterval(pollTimer)
        pollTimer = null
        
        // 保存token并获取用户信息
        await userStore.login({ token, refresh_token: refresh_token }, null)
        await userStore.fetchUserInfo()
        
        // 关闭对话框
        loginModalVisible.value = false
        qrCodeUrl.value = ''
        loginState.value = ''
        
        // 跳转到首页
        router.push('/')
        message.success('登录成功')
      } else if (status === 'expired') {
        // 过期
        statusMessage.value = msg || '二维码已过期，请重新扫码'
        clearInterval(pollTimer)
        pollTimer = null
        qrCodeUrl.value = ''
        loginState.value = ''
      } else {
        // 更新状态消息
        statusMessage.value = msg || '等待扫码'
      }
    }
  } catch (error) {
    console.error('检查登录状态失败:', error)
  }
}

// 处理微信登录
const handleWechatLogin = async () => {
  try {
    loading.value = true
    const result = await authAPI.getWechatLoginUrl()
    if (result.code === 0 && result.data) {
      const { qr_url, state } = result.data
      loginState.value = state
      statusMessage.value = '请使用微信扫码登录'
      
      // 生成二维码
      try {
        const qrDataUrl = await generateQRCode(qr_url)
        qrCodeUrl.value = qrDataUrl
        loginModalVisible.value = true
        
        // 开始轮询检查登录状态
        if (pollTimer) {
          clearInterval(pollTimer)
        }
        pollTimer = setInterval(pollLoginStatus, 2000) // 每2秒检查一次
      } catch (error) {
        console.error('生成二维码失败:', error)
        message.error('生成二维码失败，请稍后重试')
      }
    } else {
      message.error('获取登录链接失败')
    }
  } catch (error) {
    console.error('微信登录失败:', error)
    message.error('登录失败，请稍后重试')
  } finally {
    loading.value = false
  }
}

// 处理对话框关闭
const handleModalCancel = () => {
  // 清除轮询
  if (pollTimer) {
    clearInterval(pollTimer)
    pollTimer = null
  }
  qrCodeUrl.value = ''
  loginState.value = ''
  statusMessage.value = '请使用微信扫码登录'
}

// 组件卸载时清除定时器
onUnmounted(() => {
  if (pollTimer) {
    clearInterval(pollTimer)
    pollTimer = null
  }
})
</script>

<style scoped>
.login-container {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  padding: 20px;
}

.login-box {
  background: white;
  border-radius: 12px;
  box-shadow: 0 10px 40px rgba(0, 0, 0, 0.1);
  padding: 40px;
  width: 100%;
  max-width: 400px;
}

.login-header {
  text-align: center;
  margin-bottom: 40px;
}

.login-header h1 {
  font-size: 32px;
  margin: 0 0 10px 0;
  color: #1890ff;
}

.login-header p {
  color: #666;
  font-size: 14px;
  margin: 0;
}

.login-content {
  margin-top: 30px;
}

.wechat-login-btn {
  height: 50px;
  font-size: 16px;
  border-radius: 6px;
}

.login-tips {
  margin-top: 30px;
  text-align: center;
  color: #999;
  font-size: 13px;
}

.login-tips p {
  margin: 8px 0;
}

.qr-login-content {
  text-align: center;
  padding: 20px 0;
}

.qr-code-container {
  display: flex;
  flex-direction: column;
  align-items: center;
}

.qr-code-wrapper {
  padding: 20px;
  background: #fff;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  margin-bottom: 20px;
}

.qr-code-image {
  width: 256px;
  height: 256px;
  display: block;
}

.qr-tips {
  color: #666;
  font-size: 14px;
  margin: 0;
}

.loading-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 40px 0;
}

.loading-container p {
  margin-top: 16px;
  color: #666;
}
</style>

