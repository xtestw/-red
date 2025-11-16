<template>
  <a-layout style="min-height: 100vh; background: transparent;">
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
        @select="handleMenuSelect"
        :forceSubMenuRender="true"
        :triggerSubMenuAction="'click'"
      >
        <a-menu-item key="home">
          <template #icon><HomeOutlined /></template>
          <span>首页</span>
        </a-menu-item>
        <a-menu-item key="stocks">
          <template #icon><StockOutlined /></template>
          <span>A股股票</span>
        </a-menu-item>
        <a-sub-menu key="strategy">
          <template #icon><AppstoreOutlined /></template>
          <template #title>策略</template>
          <a-menu-item key="strategy-selection">
            <template #icon><FundOutlined /></template>
            <span>选股页面</span>
          </a-menu-item>
        </a-sub-menu>
        <a-menu-item key="global">
          <template #icon><GlobalOutlined /></template>
          <span>外盘跟踪</span>
        </a-menu-item>
        <a-menu-item key="bigplayers">
          <template #icon><TeamOutlined /></template>
          <span>大佬追踪</span>
        </a-menu-item>
      </a-menu>
    </a-layout-header>
    <a-layout-content class="content">
      <router-view :key="route.fullPath" />
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
import { ref, watch } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import {
  HomeOutlined,
  StockOutlined,
  GlobalOutlined,
  TeamOutlined,
  AppstoreOutlined,
  FundOutlined
} from '@ant-design/icons-vue'

const router = useRouter()
const route = useRoute()
const selectedKeys = ref([getRouteKey(route.name)])

const routeMap = {
  home: '/',
  stocks: '/stocks',
  'strategy-selection': '/strategy/selection',
  global: '/global',
  bigplayers: '/bigplayers'
}

const navigateToRoute = (key) => {
  // 如果点击的是子菜单的父项，不处理
  if (key === 'strategy') {
    return
  }
  
  const targetRoute = routeMap[key]
  if (!targetRoute) {
    console.warn('Unknown menu key:', key)
    return
  }
  
  // 获取当前完整路径（包括父路径）
  const currentFullPath = route.fullPath || route.path || '/'
  const currentPath = route.path || '/'
  
  // 规范化路径进行比较
  const normalizedCurrent = currentPath.replace(/\/$/, '') || '/'
  const normalizedTarget = targetRoute.replace(/\/$/, '') || '/'
  
  console.log('=== Navigation Debug ===')
  console.log('Menu key:', key)
  console.log('Target route:', targetRoute)
  console.log('Current path:', currentPath)
  console.log('Current fullPath:', currentFullPath)
  console.log('Normalized current:', normalizedCurrent)
  console.log('Normalized target:', normalizedTarget)
  
  // 如果已经在目标路由，不重复导航
  if (normalizedCurrent === normalizedTarget) {
    console.log('Already on target route, skipping navigation')
    return
  }
  
  console.log('Navigating from', normalizedCurrent, 'to', normalizedTarget)
  
  // 使用 router.push 进行导航
  router.push(targetRoute).then(() => {
    console.log('✓ Navigation successful')
    console.log('New route path:', route.path)
    console.log('New route fullPath:', route.fullPath)
    console.log('New route name:', route.name)
    
    // 验证路径是否真的改变了
    if (route.path === normalizedTarget) {
      console.log('✓ Route path updated correctly')
    } else {
      console.warn('⚠ Route path may not have updated correctly')
      console.warn('Expected:', normalizedTarget, 'Got:', route.path)
    }
  }).catch(err => {
    console.error('✗ Navigation error:', err)
  })
}

const handleMenuClick = (e) => {
  const key = e?.key
  console.log('Menu clicked:', key, 'Full event:', e)
  if (key && key !== 'strategy') {
    navigateToRoute(key)
  }
}

const handleMenuSelect = (info) => {
  const key = info?.key
  console.log('Menu selected:', key, 'Full info:', info)
  if (key && key !== 'strategy') {
    navigateToRoute(key)
  }
}

const getRouteKey = (routeName) => {
  const nameMap = {
    'Dashboard': 'home',
    'StockList': 'stocks',
    'StrategySelection': 'strategy-selection',
    'GlobalMarket': 'global',
    'BigPlayerTracking': 'bigplayers'
  }
  return nameMap[routeName] || 'home'
}

watch(() => route.name, (newName) => {
  const key = getRouteKey(newName)
  selectedKeys.value = [key]
  console.log('Route changed to:', newName, 'Menu key:', key)
}, { immediate: true })

// 同时监听路径变化
watch(() => route.path, (newPath) => {
  console.log('Route path changed to:', newPath)
  console.log('Route fullPath:', route.fullPath)
  console.log('Route name:', route.name)
}, { immediate: true })

// 监听完整路径变化（包括查询参数和哈希）
watch(() => route.fullPath, (newFullPath) => {
  console.log('Route fullPath changed to:', newFullPath)
}, { immediate: true })
</script>

<style scoped>
.header {
  background: #fff;
  border-bottom: 1px solid #f0f0f0;
  padding: 0 32px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
  position: sticky;
  top: 0;
  z-index: 1000;
}

.logo {
  margin-right: 48px;
}

.logo-text {
  font-size: 22px;
  font-weight: 700;
  color: #1890ff;
  letter-spacing: 0.5px;
}

.nav-menu {
  flex: 1;
  border-bottom: none !important;
  line-height: 64px;
}

/* 确保菜单项可点击 */
.nav-menu :deep(.ant-menu-item),
.nav-menu :deep(.ant-menu-submenu-title) {
  cursor: pointer;
  user-select: none;
}

.nav-menu :deep(.ant-menu-item:hover),
.nav-menu :deep(.ant-menu-submenu-title:hover) {
  color: #1890ff;
}

.content {
  padding: 32px 24px;
  background: #f0f2f5;
  min-height: calc(100vh - 64px - 80px);
}

.footer {
  background: #fff;
  border-top: 1px solid #f0f0f0;
  padding: 24px;
  text-align: center;
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
</style>
