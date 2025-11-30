<template>
  <div class="page-container">
    <a-card class="strategy-card" :bordered="false">
      <template #title>
        <span>自定义策略</span>
      </template>
      
      <div class="strategy-content">
        <!-- 策略描述输入 -->
        <div class="input-section">
          <a-textarea
            v-model:value="description"
            placeholder="请描述您的选股策略，例如：筛选出最近30天涨幅超过20%的股票，且成交量是最近120天最高的"
            :rows="6"
            :disabled="generating"
          />
          <div class="button-group">
            <a-button
              type="primary"
              @click="generateSQL"
              :loading="generating"
              :disabled="!description.trim()"
            >
              <template #icon><ThunderboltOutlined /></template>
              生成SQL
            </a-button>
            <a-button @click="clearAll" :disabled="generating">
              清空
            </a-button>
          </div>
        </div>

        <!-- SQL预览 -->
        <div class="sql-section" v-if="generatedSQL">
          <div class="section-title">生成的SQL查询</div>
          <a-textarea
            v-model:value="generatedSQL"
            :rows="8"
            readonly
            class="sql-preview"
          />
          <div class="sql-actions">
            <a-button
              type="default"
              @click="previewSQL"
              :loading="previewing"
              :disabled="!generatedSQL.trim()"
            >
              <template #icon><EyeOutlined /></template>
              预览结果
            </a-button>
          </div>
        </div>

        <!-- 缺失数据提示 -->
        <div class="missing-data-section" v-if="missingTables.length > 0 || missingFields.length > 0">
          <a-alert
            type="warning"
            show-icon
            :message="'缺失的数据'"
            :description="missingDataDescription"
          />
        </div>

        <!-- 预览结果 -->
        <div class="preview-section" v-if="previewData">
          <div class="section-title">
            预览结果
            <span class="preview-count">（共 {{ previewData.count }} 条{{ previewData.has_more ? '，仅显示前1000条' : '' }}）</span>
          </div>
          <a-table
            :columns="previewColumns"
            :data-source="previewData.rows"
            :pagination="{ pageSize: 20, showSizeChanger: true, showTotal: (total) => `共 ${total} 条` }"
            :scroll="{ x: 'max-content' }"
            size="small"
            bordered
          >
            <template #bodyCell="{ column, record }">
              <template v-if="column.dataIndex === 'ts_code'">
                <div>
                  <div>{{ record.ts_code }}</div>
                  <div v-if="previewData.stock_info && previewData.stock_info[record.ts_code]" class="stock-info">
                    <span class="stock-name">{{ previewData.stock_info[record.ts_code].name }}</span>
                    <span v-if="previewData.stock_info[record.ts_code].industry" class="stock-industry">
                      {{ previewData.stock_info[record.ts_code].industry }}
                    </span>
                  </div>
                </div>
              </template>
              <template v-else-if="column.dataIndex === 'pct_chg'">
                <span :class="record.pct_chg >= 0 ? 'text-red' : 'text-green'">
                  {{ record.pct_chg ? (record.pct_chg > 0 ? '+' : '') + record.pct_chg.toFixed(2) + '%' : '-' }}
                </span>
              </template>
              <template v-else-if="column.dataIndex === 'close'">
                {{ record.close ? record.close.toFixed(2) : '-' }}
              </template>
              <template v-else-if="column.dataIndex === 'vol'">
                {{ record.vol ? (record.vol / 10000).toFixed(2) + '万' : '-' }}
              </template>
              <template v-else-if="column.dataIndex === 'amount'">
                {{ record.amount ? (record.amount / 10000).toFixed(2) + '万' : '-' }}
              </template>
            </template>
          </a-table>
        </div>

        <!-- 保存按钮 -->
        <div class="save-section" v-if="generatedSQL">
          <a-button
            type="primary"
            size="large"
            @click="showSaveModal"
            :disabled="!generatedSQL.trim()"
          >
            <template #icon><SaveOutlined /></template>
            保存策略
          </a-button>
        </div>
      </div>
    </a-card>

    <!-- 保存策略对话框 -->
    <a-modal
      v-model:open="saveModalVisible"
      title="保存自定义策略"
      :width="600"
      @ok="handleSave"
      @cancel="handleCancelSave"
      :confirmLoading="saving"
    >
      <a-form :model="saveForm" :label-col="{ span: 6 }" :wrapper-col="{ span: 18 }">
        <a-form-item label="策略名称" required>
          <a-input
            v-model:value="saveForm.name"
            placeholder="请输入策略名称"
            :maxlength="100"
          />
        </a-form-item>
        <a-form-item label="策略描述">
          <a-textarea
            v-model:value="saveForm.description"
            placeholder="可选：策略的详细说明"
            :rows="3"
          />
        </a-form-item>
        <a-form-item label="执行规则" required>
          <a-select v-model:value="saveForm.execution_rule" placeholder="选择执行规则">
            <a-select-option value="daily">每天执行</a-select-option>
            <a-select-option value="weekly">每周执行</a-select-option>
            <a-select-option value="monthly">每月执行</a-select-option>
          </a-select>
        </a-form-item>
        <a-form-item label="执行时间" required>
          <a-time-picker
            v-model:value="saveForm.execution_time"
            format="HH:mm"
            placeholder="选择执行时间"
            style="width: 100%"
          />
        </a-form-item>
      </a-form>
    </a-modal>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { message } from 'ant-design-vue'
import { ThunderboltOutlined, SaveOutlined, EyeOutlined } from '@ant-design/icons-vue'
import { customStrategyAPI } from '../api/index'
import dayjs from 'dayjs'

const description = ref('')
const generatedSQL = ref('')
const missingTables = ref([])
const missingFields = ref([])
const generating = ref(false)
const previewing = ref(false)
const previewData = ref(null)
const saving = ref(false)
const saveModalVisible = ref(false)
const saveForm = ref({
  name: '',
  description: '',
  execution_rule: 'daily',
  execution_time: null
})

const missingDataDescription = computed(() => {
  const parts = []
  if (missingTables.value.length > 0) {
    parts.push(`缺失的数据表：${missingTables.value.join('、')}`)
  }
  if (missingFields.value.length > 0) {
    parts.push(`缺失的字段：${missingFields.value.join('、')}`)
  }
  return parts.join('\n')
})

const generateSQL = async () => {
  if (!description.value.trim()) {
    message.warning('请输入策略描述')
    return
  }

  try {
    generating.value = true
    const response = await customStrategyAPI.generateSQL(description.value)
    
    if (response.code === 0) {
      generatedSQL.value = response.data.sql || ''
      missingTables.value = response.data.missing_tables || []
      missingFields.value = response.data.missing_fields || []
      
      if (generatedSQL.value) {
        message.success('SQL生成成功')
      } else {
        message.warning('未能生成有效的SQL，请检查策略描述')
      }
    } else {
      message.error(response.message || '生成SQL失败')
    }
  } catch (error) {
    console.error('生成SQL失败:', error)
    message.error(error.message || '生成SQL失败')
  } finally {
    generating.value = false
  }
}

const clearAll = () => {
  description.value = ''
  generatedSQL.value = ''
  missingTables.value = []
  missingFields.value = []
  previewData.value = null
}

const previewColumns = computed(() => {
  if (!previewData.value || !previewData.value.columns) {
    return []
  }
  
  return previewData.value.columns.map(col => {
    const column = {
      title: col,
      dataIndex: col,
      key: col,
      width: col === 'ts_code' ? 150 : undefined
    }
    
    // 特殊处理某些列
    if (col === 'ts_code') {
      column.title = '股票代码'
      column.fixed = 'left'
    } else if (col === 'name') {
      column.title = '股票名称'
    } else if (col === 'trade_date') {
      column.title = '交易日期'
      column.width = 120
    } else if (col === 'close') {
      column.title = '收盘价'
      column.width = 100
      column.align = 'right'
    } else if (col === 'pct_chg') {
      column.title = '涨跌幅'
      column.width = 100
      column.align = 'right'
    } else if (col === 'vol') {
      column.title = '成交量'
      column.width = 120
      column.align = 'right'
    } else if (col === 'amount') {
      column.title = '成交额'
      column.width = 120
      column.align = 'right'
    } else if (col === 'industry') {
      column.title = '行业'
      column.width = 120
    }
    
    return column
  })
})

const previewSQL = async () => {
  if (!generatedSQL.value.trim()) {
    message.warning('请先生成SQL')
    return
  }

  try {
    previewing.value = true
    previewData.value = null
    
    const response = await customStrategyAPI.previewSQL(generatedSQL.value)
    
    if (response.code === 0) {
      previewData.value = response.data
      message.success(`预览成功，共找到 ${response.data.count} 条结果`)
    } else {
      message.error(response.message || '预览失败')
    }
  } catch (error) {
    console.error('预览SQL失败:', error)
    message.error(error.response?.data?.message || error.message || '预览失败')
  } finally {
    previewing.value = false
  }
}

const showSaveModal = () => {
  if (!generatedSQL.value.trim()) {
    message.warning('请先生成SQL')
    return
  }
  
  // 重置表单
  saveForm.value = {
    name: '',
    description: description.value,
    execution_rule: 'daily',
    execution_time: dayjs('15:30', 'HH:mm')
  }
  saveModalVisible.value = true
}

const handleSave = async () => {
  if (!saveForm.value.name.trim()) {
    message.warning('请输入策略名称')
    return
  }

  if (!saveForm.value.execution_time) {
    message.warning('请选择执行时间')
    return
  }

  try {
    saving.value = true
    
    const data = {
      name: saveForm.value.name.trim(),
      description: saveForm.value.description || description.value,
      sql_query: generatedSQL.value,
      missing_tables: missingTables.value,
      execution_rule: saveForm.value.execution_rule,
      execution_time: saveForm.value.execution_time.format('HH:mm')
    }

    const response = await customStrategyAPI.createStrategy(data)
    
    if (response.code === 0) {
      message.success('策略保存成功')
      saveModalVisible.value = false
      clearAll()
    } else {
      message.error(response.message || '保存失败')
    }
  } catch (error) {
    console.error('保存策略失败:', error)
    message.error(error.message || '保存策略失败')
  } finally {
    saving.value = false
  }
}

const handleCancelSave = () => {
  saveModalVisible.value = false
}
</script>

<style scoped>
.page-container {
  padding: 16px;
  background: #f0f2f5;
  min-height: calc(100vh - 48px - 60px);
}

.strategy-card {
  background: #fff;
}

.strategy-content {
  padding: 16px 0;
}

.input-section {
  margin-bottom: 24px;
}

.button-group {
  margin-top: 12px;
  display: flex;
  gap: 12px;
}

.sql-section {
  margin-bottom: 24px;
}

.section-title {
  font-weight: 600;
  margin-bottom: 8px;
  color: #333;
}

.sql-preview {
  font-family: 'Monaco', 'Menlo', 'Courier New', monospace;
  font-size: 13px;
  background: #f5f5f5;
}

.missing-data-section {
  margin-bottom: 24px;
}

.sql-actions {
  margin-top: 12px;
  display: flex;
  gap: 12px;
}

.preview-section {
  margin-bottom: 24px;
}

.preview-count {
  font-weight: normal;
  font-size: 14px;
  color: #666;
  margin-left: 8px;
}

.stock-info {
  margin-top: 4px;
  font-size: 12px;
  color: #666;
}

.stock-name {
  font-weight: 500;
  color: #333;
  margin-right: 8px;
}

.stock-industry {
  color: #999;
}

.text-red {
  color: #ff4d4f;
}

.text-green {
  color: #52c41a;
}

.save-section {
  margin-top: 24px;
  text-align: center;
}
</style>

