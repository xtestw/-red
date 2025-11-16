<template>
  <div class="bigplayer-container">
    <a-card :bordered="false" class="header-card">
      <template #title>
        <h1 style="margin: 0; font-size: 28px; font-weight: 700;">
          👥 知名大佬追踪
        </h1>
      </template>
      <p style="margin: 8px 0 0 0; font-size: 16px; color: rgba(0, 0, 0, 0.65);">
        追踪知名投资者的持仓动态和投资策略
      </p>
    </a-card>

    <!-- 大佬列表 -->
    <a-card :bordered="false" style="margin-top: 24px;">
      <template #title>
        <span style="font-size: 20px; font-weight: 600;">📋 追踪列表</span>
      </template>
      
      <a-input-search
        v-model:value="searchKeyword"
        placeholder="搜索大佬姓名"
        style="width: 300px; margin-bottom: 16px"
        @search="handleSearch"
      />

      <a-spin :spinning="loading">
        <a-table
          :columns="playerColumns"
          :data-source="players"
          :pagination="{ pageSize: 20 }"
          @change="handleTableChange"
        >
          <template #bodyCell="{ column, record }">
            <template v-if="column.key === 'action'">
              <a-button type="link" size="small" @click="viewHoldings(record.id)">
                查看持仓
              </a-button>
            </template>
          </template>
        </a-table>
      </a-spin>
    </a-card>

    <!-- 持仓详情模态框 -->
    <a-modal
      v-model:open="holdingsVisible"
      :title="currentPlayer?.name + ' - 持仓详情'"
      width="90%"
      :footer="null"
    >
      <a-spin :spinning="holdingsLoading">
        <a-table
          :columns="holdingColumns"
          :data-source="holdings"
          :pagination="{ pageSize: 20 }"
        >
          <template #bodyCell="{ column, record }">
            <template v-if="column.key === 'pct_chg'">
              <span :class="record.pct_chg >= 0 ? 'positive' : 'negative'">
                {{ record.pct_chg ? (record.pct_chg > 0 ? '+' : '') + record.pct_chg.toFixed(2) + '%' : '--' }}
              </span>
            </template>
            <template v-else-if="column.key === 'market_value'">
              <span class="number">{{ record.market_value ? formatNumber(record.market_value) : '--' }}</span>
            </template>
          </template>
        </a-table>
      </a-spin>
    </a-modal>

    <!-- 最新动态 -->
    <a-card :bordered="false" style="margin-top: 24px;">
      <template #title>
        <span style="font-size: 20px; font-weight: 600;">📰 最新动态</span>
      </template>
      
      <a-timeline>
        <a-timeline-item v-for="activity in activities" :key="activity.id">
          <template #dot>
            <span style="font-size: 16px;">{{ activity.type === 'buy' ? '📈' : activity.type === 'sell' ? '📉' : '📝' }}</span>
          </template>
          <div>
            <div style="font-weight: 600; margin-bottom: 4px;">
              {{ activity.player_name }} - {{ activity.stock_name }} ({{ activity.stock_code }})
            </div>
            <div style="color: rgba(0, 0, 0, 0.65);">
              {{ activity.description }}
            </div>
            <div style="color: rgba(0, 0, 0, 0.45); font-size: 12px; margin-top: 4px;">
              {{ activity.date }}
            </div>
          </div>
        </a-timeline-item>
      </a-timeline>
    </a-card>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { bigPlayerAPI } from '../api'

const loading = ref(false)
const holdingsLoading = ref(false)
const searchKeyword = ref('')
const players = ref([])
const holdings = ref([])
const activities = ref([])
const holdingsVisible = ref(false)
const currentPlayer = ref(null)

const playerColumns = [
  { title: '姓名', dataIndex: 'name', key: 'name', width: 150 },
  { title: '类型', dataIndex: 'type', key: 'type', width: 120 },
  { title: '简介', dataIndex: 'description', key: 'description' },
  { title: '操作', key: 'action', width: 120 }
]

const holdingColumns = [
  { title: '股票代码', dataIndex: 'stock_code', key: 'stock_code', width: 120 },
  { title: '股票名称', dataIndex: 'stock_name', key: 'stock_name', width: 150 },
  { title: '持仓数量', dataIndex: 'quantity', key: 'quantity', align: 'right', width: 120 },
  { title: '持仓市值（万元）', key: 'market_value', align: 'right', width: 150 },
  { title: '涨跌幅', key: 'pct_chg', align: 'right', width: 100 },
  { title: '更新时间', dataIndex: 'update_date', key: 'update_date', width: 120 }
]

const formatNumber = (num) => {
  return num.toLocaleString('zh-CN')
}

const loadPlayers = async () => {
  loading.value = true
  try {
    const result = await bigPlayerAPI.getPlayers({ keyword: searchKeyword.value })
    if (result.code === 0) {
      players.value = result.data || []
    }
  } catch (error) {
    console.error('加载大佬列表失败:', error)
  } finally {
    loading.value = false
  }
}

const viewHoldings = async (playerId) => {
  holdingsVisible.value = true
  holdingsLoading.value = true
  try {
    const result = await bigPlayerAPI.getHoldings(playerId)
    if (result.code === 0) {
      holdings.value = result.data || []
      currentPlayer.value = players.value.find(p => p.id === playerId)
    }
  } catch (error) {
    console.error('加载持仓详情失败:', error)
  } finally {
    holdingsLoading.value = false
  }
}

const loadActivities = async () => {
  try {
    const result = await bigPlayerAPI.getActivities()
    if (result.code === 0) {
      activities.value = result.data || []
    }
  } catch (error) {
    console.error('加载最新动态失败:', error)
  }
}

const handleSearch = () => {
  loadPlayers()
}

const handleTableChange = () => {
  loadPlayers()
}

onMounted(() => {
  loadPlayers()
  loadActivities()
})
</script>

<style scoped>
.bigplayer-container {
  max-width: 1600px;
  margin: 0 auto;
}

.positive {
  color: #ff4d4f;
  font-weight: 600;
}

.negative {
  color: #52c41a;
  font-weight: 600;
}

.number {
  font-variant-numeric: tabular-nums;
  font-feature-settings: 'tnum';
}
</style>


