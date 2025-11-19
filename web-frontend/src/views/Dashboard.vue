<template>
  <div class="dashboard-container">
    <!-- 网站介绍 -->
    <a-card class="intro-card" :bordered="false">
      <template #title>
        <h1 style="margin: 0; font-size: 32px; font-weight: 700;">
          📈 Red-Stock
        </h1>
      </template>
      <div class="intro-content">
        <p style="font-size: 18px; line-height: 1.8; color: rgba(0, 0, 0, 0.65);">
          专业的股票数据分析平台，提供实时行情、技术分析、资金流向、行业统计等全方位数据服务。
          帮助投资者做出更明智的投资决策。
        </p>
        <a-row :gutter="24" style="margin-top: 32px;">
          <a-col :xs="24" :sm="12" :md="6">
            <div class="feature-item">
              <div class="feature-icon">📊</div>
              <h3>实时数据</h3>
              <p>实时获取A股市场数据</p>
            </div>
          </a-col>
          <a-col :xs="24" :sm="12" :md="6">
            <div class="feature-item">
              <div class="feature-icon">📈</div>
              <h3>技术分析</h3>
              <p>多维度技术指标分析</p>
            </div>
          </a-col>
          <a-col :xs="24" :sm="12" :md="6">
            <div class="feature-item">
              <div class="feature-icon">💰</div>
              <h3>资金流向</h3>
              <p>追踪主力资金动向</p>
            </div>
          </a-col>
          <a-col :xs="24" :sm="12" :md="6">
            <div class="feature-item">
              <div class="feature-icon">🔍</div>
              <h3>智能筛选</h3>
              <p>多条件精准筛选股票</p>
            </div>
          </a-col>
        </a-row>
      </div>
    </a-card>

    <!-- 大盘情况 -->
    <a-card class="market-card" :bordered="false" style="margin-top: 24px;">
      <template #title>
        <span style="font-size: 20px; font-weight: 600;">📊 今日大盘情况</span>
      </template>
      
      <a-spin :spinning="marketLoading">
        <a-row :gutter="24">
          <!-- 上证指数 -->
          <a-col :xs="24" :sm="12" :md="8">
            <a-card class="index-card" :bordered="false">
              <div class="index-header">
                <span class="index-name">上证指数</span>
                <span class="index-code">000001.SH</span>
              </div>
              <div class="index-value" :class="getIndexClass(shIndex?.pct_chg)">
                {{ shIndex?.close ? shIndex.close.toFixed(2) : '--' }}
              </div>
              <div class="index-change">
                <span :class="getIndexClass(shIndex?.pct_chg)">
                  {{ shIndex?.pct_chg ? (shIndex.pct_chg > 0 ? '+' : '') + shIndex.pct_chg.toFixed(2) + '%' : '--' }}
                </span>
                <span style="margin-left: 16px; color: #999;">
                  {{ shIndex?.change ? (shIndex.change > 0 ? '+' : '') + shIndex.change.toFixed(2) : '--' }}
                </span>
              </div>
              <div v-if="shIndex?.trade_date" class="index-date">
                日期：{{ formatDate(shIndex.trade_date) }}
              </div>
              <div class="index-detail" v-if="shIndex">
                <a-row :gutter="8" style="margin-top: 12px; font-size: 12px;">
                  <a-col :span="12">
                    <span style="color: #999;">开：</span>
                    <span>{{ shIndex.open ? shIndex.open.toFixed(2) : '--' }}</span>
                  </a-col>
                  <a-col :span="12">
                    <span style="color: #999;">高：</span>
                    <span>{{ shIndex.high ? shIndex.high.toFixed(2) : '--' }}</span>
                  </a-col>
                  <a-col :span="12" style="margin-top: 4px;">
                    <span style="color: #999;">低：</span>
                    <span>{{ shIndex.low ? shIndex.low.toFixed(2) : '--' }}</span>
                  </a-col>
                  <a-col :span="12" style="margin-top: 4px;">
                    <span style="color: #999;">昨收：</span>
                    <span>{{ shIndex.pre_close ? shIndex.pre_close.toFixed(2) : '--' }}</span>
                  </a-col>
                </a-row>
              </div>
            </a-card>
          </a-col>

          <!-- 深证成指 -->
          <a-col :xs="24" :sm="12" :md="8">
            <a-card class="index-card" :bordered="false">
              <div class="index-header">
                <span class="index-name">深证成指</span>
                <span class="index-code">399001.SZ</span>
              </div>
              <div class="index-value" :class="getIndexClass(szIndex?.pct_chg)">
                {{ szIndex?.close ? szIndex.close.toFixed(2) : '--' }}
              </div>
              <div class="index-change">
                <span :class="getIndexClass(szIndex?.pct_chg)">
                  {{ szIndex?.pct_chg ? (szIndex.pct_chg > 0 ? '+' : '') + szIndex.pct_chg.toFixed(2) + '%' : '--' }}
                </span>
                <span style="margin-left: 16px; color: #999;">
                  {{ szIndex?.change ? (szIndex.change > 0 ? '+' : '') + szIndex.change.toFixed(2) : '--' }}
                </span>
              </div>
              <div v-if="szIndex?.trade_date" class="index-date">
                日期：{{ formatDate(szIndex.trade_date) }}
              </div>
              <div class="index-detail" v-if="szIndex">
                <a-row :gutter="8" style="margin-top: 12px; font-size: 12px;">
                  <a-col :span="12">
                    <span style="color: #999;">开：</span>
                    <span>{{ szIndex.open ? szIndex.open.toFixed(2) : '--' }}</span>
                  </a-col>
                  <a-col :span="12">
                    <span style="color: #999;">高：</span>
                    <span>{{ szIndex.high ? szIndex.high.toFixed(2) : '--' }}</span>
                  </a-col>
                  <a-col :span="12" style="margin-top: 4px;">
                    <span style="color: #999;">低：</span>
                    <span>{{ szIndex.low ? szIndex.low.toFixed(2) : '--' }}</span>
                  </a-col>
                  <a-col :span="12" style="margin-top: 4px;">
                    <span style="color: #999;">昨收：</span>
                    <span>{{ szIndex.pre_close ? szIndex.pre_close.toFixed(2) : '--' }}</span>
                  </a-col>
                </a-row>
              </div>
            </a-card>
          </a-col>

          <!-- 创业板指 -->
          <a-col :xs="24" :sm="12" :md="8">
            <a-card class="index-card" :bordered="false">
              <div class="index-header">
                <span class="index-name">创业板指</span>
                <span class="index-code">399006.SZ</span>
              </div>
              <div class="index-value" :class="getIndexClass(cybIndex?.pct_chg)">
                {{ cybIndex?.close ? cybIndex.close.toFixed(2) : '--' }}
              </div>
              <div class="index-change">
                <span :class="getIndexClass(cybIndex?.pct_chg)">
                  {{ cybIndex?.pct_chg ? (cybIndex.pct_chg > 0 ? '+' : '') + cybIndex.pct_chg.toFixed(2) + '%' : '--' }}
                </span>
                <span style="margin-left: 16px; color: #999;">
                  {{ cybIndex?.change ? (cybIndex.change > 0 ? '+' : '') + cybIndex.change.toFixed(2) : '--' }}
                </span>
              </div>
              <div v-if="cybIndex?.trade_date" class="index-date">
                日期：{{ formatDate(cybIndex.trade_date) }}
              </div>
              <div class="index-detail" v-if="cybIndex">
                <a-row :gutter="8" style="margin-top: 12px; font-size: 12px;">
                  <a-col :span="12">
                    <span style="color: #999;">开：</span>
                    <span>{{ cybIndex.open ? cybIndex.open.toFixed(2) : '--' }}</span>
                  </a-col>
                  <a-col :span="12">
                    <span style="color: #999;">高：</span>
                    <span>{{ cybIndex.high ? cybIndex.high.toFixed(2) : '--' }}</span>
                  </a-col>
                  <a-col :span="12" style="margin-top: 4px;">
                    <span style="color: #999;">低：</span>
                    <span>{{ cybIndex.low ? cybIndex.low.toFixed(2) : '--' }}</span>
                  </a-col>
                  <a-col :span="12" style="margin-top: 4px;">
                    <span style="color: #999;">昨收：</span>
                    <span>{{ cybIndex.pre_close ? cybIndex.pre_close.toFixed(2) : '--' }}</span>
                  </a-col>
                </a-row>
              </div>
            </a-card>
          </a-col>
        </a-row>

        <!-- 市场统计 -->
        <a-divider />
        <a-row :gutter="24" style="margin-top: 24px;">
          <a-col :xs="24" :sm="12" :md="6">
            <a-statistic
              title="上涨家数"
              :value="marketStats.rise_count"
              :value-style="{ color: '#ff4d4f' }"
            />
          </a-col>
          <a-col :xs="24" :sm="12" :md="6">
            <a-statistic
              title="下跌家数"
              :value="marketStats.fall_count"
              :value-style="{ color: '#52c41a' }"
            />
          </a-col>
          <a-col :xs="24" :sm="12" :md="6">
            <a-statistic
              title="平盘家数"
              :value="marketStats.flat_count"
              :value-style="{ color: '#999' }"
            />
          </a-col>
          <a-col :xs="24" :sm="12" :md="6">
            <a-statistic
              title="总成交额（亿元）"
              :value="marketStats.total_amount"
              :precision="2"
              :value-style="{ color: '#1890ff' }"
            />
          </a-col>
        </a-row>
      </a-spin>
    </a-card>

    <!-- 热门板块 -->
    <a-card class="sector-card" :bordered="false" style="margin-top: 24px;">
      <template #title>
        <span style="font-size: 20px; font-weight: 600;">🔥 热门板块</span>
      </template>
      <a-spin :spinning="sectorLoading">
        <a-table
          :columns="sectorColumns"
          :data-source="hotSectors"
          :pagination="false"
          size="small"
        >
          <template #bodyCell="{ column, record }">
            <template v-if="column.key === 'pct_chg'">
              <span :class="record.pct_chg >= 0 ? 'positive' : 'negative'">
                {{ record.pct_chg ? (record.pct_chg > 0 ? '+' : '') + record.pct_chg.toFixed(2) + '%' : '--' }}
              </span>
            </template>
          </template>
        </a-table>
      </a-spin>
    </a-card>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { marketAPI } from '../api'

const marketLoading = ref(false)
const sectorLoading = ref(false)
const shIndex = ref(null)
const szIndex = ref(null)
const cybIndex = ref(null)
const marketStats = ref({
  rise_count: 0,
  fall_count: 0,
  flat_count: 0,
  total_amount: 0
})
const hotSectors = ref([])

const sectorColumns = [
  { title: '板块名称', dataIndex: 'name', key: 'name' },
  { title: '涨跌幅', key: 'pct_chg', align: 'right' },
  { title: '成交额（亿元）', dataIndex: 'amount', key: 'amount', align: 'right' }
]

const getIndexClass = (pctChg) => {
  if (!pctChg) return ''
  return pctChg > 0 ? 'positive' : pctChg < 0 ? 'negative' : ''
}

const formatDate = (dateStr) => {
  if (!dateStr) return ''
  // 将 20241118 格式转换为 2024-11-18
  if (dateStr.length === 8) {
    return `${dateStr.substring(0, 4)}-${dateStr.substring(4, 6)}-${dateStr.substring(6, 8)}`
  }
  return dateStr
}

const loadMarketData = async () => {
  marketLoading.value = true
  try {
    const result = await marketAPI.getMarketOverview()
    if (result && result.code === 0) {
      const data = result.data
      shIndex.value = data?.sh_index || null
      szIndex.value = data?.sz_index || null
      cybIndex.value = data?.cyb_index || null
      marketStats.value = data?.stats || marketStats.value
    }
  } catch (error) {
    console.error('加载大盘数据失败:', error)
    // API可能不存在，使用默认值
    console.warn('使用默认数据，后端API可能未实现')
  } finally {
    marketLoading.value = false
  }
}

const loadHotSectors = async () => {
  sectorLoading.value = true
  try {
    const result = await marketAPI.getHotSectors()
    if (result && result.code === 0) {
      hotSectors.value = result.data || []
    }
  } catch (error) {
    console.error('加载热门板块失败:', error)
    // API可能不存在，使用空数组
    hotSectors.value = []
  } finally {
    sectorLoading.value = false
  }
}

onMounted(() => {
  loadMarketData()
  loadHotSectors()
})
</script>

<style scoped>
.dashboard-container {
  max-width: 1600px;
  margin: 0 auto;
}

.intro-content {
  padding: 16px 0;
}

.intro-content p {
  font-size: 18px;
  line-height: 1.8;
  color: rgba(0, 0, 0, 0.65);
  margin-bottom: 0;
}

.feature-item {
  text-align: center;
  padding: 32px 24px;
  background: #fff;
  border: 1px solid #f0f0f0;
  border-radius: 8px;
  transition: all 0.3s;
  height: 100%;
}

.feature-item:hover {
  transform: translateY(-4px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
  border-color: #1890ff;
}

.feature-icon {
  font-size: 56px;
  margin-bottom: 20px;
  transition: transform 0.3s;
}

.feature-item:hover .feature-icon {
  transform: scale(1.1);
}

.feature-item h3 {
  margin: 20px 0 12px 0;
  font-size: 20px;
  font-weight: 600;
  color: rgba(0, 0, 0, 0.85);
}

.feature-item p {
  color: rgba(0, 0, 0, 0.65);
  margin: 0;
  font-size: 14px;
}

.index-card {
  background: #fff;
  border: 1px solid #f0f0f0;
  border-radius: 8px;
  padding: 24px;
  transition: all 0.3s;
}

.index-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
  border-color: #1890ff;
}

.index-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.index-name {
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
  font-size: 36px;
  font-weight: 700;
  margin-bottom: 12px;
  color: rgba(0, 0, 0, 0.85);
}

.index-change {
  font-size: 16px;
  margin-bottom: 8px;
}

.index-date {
  font-size: 12px;
  color: rgba(0, 0, 0, 0.45);
  margin-top: 8px;
}

.index-detail {
  margin-top: 12px;
  padding-top: 12px;
  border-top: 1px solid #f0f0f0;
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


