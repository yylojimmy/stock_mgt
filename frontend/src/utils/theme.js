// 主題和樣式系統

/**
 * 主題配置
 */
export const themes = {
  light: {
    name: 'light',
    colors: {
      // 主色調
      primary: '#409EFF',
      primaryLight: '#79BBFF',
      primaryDark: '#337ECC',
      
      // 成功色
      success: '#67C23A',
      successLight: '#95D475',
      successDark: '#529B2E',
      
      // 警告色
      warning: '#E6A23C',
      warningLight: '#ELBF7F',
      warningDark: '#B88230',
      
      // 危險色
      danger: '#F56C6C',
      dangerLight: '#F89898',
      dangerDark: '#C45656',
      
      // 信息色
      info: '#909399',
      infoLight: '#B1B3B8',
      infoDark: '#73767A',
      
      // 文字顏色
      textPrimary: '#303133',
      textRegular: '#606266',
      textSecondary: '#909399',
      textPlaceholder: '#C0C4CC',
      
      // 邊框顏色
      borderBase: '#DCDFE6',
      borderLight: '#E4E7ED',
      borderLighter: '#EBEEF5',
      borderExtraLight: '#F2F6FC',
      
      // 背景顏色
      background: '#FFFFFF',
      backgroundPage: '#F2F3F5',
      backgroundOverlay: 'rgba(0, 0, 0, 0.8)',
      
      // 股票相關顏色
      stockUp: '#F56C6C',     // 上漲紅色
      stockDown: '#67C23A',   // 下跌綠色
      stockFlat: '#909399'    // 平盤灰色
    },
    
    shadows: {
      base: '0 2px 4px rgba(0, 0, 0, 0.12), 0 0 6px rgba(0, 0, 0, 0.04)',
      light: '0 2px 12px 0 rgba(0, 0, 0, 0.1)',
      dark: '0 4px 12px rgba(0, 0, 0, 0.15)'
    }
  },
  
  dark: {
    name: 'dark',
    colors: {
      // 主色調
      primary: '#409EFF',
      primaryLight: '#79BBFF',
      primaryDark: '#337ECC',
      
      // 成功色
      success: '#67C23A',
      successLight: '#95D475',
      successDark: '#529B2E',
      
      // 警告色
      warning: '#E6A23C',
      warningLight: '#ELBF7F',
      warningDark: '#B88230',
      
      // 危險色
      danger: '#F56C6C',
      dangerLight: '#F89898',
      dangerDark: '#C45656',
      
      // 信息色
      info: '#909399',
      infoLight: '#B1B3B8',
      infoDark: '#73767A',
      
      // 文字顏色
      textPrimary: '#E5EAF3',
      textRegular: '#CFD3DC',
      textSecondary: '#A3A6AD',
      textPlaceholder: '#8D9095',
      
      // 邊框顏色
      borderBase: '#4C4D4F',
      borderLight: '#414243',
      borderLighter: '#363637',
      borderExtraLight: '#2B2B2C',
      
      // 背景顏色
      background: '#1D1E1F',
      backgroundPage: '#0A0A0A',
      backgroundOverlay: 'rgba(0, 0, 0, 0.8)',
      
      // 股票相關顏色
      stockUp: '#F56C6C',     // 上漲紅色
      stockDown: '#67C23A',   // 下跌綠色
      stockFlat: '#909399'    // 平盤灰色
    },
    
    shadows: {
      base: '0 2px 4px rgba(0, 0, 0, 0.12), 0 0 6px rgba(0, 0, 0, 0.04)',
      light: '0 2px 12px 0 rgba(0, 0, 0, 0.1)',
      dark: '0 4px 12px rgba(0, 0, 0, 0.15)'
    }
  }
}

/**
 * 主題管理器
 */
class ThemeManager {
  constructor() {
    this.currentTheme = 'light'
    this.listeners = []
    this.init()
  }
  
  init() {
    // 從本地存儲讀取主題設置
    const savedTheme = localStorage.getItem('theme')
    if (savedTheme && themes[savedTheme]) {
      this.currentTheme = savedTheme
    } else {
      // 檢測系統主題偏好
      const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches
      this.currentTheme = prefersDark ? 'dark' : 'light'
    }
    
    // 監聽系統主題變化
    window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', (e) => {
      if (!localStorage.getItem('theme')) {
        this.setTheme(e.matches ? 'dark' : 'light')
      }
    })
    
    this.applyTheme()
  }
  
  /**
   * 設置主題
   * @param {string} themeName 主題名稱
   */
  setTheme(themeName) {
    if (!themes[themeName]) {
      console.warn(`主題 "${themeName}" 不存在`)
      return
    }
    
    this.currentTheme = themeName
    localStorage.setItem('theme', themeName)
    this.applyTheme()
    this.notifyListeners()
  }
  
  /**
   * 獲取當前主題
   */
  getCurrentTheme() {
    return this.currentTheme
  }
  
  /**
   * 獲取主題配置
   * @param {string} themeName 主題名稱，默認為當前主題
   */
  getTheme(themeName = this.currentTheme) {
    return themes[themeName]
  }
  
  /**
   * 切換主題
   */
  toggleTheme() {
    const newTheme = this.currentTheme === 'light' ? 'dark' : 'light'
    this.setTheme(newTheme)
  }
  
  /**
   * 應用主題到DOM
   */
  applyTheme() {
    const theme = this.getTheme()
    const root = document.documentElement
    
    // 設置CSS變量
    Object.entries(theme.colors).forEach(([key, value]) => {
      root.style.setProperty(`--color-${this.kebabCase(key)}`, value)
    })
    
    Object.entries(theme.shadows).forEach(([key, value]) => {
      root.style.setProperty(`--shadow-${key}`, value)
    })
    
    // 設置主題類名
    root.className = root.className.replace(/theme-\w+/g, '')
    root.classList.add(`theme-${this.currentTheme}`)
    
    // 設置meta標籤（移動端狀態欄）
    this.updateMetaTheme(theme)
  }
  
  /**
   * 更新移動端meta標籤
   */
  updateMetaTheme(theme) {
    // 更新狀態欄顏色
    let metaTheme = document.querySelector('meta[name="theme-color"]')
    if (!metaTheme) {
      metaTheme = document.createElement('meta')
      metaTheme.name = 'theme-color'
      document.head.appendChild(metaTheme)
    }
    metaTheme.content = theme.colors.primary
    
    // 更新狀態欄樣式
    let metaStatus = document.querySelector('meta[name="apple-mobile-web-app-status-bar-style"]')
    if (!metaStatus) {
      metaStatus = document.createElement('meta')
      metaStatus.name = 'apple-mobile-web-app-status-bar-style'
      document.head.appendChild(metaStatus)
    }
    metaStatus.content = this.currentTheme === 'dark' ? 'black-translucent' : 'default'
  }
  
  /**
   * 添加主題變化監聽器
   * @param {Function} listener 監聽器函數
   */
  addListener(listener) {
    this.listeners.push(listener)
  }
  
  /**
   * 移除主題變化監聽器
   * @param {Function} listener 監聽器函數
   */
  removeListener(listener) {
    const index = this.listeners.indexOf(listener)
    if (index > -1) {
      this.listeners.splice(index, 1)
    }
  }
  
  /**
   * 通知所有監聽器
   */
  notifyListeners() {
    this.listeners.forEach(listener => {
      try {
        listener(this.currentTheme, this.getTheme())
      } catch (error) {
        console.error('主題監聽器執行錯誤:', error)
      }
    })
  }
  
  /**
   * 將駝峰命名轉換為短橫線命名
   */
  kebabCase(str) {
    return str.replace(/([a-z0-9]|(?=[A-Z]))([A-Z])/g, '$1-$2').toLowerCase()
  }
}

// 創建全局主題管理器實例
export const themeManager = new ThemeManager()

/**
 * 樣式工具函數
 */
export const styleUtils = {
  /**
   * 獲取CSS變量值
   * @param {string} name 變量名
   * @param {Element} element 元素，默認為根元素
   */
  getCSSVar(name, element = document.documentElement) {
    return getComputedStyle(element).getPropertyValue(name).trim()
  },
  
  /**
   * 設置CSS變量值
   * @param {string} name 變量名
   * @param {string} value 變量值
   * @param {Element} element 元素，默認為根元素
   */
  setCSSVar(name, value, element = document.documentElement) {
    element.style.setProperty(name, value)
  },
  
  /**
   * 生成漸變背景
   * @param {string} startColor 起始顏色
   * @param {string} endColor 結束顏色
   * @param {string} direction 方向，默認為'to right'
   */
  createGradient(startColor, endColor, direction = 'to right') {
    return `linear-gradient(${direction}, ${startColor}, ${endColor})`
  },
  
  /**
   * 生成陰影樣式
   * @param {number} x X偏移
   * @param {number} y Y偏移
   * @param {number} blur 模糊半徑
   * @param {string} color 陰影顏色
   * @param {number} spread 擴散半徑
   */
  createShadow(x = 0, y = 2, blur = 4, color = 'rgba(0, 0, 0, 0.12)', spread = 0) {
    return `${x}px ${y}px ${blur}px ${spread}px ${color}`
  },
  
  /**
   * 轉換顏色透明度
   * @param {string} color 顏色值
   * @param {number} alpha 透明度 (0-1)
   */
  colorWithAlpha(color, alpha) {
    // 簡單的十六進制顏色處理
    if (color.startsWith('#')) {
      const hex = color.slice(1)
      const r = parseInt(hex.slice(0, 2), 16)
      const g = parseInt(hex.slice(2, 4), 16)
      const b = parseInt(hex.slice(4, 6), 16)
      return `rgba(${r}, ${g}, ${b}, ${alpha})`
    }
    return color
  },
  
  /**
   * 響應式字體大小
   * @param {number} baseSize 基礎字體大小
   * @param {number} minSize 最小字體大小
   * @param {number} maxSize 最大字體大小
   */
  responsiveFontSize(baseSize, minSize = baseSize * 0.8, maxSize = baseSize * 1.2) {
    return `clamp(${minSize}px, ${baseSize}px + 1vw, ${maxSize}px)`
  }
}

/**
 * Vue 3 組合式API主題鉤子
 */
export function useTheme() {
  const currentTheme = ref(themeManager.getCurrentTheme())
  const theme = computed(() => themeManager.getTheme(currentTheme.value))
  
  const setTheme = (themeName) => {
    themeManager.setTheme(themeName)
  }
  
  const toggleTheme = () => {
    themeManager.toggleTheme()
  }
  
  // 監聽主題變化
  const handleThemeChange = (newTheme) => {
    currentTheme.value = newTheme
  }
  
  onMounted(() => {
    themeManager.addListener(handleThemeChange)
  })
  
  onUnmounted(() => {
    themeManager.removeListener(handleThemeChange)
  })
  
  return {
    currentTheme: readonly(currentTheme),
    theme: readonly(theme),
    setTheme,
    toggleTheme
  }
}

// 導入Vue相關API（需要在使用時確保已安裝Vue）
let ref, computed, readonly, onMounted, onUnmounted
try {
  const vue = await import('vue')
  ref = vue.ref
  computed = vue.computed
  readonly = vue.readonly
  onMounted = vue.onMounted
  onUnmounted = vue.onUnmounted
} catch (error) {
  // Vue未安裝或不可用時的處理
  console.warn('Vue未安裝，useTheme鉤子不可用')
}

export default themeManager