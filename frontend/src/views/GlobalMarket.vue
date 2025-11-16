<template>
  <div class="global-market-container">
    <a-card :bordered="false" class="header-card">
      <template #title>
        <h1 style="margin: 0; font-size: 28px; font-weight: 700;">
          🌍 外盘跟踪
        </h1>
      </template>
      <p style="margin: 8px 0 0 0; font-size: 16px; color: rgba(0, 0, 0, 0.65);">
        实时跟踪全球主要市场指数和热门股票
      </p>
    </a-card>

    <!-- 主要市场指数 -->
    <a-card :bordered="false" style="margin-top: 24px;">
      <template #title>
        <span style="font-size: 20px; font-weight: 600;">📊 主要市场指数</span>
      </template>
      
      <a-spin :spinning="indexLoading">
        <a-row :gutter="24">
          <a-col
            v-for="index in marketIndices"
            :key="index.code"
            :xs="24"
            :sm="12"
            :md="8"
            :lg="6"
            style="margin-bottom: 16px"
          >
            <a-card class="index-card" :bordered="false">
              <div class="index-header">
                <span class="index-name">{{ index.name }}</span>
                <span class="index-code">{{ index.code }}</span>
              </div>
              <div class="index-value" :class="getIndexClass(index.pct_chg)">
                {{ index.value ? index.value.toFixed(2) : '--' }}
              </div>
              <div class="index-change">
                <span :class="getIndexClass(index.pct_chg)">
                  {{ index.pct_chg ? (index.pct_chg > 0 ? '+' : '') + index.pct_chg.toFixed(2) + '%' : '--' }}
                </span>
                <span style="margin-left: 16px; color: rgba(0, 0, 0, 0.45); font-size: 12px;">
                  {{ index.time || '--' }}
                </span>
              </div>
            </a-card>
          </a-col>
        </a-row>
      </a-spin>
    </a-card>

    <!-- 热门外盘股票 -->
    <a-card :bordered="false" style="margin-top: 24px;">
      <template #title>
        <span style="font-size: 20px; font-weight: 600;">🔥 热门外盘股票</span>
      </template>
      
      <a-tabs v-model:activeKey="activeTab" @change="handleTabChange">
        <a-tab-pane key="us" tab="美股">
          <a-table
            :columns="stockColumns"
            :data-source="usStocks"
            :loading="stockLoading"
            :pagination="{ pageSize: 20 }"
          >
            <template #bodyCell="{ column, record }">
              <template v-if="column.key === 'pct_chg'">
                <span :class="record.pct_chg >= 0 ? 'positive' : 'negative'">
                  {{ record.pct_chg ? (record.pct_chg > 0 ? '+' : '') + record.pct_chg.toFixed(2) + '%' : '--' }}
                </span>
              </template>
            </template>
          </a-table>
        </a-tab-pane>
        
        <a-tab-pane key="hk" tab="港股">
          <a-table
            :columns="stockColumns"
            :data-source="hkStocks"
            :loading="stockLoading"
            :pagination="{ pageSize: 20 }"
          >
            <template #bodyCell="{ column, record }">
              <template v-if="column.key === 'pct_chg'">
                <span :class="record.pct_chg >= 0 ? 'positive' : 'negative'">
                  {{ record.pct_chg ? (record.pct_chg > 0 ? '+' : '') + record.pct_chg.toFixed(2) + '%' : '--' }}
                </span>
              </template>
            </template>
          </a-table>
        </a-tab-pane>
      </a-tabs>
    </a-card>

    <!-- 外汇市场 -->
    <a-card :bordered="false" style="margin-top: 24px;">
      <template #title>
        <span style="font-size: 20px; font-weight: 600;">💱 外汇市场</span>
      </template>
      
      <a-spin :spinning="forexLoading">
        <a-row :gutter="24">
          <a-col
            v-for="forex in forexData"
            :key="forex.pair"
            :xs="24"
            :sm="12"
            :md="8"
            :lg="6"
            style="margin-bottom: 16px"
          >
            <a-card class="forex-card" :bordered="false">
              <div class="forex-header">
                <span class="forex-pair">{{ forex.pair }}</span>
              </div>
              <div class="forex-value">
                {{ forex.rate ? forex.rate.toFixed(4) : '--' }}
              </div>
              <div class="forex-change" :class="getIndexClass(forex.change)">
                {{ forex.change ? (forex.change > 0 ? '+' : '') + forex.change.toFixed(4) : '--' }}
              </div>
            </a-card>
          </a-col>
        </a-row>
      </a-spin>
    </a-card>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { globalMarketAPI } from '../api'

const indexLoading = ref(false)
const stockLoading = ref(false)
const forexLoading = ref(false)
const activeTab = ref('us')
const marketIndices = ref([])
const usStocks = ref([])
const hkStocks = ref([])
const forexData = ref([])

const stockColumns = [
  { title: '代码', dataIndex: 'code', key: 'code', width: 120 },
  { title: '名称', dataIndex: 'name', key: 'name', width: 150 },
  { title: '最新价', dataIndex: 'price', key: 'price', align: 'right', width: 120 },
  { title: '涨跌幅', key: 'pct_chg', align: 'right', width: 100 },
  { title: '成交量', dataIndex: 'volume', key: 'volume', align: 'right', width: 120 }
]

const getIndexClass = (pctChg) => {
  if (!pctChg && pctChg !== 0) return ''
  return pctChg > 0 ? 'positive' : pctChg < 0 ? 'negative' : ''
}

const loadMarketIndices = async () => {
  indexLoading.value = true
  try {
    const result = await globalMarketAPI.getMarketIndices()
    if (result.code === 0) {
      marketIndices.value = result.data || []
    }
  } catch (error) {
    console.error('加载市场指数失败:', error)
  } finally {
    indexLoading.value = false
  }
}

const loadStocks = async (market) => {
  stockLoading.value = true
  try {
    const result = await globalMarketAPI.getStocks(market)
    if (result.code === 0) {
      if (market === 'us') {
        usStocks.value = result.data || []
      } else if (market === 'hk') {
        hkStocks.value = result.data || []
      }
    }
  } catch (error) {
    console.error('加载股票数据失败:', error)
  } finally {
    stockLoading.value = false
  }
}

const loadForex = async () => {
  forexLoading.value = true
  try {
    const result = await globalMarketAPI.getForex()
    if (result.code === 0) {
      forexData.value = result.data || []
    }
  } catch (error) {
    console.error('加载外汇数据失败:', error)
  } finally {
    forexLoading.value = false
  }
}

const handleTabChange = (key) => {
  activeTab.value = key
  loadStocks(key)
}

onMounted(() => {
  loadMarketIndices()
  loadStocks('us')
  loadForex()
})
</script>

<style scoped>
.global-market-container {
  max-width: 1600px;
  margin: 0 auto;
}

.index-card,
.forex-card {
  background: #fff;
  border: 1px solid #f0f0f0;
  border-radius: 8px;
  padding: 24px;
  transition: all 0.3s;
}

.index-card:hover,
.forex-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
  border-color: #1890ff;
}

.index-header,
.forex-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.index-name,
.forex-pair {
  font-size: 18px;
  font-weight: 600;
  color: rgba(0, 0, 0, 0.85);
}

.index-code {
  font-size: 12px;
  color: rgba(0, 0, 0, 0.45);
  background: #f5f5f5;
  padding: 4px 8px;
  border-radius: 4px;
}

.index-value {
  font-size: 32px;
  font-weight: 700;
  margin-bottom: 12px;
  color: rgba(0, 0, 0, 0.85);
}

.forex-value {
  font-size: 28px;
  font-weight: 700;
  margin-bottom: 12px;
  color: rgba(0, 0, 0, 0.85);
}

.index-change,
.forex-change {
  font-size: 16px;
}

.positive {
  color: #ff4d4f;
  font-weight: 600;
}

.negative {
  color: #52c41a;
  font-weight: 600;
}
</style>


