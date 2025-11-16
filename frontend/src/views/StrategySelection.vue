<template>
  <div class="page-container">
    <!-- 头部 -->
    <a-card class="header-card" :bordered="false">
      <template #title>
        <h1 style="margin: 0; font-size: 28px; font-weight: 700;">
          📊 策略选股
        </h1>
      </template>
      <p style="margin: 8px 0 0 0; font-size: 16px; opacity: 0.8;">
        基于多种策略的智能选股系统 | 专业 · 高效 · 智能
      </p>
    </a-card>

    <!-- 策略Tab区域 -->
    <a-card class="strategy-card" :bordered="false" style="margin-top: 24px;">
      <a-tabs v-model:activeKey="activeStrategy" @change="handleStrategyChange">
        <a-tab-pane key="放量策略" tab="放量策略选股">
          <div class="strategy-content">
            <!-- 日期选择 -->
            <div class="date-selector">
              <a-space>
                <span>选股日期：</span>
                <a-select
                  v-model:value="selectedDate"
                  style="width: 200px"
                  placeholder="选择日期"
                  :loading="datesLoading"
                  @change="handleDateChange"
                >
                  <a-select-option v-for="date in dates" :key="date" :value="date">
                    {{ date }}
                  </a-select-option>
                </a-select>
                <a-button type="primary" @click="loadSelections" :loading="loading">
                  <template #icon><ReloadOutlined /></template>
                  刷新
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
              :scroll="{ x: 1200 }"
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
import { ref, computed, onMounted } from 'vue'
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
const dates = ref([])
const datesLoading = ref(false)
const selections = ref([])
const loading = ref(false)
const detailVisible = ref(false)
const currentStockCode = ref('')
const pagination = ref({
  current: 1,
  pageSize: 50,
  total: 0
})

// 表格列定义
const columns = [
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
    title: '收盘价',
    key: 'close',
    width: 100,
    align: 'right'
  },
  {
    title: '涨跌幅',
    key: 'pct_chg',
    width: 100,
    align: 'right'
  },
  {
    title: '成交量（手）',
    key: 'vol',
    width: 120,
    align: 'right'
  },
  {
    title: '成交额（千元）',
    key: 'amount',
    width: 120,
    align: 'right'
  },
  {
    title: '策略评分',
    key: 'score',
    width: 100,
    align: 'right'
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
      selections.value = response.data.selections || []
      pagination.value = {
        current: response.data.page || 1,
        pageSize: response.data.per_page || 50,
        total: response.data.total || 0
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

const handleTableChange = (pag) => {
  loadSelections(pag.current)
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

// 初始化
onMounted(async () => {
  await store.loadFavorites()
  await loadDates()
  await loadSelections()
})
</script>

<style scoped>
.strategy-content {
  padding: 16px 0;
}

.date-selector {
  margin-bottom: 16px;
  padding: 16px;
  background: #fafafa;
  border-radius: 4px;
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
</style>


