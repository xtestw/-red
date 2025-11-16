<template>
  <div>
    <a-spin :spinning="loading">
      <!-- 技术信号 -->
      <a-card style="margin-bottom: 24px;">
        <template #title>
          <span>🎯 技术信号</span>
        </template>
        <a-space v-if="signals && Object.keys(signals).length > 0" wrap>
          <a-tag v-if="signals.ma_golden_cross" color="success">MA金叉</a-tag>
          <a-tag v-if="signals.ma_death_cross" color="error">MA死叉</a-tag>
          <a-tag v-if="signals.macd_buy" color="success">MACD买入</a-tag>
          <a-tag v-if="signals.macd_sell" color="error">MACD卖出</a-tag>
          <a-tag v-if="signals.rsi_oversold" color="warning">RSI超卖</a-tag>
          <a-tag v-if="signals.rsi_overbought" color="warning">RSI超买</a-tag>
          <a-tag v-if="signals.kdj_golden_cross" color="success">KDJ金叉</a-tag>
          <a-tag v-if="signals.kdj_death_cross" color="error">KDJ死叉</a-tag>
        </a-space>
        <span v-else>暂无明确信号</span>
      </a-card>

      <!-- 技术指标值 -->
      <a-card style="margin-bottom: 24px;">
        <template #title>
          <span>📈 技术指标值</span>
        </template>
        <a-table
          :columns="indicatorColumns"
          :data-source="indicatorData"
          :pagination="false"
          size="small"
        />
      </a-card>

      <!-- MACD图表 -->
      <div ref="chartRef" style="width: 100%; height: 400px;"></div>
    </a-spin>
  </div>
</template>

<script setup>
import { ref, onMounted, watch, onBeforeUnmount, computed } from 'vue'
import * as echarts from 'echarts'
import { stockAPI } from '../api'

const props = defineProps({
  tsCode: String
})

const chartRef = ref(null)
const chart = ref(null)
const loading = ref(false)
const indicators = ref([])
const signals = ref({})

const indicatorColumns = [
  { title: '指标名称', dataIndex: 'name', key: 'name' },
  { title: '当前数值', dataIndex: 'value', key: 'value', align: 'right' }
]

const indicatorData = computed(() => {
  if (indicators.value.length === 0) return []
  
  const latest = indicators.value[indicators.value.length - 1]
  const data = []
  
  if (latest.ma5) data.push({ name: 'MA5', value: latest.ma5.toFixed(2) })
  if (latest.ma10) data.push({ name: 'MA10', value: latest.ma10.toFixed(2) })
  if (latest.ma20) data.push({ name: 'MA20', value: latest.ma20.toFixed(2) })
  if (latest.ma30) data.push({ name: 'MA30', value: latest.ma30.toFixed(2) })
  if (latest.ma60) data.push({ name: 'MA60', value: latest.ma60.toFixed(2) })
  if (latest.macd !== null) data.push({ name: 'MACD', value: latest.macd.toFixed(4) })
  if (latest.macd_signal !== null) data.push({ name: 'MACD信号线', value: latest.macd_signal.toFixed(4) })
  if (latest.rsi !== null) data.push({ name: 'RSI', value: latest.rsi.toFixed(2) })
  if (latest.kdj_k !== null) data.push({ name: 'KDJ-K', value: latest.kdj_k.toFixed(2) })
  if (latest.kdj_d !== null) data.push({ name: 'KDJ-D', value: latest.kdj_d.toFixed(2) })
  if (latest.kdj_j !== null) data.push({ name: 'KDJ-J', value: latest.kdj_j.toFixed(2) })
  
  return data
})

const loadData = async () => {
  if (!props.tsCode) return
  
  loading.value = true
  try {
    const result = await stockAPI.getIndicators(props.tsCode, { period: 'daily', limit: 100 })
    
    if (result.code === 0 && result.data.indicators.length > 0) {
      indicators.value = result.data.indicators
      signals.value = result.data.signals || {}
      
      // 绘制MACD图表
      const dates = indicators.value.map(i => i.trade_date)
      const macd = indicators.value.map(i => i.macd || 0)
      const signal = indicators.value.map(i => i.macd_signal || 0)
      const hist = indicators.value.map(i => i.macd_hist || 0)
      
      const option = {
        title: {
          text: 'MACD指标走势图',
          left: 'center',
          textStyle: { fontSize: 16, fontWeight: 600 }
        },
        tooltip: {
          trigger: 'axis',
          axisPointer: { type: 'cross' }
        },
        legend: {
          data: ['MACD', '信号线', '柱状图'],
          top: 35
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
          boundaryGap: false
        },
        yAxis: {
          type: 'value',
          splitLine: {
            show: true,
            lineStyle: { type: 'dashed' }
          }
        },
        series: [
          {
            name: 'MACD',
            type: 'line',
            data: macd,
            smooth: true,
            itemStyle: { color: '#667eea' },
            lineStyle: { width: 2 }
          },
          {
            name: '信号线',
            type: 'line',
            data: signal,
            smooth: true,
            itemStyle: { color: '#f093fb' },
            lineStyle: { width: 2 }
          },
          {
            name: '柱状图',
            type: 'bar',
            data: hist,
            itemStyle: {
              color: function(params) {
                return params.value >= 0 ? '#28a745' : '#dc3545'
              }
            }
          }
        ]
      }
      
      if (chart.value) {
        chart.value.setOption(option, true)
      }
    }
  } catch (error) {
    console.error('加载技术指标失败:', error)
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



