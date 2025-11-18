<template>
  <div class="page-container">
    <!-- 策略Tab区域 -->
    <a-card class="strategy-card" :bordered="false">
      <a-tabs v-model:activeKey="activeStrategy" @change="handleStrategyChange">
        <a-tab-pane key="放量策略" tab="放量策略选股">
          <div class="strategy-content">
            <!-- 筛选区域 -->
            <div class="filter-selector">
              <a-space wrap size="small">
                <span>选股日期：</span>
                <a-select
                  v-model:value="selectedDate"
                  style="width: 180px"
                  placeholder="选择日期"
                  :loading="datesLoading"
                  @change="handleDateChange"
                  allowClear
                  size="small"
                >
                  <a-select-option v-for="date in dates" :key="date" :value="date">
                    {{ date }}
                  </a-select-option>
                </a-select>
                <span>行业筛选：</span>
                <a-select
                  v-model:value="selectedIndustry"
                  style="width: 180px"
                  placeholder="选择行业"
                  allowClear
                  @change="handleFilterChange"
                  size="small"
                >
                  <a-select-option v-for="industry in industries" :key="industry" :value="industry">
                    {{ industry }}
                  </a-select-option>
                </a-select>
                <a-button type="primary" @click="loadSelections" :loading="loading" size="small">
                  <template #icon><ReloadOutlined /></template>
                  刷新
                </a-button>
                <a-button @click="resetFilters" size="small">
                  重置筛选
                </a-button>
              </a-space>
            </div>

            <!-- 股票列表 -->
            <a-table
              :columns="columns"
              :data-source="selections"
              :loading="loading"
              :pagination="paginationConfig"
              @change="handleTableChange"
              :scroll="{ x: 1200, y: tableScrollHeight.value }"
              size="small"
            >
              <template #bodyCell="{ column, record }">
                <template v-if="column.key === 'pct_chg'">
                  <span :class="getPctChgClass(record.pct_chg)">
                    {{ record.pct_chg ? formatPctChg(record.pct_chg) : '-' }}
                  </span>
                </template>
                <template v-else-if="column.key === 'close'">
                  <span class="number">{{ record.close ? record.close.toFixed(2) : '-' }}</span>
                </template>
                <template v-else-if="column.key === 'vol'">
                  <span class="number">{{ record.vol ? formatNumber(record.vol) : '-' }}</span>
                </template>
                <template v-else-if="column.key === 'amount'">
                  <span class="number">{{ record.amount ? formatNumber(record.amount) : '-' }}</span>
                </template>
                <template v-else-if="column.key === 'score'">
                  <span class="number">{{ record.score ? record.score.toFixed(2) : '-' }}</span>
                </template>
                <template v-else-if="column.key === 'reason'">
                  <a-tooltip :title="record.reason" placement="topLeft">
                    <span class="reason-text">{{ record.reason || '-' }}</span>
                  </a-tooltip>
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
          </div>
        </a-tab-pane>
        <!-- 可以在这里添加更多策略的tab -->
      </a-tabs>
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
  ReloadOutlined,
  StarOutlined,
  EyeOutlined
} from '@ant-design/icons-vue'
import StockDetailModal from '../components/StockDetailModal.vue'
import { strategyAPI } from '../api/index'
import { favoriteAPI } from '../api/index'
import { useStockStore } from '../stores/stock'

const store = useStockStore()
const activeStrategy = ref('放量策略')
const selectedDate = ref('')
const selectedIndustry = ref('')
const dates = ref([])
const datesLoading = ref(false)
const selections = ref([])
const loading = ref(false)
const detailVisible = ref(false)
const currentStockCode = ref('')
const industries = ref([])
const pagination = ref({
  current: 1,
  pageSize: 100,
  total: 0
})
const tableSorter = ref({})
const tableScrollHeight = ref(600) // 默认高度

// 计算表格滚动高度（窗口高度减去其他元素高度）
const calculateTableHeight = () => {
  // 窗口高度 - 顶部导航栏(约64px) - 筛选区域(约50px) - Tab区域(约46px) - 分页器(约60px) - 边距(约40px)
  const height = window.innerHeight - 260
  tableScrollHeight.value = Math.max(400, height) // 最小高度400px
}

// 表格列定义（使用函数返回，以便动态更新 filters）
const getColumns = () => [
  {
    title: '股票代码',
    dataIndex: 'symbol',
    key: 'symbol',
    width: 120,
    fixed: 'left',
    sorter: (a, b) => {
      if (!a.symbol || !b.symbol) return 0
      return a.symbol.localeCompare(b.symbol)
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
    title: '行业',
    dataIndex: 'industry',
    key: 'industry',
    width: 150,
    filters: [], // 将在 computed 中动态更新
    onFilter: (value, record) => record.industry === value,
    sorter: (a, b) => {
      if (!a.industry || !b.industry) return 0
      return a.industry.localeCompare(b.industry)
    }
  },
  {
    title: '选股日期',
    dataIndex: 'trade_date',
    key: 'trade_date',
    width: 120,
    sorter: (a, b) => {
      if (!a.trade_date || !b.trade_date) return 0
      return a.trade_date.localeCompare(b.trade_date)
    }
  },
  {
    title: '收盘价',
    key: 'close',
    width: 100,
    align: 'right',
    sorter: (a, b) => {
      const aVal = a.close || 0
      const bVal = b.close || 0
      return aVal - bVal
    }
  },
  {
    title: '涨跌幅',
    key: 'pct_chg',
    width: 100,
    align: 'right',
    sorter: (a, b) => {
      const aVal = a.pct_chg || 0
      const bVal = b.pct_chg || 0
      return aVal - bVal
    }
  },
  {
    title: '成交量（手）',
    key: 'vol',
    width: 120,
    align: 'right',
    sorter: (a, b) => {
      const aVal = a.vol || 0
      const bVal = b.vol || 0
      return aVal - bVal
    }
  },
  {
    title: '成交额（千元）',
    key: 'amount',
    width: 120,
    align: 'right',
    sorter: (a, b) => {
      const aVal = a.amount || 0
      const bVal = b.amount || 0
      return aVal - bVal
    }
  },
  {
    title: '策略评分',
    key: 'score',
    width: 100,
    align: 'right',
    defaultSortOrder: 'descend',
    sorter: (a, b) => {
      const aVal = a.score || 0
      const bVal = b.score || 0
      return aVal - bVal
    }
  },
  {
    title: '选股理由',
    dataIndex: 'reason',
    key: 'reason',
    width: 200,
    ellipsis: true
  },
  {
    title: '操作',
    key: 'action',
    width: 150,
    fixed: 'right'
  }
]

// 使用 computed 包装，以便响应式更新
const columns = computed(() => {
  const cols = getColumns()
  // 更新行业筛选器
  const industryCol = cols.find(col => col.key === 'industry')
  if (industryCol) {
    industryCol.filters = industries.value.map(ind => ({ text: ind, value: ind }))
  }
  return cols
})

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
    loadSelections(page)
  },
  onShowSizeChange: (current, size) => {
    pagination.value.current = 1
    pagination.value.pageSize = size
    loadSelections(1)
  }
}))

// 方法
const formatNumber = (num) => {
  return num.toLocaleString('zh-CN')
}

const formatPctChg = (pct) => {
  return `${pct > 0 ? '+' : ''}${pct.toFixed(2)}%`
}

const getPctChgClass = (pct) => {
  if (!pct) return ''
  return pct > 0 ? 'pct-up' : pct < 0 ? 'pct-down' : ''
}

const isFavorited = (tsCode) => {
  return store.favoriteCodes.includes(tsCode)
}

const handleStrategyChange = (key) => {
  activeStrategy.value = key
  loadDates()
  loadSelections()
}

const handleDateChange = () => {
  pagination.value.current = 1
  loadSelections()
}

const handleFilterChange = () => {
  pagination.value.current = 1
  loadSelections()
}

const resetFilters = () => {
  selectedDate.value = ''
  selectedIndustry.value = ''
  pagination.value.current = 1
  loadSelections()
}

const loadDates = async () => {
  try {
    datesLoading.value = true
    const response = await strategyAPI.getDates({ strategy_name: activeStrategy.value })
    if (response.code === 0) {
      dates.value = response.data
      if (dates.value.length > 0 && !selectedDate.value) {
        selectedDate.value = dates.value[0]
      }
    }
  } catch (error) {
    console.error('加载日期列表失败:', error)
  } finally {
    datesLoading.value = false
  }
}

const loadSelections = async (page = 1) => {
  try {
    loading.value = true
    const params = {
      strategy_name: activeStrategy.value,
      page: page,
      per_page: pagination.value.pageSize
    }
    if (selectedDate.value) {
      params.trade_date = selectedDate.value
    }
    
    const response = await strategyAPI.getSelections(params)
    if (response.code === 0) {
      let data = response.data.selections || []
      
      // 应用行业筛选
      if (selectedIndustry.value) {
        data = data.filter(item => item.industry === selectedIndustry.value)
      }
      
      // 提取行业列表
      const industrySet = new Set()
      data.forEach(item => {
        if (item.industry) {
          industrySet.add(item.industry)
        }
      })
      industries.value = Array.from(industrySet).sort()
      
      selections.value = data
      pagination.value = {
        current: response.data.page || 1,
        pageSize: response.data.per_page || 100,
        total: selectedIndustry.value ? data.length : response.data.total || 0
      }
    } else {
      message.error(response.message || '加载选股结果失败')
    }
  } catch (error) {
    console.error('加载选股结果失败:', error)
    message.error('加载选股结果失败')
  } finally {
    loading.value = false
  }
}

const handleTableChange = (pag, filters, sorter) => {
  // 处理分页
  if (pag && typeof pag === 'object' && 'current' in pag) {
    pagination.value.current = pag.current
    pagination.value.pageSize = pag.pageSize || pagination.value.pageSize
  }
  
  // 保存排序信息（前端排序，不需要重新请求）
  if (sorter && sorter.columnKey) {
    tableSorter.value = {
      field: sorter.columnKey,
      order: sorter.order
    }
  }
  
  // 如果有筛选，应用筛选
  if (filters && filters.industry) {
    selectedIndustry.value = filters.industry[0] || ''
  }
  
  // 重新加载数据
  loadSelections(pagination.value.current)
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
  await loadDates()
  await loadSelections()
  
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
.strategy-content {
  padding: 8px 0;
}

.filter-selector {
  margin-bottom: 8px;
  padding: 8px 12px;
  background: #fafafa;
  border-radius: 4px;
}

.page-container {
  height: 100%;
  display: flex;
  flex-direction: column;
}

.strategy-card {
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.strategy-card :deep(.ant-card-body) {
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  padding: 12px;
}

.strategy-card :deep(.ant-tabs) {
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.strategy-card :deep(.ant-tabs-content-holder) {
  flex: 1;
  overflow: hidden;
}

.strategy-card :deep(.ant-tabs-content) {
  height: 100%;
}

.strategy-card :deep(.ant-tabs-tabpane) {
  height: 100%;
  display: flex;
  flex-direction: column;
}

.number {
  font-family: 'Monaco', 'Menlo', monospace;
}

.pct-up {
  color: #f5222d;
  font-weight: 600;
}

.pct-down {
  color: #52c41a;
  font-weight: 600;
}

.favorited {
  color: #faad14 !important;
  font-weight: 600;
}

.favorited:hover {
  color: #ffc53d !important;
}

.reason-text {
  display: inline-block;
  max-width: 200px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  cursor: help;
}
</style>


