import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { authAPI } from '../api'
import { message } from 'ant-design-vue'

export const useUserStore = defineStore('user', () => {
  // 状态
  const user = ref(null)
  const token = ref(localStorage.getItem('token') || '')
  const refreshToken = ref(localStorage.getItem('refreshToken') || '')
  const loading = ref(false)

  // 计算属性
  const isLoggedIn = computed(() => !!token.value && !!user.value)
  const userNickname = computed(() => user.value?.nickname || '未登录')
  const userAvatar = computed(() => user.value?.avatar || '')

  // 方法
  const setToken = (newToken, newRefreshToken) => {
    token.value = newToken
    refreshToken.value = newRefreshToken
    if (newToken) {
      localStorage.setItem('token', newToken)
    } else {
      localStorage.removeItem('token')
    }
    if (newRefreshToken) {
      localStorage.setItem('refreshToken', newRefreshToken)
    } else {
      localStorage.removeItem('refreshToken')
    }
  }

  const setUser = (userData) => {
    user.value = userData
  }

  const login = async (tokenData, userData) => {
    setToken(tokenData.token, tokenData.refresh_token)
    setUser(userData)
    message.success('登录成功')
  }

  const logout = async () => {
    try {
      if (token.value) {
        await authAPI.logout()
      }
    } catch (error) {
      console.error('退出登录失败:', error)
    } finally {
      setToken('', '')
      setUser(null)
      message.success('已退出登录')
    }
  }

  const fetchUserInfo = async () => {
    if (!token.value) {
      return
    }
    
    try {
      loading.value = true
      const result = await authAPI.getUserInfo()
      if (result.code === 0) {
        setUser(result.data)
      } else {
        // token可能已过期，清除
        setToken('', '')
        setUser(null)
      }
    } catch (error) {
      console.error('获取用户信息失败:', error)
      // token可能已过期，清除
      setToken('', '')
      setUser(null)
    } finally {
      loading.value = false
    }
  }

  const initAuth = async () => {
    // 如果本地有token，尝试获取用户信息
    if (token.value) {
      await fetchUserInfo()
    }
  }

  const wechatLogin = async () => {
    try {
      loading.value = true
      const result = await authAPI.getWechatLoginUrl()
      if (result.code === 0 && result.data?.auth_url) {
        // 跳转到微信授权页面
        window.location.href = result.data.auth_url
      } else {
        throw new Error('获取登录链接失败')
      }
    } catch (error) {
      console.error('微信登录失败:', error)
      throw error
    } finally {
      loading.value = false
    }
  }

  return {
    // 状态
    user,
    token,
    refreshToken,
    loading,
    // 计算属性
    isLoggedIn,
    userNickname,
    userAvatar,
    // 方法
    login,
    logout,
    fetchUserInfo,
    initAuth,
    wechatLogin,
    setToken,
    setUser
  }
})

