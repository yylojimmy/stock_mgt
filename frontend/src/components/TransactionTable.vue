<template>
  <div class="transaction-table">
    <!-- 篩選器 -->
    <div class="filter-section">
      <el-row :gutter="16" class="mb-4">
        <el-col :span="6">
          <el-select
            v-model="filters.stock_code"
            placeholder="選擇股票"
            clearable
            filterable
            @change="handleFilterChange"
          >
            <el-option
              v-for="stock in availableStocks"
              :key="stock.stock_code"
              :label="`${stock.stock_code} - ${stock.stock_name}`"
              :value="stock.stock_code"
            />
          </el-select>
        </el-col>
        <el-col :span="4">
          <el-select
            v-model="filters.transaction_type"
            placeholder="交易類型"
            clearable
            @change="handleFilterChange"
          >
            <el-option label="買入" value="buy" />
            <el-option label="賣出" value="sell" />
          </el-select>
        </el-col>
        <el-col :span="6">
          <el-date-picker
            v-model="dateRange"
            type="daterange"
            range-separator="至"
            start-placeholder="開始日期"
            end-placeholder="結束日期"
            format="YYYY-MM-DD"
            value-format="YYYY-MM-DD"
            @change="handleDateRangeChange"
          />
        </el-col>
        <el-col :span="4">
          <el-button type="primary" @click="handleSearch">
            <el-icon><Search /></el-icon>
            搜索
          </el-button>
        </el-col>
        <el-col :span="4">
          <el-button @click="handleReset">
            <el-icon><Refresh /></el-icon>
            重置
          </el-button>
        </el-col>
      </el-row>
    </div>

    <!-- 批量操作 -->
    <div class="batch-actions" v-if="selectedTransactions.length > 0">
      <el-alert
        :title="`已選擇 ${selectedTransactions.length} 條記錄`"
        type="info"
        show-icon
        :closable="false"
      >
        <template #default>
          <div class="batch-buttons">
            <el-button size="small" type="danger" @click="handleBatchDelete">
              <el-icon><Delete /></el-icon>
              批量刪除
            </el-button>
            <el-button size="small" @click="handleExportSelected">
              <el-icon><Download /></el-icon>
              導出選中
            </el-button>
          </div>
        </template>
      </el-alert>
    </div>

    <!-- 數據表格 -->
    <el-table
      ref="tableRef"
      v-loading="loading"
      :data="transactions"
      stripe
      border
      style="width: 100%"
      @selection-change="handleSelectionChange"
      @sort-change="handleSortChange"
    >
      <!-- 選擇列 -->
      <el-table-column type="selection" width="55" />
      
      <!-- 交易日期 -->
      <el-table-column
        prop="transaction_date"
        label="交易日期"
        width="120"
        sortable="custom"
      >
        <template #default="{ row }">
          {{ formatDate(row.transaction_date) }}
        </template>
      </el-table-column>
      
      <!-- 股票代碼 -->
      <el-table-column prop="stock_code" label="股票代碼" width="120" />
      
      <!-- 交易類型 -->
      <el-table-column prop="transaction_type" label="交易類型" width="100">
        <template #default="{ row }">
          <el-tag :type="row.transaction_type === 'BUY' ? 'success' : 'danger'">
            {{ row.transaction_type === 'BUY' ? '買入' : '賣出' }}
          </el-tag>
        </template>
      </el-table-column>
      
      <!-- 價格 -->
      <el-table-column
        prop="price"
        label="價格"
        width="100"
        sortable="custom"
        align="right"
      >
        <template #default="{ row }">
          {{ formatCurrency(row.price) }}
        </template>
      </el-table-column>
      
      <!-- 股數 -->
      <el-table-column
        prop="shares"
        label="股數"
        width="100"
        sortable="custom"
        align="right"
      >
        <template #default="{ row }">
          {{ formatNumber(row.shares) }}
        </template>
      </el-table-column>
      
      <!-- 總金額 -->
      <el-table-column
        prop="total_amount"
        label="總金額"
        width="120"
        sortable="custom"
        align="right"
      >
        <template #default="{ row }">
          {{ formatCurrency(row.total_amount) }}
        </template>
      </el-table-column>
      
      <!-- 手續費 -->
      <el-table-column
        prop="commission"
        label="手續費"
        width="100"
        align="right"
      >
        <template #default="{ row }">
          {{ formatCurrency(row.commission) }}
        </template>
      </el-table-column>
      
      <!-- 備註 -->
      <el-table-column prop="notes" label="備註" min-width="150">
        <template #default="{ row }">
          <span :title="row.notes">{{ row.notes || '-' }}</span>
        </template>
      </el-table-column>
      
      <!-- 操作 -->
      <el-table-column label="操作" width="120" fixed="right">
        <template #default="{ row }">
          <el-button
            size="small"
            type="primary"
            link
            @click="handleEdit(row)"
          >
            編輯
          </el-button>
          <el-button
            size="small"
            type="danger"
            link
            @click="handleDelete(row)"
          >
            刪除
          </el-button>
        </template>
      </el-table-column>
    </el-table>

    <!-- 分頁 -->
    <div class="pagination-wrapper">
      <el-pagination
        v-model:current-page="pagination.page"
        v-model:page-size="pagination.per_page"
        :page-sizes="[10, 20, 50, 100]"
        :total="pagination.total"
        layout="total, sizes, prev, pager, next, jumper"
        @size-change="handleSizeChange"
        @current-change="handleCurrentChange"
      />
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted, watch } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Search, Refresh, Delete, Download } from '@element-plus/icons-vue'
import { useTransactionStore, useStockStore } from '../stores'

// Props
const props = defineProps({
  // 是否顯示篩選器
  showFilters: {
    type: Boolean,
    default: true
  },
  // 是否顯示批量操作
  showBatchActions: {
    type: Boolean,
    default: true
  },
  // 預設股票代碼篩選
  defaultStockCode: {
    type: String,
    default: ''
  }
})

// Emits
const emit = defineEmits(['edit', 'delete', 'refresh'])

// Stores
const transactionStore = useTransactionStore()
const stockStore = useStockStore()

// 響應式數據
const loading = ref(false)
const tableRef = ref()
const selectedTransactions = ref([])
const dateRange = ref([])

// 篩選條件
const filters = reactive({
  stock_code: props.defaultStockCode,
  transaction_type: '',
  start_date: '',
  end_date: ''
})

// 分頁信息
const pagination = reactive({
  page: 1,
  per_page: 20,
  total: 0,
  pages: 0
})

// 排序信息
const sortInfo = reactive({
  prop: '',
  order: ''
})

// 計算屬性
const transactions = computed(() => transactionStore.transactions || [])
const availableStocks = computed(() => stockStore.stocks || [])

// 格式化函數
const formatDate = (value) => {
  if (!value) return '-'
  return new Date(value).toLocaleDateString('zh-CN')
}

const formatCurrency = (value) => {
  if (value === null || value === undefined) return '0.00'
  return new Intl.NumberFormat('zh-CN', {
    style: 'currency',
    currency: 'CNY',
    minimumFractionDigits: 2
  }).format(value)
}

const formatNumber = (value) => {
  if (value === null || value === undefined) return '0'
  return new Intl.NumberFormat('zh-CN').format(value)
}

// 事件處理函數
const handleFilterChange = () => {
  pagination.page = 1
  fetchTransactions()
}

const handleDateRangeChange = (dates) => {
  if (dates && dates.length === 2) {
    filters.start_date = dates[0]
    filters.end_date = dates[1]
  } else {
    filters.start_date = ''
    filters.end_date = ''
  }
  handleFilterChange()
}

const handleSearch = () => {
  pagination.page = 1
  fetchTransactions()
}

const handleReset = () => {
  // 重置篩選條件
  filters.stock_code = props.defaultStockCode
  filters.transaction_type = ''
  filters.start_date = ''
  filters.end_date = ''
  dateRange.value = []
  
  // 重置分頁
  pagination.page = 1
  
  // 重置排序
  sortInfo.prop = ''
  sortInfo.order = ''
  
  // 清除選擇
  selectedTransactions.value = []
  
  // 重新獲取數據
  fetchTransactions()
}

const handleSelectionChange = (selection) => {
  selectedTransactions.value = selection
}

const handleSortChange = ({ prop, order }) => {
  sortInfo.prop = prop
  sortInfo.order = order
  fetchTransactions()
}

const handleSizeChange = (size) => {
  pagination.per_page = size
  pagination.page = 1
  fetchTransactions()
}

const handleCurrentChange = (page) => {
  pagination.page = page
  fetchTransactions()
}

const handleEdit = (row) => {
  emit('edit', row)
}

const handleDelete = async (row) => {
  try {
    await ElMessageBox.confirm(
      `確定要刪除這條交易記錄嗎？\n股票：${row.stock_code}\n日期：${formatDate(row.transaction_date)}`,
      '確認刪除',
      {
        confirmButtonText: '確定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )
    
    await transactionStore.deleteTransaction(row.id)
    ElMessage.success('交易記錄刪除成功')
    
    // 重新獲取數據
    fetchTransactions()
    
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('刪除失敗：' + (error.message || error))
    }
  }
}

const handleBatchDelete = async () => {
  if (selectedTransactions.value.length === 0) {
    ElMessage.warning('請先選擇要刪除的記錄')
    return
  }
  
  try {
    await ElMessageBox.confirm(
      `確定要刪除選中的 ${selectedTransactions.value.length} 條交易記錄嗎？`,
      '確認批量刪除',
      {
        confirmButtonText: '確定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )
    
    // 批量刪除
    const deletePromises = selectedTransactions.value.map(transaction => 
      transactionStore.deleteTransaction(transaction.id)
    )
    
    await Promise.all(deletePromises)
    ElMessage.success(`成功刪除 ${selectedTransactions.value.length} 條記錄`)
    
    // 清除選擇並重新獲取數據
    selectedTransactions.value = []
    fetchTransactions()
    
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('批量刪除失敗：' + (error.message || error))
    }
  }
}

const handleExportSelected = () => {
  if (selectedTransactions.value.length === 0) {
    ElMessage.warning('請先選擇要導出的記錄')
    return
  }
  
  // 導出選中的交易記錄
  exportTransactions(selectedTransactions.value)
}

// 導出功能
const exportTransactions = (data) => {
  try {
    // 準備CSV數據
    const headers = ['交易日期', '股票代碼', '交易類型', '價格', '股數', '總金額', '手續費', '備註']
    const csvContent = [
      headers.join(','),
      ...data.map(row => [
        formatDate(row.transaction_date),
        row.stock_code,
        row.transaction_type === 'BUY' ? '買入' : '賣出',
        row.price,
        row.shares,
        row.total_amount,
        row.commission,
        `"${row.notes || ''}"`
      ].join(','))
    ].join('\n')
    
    // 創建並下載文件
    const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' })
    const link = document.createElement('a')
    const url = URL.createObjectURL(blob)
    link.setAttribute('href', url)
    link.setAttribute('download', `交易記錄_${new Date().toISOString().split('T')[0]}.csv`)
    link.style.visibility = 'hidden'
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
    
    ElMessage.success('導出成功')
  } catch (error) {
    ElMessage.error('導出失敗：' + error.message)
  }
}

// 獲取交易記錄數據
const fetchTransactions = async () => {
  loading.value = true
  try {
    const params = {
      page: pagination.page,
      per_page: pagination.per_page,
      ...filters
    }
    
    // 添加排序參數
    if (sortInfo.prop && sortInfo.order) {
      params.sort_by = sortInfo.prop
      params.sort_order = sortInfo.order === 'ascending' ? 'asc' : 'desc'
    }
    
    const result = await transactionStore.fetchTransactions(params)
    
    // 更新分頁信息
    if (result && result.pagination) {
      Object.assign(pagination, result.pagination)
    }
    
  } catch (error) {
    ElMessage.error('獲取交易記錄失敗：' + (error.message || error))
  } finally {
    loading.value = false
  }
}

// 公開方法
const refresh = () => {
  fetchTransactions()
}

const exportAll = () => {
  exportTransactions(transactions.value)
}

// 暴露給父組件的方法
defineExpose({
  refresh,
  exportAll
})

// 生命週期
onMounted(async () => {
  // 獲取股票列表用於篩選
  if (stockStore.stocks.length === 0) {
    await stockStore.fetchStocks()
  }
  
  // 獲取交易記錄
  await fetchTransactions()
})

// 監聽默認股票代碼變化
watch(() => props.defaultStockCode, (newValue) => {
  filters.stock_code = newValue
  handleFilterChange()
})
</script>

<style scoped>
.transaction-table {
  width: 100%;
}

.filter-section {
  margin-bottom: 16px;
  padding: 16px;
  background-color: #f5f7fa;
  border-radius: 4px;
}

.batch-actions {
  margin-bottom: 16px;
}

.batch-buttons {
  margin-top: 8px;
}

.batch-buttons .el-button {
  margin-right: 8px;
}

.pagination-wrapper {
  margin-top: 16px;
  text-align: right;
}

/* 響應式設計 */
@media (max-width: 768px) {
  .filter-section .el-row .el-col {
    margin-bottom: 8px;
  }
  
  .pagination-wrapper {
    text-align: center;
  }
  
  .el-table {
    font-size: 12px;
  }
}

@media (max-width: 480px) {
  .filter-section {
    padding: 8px;
  }
  
  .batch-buttons .el-button {
    margin-bottom: 4px;
  }
}
</style>