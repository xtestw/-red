<template>
  <div class="page-container">
    <!-- 筛选区域 -->
    <a-card class="filter-card" :bordered="false">
      <template #title>
        <span>🆕 IPO新股筛选</span>
      </template>
      
      <a-form :model="filters" layout="vertical">
        <a-row :gutter="12">
          <a-col :xs="24" :sm="12" :md="6" :lg="5">
            <a-form-item label="关键词搜索（代码/名称/申购代码）">
              <a-input
                v-model:value="filters.keyword"
                placeholder="输入股票代码、名称或申购代码"
                allow-clear
                size="small"
                @pressEnter="handleSearch"
              />
            </a-form-item>
          </a-col>
          <a-col :xs="24" :sm="12" :md="6" :lg="5">
            <a-form-item label="上网发行开始日期">
              <a-date-picker
                v-model:value="filters.start_date"
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
                v-model:value="filters.end_date"
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
                v-model:value="filters.min_price"
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
                v-model:value="filters.max_price"
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
                v-model:value="filters.min_pe"
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
                v-model:value="filters.max_pe"
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
                v-model:value="filters.min_funds"
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
                v-model:value="filters.max_funds"
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
          <a-button type="primary" @click="handleSearch" :loading="loading" size="small">
            <template #icon><SearchOutlined /></template>
            搜索
          </a-button>
          <a-button @click="handleReset" size="small">
            <template #icon><ReloadOutlined /></template>
            重置
          </a-button>
        </a-space>
      </div>
    </a-card>

    <!-- 股票列表 -->
    <a-card class="stock-list-card" :bordered="false">
      <a-table
        :columns="columns"
        :data-source="stocks"
        :loading="loading"
        :pagination="paginationConfig"
        @change="handleTableChange"
        :scroll="{ x: 1400, y: tableScrollHeight }"
        row-key="ts_code"
        size="small"
        :bordered="true"
      >
        <template #bodyCell="{ column, record }">
          <template v-if="column.key === 'price'">
            <span class="number">{{ record.price ? record.price.toFixed(2) : '-' }}</span>
          </template>
          <template v-else-if="column.key === 'pe'">
            <span class="number">{{ record.pe ? record.pe.toFixed(2) : '-' }}</span>
          </template>
          <template v-else-if="column.key === 'funds'">
            <span class="number">{{ record.funds ? record.funds.toFixed(2) : '-' }}</span>
          </template>
          <template v-else-if="column.key === 'amount'">
            <span class="number">{{ record.amount ? formatNumber(record.amount) : '-' }}</span>
          </template>
          <template v-else-if="column.key === 'ballot'">
            <span class="number">{{ record.ballot ? (record.ballot * 100).toFixed(4) + '%' : '-' }}</span>
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
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onBeforeUnmount } from 'vue'
import { message } from 'ant-design-vue'
import {
  SearchOutlined,
  ReloadOutlined,
  StarOutlined,
  EyeOutlined
} from '@ant-design/icons-vue'
import StockDetailModal from '../components/StockDetailModal.vue'
import { stockAPI } from '../api/index'
import { favoriteAPI } from '../api/index'
import { useStockStore } from '../stores/stock'

const store = useStockStore()

// 数据
const stocks = ref([])
const loading = ref(false)
const detailVisible = ref(false)
const currentStockCode = ref('')
const tableScrollHeight = ref(600)

// 筛选条件
const filters = ref({
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

// 分页
const pagination = ref({
  current: 1,
  pageSize: 100,
  total: 0
})

// 计算表格滚动高度
const calculateTableHeight = () => {
  const height = window.innerHeight - 400
  tableScrollHeight.value = Math.max(400, height)
}

// 表格列定义
const columns = [
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
      return a.ipo_date.localeCompare(b.ipo_date)
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
    key: 'ballot',
    width: 100,
    align: 'right',
    sorter: (a, b) => {
      const aVal = a.ballot || 0
      const bVal = b.ballot || 0
      return aVal - bVal
    }
  },
  {
    title: '操作',
    key: 'action',
    width: 150,
    fixed: 'right'
  }
]

// 分页配置
const paginationConfig = computed(() => ({
  current: pagination.value.current,
  pageSize: pagination.value.pageSize,
  total: pagination.value.total,
  showSizeChanger: true,
  showQuickJumper: true,
  showTotal: (total) => `共 ${total} 条记录`,
  onChange: (page, pageSize) => {
    pagination.value.current = page
    pagination.value.pageSize = pageSize
    loadStocks(page)
  },
  onShowSizeChange: (current, size) => {
    pagination.value.current = 1
    pagination.value.pageSize = size
    loadStocks(1)
  }
}))

// 方法
const formatNumber = (num) => {
  return num.toLocaleString('zh-CN')
}

const isFavorited = (tsCode) => {
  return store.favoriteCodes.includes(tsCode)
}

const handleSearch = () => {
  pagination.value.current = 1
  loadStocks(1)
}

const handleReset = () => {
  filters.value = {
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
  pagination.value.current = 1
  loadStocks(1)
}

const loadStocks = async (page = 1) => {
  try {
    loading.value = true
    const params = {
      page: page,
      per_page: pagination.value.pageSize
    }
    
    // 添加筛选条件
    if (filters.value.keyword) {
      params.keyword = filters.value.keyword
    }
    if (filters.value.start_date) {
      params.start_date = filters.value.start_date
    }
    if (filters.value.end_date) {
      params.end_date = filters.value.end_date
    }
    if (filters.value.min_price !== null && filters.value.min_price !== undefined) {
      params.min_price = filters.value.min_price
    }
    if (filters.value.max_price !== null && filters.value.max_price !== undefined) {
      params.max_price = filters.value.max_price
    }
    if (filters.value.min_pe !== null && filters.value.min_pe !== undefined) {
      params.min_pe = filters.value.min_pe
    }
    if (filters.value.max_pe !== null && filters.value.max_pe !== undefined) {
      params.max_pe = filters.value.max_pe
    }
    if (filters.value.min_funds !== null && filters.value.min_funds !== undefined) {
      params.min_funds = filters.value.min_funds
    }
    if (filters.value.max_funds !== null && filters.value.max_funds !== undefined) {
      params.max_funds = filters.value.max_funds
    }
    
    const response = await stockAPI.getIPOStocks(params)
    if (response.code === 0) {
      stocks.value = response.data.stocks || []
      pagination.value = {
        current: response.data.page || 1,
        pageSize: response.data.per_page || 100,
        total: response.data.total || 0
      }
    } else {
      message.error(response.message || '加载IPO股票失败')
    }
  } catch (error) {
    console.error('加载IPO股票失败:', error)
    message.error('加载IPO股票失败')
  } finally {
    loading.value = false
  }
}

const handleTableChange = (pag, filters, sorter) => {
  if (pag && typeof pag === 'object' && 'current' in pag) {
    pagination.value.current = pag.current
    pagination.value.pageSize = pag.pageSize || pagination.value.pageSize
  }
  loadStocks(pagination.value.current)
}

const showStockDetail = (tsCode) => {
  currentStockCode.value = tsCode
  detailVisible.value = true
}

const toggleFavorite = async (tsCode) => {
  try {
    if (isFavorited(tsCode)) {
      await favoriteAPI.removeFavorite(tsCode)
      await store.loadFavorites()
      message.success('已取消收藏')
    } else {
      await favoriteAPI.addFavorite(tsCode)
      await store.loadFavorites()
      message.success('已添加收藏')
    }
  } catch (error) {
    console.error('收藏操作失败:', error)
    message.error('操作失败')
  }
}

// 窗口大小变化时更新表格高度
const updateTableHeight = () => {
  calculateTableHeight()
}

// 初始化
onMounted(async () => {
  await store.loadFavorites()
  await loadStocks()
  
  // 计算初始表格高度
  calculateTableHeight()
  
  // 监听窗口大小变化
  window.addEventListener('resize', updateTableHeight)
})

// 组件卸载时移除监听
onBeforeUnmount(() => {
  window.removeEventListener('resize', updateTableHeight)
})
</script>

<style scoped>
.page-container {
  height: 100%;
  display: flex;
  flex-direction: column;
}

.filter-card {
  margin-bottom: 16px;
}

.filter-actions {
  margin-top: 16px;
  text-align: right;
}

.stock-list-card {
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.stock-list-card :deep(.ant-card-body) {
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  padding: 12px;
}

.number {
  font-family: 'Monaco', 'Menlo', monospace;
}

.favorited {
  color: #faad14 !important;
  font-weight: 600;
}

.favorited:hover {
  color: #ffc53d !important;
}
</style>

