import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import api from '../utils/api'

// 股票數據store
export const useStockStore = defineStore('stock', () => {
  // 狀態
  const stocks = ref([])
  const loading = ref(false)
  const error = ref(null)

  // 計算屬性
  const totalMarketValue = computed(() => {
    return stocks.value.reduce((total, stock) => total + (stock.market_value || 0), 0)
  })

  const totalProfitLoss = computed(() => {
    return stocks.value.reduce((total, stock) => total + (stock.profit_loss || 0), 0)
  })

  const totalProfitLossRate = computed(() => {
    const totalCost = stocks.value.reduce((total, stock) => {
      return total + (stock.avg_cost * stock.total_shares || 0)
    }, 0)
    return totalCost > 0 ? (totalProfitLoss.value / totalCost) * 100 : 0
  })

  // 動作
  const fetchStocks = async () => {
    loading.value = true
    error.value = null
    try {
      const response = await api.get('/api/stocks')
      stocks.value = response.data.data || []
    } catch (err) {
      error.value = err.message || '獲取股票數據失敗'
      console.error('獲取股票數據失敗:', err)
    } finally {
      loading.value = false
    }
  }

  const addStock = async (stockData) => {
    try {
      const response = await api.post('/api/stocks', stockData)
      stocks.value.push(response.data.data)
      return response.data
    } catch (err) {
      // 處理409錯誤（股票已存在）
      if (err.response && err.response.status === 409) {
        error.value = err.response.data.message || '股票已存在'
        // 對於409錯誤，我們仍然拋出錯誤，但會在組件中特殊處理
        const customError = new Error(err.response.data.message || '股票已存在')
        customError.status = 409
        customError.response = err.response
        throw customError
      } else {
        error.value = err.message || '添加股票失敗'
        throw err
      }
    }
  }

  const updateStock = async (stockCode, stockData) => {
    try {
      // 只發送允許更新的字段
      const updateData = {
        stock_name: stockData.stock_name,
        market: stockData.market,
        currency: stockData.currency,
        current_price: stockData.current_price
      }
      
      const response = await api.put(`/api/stocks/${stockCode}`, updateData)
      const index = stocks.value.findIndex(s => s.stock_code === stockCode)
      if (index !== -1) {
        stocks.value[index] = response.data.data
      }
      return response.data
    } catch (err) {
      error.value = err.message || '更新股票失敗'
      throw err
    }
  }

  const deleteStock = async (stockCode) => {
    try {
      await api.delete(`/api/stocks/${stockCode}`)
      stocks.value = stocks.value.filter(s => s.stock_code !== stockCode)
    } catch (err) {
      error.value = err.message || '刪除股票失敗'
      throw err
    }
  }

  return {
    // 狀態
    stocks,
    loading,
    error,
    // 計算屬性
    totalMarketValue,
    totalProfitLoss,
    totalProfitLossRate,
    // 動作
    fetchStocks,
    addStock,
    updateStock,
    deleteStock
  }
})

// 交易記錄store
export const useTransactionStore = defineStore('transaction', () => {
  const transactions = ref([])
  const loading = ref(false)
  const error = ref(null)

  // 計算屬性
  const totalTransactions = computed(() => transactions.value.length)
  
  const totalBuyAmount = computed(() => {
    return transactions.value
      .filter(t => t.transaction_type === 'BUY')
      .reduce((total, t) => total + (t.total_amount || 0), 0)
  })
  
  const totalSellAmount = computed(() => {
    return transactions.value
      .filter(t => t.transaction_type === 'SELL')
      .reduce((total, t) => total + (t.total_amount || 0), 0)
  })

  // 獲取交易記錄（支持分頁和篩選）
  const fetchTransactions = async (params = {}) => {
    loading.value = true
    error.value = null
    try {
      const queryParams = new URLSearchParams()
      
      // 添加查詢參數
      Object.keys(params).forEach(key => {
        if (params[key] !== null && params[key] !== undefined && params[key] !== '') {
          queryParams.append(key, params[key])
        }
      })
      
      const url = queryParams.toString() ? `/api/transactions?${queryParams.toString()}` : '/api/transactions'
      const response = await api.get(url)
      
      transactions.value = response.data.data || []
      
      // 返回分頁信息
      return {
        data: response.data.data || [],
        pagination: response.data.pagination || {
          total: response.data.data?.length || 0,
          page: 1,
          per_page: 20
        }
      }
    } catch (err) {
      error.value = err.message || '獲取交易記錄失敗'
      console.error('獲取交易記錄失敗:', err)
      throw err
    } finally {
      loading.value = false
    }
  }

  // 獲取所有交易記錄（不分頁）
  const fetchAllTransactions = async () => {
    try {
      const response = await api.get('/api/transactions?per_page=999999')
      return response.data.data || []
    } catch (err) {
      error.value = err.message || '獲取所有交易記錄失敗'
      throw err
    }
  }

  // 獲取篩選後的交易記錄
  const fetchFilteredTransactions = async (params) => {
    try {
      const queryParams = new URLSearchParams()
      
      Object.keys(params).forEach(key => {
        if (params[key] !== null && params[key] !== undefined && params[key] !== '') {
          queryParams.append(key, params[key])
        }
      })
      
      // 設置大的per_page值以獲取所有篩選結果
      queryParams.set('per_page', '999999')
      
      const response = await api.get(`/api/transactions?${queryParams.toString()}`)
      return response.data.data || []
    } catch (err) {
      error.value = err.message || '獲取篩選交易記錄失敗'
      throw err
    }
  }

  // 創建交易記錄
  const createTransaction = async (transactionData) => {
    try {
      const response = await api.post('/api/transactions', transactionData)
      
      // 添加到本地數組
      if (response.data.data) {
        transactions.value.unshift(response.data.data)
      }
      
      return response.data
    } catch (err) {
      error.value = err.message || '創建交易記錄失敗'
      throw err
    }
  }

  // 更新交易記錄
  const updateTransaction = async (transactionId, transactionData) => {
    try {
      const response = await api.put(`/api/transactions/${transactionId}`, transactionData)
      
      // 更新本地數組
      const index = transactions.value.findIndex(t => t.id === transactionId)
      if (index !== -1 && response.data.data) {
        transactions.value[index] = response.data.data
      }
      
      return response.data
    } catch (err) {
      error.value = err.message || '更新交易記錄失敗'
      throw err
    }
  }

  // 刪除交易記錄
  const deleteTransaction = async (transactionId) => {
    try {
      await api.delete(`/api/transactions/${transactionId}`)
      
      // 從本地數組中移除
      transactions.value = transactions.value.filter(t => t.id !== transactionId)
      
      return true
    } catch (err) {
      error.value = err.message || '刪除交易記錄失敗'
      throw err
    }
  }

  // 獲取交易統計信息
  const fetchTransactionStats = async (params = {}) => {
    try {
      const queryParams = new URLSearchParams()
      
      Object.keys(params).forEach(key => {
        if (params[key] !== null && params[key] !== undefined && params[key] !== '') {
          queryParams.append(key, params[key])
        }
      })
      
      const url = queryParams.toString() ? `/api/transactions/stats?${queryParams.toString()}` : '/api/transactions/stats'
      const response = await api.get(url)
      
      return response.data.data || {}
    } catch (err) {
      error.value = err.message || '獲取交易統計失敗'
      throw err
    }
  }

  // 批量刪除交易記錄
  const batchDeleteTransactions = async (transactionIds) => {
    try {
      const deletePromises = transactionIds.map(id => deleteTransaction(id))
      await Promise.all(deletePromises)
      
      return true
    } catch (err) {
      error.value = err.message || '批量刪除交易記錄失敗'
      throw err
    }
  }

  // 清除錯誤狀態
  const clearError = () => {
    error.value = null
  }

  return {
    // 狀態
    transactions,
    loading,
    error,
    // 計算屬性
    totalTransactions,
    totalBuyAmount,
    totalSellAmount,
    // 動作
    fetchTransactions,
    fetchAllTransactions,
    fetchFilteredTransactions,
    createTransaction,
    updateTransaction,
    deleteTransaction,
    fetchTransactionStats,
    batchDeleteTransactions,
    clearError
  }
})

// 股息記錄store
export const useDividendStore = defineStore('dividend', () => {
  const dividends = ref([])
  const loading = ref(false)
  const error = ref(null)
  const stats = ref({})

  // 計算屬性
  const totalDividends = computed(() => dividends.value.length)
  
  const totalDividendAmount = computed(() => {
    return dividends.value.reduce((total, d) => total + (d.total_dividend || 0), 0)
  })
  
  const totalNetDividend = computed(() => {
    return dividends.value.reduce((total, d) => total + (d.net_dividend || 0), 0)
  })
  
  const totalTaxAmount = computed(() => {
    return dividends.value.reduce((total, d) => total + (d.tax_amount || 0), 0)
  })

  // 獲取股息記錄（支持分頁和篩選）
  const fetchDividends = async (params = {}) => {
    loading.value = true
    error.value = null
    try {
      const queryParams = new URLSearchParams()
      
      // 添加查詢參數
      Object.keys(params).forEach(key => {
        if (params[key] !== null && params[key] !== undefined && params[key] !== '') {
          queryParams.append(key, params[key])
        }
      })
      
      const url = queryParams.toString() ? `/api/dividends?${queryParams.toString()}` : '/api/dividends'
      const response = await api.get(url)
      
      dividends.value = response.data.data || []
      
      // 返回分頁信息
      return {
        data: response.data.data || [],
        pagination: response.data.pagination || {
          total: response.data.data?.length || 0,
          page: 1,
          per_page: 20
        }
      }
    } catch (err) {
      error.value = err.message || '獲取股息記錄失敗'
      console.error('獲取股息記錄失敗:', err)
      throw err
    } finally {
      loading.value = false
    }
  }

  // 獲取所有股息記錄（不分頁）
  const fetchAllDividends = async () => {
    try {
      const response = await api.get('/api/dividends?per_page=999999')
      return response.data.data || []
    } catch (err) {
      error.value = err.message || '獲取所有股息記錄失敗'
      throw err
    }
  }

  // 獲取篩選後的股息記錄
  const fetchFilteredDividends = async (params) => {
    try {
      const queryParams = new URLSearchParams()
      
      Object.keys(params).forEach(key => {
        if (params[key] !== null && params[key] !== undefined && params[key] !== '') {
          queryParams.append(key, params[key])
        }
      })
      
      // 設置大的per_page值以獲取所有篩選結果
      queryParams.set('per_page', '999999')
      
      const response = await api.get(`/api/dividends?${queryParams.toString()}`)
      return response.data.data || []
    } catch (err) {
      error.value = err.message || '獲取篩選股息記錄失敗'
      throw err
    }
  }

  // 創建股息記錄
  const createDividend = async (dividendData) => {
    try {
      const response = await api.post('/api/dividends', dividendData)
      
      // 添加到本地數組
      if (response.data.data) {
        dividends.value.unshift(response.data.data)
      }
      
      return response.data
    } catch (err) {
      error.value = err.message || '創建股息記錄失敗'
      throw err
    }
  }

  // 更新股息記錄
  const updateDividend = async (dividendId, dividendData) => {
    try {
      const response = await api.put(`/api/dividends/${dividendId}`, dividendData)
      
      // 更新本地數組
      const index = dividends.value.findIndex(d => d.id === dividendId)
      if (index !== -1 && response.data.data) {
        dividends.value[index] = response.data.data
      }
      
      return response.data
    } catch (err) {
      error.value = err.message || '更新股息記錄失敗'
      throw err
    }
  }

  // 刪除股息記錄
  const deleteDividend = async (dividendId) => {
    try {
      await api.delete(`/api/dividends/${dividendId}`)
      
      // 從本地數組中移除
      dividends.value = dividends.value.filter(d => d.id !== dividendId)
      
      return true
    } catch (err) {
      error.value = err.message || '刪除股息記錄失敗'
      throw err
    }
  }

  // 獲取股息統計信息
  const fetchDividendStats = async (params = {}) => {
    try {
      const queryParams = new URLSearchParams()
      
      Object.keys(params).forEach(key => {
        if (params[key] !== null && params[key] !== undefined && params[key] !== '') {
          queryParams.append(key, params[key])
        }
      })
      
      const url = queryParams.toString() ? `/api/dividends/stats?${queryParams.toString()}` : '/api/dividends/stats'
      const response = await api.get(url)
      
      stats.value = response.data.data || {}
      return response.data.data || {}
    } catch (err) {
      error.value = err.message || '獲取股息統計失敗'
      throw err
    }
  }

  // 批量刪除股息記錄
  const batchDeleteDividends = async (dividendIds) => {
    try {
      const deletePromises = dividendIds.map(id => deleteDividend(id))
      await Promise.all(deletePromises)
      
      return true
    } catch (err) {
      error.value = err.message || '批量刪除股息記錄失敗'
      throw err
    }
  }

  // 清除錯誤狀態
  const clearError = () => {
    error.value = null
  }

  return {
    // 狀態
    dividends,
    loading,
    error,
    stats,
    // 計算屬性
    totalDividends,
    totalDividendAmount,
    totalNetDividend,
    totalTaxAmount,
    // 動作
    fetchDividends,
    fetchAllDividends,
    fetchFilteredDividends,
    createDividend,
    updateDividend,
    deleteDividend,
    fetchDividendStats,
    batchDeleteDividends,
    clearError
  }
})