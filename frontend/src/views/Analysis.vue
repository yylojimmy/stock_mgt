<template>
  <div class="analysis">
    <el-row :gutter="20">
      <!-- 投資組合分析 -->
      <el-col :span="24">
        <el-card>
          <template #header>
            <span>投資組合分析</span>
          </template>
          
          <el-row :gutter="20">
            <el-col :xs="24" :md="12">
              <div class="analysis-item">
                <h3>市場分佈</h3>
                <div class="chart-placeholder">
                  <el-empty description="圖表功能開發中" />
                </div>
              </div>
            </el-col>
            
            <el-col :xs="24" :md="12">
              <div class="analysis-item">
                <h3>收益趨勢</h3>
                <div class="chart-placeholder">
                  <el-empty description="圖表功能開發中" />
                </div>
              </div>
            </el-col>
          </el-row>
        </el-card>
      </el-col>
    </el-row>
    
    <el-row :gutter="20" style="margin-top: 20px;">
      <!-- 統計數據 -->
      <el-col :span="24">
        <el-card>
          <template #header>
            <span>統計數據</span>
          </template>
          
          <el-row :gutter="20">
            <el-col :xs="24" :sm="12" :md="6">
              <div class="stat-item">
                <div class="stat-label">總投資金額</div>
                <div class="stat-value">{{ formatCurrency(totalInvestment) }}</div>
              </div>
            </el-col>
            
            <el-col :xs="24" :sm="12" :md="6">
              <div class="stat-item">
                <div class="stat-label">當前市值</div>
                <div class="stat-value">{{ formatCurrency(stockStore.totalMarketValue) }}</div>
              </div>
            </el-col>
            
            <el-col :xs="24" :sm="12" :md="6">
              <div class="stat-item">
                <div class="stat-label">總盈虧</div>
                <div class="stat-value" :class="{ 'negative': stockStore.totalProfitLoss < 0 }">
                  {{ formatCurrency(stockStore.totalProfitLoss) }}
                </div>
              </div>
            </el-col>
            
            <el-col :xs="24" :sm="12" :md="6">
              <div class="stat-item">
                <div class="stat-label">總收益率</div>
                <div class="stat-value" :class="{ 'negative': stockStore.totalProfitLossRate < 0 }">
                  {{ stockStore.totalProfitLossRate.toFixed(2) }}%
                </div>
              </div>
            </el-col>
          </el-row>
        </el-card>
      </el-col>
    </el-row>
    
    <el-row :gutter="20" style="margin-top: 20px;">
      <!-- 持倉分析 -->
      <el-col :span="24">
        <el-card>
          <template #header>
            <span>持倉分析</span>
          </template>
          
          <el-table 
            :data="stockAnalysis"
            stripe
            style="width: 100%"
          >
            <el-table-column prop="stock_code" label="股票代碼" width="120" />
            <el-table-column prop="stock_name" label="股票名稱" width="150" />
            <el-table-column prop="market" label="市場" width="80" />
            <el-table-column prop="weight" label="權重" width="100">
              <template #default="{ row }">
                {{ row.weight.toFixed(2) }}%
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
          </el-table>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script>
import { computed, onMounted } from 'vue'
import { useStockStore } from '../stores'

export default {
  name: 'Analysis',
  setup() {
    const stockStore = useStockStore()

    // 計算總投資金額
    const totalInvestment = computed(() => {
      return stockStore.stocks.reduce((total, stock) => {
        return total + (stock.avg_cost * stock.total_shares || 0)
      }, 0)
    })

    // 持倉分析數據
    const stockAnalysis = computed(() => {
      const totalMarketValue = stockStore.totalMarketValue
      
      return stockStore.stocks.map(stock => ({
        ...stock,
        weight: totalMarketValue > 0 ? (stock.market_value / totalMarketValue) * 100 : 0
      }))
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

    // 組件掛載時獲取數據
    onMounted(() => {
      stockStore.fetchStocks()
    })

    return {
      stockStore,
      totalInvestment,
      stockAnalysis,
      formatCurrency
    }
  }
}
</script>

<style scoped>
.analysis {
  padding: 20px;
}

.analysis-item {
  text-align: center;
}

.analysis-item h3 {
  margin-bottom: 20px;
  color: #303133;
}

.chart-placeholder {
  height: 300px;
  display: flex;
  align-items: center;
  justify-content: center;
  background-color: #f5f7fa;
  border-radius: 4px;
}

.stat-item {
  text-align: center;
  padding: 20px;
  border-radius: 8px;
  background-color: #f8f9fa;
}

.stat-label {
  font-size: 14px;
  color: #909399;
  margin-bottom: 10px;
}

.stat-value {
  font-size: 24px;
  font-weight: 600;
  color: #303133;
}

.stat-value.negative {
  color: #f56c6c;
}

.negative {
  color: #f56c6c;
}

/* 響應式設計 */
@media (max-width: 768px) {
  .analysis {
    padding: 10px;
  }
  
  .stat-item {
    margin-bottom: 10px;
  }
}
</style>