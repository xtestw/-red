<template>
  <div class="page-container">
    <!-- 头部 -->
    <a-card class="header-card" :bordered="false">
      <template #title>
        <h1 style="margin: 0; font-size: 28px; font-weight: 700;">
          📊 板块数据
        </h1>
      </template>
      <template #extra>
        <a-button @click="loadSectorData" :loading="loading">
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
            placeholder="输入板块名称"
            allow-clear
            style="width: 200px"
            @pressEnter="handleSearch"
          />
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
        :data-source="sectorData"
        :loading="loading"
        :pagination="pagination"
        :scroll="{ x: 1200 }"
        @change="handleTableChange"
        row-key="industry"
      >
        <template #bodyCell="{ column, record }">
          <template v-if="column.key === 'industry'">
            <span style="font-weight: 500;">{{ record.industry }}</span>
          </template>
          <template v-else-if="column.key === 'stock_count'">
            <a-tag color="blue">{{ record.stock_count }}</a-tag>
          </template>
          <template v-else-if="column.key === 'avg_market_value'">
            <span v-if="record.avg_market_value">
              {{ formatNumber(record.avg_market_value / 10000, 2) }} 亿元
            </span>
            <span v-else>-</span>
          </template>
          <template v-else-if="column.key === 'total_market_value'">
            <span v-if="record.total_market_value" style="font-weight: 600; color: #1890ff;">
              {{ formatNumber(record.total_market_value / 10000, 2) }} 亿元
            </span>
            <span v-else>-</span>
          </template>
          <template v-else-if="column.key === 'avg_pe'">
            <span v-if="record.avg_pe">
              {{ formatNumber(record.avg_pe, 2) }}
            </span>
            <span v-else>-</span>
          </template>
          <template v-else-if="column.key === 'pe_range'">
            <span v-if="record.min_pe !== null && record.max_pe !== null">
              {{ formatNumber(record.min_pe, 2) }} ~ {{ formatNumber(record.max_pe, 2) }}
            </span>
            <span v-else>-</span>
          </template>
        </template>
      </a-table>
    </a-card>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { industryAPI } from '../api'
import { message } from 'ant-design-vue'
import { SearchOutlined, ReloadOutlined } from '@ant-design/icons-vue'

const loading = ref(false)
const sectorData = ref([])
const filters = reactive({
  keyword: ''
})

// 表格列定义
const columns = [
  {
    title: '排名',
    key: 'rank',
    width: 80,
    customRender: ({ index }) => index + 1
  },
  {
    title: '板块名称',
    dataIndex: 'industry',
    key: 'industry',
    width: 200,
    fixed: 'left',
    sorter: (a, b) => {
      if (!a.industry || !b.industry) return 0
      return a.industry.localeCompare(b.industry)
    }
  },
  {
    title: '股票数量',
    key: 'stock_count',
    width: 120,
    align: 'center',
    sorter: (a, b) => {
      const aVal = a.stock_count || 0
      const bVal = b.stock_count || 0
      return aVal - bVal
    }
  },
  {
    title: '平均市值',
    key: 'avg_market_value',
    width: 150,
    align: 'right',
    sorter: (a, b) => {
      const aVal = a.avg_market_value || 0
      const bVal = b.avg_market_value || 0
      return aVal - bVal
    }
  },
  {
    title: '总市值',
    key: 'total_market_value',
    width: 150,
    align: 'right',
    sorter: (a, b) => {
      const aVal = a.total_market_value || 0
      const bVal = b.total_market_value || 0
      return aVal - bVal
    }
  },
  {
    title: '平均市盈率',
    key: 'avg_pe',
    width: 120,
    align: 'right',
    sorter: (a, b) => {
      const aVal = a.avg_pe || 0
      const bVal = b.avg_pe || 0
      return aVal - bVal
    }
  },
  {
    title: '市盈率范围',
    key: 'pe_range',
    width: 180,
    align: 'right',
    sorter: (a, b) => {
      // 按最小PE排序
      const aVal = a.min_pe || 0
      const bVal = b.min_pe || 0
      return aVal - bVal
    }
  }
]

// 分页配置
const pagination = reactive({
  current: 1,
  pageSize: 20,
  total: 0,
  showSizeChanger: true,
  showTotal: (total) => `共 ${total} 条数据`,
  pageSizeOptions: ['10', '20', '50', '100']
})

// 格式化数字
const formatNumber = (num, decimals = 2) => {
  if (num === null || num === undefined) return '-'
  return Number(num).toFixed(decimals).replace(/\B(?=(\d{3})+(?!\d))/g, ',')
}

// 加载板块数据
const loadSectorData = async () => {
  loading.value = true
  try {
    const result = await industryAPI.getStatistics()
    if (result.code === 0 && result.data) {
      let data = result.data
      
      // 关键词筛选
      if (filters.keyword) {
        const keyword = filters.keyword.toLowerCase()
        data = data.filter(item => 
          item.industry && item.industry.toLowerCase().includes(keyword)
        )
      }
      
      sectorData.value = data
      pagination.total = data.length
    } else {
      message.error('获取板块数据失败')
      sectorData.value = []
    }
  } catch (error) {
    console.error('加载板块数据失败:', error)
    message.error('加载板块数据失败，请稍后重试')
    sectorData.value = []
  } finally {
    loading.value = false
  }
}

// 搜索
const handleSearch = () => {
  pagination.current = 1
  loadSectorData()
}

// 重置
const handleReset = () => {
  filters.keyword = ''
  pagination.current = 1
  loadSectorData()
}

// 表格变化处理
const handleTableChange = (pag) => {
  pagination.current = pag.current
  pagination.pageSize = pag.pageSize
}

onMounted(() => {
  loadSectorData()
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

