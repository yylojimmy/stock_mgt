<template>
  <div class="status-card" :class="cardClass">
    <!-- 圖標區域 -->
    <div v-if="icon || $slots.icon" class="status-icon" :class="iconClass">
      <slot name="icon">
        <el-icon v-if="icon" :size="iconSize">
          <component :is="icon" />
        </el-icon>
      </slot>
    </div>
    
    <!-- 內容區域 -->
    <div class="status-content">
      <!-- 標題 -->
      <div class="status-header">
        <h3 class="status-title" :class="titleClass">
          {{ title }}
        </h3>
        <div v-if="badge" class="status-badge" :class="badgeClass">
          {{ badge }}
        </div>
      </div>
      
      <!-- 主要數值 -->
      <div class="status-value" :class="valueClass">
        <span class="value-text">
          {{ formattedValue }}
        </span>
        <span v-if="unit" class="value-unit">
          {{ unit }}
        </span>
      </div>
      
      <!-- 變化指示器 -->
      <div v-if="change !== null && change !== undefined" class="status-change" :class="changeClass">
        <el-icon class="change-icon">
          <component :is="changeIcon" />
        </el-icon>
        <span class="change-text">
          {{ formattedChange }}
        </span>
        <span v-if="changePercent !== null && changePercent !== undefined" class="change-percent">
          ({{ formattedChangePercent }})
        </span>
      </div>
      
      <!-- 描述 -->
      <p v-if="description" class="status-description">
        {{ description }}
      </p>
    </div>
    
    <!-- 操作區域 -->
    <div v-if="$slots.action" class="status-action">
      <slot name="action"></slot>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { ArrowUp, ArrowDown, Minus } from '@element-plus/icons-vue'

const props = defineProps({
  // 標題
  title: {
    type: String,
    required: true
  },
  // 主要數值
  value: {
    type: [Number, String],
    required: true
  },
  // 數值單位
  unit: {
    type: String,
    default: ''
  },
  // 變化值
  change: {
    type: Number,
    default: null
  },
  // 變化百分比
  changePercent: {
    type: Number,
    default: null
  },
  // 描述
  description: {
    type: String,
    default: ''
  },
  // 圖標
  icon: {
    type: String,
    default: ''
  },
  // 圖標大小
  iconSize: {
    type: Number,
    default: 24
  },
  // 徽章
  badge: {
    type: String,
    default: ''
  },
  // 狀態類型：positive, negative, neutral
  status: {
    type: String,
    default: 'neutral',
    validator: (value) => ['positive', 'negative', 'neutral'].includes(value)
  },
  // 尺寸：small, medium, large
  size: {
    type: String,
    default: 'medium',
    validator: (value) => ['small', 'medium', 'large'].includes(value)
  },
  // 是否可點擊
  clickable: {
    type: Boolean,
    default: false
  },
  // 數值格式化選項
  formatOptions: {
    type: Object,
    default: () => ({})
  }
})

const emit = defineEmits(['click'])

// 卡片樣式類
const cardClass = computed(() => {
  const classes = ['card', 'relative']
  
  if (props.clickable) {
    classes.push('card-hover', 'cursor-pointer')
  }
  
  const sizeClasses = {
    small: 'p-4',
    medium: 'p-6',
    large: 'p-8'
  }
  
  classes.push(sizeClasses[props.size])
  
  return classes
})

// 圖標樣式類
const iconClass = computed(() => {
  const statusClasses = {
    positive: 'text-success-600',
    negative: 'text-danger-600',
    neutral: 'text-gray-600'
  }
  
  return [
    statusClasses[props.status],
    'mb-2'
  ]
})

// 標題樣式類
const titleClass = computed(() => {
  const sizeClasses = {
    small: 'text-sm',
    medium: 'text-base',
    large: 'text-lg'
  }
  
  return [
    sizeClasses[props.size],
    'font-medium',
    'text-gray-600'
  ]
})

// 徽章樣式類
const badgeClass = computed(() => {
  const statusClasses = {
    positive: 'status-positive',
    negative: 'status-negative',
    neutral: 'status-neutral'
  }
  
  return statusClasses[props.status]
})

// 數值樣式類
const valueClass = computed(() => {
  const sizeClasses = {
    small: 'text-xl',
    medium: 'text-2xl',
    large: 'text-3xl'
  }
  
  return [
    sizeClasses[props.size],
    'font-bold',
    'text-gray-900',
    'mb-2'
  ]
})

// 變化樣式類
const changeClass = computed(() => {
  if (props.change === null || props.change === undefined) return []
  
  const statusClasses = {
    positive: 'text-success-600',
    negative: 'text-danger-600',
    neutral: 'text-gray-600'
  }
  
  const changeStatus = props.change > 0 ? 'positive' : props.change < 0 ? 'negative' : 'neutral'
  
  return [
    statusClasses[changeStatus],
    'flex',
    'items-center',
    'text-sm',
    'font-medium',
    'mb-2'
  ]
})

// 變化圖標
const changeIcon = computed(() => {
  if (props.change === null || props.change === undefined) return 'Minus'
  if (props.change > 0) return 'ArrowUp'
  if (props.change < 0) return 'ArrowDown'
  return 'Minus'
})

// 格式化數值
const formattedValue = computed(() => {
  if (typeof props.value === 'string') return props.value
  
  const options = {
    minimumFractionDigits: 2,
    maximumFractionDigits: 2,
    ...props.formatOptions
  }
  
  return props.value.toLocaleString('zh-TW', options)
})

// 格式化變化值
const formattedChange = computed(() => {
  if (props.change === null || props.change === undefined) return ''
  
  const sign = props.change >= 0 ? '+' : ''
  const options = {
    minimumFractionDigits: 2,
    maximumFractionDigits: 2
  }
  
  return sign + props.change.toLocaleString('zh-TW', options)
})

// 格式化變化百分比
const formattedChangePercent = computed(() => {
  if (props.changePercent === null || props.changePercent === undefined) return ''
  
  const sign = props.changePercent >= 0 ? '+' : ''
  return sign + props.changePercent.toFixed(2) + '%'
})

// 處理點擊事件
const handleClick = () => {
  if (props.clickable) {
    emit('click')
  }
}
</script>

<style scoped>
.status-card {
  @apply transition-all duration-200;
}

.status-header {
  @apply flex items-center justify-between mb-2;
}

.status-title {
  @apply flex-1;
}

.status-badge {
  @apply text-xs;
}

.status-value {
  @apply flex items-baseline space-x-1;
}

.value-unit {
  @apply text-sm text-gray-500 font-normal;
}

.status-change {
  @apply space-x-1;
}

.change-icon {
  @apply text-xs;
}

.status-description {
  @apply text-sm text-gray-500 mt-2;
}

.status-action {
  @apply mt-4 pt-4 border-t border-gray-100;
}
</style>