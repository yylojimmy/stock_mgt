# 股票管理系統需求規格說明

## 項目概述

本項目旨在開發一個個人股票投資管理系統，支持日常交易記錄、實時價格監控、投資組合分析等功能。系統需要同時支持PC端和移動端使用，滿足用戶每日查看和管理股票投資的需求。

## 用戶故事與驗收標準

### US-001: 每日持倉概覽

**作為** 股票投資者  
**我希望** 每天能夠快速查看我的持倉概況和當日盈虧  
**以便** 及時了解投資組合的表現  

**驗收標準 (EARS格式):**
- **當** 用戶打開系統首頁時，**系統應該** 顯示總資產、當日盈虧、總盈虧等關鍵指標
- **當** 用戶查看持倉列表時，**系統應該** 顯示每支股票的當前價格、持倉數量、成本價、盈虧金額和盈虧比例
- **當** 股價發生變化時，**系統應該** 實時更新相關數據並用顏色標識漲跌
- **當** 用戶在移動端查看時，**系統應該** 提供簡潔的卡片式布局
- **如果** 網絡連接異常，**系統應該** 顯示最後更新時間並提示刷新

### US-002: 實時價格更新

**作為** 股票投資者  
**我希望** 系統能夠自動獲取並更新股票的最新價格  
**以便** 實時了解我的投資價值變化  

**驗收標準 (EARS格式):**
- **當** 系統啟動時，**系統應該** 自動獲取所有持倉股票的最新價格
- **當** 市場開盤時，**系統應該** 每分鐘更新一次股價數據
- **當** 市場收盤時，**系統應該** 降低更新頻率至每小時一次
- **當** 價格更新時，**系統應該** 在界面上顯示更新時間戳
- **如果** API調用失敗，**系統應該** 使用備用數據源或顯示錯誤提示

### US-003: 快速交易錄入

**作為** 股票投資者  
**我希望** 能夠快速手動錄入交易記錄  
**以便** 及時記錄我的買賣操作  

**驗收標準 (EARS格式):**
- **當** 用戶點擊"添加交易"按鈕時，**系統應該** 顯示簡潔的交易錄入表單
- **當** 用戶輸入股票代碼時，**系統應該** 自動補全並顯示股票名稱
- **當** 用戶選擇交易類型（買入/賣出）時，**系統應該** 相應調整界面顏色和提示
- **當** 用戶保存交易記錄時，**系統應該** 自動計算並更新持倉數量和成本價
- **當** 用戶在移動端操作時，**系統應該** 提供大按鈕和簡化的輸入方式
- **如果** 賣出數量超過持倉，**系統應該** 顯示警告並阻止提交

### US-004: 股票基本信息管理

**作為** 股票投資者  
**我希望** 能夠查看和管理我持有的股票基本信息  
**以便** 了解我的投資組合詳情  

**驗收標準 (EARS格式):**
- **當** 用戶查看股票詳情時，**系統應該** 顯示股票代碼、名稱、當前價格、持倉數量、成本價等信息
- **當** 用戶點擊股票卡片時，**系統應該** 展開顯示該股票的交易歷史和收益分析
- **當** 用戶添加新股票時，**系統應該** 驗證股票代碼的有效性
- **當** 計算平均成本價時，**系統應該** 基於所有交易記錄實時計算
- **如果** 股票代碼已存在，**系統應該** 合併到現有記錄中

### US-005: 股息記錄管理

**作為** 股票投資者  
**我希望** 能夠記錄和查看股息收入  
**以便** 跟踪我的被動收入情況  

**驗收標準 (EARS格式):**
- **當** 用戶添加股息記錄時，**系統應該** 自動關聯到對應的股票並計算每股股息
- **當** 用戶查看股息歷史時，**系統應該** 按時間順序顯示所有股息記錄和累計收入
- **當** 用戶查看年度股息統計時，**系統應該** 顯示各股票的股息貢獻和總收益率
- **當** 用戶在移動端查看時，**系統應該** 提供簡潔的股息收入卡片視圖
- **如果** 股息金額異常，**系統應該** 提示用戶確認並允許修改

### US-006: 投資組合分析

**作為** 股票投資者  
**我希望** 能夠查看投資組合的關鍵分析數據  
**以便** 快速評估我的投資表現  

**驗收標準 (EARS格式):**
- **當** 用戶查看組合概覽時，**系統應該** 顯示總投資金額、當前市值、總盈虧和收益率
- **當** 用戶查看持倉分佈時，**系統應該** 以餅圖顯示各股票的資產佔比
- **當** 用戶查看收益排行時，**系統應該** 按盈虧金額或比例排序顯示股票表現
- **當** 用戶在移動端查看時，**系統應該** 提供滑動卡片式的分析視圖
- **如果** 數據不完整，**系統應該** 顯示可用數據並標註缺失項目

### US-007: 響應式設計與移動端適配

**作為** 股票投資者  
**我希望** 在PC和移動設備上都能獲得良好的使用體驗  
**以便** 隨時隨地管理我的投資組合  

**驗收標準 (EARS格式):**
- **當** 用戶在PC端訪問時，**系統應該** 提供多欄布局和詳細的數據展示
- **當** 用戶在移動端訪問時，**系統應該** 自動切換為單欄卡片式布局
- **當** 用戶在平板設備上訪問時，**系統應該** 提供適中的布局密度
- **當** 用戶旋轉移動設備時，**系統應該** 自動調整布局方向
- **當** 用戶在移動端操作時，**系統應該** 提供大尺寸的觸摸按鈕
- **如果** 屏幕尺寸過小，**系統應該** 隱藏次要信息並提供展開選項

### US-008: 用戶界面和操作體驗

**作為** 股票投資者  
**我希望** 擁有直觀易用的用戶界面  
**以便** 高效地進行日常投資管理  

**驗收標準 (EARS格式):**
- **當** 用戶首次訪問系統時，**系統應該** 顯示簡潔的功能介紹
- **當** 用戶執行操作時，**系統應該** 提供即時的視覺反饋
- **當** 數據加載時，**系統應該** 顯示加載動畫和進度提示
- **當** 發生錯誤時，**系統應該** 顯示清晰的錯誤信息和解決建議
- **當** 用戶進行重要操作時，**系統應該** 提供確認對話框
- **如果** 網絡連接不穩定，**系統應該** 提供離線模式和數據同步功能

## 數據模型與字段定義

### 數據庫表結構

#### 1. 股票基本信息表 (stocks)
```sql
CREATE TABLE stocks (
    stock_code VARCHAR(20) PRIMARY KEY COMMENT '股票代碼',
    stock_name VARCHAR(100) NOT NULL COMMENT '股票名稱',
    market ENUM('SZ', 'SH', 'HK', 'US') NOT NULL COMMENT '市場類型',
    currency ENUM('CNY', 'HKD', 'USD') DEFAULT 'CNY' COMMENT '交易幣種',
    current_price DECIMAL(10,4) DEFAULT 0 COMMENT '當前價格',
    price_update_time DATETIME COMMENT '價格更新時間',
    total_shares DECIMAL(15,4) DEFAULT 0 COMMENT '總持股數',
    avg_cost DECIMAL(10,4) DEFAULT 0 COMMENT '平均成本價',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '創建時間',
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新時間'
);
```

#### 2. 交易記錄表 (transactions)
```sql
CREATE TABLE transactions (
    id INT AUTO_INCREMENT PRIMARY KEY COMMENT '交易ID',
    stock_code VARCHAR(20) NOT NULL COMMENT '股票代碼',
    transaction_type ENUM('BUY', 'SELL') NOT NULL COMMENT '交易類型',
    transaction_date DATE NOT NULL COMMENT '交易日期',
    price DECIMAL(10,4) NOT NULL COMMENT '交易價格',
    shares DECIMAL(15,4) NOT NULL COMMENT '交易股數',
    total_amount DECIMAL(15,2) NOT NULL COMMENT '交易總額',
    commission DECIMAL(10,2) DEFAULT 0 COMMENT '手續費',
    notes TEXT COMMENT '備註',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '記錄創建時間',
    FOREIGN KEY (stock_code) REFERENCES stocks(stock_code) ON DELETE CASCADE
);
```

#### 3. 股息記錄表 (dividends)
```sql
CREATE TABLE dividends (
    id INT AUTO_INCREMENT PRIMARY KEY COMMENT '股息ID',
    stock_code VARCHAR(20) NOT NULL COMMENT '股票代碼',
    dividend_date DATE NOT NULL COMMENT '股息發放日期',
    dividend_per_share DECIMAL(10,4) NOT NULL COMMENT '每股股息',
    total_dividend DECIMAL(15,2) NOT NULL COMMENT '總股息金額',
    tax_amount DECIMAL(10,2) DEFAULT 0 COMMENT '稅額',
    net_dividend DECIMAL(15,2) NOT NULL COMMENT '稅後股息',
    currency ENUM('CNY', 'HKD', 'USD') DEFAULT 'CNY' COMMENT '股息幣種',
    notes TEXT COMMENT '備註',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '記錄創建時間',
    FOREIGN KEY (stock_code) REFERENCES stocks(stock_code) ON DELETE CASCADE
);
```

### API接口數據格式

#### 4. 股價API響應格式
```json
{
  "stock_code": "000001.SZ",
  "stock_name": "平安銀行",
  "current_price": 12.34,
  "change": 0.15,
  "change_percent": 1.23,
  "volume": 1234567,
  "timestamp": "2024-01-15T15:30:00Z",
  "market_status": "OPEN"
}
```

#### 5. 持倉概覽數據格式
```json
{
  "total_market_value": 150000.00,
  "total_cost": 140000.00,
  "total_profit_loss": 10000.00,
  "total_return_rate": 7.14,
  "daily_profit_loss": 500.00,
  "daily_return_rate": 0.33,
  "total_dividend_income": 2000.00,
  "stock_count": 8,
  "last_update_time": "2024-01-15T15:30:00Z"
}
```

#### 6. 股票卡片數據格式
```json
{
  "stock_code": "000001.SZ",
  "stock_name": "平安銀行",
  "current_price": 12.34,
  "change": 0.15,
  "change_percent": 1.23,
  "shares": 1000,
  "avg_cost": 11.50,
  "market_value": 12340.00,
  "profit_loss": 840.00,
  "profit_loss_rate": 7.30,
  "position_ratio": 8.23,
  "currency": "CNY"
}
```

### 表單字段定義

#### 7. 交易錄入表單
```json
{
  "stock_code": {
    "type": "autocomplete",
    "required": true,
    "placeholder": "輸入股票代碼或名稱",
    "validation": "^[0-9]{6}\\.(SZ|SH)$|^[0-9]{4}\\.(HK)$"
  },
  "transaction_type": {
    "type": "radio",
    "required": true,
    "options": ["BUY", "SELL"],
    "labels": ["買入", "賣出"]
  },
  "transaction_date": {
    "type": "date",
    "required": true,
    "default": "today"
  },
  "price": {
    "type": "number",
    "required": true,
    "min": 0.01,
    "step": 0.01,
    "placeholder": "交易價格"
  },
  "shares": {
    "type": "number",
    "required": true,
    "min": 1,
    "step": 1,
    "placeholder": "交易股數"
  },
  "commission": {
    "type": "number",
    "required": false,
    "min": 0,
    "step": 0.01,
    "default": 0,
    "placeholder": "手續費（可選）"
  },
  "notes": {
    "type": "textarea",
    "required": false,
    "maxlength": 500,
    "placeholder": "備註（可選）"
  }
}
```

#### 8. 股息錄入表單
```json
{
  "stock_code": {
    "type": "select",
    "required": true,
    "source": "user_stocks",
    "placeholder": "選擇股票"
  },
  "dividend_date": {
    "type": "date",
    "required": true,
    "placeholder": "股息發放日期"
  },
  "dividend_per_share": {
    "type": "number",
    "required": true,
    "min": 0.0001,
    "step": 0.0001,
    "placeholder": "每股股息"
  },
  "tax_amount": {
    "type": "number",
    "required": false,
    "min": 0,
    "step": 0.01,
    "default": 0,
    "placeholder": "稅額（可選）"
  },
  "notes": {
    "type": "textarea",
    "required": false,
    "maxlength": 500,
    "placeholder": "備註（可選）"
  }
}
```

### 移動端適配字段

#### 9. 移動端簡化顯示字段
```json
{
  "home_cards": {
    "summary_card": ["total_market_value", "daily_profit_loss", "total_return_rate"],
    "quick_actions": ["add_transaction", "view_portfolio", "refresh_prices"]
  },
  "portfolio_list": {
    "primary_fields": ["stock_name", "current_price", "profit_loss"],
    "secondary_fields": ["shares", "market_value", "change_percent"]
  },
  "stock_detail": {
    "tabs": ["overview", "transactions", "dividends", "analysis"],
    "overview_fields": ["current_price", "shares", "avg_cost", "market_value", "profit_loss", "profit_loss_rate"]
  }
}
```

## 非功能性需求

### 性能需求
- 頁面加載時間應該<2秒
- 股價數據更新響應時間應該<1秒
- 系統應該支持離線查看已緩存的數據
- 移動端操作響應時間應該<500毫秒

### 用戶體驗需求
- 界面應該簡潔直觀，減少學習成本
- 重要操作應該有明確的視覺反饋
- 錯誤信息應該用戶友好且提供解決方案
- 支持深色模式和淺色模式切換

### 兼容性需求
- PC端支持Chrome、Firefox、Safari、Edge瀏覽器
- 移動端支持iOS Safari和Android Chrome
- 響應式設計適配320px-1920px屏幕寬度
- 支持觸摸操作和鍵盤快捷鍵

### 數據安全需求
- 本地數據存儲加密
- API調用使用HTTPS協議
- 敏感操作需要用戶確認
- 定期數據備份提醒

### 可維護性需求
- 代碼遵循PEP 8編碼規範
- 關鍵函數包含中文註釋
- 前後端分離架構設計
- 模塊化組件便於擴展