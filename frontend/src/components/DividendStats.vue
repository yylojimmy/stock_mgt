<template>
  <div class="dividend-stats">
    <!-- 統計卡片 -->
    <div class="stats-cards">
      <!-- 總股息 -->
      <el-card class="stats-card" shadow="hover">
        <div class="stats-content">
          <div class="stats-icon total">
            <el-icon size="24"><Money /></el-icon>
          </div>
          <div class="stats-info">
            <div class="stats-value">{{ formatCurrency(stats.total_dividend || 0) }}</div>
            <div class="stats-label">總股息</div>
          </div>
        </div>
      </el-card>

      <!-- 稅額 -->
      <el-card class="stats-card" shadow="hover">
        <div class="stats-content">
          <div class="stats-icon tax">
            <el-icon size="24"><Document /></el-icon>
          </div>
          <div class="stats-info">
            <div class="stats-value">{{ formatCurrency(stats.total_tax || 0) }}</div>
            <div class="stats-label">總稅額</div>
          </div>
        </div>
      </el-card>

      <!-- 淨股息 -->
      <el-card class="stats-card" shadow="hover">
        <div class="stats-content">
          <div class="stats-icon net">
            <el-icon size="24"><Wallet /></el-icon>
          </div>
          <div class="stats-info">
            <div class="stats-value">{{ formatCurrency(stats.net_dividend || 0) }}</div>
            <div class="stats-label">淨股息</div>
          </div>
        </div>
      </el-card>

      <!-- 記錄數量 -->
      <el-card class="stats-card" shadow="hover">
        <div class="stats-content">
          <div class="stats-icon count">
            <el-icon size="24"><Document /></el-icon>
          </div>
          <div class="stats-info">
            <div class="stats-value">{{ stats.total_records || 0 }}</div>
            <div class="stats-label">記錄數量</div>
          </div>
        </div>
      </el-card>
    </div>

    <!-- 按幣種統計 -->
    <div v-if="stats.by_currency && Object.keys(stats.by_currency).length > 0" class="currency-stats">
      <el-card>
        <template #header>
          <div class="card-header">
            <span>按幣種統計</span>
          </div>
        </template>
        
        <div class="currency-grid">
          <div 
            v-for="(currencyData, currency) in stats.by_currency" 
            :key="currency"
            class="currency-item"
          >
            <div class="currency-header">
              <el-tag :type="getCurrencyTagType(currency)" size="large">
                {{ currency }}
              </el-tag>
            </div>
            <div class="currency-details">
              <div class="detail-row">
                <span class="detail-label">總股息:</span>
                <span class="detail-value positive">
                  {{ formatCurrency(currencyData.total_dividend, currency) }}
                </span>
              </div>
              <div class="detail-row">
                <span class="detail-label">稅額:</span>
                <span class="detail-value negative">
                  {{ formatCurrency(currencyData.total_tax, currency) }}
                </span>
              </div>
              <div class="detail-row">
                <span class="detail-label">淨股息:</span>
                <span class="detail-value positive">
                  {{ formatCurrency(currencyData.net_dividend, currency) }}
                </span>
              </div>
              <div class="detail-row">
                <span class="detail-label">記錄數:</span>
                <span class="detail-value">{{ currencyData.count }}</span>
              </div>
            </div>
          </div>
        </div>
      </el-card>
    </div>

    <!-- 按股票統計 -->
    <div v-if="stats.by_stock && stats.by_stock.length > 0" class="stock-stats">
      <el-card>
        <template #header>
          <div class="card-header">
            <span>按股票統計 (前10名)</span>
          </div>
        </template>
        
        <el-table 
          :data="topStockStats" 
          stripe 
          style="width: 100%"
          :default-sort="{ prop: 'net_dividend', order: 'descending' }"
        >
          <el-table-column prop="stock_code" label="股票代碼" width="120">
            <template #default="{ row }">
              <el-tag type="primary" size="small">{{ row.stock_code }}</el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="total_dividend" label="總股息" sortable>
            <template #default="{ row }">
              <span class="amount-text positive">
                {{ formatCurrency(row.total_dividend) }}
              </span>
            </template>
          </el-table-column>
          <el-table-column prop="total_tax" label="稅額" sortable>
            <template #default="{ row }">
              <span class="amount-text negative">
                {{ formatCurrency(row.total_tax) }}
              </span>
            </template>
          </el-table-column>
          <el-table-column prop="net_dividend" label="淨股息" sortable>
            <template #default="{ row }">
              <span class="amount-text positive">
                {{ formatCurrency(row.net_dividend) }}
              </span>
            </template>
          </el-table-column>
          <el-table-column prop="count" label="記錄數" width="100" sortable />
        </el-table>
      </el-card>
    </div>

    <!-- 月度趨勢 -->
    <div v-if="stats.monthly_trend && stats.monthly_trend.length > 0" class="trend-stats">
      <el-card>
        <template #header>
          <div class="card-header">
            <span>月度趨勢</span>
          </div>
        </template>
        
        <div class="trend-chart">
          <!-- 這裡可以集成圖表庫，如Chart.js或ECharts -->
          <div class="trend-list">
            <div 
              v-for="item in recentTrend" 
              :key="item.month"
              class="trend-item"
            >
              <div class="trend-month">{{ item.month }}</div>
              <div class="trend-amount">
                <span class="amount-text positive">
                  {{ formatCurrency(item.net_dividend) }}
                </span>
              </div>
              <div class="trend-count">{{ item.count }} 筆</div>
            </div>
          </div>
        </div>
      </el-card>
    </div>

    <!-- 空狀態 -->
    <div v-if="!hasData" class="empty-state">
      <el-empty description="暫無統計數據" />
    </div>
  </div>
</template>

<script>
import { computed } from 'vue'
import { Money, Document, Wallet } from '@element-plus/icons-vue'

export default {
  name: 'DividendStats',
  components: {
    Money,
    Document,
    Wallet
  },
  props: {
    stats: {
      type: Object,
      default: () => ({})
    },
    loading: {
      type: Boolean,
      default: false
    }
  },
  setup(props) {
    // 是否有數據
    const hasData = computed(() => {
      return props.stats && (
        props.stats.total_dividend > 0 ||
        props.stats.total_records > 0 ||
        (props.stats.by_currency && Object.keys(props.stats.by_currency).length > 0) ||
        (props.stats.by_stock && props.stats.by_stock.length > 0)
      )
    })

    // 前10名股票統計
    const topStockStats = computed(() => {
      if (!props.stats.by_stock || !Array.isArray(props.stats.by_stock)) {
        return []
      }
      return props.stats.by_stock
        .sort((a, b) => (b.net_dividend || 0) - (a.net_dividend || 0))
        .slice(0, 10)
    })

    // 最近趨勢（最近12個月）
    const recentTrend = computed(() => {
      if (!props.stats.monthly_trend || !Array.isArray(props.stats.monthly_trend)) {
        return []
      }
      return props.stats.monthly_trend
        .sort((a, b) => new Date(b.month) - new Date(a.month))
        .slice(0, 12)
        .reverse()
    })

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

    return {
      hasData,
      topStockStats,
      recentTrend,
      formatCurrency,
      getCurrencyTagType
    }
  }
}
</script>

<style scoped>
.dividend-stats {
  width: 100%;
}

.stats-cards {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 16px;
  margin-bottom: 24px;
}

.stats-card {
  border-radius: 8px;
  transition: transform 0.2s;
}

.stats-card:hover {
  transform: translateY(-2px);
}

.stats-content {
  display: flex;
  align-items: center;
  gap: 16px;
}

.stats-icon {
  width: 48px;
  height: 48px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
}

.stats-icon.total {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

.stats-icon.tax {
  background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
}

.stats-icon.net {
  background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
}

.stats-icon.count {
  background: linear-gradient(135deg, #43e97b 0%, #38f9d7 100%);
}

.stats-info {
  flex: 1;
}

.stats-value {
  font-size: 24px;
  font-weight: bold;
  color: #303133;
  margin-bottom: 4px;
}

.stats-label {
  font-size: 14px;
  color: #909399;
}

.currency-stats,
.stock-stats,
.trend-stats {
  margin-bottom: 24px;
}

.card-header {
  font-weight: 600;
  color: #303133;
}

.currency-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 16px;
}

.currency-item {
  padding: 16px;
  border: 1px solid #ebeef5;
  border-radius: 6px;
  background: #fafafa;
}

.currency-header {
  margin-bottom: 12px;
}

.currency-details {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.detail-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.detail-label {
  font-size: 14px;
  color: #606266;
}

.detail-value {
  font-weight: 500;
  font-family: 'Monaco', 'Menlo', monospace;
}

.detail-value.positive {
  color: #67c23a;
}

.detail-value.negative {
  color: #f56c6c;
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

.trend-chart {
  min-height: 200px;
}

.trend-list {
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
}

.trend-item {
  flex: 1;
  min-width: 120px;
  padding: 12px;
  border: 1px solid #ebeef5;
  border-radius: 6px;
  text-align: center;
  background: #fafafa;
}

.trend-month {
  font-size: 12px;
  color: #909399;
  margin-bottom: 4px;
}

.trend-amount {
  font-size: 16px;
  font-weight: bold;
  margin-bottom: 4px;
}

.trend-count {
  font-size: 12px;
  color: #606266;
}

.empty-state {
  margin-top: 40px;
  text-align: center;
}

/* 響應式設計 */
@media (max-width: 768px) {
  .stats-cards {
    grid-template-columns: repeat(2, 1fr);
    gap: 12px;
  }
  
  .stats-value {
    font-size: 20px;
  }
  
  .currency-grid {
    grid-template-columns: 1fr;
  }
  
  .trend-list {
    flex-direction: column;
  }
  
  .trend-item {
    min-width: auto;
  }
}

@media (max-width: 480px) {
  .stats-cards {
    grid-template-columns: 1fr;
  }
  
  .stats-content {
    gap: 12px;
  }
  
  .stats-icon {
    width: 40px;
    height: 40px;
  }
  
  .stats-value {
    font-size: 18px;
  }
}
</style>