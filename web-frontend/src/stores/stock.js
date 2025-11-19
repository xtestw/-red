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
    pageSize: 200,
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
  const favoriteCodes = computed(() => {
    if (!favorites.value || !Array.isArray(favorites.value)) {
      return []
    }
    return favorites.value.map(f => f?.ts_code).filter(Boolean)
  })

  // 分批更新数据，避免阻塞UI
  // 使用更小的批次和更长的延迟，确保赋值和渲染不会阻塞UI
  const updateStocksInBatches = async (newStocks, batchSize = 20) => {
    // 先清空数据，让表格显示为空状态（避免显示旧数据）
    // 使用requestIdleCallback确保清空操作不阻塞
    await new Promise(resolve => {
      const clear = () => {
        stocks.value = []
        resolve()
      }
      if (window.requestIdleCallback) {
        requestIdleCallback(clear, { timeout: 50 })
      } else {
        setTimeout(clear, 0)
      }
    })
    
    // 等待一个事件循环，让UI有机会更新和响应点击
    await new Promise(resolve => setTimeout(resolve, 30))
    
    // 如果数据量小，直接更新
    if (newStocks.length <= batchSize) {
      // 使用requestIdleCallback或setTimeout确保不阻塞
      await new Promise(resolve => {
        const update = () => {
          stocks.value = newStocks
          resolve()
        }
        if (window.requestIdleCallback) {
          requestIdleCallback(update, { timeout: 100 })
        } else {
          setTimeout(update, 0)
        }
      })
      // 等待表格渲染完成
      await new Promise(resolve => setTimeout(resolve, 20))
      return
    }
    
    // 分批更新数据，使用更小的批次避免单次赋值和渲染开销过大
    for (let i = 0; i < newStocks.length; i += batchSize) {
      const batch = newStocks.slice(i, i + batchSize)
      
      // 使用更长的延迟，确保UI有时间响应点击事件和处理渲染
      await new Promise(resolve => {
        const updateBatch = () => {
          // 追加新批次到现有数据
          // 注意：每次赋值都会触发Vue的响应式系统和表格的重新渲染
          stocks.value = [...stocks.value, ...batch]
          resolve()
        }
        
        // 使用requestIdleCallback，给更长的超时时间，让浏览器优先处理用户交互
        // 这样赋值和渲染会在浏览器空闲时进行
        if (window.requestIdleCallback) {
          requestIdleCallback(updateBatch, { timeout: 200 })
        } else {
          // 使用setTimeout + requestAnimationFrame，给浏览器更多时间处理事件和渲染
          setTimeout(() => {
            requestAnimationFrame(() => {
              setTimeout(updateBatch, 0)
            })
          }, 10)
        }
      })
      
      // 每批之间让出更多时间，确保：
      // 1. Vue的响应式系统有时间处理
      // 2. 表格组件有时间渲染DOM
      // 3. 浏览器有时间处理点击事件
      if (i + batchSize < newStocks.length) {
        await new Promise(resolve => setTimeout(resolve, 20))
      }
    }
    
    // 最后等待一下，确保所有渲染完成
    await new Promise(resolve => setTimeout(resolve, 10))
  }

  // 方法
  const loadStocks = async (page = 1) => {
    // 使用nextTick确保loading状态更新不阻塞
    await new Promise(resolve => setTimeout(resolve, 0))
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
          // 更新分页信息
          pagination.value = {
            current: result.data.page,
            pageSize: result.data.per_page,
            total: result.data.total
          }
          // 分批更新股票数据
          await updateStocksInBatches(result.data.stocks || [])
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
        console.log('股票列表API响应:', result)
        if (result.code === 0) {
          console.log('股票数据:', result.data.stocks)
          console.log('股票数量:', result.data.stocks?.length)
          // 更新分页信息
          pagination.value = {
            current: result.data.page,
            pageSize: result.data.per_page,
            total: result.data.total
          }
          // 分批更新股票数据
          await updateStocksInBatches(result.data.stocks || [])
          console.log('Store stocks更新后:', stocks.value.length, '条')
        } else {
          console.error('API返回错误:', result.message)
          stocks.value = []
        }
      }
    } catch (error) {
      console.error('加载股票列表失败:', error)
      stocks.value = []
    } finally {
      // 确保loading状态在下一个事件循环中更新，不阻塞UI
      await new Promise(resolve => setTimeout(resolve, 0))
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
      const result = await favoriteAPI.addFavorite(tsCode, notes)
      if (result.code === 0) {
        await loadFavorites()
        return true
      }
    } catch (error) {
      console.error('添加收藏失败:', error)
      throw error
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
      throw error
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



