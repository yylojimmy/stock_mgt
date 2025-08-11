<template>
  <div class="dividend-list">
    <!-- 統計卡片 -->
    <DividendStats :stats="dividendStore.stats" :loading="dividendStore.loading" />
    
    <!-- 篩選和操作區域 -->
    <el-card class="filter-card">
      <div class="filter-section">
        <div class="filter-row">
          <!-- 日期範圍篩選 -->
          <div class="filter-item">
            <label>日期範圍：</label>
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
          </div>
          
          <!-- 股票代碼篩選 -->
          <div class="filter-item">
            <label>股票代碼：</label>
            <el-select
              v-model="selectedStockCode"
              placeholder="選擇股票"
              clearable
              @change="handleStockCodeChange"
            >
              <el-option
                v-for="stock in stockStore.stocks"
                :key="stock.stock_code"
                :label="`${stock.stock_code} - ${stock.stock_name}`"
                :value="stock.stock_code"
              />
            </el-select>
          </div>
          
          <!-- 幣種篩選 -->
          <div class="filter-item">
            <label>幣種：</label>
            <el-select
              v-model="selectedCurrency"
              placeholder="選擇幣種"
              clearable
              @change="handleCurrencyChange"
            >
              <el-option label="USD" value="USD" />
              <el-option label="HKD" value="HKD" />
              <el-option label="CNY" value="CNY" />
            </el-select>
          </div>
        </div>
        
        <div class="action-row">
          <div class="action-buttons">
            <el-button type="primary" @click="showAddForm">
              <el-icon><Plus /></el-icon>
              添加股息
            </el-button>
            <el-button type="success" @click="exportData">
              <el-icon><Download /></el-icon>
              導出數據
            </el-button>
            <el-button @click="resetFilters">
              <el-icon><Refresh /></el-icon>
              重置篩選
            </el-button>
          </div>
        </div>
      </div>
    </el-card>
    
    <!-- 股息記錄表格 -->
    <DividendTable
      :dividends="dividendStore.dividends"
      :loading="dividendStore.loading"
      :pagination="pagination"
      @edit="handleEdit"
      @delete="handleDelete"
      @batch-delete="handleBatchDelete"
      @page-change="handlePageChange"
      @size-change="handleSizeChange"
    />
    
    <!-- 新增/編輯表單對話框 -->
    <el-dialog
      v-model="showForm"
      :title="isEditing ? '編輯股息記錄' : '新增股息記錄'"
      width="600px"
      :before-close="handleCloseForm"
    >
      <DividendForm
        :visible="showForm"
        :edit-data="currentDividend"
        @success="handleFormSuccess"
      />
    </el-dialog>
  </div>
</template>

<script>
import { ref, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { useDividendStore, useStockStore } from '../stores'
import { Plus, Download, Refresh } from '@element-plus/icons-vue'
import DividendTable from '../components/DividendTable.vue'
import DividendForm from '../components/DividendForm.vue'
import DividendStats from '../components/DividendStats.vue'

export default {
  name: 'DividendList',
  components: {
    Plus,
    Download,
    Refresh,
    DividendTable,
    DividendForm,
    DividendStats
  },
  setup() {
    const dividendStore = useDividendStore()
    const stockStore = useStockStore()
    
    // 表單相關狀態
    const showForm = ref(false)
    const isEditing = ref(false)
    const currentDividend = ref(null)
    
    // 篩選相關狀態
    const dateRange = ref(null)
    const selectedStockCode = ref('')
    const selectedCurrency = ref('')
    
    // 分頁狀態
    const pagination = ref({
      total: 0,
      page: 1,
      per_page: 20
    })
    
    // 顯示新增表單
    const showAddForm = () => {
      currentDividend.value = null
      isEditing.value = false
      showForm.value = true
    }
    
    // 處理編輯
    const handleEdit = (dividend) => {
      currentDividend.value = { ...dividend }
      isEditing.value = true
      showForm.value = true
    }
    
    // 處理刪除
    const handleDelete = async (dividend) => {
      try {
        await ElMessageBox.confirm(
          `確定要刪除 ${dividend.stock_code} 在 ${dividend.dividend_date} 的股息記錄嗎？`,
          '確認刪除',
          {
            confirmButtonText: '確定',
            cancelButtonText: '取消',
            type: 'warning'
          }
        )
        
        await dividendStore.deleteDividend(dividend.id)
        ElMessage.success('刪除成功')
        await refreshData()
      } catch (error) {
        if (error !== 'cancel') {
          ElMessage.error('刪除失敗：' + error.message)
        }
      }
    }
    
    // 處理批量刪除
    const handleBatchDelete = async (dividendIds) => {
      try {
        await ElMessageBox.confirm(
          `確定要刪除選中的 ${dividendIds.length} 條股息記錄嗎？`,
          '確認批量刪除',
          {
            confirmButtonText: '確定',
            cancelButtonText: '取消',
            type: 'warning'
          }
        )
        
        await dividendStore.batchDeleteDividends(dividendIds)
        ElMessage.success('批量刪除成功')
        await refreshData()
      } catch (error) {
        if (error !== 'cancel') {
          ElMessage.error('批量刪除失敗：' + error.message)
        }
      }
    }
    
    // 處理表單成功提交
    const handleFormSuccess = async () => {
      showForm.value = false
      await refreshData()
    }
    
    // 關閉表單
    const handleCloseForm = () => {
      showForm.value = false
      currentDividend.value = null
      isEditing.value = false
    }
    
    // 處理日期範圍變化
    const handleDateRangeChange = (dates) => {
      applyFilters()
    }
    
    // 處理股票代碼變化
    const handleStockCodeChange = () => {
      applyFilters()
    }
    
    // 處理幣種變化
    const handleCurrencyChange = () => {
      applyFilters()
    }
    
    // 應用篩選
    const applyFilters = async () => {
      pagination.value.page = 1 // 重置到第一頁
      await fetchDividendsWithPagination()
    }
    
    // 重置篩選
    const resetFilters = async () => {
      dateRange.value = null
      selectedStockCode.value = ''
      selectedCurrency.value = ''
      pagination.value.page = 1
      await fetchDividendsWithPagination()
    }
    
    // 導出數據
    const exportData = () => {
      try {
        const data = dividendStore.dividends
        if (!data || data.length === 0) {
          ElMessage.warning('沒有數據可導出')
          return
        }
        
        // 準備CSV數據
        const headers = ['股息日期', '股票代碼', '每股股息', '總股息', '稅額', '淨股息', '幣種', '備註']
        const csvContent = [
          headers.join(','),
          ...data.map(row => [
            row.dividend_date,
            row.stock_code,
            row.dividend_per_share,
            row.total_dividend,
            row.tax_amount || 0,
            row.net_dividend,
            row.currency,
            `"${row.notes || ''}"`
          ].join(','))
        ].join('\n')
        
        // 創建並下載文件
        const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' })
        const link = document.createElement('a')
        const url = URL.createObjectURL(blob)
        link.setAttribute('href', url)
        link.setAttribute('download', `股息記錄_${new Date().toISOString().split('T')[0]}.csv`)
        link.style.visibility = 'hidden'
        document.body.appendChild(link)
        link.click()
        document.body.removeChild(link)
        
        ElMessage.success('數據導出成功')
      } catch (error) {
        ElMessage.error('導出失敗：' + error.message)
      }
    }
    
    // 處理分頁變化
    const handlePageChange = async (page) => {
      pagination.value.page = page
      await fetchDividendsWithPagination()
    }
    
    // 處理分頁大小變化
    const handleSizeChange = async (size) => {
      pagination.value.per_page = size
      pagination.value.page = 1
      await fetchDividendsWithPagination()
    }
    
    // 獲取分頁數據
    const fetchDividendsWithPagination = async () => {
      const params = {
        page: pagination.value.page,
        per_page: pagination.value.per_page
      }
      
      // 添加篩選條件
      if (dateRange.value && dateRange.value.length === 2) {
        params.start_date = dateRange.value[0]
        params.end_date = dateRange.value[1]
      }
      
      if (selectedStockCode.value) {
        params.stock_code = selectedStockCode.value
      }
      
      if (selectedCurrency.value) {
        params.currency = selectedCurrency.value
      }
      
      const result = await dividendStore.fetchDividends(params)
      if (result && result.pagination) {
        pagination.value = result.pagination
      }
    }
    
    // 刷新數據
    const refreshData = async () => {
      await fetchDividendsWithPagination()
      await dividendStore.fetchDividendStats({
        start_date: dateRange.value?.[0],
        end_date: dateRange.value?.[1],
        stock_code: selectedStockCode.value,
        currency: selectedCurrency.value
      })
    }
    
    // 組件掛載時獲取數據
    onMounted(async () => {
      await stockStore.fetchStocks()
      await refreshData()
    })
    
    return {
      dividendStore,
      stockStore,
      showForm,
      isEditing,
      currentDividend,
      dateRange,
      selectedStockCode,
      selectedCurrency,
      pagination,
      showAddForm,
      handleEdit,
      handleDelete,
      handleBatchDelete,
      handleFormSuccess,
      handleCloseForm,
      handleDateRangeChange,
      handleStockCodeChange,
      handleCurrencyChange,
      resetFilters,
      exportData,
      handlePageChange,
      handleSizeChange
    }
  }
}
</script>

<style scoped>
.dividend-list {
  padding: 20px;
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.filter-card {
  margin-bottom: 0;
}

.filter-section {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.filter-row {
  display: flex;
  flex-wrap: wrap;
  gap: 16px;
  align-items: center;
}

.filter-item {
  display: flex;
  align-items: center;
  gap: 8px;
  min-width: 200px;
}

.filter-item label {
  font-weight: 500;
  white-space: nowrap;
  min-width: 80px;
}

.action-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.action-buttons {
  display: flex;
  gap: 12px;
}

/* 響應式設計 */
@media (max-width: 1200px) {
  .filter-row {
    flex-direction: column;
    align-items: stretch;
  }
  
  .filter-item {
    min-width: auto;
  }
}

@media (max-width: 768px) {
  .dividend-list {
    padding: 10px;
    gap: 15px;
  }
  
  .filter-item {
    flex-direction: column;
    align-items: stretch;
    gap: 4px;
  }
  
  .filter-item label {
    min-width: auto;
  }
  
  .action-buttons {
    flex-direction: column;
    width: 100%;
  }
  
  .action-buttons .el-button {
    width: 100%;
  }
}
</style>