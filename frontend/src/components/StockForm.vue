<template>
  <div class="stock-form-overlay" @click="handleOverlayClick">
    <div class="stock-form-modal" @click.stop>
      <div class="form-header">
        <h3>{{ isEdit ? '編輯股票' : '添加股票' }}</h3>
        <button class="close-btn" @click="$emit('close')">
          <svg class="icon" viewBox="0 0 24 24">
            <path d="M19 6.41L17.59 5 12 10.59 6.41 5 5 6.41 10.59 12 5 17.59 6.41 19 12 13.41 17.59 19 19 17.59 13.41 12z"/>
          </svg>
        </button>
      </div>
      
      <form @submit.prevent="handleSubmit" class="form-body">
        <div class="form-group">
          <label for="stock_code" class="form-label">股票代碼 *</label>
          <input
            id="stock_code"
            v-model="formData.stock_code"
            type="text"
            class="form-input"
            :class="{ 'error': errors.stock_code }"
            placeholder="例如: 000001.SZ"
            :disabled="isEdit"
            @blur="validateStockCode"
            @input="onStockCodeInput"
          />
          <div v-if="errors.stock_code" class="error-message">{{ errors.stock_code }}</div>
          <div v-if="stockCodeSuggestions.length > 0" class="suggestions">
            <div
              v-for="suggestion in stockCodeSuggestions"
              :key="suggestion.code"
              class="suggestion-item"
              @click="selectSuggestion(suggestion)"
            >
              <span class="suggestion-code">{{ suggestion.code }}</span>
              <span class="suggestion-name">{{ suggestion.name }}</span>
            </div>
          </div>
        </div>
        
        <div class="form-group">
          <label for="stock_name" class="form-label">股票名稱 *</label>
          <input
            id="stock_name"
            v-model="formData.stock_name"
            type="text"
            class="form-input"
            :class="{ 'error': errors.stock_name }"
            placeholder="股票名稱"
            @blur="validateStockName"
          />
          <div v-if="errors.stock_name" class="error-message">{{ errors.stock_name }}</div>
        </div>
        
        <div class="form-row">
          <div class="form-group">
            <label for="market" class="form-label">市場 *</label>
            <select
              id="market"
              v-model="formData.market"
              class="form-select"
              :class="{ 'error': errors.market }"
              @change="validateMarket"
            >
              <option value="">請選擇市場</option>
              <option value="SZ">深圳證券交易所</option>
              <option value="SH">上海證券交易所</option>
              <option value="HK">香港交易所</option>
              <option value="US">美國市場</option>
            </select>
            <div v-if="errors.market" class="error-message">{{ errors.market }}</div>
          </div>
          
          <div class="form-group">
            <label for="currency" class="form-label">幣種</label>
            <select
              id="currency"
              v-model="formData.currency"
              class="form-select"
            >
              <option value="CNY">人民幣 (CNY)</option>
              <option value="HKD">港幣 (HKD)</option>
              <option value="USD">美元 (USD)</option>
            </select>
          </div>
        </div>
        
        <div class="form-row">
          <div class="form-group">
            <label for="current_price" class="form-label">當前價格</label>
            <input
              id="current_price"
              v-model.number="formData.current_price"
              type="number"
              step="0.01"
              min="0"
              class="form-input"
              placeholder="0.00"
            />
          </div>
          
          <div class="form-group" v-if="isEdit">
            <label for="total_shares" class="form-label">持股數量</label>
            <input
              id="total_shares"
              v-model.number="formData.total_shares"
              type="number"
              step="1"
              min="0"
              class="form-input"
              placeholder="0"
              readonly
              title="持股數量由交易記錄自動計算"
            />
          </div>
        </div>
        
        <div class="form-group" v-if="isEdit">
          <label for="avg_cost" class="form-label">平均成本</label>
          <input
            id="avg_cost"
            v-model.number="formData.avg_cost"
            type="number"
            step="0.01"
            min="0"
            class="form-input"
            placeholder="0.00"
            readonly
            title="平均成本由交易記錄自動計算"
          />
        </div>
        
        <div class="form-actions">
          <button type="button" class="btn btn-secondary" @click="$emit('close')">
            取消
          </button>
          <button type="submit" class="btn btn-primary" :disabled="!isFormValid || loading">
            <span v-if="loading" class="loading-spinner"></span>
            {{ isEdit ? '更新' : '添加' }}
          </button>
        </div>
      </form>
    </div>
  </div>
</template>

<script>
import { defineComponent, ref, computed, watch, onMounted } from 'vue'

export default {
  name: 'StockForm',
  props: {
    stock: {
      type: Object,
      default: null
    },
    visible: {
      type: Boolean,
      default: false
    }
  },
  emits: ['close', 'submit'],
  setup(props, { emit }) {
    const loading = ref(false)
    const stockCodeSuggestions = ref([])
    
    // 表單數據
    const formData = ref({
      stock_code: '',
      stock_name: '',
      market: '',
      currency: 'CNY',
      current_price: 0,
      total_shares: 0,
      avg_cost: 0
    })
    
    // 錯誤信息
    const errors = ref({
      stock_code: '',
      stock_name: '',
      market: ''
    })
    
    // 是否為編輯模式
    const isEdit = computed(() => {
      return props.stock !== null
    })
    
    // 表單是否有效
    const isFormValid = computed(() => {
      return formData.value.stock_code &&
             formData.value.stock_name &&
             formData.value.market &&
             !errors.value.stock_code &&
             !errors.value.stock_name &&
             !errors.value.market
    })
    
    // 重置表單
    const resetForm = () => {
      formData.value = {
        stock_code: '',
        stock_name: '',
        market: '',
        currency: 'CNY',
        current_price: 0,
        total_shares: 0,
        avg_cost: 0
      }
      errors.value = {
        stock_code: '',
        stock_name: '',
        market: ''
      }
      stockCodeSuggestions.value = []
    }
    
    // 監聽股票數據變化
    watch(() => props.stock, (newStock) => {
      if (newStock) {
        formData.value = { ...newStock }
      } else {
        resetForm()
      }
    }, { immediate: true })
    
    // 監聽市場變化，自動設置幣種
    watch(() => formData.value.market, (newMarket) => {
      if (newMarket === 'HK') {
        formData.value.currency = 'HKD'
      } else if (newMarket === 'US') {
        formData.value.currency = 'USD'
      } else {
        formData.value.currency = 'CNY'
      }
    })
    
    // 驗證股票代碼
    const validateStockCode = () => {
      const code = formData.value.stock_code.trim().toUpperCase()
      if (!code) {
        errors.value.stock_code = '請輸入股票代碼'
        return false
      }
      
      // 股票代碼格式驗證，與後端保持一致
      const patterns = {
        'SZ': /^[0-9]{6}\.SZ$/,  // 深圳: 000001.SZ
        'SH': /^[0-9]{6}\.SH$/,  // 上海: 600000.SH
        'HK': /^[0-9]{4,5}\.HK$/, // 香港: 0700.HK 或 00700.HK
        'US': /^[A-Z]{1,5}$/      // 美股: AAPL
      }
      
      let isValid = false
      let detectedMarket = ''
      for (const [market, pattern] of Object.entries(patterns)) {
        if (pattern.test(code)) {
          isValid = true
          detectedMarket = market
          // 自動設置市場（如果未設置）
          if (!formData.value.market) {
            formData.value.market = market
          }
          break
        }
      }
      
      if (!isValid) {
        errors.value.stock_code = '股票代碼格式不正確。支持格式：SZ市場(000001.SZ)、SH市場(600000.SH)、HK市場(0700.HK)、US市場(AAPL)'
        return false
      }
      
      // 更新表單數據為大寫格式
      formData.value.stock_code = code
      errors.value.stock_code = ''
      return true
    }
    
    // 驗證股票名稱
    const validateStockName = () => {
      const name = formData.value.stock_name.trim()
      if (!name) {
        errors.value.stock_name = '請輸入股票名稱'
        return false
      }
      
      if (name.length < 2) {
        errors.value.stock_name = '股票名稱至少需要2個字符'
        return false
      }
      
      errors.value.stock_name = ''
      return true
    }
    
    // 驗證市場
    const validateMarket = () => {
      if (!formData.value.market) {
        errors.value.market = '請選擇市場'
        return false
      }
      
      errors.value.market = ''
      return true
    }
    
    // 股票代碼輸入處理
    const onStockCodeInput = async () => {
      const query = formData.value.stock_code.trim()
      if (query.length >= 2) {
        // 這裡可以調用API獲取股票代碼建議
        // 暫時使用模擬數據
        stockCodeSuggestions.value = getMockSuggestions(query)
      } else {
        stockCodeSuggestions.value = []
      }
    }
    
    // 獲取模擬建議（實際項目中應該調用API）
    const getMockSuggestions = (query) => {
      const mockData = [
        { code: '000001.SZ', name: '平安銀行' },
        { code: '000002.SZ', name: '萬科A' },
        { code: '600000.SH', name: '浦發銀行' },
        { code: '600036.SH', name: '招商銀行' },
        { code: '0700.HK', name: '騰訊控股' },
        { code: '0941.HK', name: '中國移動' },
        { code: 'AAPL', name: 'Apple Inc.' },
        { code: 'TSLA', name: 'Tesla Inc.' }
      ]
      
      return mockData.filter(item => 
        item.code.toLowerCase().includes(query.toLowerCase()) ||
        item.name.toLowerCase().includes(query.toLowerCase())
      ).slice(0, 5)
    }
    
    // 選擇建議
    const selectSuggestion = (suggestion) => {
      formData.value.stock_code = suggestion.code
      formData.value.stock_name = suggestion.name
      
      // 根據代碼自動設置市場
      if (suggestion.code.endsWith('.SZ')) {
        formData.value.market = 'SZ'
      } else if (suggestion.code.endsWith('.SH')) {
        formData.value.market = 'SH'
      } else if (suggestion.code.endsWith('.HK')) {
        formData.value.market = 'HK'
      } else {
        formData.value.market = 'US'
      }
      
      stockCodeSuggestions.value = []
      validateStockCode()
      validateStockName()
    }
    
    // 處理遮罩點擊
    const handleOverlayClick = (event) => {
      if (event.target === event.currentTarget) {
        emit('close')
      }
    }
    
    // 提交表單
    const handleSubmit = async () => {
      // 驗證所有字段
      const isCodeValid = validateStockCode()
      const isNameValid = validateStockName()
      const isMarketValid = validateMarket()
      
      if (!isCodeValid || !isNameValid || !isMarketValid) {
        return
      }
      
      // 只發出事件，讓父組件處理實際的提交邏輯
      emit('submit', formData.value)
    }
    
    // 組件掛載時重置表單
    onMounted(() => {
      if (!props.stock) {
        resetForm()
      }
    })
    
    return {
      formData,
      errors,
      loading,
      stockCodeSuggestions,
      isEdit,
      isFormValid,
      validateStockCode,
      validateStockName,
      validateMarket,
      onStockCodeInput,
      selectSuggestion,
      handleOverlayClick,
      handleSubmit,
      resetForm
    }
  }
}
</script>

<style scoped>
.stock-form-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  padding: 20px;
}

.stock-form-modal {
  background: var(--color-background);
  border-radius: 12px;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.2);
  width: 100%;
  max-width: 600px;
  max-height: 90vh;
  overflow-y: auto;
}

.form-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px 24px;
  border-bottom: 1px solid var(--color-border);
}

.form-header h3 {
  margin: 0;
  font-size: 20px;
  font-weight: 600;
  color: var(--color-text);
}

.close-btn {
  width: 32px;
  height: 32px;
  border: none;
  background: none;
  border-radius: 6px;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--color-text-secondary);
  transition: all 0.2s ease;
}

.close-btn:hover {
  background-color: var(--color-background-soft);
  color: var(--color-text);
}

.icon {
  width: 20px;
  height: 20px;
  fill: currentColor;
}

.form-body {
  padding: 24px;
}

.form-group {
  margin-bottom: 20px;
  position: relative;
}

.form-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 16px;
}

.form-label {
  display: block;
  margin-bottom: 6px;
  font-size: 14px;
  font-weight: 500;
  color: var(--color-text);
}

.form-input,
.form-select {
  width: 100%;
  padding: 10px 12px;
  border: 1px solid var(--color-border);
  border-radius: 6px;
  font-size: 14px;
  background-color: var(--color-background);
  color: var(--color-text);
  transition: all 0.2s ease;
}

.form-input:focus,
.form-select:focus {
  outline: none;
  border-color: var(--color-primary);
  box-shadow: 0 0 0 3px rgba(64, 158, 255, 0.1);
}

.form-input.error,
.form-select.error {
  border-color: var(--color-danger);
}

.form-input:disabled,
.form-input[readonly] {
  background-color: var(--color-background-soft);
  color: var(--color-text-secondary);
  cursor: not-allowed;
}

.error-message {
  margin-top: 4px;
  font-size: 12px;
  color: var(--color-danger);
}

.suggestions {
  position: absolute;
  top: 100%;
  left: 0;
  right: 0;
  background: var(--color-background);
  border: 1px solid var(--color-border);
  border-top: none;
  border-radius: 0 0 6px 6px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  z-index: 10;
  max-height: 200px;
  overflow-y: auto;
}

.suggestion-item {
  padding: 10px 12px;
  cursor: pointer;
  display: flex;
  justify-content: space-between;
  align-items: center;
  transition: background-color 0.2s ease;
}

.suggestion-item:hover {
  background-color: var(--color-background-soft);
}

.suggestion-code {
  font-weight: 500;
  color: var(--color-primary);
}

.suggestion-name {
  color: var(--color-text-secondary);
  font-size: 13px;
}

.form-actions {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
  margin-top: 32px;
  padding-top: 20px;
  border-top: 1px solid var(--color-border);
}

.btn {
  padding: 10px 20px;
  border: none;
  border-radius: 6px;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s ease;
  display: flex;
  align-items: center;
  gap: 6px;
}

.btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.btn-secondary {
  background-color: var(--color-background-soft);
  color: var(--color-text);
  border: 1px solid var(--color-border);
}

.btn-secondary:hover:not(:disabled) {
  background-color: var(--color-background-mute);
}

.btn-primary {
  background-color: var(--color-primary);
  color: white;
}

.btn-primary:hover:not(:disabled) {
  background-color: var(--color-primary-dark);
}

.loading-spinner {
  width: 14px;
  height: 14px;
  border: 2px solid transparent;
  border-top: 2px solid currentColor;
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}

/* 響應式設計 */
@media (max-width: 768px) {
  .stock-form-overlay {
    padding: 10px;
  }
  
  .stock-form-modal {
    max-height: 95vh;
  }
  
  .form-header,
  .form-body {
    padding: 16px;
  }
  
  .form-row {
    grid-template-columns: 1fr;
    gap: 12px;
  }
  
  .form-actions {
    flex-direction: column-reverse;
  }
  
  .btn {
    width: 100%;
    justify-content: center;
  }
}
</style>