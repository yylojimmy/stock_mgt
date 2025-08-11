# -*- coding: utf-8 -*-
"""
股票管理系統 - 簡化的CRUD功能測試

使用Playwright進行前端功能測試，驗證股票的增刪改查功能。
"""

import pytest
import asyncio
import time
from playwright.async_api import async_playwright
import requests
import json
import os

# 設置環境變量以避免代理問題
os.environ['NO_PROXY'] = 'localhost,127.0.0.1'
os.environ['no_proxy'] = 'localhost,127.0.0.1'


class TestStockCRUDSimple:
    """股票CRUD簡化測試類"""
    
    def cleanup_test_data(self):
        """清理測試數據"""
        test_stock_codes = ['000001.SZ', '600000.SH', 'AAPL', '0700.HK', '000002.SZ']
        for stock_code in test_stock_codes:
            try:
                requests.delete(f'http://localhost:5001/api/stocks/{stock_code}')
            except:
                pass  # 忽略刪除失敗的情況
    
    @pytest.mark.asyncio
    async def test_stock_create_functionality(self):
        """測試股票創建功能"""
        # 清理測試數據
        self.cleanup_test_data()
        
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=False)
            context = await browser.new_context()
            page = await context.new_page()
            
            try:
                # 導航到股票管理頁面
                await page.goto('http://localhost:3000/stocks')
                await page.wait_for_load_state('networkidle')
                await page.wait_for_timeout(2000)  # 額外等待時間

                # 檢查頁面是否正確加載
                page_title = await page.title()
                print(f"頁面標題: {page_title}")
                
                # 等待更長時間讓頁面完全加載
                await page.wait_for_timeout(5000)
                
                # 截圖調試
                await page.screenshot(path='debug_page.png')
                
                # 打印頁面URL和狀態
                print(f"當前URL: {page.url}")
                print(f"頁面準備狀態: {await page.evaluate('document.readyState')}")
                
                # 檢查Vue應用是否已掛載
                vue_app = await page.query_selector('#app')
                if vue_app:
                    print("Vue應用已掛載")
                else:
                    print("Vue應用未掛載")
                
                # 等待頁面標題包含"股票管理"
                await page.wait_for_function('document.title.includes("股票管理") || document.title.includes("持倉概覽")')
                
                # 打印所有按鈕的詳細信息
                buttons = await page.query_selector_all('button')
                print(f"找到 {len(buttons)} 個按鈕")
                for i, button in enumerate(buttons):
                    text = await button.inner_text()
                    class_name = await button.get_attribute('class')
                    print(f"按鈕 {i}: 文本='{text}', 類名='{class_name}'")
                
                # 檢查是否有添加股票按鈕
                add_buttons = await page.query_selector_all('button:has-text("添加股票")')
                print(f"找到 {len(add_buttons)} 個添加股票按鈕")
                
                # 監聽控制台錯誤
                page.on('console', lambda msg: print(f"控制台: {msg.type}: {msg.text}"))
                page.on('pageerror', lambda error: print(f"頁面錯誤: {error}"))
                
                # 監聽網絡請求和響應
                def handle_request(request):
                    print(f"Request: {request.method} {request.url}")
                    if request.method == "POST":
                        print(f"Request body: {request.post_data}")
                    
                async def handle_response(response):
                    print(f"Response: {response.status} {response.url}")
                    if response.status >= 400:
                        try:
                            response_text = await response.text()
                            print(f"Error response body: {response_text}")
                        except Exception as e:
                            print(f"Could not read response body: {e}")
                    
                page.on("request", handle_request)
                page.on("response", handle_response)
                
                # 等待並點擊添加股票按鈕（選擇第一個）
                add_button = page.locator('button:has-text("添加股票")').first
                await add_button.wait_for(state='visible', timeout=10000)
                await add_button.click()
                print("已點擊添加股票按鈕")
                
                # 等待一下讓對話框有時間出現
                await page.wait_for_timeout(3000)
                
                # 檢查Vue組件狀態
                show_form_value = await page.evaluate('window.$nuxt?.$root?.$children?.[0]?.showForm')
                print(f"showForm 狀態: {show_form_value}")
                
                # 檢查對話框是否出現
                modal_elements = await page.query_selector_all('.stock-form-modal')
                overlay_elements = await page.query_selector_all('.stock-form-overlay')
                form_elements = await page.query_selector_all('[class*="stock-form"]')
                print(f"找到 {len(modal_elements)} 個 .stock-form-modal 元素")
                print(f"找到 {len(overlay_elements)} 個 .stock-form-overlay 元素")
                print(f"找到 {len(form_elements)} 個包含stock-form的元素")
                
                # 截圖查看點擊後的狀態
                await page.screenshot(path='after_click.png')
                
                # 等待對話框出現
                await page.wait_for_selector('.stock-form-modal', timeout=10000)
                
                # 填寫股票信息
                await page.fill('input[placeholder="例如: 000001.SZ"]', '000001.SZ')
                await page.fill('input[placeholder="股票名稱"]', '測試股票001')
                await page.select_option('select#market', 'SZ')  # 選擇深圳市場
                await page.fill('input[placeholder="0.00"]', '10.50')
                
                # 檢查表單數據
                stock_code_value = await page.input_value('input[placeholder="例如: 000001.SZ"]')
                stock_name_value = await page.input_value('input[placeholder="股票名稱"]')
                current_price_value = await page.input_value('input[placeholder="0.00"]')
                market_value = await page.input_value('select#market')
                
                print(f"表單數據 - 股票代碼: {stock_code_value}, 股票名稱: {stock_name_value}, 當前價格: {current_price_value}, 市場: {market_value}")
                
                # 檢查是否有驗證錯誤
                error_messages = await page.query_selector_all('.error-message, .field-error')
                print(f"找到 {len(error_messages)} 個驗證錯誤")
                for i, error in enumerate(error_messages):
                    error_text = await error.text_content()
                    print(f"錯誤 {i}: {error_text}")
                
                # 點擊提交按鈕（使用更精確的選擇器）
                submit_button = page.locator('button[type="submit"]:has-text("添加")')
                print(f"提交按鈕數量: {await submit_button.count()}")
                if await submit_button.count() > 0:
                    print("點擊提交按鈕...")
                    await submit_button.click(force=True)
                else:
                    print("未找到提交按鈕，嘗試其他選擇器")
                    # 嘗試使用表單內的提交按鈕
                    form_submit_button = page.locator('.stock-form-modal button[type="submit"]')
                    if await form_submit_button.count() > 0:
                        print("找到表單內的提交按鈕")
                        await form_submit_button.click(force=True)
                    else:
                        print("未找到任何提交按鈕")
                        # 列出所有按鈕
                        all_buttons = await page.query_selector_all('button')
                        for i, btn in enumerate(all_buttons):
                            btn_text = await btn.text_content()
                            btn_type = await btn.get_attribute('type')
                            print(f"按鈕 {i}: '{btn_text}' (type: {btn_type})")
                
                # 等待表單提交完成
                await page.wait_for_timeout(3000)
                
                # 截圖查看提交後的狀態
                await page.screenshot(path='after_submit.png')
                
                # 檢查頁面內容
                page_content = await page.content()
                print(f"提交後頁面內容長度: {len(page_content)}")
                
                # 檢查是否有錯誤信息
                error_elements = await page.query_selector_all('.error-message')
                print(f"找到 {len(error_elements)} 個錯誤信息")
                
                # 嘗試刷新頁面數據
                refresh_button = page.locator('button:has-text("刷新")')
                if await refresh_button.count() > 0:
                    await refresh_button.first.click()
                    await page.wait_for_timeout(2000)
                
                # 驗證股票是否成功添加到列表中
                try:
                    await page.wait_for_selector('text=000001.SZ', state='visible', timeout=10000)
                    print("成功找到新添加的股票")
                except:
                    print("未找到新添加的股票，檢查頁面內容...")
                    # 檢查所有股票代碼
                    stock_codes = await page.query_selector_all('[class*="stock-code"]')
                    print(f"找到 {len(stock_codes)} 個股票代碼元素")
                    
                    # 檢查包含000001的文本
                    text_elements = await page.query_selector_all('text=/000001/')
                    print(f"找到 {len(text_elements)} 個包含000001的文本元素")
                    
                    raise Exception("股票未成功添加到列表中")
                
                # 通過API驗證股票是否真的被創建
                response = requests.get('http://localhost:5001/api/stocks/000001.SZ')
                print(f"API驗證響應: {response.status_code}, {response.json()}")
                if response.status_code == 200:
                    response_data = response.json()
                    assert 'data' in response_data, "響應中缺少data字段"
                    stock_data = response_data['data']
                    assert stock_data['stock_code'] == '000001.SZ'
                    assert stock_data['stock_name'] == '測試股票001'
                    assert stock_data['market'] == 'SZ'
                    print("API驗證成功：股票已創建")
                else:
                    print(f"API驗證失敗：股票未找到，狀態碼 {response.status_code}")
                    # 檢查所有股票列表
                    all_stocks_response = requests.get('http://localhost:5001/api/stocks')
                    print(f"所有股票列表: {all_stocks_response.json()}")
                    raise AssertionError(f"股票創建失敗，API返回狀態碼: {response.status_code}")
                
                # 驗證價格
                if response.status_code == 200:
                    assert float(stock_data['current_price']) == 10.50
                
                print("✅ 股票創建功能測試通過")
                
            finally:
                await browser.close()
                self.cleanup_test_data()
    
    @pytest.mark.asyncio
    async def test_stock_update_functionality(self):
        """測試股票更新功能"""
        # 清理測試數據
        self.cleanup_test_data()
        
        # 先通過API創建一個測試股票
        test_stock = {
            'stock_code': '600000.SH',
            'stock_name': '測試股票002',
            'market': 'SH',
            'current_price': 15.75
        }
        requests.post('http://localhost:5001/api/stocks', json=test_stock)
        
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=False)
            context = await browser.new_context()
            page = await context.new_page()
            
            try:
                # 導航到股票列表頁面
                await page.goto('http://localhost:3000/stocks')
                await page.wait_for_load_state('networkidle')
                
                # 找到測試股票並點擊編輯按鈕
                stock_card = page.locator('.stock-card:has-text("600000.SH")').first
                await stock_card.locator('.edit-btn').click()
                await page.wait_for_selector('.stock-form-overlay')
                
                # 修改股票信息
                await page.fill('input[placeholder="股票名稱"]', '測試股票002更新')
                await page.fill('input[placeholder="0.00"]', '18.90')
                
                # 提交表單
                await page.click('button:has-text("更新")')
                
                # 等待更新完成
                await page.wait_for_timeout(3000)
                
                # 驗證更新是否成功
                await page.wait_for_selector('text=測試股票002更新')
                
                # 通過API驗證股票是否真的被更新
                response = requests.get('http://localhost:5001/api/stocks/600000.SH')
                assert response.status_code == 200
                stock_data = response.json()
                
                # 檢查返回數據結構
                if 'data' in stock_data:
                    stock_info = stock_data['data']
                else:
                    stock_info = stock_data
                    
                assert stock_info['stock_name'] == '測試股票002更新'
                assert float(stock_info['current_price']) == 18.90
                
                print("✅ 股票更新功能測試通過")
                
            finally:
                await browser.close()
            
        # 清理測試數據
        self.cleanup_test_data()
    
    @pytest.mark.asyncio
    async def test_stock_delete_functionality(self):
        """測試股票刪除功能"""
        # 清理測試數據
        self.cleanup_test_data()
        
        # 先通過API創建一個測試股票
        test_stock = {
            'stock_code': '0700.HK',
            'stock_name': '測試股票003',
            'market': 'HK',
            'current_price': 25.30
        }
        requests.post('http://localhost:5001/api/stocks', json=test_stock)
        
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=False)
            context = await browser.new_context()
            page = await context.new_page()
            
            try:
                # 導航到股票列表頁面
                await page.goto('http://localhost:3000/stocks')
                await page.wait_for_load_state('networkidle')
                
                # 設置對話框處理器
                page.on('dialog', lambda dialog: dialog.accept())
                
                # 找到測試股票並點擊刪除按鈕
                stock_card = page.locator('.stock-card:has-text("0700.HK")').first
                await stock_card.locator('.delete-btn').click()
                
                # 等待刪除完成
                await page.wait_for_timeout(3000)
                
                # 通過API驗證股票是否真的被刪除
                response = requests.get('http://localhost:5001/api/stocks/0700.HK')
                assert response.status_code == 404
                
                print("✅ 股票刪除功能測試通過")
                
            finally:
                await browser.close()
                self.cleanup_test_data()
    
    @pytest.mark.asyncio
    async def test_stock_list_display(self):
        """測試股票列表顯示功能"""
        # 清理測試數據
        self.cleanup_test_data()
        
        # 先通過API創建多個測試股票
        test_stocks = [
            {
                'stock_code': '000001.SZ',
                'stock_name': '測試股票001',
                'market': 'SZ',
                'current_price': 10.50
            },
            {
                'stock_code': '600000.SH',
                'stock_name': '測試股票002',
                'market': 'SH',
                'current_price': 15.75
            },
            {
                'stock_code': 'AAPL',
                'stock_name': '測試美股',
                'market': 'US',
                'current_price': 125.80
            }
        ]
        
        for stock in test_stocks:
            requests.post('http://localhost:5001/api/stocks', json=stock)
        
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=False)
            context = await browser.new_context()
            page = await context.new_page()
            
            try:
                # 導航到股票列表頁面
                await page.goto('http://localhost:3000')
                await page.wait_for_load_state('networkidle')
                
                # 驗證所有測試股票都顯示在列表中
                for stock in test_stocks:
                    await page.wait_for_selector(f'text={stock["stock_code"]}')
                    await page.wait_for_selector(f'text={stock["stock_name"]}')
                
                print("✅ 股票列表顯示功能測試通過")
                
            finally:
                await browser.close()
                self.cleanup_test_data()
    
    def test_api_functionality(self):
        """測試API功能（不需要瀏覽器）"""
        # 清理測試數據
        self.cleanup_test_data()
        
        try:
            # 測試創建股票
            test_stock = {
                'stock_code': '000002.SZ',
                'stock_name': 'API測試股票',
                'market': 'SZ',
                'current_price': 12.34
            }
            
            response = requests.post('http://localhost:5001/api/stocks', json=test_stock)
            if response.status_code not in [200, 201]:
                print(f"創建股票失敗: {response.status_code}, {response.text}")
            assert response.status_code in [200, 201]
            response_data = response.json()
            created_stock = response_data['data']
            assert created_stock['stock_code'] == '000002.SZ'
            
            # 測試獲取股票
            response = requests.get('http://localhost:5001/api/stocks/000002.SZ')
            assert response.status_code == 200
            response_data = response.json()
            stock_data = response_data['data']
            assert stock_data['stock_name'] == 'API測試股票'
            
            # 測試更新股票
            update_data = {
                'stock_name': 'API測試股票更新',
                'current_price': 15.67
            }
            response = requests.put('http://localhost:5001/api/stocks/000002.SZ', json=update_data)
            assert response.status_code == 200
            response_data = response.json()
            updated_stock = response_data['data']
            assert updated_stock['stock_name'] == 'API測試股票更新'
            assert float(updated_stock['current_price']) == 15.67
            
            # 測試刪除股票
            response = requests.delete('http://localhost:5001/api/stocks/000002.SZ')
            assert response.status_code == 200
            
            # 驗證股票已被刪除
            response = requests.get('http://localhost:5001/api/stocks/000002.SZ')
            assert response.status_code == 404
            
            print("✅ API功能測試通過")
            
        finally:
            # 清理測試數據
            try:
                requests.delete('http://localhost:5001/api/stocks/000002.SZ')
            except:
                pass


if __name__ == '__main__':
    pytest.main([__file__, '-v', '--tb=short'])