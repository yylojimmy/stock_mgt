<template>
  <div id="app" :class="`theme-${currentTheme}`">
    <MainLayout>
      <router-view />
    </MainLayout>
  </div>
</template>

<script>
import MainLayout from './layouts/MainLayout.vue'
import { useTheme } from './utils/theme.js'

export default {
  name: 'App',
  components: {
    MainLayout
  },
  setup() {
    const { currentTheme } = useTheme()
    
    return {
      currentTheme
    }
  }
}
</script>

<style>
#app {
  font-family: 'Helvetica Neue', Helvetica, 'PingFang SC', 'Hiragino Sans GB', 'Microsoft YaHei', '微軟雅黑', Arial, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  min-height: 100vh;
  overflow: auto;
}

/* 全局主題變量 */
:root {
  --transition-duration: 0.3s;
  --border-radius: 8px;
  --header-height: 60px;
  --footer-height: 60px;
}

/* 響應式斷點 */
@media (max-width: 768px) {
  :root {
    --header-height: 56px;
    --footer-height: 56px;
  }
}

/* 主題切換動畫 */
.theme-light,
.theme-dark {
  transition: background-color var(--transition-duration) ease,
              color var(--transition-duration) ease;
}

/* 滾動條樣式 */
::-webkit-scrollbar {
  width: 6px;
  height: 6px;
}

::-webkit-scrollbar-track {
  background: var(--color-border-lighter);
  border-radius: 3px;
}

::-webkit-scrollbar-thumb {
  background: var(--color-border-base);
  border-radius: 3px;
}

::-webkit-scrollbar-thumb:hover {
  background: var(--color-text-secondary);
}

/* 移動端優化 */
@media (max-width: 768px) {
  #app {
    font-size: 14px;
  }
  
  ::-webkit-scrollbar {
    width: 4px;
    height: 4px;
  }
}
</style>