<template>
  <a-modal
    v-model:open="visible"
    title="股票对比"
    width="90%"
    :footer="null"
    @cancel="handleClose"
  >
    <a-spin :spinning="loading">
      <a-table
        :columns="columns"
        :data-source="compareData"
        :pagination="false"
        :scroll="{ x: 1000 }"
      >
        <template #bodyCell="{ column, record }">
          <template v-if="column.key === 'pct_chg'">
            <span :class="record.pct_chg >= 0 ? 'positive' : 'negative'">
              {{ record.pct_chg ? record.pct_chg.toFixed(2) + '%' : '-' }}
            </span>
          </template>
          <template v-else-if="column.key === 'total_mv'">
            <span class="number">{{ record.total_mv ? formatNumber(record.total_mv) : '-' }}</span>
          </template>
          <template v-else-if="column.key === 'pe'">
            <span class="number">{{ record.pe ? record.pe.toFixed(2) : '-' }}</span>
          </template>
          <template v-else-if="column.key === 'pb'">
            <span class="number">{{ record.pb ? record.pb.toFixed(2) : '-' }}</span>
          </template>
        </template>
      </a-table>
    </a-spin>
  </a-modal>
</template>

<script setup>
import { ref, watch, computed } from 'vue'
import { stockAPI } from '../api'

const props = defineProps({
  open: Boolean,
  tsCodes: Array
})

const emit = defineEmits(['update:open', 'close'])

const visible = computed({
  get: () => props.open,
  set: (val) => emit('update:open', val)
})

const loading = ref(false)
const compareData = ref([])

const columns = [
  { 
    title: '股票代码', 
    dataIndex: 'symbol', 
    key: 'symbol', 
    width: 120,
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
    sorter: (a, b) => {
      if (!a.industry || !b.industry) return 0
      return (a.industry || '').localeCompare(b.industry || '')
    }
  },
  { 
    title: '收盘价', 
    dataIndex: 'close', 
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
    title: '总市值（万元）', 
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
  }
]

const formatNumber = (num) => {
  return num.toLocaleString('zh-CN')
}

const loadCompareData = async () => {
  if (!props.tsCodes || props.tsCodes.length === 0) return
  
  loading.value = true
  try {
    const result = await stockAPI.compare(props.tsCodes)
    if (result.code === 0) {
      compareData.value = result.data
    }
  } catch (error) {
    console.error('加载对比数据失败:', error)
  } finally {
    loading.value = false
  }
}

const handleClose = () => {
  emit('close')
}

watch(() => props.open, (newVal) => {
  if (newVal && props.tsCodes && props.tsCodes.length > 0) {
    loadCompareData()
  }
})

watch(() => props.tsCodes, () => {
  if (props.open && props.tsCodes && props.tsCodes.length > 0) {
    loadCompareData()
  }
})
</script>

<style scoped>
</style>



