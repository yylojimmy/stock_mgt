import axios from 'axios'
import { ElMessage, ElLoading } from 'element-plus'

// 創建axios實例
const api = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || 'http://localhost:5001',
  timeout: 15000,
  headers: {
    'Content-Type': 'application/json'
  }
})

// 請求計數器和加載實例
let requestCount = 0
let loadingInstance = null

// 顯示全局加載
const showLoading = () => {
  if (requestCount === 0) {
    loadingInstance = ElLoading.service({
      lock: true,
      text: '加載中...',
      background: 'rgba(0, 0, 0, 0.7)'
    })
  }
  requestCount++
}

// 隱藏全局加載
const hideLoading = () => {
  requestCount--
  if (requestCount <= 0) {
    requestCount = 0
    if (loadingInstance) {
      loadingInstance.close()
      loadingInstance = null
    }
  }
}

// 請求攔截器
api.interceptors.request.use(
  (config) => {
    // 顯示加載狀態（除非配置中禁用）
    if (!config.hideLoading) {
      showLoading()
    }
    
    // 在發送請求之前做些什麼
    console.log('發送請求:', config.method?.toUpperCase(), config.url)
    
    // 添加時間戳防止緩存
    if (config.method === 'get') {
      config.params = {
        ...config.params,
        _t: Date.now()
      }
    }
    
    return config
  },
  (error) => {
    // 隱藏加載狀態
    hideLoading()
    
    // 對請求錯誤做些什麼
    console.error('請求錯誤:', error)
    ElMessage.error('請求發送失敗')
    return Promise.reject(error)
  }
)

// 響應攔截器
api.interceptors.response.use(
  (response) => {
    // 隱藏加載狀態
    if (!response.config.hideLoading) {
      hideLoading()
    }
    
    // 對響應數據做點什麼
    console.log('收到響應:', response.status, response.config.url)
    return response
  },
  (error) => {
    // 隱藏加載狀態
    hideLoading()
    
    // 對響應錯誤做點什麼
    console.error('響應錯誤:', error)
    
    let message = '請求失敗'
    
    if (error.response) {
      // 服務器響應了錯誤狀態碼
      const { status, data } = error.response
      
      switch (status) {
        case 400:
          message = data.message || data.error || '請求參數錯誤'
          break
        case 401:
          message = '未授權，請重新登錄'
          // 可以在這裡處理登出邏輯
          break
        case 403:
          message = '權限不足'
          break
        case 404:
          message = '請求的資源不存在'
          break
        case 409:
          message = data.message || '資源已存在'
          break
        case 422:
          message = data.message || '數據驗證失敗'
          break
        case 500:
          message = '服務器內部錯誤'
          break
        case 502:
          message = '網關錯誤'
          break
        case 503:
          message = '服務暫時不可用'
          break
        default:
          message = data.message || data.error || `請求失敗 (${status})`
          break
      }
    } else if (error.request) {
      // 請求已發出但沒有收到響應
      message = '網絡連接失敗，請檢查網絡設置'
    } else {
      // 其他錯誤
      message = error.message || '未知錯誤'
    }
    
    // 顯示錯誤消息（除非配置中禁用）
    if (!error.config?.hideMessage) {
      ElMessage.error(message)
    }
    
    return Promise.reject(error)
  }
)

// 通用請求方法
const request = {
  get(url, params = {}, config = {}) {
    return api.get(url, { params, ...config })
  },
  
  post(url, data = {}, config = {}) {
    return api.post(url, data, config)
  },
  
  put(url, data = {}, config = {}) {
    return api.put(url, data, config)
  },
  
  delete(url, config = {}) {
    return api.delete(url, config)
  },
  
  patch(url, data = {}, config = {}) {
    return api.patch(url, data, config)
  }
}

export { request }

export default api

// 導出常用的API方法
export const stockAPI = {
  // 獲取股票列表
  getStocks: (params) => api.get('/api/stocks', { params }),
  
  // 獲取單個股票詳情
  getStock: (stockCode) => api.get(`/api/stocks/${stockCode}`),
  
  // 創建股票
  createStock: (data) => api.post('/api/stocks', data),
  
  // 更新股票
  updateStock: (stockCode, data) => api.put(`/api/stocks/${stockCode}`, data),
  
  // 刪除股票
  deleteStock: (stockCode) => api.delete(`/api/stocks/${stockCode}`),
  
  // 搜索股票
  searchStocks: (query) => api.get('/api/stocks/search', { params: { q: query } })
}

export const transactionAPI = {
  // 獲取交易記錄
  getTransactions: (params) => api.get('/api/transactions', { params }),
  
  // 創建交易記錄
  createTransaction: (data) => api.post('/api/transactions', data)
}

export const dividendAPI = {
  // 獲取股息記錄
  getDividends: (params) => api.get('/api/dividends', { params }),
  
  // 獲取篩選後的股息記錄
  getFilteredDividends: (params) => api.get('/api/dividends', { params }),
  
  // 創建股息記錄
  createDividend: (data) => api.post('/api/dividends', data),
  
  // 更新股息記錄
  updateDividend: (id, data) => api.put(`/api/dividends/${id}`, data),
  
  // 刪除股息記錄
  deleteDividend: (id) => api.delete(`/api/dividends/${id}`),
  
  // 批量刪除股息記錄
  batchDeleteDividends: (ids) => api.delete('/api/dividends/batch', { data: { ids } }),
  
  // 獲取股息統計
  getDividendStats: () => api.get('/api/dividends/stats')
}

export const portfolioAPI = {
  // 獲取投資組合概覽
  getOverview: () => api.get('/api/portfolio/overview'),
  
  // 獲取投資組合分析
  getAnalysis: () => api.get('/api/portfolio/analysis')
}

export const priceAPI = {
  // 獲取當前股價
  getCurrentPrices: () => api.get('/api/prices/current'),
  
  // 刷新股價
  refreshPrices: () => api.post('/api/prices/refresh'),
  
  // 獲取特定股票價格
  getStockPrice: (stockCode) => api.get(`/api/prices/${stockCode}`)
}