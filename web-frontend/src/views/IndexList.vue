<template>
  <div class="page-container">
    <!-- 头部 -->
    <a-card class="header-card" :bordered="false">
      <template #title>
        <h1 style="margin: 0; font-size: 28px; font-weight: 700;">
          📉 指数信息
        </h1>
      </template>
      <template #extra>
        <a-button @click="loadIndexData" :loading="loading">
          <template #icon><ReloadOutlined /></template>
          刷新数据
        </a-button>
      </template>
    </a-card>

    <!-- 筛选区域 -->
    <a-card class="filter-card" :bordered="false">
      <template #title>
        <span>🔍 筛选条件</span>
      </template>
      
      <a-form :model="filters" layout="inline">
        <a-form-item label="关键词搜索">
          <a-input
            v-model:value="filters.keyword"
            placeholder="输入指数代码或名称"
            allow-clear
            style="width: 200px"
            @pressEnter="handleSearch"
          />
        </a-form-item>
        <a-form-item label="市场">
          <a-select
            v-model:value="filters.market"
            placeholder="选择市场"
            allow-clear
            style="width: 150px"
          >
            <a-select-option value="">全部市场</a-select-option>
            <a-select-option value="SSE">上交所</a-select-option>
            <a-select-option value="SZSE">深交所</a-select-option>
            <a-select-option value="CSI">中证指数</a-select-option>
            <a-select-option value="SW">申万指数</a-select-option>
            <a-select-option value="MSCI">MSCI指数</a-select-option>
            <a-select-option value="CICC">中金指数</a-select-option>
            <a-select-option value="OTH">其他指数</a-select-option>
          </a-select>
        </a-form-item>
        <a-form-item label="指数类别">
          <a-select
            v-model:value="filters.category"
            placeholder="选择类别"
            allow-clear
            style="width: 150px"
          >
            <a-select-option value="">全部类别</a-select-option>
            <a-select-option value="主题指数">主题指数</a-select-option>
            <a-select-option value="规模指数">规模指数</a-select-option>
            <a-select-option value="策略指数">策略指数</a-select-option>
            <a-select-option value="风格指数">风格指数</a-select-option>
            <a-select-option value="综合指数">综合指数</a-select-option>
            <a-select-option value="行业指数">行业指数</a-select-option>
          </a-select>
        </a-form-item>
        <a-form-item>
          <a-button type="primary" @click="handleSearch">
            <template #icon><SearchOutlined /></template>
            搜索
          </a-button>
          <a-button style="margin-left: 8px" @click="handleReset">
            重置
          </a-button>
        </a-form-item>
      </a-form>
    </a-card>

    <!-- 数据表格 -->
    <a-card class="table-card" :bordered="false">
      <a-table
        :columns="columns"
        :data-source="indexData"
        :loading="loading"
        :pagination="pagination"
        :scroll="{ x: 1400 }"
        @change="handleTableChange"
        row-key="ts_code"
      >
        <template #bodyCell="{ column, record }">
          <template v-if="column.key === 'ts_code'">
            <span style="font-weight: 500; color: #1890ff;">{{ record.ts_code }}</span>
          </template>
          <template v-else-if="column.key === 'name'">
            <span style="font-weight: 500;">{{ record.name }}</span>
          </template>
          <template v-else-if="column.key === 'market'">
            <a-tag :color="getMarketColor(record.market)">{{ record.market }}</a-tag>
          </template>
          <template v-else-if="column.key === 'category'">
            <a-tag color="purple">{{ record.category || '-' }}</a-tag>
          </template>
          <template v-else-if="column.key === 'close'">
            <span v-if="record.close" style="font-weight: 600;">
              {{ formatNumber(record.close, 2) }}
            </span>
            <span v-else>-</span>
          </template>
          <template v-else-if="column.key === 'pct_chg'">
            <span v-if="record.pct_chg !== null && record.pct_chg !== undefined" :style="{ color: getChangeColor(record.pct_chg) }">
              {{ record.pct_chg > 0 ? '+' : '' }}{{ formatNumber(record.pct_chg, 2) }}%
            </span>
            <span v-else>-</span>
          </template>
          <template v-else-if="column.key === 'pe'">
            <span v-if="record.pe">{{ formatNumber(record.pe, 2) }}</span>
            <span v-else>-</span>
          </template>
          <template v-else-if="column.key === 'pb'">
            <span v-if="record.pb">{{ formatNumber(record.pb, 2) }}</span>
            <span v-else>-</span>
          </template>
          <template v-else-if="column.key === 'total_mv'">
            <span v-if="record.total_mv" style="font-weight: 600; color: #1890ff;">
              {{ formatNumber(record.total_mv / 10000, 2) }} 亿元
            </span>
            <span v-else>-</span>
          </template>
          <template v-else-if="column.key === 'action'">
            <a-button type="link" size="small" @click="viewIndexDetail(record)">
              查看详情
            </a-button>
          </template>
        </template>
      </a-table>
    </a-card>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, computed } from 'vue'
import { indexAPI } from '../api'
import { message } from 'ant-design-vue'
import { SearchOutlined, ReloadOutlined } from '@ant-design/icons-vue'

const loading = ref(false)
const indexData = ref([])
const allIndexData = ref([])
const filters = reactive({
  keyword: '',
  market: '',
  category: ''
})

// 表格列定义
const columns = [
  {
    title: '指数代码',
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
    title: '指数名称',
    dataIndex: 'name',
    key: 'name',
    width: 200,
    fixed: 'left',
    sorter: (a, b) => {
      if (!a.name || !b.name) return 0
      return a.name.localeCompare(b.name)
    }
  },
  {
    title: '市场',
    dataIndex: 'market',
    key: 'market',
    width: 100,
    align: 'center',
    sorter: (a, b) => {
      if (!a.market || !b.market) return 0
      return a.market.localeCompare(b.market)
    }
  },
  {
    title: '发布方',
    dataIndex: 'publisher',
    key: 'publisher',
    width: 120,
    sorter: (a, b) => {
      if (!a.publisher || !b.publisher) return 0
      return a.publisher.localeCompare(b.publisher)
    }
  },
  {
    title: '指数类别',
    dataIndex: 'category',
    key: 'category',
    width: 120,
    sorter: (a, b) => {
      if (!a.category || !b.category) return 0
      return a.category.localeCompare(b.category)
    }
  },
  {
    title: '最新点位',
    key: 'close',
    width: 120,
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
    width: 120,
    align: 'right',
    sorter: (a, b) => {
      const aVal = a.pct_chg || 0
      const bVal = b.pct_chg || 0
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
    title: '市净率',
    key: 'pb',
    width: 100,
    align: 'right',
    sorter: (a, b) => {
      const aVal = a.pb || 0
      const bVal = b.pb || 0
      return aVal - bVal
    }
  },
  {
    title: '总市值（亿元）',
    key: 'total_mv',
    width: 150,
    align: 'right',
    sorter: (a, b) => {
      const aVal = a.total_mv || 0
      const bVal = b.total_mv || 0
      return aVal - bVal
    }
  },
  {
    title: '基期',
    dataIndex: 'base_date',
    key: 'base_date',
    width: 100,
    align: 'center'
  },
  {
    title: '基点',
    dataIndex: 'base_point',
    key: 'base_point',
    width: 100,
    align: 'right',
    sorter: (a, b) => {
      const aVal = a.base_point || 0
      const bVal = b.base_point || 0
      return aVal - bVal
    }
  },
  {
    title: '操作',
    key: 'action',
    width: 100,
    fixed: 'right',
    align: 'center'
  }
]

// 分页配置
const pagination = reactive({
  current: 1,
  pageSize: 50,
  total: 0,
  showSizeChanger: true,
  showQuickJumper: true,
  showTotal: (total) => `共 ${total} 条数据`,
  pageSizeOptions: ['20', '50', '100', '200']
})

// 过滤后的数据
const filteredData = computed(() => {
  let data = [...allIndexData.value]
  
  if (filters.keyword) {
    const keyword = filters.keyword.toLowerCase()
    data = data.filter(item => 
      item.ts_code?.toLowerCase().includes(keyword) ||
      item.name?.toLowerCase().includes(keyword) ||
      item.fullname?.toLowerCase().includes(keyword)
    )
  }
  
  if (filters.market) {
    data = data.filter(item => item.market === filters.market)
  }
  
  if (filters.category) {
    data = data.filter(item => item.category === filters.category)
  }
  
  return data
})

// 加载指数数据
const loadIndexData = async () => {
  loading.value = true
  try {
    const response = await indexAPI.getIndices()
    if (response.code === 0 && response.data) {
      allIndexData.value = response.data.indices || []
      pagination.total = filteredData.value.length
      updateTableData()
      message.success('数据加载成功')
    } else {
      message.error('加载指数数据失败')
    }
  } catch (error) {
    console.error('加载指数数据失败:', error)
    message.error('加载指数数据失败，请稍后重试')
  } finally {
    loading.value = false
  }
}

// 更新表格数据（根据分页）
const updateTableData = () => {
  const start = (pagination.current - 1) * pagination.pageSize
  const end = start + pagination.pageSize
  indexData.value = filteredData.value.slice(start, end)
}

// 搜索
const handleSearch = () => {
  pagination.current = 1
  pagination.total = filteredData.value.length
  updateTableData()
}

// 重置
const handleReset = () => {
  filters.keyword = ''
  filters.market = ''
  filters.category = ''
  handleSearch()
}

// 表格变化处理
const handleTableChange = (pag) => {
  pagination.current = pag.current
  pagination.pageSize = pag.pageSize
  updateTableData()
}

// 查看指数详情
const viewIndexDetail = (record) => {
  message.info(`查看指数详情: ${record.name} (${record.ts_code})`)
  // TODO: 可以跳转到指数详情页面或打开详情模态框
}

// 格式化数字
const formatNumber = (num, decimals = 2) => {
  if (num === null || num === undefined || isNaN(num)) return '-'
  return Number(num).toFixed(decimals)
}

// 获取市场颜色
const getMarketColor = (market) => {
  const colorMap = {
    'SSE': 'red',
    'SZSE': 'blue',
    'CSI': 'green',
    'SW': 'orange',
    'MSCI': 'purple',
    'CICC': 'cyan',
    'OTH': 'default'
  }
  return colorMap[market] || 'default'
}

// 获取涨跌幅颜色
const getChangeColor = (pctChg) => {
  if (pctChg > 0) return '#f5222d'
  if (pctChg < 0) return '#52c41a'
  return '#666'
}

// 监听过滤条件变化
import { watch } from 'vue'
watch([() => filters.keyword, () => filters.market, () => filters.category], () => {
  handleSearch()
})

onMounted(() => {
  loadIndexData()
})
</script>

<style scoped>
.page-container {
  padding: 16px;
  background: #f0f2f5;
  min-height: calc(100vh - 48px - 60px);
}

.header-card {
  margin-bottom: 16px;
}

.filter-card {
  margin-bottom: 16px;
}

.table-card {
  background: #fff;
}

:deep(.ant-table-thead > tr > th) {
  background: #fafafa;
  font-weight: 600;
}

:deep(.ant-table-tbody > tr:hover > td) {
  background: #f5f5f5;
}
</style>


