<template>
  <div>
    <a-spin :spinning="loading">
      <a-table
        :columns="columns"
        :data-source="data"
        :pagination="false"
        size="small"
        style="margin-bottom: 24px"
      />
      <div ref="chartRef" style="width: 100%; height: 400px;"></div>
    </a-spin>
  </div>
</template>

<script setup>
import { ref, onMounted, watch, onBeforeUnmount } from 'vue'
import * as echarts from 'echarts'
import { stockAPI } from '../api'

const props = defineProps({
  tsCode: String
})

const chartRef = ref(null)
const chart = ref(null)
const loading = ref(false)
const data = ref([])

const columns = [
  { title: '日期', dataIndex: 'trade_date', key: 'trade_date', width: 120 },
  { title: '小单买入', dataIndex: 'buy_sm_amount', key: 'buy_sm_amount', align: 'right' },
  { title: '小单卖出', dataIndex: 'sell_sm_amount', key: 'sell_sm_amount', align: 'right' },
  { title: '中单买入', dataIndex: 'buy_md_amount', key: 'buy_md_amount', align: 'right' },
  { title: '中单卖出', dataIndex: 'sell_md_amount', key: 'sell_md_amount', align: 'right' },
  { title: '大单买入', dataIndex: 'buy_lg_amount', key: 'buy_lg_amount', align: 'right' },
  { title: '大单卖出', dataIndex: 'sell_lg_amount', key: 'sell_lg_amount', align: 'right' },
  { title: '特大单买入', dataIndex: 'buy_elg_amount', key: 'buy_elg_amount', align: 'right' },
  { title: '特大单卖出', dataIndex: 'sell_elg_amount', key: 'sell_elg_amount', align: 'right' },
  {
    title: '净流入',
    dataIndex: 'net_mf_amount',
    key: 'net_mf_amount',
    align: 'right'
  }
]

const loadData = async () => {
  if (!props.tsCode) return
  
  loading.value = true
  try {
    const result = await stockAPI.getMoneyflow(props.tsCode, { limit: 30 })
    
    if (result.code === 0 && result.data.length > 0) {
      data.value = result.data.reverse()
      
      const dates = data.value.map(d => d.trade_date)
      const netAmounts = data.value.map(d => d.net_mf_amount || 0)
      
      const option = {
        title: {
          text: '资金流向趋势图',
          left: 'center',
          textStyle: { fontSize: 16, fontWeight: 600 }
        },
        tooltip: {
          trigger: 'axis',
          axisPointer: {
            type: 'cross',
            label: { backgroundColor: '#667eea' }
          },
          formatter: function(params) {
            const data = params[0]
            const color = data.value >= 0 ? 'red' : 'green'
            return `${data.name}<br/>${data.seriesName}: <span style="color:${color}">${data.value.toFixed(2)}</span> 万元`
          }
        },
        grid: {
          left: '3%',
          right: '4%',
          bottom: '3%',
          top: '15%',
          containLabel: true
        },
        xAxis: {
          type: 'category',
          data: dates,
          axisLabel: { rotate: 45 }
        },
        yAxis: {
          type: 'value',
          name: '净流入（万元）',
          splitLine: {
            show: true,
            lineStyle: { type: 'dashed' }
          }
        },
        series: [{
          name: '净流入',
          type: 'bar',
          data: netAmounts,
          itemStyle: {
            color: function(params) {
              return params.value >= 0 ? '#dc3545' : '#28a745'
            },
            borderRadius: [4, 4, 0, 0]
          },
          emphasis: {
            itemStyle: {
              shadowBlur: 10,
              shadowOffsetX: 0,
              shadowColor: 'rgba(0, 0, 0, 0.5)'
            }
          }
        }]
      }
      
      if (chart.value) {
        chart.value.setOption(option, true)
      }
    }
  } catch (error) {
    console.error('加载资金流向数据失败:', error)
  } finally {
    loading.value = false
  }
}

const initChart = () => {
  if (chartRef.value && !chart.value) {
    chart.value = echarts.init(chartRef.value)
    window.addEventListener('resize', handleResize)
  }
}

const handleResize = () => {
  if (chart.value) {
    chart.value.resize()
  }
}

onMounted(() => {
  initChart()
  loadData()
})

watch(() => props.tsCode, () => {
  loadData()
})

onBeforeUnmount(() => {
  if (chart.value) {
    chart.value.dispose()
    chart.value = null
  }
  window.removeEventListener('resize', handleResize)
})
</script>

<style scoped>
</style>

