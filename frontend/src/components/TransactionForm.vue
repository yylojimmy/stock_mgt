<template>
  <el-dialog
    v-model="dialogVisible"
    :title="isEdit ? '編輯交易記錄' : '新增交易記錄'"
    width="600px"
    :before-close="handleClose"
    destroy-on-close
  >
    <el-form
      ref="formRef"
      :model="formData"
      :rules="formRules"
      label-width="100px"
      label-position="right"
    >
      <!-- 股票代碼 -->
      <el-form-item label="股票代碼" prop="stock_code">
        <el-select
          v-model="formData.stock_code"
          placeholder="請選擇股票"
          filterable
          remote
          :remote-method="searchStocks"
          :loading="stockSearchLoading"
          style="width: 100%"
          @change="handleStockChange"
        >
          <el-option
            v-for="stock in availableStocks"
            :key="stock.stock_code"
            :label="`${stock.stock_code} - ${stock.stock_name}`"
            :value="stock.stock_code"
          >
            <span style="float: left">{{ stock.stock_code }}</span>
            <span style="float: right; color: #8492a6; font-size: 13px">
              {{ stock.stock_name }}
            </span>
          </el-option>
        </el-select>
      </el-form-item>

      <!-- 交易類型 -->
      <el-form-item label="交易類型" prop="transaction_type">
        <el-radio-group v-model="formData.transaction_type">
          <el-radio value="BUY">
            <el-tag type="success" size="small">買入</el-tag>
          </el-radio>
          <el-radio value="SELL">
            <el-tag type="danger" size="small">賣出</el-tag>
          </el-radio>
        </el-radio-group>
      </el-form-item>

      <!-- 交易日期 -->
      <el-form-item label="交易日期" prop="transaction_date">
        <el-date-picker
          v-model="formData.transaction_date"
          type="date"
          placeholder="選擇交易日期"
          format="YYYY-MM-DD"
          value-format="YYYY-MM-DD"
          style="width: 100%"
          :disabled-date="disabledDate"
        />
      </el-form-item>

      <!-- 交易價格 -->
      <el-form-item label="交易價格" prop="price">
        <el-input-number
          v-model="formData.price"
          :precision="4"
          :step="0.01"
          :min="0.0001"
          :max="9999.9999"
          placeholder="請輸入交易價格"
          style="width: 100%"
          @change="calculateTotalAmount"
        >
          <template #append>元</template>
        </el-input-number>
      </el-form-item>

      <!-- 交易股數 -->
      <el-form-item label="交易股數" prop="shares">
        <el-input-number
          v-model="formData.shares"
          :precision="0"
          :step="100"
          :min="1"
          :max="999999999"
          placeholder="請輸入交易股數"
          style="width: 100%"
          @change="calculateTotalAmount"
        >
          <template #append>股</template>
        </el-input-number>
      </el-form-item>

      <!-- 總金額（自動計算） -->
      <el-form-item label="總金額">
        <el-input
          :value="formatCurrency(calculatedTotalAmount)"
          readonly
          style="width: 100%"
        >
          <template #append>元</template>
        </el-input>
      </el-form-item>

      <!-- 手續費 -->
      <el-form-item label="手續費" prop="commission">
        <el-input-number
          v-model="formData.commission"
          :precision="2"
          :step="1"
          :min="0"
          :max="99999.99"
          placeholder="請輸入手續費（可選）"
          style="width: 100%"
        >
          <template #append>元</template>
        </el-input-number>
      </el-form-item>

      <!-- 備註 -->
      <el-form-item label="備註" prop="notes">
        <el-input
          v-model="formData.notes"
          type="textarea"
          :rows="3"
          :maxlength="500"
          show-word-limit
          placeholder="請輸入備註信息（可選）"
        />
      </el-form-item>

      <!-- 賣出警告提示 -->
      <el-form-item v-if="formData.transaction_type === 'SELL' && selectedStock">
        <el-alert
          :title="`當前持股：${formatNumber(selectedStock.total_shares)} 股`"
          type="info"
          show-icon
          :closable="false"
        >
          <template #default>
            <div v-if="formData.shares > selectedStock.total_shares">
              <el-text type="danger">
                警告：賣出股數 ({{ formatNumber(formData.shares) }}) 超過持有股數！
              </el-text>
            </div>
            <div v-else-if="formData.shares > 0">
              <el-text type="success">
                賣出後剩餘：{{ formatNumber(selectedStock.total_shares - formData.shares) }} 股
              </el-text>
            </div>
          </template>
        </el-alert>
      </el-form-item>
    </el-form>

    <template #footer>
      <div class="dialog-footer">
        <el-button @click="handleClose">取消</el-button>
        <el-button type="primary" :loading="submitLoading" @click="handleSubmit">
          {{ isEdit ? '更新' : '創建' }}
        </el-button>
      </div>
    </template>
  </el-dialog>
</template>

<script setup>
import { ref, reactive, computed, watch, nextTick } from 'vue'
import { ElMessage } from 'element-plus'
import { useTransactionStore, useStockStore } from '../stores'

// Props
const props = defineProps({
  // 是否顯示對話框
  visible: {
    type: Boolean,
    default: false
  },
  // 編輯的交易記錄數據
  editData: {
    type: Object,
    default: null
  }
})

// Emits
const emit = defineEmits(['update:visible', 'success', 'cancel'])

// Stores
const transactionStore = useTransactionStore()
const stockStore = useStockStore()

// 響應式數據
const formRef = ref()
const dialogVisible = ref(false)
const submitLoading = ref(false)
const stockSearchLoading = ref(false)
const availableStocks = ref([])

// 表單數據
const formData = reactive({
  stock_code: '',
  transaction_type: 'BUY',
  transaction_date: '',
  price: null,
  shares: null,
  commission: 0,
  notes: ''
})

// 表單驗證規則
const formRules = {
  stock_code: [
    { required: true, message: '請選擇股票', trigger: 'change' }
  ],
  transaction_type: [
    { required: true, message: '請選擇交易類型', trigger: 'change' }
  ],
  transaction_date: [
    { required: true, message: '請選擇交易日期', trigger: 'change' }
  ],
  price: [
    { required: true, message: '請輸入交易價格', trigger: 'blur' },
    { type: 'number', min: 0.0001, message: '價格必須大於0', trigger: 'blur' }
  ],
  shares: [
    { required: true, message: '請輸入交易股數', trigger: 'blur' },
    { type: 'number', min: 1, message: '股數必須大於0', trigger: 'blur' }
  ],
  commission: [
    { type: 'number', min: 0, message: '手續費不能為負數', trigger: 'blur' }
  ],
  notes: [
    { max: 500, message: '備註不能超過500個字符', trigger: 'blur' }
  ]
}

// 計算屬性
const isEdit = computed(() => !!props.editData)

const selectedStock = computed(() => {
  return availableStocks.value.find(stock => stock.stock_code === formData.stock_code)
})

const calculatedTotalAmount = computed(() => {
  if (formData.price && formData.shares) {
    return formData.price * formData.shares
  }
  return 0
})

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

// 日期禁用函數
const disabledDate = (time) => {
  // 禁用未來日期
  return time.getTime() > Date.now()
}

// 事件處理函數
const handleClose = () => {
  dialogVisible.value = false
  emit('update:visible', false)
  emit('cancel')
  resetForm()
}

const handleStockChange = (stockCode) => {
  // 當選擇股票時，可以獲取當前價格作為默認值
  const stock = availableStocks.value.find(s => s.stock_code === stockCode)
  if (stock && stock.current_price && !formData.price) {
    formData.price = stock.current_price
    calculateTotalAmount()
  }
}

const calculateTotalAmount = () => {
  // 總金額會通過計算屬性自動更新
  // 這個函數主要用於觸發重新計算
}

const searchStocks = async (query) => {
  if (query) {
    stockSearchLoading.value = true
    try {
      // 從已有股票中搜索
      availableStocks.value = stockStore.stocks.filter(stock => 
        stock.stock_code.toLowerCase().includes(query.toLowerCase()) ||
        stock.stock_name.toLowerCase().includes(query.toLowerCase())
      )
    } finally {
      stockSearchLoading.value = false
    }
  } else {
    // 顯示所有股票
    availableStocks.value = stockStore.stocks
  }
}

const handleSubmit = async () => {
  try {
    // 表單驗證
    await formRef.value.validate()
    
    // 賣出股數驗證
    if (formData.transaction_type === 'SELL' && selectedStock.value) {
      if (formData.shares > selectedStock.value.total_shares) {
        ElMessage.error('賣出股數不能超過持有股數')
        return
      }
    }
    
    submitLoading.value = true
    
    // 準備提交數據
    const submitData = {
      stock_code: formData.stock_code,
      transaction_type: formData.transaction_type,
      transaction_date: formData.transaction_date,
      price: formData.price,
      shares: formData.shares,
      commission: formData.commission || 0,
      notes: formData.notes || ''
    }
    
    let result
    if (isEdit.value) {
      // 更新交易記錄
      result = await transactionStore.updateTransaction(props.editData.id, submitData)
    } else {
      // 創建新交易記錄
      result = await transactionStore.createTransaction(submitData)
    }
    
    ElMessage.success(isEdit.value ? '交易記錄更新成功' : '交易記錄創建成功')
    
    // 關閉對話框並通知父組件
    dialogVisible.value = false
    emit('update:visible', false)
    emit('success', result)
    
    resetForm()
    
  } catch (error) {
    ElMessage.error((isEdit.value ? '更新' : '創建') + '失敗：' + (error.message || error))
  } finally {
    submitLoading.value = false
  }
}

const resetForm = () => {
  // 重置表單數據
  Object.assign(formData, {
    stock_code: '',
    transaction_type: 'BUY',
    transaction_date: '',
    price: null,
    shares: null,
    commission: 0,
    notes: ''
  })
  
  // 清除表單驗證
  nextTick(() => {
    formRef.value?.clearValidate()
  })
}

const initForm = () => {
  if (isEdit.value && props.editData) {
    // 編輯模式：填充現有數據
    Object.assign(formData, {
      stock_code: props.editData.stock_code,
      transaction_type: props.editData.transaction_type,
      transaction_date: props.editData.transaction_date,
      price: props.editData.price,
      shares: props.editData.shares,
      commission: props.editData.commission || 0,
      notes: props.editData.notes || ''
    })
  } else {
    // 新增模式：設置默認值
    formData.transaction_date = new Date().toISOString().split('T')[0]
  }
}

// 監聽器
watch(() => props.visible, (newValue) => {
  dialogVisible.value = newValue
  if (newValue) {
    // 對話框打開時初始化
    initForm()
    // 加載股票列表
    if (stockStore.stocks.length === 0) {
      stockStore.fetchStocks()
    }
    availableStocks.value = stockStore.stocks
  }
})

watch(() => props.editData, () => {
  if (dialogVisible.value) {
    initForm()
  }
})
</script>

<style scoped>
.dialog-footer {
  text-align: right;
}

.dialog-footer .el-button {
  margin-left: 8px;
}

/* 表單樣式優化 */
:deep(.el-form-item__label) {
  font-weight: 500;
}

:deep(.el-input-number) {
  width: 100%;
}

:deep(.el-radio-group) {
  display: flex;
  gap: 16px;
}

:deep(.el-radio) {
  margin-right: 0;
}

/* 響應式設計 */
@media (max-width: 768px) {
  .el-dialog {
    width: 90% !important;
    margin: 5vh auto;
  }
  
  :deep(.el-form) {
    .el-form-item__label {
      width: 80px !important;
    }
  }
}

@media (max-width: 480px) {
  .el-dialog {
    width: 95% !important;
    margin: 2vh auto;
  }
  
  :deep(.el-form) {
    .el-form-item__label {
      width: 70px !important;
      font-size: 12px;
    }
  }
}
</style>