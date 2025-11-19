<template>
  <div class="data-map-container">
    <!-- 头部信息 -->
    <a-card class="header-card" :bordered="false" size="small">
      <template #title>
        <h2 style="margin: 0; font-size: 20px;">🗺️ 数据地图</h2>
      </template>
      <template #extra>
        <a-space>
          <a-input
            v-model:value="searchKeyword"
            placeholder="搜索表名或字段名"
            allow-clear
            size="small"
            style="width: 250px"
            @change="handleSearch"
          >
            <template #prefix>🔍</template>
          </a-input>
          <a-button size="small" @click="loadSchema" :loading="loading">
            <template #icon><ReloadOutlined /></template>
            刷新
          </a-button>
        </a-space>
      </template>
      <div class="summary-info">
        <a-row :gutter="16">
          <a-col :span="8">
            <a-statistic title="数据库表总数" :value="filteredTables.length" :value-style="{ fontSize: '16px' }" />
          </a-col>
          <a-col :span="8">
            <a-statistic title="总字段数" :value="totalColumns" :value-style="{ fontSize: '16px' }" />
          </a-col>
          <a-col :span="8">
            <a-statistic title="总索引数" :value="totalIndexes" :value-style="{ fontSize: '16px' }" />
          </a-col>
        </a-row>
      </div>
    </a-card>

    <!-- 两列布局 -->
    <div class="content-layout">
      <!-- 左边：表名列表 -->
      <div class="table-list-panel">
        <a-card title="📋 数据表列表" :bordered="false" class="table-list-card">
          <a-list
            :data-source="filteredTables"
            :loading="loading"
            size="small"
            :pagination="false"
          >
            <template #renderItem="{ item }">
              <a-list-item
                :class="{ 'active': selectedTable?.table_name === item.table_name }"
                @click="selectTable(item)"
                style="cursor: pointer; padding: 8px 12px;"
              >
                <a-list-item-meta>
                  <template #title>
                    <div style="display: flex; align-items: center; justify-content: space-between;">
                      <span style="font-weight: 500;">{{ item.table_name }}</span>
                      <a-tag color="blue" size="small">{{ item.column_count }} 字段</a-tag>
                    </div>
                  </template>
                  <template #description>
                    <span v-if="item.comment" style="color: #999; font-size: 12px;">
                      {{ item.comment }}
                    </span>
                    <span v-else style="color: #ccc; font-size: 12px;">无注释</span>
                  </template>
                </a-list-item-meta>
              </a-list-item>
            </template>
          </a-list>
        </a-card>
      </div>

      <!-- 右边：表详情（两个tab） -->
      <div class="table-detail-panel">
        <a-card :bordered="false" class="table-detail-card" v-if="selectedTable">
          <template #title>
            <div>
              <h3 style="margin: 0;">{{ selectedTable.table_name }}</h3>
              <span v-if="selectedTable.comment" style="color: #666; font-size: 12px;">
                {{ selectedTable.comment }}
              </span>
            </div>
          </template>
          
          <a-tabs v-model:activeKey="activeTab">
            <!-- Tab 1: 表结构定义 -->
            <a-tab-pane key="schema" tab="📐 表结构定义">
              <div class="schema-content">
                <!-- 主键信息 -->
                <div v-if="selectedTable.primary_keys && selectedTable.primary_keys.length > 0" class="primary-keys">
                  <span>
                    <strong>主键：</strong>
                    <a-tag v-for="pk in selectedTable.primary_keys" :key="pk" color="red" style="margin-left: 4px;">
                      {{ pk }}
                    </a-tag>
                  </span>
                </div>

                <!-- 字段列表 -->
                <div class="columns-section">
                  <h4>字段列表</h4>
                  <a-table
                    :columns="columnColumns"
                    :data-source="selectedTable.columns"
                    :pagination="false"
                    size="small"
                    :scroll="{ x: 800 }"
                  >
                    <template #bodyCell="{ column, record }">
                      <template v-if="column.key === 'name'">
                        <span style="font-weight: 500; color: #1890ff;">{{ record.name }}</span>
                        <a-tag v-if="record.primary_key" color="red" style="margin-left: 8px;">PK</a-tag>
                      </template>
                      <template v-else-if="column.key === 'type'">
                        <a-tag color="purple">{{ record.type }}</a-tag>
                      </template>
                      <template v-else-if="column.key === 'nullable'">
                        <a-tag :color="record.nullable ? 'default' : 'orange'">
                          {{ record.nullable ? '可空' : '非空' }}
                        </a-tag>
                      </template>
                      <template v-else-if="column.key === 'default'">
                        <span v-if="record.default" style="color: #666;">{{ record.default }}</span>
                        <span v-else style="color: #999;">-</span>
                      </template>
                      <template v-else-if="column.key === 'comment'">
                        <span v-if="record.comment" style="color: #666;">{{ record.comment }}</span>
                        <span v-else style="color: #999;">-</span>
                      </template>
                    </template>
                  </a-table>
                </div>

                <!-- 索引列表 -->
                <div v-if="selectedTable.indexes && selectedTable.indexes.length > 0" class="indexes-section">
                  <h4>索引列表</h4>
                  <a-table
                    :columns="indexColumns"
                    :data-source="selectedTable.indexes"
                    :pagination="false"
                    size="small"
                  >
                    <template #bodyCell="{ column, record }">
                      <template v-if="column.key === 'name'">
                        <span style="font-weight: 500;">{{ record.name }}</span>
                      </template>
                      <template v-else-if="column.key === 'columns'">
                        <a-tag v-for="col in record.columns" :key="col" style="margin-right: 4px;">
                          {{ col }}
                        </a-tag>
                      </template>
                      <template v-else-if="column.key === 'unique'">
                        <a-tag :color="record.unique ? 'green' : 'blue'">
                          {{ record.unique ? '唯一索引' : '普通索引' }}
                        </a-tag>
                      </template>
                    </template>
                  </a-table>
                </div>
              </div>
            </a-tab-pane>

            <!-- Tab 2: 数据预览 -->
            <a-tab-pane key="preview" tab="👁️ 数据预览">
              <div class="preview-content">
                <a-spin :spinning="previewLoading">
                  <div v-if="previewData && previewData.length > 0">
                    <a-alert
                      message="数据预览（仅显示前10条记录）"
                      type="info"
                      show-icon
                      style="margin-bottom: 16px;"
                    />
                    <a-table
                      :columns="previewColumns"
                      :data-source="previewData"
                      :pagination="false"
                      size="small"
                      :scroll="{ x: 'max-content' }"
                    />
                  </div>
                  <a-empty v-else-if="!previewLoading" description="暂无数据" />
                </a-spin>
              </div>
            </a-tab-pane>
          </a-tabs>
        </a-card>

        <!-- 未选择表时的提示 -->
        <a-card :bordered="false" class="table-detail-card" v-else>
          <a-empty description="请从左侧选择一个数据表" />
        </a-card>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { message } from 'ant-design-vue'
import { ReloadOutlined } from '@ant-design/icons-vue'
import { databaseAPI } from '../api'

const loading = ref(false)
const previewLoading = ref(false)
const tables = ref([])
const searchKeyword = ref('')
const selectedTable = ref(null)
const activeTab = ref('schema')
const previewData = ref([])
const previewColumns = ref([])

// 字段列表表格列定义
const columnColumns = [
  {
    title: '字段名',
    dataIndex: 'name',
    key: 'name',
    width: 150,
    fixed: 'left',
    sorter: (a, b) => a.name.localeCompare(b.name)
  },
  {
    title: '数据类型',
    dataIndex: 'type',
    key: 'type',
    width: 150,
    sorter: (a, b) => a.type.localeCompare(b.type)
  },
  {
    title: '可空',
    dataIndex: 'nullable',
    key: 'nullable',
    width: 80,
    align: 'center'
  },
  {
    title: '默认值',
    dataIndex: 'default',
    key: 'default',
    width: 120
  },
  {
    title: '注释',
    dataIndex: 'comment',
    key: 'comment',
    ellipsis: true
  }
]

// 索引列表表格列定义
const indexColumns = [
  {
    title: '索引名',
    dataIndex: 'name',
    key: 'name',
    width: 200,
    sorter: (a, b) => a.name.localeCompare(b.name)
  },
  {
    title: '字段',
    dataIndex: 'columns',
    key: 'columns',
    width: 300
  },
  {
    title: '类型',
    dataIndex: 'unique',
    key: 'unique',
    width: 100,
    align: 'center'
  }
]

// 过滤后的表列表
const filteredTables = computed(() => {
  if (!searchKeyword.value) {
    return tables.value
  }
  
  const keyword = searchKeyword.value.toLowerCase()
  return tables.value.filter(table => {
    // 搜索表名
    if (table.table_name.toLowerCase().includes(keyword)) {
      return true
    }
    // 搜索字段名
    if (table.columns.some(col => col.name.toLowerCase().includes(keyword))) {
      return true
    }
    // 搜索注释
    if (table.comment && table.comment.toLowerCase().includes(keyword)) {
      return true
    }
    return false
  })
})

// 总字段数
const totalColumns = computed(() => {
  return filteredTables.value.reduce((sum, table) => sum + table.column_count, 0)
})

// 总索引数
const totalIndexes = computed(() => {
  return filteredTables.value.reduce((sum, table) => sum + table.index_count, 0)
})

// 选择表
const selectTable = (table) => {
  selectedTable.value = table
  activeTab.value = 'schema'
  // 如果切换到数据预览tab，加载预览数据
  if (activeTab.value === 'preview') {
    loadPreviewData(table.table_name)
  }
}

// 监听tab切换
watch(activeTab, (newTab) => {
  if (newTab === 'preview' && selectedTable.value) {
    loadPreviewData(selectedTable.value.table_name)
  }
})

// 加载数据预览
const loadPreviewData = async (tableName) => {
  if (!tableName) return
  
  previewLoading.value = true
  previewData.value = []
  previewColumns.value = []
  
  try {
    const response = await databaseAPI.getTablePreview(tableName)
    if (response.code === 0 && response.data) {
      const data = response.data.rows || []
      const columns = response.data.columns || []
      
      // 构建预览列
      previewColumns.value = columns.map(col => ({
        title: col,
        dataIndex: col,
        key: col,
        width: 150,
        ellipsis: true
      }))
      
      // 处理预览数据
      previewData.value = data.map((row, index) => ({
        key: index,
        ...row
      }))
    } else {
      message.error('加载数据预览失败')
    }
  } catch (error) {
    console.error('加载数据预览失败:', error)
    message.error('加载数据预览失败，请稍后重试')
  } finally {
    previewLoading.value = false
  }
}

// 加载数据库结构
const loadSchema = async () => {
  loading.value = true
  try {
    const response = await databaseAPI.getSchema()
    if (response.code === 0 && response.data) {
      tables.value = response.data.tables || []
      // 如果之前选择了表，需要重新选择（因为数据更新了）
      if (selectedTable.value) {
        const table = tables.value.find(t => t.table_name === selectedTable.value.table_name)
        if (table) {
          selectedTable.value = table
        }
      }
      message.success('数据加载成功')
    } else {
      message.error('加载数据库结构失败')
    }
  } catch (error) {
    console.error('加载数据库结构失败:', error)
    message.error('加载数据库结构失败，请稍后重试')
  } finally {
    loading.value = false
  }
}

// 搜索处理
const handleSearch = () => {
  // 搜索时清除选择
  if (searchKeyword.value && selectedTable.value) {
    const found = filteredTables.value.find(t => t.table_name === selectedTable.value.table_name)
    if (!found) {
      selectedTable.value = null
    }
  }
}

onMounted(() => {
  loadSchema()
})
</script>

<style scoped>
.data-map-container {
  padding: 0 16px 16px 16px;
  background: #f0f2f5;
  min-height: calc(100vh - 48px - 60px);
}

.header-card {
  margin-bottom: 16px;
}

.header-card :deep(.ant-card-head) {
  min-height: 48px;
  padding: 8px 16px;
}

.header-card :deep(.ant-card-body) {
  padding: 12px 16px 12px 16px;
  border-top: none;
}

.summary-info {
  margin-top: 8px;
  padding-top: 0;
  border-top: none;
}

.summary-info :deep(.ant-statistic-title) {
  font-size: 12px;
  margin-bottom: 4px;
}

.content-layout {
  display: flex;
  gap: 16px;
  height: calc(100vh - 200px);
}

.table-list-panel {
  width: 350px;
  flex-shrink: 0;
}

.table-list-card {
  height: 100%;
  overflow: hidden;
  display: flex;
  flex-direction: column;
}

.table-list-card :deep(.ant-card-body) {
  flex: 1;
  overflow-y: auto;
  padding: 12px;
}

.table-detail-panel {
  flex: 1;
  min-width: 0;
}

.table-detail-card {
  height: 100%;
  display: flex;
  flex-direction: column;
}

.table-detail-card :deep(.ant-card-body) {
  flex: 1;
  overflow-y: auto;
  padding: 16px;
}

.table-detail-card :deep(.ant-tabs) {
  height: 100%;
  display: flex;
  flex-direction: column;
}

.table-detail-card :deep(.ant-tabs-content-holder) {
  flex: 1;
  overflow-y: auto;
}

.table-detail-card :deep(.ant-tabs-tabpane) {
  height: 100%;
}

:deep(.ant-list-item.active) {
  background: #e6f7ff;
  border-left: 3px solid #1890ff;
}

:deep(.ant-list-item:hover) {
  background: #f5f5f5;
}

.primary-keys {
  margin-bottom: 16px;
  padding: 12px;
  background: #fff7e6;
  border-radius: 4px;
}

.columns-section,
.indexes-section {
  margin-top: 16px;
}

.columns-section h4,
.indexes-section h4 {
  margin-bottom: 12px;
  color: #1890ff;
  font-size: 16px;
}

.preview-content {
  min-height: 200px;
}

:deep(.ant-table-thead > tr > th) {
  background: #fafafa;
  font-weight: 600;
}

:deep(.ant-table-tbody > tr:hover > td) {
  background: #f5f5f5;
}
</style>
