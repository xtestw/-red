<template>
  <div class="kline-chart-container">
    <a-spin :spinning="loading" tip="加载中...">
      <div ref="chartRef" class="chart-wrapper"></div>
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
    // 根据类型设置不同的limit
    const limit = props.type === 'daily' ? 100 : props.type === 'weekly' ? 200 : 300
    const result = await stockAPI.getKlineData(props.tsCode, props.type, { limit })
    
    if (result.code === 0 && result.data && result.data.length > 0) {
      const data = result.data.reverse()
      
      const dates = data.map(d => {
        // 格式化日期显示
        const dateStr = String(d.trade_date)
        if (dateStr.length === 8) {
          return `${dateStr.substring(0, 4)}-${dateStr.substring(4, 6)}-${dateStr.substring(6, 8)}`
        }
        return dateStr
      })
      const opens = data.map(d => d.open)
      const highs = data.map(d => d.high)
      const lows = data.map(d => d.low)
      const closes = data.map(d => d.close)
      const volumes = data.map(d => d.vol || 0)
      
      const klineData = data.map(d => [
        parseFloat(d.open) || 0,
        parseFloat(d.close) || 0,
        parseFloat(d.low) || 0,
        parseFloat(d.high) || 0
      ])
      
      const chartTitle = props.type === 'daily' ? '日线图' : props.type === 'weekly' ? '周线图' : '月线图'
      
      const option = {
        title: {
          text: chartTitle,
          left: 'center',
          textStyle: {
            fontSize: 16,
            fontWeight: 'bold'
          }
        },
        tooltip: {
          trigger: 'axis',
          axisPointer: {
            type: 'cross'
          },
          formatter: function(params) {
            let result = params[0].axisValue + '<br/>'
            params.forEach(function(item) {
              if (item.seriesName === 'K线') {
                result += item.marker + item.seriesName + '<br/>'
                result += '开盘: ' + item.value[0] + '<br/>'
                result += '收盘: ' + item.value[1] + '<br/>'
                result += '最低: ' + item.value[2] + '<br/>'
                result += '最高: ' + item.value[3] + '<br/>'
              } else {
                result += item.marker + item.seriesName + ': ' + item.value + '<br/>'
              }
            })
            return result
          }
        },
        legend: {
          data: ['K线', '成交量'],
          top: 35
        },
        grid: [
          {
            left: '10%',
            right: '8%',
            top: '18%',
            height: '60%'
          },
          {
            left: '10%',
            right: '8%',
            top: '82%',
            height: '12%'
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
            start: props.type === 'daily' ? 50 : props.type === 'weekly' ? 30 : 20,
            end: 100
          },
          {
            show: true,
            xAxisIndex: [0, 1],
            type: 'slider',
            top: '96%',
            height: 20,
            start: props.type === 'daily' ? 50 : props.type === 'weekly' ? 30 : 20,
            end: 100,
            handleStyle: {
              color: '#1890ff'
            }
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
      } else {
        // 如果图表未初始化，先初始化
        initChart()
        if (chart.value) {
          chart.value.setOption(option, true)
        }
      }
    } else {
      console.warn(`未获取到${chartTitle}数据`)
    }
  } catch (error) {
    console.error(`加载${props.type}K线数据失败:`, error)
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
.kline-chart-container {
  width: 100%;
  min-height: 500px;
}

.chart-wrapper {
  width: 100%;
  height: 500px;
  min-height: 500px;
}

@media (max-width: 768px) {
  .chart-wrapper {
    height: 400px;
    min-height: 400px;
  }
}
</style>



