<template>
  <a-modal
    v-model:open="visible"
    :title="stockName"
    width="90%"
    :footer="null"
    @cancel="handleClose"
    :maskClosable="false"
  >
    <div v-if="tsCode">
      <a-tabs v-model:activeKey="activeTab" @change="handleTabChange">
        <a-tab-pane key="daily" tab="日线">
          <KlineChart :ts-code="tsCode" type="daily" />
        </a-tab-pane>
        <a-tab-pane key="weekly" tab="周线">
          <KlineChart :ts-code="tsCode" type="weekly" />
        </a-tab-pane>
        <a-tab-pane key="monthly" tab="月线">
          <KlineChart :ts-code="tsCode" type="monthly" />
        </a-tab-pane>
        <a-tab-pane key="moneyflow" tab="资金流向">
          <MoneyflowChart :ts-code="tsCode" />
        </a-tab-pane>
        <a-tab-pane key="indicators" tab="技术指标">
          <TechnicalIndicators :ts-code="tsCode" />
        </a-tab-pane>
        <a-tab-pane key="sector" tab="板块分析">
          <SectorAnalysis :ts-code="tsCode" />
        </a-tab-pane>
      </a-tabs>
      
      <a-divider />
      
      <a-space>
        <a-button type="primary" @click="exportData('csv')">
          <template #icon><DownloadOutlined /></template>
          导出CSV
        </a-button>
        <a-button type="primary" @click="exportData('excel')">
          <template #icon><FileExcelOutlined /></template>
          导出Excel
        </a-button>
      </a-space>
    </div>
    <a-spin v-else :spinning="true" style="width: 100%; padding: 40px; text-align: center;" />
  </a-modal>
</template>

<script setup>
import { ref, watch, computed } from 'vue'
import { stockAPI } from '../api'
import { DownloadOutlined, FileExcelOutlined } from '@ant-design/icons-vue'
import KlineChart from './KlineChart.vue'
import MoneyflowChart from './MoneyflowChart.vue'
import TechnicalIndicators from './TechnicalIndicators.vue'
import SectorAnalysis from './SectorAnalysis.vue'

const props = defineProps({
  open: Boolean,
  tsCode: String
})

const emit = defineEmits(['update:open', 'close'])

const visible = computed({
  get: () => props.open,
  set: (val) => emit('update:open', val)
})

const activeTab = ref('daily')
const stockName = ref('')
const stockInfo = ref(null)

// 加载股票信息
const loadStockInfo = async () => {
  if (!props.tsCode) return
  
  try {
    const result = await stockAPI.getStockDetail(props.tsCode)
    if (result.code === 0) {
      stockInfo.value = result.data
      stockName.value = `${result.data.name} (${result.data.symbol})`
    }
  } catch (error) {
    console.error('加载股票信息失败:', error)
  }
}

const handleTabChange = (key) => {
  activeTab.value = key
}

const handleClose = () => {
  emit('close')
}

const exportData = (format) => {
  stockAPI.export(props.tsCode, { period: 'daily', format })
}

watch(() => props.open, (newVal) => {
  if (newVal && props.tsCode) {
    loadStockInfo()
  }
})

watch(() => props.tsCode, () => {
  if (props.open && props.tsCode) {
    loadStockInfo()
  }
})
</script>

<style scoped>
</style>



