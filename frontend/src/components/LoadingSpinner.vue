<template>
  <div class="loading-container" :class="containerClass">
    <div class="loading-spinner" :class="spinnerClass">
      <div class="spinner-ring"></div>
    </div>
    <p v-if="text" class="loading-text" :class="textClass">
      {{ text }}
    </p>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  // 加載文字
  text: {
    type: String,
    default: '加載中...'
  },
  // 尺寸：small, medium, large
  size: {
    type: String,
    default: 'medium',
    validator: (value) => ['small', 'medium', 'large'].includes(value)
  },
  // 是否全屏顯示
  fullscreen: {
    type: Boolean,
    default: false
  },
  // 是否顯示背景遮罩
  overlay: {
    type: Boolean,
    default: false
  },
  // 自定義顏色
  color: {
    type: String,
    default: 'primary'
  }
})

// 容器樣式類
const containerClass = computed(() => {
  const classes = ['flex', 'flex-col', 'items-center', 'justify-center']
  
  if (props.fullscreen) {
    classes.push('fixed', 'inset-0', 'z-50')
  }
  
  if (props.overlay) {
    classes.push('bg-white', 'bg-opacity-80')
  }
  
  return classes
})

// 加載器樣式類
const spinnerClass = computed(() => {
  const sizeClasses = {
    small: 'w-6 h-6',
    medium: 'w-8 h-8',
    large: 'w-12 h-12'
  }
  
  const colorClasses = {
    primary: 'border-primary-600',
    success: 'border-success-600',
    danger: 'border-danger-600',
    gray: 'border-gray-600'
  }
  
  return [
    sizeClasses[props.size],
    colorClasses[props.color] || colorClasses.primary
  ]
})

// 文字樣式類
const textClass = computed(() => {
  const sizeClasses = {
    small: 'text-sm',
    medium: 'text-base',
    large: 'text-lg'
  }
  
  return [
    sizeClasses[props.size],
    'text-gray-600',
    'mt-2'
  ]
})
</script>

<style scoped>
.loading-spinner {
  @apply animate-spin rounded-full border-2 border-transparent;
}

.spinner-ring {
  @apply w-full h-full rounded-full border-2 border-current border-t-transparent;
}

.loading-text {
  @apply font-medium;
}

/* 動畫效果 */
@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}

.loading-spinner {
  animation: spin 1s linear infinite;
}
</style>