<template>
  <div class="sector-analysis">
    <a-spin :spinning="loading">
      <div v-if="sectorData">
        <!-- 板块概览 -->
        <a-card :bordered="false" style="margin-bottom: 24px;">
          <template #title>
            <span style="font-size: 18px; font-weight: 600;">
              📊 {{ sectorData.industry }} 板块分析
            </span>
          </template>
          
          <a-row :gutter="24">
            <a-col :xs="24" :sm="12" :md="6">
              <a-statistic
                title="板块股票数"
                :value="sectorData.stock_count"
                :value-style="{ color: '#1890ff' }"
              />
            </a-col>
            <a-col :xs="24" :sm="12" :md="6">
              <a-statistic
                title="板块平均涨跌幅"
                :value="sectorData.sector_stats.avg_pct_chg"
                suffix="%"
                :precision="2"
                :value-style="{ 
                  color: sectorData.sector_stats.avg_pct_chg >= 0 ? '#ff4d4f' : '#52c41a' 
                }"
              />
            </a-col>
            <a-col :xs="24" :sm="12" :md="6">
              <a-statistic
                title="板块总成交额"
                :value="sectorData.sector_stats.total_amount"
                suffix="亿元"
                :precision="2"
                :value-style="{ color: '#722ed1' }"
              />
            </a-col>
            <a-col :xs="24" :sm="12" :md="6">
              <a-statistic
                title="当前股票排名"
                :value="sectorData.current_stock.rank"
                suffix="名"
                :value-style="{ color: '#fa8c16' }"
              />
            </a-col>
          </a-row>
          
          <a-divider />
          
          <!-- 当前股票信息 -->
          <div class="current-stock-info">
            <h3 style="margin-bottom: 16px;">当前股票信息</h3>
            <a-descriptions :column="3" bordered size="small">
              <a-descriptions-item label="股票名称">
                {{ sectorData.current_stock.name }} ({{ sectorData.current_stock.symbol }})
              </a-descriptions-item>
              <a-descriptions-item label="涨跌幅">
                <span :class="getPctChgClass(sectorData.current_stock.pct_chg)">
                  {{ sectorData.current_stock.pct_chg !== null 
                    ? (sectorData.current_stock.pct_chg > 0 ? '+' : '') + sectorData.current_stock.pct_chg.toFixed(2) + '%'
                    : '--' }}
                </span>
              </a-descriptions-item>
              <a-descriptions-item label="收盘价">
                {{ sectorData.current_stock.close !== null 
                  ? sectorData.current_stock.close.toFixed(2) 
                  : '--' }}
              </a-descriptions-item>
            </a-descriptions>
          </div>
          
          <a-divider />
          
          <!-- 板块涨跌分布 -->
          <div class="sector-distribution">
            <h3 style="margin-bottom: 16px;">板块涨跌分布</h3>
            <a-row :gutter="16">
              <a-col :xs="8" :sm="8" :md="8">
                <a-statistic
                  title="上涨"
                  :value="sectorData.sector_stats.rise_count"
                  :value-style="{ color: '#ff4d4f' }"
                />
              </a-col>
              <a-col :xs="8" :sm="8" :md="8">
                <a-statistic
                  title="下跌"
                  :value="sectorData.sector_stats.fall_count"
                  :value-style="{ color: '#52c41a' }"
                />
              </a-col>
              <a-col :xs="8" :sm="8" :md="8">
                <a-statistic
                  title="平盘"
                  :value="sectorData.sector_stats.flat_count"
                  :value-style="{ color: '#999' }"
                />
              </a-col>
            </a-row>
          </div>
        </a-card>
        
        <!-- 板块内股票排名 -->
        <a-card :bordered="false">
          <template #title>
            <span style="font-size: 18px; font-weight: 600;">
              📈 板块内股票排名（前20名）
            </span>
          </template>
          
          <a-table
            :columns="columns"
            :data-source="sectorData.stock_rankings"
            :pagination="{ pageSize: 20 }"
            size="small"
            :row-class-name="getRowClassName"
          >
            <template #bodyCell="{ column, record }">
              <template v-if="column.key === 'rank'">
                <a-tag :color="getRankColor(record.rank)">
                  {{ record.rank }}
                </a-tag>
              </template>
              <template v-if="column.key === 'name'">
                <span :class="{ 'current-stock': record.ts_code === tsCode }">
                  {{ record.name }} ({{ record.symbol }})
                </span>
              </template>
              <template v-if="column.key === 'pct_chg'">
                <span :class="getPctChgClass(record.pct_chg)">
                  {{ record.pct_chg > 0 ? '+' : '' }}{{ record.pct_chg.toFixed(2) }}%
                </span>
              </template>
              <template v-if="column.key === 'close'">
                {{ record.close !== null ? record.close.toFixed(2) : '--' }}
              </template>
              <template v-if="column.key === 'amount'">
                {{ record.amount.toFixed(2) }} 亿元
              </template>
            </template>
          </a-table>
        </a-card>
      </div>
      
      <a-empty v-else description="暂无板块数据" />
    </a-spin>
  </div>
</template>

<script setup>
import { ref, onMounted, watch } from 'vue'
import { stockAPI } from '../api'

const props = defineProps({
  tsCode: String
})

const loading = ref(false)
const sectorData = ref(null)

const columns = [
  {
    title: '排名',
    key: 'rank',
    dataIndex: 'rank',
    width: 80,
    align: 'center',
    sorter: (a, b) => {
      const aVal = a.rank || 0
      const bVal = b.rank || 0
      return aVal - bVal
    }
  },
  {
    title: '股票名称',
    key: 'name',
    dataIndex: 'name',
    width: 200,
    sorter: (a, b) => {
      if (!a.name || !b.name) return 0
      return a.name.localeCompare(b.name)
    }
  },
  {
    title: '涨跌幅',
    key: 'pct_chg',
    dataIndex: 'pct_chg',
    align: 'right',
    width: 120,
    sorter: (a, b) => {
      const aVal = a.pct_chg || 0
      const bVal = b.pct_chg || 0
      return aVal - bVal
    }
  },
  {
    title: '收盘价',
    key: 'close',
    dataIndex: 'close',
    align: 'right',
    width: 120,
    sorter: (a, b) => {
      const aVal = a.close || 0
      const bVal = b.close || 0
      return aVal - bVal
    }
  },
  {
    title: '成交额',
    key: 'amount',
    dataIndex: 'amount',
    align: 'right',
    width: 150,
    sorter: (a, b) => {
      const aVal = a.amount || 0
      const bVal = b.amount || 0
      return aVal - bVal
    }
  }
]

const loadSectorData = async () => {
  if (!props.tsCode) return
  
  loading.value = true
  try {
    const result = await stockAPI.getSectorAnalysis(props.tsCode)
    if (result.code === 0) {
      sectorData.value = result.data
    } else {
      sectorData.value = null
    }
  } catch (error) {
    console.error('加载板块分析数据失败:', error)
    sectorData.value = null
  } finally {
    loading.value = false
  }
}

const getPctChgClass = (pctChg) => {
  if (pctChg === null || pctChg === undefined) return ''
  return pctChg > 0 ? 'positive' : pctChg < 0 ? 'negative' : ''
}

const getRankColor = (rank) => {
  if (rank <= 3) return 'red'
  if (rank <= 10) return 'orange'
  return 'default'
}

const getRowClassName = (record) => {
  return record.ts_code === props.tsCode ? 'current-stock-row' : ''
}

watch(() => props.tsCode, () => {
  if (props.tsCode) {
    loadSectorData()
  }
})

onMounted(() => {
  if (props.tsCode) {
    loadSectorData()
  }
})
</script>

<style scoped>
.sector-analysis {
  padding: 0;
}

.current-stock-info,
.sector-distribution {
  margin-top: 16px;
}

.current-stock {
  font-weight: 600;
  color: #1890ff;
}

.positive {
  color: #ff4d4f;
  font-weight: 600;
}

.negative {
  color: #52c41a;
  font-weight: 600;
}

:deep(.current-stock-row) {
  background-color: #e6f7ff;
}

:deep(.current-stock-row:hover) {
  background-color: #bae7ff !important;
}
</style>

