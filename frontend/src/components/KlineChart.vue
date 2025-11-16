<template>
  <div>
    <a-spin :spinning="loading">
      <div ref="chartRef" style="width: 100%; height: 450px;"></div>
    </a-spin>
  </div>
</template>

<script setup>
import { ref, onMounted, watch, onBeforeUnmount } from 'vue'
import * as echarts from 'echarts'
import { stockAPI } from '../api'

const props = defineProps({
  tsCode: String,
  type: {
    type: String,
    default: 'daily',
    validator: (value) => ['daily', 'weekly', 'monthly'].includes(value)
  }
})

const chartRef = ref(null)
const chart = ref(null)
const loading = ref(false)

const loadData = async () => {
  if (!props.tsCode) return
  
  loading.value = true
  try {
    const result = await stockAPI.getKlineData(props.tsCode, props.type, { limit: 100 })
    
    if (result.code === 0 && result.data.length > 0) {
      const data = result.data.reverse()
      
      const dates = data.map(d => d.trade_date)
      const opens = data.map(d => d.open)
      const highs = data.map(d => d.high)
      const lows = data.map(d => d.low)
      const closes = data.map(d => d.close)
      const volumes = data.map(d => d.vol)
      
      const klineData = data.map(d => [d.open, d.close, d.low, d.high])
      
      const option = {
        title: {
          text: props.type === 'daily' ? '日线图' : props.type === 'weekly' ? '周线图' : '月线图',
          left: 'center'
        },
        tooltip: {
          trigger: 'axis',
          axisPointer: {
            type: 'cross'
          }
        },
        legend: {
          data: ['K线', '成交量'],
          top: 30
        },
        grid: [
          {
            left: '10%',
            right: '8%',
            top: '15%',
            height: '60%'
          },
          {
            left: '10%',
            right: '8%',
            top: '80%',
            height: '15%'
          }
        ],
        xAxis: [
          {
            type: 'category',
            data: dates,
            scale: true,
            boundaryGap: false,
            axisLine: { onZero: false },
            splitLine: { show: false },
            min: 'dataMin',
            max: 'dataMax'
          },
          {
            type: 'category',
            gridIndex: 1,
            data: dates,
            scale: true,
            boundaryGap: false,
            axisLine: { onZero: false },
            axisTick: { show: false },
            splitLine: { show: false },
            min: 'dataMin',
            max: 'dataMax'
          }
        ],
        yAxis: [
          {
            scale: true,
            splitArea: {
              show: true
            }
          },
          {
            scale: true,
            gridIndex: 1,
            splitNumber: 2,
            axisLabel: { show: false },
            axisLine: { show: false },
            axisTick: { show: false },
            splitLine: { show: false }
          }
        ],
        dataZoom: [
          {
            type: 'inside',
            xAxisIndex: [0, 1],
            start: 50,
            end: 100
          },
          {
            show: true,
            xAxisIndex: [0, 1],
            type: 'slider',
            top: '95%',
            start: 50,
            end: 100
          }
        ],
        series: [
          {
            name: 'K线',
            type: 'candlestick',
            data: klineData,
            itemStyle: {
              color: '#ec0000',
              color0: '#00da3c',
              borderColor: '#8A0000',
              borderColor0: '#008F28'
            }
          },
          {
            name: '成交量',
            type: 'bar',
            xAxisIndex: 1,
            yAxisIndex: 1,
            data: volumes,
            itemStyle: {
              color: function(params) {
                const dataIndex = params.dataIndex
                if (dataIndex === 0) return '#c23531'
                return closes[dataIndex] >= closes[dataIndex - 1] ? '#c23531' : '#91c7ae'
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
    console.error('加载K线数据失败:', error)
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

watch([() => props.tsCode, () => props.type], () => {
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



