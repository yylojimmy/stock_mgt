<template>
  <div class="dividend-table">
    <!-- 批量操作工具欄 -->
    <div v-if="selectedRows.length > 0" class="batch-toolbar">
      <el-alert
        :title="`已選擇 ${selectedRows.length} 條記錄`"
        type="info"
        show-icon
        :closable="false"
      >
        <template #default>
          <div class="batch-actions">
            <el-button
              type="danger"
              size="small"
              @click="handleBatchDelete"
              :loading="batchDeleting"
            >
              <el-icon><Delete /></el-icon>
              批量刪除
            </el-button>
            <el-button size="small" @click="clearSelection">
              取消選擇
            </el-button>
          </div>
        </template>
      </el-alert>
    </div>

    <!-- 數據表格 -->
    <el-table
      ref="tableRef"
      v-loading="loading"
      :data="dividends"
      stripe
      style="width: 100%"
      @selection-change="handleSelectionChange"
      :row-key="'id'"
    >
      <!-- 選擇列 -->
      <el-table-column type="selection" width="55" :reserve-selection="true" />
      
      <!-- 股息日期 -->
      <el-table-column prop="dividend_date" label="股息日期" width="120" sortable>
        <template #default="{ row }">
          {{ formatDate(row.dividend_date) }}
        </template>
      </el-table-column>
      
      <!-- 股票代碼 -->
      <el-table-column prop="stock_code" label="股票代碼" width="120" sortable>
        <template #default="{ row }">
          <el-tag type="primary" size="small">{{ row.stock_code }}</el-tag>
        </template>
      </el-table-column>
      
      <!-- 每股股息 -->
      <el-table-column prop="dividend_per_share" label="每股股息" width="120" sortable>
        <template #default="{ row }">
          <span class="amount-text">
            {{ formatCurrency(row.dividend_per_share, row.currency) }}
          </span>
        </template>
      </el-table-column>
      
      <!-- 總股息 -->
      <el-table-column prop="total_dividend" label="總股息" width="140" sortable>
        <template #default="{ row }">
          <span class="amount-text positive">
            {{ formatCurrency(row.total_dividend, row.currency) }}
          </span>
        </template>
      </el-table-column>
      
      <!-- 稅額 -->
      <el-table-column prop="tax_amount" label="稅額" width="120" sortable>
        <template #default="{ row }">
          <span class="amount-text negative">
            {{ formatCurrency(row.tax_amount, row.currency) }}
          </span>
        </template>
      </el-table-column>
      
      <!-- 淨股息 -->
      <el-table-column prop="net_dividend" label="淨股息" width="140" sortable>
        <template #default="{ row }">
          <span class="amount-text positive">
            {{ formatCurrency(row.net_dividend, row.currency) }}
          </span>
        </template>
      </el-table-column>
      
      <!-- 幣種 -->
      <el-table-column prop="currency" label="幣種" width="80" sortable>
        <template #default="{ row }">
          <el-tag :type="getCurrencyTagType(row.currency)" size="small">
            {{ row.currency }}
          </el-tag>
        </template>
      </el-table-column>
      
      <!-- 備註 -->
      <el-table-column prop="notes" label="備註" min-width="150" show-overflow-tooltip>
        <template #default="{ row }">
          <span class="notes-text">{{ row.notes || '-' }}</span>
        </template>
      </el-table-column>
      
      <!-- 操作列 -->
      <el-table-column label="操作" width="120" fixed="right">
        <template #default="{ row }">
          <div class="action-buttons">
            <el-button
              type="primary"
              size="small"
              text
              @click="handleEdit(row)"
              :icon="Edit"
            >
              編輯
            </el-button>
            <el-button
              type="danger"
              size="small"
              text
              @click="handleDelete(row)"
              :icon="Delete"
            >
              刪除
            </el-button>
          </div>
        </template>
      </el-table-column>
    </el-table>

    <!-- 分頁組件 -->
    <div v-if="pagination.total > 0" class="pagination-wrapper">
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

    <!-- 空狀態 -->
    <div v-if="!loading && dividends.length === 0" class="empty-state">
      <el-empty description="暫無股息記錄" />
    </div>
  </div>
</template>

<script>
import { ref, computed } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Edit, Delete } from '@element-plus/icons-vue'

export default {
  name: 'DividendTable',
  components: {
    Edit,
    Delete
  },
  props: {
    dividends: {
      type: Array,
      default: () => []
    },
    loading: {
      type: Boolean,
      default: false
    },
    pagination: {
      type: Object,
      default: () => ({
        total: 0,
        page: 1,
        per_page: 20
      })
    }
  },
  emits: ['edit', 'delete', 'batch-delete', 'page-change', 'size-change'],
  setup(props, { emit }) {
    const tableRef = ref()
    const selectedRows = ref([])
    const batchDeleting = ref(false)

    // 格式化日期
    const formatDate = (value) => {
      if (!value) return '-'
      return new Date(value).toLocaleDateString('zh-CN')
    }

    // 格式化貨幣
    const formatCurrency = (value, currency = 'CNY') => {
      if (value === null || value === undefined) return '0.00'
      return new Intl.NumberFormat('zh-CN', {
        style: 'currency',
        currency: currency,
        minimumFractionDigits: 2
      }).format(value)
    }

    // 獲取幣種標籤類型
    const getCurrencyTagType = (currency) => {
      const typeMap = {
        'CNY': 'success',
        'HKD': 'warning',
        'USD': 'info'
      }
      return typeMap[currency] || 'default'
    }

    // 處理選擇變化
    const handleSelectionChange = (selection) => {
      selectedRows.value = selection
    }

    // 清除選擇
    const clearSelection = () => {
      tableRef.value.clearSelection()
      selectedRows.value = []
    }

    // 處理編輯
    const handleEdit = (row) => {
      emit('edit', row)
    }

    // 處理刪除
    const handleDelete = async (row) => {
      try {
        await ElMessageBox.confirm(
          `確定要刪除股票 ${row.stock_code} 在 ${formatDate(row.dividend_date)} 的股息記錄嗎？`,
          '確認刪除',
          {
            confirmButtonText: '確定',
            cancelButtonText: '取消',
            type: 'warning'
          }
        )
        emit('delete', row.id)
      } catch {
        // 用戶取消刪除
      }
    }

    // 處理批量刪除
    const handleBatchDelete = async () => {
      if (selectedRows.value.length === 0) {
        ElMessage.warning('請先選擇要刪除的記錄')
        return
      }

      try {
        await ElMessageBox.confirm(
          `確定要刪除選中的 ${selectedRows.value.length} 條股息記錄嗎？`,
          '確認批量刪除',
          {
            confirmButtonText: '確定',
            cancelButtonText: '取消',
            type: 'warning'
          }
        )

        batchDeleting.value = true
        const ids = selectedRows.value.map(row => row.id)
        emit('batch-delete', ids)
        
        // 清除選擇
        clearSelection()
      } catch {
        // 用戶取消刪除
      } finally {
        batchDeleting.value = false
      }
    }

    // 處理分頁大小變化
    const handleSizeChange = (size) => {
      emit('size-change', size)
    }

    // 處理當前頁變化
    const handleCurrentChange = (page) => {
      emit('page-change', page)
    }

    return {
      tableRef,
      selectedRows,
      batchDeleting,
      formatDate,
      formatCurrency,
      getCurrencyTagType,
      handleSelectionChange,
      clearSelection,
      handleEdit,
      handleDelete,
      handleBatchDelete,
      handleSizeChange,
      handleCurrentChange
    }
  }
}
</script>

<style scoped>
.dividend-table {
  width: 100%;
}

.batch-toolbar {
  margin-bottom: 16px;
}

.batch-actions {
  display: flex;
  gap: 8px;
  align-items: center;
}

.amount-text {
  font-weight: 500;
  font-family: 'Monaco', 'Menlo', monospace;
}

.amount-text.positive {
  color: #67c23a;
}

.amount-text.negative {
  color: #f56c6c;
}

.notes-text {
  color: #606266;
  font-size: 13px;
}

.action-buttons {
  display: flex;
  gap: 4px;
}

.pagination-wrapper {
  margin-top: 20px;
  display: flex;
  justify-content: center;
}

.empty-state {
  margin-top: 40px;
}

/* 響應式設計 */
@media (max-width: 768px) {
  .dividend-table {
    font-size: 14px;
  }
  
  .action-buttons {
    flex-direction: column;
    gap: 2px;
  }
  
  .batch-actions {
    flex-direction: column;
    align-items: flex-start;
    gap: 4px;
  }
}

@media (max-width: 480px) {
  .pagination-wrapper {
    overflow-x: auto;
  }
}
</style>