// 移動端手勢支持工具

/**
 * 觸摸事件處理類
 */
class TouchHandler {
  constructor(element, options = {}) {
    this.element = element
    this.options = {
      threshold: 50, // 滑動閾值
      timeout: 300,  // 點擊超時
      ...options
    }
    
    this.startX = 0
    this.startY = 0
    this.startTime = 0
    this.isMoving = false
    
    this.init()
  }
  
  init() {
    this.element.addEventListener('touchstart', this.handleTouchStart.bind(this), { passive: false })
    this.element.addEventListener('touchmove', this.handleTouchMove.bind(this), { passive: false })
    this.element.addEventListener('touchend', this.handleTouchEnd.bind(this), { passive: false })
  }
  
  handleTouchStart(e) {
    const touch = e.touches[0]
    this.startX = touch.clientX
    this.startY = touch.clientY
    this.startTime = Date.now()
    this.isMoving = false
    
    this.emit('touchstart', {
      x: touch.clientX,
      y: touch.clientY,
      originalEvent: e
    })
  }
  
  handleTouchMove(e) {
    if (!this.isMoving) {
      this.isMoving = true
    }
    
    const touch = e.touches[0]
    const deltaX = touch.clientX - this.startX
    const deltaY = touch.clientY - this.startY
    
    this.emit('touchmove', {
      x: touch.clientX,
      y: touch.clientY,
      deltaX,
      deltaY,
      originalEvent: e
    })
  }
  
  handleTouchEnd(e) {
    const touch = e.changedTouches[0]
    const deltaX = touch.clientX - this.startX
    const deltaY = touch.clientY - this.startY
    const deltaTime = Date.now() - this.startTime
    
    // 判斷是否為點擊
    if (!this.isMoving && deltaTime < this.options.timeout) {
      this.emit('tap', {
        x: touch.clientX,
        y: touch.clientY,
        originalEvent: e
      })
    }
    
    // 判斷滑動方向
    if (Math.abs(deltaX) > this.options.threshold || Math.abs(deltaY) > this.options.threshold) {
      let direction = ''
      
      if (Math.abs(deltaX) > Math.abs(deltaY)) {
        direction = deltaX > 0 ? 'right' : 'left'
      } else {
        direction = deltaY > 0 ? 'down' : 'up'
      }
      
      this.emit('swipe', {
        direction,
        deltaX,
        deltaY,
        distance: Math.sqrt(deltaX * deltaX + deltaY * deltaY),
        originalEvent: e
      })
      
      // 觸發具體方向的事件
      this.emit(`swipe${direction}`, {
        deltaX,
        deltaY,
        distance: Math.sqrt(deltaX * deltaX + deltaY * deltaY),
        originalEvent: e
      })
    }
    
    this.emit('touchend', {
      x: touch.clientX,
      y: touch.clientY,
      deltaX,
      deltaY,
      deltaTime,
      originalEvent: e
    })
  }
  
  emit(eventName, data) {
    const event = new CustomEvent(eventName, { detail: data })
    this.element.dispatchEvent(event)
  }
  
  destroy() {
    this.element.removeEventListener('touchstart', this.handleTouchStart)
    this.element.removeEventListener('touchmove', this.handleTouchMove)
    this.element.removeEventListener('touchend', this.handleTouchEnd)
  }
}

/**
 * 下拉刷新組件
 */
export class PullToRefresh {
  constructor(element, callback, options = {}) {
    this.element = element
    this.callback = callback
    this.options = {
      threshold: 60,     // 觸發閾值
      maxDistance: 100,  // 最大拉動距離
      resistance: 2.5,   // 阻力係數
      ...options
    }
    
    this.isRefreshing = false
    this.startY = 0
    this.currentY = 0
    this.distance = 0
    
    this.init()
  }
  
  init() {
    this.element.addEventListener('touchstart', this.handleTouchStart.bind(this))
    this.element.addEventListener('touchmove', this.handleTouchMove.bind(this))
    this.element.addEventListener('touchend', this.handleTouchEnd.bind(this))
  }
  
  handleTouchStart(e) {
    if (this.isRefreshing || this.element.scrollTop > 0) return
    
    this.startY = e.touches[0].clientY
  }
  
  handleTouchMove(e) {
    if (this.isRefreshing || this.element.scrollTop > 0) return
    
    this.currentY = e.touches[0].clientY
    this.distance = (this.currentY - this.startY) / this.options.resistance
    
    if (this.distance > 0) {
      e.preventDefault()
      
      // 限制最大距離
      this.distance = Math.min(this.distance, this.options.maxDistance)
      
      // 更新UI
      this.updateUI()
    }
  }
  
  handleTouchEnd(e) {
    if (this.isRefreshing || this.distance <= 0) return
    
    if (this.distance >= this.options.threshold) {
      this.triggerRefresh()
    } else {
      this.resetUI()
    }
  }
  
  updateUI() {
    const progress = Math.min(this.distance / this.options.threshold, 1)
    
    this.element.style.transform = `translateY(${this.distance}px)`
    
    // 觸發自定義事件
    this.element.dispatchEvent(new CustomEvent('pullprogress', {
      detail: { distance: this.distance, progress }
    }))
  }
  
  triggerRefresh() {
    this.isRefreshing = true
    this.element.style.transform = `translateY(${this.options.threshold}px)`
    
    // 觸發刷新事件
    this.element.dispatchEvent(new CustomEvent('pullrefresh'))
    
    // 執行回調
    if (this.callback) {
      Promise.resolve(this.callback()).finally(() => {
        this.finishRefresh()
      })
    }
  }
  
  finishRefresh() {
    this.isRefreshing = false
    this.resetUI()
  }
  
  resetUI() {
    this.distance = 0
    this.element.style.transform = 'translateY(0)'
    this.element.style.transition = 'transform 0.3s ease'
    
    setTimeout(() => {
      this.element.style.transition = ''
    }, 300)
  }
  
  destroy() {
    this.element.removeEventListener('touchstart', this.handleTouchStart)
    this.element.removeEventListener('touchmove', this.handleTouchMove)
    this.element.removeEventListener('touchend', this.handleTouchEnd)
  }
}

/**
 * 無限滾動組件
 */
export class InfiniteScroll {
  constructor(element, callback, options = {}) {
    this.element = element
    this.callback = callback
    this.options = {
      threshold: 100,    // 觸發閾值（距離底部的距離）
      throttle: 200,     // 節流時間
      ...options
    }
    
    this.isLoading = false
    this.isFinished = false
    this.throttleTimer = null
    
    this.init()
  }
  
  init() {
    this.element.addEventListener('scroll', this.handleScroll.bind(this))
  }
  
  handleScroll() {
    if (this.throttleTimer) return
    
    this.throttleTimer = setTimeout(() => {
      this.checkLoadMore()
      this.throttleTimer = null
    }, this.options.throttle)
  }
  
  checkLoadMore() {
    if (this.isLoading || this.isFinished) return
    
    const { scrollTop, scrollHeight, clientHeight } = this.element
    const distanceToBottom = scrollHeight - scrollTop - clientHeight
    
    if (distanceToBottom <= this.options.threshold) {
      this.loadMore()
    }
  }
  
  loadMore() {
    this.isLoading = true
    
    // 觸發加載事件
    this.element.dispatchEvent(new CustomEvent('loadmore'))
    
    // 執行回調
    if (this.callback) {
      Promise.resolve(this.callback()).then((hasMore) => {
        this.isLoading = false
        if (hasMore === false) {
          this.isFinished = true
        }
      }).catch(() => {
        this.isLoading = false
      })
    }
  }
  
  reset() {
    this.isLoading = false
    this.isFinished = false
  }
  
  destroy() {
    this.element.removeEventListener('scroll', this.handleScroll)
    if (this.throttleTimer) {
      clearTimeout(this.throttleTimer)
    }
  }
}

/**
 * 工具函數
 */
export const gestureUtils = {
  // 檢測是否為移動設備
  isMobile() {
    return /Android|webOS|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i.test(navigator.userAgent)
  },
  
  // 檢測是否支持觸摸
  isTouchDevice() {
    return 'ontouchstart' in window || navigator.maxTouchPoints > 0
  },
  
  // 防止頁面滾動
  preventDefault(e) {
    e.preventDefault()
  },
  
  // 節流函數
  throttle(func, wait) {
    let timeout
    return function executedFunction(...args) {
      const later = () => {
        clearTimeout(timeout)
        func(...args)
      }
      clearTimeout(timeout)
      timeout = setTimeout(later, wait)
    }
  },
  
  // 防抖函數
  debounce(func, wait, immediate) {
    let timeout
    return function executedFunction(...args) {
      const later = () => {
        timeout = null
        if (!immediate) func(...args)
      }
      const callNow = immediate && !timeout
      clearTimeout(timeout)
      timeout = setTimeout(later, wait)
      if (callNow) func(...args)
    }
  }
}

export default TouchHandler