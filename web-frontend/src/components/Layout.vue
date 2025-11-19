<template>
  <a-layout style="min-height: 100vh; background: transparent; width: 100%; max-width: 100%;">
    <a-layout-header class="header">
      <div class="logo">
        <span class="logo-text">📈 Red-Stock</span>
      </div>
      <a-menu
        :selectedKeys="selectedKeys"
        mode="horizontal"
        theme="light"
        class="nav-menu"
        @click="handleMenuClick"
        @update:selectedKeys="handleSelectedKeysChange"
        :forceSubMenuRender="true"
        :triggerSubMenuAction="'hover'"
      >
        <a-menu-item key="home">
          <span>🏠 首页</span>
        </a-menu-item>
        <a-sub-menu key="stocks">
          <template #title>📊 A股股票</template>
          <a-menu-item key="stocks-all">
            <span>📈 全部股票</span>
          </a-menu-item>
          <a-menu-item key="stocks-ipo">
            <span>🆕 IPO新股</span>
          </a-menu-item>
          <a-menu-item key="stocks-sector">
            <span>📊 板块数据</span>
          </a-menu-item>
          <a-menu-item key="stocks-index">
            <span>📉 指数</span>
          </a-menu-item>
        </a-sub-menu>
        <a-sub-menu key="strategy">
          <template #title>📈 策略</template>
          <a-menu-item key="strategy-selection">
            <span>💰 选股页面</span>
          </a-menu-item>
        </a-sub-menu>
        <a-menu-item key="global">
          <span>🌍 外盘跟踪</span>
        </a-menu-item>
        <a-menu-item key="bigplayers">
          <span>👥 大佬追踪</span>
        </a-menu-item>
        <a-menu-item key="datamap">
          <span>🗺️ 数据地图</span>
        </a-menu-item>
      </a-menu>
      <div class="user-actions">
        <template v-if="userStore.isLoggedIn">
          <a-dropdown>
            <template #overlay>
              <a-menu>
                <a-menu-item>
                  <div class="user-info">
                    <a-avatar :src="userStore.userAvatar" :size="24" style="margin-right: 8px;">
                      {{ userStore.userNickname.charAt(0) }}
                    </a-avatar>
                    <span>{{ userStore.userNickname }}</span>
                  </div>
                </a-menu-item>
                <a-menu-divider />
                <a-menu-item @click="handleLogout">
                  <span>退出登录</span>
                </a-menu-item>
              </a-menu>
            </template>
            <a-button type="text" class="user-btn">
              <a-avatar :src="userStore.userAvatar" :size="24" style="margin-right: 8px;">
                {{ userStore.userNickname.charAt(0) }}
              </a-avatar>
              <span>{{ userStore.userNickname }}</span>
            </a-button>
          </a-dropdown>
        </template>
        <template v-else>
          <a-button type="primary" @click="handleLogin">
            登录
          </a-button>
        </template>
      </div>
    </a-layout-header>

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
    <a-layout-content class="content">
      <router-view :key="route?.fullPath || route?.path || ''" />
    </a-layout-content>
    <a-layout-footer class="footer">
      <div class="footer-content">
        <span>Red-Stock © 2024</span>
        <span class="divider">|</span>
        <span>数据来源：Tushare</span>
      </div>
    </a-layout-footer>
  </a-layout>
</template>

<script setup>
import { ref, watch, onUnmounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useUserStore } from '../stores/user'
import { authAPI } from '../api'
import { message } from 'ant-design-vue'

const router = useRouter()
const route = useRoute()
const userStore = useUserStore()

// 登录对话框相关状态
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

// 处理登录按钮点击
const handleLogin = async () => {
  try {
    loginModalVisible.value = true
    statusMessage.value = '正在生成二维码...'
    qrCodeUrl.value = ''
    
    const result = await authAPI.getWechatLoginUrl()
    if (result.code === 0 && result.data) {
      const { qr_url, state } = result.data
      loginState.value = state
      statusMessage.value = '请使用微信扫码登录'
      
      // 生成二维码
      try {
        const qrDataUrl = await generateQRCode(qr_url)
        qrCodeUrl.value = qrDataUrl
        
        // 开始轮询检查登录状态
        if (pollTimer) {
          clearInterval(pollTimer)
        }
        pollTimer = setInterval(pollLoginStatus, 2000) // 每2秒检查一次
      } catch (error) {
        console.error('生成二维码失败:', error)
        message.error('生成二维码失败，请稍后重试')
        loginModalVisible.value = false
      }
    } else {
      message.error('获取登录链接失败')
      loginModalVisible.value = false
    }
  } catch (error) {
    console.error('微信登录失败:', error)
    message.error('登录失败，请稍后重试')
    loginModalVisible.value = false
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

const handleLogout = async () => {
  await userStore.logout()
  router.push('/')
}

// 组件卸载时清除定时器
onUnmounted(() => {
  if (pollTimer) {
    clearInterval(pollTimer)
    pollTimer = null
  }
})

// 路由名称到菜单key的映射
const getRouteKey = (routeName, query) => {
  const nameMap = {
    'Dashboard': 'home',
    'StockList': 'stocks-all',
    'IPOStocks': 'stocks-ipo',
    'SectorData': 'stocks-sector',
    'IndexList': 'stocks-index',
    'StrategySelection': 'strategy-selection',
    'GlobalMarket': 'global',
    'BigPlayerTracking': 'bigplayers',
    'DataMap': 'datamap'
  }
  return nameMap[routeName] || 'home'
}

// 初始化选中状态
const selectedKeys = ref([getRouteKey(route?.name, route?.query)])

// 路由映射：菜单key -> 路由配置
const routeMap = {
  'home': { name: 'Dashboard' },
  'stocks-all': { name: 'StockList' },
  'stocks-ipo': { name: 'IPOStocks' },
  'stocks-sector': { name: 'SectorData' },
  'stocks-index': { name: 'IndexList' },
  'strategy-selection': { name: 'StrategySelection' },
  'global': { name: 'GlobalMarket' },
  'bigplayers': { name: 'BigPlayerTracking' },
  'datamap': { name: 'DataMap' }
}

const navigateToRoute = (key) => {
  // 如果点击的是子菜单的父项，不处理
  if (key === 'strategy' || key === 'stocks') {
    return
  }
  
  const routeConfig = routeMap[key]
  if (!routeConfig) {
    console.warn('Unknown menu key:', key)
    return
  }
  
  // 获取当前路由名称和查询参数
  const currentRouteName = route?.name
  const currentQuery = route?.query || {}
  
  // 检查是否已经在目标路由（包括查询参数）
  const isSameRoute = currentRouteName === routeConfig.name && 
    JSON.stringify(currentQuery) === JSON.stringify(routeConfig.query || {})
  
  // 如果已经在目标路由，强制刷新
  if (isSameRoute) {
    console.log('Already on target route, forcing refresh')
    // 强制刷新当前路由
    router.replace({ ...routeConfig, query: { ...(routeConfig.query || {}), _t: Date.now() } })
    return
  }
  
  console.log('Navigating from', currentRouteName, 'to', routeConfig.name, 'with query:', routeConfig.query)
  
  // 使用路由名称进行导航（更可靠）
  router.push(routeConfig).then(() => {
    console.log('✓ Navigation successful to', routeConfig.name)
    // 确保选中状态正确（创建新数组）
    selectedKeys.value = [key]
  }).catch(err => {
    console.error('✗ Navigation error:', err)
    // 导航失败时恢复选中状态（创建新数组）
    const currentKey = getRouteKey(route?.name, route?.query)
    selectedKeys.value = [currentKey]
  })
}

const handleSelectedKeysChange = (keys) => {
  // 当菜单选中状态改变时，更新 selectedKeys
  if (Array.isArray(keys) && keys.length > 0) {
    selectedKeys.value = [...keys]
  }
}

const handleMenuClick = (e) => {
  const key = e?.key
  console.log('Menu clicked:', key, 'Event:', e)
  
  // 忽略子菜单父项的点击
  if (!key || key === 'strategy' || key === 'stocks') {
    return
  }
  
  // 执行路由跳转（选中状态由 handleSelectedKeysChange 处理）
  navigateToRoute(key)
}

// 监听路由变化，更新选中的菜单项
watch(() => [route?.name, route?.query], ([newName, newQuery]) => {
  if (newName) {
    const key = getRouteKey(newName, newQuery)
    // 创建新的数组，确保是可扩展的
    selectedKeys.value = [key]
    console.log('Route changed to:', newName, 'Query:', newQuery, 'Menu key:', key)
  }
}, { immediate: true })
</script>

<style scoped>
.header {
  background: #fff;
  border-bottom: 1px solid #f0f0f0;
  padding: 0 16px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
  position: sticky;
  top: 0;
  z-index: 1001;
  height: 48px;
  line-height: 48px;
  pointer-events: auto;
}

.user-actions {
  margin-left: 16px;
  display: flex;
  align-items: center;
}

.user-btn {
  display: flex;
  align-items: center;
  padding: 0 8px;
  height: 32px;
}

.user-info {
  display: flex;
  align-items: center;
  padding: 4px 0;
}

.logo {
  margin-right: 32px;
}

.logo-text {
  font-size: 18px;
  font-weight: 700;
  color: #1890ff;
  letter-spacing: 0.5px;
}

.nav-menu {
  flex: 1;
  border-bottom: none !important;
  line-height: 48px;
}

/* 确保菜单项可点击 */
.nav-menu :deep(.ant-menu-item),
.nav-menu :deep(.ant-menu-submenu-title) {
  cursor: pointer;
  user-select: none;
  pointer-events: auto;
  position: relative;
  z-index: 1002;
}

.nav-menu :deep(.ant-menu-item:hover),
.nav-menu :deep(.ant-menu-submenu-title:hover) {
  color: #1890ff;
}

/* 确保菜单始终可点击，不受其他元素影响 */
.nav-menu {
  pointer-events: auto;
  position: relative;
  z-index: 1002;
}

.content {
  padding: 16px 0;
  background: #f0f2f5;
  min-height: calc(100vh - 48px - 60px);
  width: 100%;
  max-width: 100%;
}

.footer {
  background: #fff;
  border-top: 1px solid #f0f0f0;
  padding: 12px;
  text-align: center;
  height: 60px;
}

.footer-content {
  color: rgba(0, 0, 0, 0.65);
  font-size: 14px;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 12px;
}

.divider {
  color: rgba(0, 0, 0, 0.25);
}

@media (max-width: 768px) {
  .header {
    padding: 0 16px;
  }
  
  .logo {
    margin-right: 16px;
  }
  
  .logo-text {
    font-size: 18px;
  }
  
  .content {
    padding: 16px;
  }
}

/* 路由过渡动画 */
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.2s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
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
