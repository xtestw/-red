import { createRouter, createWebHistory } from 'vue-router'
import Layout from '../components/Layout.vue'
import Dashboard from '../views/Dashboard.vue'
import StockList from '../views/StockList.vue'
import IPOStocks from '../views/IPOStocks.vue'
import SectorData from '../views/SectorData.vue'
import IndexList from '../views/IndexList.vue'
import GlobalMarket from '../views/GlobalMarket.vue'
import BigPlayerTracking from '../views/BigPlayerTracking.vue'
import StrategySelection from '../views/StrategySelection.vue'
import DataMap from '../views/DataMap.vue'
import Login from '../views/Login.vue'
import AuthCallback from '../views/AuthCallback.vue'

const routes = [
  {
    path: '/login',
    name: 'Login',
    component: Login
  },
  {
    path: '/auth/callback',
    name: 'AuthCallback',
    component: AuthCallback
  },
  {
    path: '/',
    component: Layout,
    children: [
      {
        path: '',
        name: 'Dashboard',
        component: Dashboard
      },
      {
        path: 'stocks',
        name: 'StockList',
        component: StockList
      },
      {
        path: 'ipo',
        name: 'IPOStocks',
        component: IPOStocks
      },
      {
        path: 'sector',
        name: 'SectorData',
        component: SectorData
      },
      {
        path: 'index',
        name: 'IndexList',
        component: IndexList
      },
      {
        path: 'strategy/selection',
        name: 'StrategySelection',
        component: StrategySelection
      },
      {
        path: 'global',
        name: 'GlobalMarket',
        component: GlobalMarket
      },
      {
        path: 'bigplayers',
        name: 'BigPlayerTracking',
        component: BigPlayerTracking
      },
      {
        path: 'datamap',
        name: 'DataMap',
        component: DataMap
      }
    ]
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

// 添加路由导航守卫用于调试
router.beforeEach((to, from, next) => {
  console.log('Router: Navigating from', from.path, 'to', to.path, 'name:', to.name)
  next()
})

router.afterEach((to, from) => {
  console.log('Router: Navigation completed to', to.path, 'name:', to.name)
})

export default router
