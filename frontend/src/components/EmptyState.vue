<template>
  <div class="empty-state" :class="containerClass">
    <!-- 圖標區域 -->
    <div class="empty-icon" :class="iconClass">
      <el-icon v-if="icon" :size="iconSize">
        <component :is="icon" />
      </el-icon>
      <div v-else class="default-icon">
        <el-icon :size="iconSize">
          <Box />
        </el-icon>
      </div>
    </div>
    
    <!-- 標題 -->
    <h3 class="empty-title" :class="titleClass">
      {{ title || '暫無數據' }}
    </h3>
    
    <!-- 描述 -->
    <p v-if="description" class="empty-description" :class="descriptionClass">
      {{ description }}
    </p>
    
    <!-- 操作按鈕 -->
    <div v-if="$slots.action || actionText" class="empty-action">
      <slot name="action">
        <el-button
          v-if="actionText"
          :type="actionType"
          :size="actionSize"
          @click="handleAction"
        >
          <el-icon v-if="actionIcon" class="mr-1">
            <component :is="actionIcon" />
          </el-icon>
          {{ actionText }}
        </el-button>
      </slot>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { Box } from '@element-plus/icons-vue'

const props = defineProps({
  // 標題
  title: {
    type: String,
    default: ''
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
    default: 64
  },
  // 尺寸：small, medium, large
  size: {
    type: String,
    default: 'medium',
    validator: (value) => ['small', 'medium', 'large'].includes(value)
  },
  // 操作按鈕文字
  actionText: {
    type: String,
    default: ''
  },
  // 操作按鈕類型
  actionType: {
    type: String,
    default: 'primary'
  },
  // 操作按鈕圖標
  actionIcon: {
    type: String,
    default: ''
  },
  // 操作按鈕大小
  actionSize: {
    type: String,
    default: 'default'
  },
  // 是否垂直居中
  centered: {
    type: Boolean,
    default: true
  }
})

const emit = defineEmits(['action'])

// 容器樣式類
const containerClass = computed(() => {
  const classes = ['flex', 'flex-col', 'items-center', 'text-center']
  
  if (props.centered) {
    classes.push('justify-center', 'min-h-64')
  }
  
  const sizeClasses = {
    small: 'p-4',
    medium: 'p-8',
    large: 'p-12'
  }
  
  classes.push(sizeClasses[props.size])
  
  return classes
})

// 圖標樣式類
const iconClass = computed(() => {
  return [
    'text-gray-400',
    'mb-4'
  ]
})

// 標題樣式類
const titleClass = computed(() => {
  const sizeClasses = {
    small: 'text-lg',
    medium: 'text-xl',
    large: 'text-2xl'
  }
  
  return [
    sizeClasses[props.size],
    'font-semibold',
    'text-gray-900',
    'mb-2'
  ]
})

// 描述樣式類
const descriptionClass = computed(() => {
  const sizeClasses = {
    small: 'text-sm',
    medium: 'text-base',
    large: 'text-lg'
  }
  
  return [
    sizeClasses[props.size],
    'text-gray-500',
    'mb-6',
    'max-w-md'
  ]
})

// 處理操作按鈕點擊
const handleAction = () => {
  emit('action')
}
</script>

<style scoped>
.empty-state {
  @apply animate-fade-in;
}

.empty-icon {
  @apply transition-all duration-300 hover:scale-105;
}

.empty-action {
  @apply animate-slide-up;
}
</style>