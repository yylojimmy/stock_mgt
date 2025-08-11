<template>
  <div class="stock-list">
    <!-- 頁面標題和操作欄 -->
    <div class="page-header">
      <div class="header-content">
        <h1 class="page-title">股票管理</h1>
        <p class="page-subtitle">管理您的股票投資組合</p>
      </div>
      <div class="header-actions">
        <button class="btn btn-primary" @click="showAddForm">
          <svg class="icon" viewBox="0 0 24 24">
            <path d="M19 13h-6v6h-2v-6H5v-2h6V5h2v6h6v2z"/>
          </svg>
          添加股票
        </button>
      </div>
    </div>
    
    <!-- 搜索和篩選 -->
    <div class="search-section">
      <div class="search-bar">
        <div class="search-input-group">
          <svg class="search-icon" viewBox="0 0 24 24">
            <path d="M15.5 14h-.79l-.28-.27C15.41 12.59 16 11.11 16 9.5 16 5.91 13.09 3 9.5 3S3 5.91 3 9.5 5.91 16 9.5 16c1.61 0 3.09-.59 4.23-1.57l.27.28v.79l5 4.99L20.49 19l-4.99-5zm-6 0C7.01 14 5 11.99 5 9.5S7.01 5 9.5 5 14 7.01 14 9.5 11.99 14 9.5 14z"/>
          </svg>
          <input
            v-model="searchQuery"
            type="text"
            class="search-input"
            placeholder="搜索股票代碼或名稱..."
            @input="onSearchInput"
          />
          <button v-if="searchQuery" class="clear-btn" @click="clearSearch">
            <svg class="icon" viewBox="0 0 24 24">
              <path d="M19 6.41L17.59 5 12 10.59 6.41 5 5 6.41 10.59 12 5 17.59 6.41 19 12 13.41 17.59 19 19 17.59 13.41 12z"/>
            </svg>
          </button>
        </div>
        
        <div class="filter-group">
          <select v-model="selectedMarket" class="filter-select" @change="onFilterChange">
            <option value="">全部市場</option>
            <option value="SZ">深圳</option>
            <option value="SH">上海</option>
            <option value="HK">香港</option>
            <option value="US">美國</option>
          </select>
          
          <select v-model="sortBy" class="filter-select" @change="onSortChange">
            <option value="stock_code">按代碼排序</option>
            <option value="stock_name">按名稱排序</option>
            <option value="market_value">按市值排序</option>
            <option value="profit_loss">按盈虧排序</option>
          </select>
        </div>
      </div>
      
      <!-- 統計信息 -->
      <div class="stats-bar" v-if="!stockStore.loading && filteredStocks.length > 0">
        <div class="stat-item">
          <span class="stat-label">總股票數</span>
          <span class="stat-value">{{ filteredStocks.length }}</span>
        </div>
        <div class="stat-item">
          <span class="stat-label">總市值</span>
          <span class="stat-value">{{ formatCurrency(totalMarketValue) }}</span>
        </div>
        <div class="stat-item">
          <span class="stat-label">總盈虧</span>
          <span class="stat-value" :class="totalProfitLoss >= 0 ? 'profit' : 'loss'">
            {{ formatCurrency(totalProfitLoss) }}
          </span>
        </div>
      </div>
    </div>
    
    <!-- 股票列表 -->
    <div class="stocks-container">
      <!-- 加載狀態 -->
      <div v-if="stockStore.loading" class="loading-container">
        <LoadingSpinner />
        <p>正在加載股票數據...</p>
      </div>
      
      <!-- 錯誤狀態 -->
      <div v-else-if="stockStore.error" class="error-container">
        <div class="error-content">
          <svg class="error-icon" viewBox="0 0 24 24">
            <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-2 15l-5-5 1.41-1.41L10 14.17l7.59-7.59L19 8l-9 9z"/>
          </svg>
          <h3>加載失敗</h3>
          <p>{{ stockStore.error }}</p>
          <button class="btn btn-primary" @click="retryLoad">
            重新加載
          </button>
        </div>
      </div>
      
      <!-- 空狀態 -->
      <div v-else-if="filteredStocks.length === 0" class="empty-container">
        <EmptyState
          title="暫無股票數據"
          :description="searchQuery || selectedMarket ? '沒有找到符合條件的股票' : '您還沒有添加任何股票'"
          :show-action="!searchQuery && !selectedMarket"
          action-text="添加第一支股票"
          @action="showAddForm"
        />
      </div>
      
      <!-- 股票卡片列表 -->
      <div v-else class="stocks-grid">
        <StockCard
          v-for="stock in sortedStocks"
          :key="stock.stock_code"
          :stock="stock"
          :total-portfolio-value="totalMarketValue"
          @edit="editStock"
          @delete="deleteStock"
        />
      </div>
    </div>
    
    <!-- 股票表單對話框 -->
    <StockForm
      v-if="showForm"
      :stock="editingStock"
      :visible="showForm"
      @close="closeForm"
      @submit="onFormSubmit"
    />
  </div>
</template>

<script>
import { ref, computed, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { useStockStore } from '../stores'
import StockCard from '../components/StockCard.vue'
import StockForm from '../components/StockForm.vue'
import LoadingSpinner from '../components/LoadingSpinner.vue'
import EmptyState from '../components/EmptyState.vue'

export default {
  name: 'StockList',
  components: {
    StockCard,
    StockForm,
    LoadingSpinner,
    EmptyState
  },
  setup() {
    const stockStore = useStockStore()
    const searchQuery = ref('')
    const selectedMarket = ref('')
    const sortBy = ref('stock_code')
    const showForm = ref(false)
    const editingStock = ref(null)

    // 過濾後的股票列表
    const filteredStocks = computed(() => {
      let stocks = stockStore.stocks
      
      if (searchQuery.value) {
        const query = searchQuery.value.toLowerCase()
        stocks = stocks.filter(stock => 
          stock.stock_code.toLowerCase().includes(query) ||
          stock.stock_name.toLowerCase().includes(query)
        )
      }
      
      if (selectedMarket.value) {
        stocks = stocks.filter(stock => stock.market === selectedMarket.value)
      }
      
      return stocks
    })
    
    // 排序後的股票列表
    const sortedStocks = computed(() => {
      const stocks = [...filteredStocks.value]
      
      return stocks.sort((a, b) => {
        switch (sortBy.value) {
          case 'stock_name':
            return a.stock_name.localeCompare(b.stock_name)
          case 'market_value':
            return (b.market_value || 0) - (a.market_value || 0)
          case 'profit_loss':
            const aProfitLoss = (a.market_value || 0) - (a.total_shares * a.avg_cost)
            const bProfitLoss = (b.market_value || 0) - (b.total_shares * b.avg_cost)
            return bProfitLoss - aProfitLoss
          default: // stock_code
            return a.stock_code.localeCompare(b.stock_code)
        }
      })
    })
    
    // 總市值
    const totalMarketValue = computed(() => {
      return filteredStocks.value.reduce((sum, stock) => sum + (stock.market_value || 0), 0)
    })
    
    // 總盈虧
    const totalProfitLoss = computed(() => {
      return filteredStocks.value.reduce((sum, stock) => {
        const profitLoss = (stock.market_value || 0) - (stock.total_shares * stock.avg_cost)
        return sum + profitLoss
      }, 0)
    })

    // 格式化貨幣
    const formatCurrency = (value) => {
      if (value === null || value === undefined) return '0.00'
      return new Intl.NumberFormat('zh-CN', {
        style: 'currency',
        currency: 'CNY',
        minimumFractionDigits: 2
      }).format(value)
    }

    // 格式化數字
    const formatNumber = (value) => {
      if (value === null || value === undefined) return '0'
      return new Intl.NumberFormat('zh-CN').format(value)
    }

    // 搜索輸入處理
    const onSearchInput = () => {
      // 搜索邏輯已在computed中實現
    }

    // 清除搜索
    const clearSearch = () => {
      searchQuery.value = ''
    }

    // 篩選變更處理
    const onFilterChange = () => {
      // 篩選邏輯已在computed中實現
    }

    // 排序變更處理
    const onSortChange = () => {
      // 排序邏輯已在computed中實現
    }

    // 顯示添加表單
    const showAddForm = () => {
      editingStock.value = null
      showForm.value = true
    }

    // 編輯股票
    const editStock = (stock) => {
      editingStock.value = { ...stock }
      showForm.value = true
    }

    // 關閉表單
    const closeForm = () => {
      showForm.value = false
      editingStock.value = null
    }

    // 表單提交
    const onFormSubmit = async (stockData) => {
      try {
        if (editingStock.value) {
          await stockStore.updateStock(stockData.stock_code, stockData)
        } else {
          await stockStore.addStock(stockData)
        }
        closeForm()
        // 刷新股票列表
        await stockStore.fetchStocks()
      } catch (error) {
        console.error('提交失敗:', error)
        // 如果是409錯誤（股票已存在），顯示友好提示並刷新數據
        if (error.status === 409 || (error.response && error.response.status === 409)) {
          // 顯示成功提示，因為股票已存在意味著數據是正確的
          ElMessage.success('股票已存在於系統中')
          closeForm()
          await stockStore.fetchStocks()
        } else {
          // 其他錯誤顯示錯誤提示
          ElMessage.error(error.message || '提交失敗')
        }
      }
    }

    // 刪除股票
    const deleteStock = async (stock) => {
      if (confirm(`確定要刪除股票 ${stock.stock_name} 嗎？`)) {
        try {
          await stockStore.deleteStock(stock.stock_code)
        } catch (error) {
          console.error('刪除失敗:', error)
        }
      }
    }

    // 重新加載
    const retryLoad = () => {
      stockStore.fetchStocks()
    }

    // 組件掛載時獲取數據
    onMounted(() => {
      stockStore.fetchStocks()
    })

    return {
      stockStore,
      searchQuery,
      selectedMarket,
      sortBy,
      showForm,
      editingStock,
      filteredStocks,
      sortedStocks,
      totalMarketValue,
      totalProfitLoss,
      formatCurrency,
      formatNumber,
      onSearchInput,
      clearSearch,
      onFilterChange,
      onSortChange,
      showAddForm,
      editStock,
      closeForm,
      onFormSubmit,
      deleteStock,
      retryLoad
    }
  }
}
</script>

<style scoped>
.stock-list {
  min-height: 100vh;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  padding: 1rem;
}

/* 頁面標題區域 */
.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 2rem;
  padding: 1.5rem;
  background: rgba(255, 255, 255, 0.95);
  border-radius: 16px;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
  backdrop-filter: blur(10px);
}

.header-content {
  flex: 1;
}

.page-title {
  font-size: 2rem;
  font-weight: 700;
  color: #1a202c;
  margin: 0 0 0.5rem 0;
}

.page-subtitle {
  color: #718096;
  margin: 0;
  font-size: 1rem;
}

.header-actions {
  display: flex;
  gap: 1rem;
}

/* 搜索區域 */
.search-section {
  margin-bottom: 2rem;
  padding: 1.5rem;
  background: rgba(255, 255, 255, 0.95);
  border-radius: 16px;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
  backdrop-filter: blur(10px);
}

.search-bar {
  display: flex;
  gap: 1rem;
  margin-bottom: 1rem;
  flex-wrap: wrap;
}

.search-input-group {
  position: relative;
  flex: 1;
  min-width: 300px;
}

.search-icon {
  position: absolute;
  left: 12px;
  top: 50%;
  transform: translateY(-50%);
  width: 20px;
  height: 20px;
  fill: #9ca3af;
  pointer-events: none;
}

.search-input {
  width: 100%;
  padding: 12px 16px 12px 44px;
  border: 2px solid #e5e7eb;
  border-radius: 12px;
  font-size: 1rem;
  transition: all 0.2s ease;
  background: white;
}

.search-input:focus {
  outline: none;
  border-color: #3b82f6;
  box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
}

.clear-btn {
  position: absolute;
  right: 8px;
  top: 50%;
  transform: translateY(-50%);
  background: none;
  border: none;
  padding: 4px;
  cursor: pointer;
  border-radius: 6px;
  transition: background-color 0.2s ease;
}

.clear-btn:hover {
  background-color: #f3f4f6;
}

.filter-group {
  display: flex;
  gap: 1rem;
  flex-wrap: wrap;
}

.filter-select {
  padding: 12px 16px;
  border: 2px solid #e5e7eb;
  border-radius: 12px;
  font-size: 1rem;
  background: white;
  cursor: pointer;
  transition: all 0.2s ease;
  min-width: 150px;
}

.filter-select:focus {
  outline: none;
  border-color: #3b82f6;
  box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
}

/* 統計欄 */
.stats-bar {
  display: flex;
  gap: 2rem;
  padding: 1rem 0;
  border-top: 1px solid #e5e7eb;
  flex-wrap: wrap;
}

.stat-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.25rem;
}

.stat-label {
  font-size: 0.875rem;
  color: #6b7280;
  font-weight: 500;
}

.stat-value {
  font-size: 1.25rem;
  font-weight: 700;
  color: #1f2937;
}

.stat-value.profit {
  color: #10b981;
}

.stat-value.loss {
  color: #ef4444;
}

/* 股票容器 */
.stocks-container {
  background: rgba(255, 255, 255, 0.95);
  border-radius: 16px;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
  backdrop-filter: blur(10px);
  padding: 1.5rem;
  min-height: 400px;
}

/* 加載狀態 */
.loading-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 4rem 2rem;
  gap: 1rem;
}

.loading-container p {
  color: #6b7280;
  font-size: 1rem;
}

/* 錯誤狀態 */
.error-container {
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 4rem 2rem;
}

.error-content {
  text-align: center;
  max-width: 400px;
}

.error-icon {
  width: 64px;
  height: 64px;
  fill: #ef4444;
  margin-bottom: 1rem;
}

.error-content h3 {
  font-size: 1.5rem;
  font-weight: 600;
  color: #1f2937;
  margin-bottom: 0.5rem;
}

.error-content p {
  color: #6b7280;
  margin-bottom: 1.5rem;
}

/* 空狀態 */
.empty-container {
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 4rem 2rem;
}

/* 股票網格 */
.stocks-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(350px, 1fr));
  gap: 1.5rem;
  padding: 1rem 0;
}

/* 按鈕樣式 */
.btn {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  padding: 12px 24px;
  border: none;
  border-radius: 12px;
  font-size: 1rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s ease;
  text-decoration: none;
}

.btn-primary {
  background: linear-gradient(135deg, #3b82f6, #1d4ed8);
  color: white;
  box-shadow: 0 4px 12px rgba(59, 130, 246, 0.3);
}

.btn-primary:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 20px rgba(59, 130, 246, 0.4);
}

.btn-primary:active {
  transform: translateY(0);
}

.icon {
  width: 20px;
  height: 20px;
  fill: currentColor;
}

/* 響應式設計 */
@media (max-width: 768px) {
  .stock-list {
    padding: 0.5rem;
  }
  
  .page-header {
    flex-direction: column;
    gap: 1rem;
    text-align: center;
    padding: 1rem;
  }
  
  .page-title {
    font-size: 1.5rem;
  }
  
  .search-bar {
    flex-direction: column;
  }
  
  .search-input-group {
    min-width: unset;
  }
  
  .filter-group {
    justify-content: center;
  }
  
  .stats-bar {
    justify-content: center;
    gap: 1rem;
  }
  
  .stocks-grid {
    grid-template-columns: 1fr;
    gap: 1rem;
  }
  
  .stocks-container {
    padding: 1rem;
  }
}

@media (max-width: 480px) {
  .search-section,
  .stocks-container {
    padding: 1rem;
  }
  
  .filter-select {
    min-width: unset;
    flex: 1;
  }
}

/* 響應式設計 */
@media (max-width: 768px) {
  .stock-list {
    padding: 10px;
  }
}
</style>