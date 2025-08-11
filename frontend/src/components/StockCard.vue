<template>
  <div class="stock-card" :class="{ 'profit': profitLoss > 0, 'loss': profitLoss < 0 }">
    <div class="card-header">
      <div class="stock-info">
        <h3 class="stock-name">{{ stock.stock_name }}</h3>
        <span class="stock-code">{{ stock.stock_code }}</span>
        <span class="market-badge" :class="`market-${stock.market?.toLowerCase()}`">
          {{ getMarketName(stock.market) }}
        </span>
      </div>
      <div class="stock-actions">
        <button class="action-btn edit-btn" @click="$emit('edit', stock)" title="編輯">
          <svg class="icon" viewBox="0 0 24 24">
            <path d="M3 17.25V21h3.75L17.81 9.94l-3.75-3.75L3 17.25zM20.71 7.04c.39-.39.39-1.02 0-1.41l-2.34-2.34c-.39-.39-1.02-.39-1.41 0l-1.83 1.83 3.75 3.75 1.83-1.83z"/>
          </svg>
        </button>
        <button class="action-btn delete-btn" @click="$emit('delete', stock)" title="刪除">
          <svg class="icon" viewBox="0 0 24 24">
            <path d="M6 19c0 1.1.9 2 2 2h8c1.1 0 2-.9 2-2V7H6v12zM19 4h-3.5l-1-1h-5l-1 1H5v2h14V4z"/>
          </svg>
        </button>
      </div>
    </div>
    
    <div class="card-body">
      <div class="price-section">
        <div class="current-price">
          <span class="price-label">當前價格</span>
          <span class="price-value">{{ formatCurrency(stock.current_price) }}</span>
          <span class="price-change" :class="priceChangeClass">
            {{ formatPriceChange(stock.price_change) }}
          </span>
        </div>
        <div class="update-time" v-if="stock.price_update_time">
          更新時間: {{ formatDateTime(stock.price_update_time) }}
        </div>
      </div>
      
      <div class="holdings-section">
        <div class="holding-item">
          <span class="label">持股數量</span>
          <span class="value">{{ formatNumber(stock.total_shares) }}</span>
        </div>
        <div class="holding-item">
          <span class="label">平均成本</span>
          <span class="value">{{ formatCurrency(stock.avg_cost) }}</span>
        </div>
        <div class="holding-item">
          <span class="label">市值</span>
          <span class="value">{{ formatCurrency(marketValue) }}</span>
        </div>
      </div>
      
      <div class="profit-section">
        <div class="profit-item">
          <span class="label">盈虧金額</span>
          <span class="value" :class="profitLossClass">
            {{ formatCurrency(profitLoss) }}
          </span>
        </div>
        <div class="profit-item">
          <span class="label">盈虧比例</span>
          <span class="value" :class="profitLossClass">
            {{ formatPercentage(profitLossRate) }}
          </span>
        </div>
      </div>
    </div>
    
    <div class="card-footer" v-if="showFooter">
      <div class="position-ratio">
        <span class="label">持倉佔比</span>
        <span class="value">{{ formatPercentage(positionRatio) }}</span>
      </div>
    </div>
  </div>
</template>

<script>
import { computed } from 'vue'

export default {
  name: 'StockCard',
  props: {
    stock: {
      type: Object,
      required: true
    },
    totalPortfolioValue: {
      type: Number,
      default: 0
    },
    showFooter: {
      type: Boolean,
      default: true
    }
  },
  emits: ['edit', 'delete'],
  setup(props) {
    // 計算市值
    const marketValue = computed(() => {
      return (props.stock.current_price || 0) * (props.stock.total_shares || 0)
    })
    
    // 計算盈虧金額
    const profitLoss = computed(() => {
      const cost = (props.stock.avg_cost || 0) * (props.stock.total_shares || 0)
      return marketValue.value - cost
    })
    
    // 計算盈虧比例
    const profitLossRate = computed(() => {
      const cost = (props.stock.avg_cost || 0) * (props.stock.total_shares || 0)
      return cost > 0 ? (profitLoss.value / cost) * 100 : 0
    })
    
    // 計算持倉佔比
    const positionRatio = computed(() => {
      return props.totalPortfolioValue > 0 ? (marketValue.value / props.totalPortfolioValue) * 100 : 0
    })
    
    // 盈虧樣式類
    const profitLossClass = computed(() => {
      if (profitLoss.value > 0) return 'profit'
      if (profitLoss.value < 0) return 'loss'
      return 'neutral'
    })
    
    // 價格變化樣式類
    const priceChangeClass = computed(() => {
      const change = props.stock.price_change || 0
      if (change > 0) return 'price-up'
      if (change < 0) return 'price-down'
      return 'price-neutral'
    })
    
    // 格式化貨幣
    const formatCurrency = (value) => {
      if (value === null || value === undefined) return '¥0.00'
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
    
    // 格式化百分比
    const formatPercentage = (value) => {
      if (value === null || value === undefined) return '0.00%'
      return `${value.toFixed(2)}%`
    }
    
    // 格式化價格變化
    const formatPriceChange = (change) => {
      if (!change) return ''
      const sign = change > 0 ? '+' : ''
      return `${sign}${change.toFixed(2)}`
    }
    
    // 格式化日期時間
    const formatDateTime = (dateTime) => {
      if (!dateTime) return ''
      return new Date(dateTime).toLocaleString('zh-CN')
    }
    
    // 獲取市場名稱
    const getMarketName = (market) => {
      const marketNames = {
        'SZ': '深圳',
        'SH': '上海',
        'HK': '香港',
        'US': '美國'
      }
      return marketNames[market] || market
    }
    
    return {
      marketValue,
      profitLoss,
      profitLossRate,
      positionRatio,
      profitLossClass,
      priceChangeClass,
      formatCurrency,
      formatNumber,
      formatPercentage,
      formatPriceChange,
      formatDateTime,
      getMarketName
    }
  }
}
</script>

<style scoped>
.stock-card {
  background: var(--color-background-soft);
  border: 1px solid var(--color-border);
  border-radius: 12px;
  padding: 16px;
  margin-bottom: 16px;
  transition: all 0.3s ease;
  position: relative;
  overflow: hidden;
}

.stock-card:hover {
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  transform: translateY(-2px);
}

.stock-card.profit {
  border-left: 4px solid var(--color-success);
}

.stock-card.loss {
  border-left: 4px solid var(--color-danger);
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 16px;
}

.stock-info {
  flex: 1;
}

.stock-name {
  font-size: 18px;
  font-weight: 600;
  margin: 0 0 4px 0;
  color: var(--color-text);
}

.stock-code {
  font-size: 14px;
  color: var(--color-text-secondary);
  margin-right: 8px;
}

.market-badge {
  display: inline-block;
  padding: 2px 8px;
  border-radius: 12px;
  font-size: 12px;
  font-weight: 500;
  color: white;
}

.market-sz { background-color: #409eff; }
.market-sh { background-color: #67c23a; }
.market-hk { background-color: #e6a23c; }
.market-us { background-color: #f56c6c; }

.stock-actions {
  display: flex;
  gap: 8px;
}

.action-btn {
  width: 32px;
  height: 32px;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s ease;
}

.edit-btn {
  background-color: var(--color-primary);
  color: white;
}

.edit-btn:hover {
  background-color: var(--color-primary-dark);
}

.delete-btn {
  background-color: var(--color-danger);
  color: white;
}

.delete-btn:hover {
  background-color: var(--color-danger-dark);
}

.icon {
  width: 16px;
  height: 16px;
  fill: currentColor;
}

.card-body {
  display: grid;
  gap: 16px;
}

.price-section {
  padding: 12px;
  background: var(--color-background);
  border-radius: 8px;
}

.current-price {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 4px;
}

.price-label {
  font-size: 14px;
  color: var(--color-text-secondary);
}

.price-value {
  font-size: 20px;
  font-weight: 600;
  color: var(--color-text);
}

.price-change {
  font-size: 14px;
  font-weight: 500;
  padding: 2px 6px;
  border-radius: 4px;
}

.price-up {
  color: var(--color-success);
  background-color: var(--color-success-light);
}

.price-down {
  color: var(--color-danger);
  background-color: var(--color-danger-light);
}

.price-neutral {
  color: var(--color-text-secondary);
}

.update-time {
  font-size: 12px;
  color: var(--color-text-secondary);
}

.holdings-section,
.profit-section {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(120px, 1fr));
  gap: 12px;
}

.holding-item,
.profit-item {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.label {
  font-size: 12px;
  color: var(--color-text-secondary);
  font-weight: 500;
}

.value {
  font-size: 14px;
  font-weight: 600;
  color: var(--color-text);
}

.value.profit {
  color: var(--color-success);
}

.value.loss {
  color: var(--color-danger);
}

.value.neutral {
  color: var(--color-text-secondary);
}

.card-footer {
  margin-top: 16px;
  padding-top: 16px;
  border-top: 1px solid var(--color-border);
}

.position-ratio {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

/* 響應式設計 */
@media (max-width: 768px) {
  .stock-card {
    padding: 12px;
  }
  
  .stock-name {
    font-size: 16px;
  }
  
  .price-value {
    font-size: 18px;
  }
  
  .holdings-section,
  .profit-section {
    grid-template-columns: repeat(2, 1fr);
  }
}

@media (max-width: 480px) {
  .card-header {
    flex-direction: column;
    gap: 12px;
  }
  
  .stock-actions {
    align-self: flex-end;
  }
  
  .holdings-section,
  .profit-section {
    grid-template-columns: 1fr;
  }
}
</style>