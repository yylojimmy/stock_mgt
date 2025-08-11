<template>
  <div class="main-layout">
    <!-- 桌面端佈局 -->
    <div class="desktop-layout desktop-hidden md:block">
      <!-- 頂部導航欄 -->
      <header class="header">
        <div class="container-responsive">
          <div class="flex items-center justify-between h-16">
            <!-- Logo 和標題 -->
            <div class="flex items-center space-x-4">
              <div class="flex items-center space-x-2">
                <el-icon class="text-2xl text-primary-600">
                  <TrendCharts />
                </el-icon>
                <h1 class="text-xl font-bold text-gray-900">股票管理系統</h1>
              </div>
            </div>
            
            <!-- 桌面端導航菜單 -->
            <nav class="hidden md:flex space-x-8">
              <router-link
                v-for="item in navItems"
                :key="item.path"
                :to="item.path"
                class="nav-link"
                :class="{ 'nav-link-active': $route.path === item.path }"
              >
                <el-icon class="mr-2">
                  <component :is="item.icon" />
                </el-icon>
                {{ item.name }}
              </router-link>
            </nav>
            
            <!-- 用戶操作區域 -->
            <div class="flex items-center space-x-4">
              <el-button type="primary" size="small" @click="refreshData">
                <el-icon class="mr-1">
                  <Refresh />
                </el-icon>
                刷新
              </el-button>
            </div>
          </div>
        </div>
      </header>
      
      <!-- 主要內容區域 -->
      <main class="main-content">
        <div class="container-responsive py-6">
          <router-view />
        </div>
      </main>
    </div>
    
    <!-- 移動端佈局 -->
    <div class="mobile-layout md:hidden">
      <!-- 移動端頂部欄 -->
      <header class="mobile-header">
        <div class="flex items-center justify-between px-4 h-14">
          <h1 class="text-lg font-semibold text-gray-900">{{ currentPageTitle }}</h1>
          <el-button type="primary" size="small" @click="refreshData">
            <el-icon>
              <Refresh />
            </el-icon>
          </el-button>
        </div>
      </header>
      
      <!-- 移動端主要內容 -->
      <main class="mobile-content">
        <div class="px-4 py-4 pb-20">
          <router-view />
        </div>
      </main>
      
      <!-- 移動端底部導航 -->
      <nav class="mobile-nav">
        <router-link
          v-for="item in navItems"
          :key="item.path"
          :to="item.path"
          class="mobile-nav-item"
          :class="{ 'active': $route.path === item.path }"
        >
          <el-icon class="text-xl mb-1">
            <component :is="item.icon" />
          </el-icon>
          <span>{{ item.shortName || item.name }}</span>
        </router-link>
      </nav>
    </div>
  </div>
</template>

<script setup>
import { computed, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { ElMessage } from 'element-plus'
import { useStockStore, useTransactionStore, useDividendStore } from '../stores'
import {
  TrendCharts,
  Refresh,
  House,
  Coin,
  List,
  Money,
  DataAnalysis
} from '@element-plus/icons-vue'

const route = useRoute()
const stockStore = useStockStore()
const transactionStore = useTransactionStore()
const dividendStore = useDividendStore()

// 導航項目配置
const navItems = [
  {
    path: '/',
    name: '持倉概覽',
    shortName: '概覽',
    icon: 'House'
  },
  {
    path: '/stocks',
    name: '股票管理',
    shortName: '股票',
    icon: 'Coin'
  },
  {
    path: '/transactions',
    name: '交易記錄',
    shortName: '交易',
    icon: 'List'
  },
  {
    path: '/dividends',
    name: '股息記錄',
    shortName: '股息',
    icon: 'Money'
  },
  {
    path: '/analysis',
    name: '投資分析',
    shortName: '分析',
    icon: 'DataAnalysis'
  }
]

// 當前頁面標題
const currentPageTitle = computed(() => {
  const currentItem = navItems.find(item => item.path === route.path)
  return currentItem ? currentItem.name : '股票管理系統'
})

// 刷新數據
const refreshData = async () => {
  try {
    await Promise.all([
      stockStore.fetchStocks(),
      transactionStore.fetchTransactions(),
      dividendStore.fetchDividends()
    ])
    ElMessage.success('數據刷新成功')
  } catch (error) {
    ElMessage.error('數據刷新失敗')
  }
}

// 組件掛載時初始化數據
onMounted(() => {
  refreshData()
})
</script>

<style scoped>
.main-layout {
  min-height: 100vh;
  background-color: #f5f7fa;
}

/* 桌面端樣式 */
.header {
  @apply bg-white shadow-sm border-b border-gray-200;
}

.nav-link {
  @apply flex items-center px-3 py-2 text-sm font-medium text-gray-600 hover:text-primary-600 transition-colors duration-200 rounded-md;
}

.nav-link-active {
  @apply text-primary-600 bg-primary-50;
}

.main-content {
  min-height: calc(100vh - 4rem);
}

/* 移動端樣式 */
.mobile-header {
  @apply bg-white shadow-sm border-b border-gray-200 sticky top-0 z-40;
}

.mobile-content {
  min-height: calc(100vh - 3.5rem - 4rem);
}

/* 響應式隱藏 */
@media (max-width: 768px) {
  .desktop-hidden {
    display: none;
  }
}

@media (min-width: 769px) {
  .mobile-layout {
    display: none;
  }
}
</style>