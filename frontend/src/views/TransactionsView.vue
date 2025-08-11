<template>
  <div class="transactions-view">
    <!-- 頁面標題 -->
    <div class="page-header">
      <h1 class="page-title">交易記錄管理</h1>
      <div class="header-actions">
        <el-button type="primary" @click="handleAddTransaction">
          <el-icon><Plus /></el-icon>
          新增交易
        </el-button>
      </div>
    </div>

    <!-- 篩選區域 - 已隱藏，使用TransactionTable組件中的篩選功能 -->
    <el-card class="filter-card" shadow="never" v-if="false">
      <div class="filter-container">
        <el-row :gutter="16">
          <!-- 股票代碼篩選 -->
          <el-col :xs="24" :sm="12" :md="6" :lg="4">
            <el-form-item label="股票代碼">
              <el-select
                v-model="filters.stock_code"
                placeholder="全部股票"
                clearable
                filterable
                style="width: 100%"
                @change="handleFilterChange"
              >
                <el-option label="全部股票" value="" />
                <el-option
                  v-for="stock in availableStocks"
                  :key="stock.stock_code"
                  :label="`${stock.stock_code} - ${stock.stock_name}`"
                  :value="stock.stock_code"
                />
              </el-select>
            </el-form-item>
          </el-col>

          <!-- 交易類型篩選 -->
          <el-col :xs="24" :sm="12" :md="6" :lg="4">
            <el-form-item label="交易類型">
              <el-select
                v-model="filters.transaction_type"
                placeholder="全部類型"
                clearable
                style="width: 100%"
                @change="handleFilterChange"
              >
                <el-option label="全部類型" value="" />
                <el-option label="買入" value="buy" />
                <el-option label="賣出" value="sell" />
              </el-select>
            </el-form-item>
          </el-col>

          <!-- 日期範圍篩選 -->
          <el-col :xs="24" :sm="12" :md="8" :lg="6">
            <el-form-item label="交易日期">
              <el-date-picker
                v-model="filters.date_range"
                type="daterange"
                range-separator="至"
                start-placeholder="開始日期"
                end-placeholder="結束日期"
                format="YYYY-MM-DD"
                value-format="YYYY-MM-DD"
                style="width: 100%"
                @change="handleFilterChange"
              />
            </el-form-item>
          </el-col>

          <!-- 搜索和重置按鈕 -->
          <el-col :xs="24" :sm="12" :md="4" :lg="4">
            <el-form-item>
              <div class="filter-buttons">
                <el-button type="primary" @click="handleSearch">
                  <el-icon><Search /></el-icon>
                  搜索
                </el-button>
                <el-button @click="handleResetFilters">
                  <el-icon><Refresh /></el-icon>
                  重置
                </el-button>
              </div>
            </el-form-item>
          </el-col>
        </el-row>
      </div>
    </el-card>

    <!-- 批量操作區域 -->
    <el-card class="batch-operations" shadow="never" v-if="selectedTransactions.length > 0">
      <div class="batch-info">
        <span>已選擇 {{ selectedTransactions.length }} 條記錄</span>
        <div class="batch-actions">
          <el-button
            type="danger"
            size="small"
            @click="handleBatchDelete"
            :loading="batchDeleteLoading"
          >
            <el-icon><Delete /></el-icon>
            批量刪除
          </el-button>
          <el-button
            type="success"
            size="small"
            @click="handleBatchExport"
            :loading="batchExportLoading"
          >
            <el-icon><Download /></el-icon>
            導出選中
          </el-button>
        </div>
      </div>
    </el-card>

    <!-- 數據導出區域 -->
    <el-card class="export-card" shadow="never">
      <div class="export-container">
        <div class="export-info">
          <span>數據導出</span>
          <el-text type="info" size="small">
            共 {{ pagination.total }} 條記錄
          </el-text>
        </div>
        <div class="export-actions">
          <el-button
            type="success"
            size="small"
            @click="handleExportAll"
            :loading="exportAllLoading"
          >
            <el-icon><Download /></el-icon>
            導出全部
          </el-button>
          <el-button
            type="primary"
            size="small"
            @click="handleExportFiltered"
            :loading="exportFilteredLoading"
          >
            <el-icon><DocumentCopy /></el-icon>
            導出篩選結果
          </el-button>
        </div>
      </div>
    </el-card>

    <!-- 交易記錄表格 -->
    <el-card class="table-card" shadow="never">
      <TransactionTable
        ref="transactionTableRef"
        @edit="handleEditTransaction"
        @delete="handleDeleteTransaction"
        @refresh="handleRefresh"
      />
    </el-card>

    <!-- 交易記錄表單對話框 -->
    <TransactionForm
      v-model:visible="formVisible"
      :edit-data="editingTransaction"
      @success="handleFormSuccess"
      @cancel="handleFormCancel"
    />
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted, watch } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus, Search, Refresh, Delete, Download, DocumentCopy } from '@element-plus/icons-vue'
import TransactionTable from '../components/TransactionTable.vue'
import TransactionForm from '../components/TransactionForm.vue'
import { useTransactionStore, useStockStore } from '../stores'

// Stores
const transactionStore = useTransactionStore()
const stockStore = useStockStore()

// 響應式數據
const loading = ref(false)
const formVisible = ref(false)
const editingTransaction = ref(null)
const selectedTransactions = ref([])
const batchDeleteLoading = ref(false)
const batchExportLoading = ref(false)
const exportAllLoading = ref(false)
const exportFilteredLoading = ref(false)
const transactionTableRef = ref()

// 篩選條件
const filters = reactive({
  stock_code: '',
  transaction_type: '',
  date_range: null
})

// 分頁數據
const pagination = reactive({
  current: 1,
  size: 20,
  total: 0,
  sizes: [10, 20, 50, 100]
})

// 排序數據
const sorting = reactive({
  prop: 'transaction_date',
  order: 'descending'
})

// 計算屬性
const transactions = computed(() => transactionStore.transactions)
const availableStocks = computed(() => stockStore.stocks)

// 格式化函數
const formatCurrency = (value) => {
  if (value === null || value === undefined) return '0.00'
  return new Intl.NumberFormat('zh-CN', {
    minimumFractionDigits: 2,
    maximumFractionDigits: 2
  }).format(value)
}

const formatNumber = (value) => {
  if (value === null || value === undefined) return '0'
  return new Intl.NumberFormat('zh-CN').format(value)
}

// 事件處理函數
const handleAddTransaction = () => {
  editingTransaction.value = null
  formVisible.value = true
}

const handleEditTransaction = (transaction) => {
  editingTransaction.value = { ...transaction }
  formVisible.value = true
}

const handleDeleteTransaction = async (transaction) => {
  try {
    await transactionStore.deleteTransaction(transaction.id)
    ElMessage.success('交易記錄刪除成功')
    
    // 刷新數據
    if (transactionTableRef.value) {
      transactionTableRef.value.refresh()
    }
    
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
      `確定要刪除選中的 ${selectedTransactions.value.length} 條交易記錄嗎？此操作不可撤銷。`,
      '確認批量刪除',
      {
        confirmButtonText: '確定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )
    
    batchDeleteLoading.value = true
    
    // 批量刪除
    const deletePromises = selectedTransactions.value.map(transaction => 
      transactionStore.deleteTransaction(transaction.id)
    )
    
    await Promise.all(deletePromises)
    
    ElMessage.success(`成功刪除 ${selectedTransactions.value.length} 條記錄`)
    
    // 清空選擇並刷新數據
    selectedTransactions.value = []
    await fetchTransactions()
    
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('批量刪除失敗：' + (error.message || error))
    }
  } finally {
    batchDeleteLoading.value = false
  }
}

const handleBatchExport = async () => {
  if (selectedTransactions.value.length === 0) {
    ElMessage.warning('請先選擇要導出的記錄')
    return
  }
  
  try {
    batchExportLoading.value = true
    
    // 導出選中的交易記錄
    const exportData = selectedTransactions.value.map(transaction => ({
      股票代碼: transaction.stock_code,
      股票名稱: transaction.stock_name,
      交易類型: transaction.transaction_type === 'BUY' ? '買入' : '賣出',
      交易日期: transaction.transaction_date,
      交易價格: formatCurrency(transaction.price),
      交易股數: formatNumber(transaction.shares),
      總金額: formatCurrency(transaction.total_amount),
      手續費: formatCurrency(transaction.commission),
      備註: transaction.notes || ''
    }))
    
    await exportToCSV(exportData, `交易記錄_選中_${new Date().toISOString().split('T')[0]}.csv`)
    
    ElMessage.success(`成功導出 ${selectedTransactions.value.length} 條記錄`)
    
  } catch (error) {
    ElMessage.error('導出失敗：' + (error.message || error))
  } finally {
    batchExportLoading.value = false
  }
}

const handleExportAll = async () => {
  try {
    exportAllLoading.value = true
    
    // 獲取所有交易記錄
    const allTransactions = await transactionStore.fetchAllTransactions()
    
    const exportData = allTransactions.map(transaction => ({
      股票代碼: transaction.stock_code,
      股票名稱: transaction.stock_name,
      交易類型: transaction.transaction_type === 'BUY' ? '買入' : '賣出',
      交易日期: transaction.transaction_date,
      交易價格: formatCurrency(transaction.price),
      交易股數: formatNumber(transaction.shares),
      總金額: formatCurrency(transaction.total_amount),
      手續費: formatCurrency(transaction.commission),
      備註: transaction.notes || ''
    }))
    
    await exportToCSV(exportData, `交易記錄_全部_${new Date().toISOString().split('T')[0]}.csv`)
    
    ElMessage.success(`成功導出 ${allTransactions.length} 條記錄`)
    
  } catch (error) {
    ElMessage.error('導出失敗：' + (error.message || error))
  } finally {
    exportAllLoading.value = false
  }
}

const handleExportFiltered = async () => {
  try {
    exportFilteredLoading.value = true
    
    // 獲取篩選後的交易記錄
    const filteredTransactions = await transactionStore.fetchFilteredTransactions(buildFilterParams())
    
    const exportData = filteredTransactions.map(transaction => ({
      股票代碼: transaction.stock_code,
      股票名稱: transaction.stock_name,
      交易類型: transaction.transaction_type === 'BUY' ? '買入' : '賣出',
      交易日期: transaction.transaction_date,
      交易價格: formatCurrency(transaction.price),
      交易股數: formatNumber(transaction.shares),
      總金額: formatCurrency(transaction.total_amount),
      手續費: formatCurrency(transaction.commission),
      備註: transaction.notes || ''
    }))
    
    await exportToCSV(exportData, `交易記錄_篩選_${new Date().toISOString().split('T')[0]}.csv`)
    
    ElMessage.success(`成功導出 ${filteredTransactions.length} 條記錄`)
    
  } catch (error) {
    ElMessage.error('導出失敗：' + (error.message || error))
  } finally {
    exportFilteredLoading.value = false
  }
}

const exportToCSV = (data, filename) => {
  return new Promise((resolve, reject) => {
    try {
      if (data.length === 0) {
        reject(new Error('沒有數據可導出'))
        return
      }
      
      // 生成CSV內容
      const headers = Object.keys(data[0])
      const csvContent = [
        headers.join(','),
        ...data.map(row => headers.map(header => `"${row[header] || ''}"`).join(','))
      ].join('\n')
      
      // 創建Blob並下載
      const blob = new Blob([`\uFEFF${csvContent}`], { type: 'text/csv;charset=utf-8;' })
      const link = document.createElement('a')
      const url = URL.createObjectURL(blob)
      
      link.setAttribute('href', url)
      link.setAttribute('download', filename)
      link.style.visibility = 'hidden'
      
      document.body.appendChild(link)
      link.click()
      document.body.removeChild(link)
      
      URL.revokeObjectURL(url)
      resolve()
      
    } catch (error) {
      reject(error)
    }
  })
}

const handleFilterChange = () => {
  // 篩選條件改變時重置到第一頁
  pagination.current = 1
  fetchTransactions()
}

const handleSearch = () => {
  pagination.current = 1
  fetchTransactions()
}

const handleResetFilters = () => {
  // 重置篩選條件
  filters.stock_code = ''
  filters.transaction_type = ''
  filters.date_range = null
  
  // 重置分頁
  pagination.current = 1
  
  // 重新獲取數據
  fetchTransactions()
}

const handlePageChange = (page) => {
  pagination.current = page
  fetchTransactions()
}

const handleSizeChange = (size) => {
  pagination.size = size
  pagination.current = 1
  fetchTransactions()
}

const handleSortChange = ({ prop, order }) => {
  sorting.prop = prop
  sorting.order = order
  fetchTransactions()
}

const handleRefresh = () => {
  fetchTransactions()
}

const handleFormSuccess = () => {
  formVisible.value = false
  editingTransaction.value = null
  fetchTransactions()
}

const handleFormCancel = () => {
  formVisible.value = false
  editingTransaction.value = null
}

// 工具函數
const buildFilterParams = () => {
  const params = {
    page: pagination.current,
    per_page: pagination.size
  }
  
  if (filters.stock_code) {
    params.stock_code = filters.stock_code
  }
  
  if (filters.transaction_type) {
    params.transaction_type = filters.transaction_type
  }
  
  if (filters.date_range && filters.date_range.length === 2) {
    params.start_date = filters.date_range[0]
    params.end_date = filters.date_range[1]
  }
  
  if (sorting.prop && sorting.order) {
    params.sort_by = sorting.prop
    params.sort_order = sorting.order === 'ascending' ? 'asc' : 'desc'
  }
  
  return params
}

const fetchTransactions = async () => {
  try {
    loading.value = true
    
    const params = buildFilterParams()
    const result = await transactionStore.fetchTransactions(params)
    
    // 更新分頁信息
    if (result && result.pagination) {
      pagination.total = result.pagination.total
    }
    
  } catch (error) {
    ElMessage.error('獲取交易記錄失敗：' + (error.message || error))
  } finally {
    loading.value = false
  }
}

// 生命週期
onMounted(async () => {
  // 加載股票列表
  if (stockStore.stocks.length === 0) {
    await stockStore.fetchStocks()
  }
  
  // 加載交易記錄
  await fetchTransactions()
})

// 監聽器
watch(() => transactionStore.error, (error) => {
  if (error) {
    ElMessage.error('操作失敗：' + error)
  }
})
</script>

<style scoped>
.transactions-view {
  padding: 20px;
  background-color: #f5f5f5;
  min-height: 100vh;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  padding: 0 4px;
}

.page-title {
  margin: 0;
  font-size: 24px;
  font-weight: 600;
  color: #303133;
}

.header-actions {
  display: flex;
  gap: 12px;
}

.filter-card {
  margin-bottom: 16px;
}

.filter-container {
  padding: 8px 0;
}

.filter-buttons {
  display: flex;
  gap: 8px;
  justify-content: flex-end;
}

.batch-operations {
  margin-bottom: 16px;
  border-left: 4px solid #409eff;
}

.batch-info {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 8px 0;
}

.batch-actions {
  display: flex;
  gap: 8px;
}

.export-card {
  margin-bottom: 16px;
}

.export-container {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 8px 0;
}

.export-info {
  display: flex;
  align-items: center;
  gap: 12px;
}

.export-actions {
  display: flex;
  gap: 8px;
}

.table-card {
  margin-bottom: 20px;
}

/* 響應式設計 */
@media (max-width: 768px) {
  .transactions-view {
    padding: 12px;
  }
  
  .page-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 12px;
  }
  
  .header-actions {
    width: 100%;
    justify-content: flex-end;
  }
  
  .filter-buttons {
    flex-direction: column;
    width: 100%;
  }
  
  .filter-buttons .el-button {
    width: 100%;
  }
  
  .batch-info {
    flex-direction: column;
    align-items: flex-start;
    gap: 12px;
  }
  
  .batch-actions {
    width: 100%;
    justify-content: flex-end;
  }
  
  .export-container {
    flex-direction: column;
    align-items: flex-start;
    gap: 12px;
  }
  
  .export-actions {
    width: 100%;
    justify-content: flex-end;
  }
}

@media (max-width: 480px) {
  .transactions-view {
    padding: 8px;
  }
  
  .page-title {
    font-size: 20px;
  }
  
  .batch-actions .el-button,
  .export-actions .el-button {
    font-size: 12px;
    padding: 8px 12px;
  }
}

/* 表單項樣式優化 */
:deep(.el-form-item) {
  margin-bottom: 12px;
}

:deep(.el-form-item__label) {
  font-weight: 500;
  color: #606266;
}

/* 卡片樣式優化 */
:deep(.el-card__body) {
  padding: 16px;
}

/* 按鈕樣式優化 */
.el-button + .el-button {
  margin-left: 0;
}
</style>