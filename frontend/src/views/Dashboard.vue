<template>
  <div class="dashboard">
    <!-- 概覽卡片 -->
    <el-row :gutter="20" class="overview-cards">
      <el-col :xs="24" :sm="12" :md="6">
        <el-card class="overview-card">
          <div class="card-content">
            <div class="card-icon market-value">
              <el-icon><TrendCharts /></el-icon>
            </div>
            <div class="card-info">
              <div class="card-title">總市值</div>
              <div class="card-value">{{ formatCurrency(stockStore.totalMarketValue) }}</div>
            </div>
          </div>
        </el-card>
      </el-col>
      
      <el-col :xs="24" :sm="12" :md="6">
        <el-card class="overview-card">
          <div class="card-content">
            <div class="card-icon profit-loss" :class="{ 'negative': stockStore.totalProfitLoss < 0 }">
              <el-icon><TrendCharts /></el-icon>
            </div>
            <div class="card-info">
              <div class="card-title">總盈虧</div>
              <div class="card-value" :class="{ 'negative': stockStore.totalProfitLoss < 0 }">
                {{ formatCurrency(stockStore.totalProfitLoss) }}
              </div>
            </div>
          </div>
        </el-card>
      </el-col>
      
      <el-col :xs="24" :sm="12" :md="6">
        <el-card class="overview-card">
          <div class="card-content">
            <div class="card-icon profit-rate" :class="{ 'negative': stockStore.totalProfitLossRate < 0 }">
              <el-icon><DataAnalysis /></el-icon>
            </div>
            <div class="card-info">
              <div class="card-title">總收益率</div>
              <div class="card-value" :class="{ 'negative': stockStore.totalProfitLossRate < 0 }">
                {{ stockStore.totalProfitLossRate.toFixed(2) }}%
              </div>
            </div>
          </div>
        </el-card>
      </el-col>
      
      <el-col :xs="24" :sm="12" :md="6">
        <el-card class="overview-card">
          <div class="card-content">
            <div class="card-icon stock-count">
              <el-icon><Grid /></el-icon>
            </div>
            <div class="card-info">
              <div class="card-title">持倉股票</div>
              <div class="card-value">{{ stockStore.stocks.length }} 支</div>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 股票持倉列表 -->
    <el-card class="stock-list-card">
      <template #header>
        <div class="card-header">
          <span>股票持倉</span>
          <el-button type="primary" @click="refreshData">
            <el-icon><Refresh /></el-icon>
            刷新數據
          </el-button>
        </div>
      </template>
      
      <el-table 
        v-loading="stockStore.loading"
        :data="stockStore.stocks"
        stripe
        style="width: 100%"
      >
        <el-table-column prop="stock_code" label="股票代碼" width="120" />
        <el-table-column prop="stock_name" label="股票名稱" width="150" />
        <el-table-column prop="market" label="市場" width="80" />
        <el-table-column prop="current_price" label="當前價格" width="100">
          <template #default="{ row }">
            {{ formatCurrency(row.current_price) }}
          </template>
        </el-table-column>
        <el-table-column prop="total_shares" label="持股數量" width="100">
          <template #default="{ row }">
            {{ formatNumber(row.total_shares) }}
          </template>
        </el-table-column>
        <el-table-column prop="avg_cost" label="平均成本" width="100">
          <template #default="{ row }">
            {{ formatCurrency(row.avg_cost) }}
          </template>
        </el-table-column>
        <el-table-column prop="market_value" label="市值" width="120">
          <template #default="{ row }">
            {{ formatCurrency(row.market_value) }}
          </template>
        </el-table-column>
        <el-table-column prop="profit_loss" label="盈虧" width="120">
          <template #default="{ row }">
            <span :class="{ 'negative': row.profit_loss < 0 }">
              {{ formatCurrency(row.profit_loss) }}
            </span>
          </template>
        </el-table-column>
        <el-table-column prop="profit_loss_rate" label="收益率" width="100">
          <template #default="{ row }">
            <span :class="{ 'negative': row.profit_loss_rate < 0 }">
              {{ row.profit_loss_rate.toFixed(2) }}%
            </span>
          </template>
        </el-table-column>
        <el-table-column prop="price_update_time" label="更新時間" width="160">
          <template #default="{ row }">
            {{ formatDateTime(row.price_update_time) }}
          </template>
        </el-table-column>
      </el-table>
    </el-card>
  </div>
</template>

<script>
import { onMounted } from 'vue'
import { useStockStore } from '../stores'
import { TrendCharts, DataAnalysis, Grid, Refresh } from '@element-plus/icons-vue'

export default {
  name: 'Dashboard',
  components: {
    TrendCharts,
    DataAnalysis,
    Grid,
    Refresh
  },
  setup() {
    const stockStore = useStockStore()

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

    // 格式化日期時間
    const formatDateTime = (value) => {
      if (!value) return '-'
      return new Date(value).toLocaleString('zh-CN')
    }

    // 刷新數據
    const refreshData = async () => {
      await stockStore.fetchStocks()
    }

    // 組件掛載時獲取數據
    onMounted(() => {
      stockStore.fetchStocks()
    })

    return {
      stockStore,
      formatCurrency,
      formatNumber,
      formatDateTime,
      refreshData
    }
  }
}
</script>

<style scoped>
.dashboard {
  padding: 20px;
}

.overview-cards {
  margin-bottom: 20px;
}

.overview-card {
  height: 120px;
}

.card-content {
  display: flex;
  align-items: center;
  height: 100%;
}

.card-icon {
  width: 60px;
  height: 60px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-right: 15px;
  font-size: 24px;
  color: white;
}

.card-icon.market-value {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

.card-icon.profit-loss {
  background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
}

.card-icon.profit-loss.negative {
  background: linear-gradient(135deg, #ff9a9e 0%, #fecfef 100%);
}

.card-icon.profit-rate {
  background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
}

.card-icon.profit-rate.negative {
  background: linear-gradient(135deg, #ffecd2 0%, #fcb69f 100%);
}

.card-icon.stock-count {
  background: linear-gradient(135deg, #a8edea 0%, #fed6e3 100%);
  color: #333;
}

.card-info {
  flex: 1;
}

.card-title {
  font-size: 14px;
  color: #909399;
  margin-bottom: 5px;
}

.card-value {
  font-size: 24px;
  font-weight: 600;
  color: #303133;
}

.card-value.negative {
  color: #f56c6c;
}

.stock-list-card {
  margin-top: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.negative {
  color: #f56c6c;
}

/* 響應式設計 */
@media (max-width: 768px) {
  .dashboard {
    padding: 10px;
  }
  
  .overview-card {
    margin-bottom: 10px;
  }
  
  .card-content {
    flex-direction: column;
    text-align: center;
  }
  
  .card-icon {
    margin-right: 0;
    margin-bottom: 10px;
  }
}
</style>