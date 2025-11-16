/**
 * API请求封装
 * 使用axios统一处理请求
 */
import axios from 'axios'
import { message } from 'ant-design-vue'

// 创建axios实例
const api = axios.create({
  baseURL: import.meta.env.VITE_API_BASE || '/api',
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json'
  }
})

// 请求拦截器
api.interceptors.request.use(
  config => {
    // 可以在这里添加token等
    return config
  },
  error => {
    return Promise.reject(error)
  }
)

// 响应拦截器
api.interceptors.response.use(
  response => {
    const res = response.data
    if (res.code === 0) {
      return res
    } else {
      // 不显示错误消息，让组件自己处理
      console.warn('API返回错误:', res.message || '请求失败')
      return Promise.reject(new Error(res.message || '请求失败'))
    }
  },
  error => {
    // 网络错误或API不存在时不显示错误消息
    const msg = error.response?.data?.message || error.message || '网络错误'
    if (error.response?.status === 404) {
      console.warn('API端点不存在:', error.config?.url)
    } else {
      console.error('API请求失败:', msg)
    }
    return Promise.reject(error)
  }
)

/**
 * 股票相关API
 */
export const stockAPI = {
  // 获取股票列表
  getStocks: (params) => api.get('/stocks', { params }),
  
  // 获取IPO股票列表
  getIPOStocks: (params) => api.get('/stocks/ipo', { params }),
  
  // 获取股票详情
  getStockDetail: (tsCode) => api.get(`/stocks/${tsCode}`),
  
  // 获取日线数据
  getDaily: (tsCode, params) => api.get(`/stocks/${tsCode}/daily`, { params }),
  
  // 获取周线数据
  getWeekly: (tsCode, params) => api.get(`/stocks/${tsCode}/weekly`, { params }),
  
  // 获取月线数据
  getMonthly: (tsCode, params) => api.get(`/stocks/${tsCode}/monthly`, { params }),
  
  // 获取资金流向
  getMoneyflow: (tsCode, params) => api.get(`/stocks/${tsCode}/moneyflow`, { params }),
  
  // 获取技术指标
  getIndicators: (tsCode, params) => api.get(`/stocks/${tsCode}/indicators`, { params }),
  
  // 获取K线数据（统一接口）
  getKlineData: (tsCode, type = 'daily', params = {}) => {
    const endpoint = type === 'daily' ? 'daily' : type === 'weekly' ? 'weekly' : 'monthly'
    return api.get(`/stocks/${tsCode}/${endpoint}`, { params })
  },
  
  // 股票对比
  compare: (tsCodes) => api.post('/stocks/compare', { ts_codes: tsCodes }),
  
  // 导出数据
  export: (tsCode, params) => {
    const queryString = new URLSearchParams(params).toString()
    window.open(`${api.defaults.baseURL}/stocks/${tsCode}/export?${queryString}`, '_blank')
  }
}

/**
 * 收藏相关API
 */
export const favoriteAPI = {
  // 获取收藏列表
  getFavorites: (userId = 'default') => api.get('/favorites', { params: { user_id: userId } }),
  
  // 添加收藏
  addFavorite: (tsCode, userId = 'default', notes = '') => 
    api.post('/favorites', { ts_code: tsCode, user_id: userId, notes }),
  
  // 取消收藏
  removeFavorite: (tsCode, userId = 'default') => 
    api.delete(`/favorites/${tsCode}`, { params: { user_id: userId } })
}

/**
 * 行业相关API
 */
export const industryAPI = {
  // 获取行业列表
  getIndustries: () => api.get('/industries'),
  
  // 获取市场列表
  getMarkets: () => api.get('/markets'),
  
  // 获取行业统计
  getStatistics: () => api.get('/industries/statistics')
}

/**
 * 系统相关API
 */
export const systemAPI = {
  // 健康检查
  health: () => api.get('/health'),
  
  // 重载配置
  reloadConfig: () => api.post('/config/reload')
}

/**
 * 大盘相关API
 */
export const marketAPI = {
  // 获取大盘概览
  getMarketOverview: () => api.get('/market/overview'),
  
  // 获取热门板块
  getHotSectors: () => api.get('/market/hot-sectors')
}

/**
 * 外盘市场API
 */
export const globalMarketAPI = {
  // 获取市场指数
  getMarketIndices: () => api.get('/global/indices'),
  
  // 获取股票列表
  getStocks: (market) => api.get(`/global/stocks/${market}`),
  
  // 获取外汇数据
  getForex: () => api.get('/global/forex')
}

/**
 * 知名大佬追踪API
 */
export const bigPlayerAPI = {
  // 获取大佬列表
  getPlayers: (params) => api.get('/bigplayers', { params }),
  
  // 获取持仓详情
  getHoldings: (playerId) => api.get(`/bigplayers/${playerId}/holdings`),
  
  // 获取最新动态
  getActivities: () => api.get('/bigplayers/activities')
}

/**
 * 策略选股API
 */
export const strategyAPI = {
  // 获取选股结果
  getSelections: (params) => api.get('/strategy/selections', { params }),
  
  // 获取有选股结果的日期列表
  getDates: (params) => api.get('/strategy/dates', { params })
}

export default api

