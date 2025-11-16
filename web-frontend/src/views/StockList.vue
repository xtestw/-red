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
          >
            <a-select-option value="all">所有股票</a-select-option>
            <a-select-option value="ipo">IPO股票</a-select-option>
          </a-select>
        </div>
      </template>
      <p style="margin: 8px 0 0 0; font-size: 16px; opacity: 0.8;">
        实时股票数据查询与分析平台 | 专业 · 高效 · 智能
      </p>
    </a-card>

    <!-- 筛选区域 -->
    <a-card class="filter-card" :bordered="false" style="margin-top: 24px;">
      <template #title>
        <span>🔍 股票筛选</span>
      </template>
      
      <!-- 所有股票筛选 -->
      <a-form v-if="store.stockType === 'all'" :model="filters" layout="vertical">
        <a-row :gutter="16">
          <a-col :xs="24" :sm="12" :md="8">
            <a-form-item label="关键词搜索（代码/名称）">
              <a-input
                v-model:value="filters.keyword"
                placeholder="输入股票代码或名称"
                allow-clear
              />
            </a-form-item>
          </a-col>
          <a-col :xs="24" :sm="12" :md="8">
            <a-form-item label="行业">
              <a-select
                v-model:value="filters.industry"
                placeholder="选择行业"
                allow-clear
                :loading="industriesLoading"
              >
                <a-select-option value="">全部行业</a-select-option>
                <a-select-option v-for="ind in industries" :key="ind" :value="ind">
                  {{ ind }}
                </a-select-option>
              </a-select>
            </a-form-item>
          </a-col>
          <a-col :xs="24" :sm="12" :md="8">
            <a-form-item label="市场">
              <a-select
                v-model:value="filters.market"
                placeholder="选择市场"
                allow-clear
                :loading="marketsLoading"
              >
                <a-select-option value="">全部市场</a-select-option>
                <a-select-option v-for="mkt in markets" :key="mkt" :value="mkt">
                  {{ mkt }}
                </a-select-option>
              </a-select>
            </a-form-item>
          </a-col>
        </a-row>
        
        <a-row :gutter="16">
          <a-col :xs="24" :sm="12" :md="6">
            <a-form-item label="最小市值（万元）">
              <a-input-number
                v-model:value="filters.min_market_value"
                placeholder="最小市值"
                :min="0"
                style="width: 100%"
              />
            </a-form-item>
          </a-col>
          <a-col :xs="24" :sm="12" :md="6">
            <a-form-item label="最大市值（万元）">
              <a-input-number
                v-model:value="filters.max_market_value"
                placeholder="最大市值"
                :min="0"
                style="width: 100%"
              />
            </a-form-item>
          </a-col>
          <a-col :xs="24" :sm="12" :md="6">
            <a-form-item label="最小市盈率">
              <a-input-number
                v-model:value="filters.min_pe"
                placeholder="最小PE"
                :min="0"
                style="width: 100%"
              />
            </a-form-item>
          </a-col>
          <a-col :xs="24" :sm="12" :md="6">
            <a-form-item label="最大市盈率">
              <a-input-number
                v-model:value="filters.max_pe"
                placeholder="最大PE"
                :min="0"
                style="width: 100%"
              />
            </a-form-item>
          </a-col>
        </a-row>
      </a-form>
      
      <!-- IPO股票筛选 -->
      <a-form v-else :model="ipoFilters" layout="vertical">
        <a-row :gutter="16">
          <a-col :xs="24" :sm="12" :md="8">
            <a-form-item label="关键词搜索（代码/名称/申购代码）">
              <a-input
                v-model:value="ipoFilters.keyword"
                placeholder="输入股票代码、名称或申购代码"
                allow-clear
              />
            </a-form-item>
          </a-col>
          <a-col :xs="24" :sm="12" :md="8">
            <a-form-item label="上网发行开始日期">
              <a-date-picker
                v-model:value="ipoFilters.start_date"
                placeholder="选择开始日期"
                format="YYYY-MM-DD"
                value-format="YYYYMMDD"
                style="width: 100%"
                allow-clear
              />
            </a-form-item>
          </a-col>
          <a-col :xs="24" :sm="12" :md="8">
            <a-form-item label="上网发行结束日期">
              <a-date-picker
                v-model:value="ipoFilters.end_date"
                placeholder="选择结束日期"
                format="YYYY-MM-DD"
                value-format="YYYYMMDD"
                style="width: 100%"
                allow-clear
              />
            </a-form-item>
          </a-col>
        </a-row>
        
        <a-row :gutter="16">
          <a-col :xs="24" :sm="12" :md="6">
            <a-form-item label="最小发行价格">
              <a-input-number
                v-model:value="ipoFilters.min_price"
                placeholder="最小价格"
                :min="0"
                style="width: 100%"
              />
            </a-form-item>
          </a-col>
          <a-col :xs="24" :sm="12" :md="6">
            <a-form-item label="最大发行价格">
              <a-input-number
                v-model:value="ipoFilters.max_price"
                placeholder="最大价格"
                :min="0"
                style="width: 100%"
              />
            </a-form-item>
          </a-col>
          <a-col :xs="24" :sm="12" :md="6">
            <a-form-item label="最小市盈率">
              <a-input-number
                v-model:value="ipoFilters.min_pe"
                placeholder="最小PE"
                :min="0"
                style="width: 100%"
              />
            </a-form-item>
          </a-col>
          <a-col :xs="24" :sm="12" :md="6">
            <a-form-item label="最大市盈率">
              <a-input-number
                v-model:value="ipoFilters.max_pe"
                placeholder="最大PE"
                :min="0"
                style="width: 100%"
              />
            </a-form-item>
          </a-col>
        </a-row>
        
        <a-row :gutter="16">
          <a-col :xs="24" :sm="12" :md="6">
            <a-form-item label="最小募集资金（亿元）">
              <a-input-number
                v-model:value="ipoFilters.min_funds"
                placeholder="最小募集资金"
                :min="0"
                style="width: 100%"
              />
            </a-form-item>
          </a-col>
          <a-col :xs="24" :sm="12" :md="6">
            <a-form-item label="最大募集资金（亿元）">
              <a-input-number
                v-model:value="ipoFilters.max_funds"
                placeholder="最大募集资金"
                :min="0"
                style="width: 100%"
              />
            </a-form-item>
          </a-col>
        </a-row>
      </a-form>

      <!-- 操作按钮 -->
      <div style="margin-top: 16px;">
        <a-space>
          <a-button type="primary" @click="handleSearch" :loading="loading">
            <template #icon><SearchOutlined /></template>
            搜索
          </a-button>
          <a-button @click="handleReset">
            <template #icon><ReloadOutlined /></template>
            重置
          </a-button>
          <a-button type="default" @click="showFavorites">
            <template #icon><StarOutlined /></template>
            我的收藏
          </a-button>
          <a-button type="default" @click="showCompare">
            <template #icon><BarChartOutlined /></template>
            股票对比
          </a-button>
          <a-button type="default" @click="showIndustryStats">
            <template #icon><PieChartOutlined /></template>
            行业统计
          </a-button>
        </a-space>
      </div>
    </a-card>

    <!-- 股票列表 -->
    <a-card class="stock-list-card" :bordered="false" style="margin-top: 24px;">
      <a-table
        :columns="columns"
        :data-source="stocks"
        :loading="loading"
        :pagination="paginationConfig"
        :row-selection="rowSelection"
        @change="handleTableChange"
        :scroll="{ x: 1200 }"
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
import { ref, computed, onMounted } from 'vue'
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
const { stocks, loading, pagination, filters, industries, markets, favoriteCodes, stockType, ipoFilters } = store

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
    title: '股票代码',
    dataIndex: 'symbol',
    key: 'symbol',
    width: 120,
    fixed: 'left'
  },
  {
    title: '股票名称',
    dataIndex: 'name',
    key: 'name',
    width: 150
  },
  {
    title: '行业',
    dataIndex: 'industry',
    key: 'industry',
    width: 150
  },
  {
    title: '市场',
    dataIndex: 'market',
    key: 'market',
    width: 100
  },
  {
    title: '总市值（万元）',
    key: 'total_mv',
    width: 150,
    align: 'right'
  },
  {
    title: '市盈率',
    key: 'pe',
    width: 100,
    align: 'right'
  },
  {
    title: '市净率',
    key: 'pb',
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

// IPO股票表格列定义
const ipoStockColumns = [
  {
    title: '股票代码',
    dataIndex: 'ts_code',
    key: 'ts_code',
    width: 120,
    fixed: 'left'
  },
  {
    title: '申购代码',
    dataIndex: 'sub_code',
    key: 'sub_code',
    width: 120
  },
  {
    title: '股票名称',
    dataIndex: 'name',
    key: 'name',
    width: 150
  },
  {
    title: '上网发行日期',
    dataIndex: 'ipo_date',
    key: 'ipo_date',
    width: 120
  },
  {
    title: '上市日期',
    dataIndex: 'issue_date',
    key: 'issue_date',
    width: 120
  },
  {
    title: '发行价格',
    dataIndex: 'price',
    key: 'price',
    width: 100,
    align: 'right'
  },
  {
    title: '市盈率',
    dataIndex: 'pe',
    key: 'pe',
    width: 100,
    align: 'right'
  },
  {
    title: '募集资金（亿元）',
    dataIndex: 'funds',
    key: 'funds',
    width: 130,
    align: 'right'
  },
  {
    title: '发行总量（万股）',
    dataIndex: 'amount',
    key: 'amount',
    width: 130,
    align: 'right'
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
      selectedRowKeys.value = stocks.value.map(s => s.ts_code)
    } else {
      selectedRowKeys.value = []
    }
  }
}))

// 分页配置
const paginationConfig = computed(() => ({
  current: pagination.value.current,
  pageSize: pagination.value.pageSize,
  total: pagination.value.total,
  showSizeChanger: true,
  showQuickJumper: true,
  showTotal: (total) => `共 ${total} 条记录`
}))

// 方法
const formatNumber = (num) => {
  return num.toLocaleString('zh-CN')
}

const isFavorited = (tsCode) => {
  return favoriteCodes.value.includes(tsCode)
}

const handleSearch = () => {
  store.loadStocks(1)
}

const handleReset = () => {
  store.resetFilters()
}

const handleTableChange = (pag) => {
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
  filters.value.keyword = ''
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
  store.setStockType(value)
}

// 初始化
onMounted(async () => {
  industriesLoading.value = true
  marketsLoading.value = true
  
  await Promise.all([
    store.loadIndustries(),
    store.loadMarkets(),
    store.loadFavorites(),
    store.loadStocks(1)
  ])
  
  industriesLoading.value = false
  marketsLoading.value = false
})
</script>

<style scoped>
.favorited {
  color: #faad14 !important;
  font-weight: 600;
}

.favorited:hover {
  color: #ffc53d !important;
}
</style>


