import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { stockAPI, favoriteAPI, industryAPI } from '../api'

export const useStockStore = defineStore('stock', () => {
  // 状态
  const stocks = ref([])
  const currentStock = ref(null)
  const favorites = ref([])
  const industries = ref([])
  const markets = ref([])
  const loading = ref(false)
  const pagination = ref({
    current: 1,
    pageSize: 50,
    total: 0
  })
  const filters = ref({
    keyword: '',
    industry: '',
    market: '',
    min_market_value: null,
    max_market_value: null,
    min_pe: null,
    max_pe: null
  })
  const stockType = ref('all')  // 'all': 所有股票, 'ipo': IPO股票
  const ipoFilters = ref({
    keyword: '',
    start_date: '',
    end_date: '',
    min_price: null,
    max_price: null,
    min_pe: null,
    max_pe: null,
    min_funds: null,
    max_funds: null
  })

  // 计算属性
  const favoriteCodes = computed(() => 
    favorites.value.map(f => f.ts_code)
  )

  // 方法
  const loadStocks = async (page = 1) => {
    loading.value = true
    try {
      if (stockType.value === 'ipo') {
        // 加载IPO股票
        const params = {
          ...ipoFilters.value,
          page,
          per_page: pagination.value.pageSize
        }
        // 移除空值（日期选择器使用value-format后已经是字符串格式）
        Object.keys(params).forEach(key => {
          if (params[key] === '' || params[key] === null || params[key] === undefined) {
            delete params[key]
          }
        })
        
        const result = await stockAPI.getIPOStocks(params)
        if (result.code === 0) {
          stocks.value = result.data.stocks
          pagination.value = {
            current: result.data.page,
            pageSize: result.data.per_page,
            total: result.data.total
          }
        }
      } else {
        // 加载所有股票
        const params = {
          ...filters.value,
          page,
          per_page: pagination.value.pageSize
        }
        // 移除空值
        Object.keys(params).forEach(key => {
          if (params[key] === '' || params[key] === null || params[key] === undefined) {
            delete params[key]
          }
        })
        
        const result = await stockAPI.getStocks(params)
        if (result.code === 0) {
          stocks.value = result.data.stocks
          pagination.value = {
            current: result.data.page,
            pageSize: result.data.per_page,
            total: result.data.total
          }
        }
      }
    } catch (error) {
      console.error('加载股票列表失败:', error)
    } finally {
      loading.value = false
    }
  }

  const loadStockDetail = async (tsCode) => {
    try {
      const result = await stockAPI.getStockDetail(tsCode)
      if (result.code === 0) {
        currentStock.value = result.data
      }
    } catch (error) {
      console.error('加载股票详情失败:', error)
    }
  }

  const loadFavorites = async () => {
    try {
      const result = await favoriteAPI.getFavorites()
      if (result.code === 0) {
        favorites.value = result.data
      }
    } catch (error) {
      console.error('加载收藏列表失败:', error)
    }
  }

  const addFavorite = async (tsCode, notes = '') => {
    try {
      const result = await favoriteAPI.addFavorite(tsCode, 'default', notes)
      if (result.code === 0) {
        await loadFavorites()
        return true
      }
    } catch (error) {
      console.error('添加收藏失败:', error)
    }
    return false
  }

  const removeFavorite = async (tsCode) => {
    try {
      const result = await favoriteAPI.removeFavorite(tsCode)
      if (result.code === 0) {
        await loadFavorites()
        return true
      }
    } catch (error) {
      console.error('取消收藏失败:', error)
    }
    return false
  }

  const loadIndustries = async () => {
    try {
      const result = await industryAPI.getIndustries()
      if (result.code === 0) {
        industries.value = result.data
      }
    } catch (error) {
      console.error('加载行业列表失败:', error)
    }
  }

  const loadMarkets = async () => {
    try {
      const result = await industryAPI.getMarkets()
      if (result.code === 0) {
        markets.value = result.data
      }
    } catch (error) {
      console.error('加载市场列表失败:', error)
    }
  }

  const resetFilters = () => {
    if (stockType.value === 'ipo') {
      ipoFilters.value = {
        keyword: '',
        start_date: '',
        end_date: '',
        min_price: null,
        max_price: null,
        min_pe: null,
        max_pe: null,
        min_funds: null,
        max_funds: null
      }
    } else {
      filters.value = {
        keyword: '',
        industry: '',
        market: '',
        min_market_value: null,
        max_market_value: null,
        min_pe: null,
        max_pe: null
      }
    }
    loadStocks(1)
  }

  const setStockType = (type) => {
    stockType.value = type
    loadStocks(1)
  }

  return {
    // 状态
    stocks,
    currentStock,
    favorites,
    industries,
    markets,
    loading,
    pagination,
    filters,
    stockType,
    ipoFilters,
    // 计算属性
    favoriteCodes,
    // 方法
    loadStocks,
    loadStockDetail,
    loadFavorites,
    addFavorite,
    removeFavorite,
    loadIndustries,
    loadMarkets,
    resetFilters,
    setStockType
  }
})



