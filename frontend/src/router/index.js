import { createRouter, createWebHistory } from 'vue-router'
import Dashboard from '../views/Dashboard.vue'
import StockList from '../views/StockList.vue'
import TransactionsView from '../views/TransactionsView.vue'
import DividendList from '../views/DividendList.vue'
import Analysis from '../views/Analysis.vue'

// 路由配置
const routes = [
  {
    path: '/',
    name: 'Dashboard',
    component: Dashboard,
    meta: {
      title: '持倉概覽'
    }
  },
  {
    path: '/stocks',
    name: 'StockList',
    component: StockList,
    meta: {
      title: '股票管理'
    }
  },
  {
    path: '/transactions',
    name: 'TransactionsView',
    component: TransactionsView,
    meta: {
      title: '交易記錄'
    }
  },
  {
    path: '/dividends',
    name: 'DividendList',
    component: DividendList,
    meta: {
      title: '股息記錄'
    }
  },
  {
    path: '/analysis',
    name: 'Analysis',
    component: Analysis,
    meta: {
      title: '投資分析'
    }
  },
  {
    path: '/:pathMatch(.*)*',
    redirect: '/'
  }
]

// 創建路由實例
const router = createRouter({
  history: createWebHistory(),
  routes
})

// 路由守衛 - 設置頁面標題
router.beforeEach((to, from, next) => {
  if (to.meta.title) {
    document.title = `${to.meta.title} - 股票管理系統`
  }
  next()
})

export default router