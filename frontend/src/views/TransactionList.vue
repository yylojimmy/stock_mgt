<template>
  <div class="transaction-list">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>交易記錄</span>
          <el-button type="primary">
            <el-icon><Plus /></el-icon>
            添加交易
          </el-button>
        </div>
      </template>
      
      <el-table 
        v-loading="transactionStore.loading"
        :data="transactionStore.transactions"
        stripe
        style="width: 100%"
      >
        <el-table-column prop="transaction_date" label="交易日期" width="120">
          <template #default="{ row }">
            {{ formatDate(row.transaction_date) }}
          </template>
        </el-table-column>
        <el-table-column prop="stock_code" label="股票代碼" width="120" />
        <el-table-column prop="transaction_type" label="交易類型" width="100">
          <template #default="{ row }">
            <el-tag :type="row.transaction_type === 'BUY' ? 'success' : 'danger'">
              {{ row.transaction_type === 'BUY' ? '買入' : '賣出' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="price" label="價格" width="100">
          <template #default="{ row }">
            {{ formatCurrency(row.price) }}
          </template>
        </el-table-column>
        <el-table-column prop="shares" label="股數" width="100">
          <template #default="{ row }">
            {{ formatNumber(row.shares) }}
          </template>
        </el-table-column>
        <el-table-column prop="total_amount" label="總金額" width="120">
          <template #default="{ row }">
            {{ formatCurrency(row.total_amount) }}
          </template>
        </el-table-column>
        <el-table-column prop="commission" label="手續費" width="100">
          <template #default="{ row }">
            {{ formatCurrency(row.commission) }}
          </template>
        </el-table-column>
        <el-table-column prop="notes" label="備註" min-width="150" />
      </el-table>
    </el-card>
  </div>
</template>

<script>
import { onMounted } from 'vue'
import { useTransactionStore } from '../stores'
import { Plus } from '@element-plus/icons-vue'

export default {
  name: 'TransactionList',
  components: {
    Plus
  },
  setup() {
    const transactionStore = useTransactionStore()

    // 格式化日期
    const formatDate = (value) => {
      if (!value) return '-'
      return new Date(value).toLocaleDateString('zh-CN')
    }

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

    // 組件掛載時獲取數據
    onMounted(() => {
      transactionStore.fetchTransactions()
    })

    return {
      transactionStore,
      formatDate,
      formatCurrency,
      formatNumber
    }
  }
}
</script>

<style scoped>
.transaction-list {
  padding: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

/* 響應式設計 */
@media (max-width: 768px) {
  .transaction-list {
    padding: 10px;
  }
}
</style>