#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
股票管理系統 - API文檔生成器

自動生成API文檔，包括所有端點的詳細說明、參數和響應格式。
"""

import os
import json
from datetime import datetime

def generate_api_documentation():
    """生成API文檔"""
    
    # API文檔內容
    api_docs = {
        "title": "股票管理系統 API 文檔",
        "version": "1.0.0",
        "description": "提供股票、交易、股息和投資組合管理的完整API服務",
        "base_url": "http://localhost:5001/api",
        "generated_at": datetime.now().isoformat(),
        "endpoints": {
            "stocks": {
                "description": "股票管理API",
                "endpoints": [
                    {
                        "method": "GET",
                        "path": "/stocks",
                        "summary": "獲取股票列表",
                        "description": "獲取所有股票的列表，支持分頁和搜索",
                        "parameters": [
                            {"name": "page", "type": "integer", "description": "頁碼，默認為1"},
                            {"name": "per_page", "type": "integer", "description": "每頁數量，默認為20，最大100"},
                            {"name": "search", "type": "string", "description": "搜索關鍵詞（股票代碼或名稱）"},
                            {"name": "market", "type": "string", "description": "市場篩選（HKEX, NYSE, NASDAQ等）"}
                        ],
                        "response": {
                            "success": True,
                            "data": [
                                {
                                    "stock_id": 1,
                                    "stock_code": "0700.HK",
                                    "stock_name": "騰訊控股",
                                    "market": "HKEX",
                                    "total_shares": 100.0,
                                    "avg_cost": 400.50,
                                    "current_price": 420.00,
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
                    },
                    {
                        "method": "POST",
                        "path": "/stocks",
                        "summary": "創建股票",
                        "description": "添加新的股票到系統中",
                        "request_body": {
                            "stock_code": "0700.HK",
                            "stock_name": "騰訊控股",
                            "market": "HKEX",
                            "current_price": 420.00
                        },
                        "response": {
                            "success": True,
                            "data": {
                                "stock_id": 1,
                                "stock_code": "0700.HK",
                                "stock_name": "騰訊控股",
                                "market": "HKEX",
                                "current_price": 420.00
                            },
                            "message": "股票創建成功"
                        }
                    },
                    {
                        "method": "GET",
                        "path": "/stocks/{stock_id}",
                        "summary": "獲取單個股票詳情",
                        "description": "根據股票ID獲取詳細信息",
                        "parameters": [
                            {"name": "stock_id", "type": "integer", "description": "股票ID", "required": True}
                        ]
                    },
                    {
                        "method": "PUT",
                        "path": "/stocks/{stock_id}",
                        "summary": "更新股票信息",
                        "description": "更新指定股票的信息"
                    },
                    {
                        "method": "DELETE",
                        "path": "/stocks/{stock_id}",
                        "summary": "刪除股票",
                        "description": "從系統中刪除指定股票"
                    }
                ]
            },
            "transactions": {
                "description": "交易記錄管理API",
                "endpoints": [
                    {
                        "method": "GET",
                        "path": "/transactions",
                        "summary": "獲取交易記錄列表",
                        "description": "獲取所有交易記錄，支持分頁和篩選",
                        "parameters": [
                            {"name": "page", "type": "integer", "description": "頁碼"},
                            {"name": "per_page", "type": "integer", "description": "每頁數量"},
                            {"name": "stock_code", "type": "string", "description": "股票代碼篩選"},
                            {"name": "transaction_type", "type": "string", "description": "交易類型（buy/sell）"},
                            {"name": "start_date", "type": "string", "description": "開始日期（YYYY-MM-DD）"},
                            {"name": "end_date", "type": "string", "description": "結束日期（YYYY-MM-DD）"}
                        ]
                    },
                    {
                        "method": "POST",
                        "path": "/transactions",
                        "summary": "創建交易記錄",
                        "description": "添加新的交易記錄",
                        "request_body": {
                            "stock_code": "0700.HK",
                            "transaction_type": "buy",
                            "transaction_date": "2024-01-15",
                            "price": 400.50,
                            "shares": 100,
                            "commission": 10.00,
                            "notes": "首次買入"
                        }
                    },
                    {
                        "method": "GET",
                        "path": "/transactions/{transaction_id}",
                        "summary": "獲取單個交易記錄"
                    },
                    {
                        "method": "PUT",
                        "path": "/transactions/{transaction_id}",
                        "summary": "更新交易記錄"
                    },
                    {
                        "method": "DELETE",
                        "path": "/transactions/{transaction_id}",
                        "summary": "刪除交易記錄"
                    },
                    {
                        "method": "GET",
                        "path": "/transactions/stats",
                        "summary": "獲取交易統計信息"
                    }
                ]
            },
            "dividends": {
                "description": "股息記錄管理API",
                "endpoints": [
                    {
                        "method": "GET",
                        "path": "/dividends",
                        "summary": "獲取股息記錄列表",
                        "parameters": [
                            {"name": "page", "type": "integer", "description": "頁碼"},
                            {"name": "per_page", "type": "integer", "description": "每頁數量"},
                            {"name": "stock_code", "type": "string", "description": "股票代碼篩選"},
                            {"name": "start_date", "type": "string", "description": "開始日期"},
                            {"name": "end_date", "type": "string", "description": "結束日期"},
                            {"name": "currency", "type": "string", "description": "幣種篩選"}
                        ]
                    },
                    {
                        "method": "POST",
                        "path": "/dividends",
                        "summary": "創建股息記錄",
                        "request_body": {
                            "stock_code": "0700.HK",
                            "dividend_date": "2024-03-15",
                            "dividend_per_share": 2.40,
                            "total_dividend": 240.00,
                            "tax_amount": 24.00,
                            "currency": "HKD",
                            "notes": "年度股息"
                        }
                    },
                    {
                        "method": "GET",
                        "path": "/dividends/{dividend_id}",
                        "summary": "獲取單個股息記錄"
                    },
                    {
                        "method": "PUT",
                        "path": "/dividends/{dividend_id}",
                        "summary": "更新股息記錄"
                    },
                    {
                        "method": "DELETE",
                        "path": "/dividends/{dividend_id}",
                        "summary": "刪除股息記錄"
                    },
                    {
                        "method": "GET",
                        "path": "/dividends/stats",
                        "summary": "獲取股息統計信息"
                    }
                ]
            },
            "portfolio": {
                "description": "投資組合分析API",
                "endpoints": [
                    {
                        "method": "GET",
                        "path": "/portfolio/summary",
                        "summary": "獲取投資組合概覽",
                        "description": "獲取投資組合的總體統計信息",
                        "response": {
                            "success": True,
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
                    },
                    {
                        "method": "GET",
                        "path": "/portfolio/analysis",
                        "summary": "獲取投資組合分析",
                        "description": "獲取資產配置和持倉分析"
                    },
                    {
                        "method": "GET",
                        "path": "/portfolio/performance",
                        "summary": "獲取投資組合績效分析",
                        "parameters": [
                            {"name": "period", "type": "string", "description": "時間週期（1m, 3m, 6m, 1y, all）"}
                        ]
                    },
                    {
                        "method": "GET",
                        "path": "/portfolio/dividend-analysis",
                        "summary": "獲取股息分析",
                        "parameters": [
                            {"name": "year", "type": "integer", "description": "年份"}
                        ]
                    }
                ]
            }
        },
        "error_codes": {
            "400": "請求參數錯誤或數據驗證失敗",
            "404": "請求的資源不存在",
            "500": "服務器內部錯誤"
        },
        "data_types": {
            "stock_code": "股票代碼，格式如 '0700.HK', 'AAPL' 等",
            "transaction_type": "交易類型，'buy' 或 'sell'",
            "currency": "幣種代碼，如 'HKD', 'USD', 'CNY' 等",
            "date": "日期格式 YYYY-MM-DD",
            "decimal": "數值類型，支持小數點後4位"
        }
    }
    
    return api_docs

def generate_markdown_docs(api_docs):
    """生成Markdown格式的API文檔"""
    
    markdown = f"""# {api_docs['title']}

**版本:** {api_docs['version']}  
**基礎URL:** {api_docs['base_url']}  
**生成時間:** {api_docs['generated_at']}

## 概述

{api_docs['description']}

## 通用響應格式

所有API響應都遵循以下格式：

```json
{{
  "success": true,
  "data": {{}},
  "message": "操作成功",
  "pagination": {{}} // 僅在列表API中存在
}}
```

## 錯誤代碼

"""
    
    for code, description in api_docs['error_codes'].items():
        markdown += f"- **{code}**: {description}\n"
    
    markdown += "\n## 數據類型說明\n\n"
    
    for data_type, description in api_docs['data_types'].items():
        markdown += f"- **{data_type}**: {description}\n"
    
    markdown += "\n## API端點\n\n"
    
    for category, info in api_docs['endpoints'].items():
        markdown += f"### {category.upper()} - {info['description']}\n\n"
        
        for endpoint in info['endpoints']:
            markdown += f"#### {endpoint['method']} {endpoint['path']}\n\n"
            markdown += f"**功能:** {endpoint['summary']}\n\n"
            
            if 'description' in endpoint:
                markdown += f"{endpoint['description']}\n\n"
            
            if 'parameters' in endpoint:
                markdown += "**參數:**\n\n"
                for param in endpoint['parameters']:
                    required = " (必填)" if param.get('required') else ""
                    markdown += f"- `{param['name']}` ({param['type']}){required}: {param['description']}\n"
                markdown += "\n"
            
            if 'request_body' in endpoint:
                markdown += "**請求體示例:**\n\n"
                markdown += "```json\n"
                markdown += json.dumps(endpoint['request_body'], indent=2, ensure_ascii=False)
                markdown += "\n```\n\n"
            
            if 'response' in endpoint:
                markdown += "**響應示例:**\n\n"
                markdown += "```json\n"
                markdown += json.dumps(endpoint['response'], indent=2, ensure_ascii=False)
                markdown += "\n```\n\n"
            
            markdown += "---\n\n"
    
    return markdown

def generate_html_docs(api_docs):
    """生成HTML格式的API文檔"""
    
    html = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{api_docs['title']}</title>
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            line-height: 1.6;
            color: #333;
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
        }}
        .header {{
            background: #f8f9fa;
            padding: 20px;
            border-radius: 8px;
            margin-bottom: 30px;
        }}
        .endpoint {{
            border: 1px solid #e9ecef;
            border-radius: 8px;
            margin-bottom: 20px;
            overflow: hidden;
        }}
        .endpoint-header {{
            background: #007bff;
            color: white;
            padding: 15px;
            font-weight: bold;
        }}
        .endpoint-content {{
            padding: 20px;
        }}
        .method {{
            display: inline-block;
            padding: 4px 8px;
            border-radius: 4px;
            font-size: 12px;
            font-weight: bold;
            margin-right: 10px;
        }}
        .method.get {{ background: #28a745; color: white; }}
        .method.post {{ background: #007bff; color: white; }}
        .method.put {{ background: #ffc107; color: black; }}
        .method.delete {{ background: #dc3545; color: white; }}
        pre {{
            background: #f8f9fa;
            padding: 15px;
            border-radius: 4px;
            overflow-x: auto;
        }}
        .parameter {{
            background: #f8f9fa;
            padding: 10px;
            margin: 5px 0;
            border-radius: 4px;
        }}
    </style>
</head>
<body>
    <div class="header">
        <h1>{api_docs['title']}</h1>
        <p><strong>版本:</strong> {api_docs['version']}</p>
        <p><strong>基礎URL:</strong> {api_docs['base_url']}</p>
        <p><strong>生成時間:</strong> {api_docs['generated_at']}</p>
        <p>{api_docs['description']}</p>
    </div>
"""
    
    for category, info in api_docs['endpoints'].items():
        html += f"<h2>{category.upper()} - {info['description']}</h2>\n"
        
        for endpoint in info['endpoints']:
            method_class = endpoint['method'].lower()
            html += f"""<div class="endpoint">
                <div class="endpoint-header">
                    <span class="method {method_class}">{endpoint['method']}</span>
                    {endpoint['path']} - {endpoint['summary']}
                </div>
                <div class="endpoint-content">"""
            
            if 'description' in endpoint:
                html += f"<p>{endpoint['description']}</p>"
            
            if 'parameters' in endpoint:
                html += "<h4>參數:</h4>"
                for param in endpoint['parameters']:
                    required = " (必填)" if param.get('required') else ""
                    html += f"""<div class="parameter">
                        <strong>{param['name']}</strong> ({param['type']}){required}: {param['description']}
                    </div>"""
            
            if 'request_body' in endpoint:
                html += "<h4>請求體示例:</h4>"
                html += "<pre><code>" + json.dumps(endpoint['request_body'], indent=2, ensure_ascii=False) + "</code></pre>"
            
            if 'response' in endpoint:
                html += "<h4>響應示例:</h4>"
                html += "<pre><code>" + json.dumps(endpoint['response'], indent=2, ensure_ascii=False) + "</code></pre>"
            
            html += "</div></div>\n"
    
    html += "</body></html>"
    return html

def main():
    """主函數"""
    # 確保docs目錄存在
    docs_dir = os.path.dirname(os.path.abspath(__file__))
    os.makedirs(docs_dir, exist_ok=True)
    
    # 生成API文檔
    api_docs = generate_api_documentation()
    
    # 生成JSON格式文檔
    json_path = os.path.join(docs_dir, 'api_docs.json')
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(api_docs, f, indent=2, ensure_ascii=False)
    
    # 生成Markdown格式文檔
    markdown_content = generate_markdown_docs(api_docs)
    markdown_path = os.path.join(docs_dir, 'API_DOCS.md')
    with open(markdown_path, 'w', encoding='utf-8') as f:
        f.write(markdown_content)
    
    # 生成HTML格式文檔
    html_content = generate_html_docs(api_docs)
    html_path = os.path.join(docs_dir, 'api_docs.html')
    with open(html_path, 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    print(f"API文檔已生成:")
    print(f"- JSON: {json_path}")
    print(f"- Markdown: {markdown_path}")
    print(f"- HTML: {html_path}")

if __name__ == '__main__':
    main()