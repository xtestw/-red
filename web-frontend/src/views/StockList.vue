<template>
  <div class="page-container">
    <!-- 头部 -->
    <a-card class="header-card" :bordered="false">
      <template #title>
        <div style="display: flex; align-items: center; justify-content: space-between;">
          <h1 style="margin: 0; font-size: 28px; font-weight: 700;">
            📊 A股股票信息
          </h1>
          <a-select
            v-model:value="store.stockType"
            style="width: 150px;"
            @change="handleStockTypeChange"
            placeholder="选择股票类型"
          >
            <a-select-option value="all">所有股票</a-select-option>
            <a-select-option value="ipo">IPO新股</a-select-option>
          </a-select>
        </div>
      </template>
    </a-card>

    <!-- 筛选区域 -->
    <a-card class="filter-card" :bordered="false">
      <template #title>
        <span>🔍 股票筛选</span>
      </template>
      
      <!-- 所有股票筛选 -->
      <a-form v-if="store.stockType === 'all'" :model="store.filters" layout="vertical">
        <a-row :gutter="12">
          <a-col :xs="24" :sm="12" :md="6" :lg="5">
            <a-form-item label="关键词搜索（代码/名称）">
              <a-input
                v-model:value="store.filters.keyword"
                placeholder="输入股票代码或名称"
                allow-clear
                size="small"
              />
            </a-form-item>
          </a-col>
          <a-col :xs="24" :sm="12" :md="6" :lg="5">
            <a-form-item label="行业">
              <a-select
                v-model:value="store.filters.industry"
                placeholder="选择行业"
                allow-clear
                :loading="industriesLoading"
                size="small"
              >
                <a-select-option value="">全部行业</a-select-option>
                <a-select-option v-for="ind in industries" :key="ind" :value="ind">
                  {{ ind }}
                </a-select-option>
              </a-select>
            </a-form-item>
          </a-col>
          <a-col :xs="24" :sm="12" :md="6" :lg="5">
            <a-form-item label="市场">
              <a-select
                v-model:value="store.filters.market"
                placeholder="选择市场"
                allow-clear
                :loading="marketsLoading"
                size="small"
              >
                <a-select-option value="">全部市场</a-select-option>
                <a-select-option v-for="mkt in markets" :key="mkt" :value="mkt">
                  {{ mkt }}
                </a-select-option>
              </a-select>
            </a-form-item>
          </a-col>
          <a-col :xs="24" :sm="12" :md="6" :lg="4">
            <a-form-item label="最小市值（万元）">
              <a-input-number
                v-model:value="store.filters.min_market_value"
                placeholder="最小市值"
                :min="0"
                style="width: 100%"
                size="small"
              />
            </a-form-item>
          </a-col>
          <a-col :xs="24" :sm="12" :md="6" :lg="4">
            <a-form-item label="最大市值（万元）">
              <a-input-number
                v-model:value="store.filters.max_market_value"
                placeholder="最大市值"
                :min="0"
                style="width: 100%"
                size="small"
              />
            </a-form-item>
          </a-col>
        </a-row>
        
        <a-row :gutter="12">
          <a-col :xs="24" :sm="12" :md="6" :lg="4">
            <a-form-item label="最小市盈率">
              <a-input-number
                v-model:value="store.filters.min_pe"
                placeholder="最小PE"
                :min="0"
                style="width: 100%"
                size="small"
              />
            </a-form-item>
          </a-col>
          <a-col :xs="24" :sm="12" :md="6" :lg="4">
            <a-form-item label="最大市盈率">
              <a-input-number
                v-model:value="store.filters.max_pe"
                placeholder="最大PE"
                :min="0"
                style="width: 100%"
                size="small"
              />
            </a-form-item>
          </a-col>
        </a-row>
      </a-form>
      
      <!-- IPO股票筛选 -->
      <a-form v-else :model="store.ipoFilters" layout="vertical">
        <a-row :gutter="12">
          <a-col :xs="24" :sm="12" :md="6" :lg="5">
            <a-form-item label="关键词搜索（代码/名称/申购代码）">
              <a-input
                v-model:value="store.ipoFilters.keyword"
                placeholder="输入股票代码、名称或申购代码"
                allow-clear
                size="small"
              />
            </a-form-item>
          </a-col>
          <a-col :xs="24" :sm="12" :md="6" :lg="5">
            <a-form-item label="上网发行开始日期">
              <a-date-picker
                v-model:value="store.ipoFilters.start_date"
                placeholder="选择开始日期"
                format="YYYY-MM-DD"
                value-format="YYYYMMDD"
                style="width: 100%"
                allow-clear
                size="small"
              />
            </a-form-item>
          </a-col>
          <a-col :xs="24" :sm="12" :md="6" :lg="5">
            <a-form-item label="上网发行结束日期">
              <a-date-picker
                v-model:value="store.ipoFilters.end_date"
                placeholder="选择结束日期"
                format="YYYY-MM-DD"
                value-format="YYYYMMDD"
                style="width: 100%"
                allow-clear
                size="small"
              />
            </a-form-item>
          </a-col>
          <a-col :xs="24" :sm="12" :md="6" :lg="4">
            <a-form-item label="最小发行价格">
              <a-input-number
                v-model:value="store.ipoFilters.min_price"
                placeholder="最小价格"
                :min="0"
                style="width: 100%"
                size="small"
              />
            </a-form-item>
          </a-col>
          <a-col :xs="24" :sm="12" :md="6" :lg="4">
            <a-form-item label="最大发行价格">
              <a-input-number
                v-model:value="store.ipoFilters.max_price"
                placeholder="最大价格"
                :min="0"
                style="width: 100%"
                size="small"
              />
            </a-form-item>
          </a-col>
        </a-row>
        
        <a-row :gutter="12">
          <a-col :xs="24" :sm="12" :md="6" :lg="4">
            <a-form-item label="最小市盈率">
              <a-input-number
                v-model:value="store.ipoFilters.min_pe"
                placeholder="最小PE"
                :min="0"
                style="width: 100%"
                size="small"
              />
            </a-form-item>
          </a-col>
          <a-col :xs="24" :sm="12" :md="6" :lg="4">
            <a-form-item label="最大市盈率">
              <a-input-number
                v-model:value="store.ipoFilters.max_pe"
                placeholder="最大PE"
                :min="0"
                style="width: 100%"
                size="small"
              />
            </a-form-item>
          </a-col>
          <a-col :xs="24" :sm="12" :md="6" :lg="4">
            <a-form-item label="最小募集资金（亿元）">
              <a-input-number
                v-model:value="store.ipoFilters.min_funds"
                placeholder="最小募集资金"
                :min="0"
                style="width: 100%"
                size="small"
              />
            </a-form-item>
          </a-col>
          <a-col :xs="24" :sm="12" :md="6" :lg="4">
            <a-form-item label="最大募集资金（亿元）">
              <a-input-number
                v-model:value="store.ipoFilters.max_funds"
                placeholder="最大募集资金"
                :min="0"
                style="width: 100%"
                size="small"
              />
            </a-form-item>
          </a-col>
        </a-row>
      </a-form>

      <!-- 操作按钮 -->
      <div class="filter-actions">
        <a-space>
          <a-button type="primary" @click="handleSearch" :loading="store.loading" size="small">
            <template #icon><SearchOutlined /></template>
            搜索
          </a-button>
          <a-button @click="handleReset" size="small">
            <template #icon><ReloadOutlined /></template>
            重置
          </a-button>
          <a-button type="default" @click="showFavorites" size="small">
            <template #icon><StarOutlined /></template>
            我的收藏
          </a-button>
          <a-button type="default" @click="showCompare" size="small">
            <template #icon><BarChartOutlined /></template>
            股票对比
          </a-button>
          <a-button type="default" @click="showIndustryStats" size="small">
            <template #icon><PieChartOutlined /></template>
            行业统计
          </a-button>
        </a-space>
      </div>
    </a-card>

    <!-- 股票列表 -->
    <a-card class="stock-list-card" :bordered="false">
      <a-table
        :columns="columns"
        :data-source="store.stocks"
        :loading="{ spinning: store.loading, tip: '加载中...' }"
        :pagination="paginationConfig"
        :row-selection="rowSelection"
        @change="handleTableChange"
        :scroll="{ x: 1400, y: 'calc(100vh - 280px)' }"
        row-key="ts_code"
        :locale="{ emptyText: '暂无数据' }"
        size="small"
        :bordered="true"
        class="compact-table"
      >
        <template #bodyCell="{ column, record }">
          <template v-if="column.key === 'total_mv'">
            <span class="number">{{ record.total_mv ? formatNumber(record.total_mv) : '-' }}</span>
          </template>
          <template v-else-if="column.key === 'pe'">
            <span class="number">{{ record.pe ? record.pe.toFixed(2) : '-' }}</span>
          </template>
          <template v-else-if="column.key === 'pb'">
            <span class="number">{{ record.pb ? record.pb.toFixed(2) : '-' }}</span>
          </template>
          <template v-else-if="column.key === 'ps'">
            <span class="number">{{ record.ps ? record.ps.toFixed(2) : '-' }}</span>
          </template>
          <template v-else-if="column.key === 'circ_mv'">
            <span class="number">{{ record.circ_mv ? formatNumber(record.circ_mv) : '-' }}</span>
          </template>
          <template v-else-if="column.key === 'list_date'">
            <span>{{ record.list_date || '-' }}</span>
          </template>
          <template v-else-if="column.key === 'area'">
            <span>{{ record.area || '-' }}</span>
          </template>
          <template v-else-if="column.key === 'ts_code'">
            <span>{{ record.ts_code || '-' }}</span>
          </template>
          <template v-else-if="column.key === 'price'">
            <span class="number">{{ record.price ? record.price.toFixed(2) : '-' }}</span>
          </template>
          <template v-else-if="column.key === 'funds'">
            <span class="number">{{ record.funds ? record.funds.toFixed(2) : '-' }}</span>
          </template>
          <template v-else-if="column.key === 'amount'">
            <span class="number">{{ record.amount ? formatNumber(record.amount) : '-' }}</span>
          </template>
          <template v-else-if="column.key === 'ballot'">
            <span class="number">{{ record.ballot ? (record.ballot * 100).toFixed(2) + '%' : '-' }}</span>
          </template>
          <template v-else-if="column.key === 'action'">
            <a-space>
              <a-button type="link" size="small" @click="showStockDetail(record.ts_code)">
                <template #icon><EyeOutlined /></template>
                详情
              </a-button>
              <a-button
                type="link"
                size="small"
                @click="toggleFavorite(record.ts_code)"
                :class="{ 'favorited': isFavorited(record.ts_code) }"
              >
                <template #icon><StarOutlined /></template>
                {{ isFavorited(record.ts_code) ? '已收藏' : '收藏' }}
              </a-button>
            </a-space>
          </template>
        </template>
      </a-table>
    </a-card>

    <!-- 股票详情模态框 -->
    <StockDetailModal
      v-model:open="detailVisible"
      :ts-code="currentStockCode"
      @close="detailVisible = false"
    />

    <!-- 股票对比模态框 -->
    <StockCompareModal
      v-model:open="compareVisible"
      :ts-codes="selectedStockCodes"
      @close="compareVisible = false"
    />

    <!-- 行业统计模态框 -->
    <IndustryStatsModal
      v-model:open="statsVisible"
      @close="statsVisible = false"
    />
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch, nextTick } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useStockStore } from '../stores/stock'
import { message } from 'ant-design-vue'
import {
  SearchOutlined,
  ReloadOutlined,
  StarOutlined,
  BarChartOutlined,
  PieChartOutlined,
  EyeOutlined
} from '@ant-design/icons-vue'
import StockDetailModal from '../components/StockDetailModal.vue'
import StockCompareModal from '../components/StockCompareModal.vue'
import IndustryStatsModal from '../components/IndustryStatsModal.vue'

const store = useStockStore()
const { stocks, loading, pagination, industries, markets, favoriteCodes } = store

// 添加调试：监听 stocks 变化
watch(() => store.stocks, (newStocks) => {
  console.log('Stocks数据变化:', newStocks?.length, '条')
  if (newStocks && newStocks.length > 0) {
    console.log('第一条股票数据:', newStocks[0])
  }
}, { immediate: true, deep: true })

const industriesLoading = ref(false)
const marketsLoading = ref(false)
const detailVisible = ref(false)
const compareVisible = ref(false)
const statsVisible = ref(false)
const currentStockCode = ref('')
const selectedRowKeys = ref([])
const selectedStockCodes = computed(() => selectedRowKeys.value)

// 所有股票表格列定义
const allStockColumns = [
  {
    title: '代码',
    dataIndex: 'symbol',
    key: 'symbol',
    width: 80,
    fixed: 'left',
    sorter: (a, b) => {
      if (!a.symbol || !b.symbol) return 0
      return a.symbol.localeCompare(b.symbol)
    }
  },
  {
    title: '名称',
    dataIndex: 'name',
    key: 'name',
    width: 100,
    fixed: 'left',
    sorter: (a, b) => {
      if (!a.name || !b.name) return 0
      return a.name.localeCompare(b.name)
    }
  },
  {
    title: 'TS代码',
    dataIndex: 'ts_code',
    key: 'ts_code',
    width: 100,
    sorter: (a, b) => {
      if (!a.ts_code || !b.ts_code) return 0
      return a.ts_code.localeCompare(b.ts_code)
    }
  },
  {
    title: '地域',
    dataIndex: 'area',
    key: 'area',
    width: 80,
    sorter: (a, b) => {
      if (!a.area || !b.area) return 0
      return (a.area || '').localeCompare(b.area || '')
    }
  },
  {
    title: '行业',
    dataIndex: 'industry',
    key: 'industry',
    width: 120,
    sorter: (a, b) => {
      if (!a.industry || !b.industry) return 0
      return (a.industry || '').localeCompare(b.industry || '')
    }
  },
  {
    title: '市场',
    dataIndex: 'market',
    key: 'market',
    width: 70,
    sorter: (a, b) => {
      if (!a.market || !b.market) return 0
      return (a.market || '').localeCompare(b.market || '')
    }
  },
  {
    title: '上市日期',
    dataIndex: 'list_date',
    key: 'list_date',
    width: 100,
    sorter: (a, b) => {
      if (!a.list_date || !b.list_date) return 0
      return (a.list_date || '').localeCompare(b.list_date || '')
    }
  },
  {
    title: '总市值（万元）',
    dataIndex: 'total_mv',
    key: 'total_mv',
    width: 120,
    align: 'right',
    sorter: (a, b) => {
      const aVal = a.total_mv || 0
      const bVal = b.total_mv || 0
      return aVal - bVal
    }
  },
  {
    title: '流通市值（万元）',
    dataIndex: 'circ_mv',
    key: 'circ_mv',
    width: 120,
    align: 'right',
    sorter: (a, b) => {
      const aVal = a.circ_mv || 0
      const bVal = b.circ_mv || 0
      return aVal - bVal
    }
  },
  {
    title: '市盈率',
    dataIndex: 'pe',
    key: 'pe',
    width: 80,
    align: 'right',
    sorter: (a, b) => {
      const aVal = a.pe || 0
      const bVal = b.pe || 0
      return aVal - bVal
    }
  },
  {
    title: '市净率',
    dataIndex: 'pb',
    key: 'pb',
    width: 80,
    align: 'right',
    sorter: (a, b) => {
      const aVal = a.pb || 0
      const bVal = b.pb || 0
      return aVal - bVal
    }
  },
  {
    title: '市销率',
    dataIndex: 'ps',
    key: 'ps',
    width: 80,
    align: 'right',
    sorter: (a, b) => {
      const aVal = a.ps || 0
      const bVal = b.ps || 0
      return aVal - bVal
    }
  },
  {
    title: '操作',
    key: 'action',
    width: 120,
    fixed: 'right'
  }
]

// IPO股票表格列定义
const ipoStockColumns = [
  {
    title: '股票代码',
    dataIndex: 'ts_code',
    key: 'ts_code',
    width: 120,
    fixed: 'left',
    sorter: (a, b) => {
      if (!a.ts_code || !b.ts_code) return 0
      return a.ts_code.localeCompare(b.ts_code)
    }
  },
  {
    title: '申购代码',
    dataIndex: 'sub_code',
    key: 'sub_code',
    width: 120,
    sorter: (a, b) => {
      if (!a.sub_code || !b.sub_code) return 0
      return (a.sub_code || '').localeCompare(b.sub_code || '')
    }
  },
  {
    title: '股票名称',
    dataIndex: 'name',
    key: 'name',
    width: 150,
    sorter: (a, b) => {
      if (!a.name || !b.name) return 0
      return a.name.localeCompare(b.name)
    }
  },
  {
    title: '上网发行日期',
    dataIndex: 'ipo_date',
    key: 'ipo_date',
    width: 120,
    sorter: (a, b) => {
      if (!a.ipo_date || !b.ipo_date) return 0
      return (a.ipo_date || '').localeCompare(b.ipo_date || '')
    }
  },
  {
    title: '上市日期',
    dataIndex: 'issue_date',
    key: 'issue_date',
    width: 120,
    sorter: (a, b) => {
      if (!a.issue_date || !b.issue_date) return 0
      return (a.issue_date || '').localeCompare(b.issue_date || '')
    }
  },
  {
    title: '发行价格',
    dataIndex: 'price',
    key: 'price',
    width: 100,
    align: 'right',
    sorter: (a, b) => {
      const aVal = a.price || 0
      const bVal = b.price || 0
      return aVal - bVal
    }
  },
  {
    title: '市盈率',
    dataIndex: 'pe',
    key: 'pe',
    width: 100,
    align: 'right',
    sorter: (a, b) => {
      const aVal = a.pe || 0
      const bVal = b.pe || 0
      return aVal - bVal
    }
  },
  {
    title: '募集资金（亿元）',
    dataIndex: 'funds',
    key: 'funds',
    width: 130,
    align: 'right',
    sorter: (a, b) => {
      const aVal = a.funds || 0
      const bVal = b.funds || 0
      return aVal - bVal
    }
  },
  {
    title: '发行总量（万股）',
    dataIndex: 'amount',
    key: 'amount',
    width: 130,
    align: 'right',
    sorter: (a, b) => {
      const aVal = a.amount || 0
      const bVal = b.amount || 0
      return aVal - bVal
    }
  },
  {
    title: '中签率',
    dataIndex: 'ballot',
    key: 'ballot',
    width: 100,
    align: 'right'
  },
  {
    title: '操作',
    key: 'action',
    width: 150,
    fixed: 'right'
  }
]

// 根据股票类型返回对应的列
const columns = computed(() => {
  return store.stockType === 'ipo' ? ipoStockColumns : allStockColumns
})

// 行选择配置
const rowSelection = computed(() => ({
  selectedRowKeys: selectedRowKeys.value,
  onChange: (keys) => {
    selectedRowKeys.value = keys
  },
  onSelectAll: (selected) => {
    if (selected) {
      selectedRowKeys.value = store.stocks.map(s => s.ts_code)
    } else {
      selectedRowKeys.value = []
    }
  }
}))

// 分页配置
const paginationConfig = computed(() => ({
  current: store.pagination.current,
  pageSize: store.pagination.pageSize,
  total: store.pagination.total,
  showSizeChanger: true,
  showQuickJumper: true,
  showTotal: (total) => `共 ${total} 条记录`,
  pageSizeOptions: ['50', '100', '200', '500', '1000', '2000', '5000', '8000'],
  size: 'small'
}))

// 方法
const formatNumber = (num) => {
  return num.toLocaleString('zh-CN')
}

const isFavorited = (tsCode) => {
  if (!tsCode || !favoriteCodes.value || !Array.isArray(favoriteCodes.value)) {
    return false
  }
  return favoriteCodes.value.includes(tsCode)
}

const handleSearch = () => {
  store.loadStocks(1)
}

const handleReset = () => {
  store.resetFilters()
}

const handleTableChange = (pag, filters, sorter) => {
  console.log('表格变化:', { pag, filters, sorter })
  // 如果分页大小改变，更新store中的pageSize
  if (pag.pageSize && pag.pageSize !== store.pagination.pageSize) {
    store.pagination.pageSize = pag.pageSize
  }
  // 加载对应页的数据
  store.loadStocks(pag.current)
}

const showStockDetail = (tsCode) => {
  currentStockCode.value = tsCode
  detailVisible.value = true
}

const toggleFavorite = async (tsCode) => {
  if (isFavorited(tsCode)) {
    const success = await store.removeFavorite(tsCode)
    if (success) {
      message.success('已取消收藏')
    }
  } else {
    const success = await store.addFavorite(tsCode)
    if (success) {
      message.success('已添加收藏')
    }
  }
}

const showFavorites = async () => {
  await store.loadFavorites()
  if (store.favorites.length === 0) {
    message.info('暂无收藏的股票')
    return
  }
  // 可以打开收藏列表模态框或直接筛选
  store.filters.keyword = ''
  store.loadStocks(1)
}

const showCompare = () => {
  if (selectedRowKeys.value.length < 2) {
    message.warning('请至少选择2只股票进行对比')
    return
  }
  if (selectedRowKeys.value.length > 10) {
    message.warning('最多只能对比10只股票')
    return
  }
  compareVisible.value = true
}

const showIndustryStats = () => {
  statsVisible.value = true
}

const handleStockTypeChange = (value) => {
  console.log('股票类型切换:', value)
  // 切换类型时重置到第一页
  store.pagination.current = 1
  store.setStockType(value)
  // 更新路由查询参数，保持URL和菜单选中状态同步
  router.replace({
    name: 'StockList',
    query: { ...route.query, stock_type: value }
  })
}

// 获取路由信息
const route = useRoute()
const router = useRouter()

// 根据路由查询参数初始化股票类型
const initStockTypeFromRoute = () => {
  const stockType = route.query?.stock_type
  if (stockType === 'ipo' || stockType === 'all') {
    store.setStockType(stockType)
  } else {
    // 如果没有查询参数，默认设置为'all'并更新URL
    store.setStockType('all')
    router.replace({
      name: 'StockList',
      query: { stock_type: 'all' }
    })
  }
}

// 监听路由查询参数变化
watch(() => route.query?.stock_type, (newType) => {
  if (newType === 'ipo' || newType === 'all') {
    if (store.stockType !== newType) {
      store.setStockType(newType)
    }
  }
})

// 初始化
onMounted(async () => {
  // 根据路由查询参数设置股票类型
  initStockTypeFromRoute()
  
  industriesLoading.value = true
  marketsLoading.value = true
  
  // 使用nextTick确保UI先渲染，然后再加载数据
  await nextTick()
  
  // 先加载行业和市场数据（这些数据量小，不会阻塞）
  await Promise.all([
    store.loadIndustries(),
    store.loadMarkets(),
    store.loadFavorites()
  ])
  
  industriesLoading.value = false
  marketsLoading.value = false
  
  // 然后异步加载股票数据，不阻塞其他操作
  store.loadStocks(1).catch(err => {
    console.error('加载股票数据失败:', err)
  })
})
</script>

<style scoped>
/* 页面容器 - 全宽显示，无左右留白 */
.page-container {
  width: 100%;
  max-width: 100%;
  padding: 0;
  margin: 0;
}

/* 头部卡片 - 紧凑样式 */
.header-card {
  margin: 0;
  border-radius: 0;
}

.header-card :deep(.ant-card-head) {
  padding: 12px 16px;
  min-height: 48px;
}

.header-card :deep(.ant-card-body) {
  padding: 8px 16px 12px 16px;
}

.header-card h1 {
  font-size: 20px !important;
  margin: 0 !important;
}

.header-card p {
  font-size: 13px !important;
  margin: 4px 0 0 0 !important;
}

/* 筛选卡片 - 紧凑样式 */
.filter-card {
  margin: 8px 0 0 0;
  border-radius: 0;
}

.filter-card :deep(.ant-card-head) {
  padding: 10px 16px;
  min-height: 40px;
}

.filter-card :deep(.ant-card-body) {
  padding: 12px 16px;
}

/* 操作按钮区域 - 右对齐 */
.filter-actions {
  margin-top: 12px;
  display: flex;
  justify-content: flex-end;
}

/* 股票列表卡片 - 全宽显示 */
.stock-list-card {
  margin: 8px 0 0 0;
  border-radius: 0;
}

.stock-list-card :deep(.ant-card-body) {
  padding: 8px 16px;
}

.favorited {
  color: #faad14 !important;
  font-weight: 600;
}

.favorited:hover {
  color: #ffc53d !important;
}

/* 紧凑表格样式 - 让一屏显示更多股票 */
.compact-table :deep(.ant-table) {
  font-size: 12px;
}

.compact-table :deep(.ant-table-thead > tr > th) {
  padding: 6px 4px;
  font-size: 12px;
  font-weight: 600;
  background: #fafafa;
  line-height: 1.2;
}

.compact-table :deep(.ant-table-tbody > tr > td) {
  padding: 4px 4px;
  font-size: 12px;
  line-height: 1.2;
}

.compact-table :deep(.ant-table-tbody > tr) {
  height: 28px;
}

.compact-table :deep(.ant-table-tbody > tr:hover > td) {
  background: #e6f7ff;
}

/* 确保loading遮罩层只覆盖表格区域，不影响其他区域 */
.compact-table :deep(.ant-spin-nested-loading) {
  position: relative;
  min-height: 200px;
  /* 确保loading容器不会阻止事件冒泡到父元素 */
  pointer-events: none;
}

.compact-table :deep(.ant-spin-container) {
  position: relative;
  /* 容器内容可以接收点击事件 */
  pointer-events: auto;
}

.compact-table :deep(.ant-spin-blur) {
  opacity: 0.5;
  pointer-events: none;
  user-select: none;
  overflow: hidden;
}

/* 确保loading遮罩层不会阻止点击其他区域 */
.compact-table :deep(.ant-spin) {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  z-index: 10;
  max-height: 100%;
  /* loading遮罩层不阻止事件穿透 */
  pointer-events: none;
}

.compact-table :deep(.ant-spin .ant-spin-dot) {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  /* loading图标可以接收事件（如果需要） */
  pointer-events: auto;
}

/* 确保表格卡片外的区域不受loading影响 */
.stock-list-card {
  position: relative;
}

.stock-list-card :deep(.ant-card-body) {
  position: relative;
  pointer-events: auto;
}

/* 数字列样式 */
.number {
  font-family: 'Monaco', 'Menlo', 'Ubuntu Mono', monospace;
  font-size: 11px;
}


/* 分页样式优化 */
.compact-table :deep(.ant-pagination) {
  margin: 12px 0;
  font-size: 12px;
}

.compact-table :deep(.ant-pagination-item) {
  min-width: 28px;
  height: 28px;
  line-height: 26px;
  font-size: 12px;
}

.compact-table :deep(.ant-pagination-options) {
  font-size: 12px;
}
</style>


