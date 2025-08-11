<template>
  <el-dialog
    v-model="dialogVisible"
    :title="isEdit ? '編輯股息記錄' : '新增股息記錄'"
    width="600px"
    :before-close="handleClose"
    destroy-on-close
  >
    <el-form
      ref="formRef"
      :model="formData"
      :rules="formRules"
      label-width="120px"
      label-position="right"
    >
      <!-- 股票代碼 -->
      <el-form-item label="股票代碼" prop="stock_code">
        <el-select
          v-model="formData.stock_code"
          placeholder="請選擇股票代碼"
          filterable
          remote
          :remote-method="searchStocks"
          :loading="stocksLoading"
          style="width: 100%"
          @change="handleStockChange"
        >
          <el-option
            v-for="stock in stockOptions"
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

      <!-- 股息發放日期 -->
      <el-form-item label="股息發放日期" prop="dividend_date">
        <el-date-picker
          v-model="formData.dividend_date"
          type="date"
          placeholder="請選擇股息發放日期"
          style="width: 100%"
          format="YYYY-MM-DD"
          value-format="YYYY-MM-DD"
        />
      </el-form-item>

      <!-- 每股股息 -->
      <el-form-item label="每股股息" prop="dividend_per_share">
        <el-input
          v-model.number="formData.dividend_per_share"
          type="number"
          placeholder="請輸入每股股息金額"
          step="0.0001"
          min="0"
        >
          <template #append>
            <span>{{ formData.currency || 'CNY' }}</span>
          </template>
        </el-input>
      </el-form-item>

      <!-- 總股息金額 -->
      <el-form-item label="總股息金額" prop="total_dividend">
        <el-input
          v-model.number="formData.total_dividend"
          type="number"
          placeholder="請輸入總股息金額"
          step="0.01"
          min="0"
        >
          <template #append>
            <span>{{ formData.currency || 'CNY' }}</span>
          </template>
        </el-input>
        <div class="form-tip">
          <el-text size="small" type="info">
            提示：總股息 = 每股股息 × 持股數量
          </el-text>
        </div>
      </el-form-item>

      <!-- 稅額 -->
      <el-form-item label="稅額" prop="tax_amount">
        <el-input
          v-model.number="formData.tax_amount"
          type="number"
          placeholder="請輸入稅額（可選）"
          step="0.01"
          min="0"
        >
          <template #append>
            <span>{{ formData.currency || 'CNY' }}</span>
          </template>
        </el-input>
      </el-form-item>

      <!-- 稅後股息（自動計算） -->
      <el-form-item label="稅後股息">
        <el-input
          :value="netDividendDisplay"
          readonly
          placeholder="自動計算"
        >
          <template #append>
            <span>{{ formData.currency || 'CNY' }}</span>
          </template>
        </el-input>
        <div class="form-tip">
          <el-text size="small" type="info">
            自動計算：稅後股息 = 總股息 - 稅額
          </el-text>
        </div>
      </el-form-item>

      <!-- 幣種 -->
      <el-form-item label="幣種" prop="currency">
        <el-select
          v-model="formData.currency"
          placeholder="請選擇幣種"
          style="width: 100%"
        >
          <el-option label="人民幣 (CNY)" value="CNY" />
          <el-option label="港幣 (HKD)" value="HKD" />
          <el-option label="美元 (USD)" value="USD" />
        </el-select>
      </el-form-item>

      <!-- 備註 -->
      <el-form-item label="備註" prop="notes">
        <el-input
          v-model="formData.notes"
          type="textarea"
          :rows="3"
          placeholder="請輸入備註信息（可選）"
          maxlength="500"
          show-word-limit
        />
      </el-form-item>
    </el-form>

    <template #footer>
      <div class="dialog-footer">
        <el-button @click="handleClose">取消</el-button>
        <el-button
          type="primary"
          @click="handleSubmit"
          :loading="submitting"
        >
          {{ isEdit ? '更新' : '創建' }}
        </el-button>
      </div>
    </template>
  </el-dialog>
</template>

<script>
import { ref, computed, watch, nextTick } from 'vue'
import { ElMessage } from 'element-plus'
import { useStockStore, useDividendStore } from '../stores'

export default {
  name: 'DividendForm',
  props: {
    visible: {
      type: Boolean,
      default: false
    },
    editData: {
      type: Object,
      default: null
    }
  },
  emits: ['update:visible', 'success'],
  setup(props, { emit }) {
    const stockStore = useStockStore()
    const dividendStore = useDividendStore()
    
    const formRef = ref()
    const submitting = ref(false)
    const stocksLoading = ref(false)
    const stockOptions = ref([])

    // 表單數據
    const formData = ref({
      stock_code: '',
      dividend_date: '',
      dividend_per_share: null,
      total_dividend: null,
      tax_amount: 0,
      currency: 'CNY',
      notes: ''
    })

    // 是否為編輯模式
    const isEdit = computed(() => {
      return props.editData && props.editData.id
    })

    // 對話框顯示狀態
    const dialogVisible = computed({
      get: () => props.visible,
      set: (value) => emit('update:visible', value)
    })

    // 稅後股息顯示
    const netDividendDisplay = computed(() => {
      const total = formData.value.total_dividend || 0
      const tax = formData.value.tax_amount || 0
      const net = total - tax
      return net.toFixed(2)
    })

    // 表單驗證規則
    const formRules = {
      stock_code: [
        { required: true, message: '請選擇股票代碼', trigger: 'change' }
      ],
      dividend_date: [
        { required: true, message: '請選擇股息發放日期', trigger: 'change' }
      ],
      dividend_per_share: [
        { required: true, message: '請輸入每股股息', trigger: 'blur' },
        { type: 'number', min: 0, message: '每股股息必須大於等於0', trigger: 'blur' }
      ],
      total_dividend: [
        { required: true, message: '請輸入總股息金額', trigger: 'blur' },
        { type: 'number', min: 0, message: '總股息金額必須大於等於0', trigger: 'blur' }
      ],
      tax_amount: [
        { type: 'number', min: 0, message: '稅額必須大於等於0', trigger: 'blur' }
      ],
      currency: [
        { required: true, message: '請選擇幣種', trigger: 'change' }
      ]
    }

    // 搜索股票
    const searchStocks = async (query) => {
      if (!query) {
        stockOptions.value = []
        return
      }

      stocksLoading.value = true
      try {
        // 獲取所有股票並進行本地篩選
        await stockStore.fetchStocks()
        stockOptions.value = stockStore.stocks.filter(stock => 
          stock.stock_code.toLowerCase().includes(query.toLowerCase()) ||
          stock.stock_name.toLowerCase().includes(query.toLowerCase())
        )
      } catch (error) {
        console.error('搜索股票失敗:', error)
        ElMessage.error('搜索股票失敗')
      } finally {
        stocksLoading.value = false
      }
    }

    // 處理股票選擇變化
    const handleStockChange = (stockCode) => {
      const selectedStock = stockOptions.value.find(s => s.stock_code === stockCode)
      if (selectedStock) {
        // 自動設置幣種
        formData.value.currency = selectedStock.currency || 'HKD'
      }
    }

    // 重置表單
    const resetForm = () => {
      formData.value = {
        stock_code: '',
        dividend_date: '',
        dividend_per_share: null,
        total_dividend: null,
        tax_amount: 0,
        currency: 'HKD',
        notes: ''
      }
      stockOptions.value = []
      
      nextTick(() => {
        if (formRef.value) {
          formRef.value.clearValidate()
        }
      })
    }

    // 初始化表單
    const initForm = () => {
      if (isEdit.value && props.editData) {
        // 編輯模式：填充現有數據
        formData.value = {
          stock_code: props.editData.stock_code,
          dividend_date: props.editData.dividend_date,
          dividend_per_share: props.editData.dividend_per_share,
          total_dividend: props.editData.total_dividend,
          tax_amount: props.editData.tax_amount || 0,
          currency: props.editData.currency || 'HKD',
          notes: props.editData.notes || ''
        }
        
        // 加載股票選項
        if (props.editData.stock_code) {
          searchStocks(props.editData.stock_code)
        }
      } else {
        // 新增模式：設置默認值
        resetForm()
        formData.value.dividend_date = new Date().toISOString().split('T')[0]
      }
    }

    // 處理提交
    const handleSubmit = async () => {
      if (!formRef.value) return

      try {
        // 表單驗證
        await formRef.value.validate()
        
        submitting.value = true
        
        // 準備提交數據
        const submitData = {
          ...formData.value
        }
        
        // 移除net_dividend字段，後端會自動計算
        delete submitData.net_dividend

        if (isEdit.value) {
          // 更新股息記錄
          await dividendStore.updateDividend(props.editData.id, submitData)
          ElMessage.success('股息記錄更新成功')
        } else {
          // 創建股息記錄
          await dividendStore.createDividend(submitData)
          ElMessage.success('股息記錄創建成功')
        }

        // 關閉對話框並通知父組件
        dialogVisible.value = false
        emit('success')
        resetForm()
        
      } catch (error) {
        console.error('提交失敗:', error)
        ElMessage.error(error.message || '操作失敗')
      } finally {
        submitting.value = false
      }
    }

    // 處理關閉
    const handleClose = () => {
      dialogVisible.value = false
      resetForm()
    }

    // 監聽對話框顯示狀態
    watch(
      () => props.visible,
      (newVal) => {
        if (newVal) {
          initForm()
          // 初始加載股票列表
          searchStocks('')
        }
      }
    )

    // 監聽編輯數據變化
    watch(
      () => props.editData,
      () => {
        if (props.visible) {
          initForm()
        }
      },
      { deep: true }
    )

    return {
      formRef,
      formData,
      formRules,
      submitting,
      stocksLoading,
      stockOptions,
      isEdit,
      dialogVisible,
      netDividendDisplay,
      searchStocks,
      handleStockChange,
      handleSubmit,
      handleClose,
      resetForm
    }
  }
}
</script>

<style scoped>
.form-tip {
  margin-top: 4px;
}

.dialog-footer {
  text-align: right;
}

/* 響應式設計 */
@media (max-width: 768px) {
  :deep(.el-dialog) {
    width: 95% !important;
    margin: 5vh auto;
  }
  
  :deep(.el-form-item__label) {
    width: 100px !important;
  }
}
</style>