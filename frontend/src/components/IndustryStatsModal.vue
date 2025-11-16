<template>
  <a-modal
    v-model:open="visible"
    title="行业统计"
    width="90%"
    :footer="null"
    @cancel="handleClose"
  >
    <a-spin :spinning="loading">
      <a-table
        :columns="columns"
        :data-source="statsData"
        :pagination="{ pageSize: 20 }"
        :scroll="{ x: 1000 }"
      >
        <template #bodyCell="{ column, record }">
          <template v-if="column.key === 'avg_market_value'">
            <span class="number">{{ record.avg_market_value ? formatNumber(record.avg_market_value) : '-' }}</span>
          </template>
          <template v-else-if="column.key === 'total_market_value'">
            <span class="number">{{ record.total_market_value ? formatNumber(record.total_market_value) : '-' }}</span>
          </template>
          <template v-else-if="column.key === 'avg_pe'">
            <span class="number">{{ record.avg_pe ? record.avg_pe.toFixed(2) : '-' }}</span>
          </template>
          <template v-else-if="column.key === 'min_pe'">
            <span class="number">{{ record.min_pe ? record.min_pe.toFixed(2) : '-' }}</span>
          </template>
          <template v-else-if="column.key === 'max_pe'">
            <span class="number">{{ record.max_pe ? record.max_pe.toFixed(2) : '-' }}</span>
          </template>
        </template>
      </a-table>
    </a-spin>
  </a-modal>
</template>

<script setup>
import { ref, watch, computed } from 'vue'
import { industryAPI } from '../api'

const props = defineProps({
  open: Boolean
})

const emit = defineEmits(['update:open', 'close'])

const visible = computed({
  get: () => props.open,
  set: (val) => emit('update:open', val)
})

const loading = ref(false)
const statsData = ref([])

const columns = [
  { title: '行业', dataIndex: 'industry', key: 'industry', width: 200 },
  { title: '股票数量', dataIndex: 'stock_count', key: 'stock_count', width: 120, align: 'right' },
  { title: '平均市值（万元）', key: 'avg_market_value', width: 150, align: 'right' },
  { title: '总市值（万元）', key: 'total_market_value', width: 150, align: 'right' },
  { title: '平均PE', key: 'avg_pe', width: 100, align: 'right' },
  { title: '最低PE', key: 'min_pe', width: 100, align: 'right' },
  { title: '最高PE', key: 'max_pe', width: 100, align: 'right' }
]

const formatNumber = (num) => {
  return num.toLocaleString('zh-CN', { maximumFractionDigits: 0 })
}

const loadStats = async () => {
  loading.value = true
  try {
    const result = await industryAPI.getStatistics()
    if (result.code === 0) {
      statsData.value = result.data
    }
  } catch (error) {
    console.error('加载行业统计失败:', error)
  } finally {
    loading.value = false
  }
}

const handleClose = () => {
  emit('close')
}

watch(() => props.open, (newVal) => {
  if (newVal) {
    loadStats()
  }
})
</script>

<style scoped>
</style>

