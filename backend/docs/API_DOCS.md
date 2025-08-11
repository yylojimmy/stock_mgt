# 股票管理系統 API 文檔

**版本:** 1.0.0  
**基礎URL:** http://localhost:5001/api  
**生成時間:** 2025-08-06T23:27:14.783391

## 概述

提供股票、交易、股息和投資組合管理的完整API服務

## 通用響應格式

所有API響應都遵循以下格式：

```json
{
  "success": true,
  "data": {},
  "message": "操作成功",
  "pagination": {} // 僅在列表API中存在
}
```

## 錯誤代碼

- **400**: 請求參數錯誤或數據驗證失敗
- **404**: 請求的資源不存在
- **500**: 服務器內部錯誤

## 數據類型說明

- **stock_code**: 股票代碼，格式如 '0700.HK', 'AAPL' 等
- **transaction_type**: 交易類型，'buy' 或 'sell'
- **currency**: 幣種代碼，如 'HKD', 'USD', 'CNY' 等
- **date**: 日期格式 YYYY-MM-DD
- **decimal**: 數值類型，支持小數點後4位

## API端點

### STOCKS - 股票管理API

#### GET /stocks

**功能:** 獲取股票列表

獲取所有股票的列表，支持分頁和搜索

**參數:**

- `page` (integer): 頁碼，默認為1
- `per_page` (integer): 每頁數量，默認為20，最大100
- `search` (string): 搜索關鍵詞（股票代碼或名稱）
- `market` (string): 市場篩選（HKEX, NYSE, NASDAQ等）

**響應示例:**

```json
{
  "success": true,
  "data": [
    {
      "stock_id": 1,
      "stock_code": "0700.HK",
      "stock_name": "騰訊控股",
      "market": "HKEX",
      "total_shares": 100.0,
      "avg_cost": 400.5,
      "current_price": 420.0,
      "created_at": "2024-01-01T00:00:00",
      "updated_at": "2024-01-01T00:00:00"
    }
  ],
  "pagination": {
    "page": 1,
    "per_page": 20,
    "total": 1,
    "pages": 1
  }
}
```

---

#### POST /stocks

**功能:** 創建股票

添加新的股票到系統中

**請求體示例:**

```json
{
  "stock_code": "0700.HK",
  "stock_name": "騰訊控股",
  "market": "HKEX",
  "current_price": 420.0
}
```

**響應示例:**

```json
{
  "success": true,
  "data": {
    "stock_id": 1,
    "stock_code": "0700.HK",
    "stock_name": "騰訊控股",
    "market": "HKEX",
    "current_price": 420.0
  },
  "message": "股票創建成功"
}
```

---

#### GET /stocks/{stock_id}

**功能:** 獲取單個股票詳情

根據股票ID獲取詳細信息

**參數:**

- `stock_id` (integer) (必填): 股票ID

---

#### PUT /stocks/{stock_id}

**功能:** 更新股票信息

更新指定股票的信息

---

#### DELETE /stocks/{stock_id}

**功能:** 刪除股票

從系統中刪除指定股票

---

### TRANSACTIONS - 交易記錄管理API

#### GET /transactions

**功能:** 獲取交易記錄列表

獲取所有交易記錄，支持分頁和篩選

**參數:**

- `page` (integer): 頁碼
- `per_page` (integer): 每頁數量
- `stock_code` (string): 股票代碼篩選
- `transaction_type` (string): 交易類型（buy/sell）
- `start_date` (string): 開始日期（YYYY-MM-DD）
- `end_date` (string): 結束日期（YYYY-MM-DD）

---

#### POST /transactions

**功能:** 創建交易記錄

添加新的交易記錄

**請求體示例:**

```json
{
  "stock_code": "0700.HK",
  "transaction_type": "buy",
  "transaction_date": "2024-01-15",
  "price": 400.5,
  "shares": 100,
  "commission": 10.0,
  "notes": "首次買入"
}
```

---

#### GET /transactions/{transaction_id}

**功能:** 獲取單個交易記錄

---

#### PUT /transactions/{transaction_id}

**功能:** 更新交易記錄

---

#### DELETE /transactions/{transaction_id}

**功能:** 刪除交易記錄

---

#### GET /transactions/stats

**功能:** 獲取交易統計信息

---

### DIVIDENDS - 股息記錄管理API

#### GET /dividends

**功能:** 獲取股息記錄列表

**參數:**

- `page` (integer): 頁碼
- `per_page` (integer): 每頁數量
- `stock_code` (string): 股票代碼篩選
- `start_date` (string): 開始日期
- `end_date` (string): 結束日期
- `currency` (string): 幣種篩選

---

#### POST /dividends

**功能:** 創建股息記錄

**請求體示例:**

```json
{
  "stock_code": "0700.HK",
  "dividend_date": "2024-03-15",
  "dividend_per_share": 2.4,
  "total_dividend": 240.0,
  "tax_amount": 24.0,
  "currency": "HKD",
  "notes": "年度股息"
}
```

---

#### GET /dividends/{dividend_id}

**功能:** 獲取單個股息記錄

---

#### PUT /dividends/{dividend_id}

**功能:** 更新股息記錄

---

#### DELETE /dividends/{dividend_id}

**功能:** 刪除股息記錄

---

#### GET /dividends/stats

**功能:** 獲取股息統計信息

---

### PORTFOLIO - 投資組合分析API

#### GET /portfolio/summary

**功能:** 獲取投資組合概覽

獲取投資組合的總體統計信息

**響應示例:**

```json
{
  "success": true,
  "data": {
    "total_market_value": 42000.0,
    "total_cost": 40050.0,
    "total_profit_loss": 1950.0,
    "total_return_rate": 4.87,
    "total_dividend": 240.0,
    "total_return": 2190.0,
    "total_return_pct": 5.47,
    "holdings_count": 1,
    "holdings": []
  }
}
```

---

#### GET /portfolio/analysis

**功能:** 獲取投資組合分析

獲取資產配置和持倉分析

---

#### GET /portfolio/performance

**功能:** 獲取投資組合績效分析

**參數:**

- `period` (string): 時間週期（1m, 3m, 6m, 1y, all）

---

#### GET /portfolio/dividend-analysis

**功能:** 獲取股息分析

**參數:**

- `year` (integer): 年份

---

