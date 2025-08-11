# -*- coding: utf-8 -*-
"""
股票管理系統 - 端到端CRUD功能測試

使用Playwright進行前端功能測試，驗證股票的增刪改查功能。
"""

import pytest
import asyncio
import time
from playwright.async_api import async_playwright, Page, Browser
import requests
import json


@pytest.fixture(scope="session")
def event_loop():
    """創建事件循環"""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session")
async def browser():
    """設置瀏覽器環境"""
    async with async_playwright() as playwright:
        browser = await playwright.chromium.launch(headless=False)
        yield browser
        await browser.close()


@pytest.fixture
async def page(browser):
    """創建新頁面"""
    context = await browser.new_context()
    page = await context.new_page()
    yield page
    await context.close()


class TestStockCRUDE2E:
    """股票CRUD端到端測試類"""
    
    def setup_method(self):
        """每個測試方法前的設置"""
        # 清理測試數據
        self.cleanup_test_data()
    
    def teardown_method(self):
        """每個測試方法後的清理"""
        # 清理測試數據
        self.cleanup_test_data()
    
    def cleanup_test_data(self):
        """清理測試數據"""
        test_stock_codes = ['TEST001.SZ', 'TEST002.SH', 'TESTUS', 'TEST003.HK']
        for stock_code in test_stock_codes:
            try:
                requests.delete(f'http://localhost:5001/api/stocks/{stock_code}')
            except:
                pass  # 忽略刪除失敗的情況
    
    @pytest.mark.asyncio
    async def test_stock_create_functionality(self, page: Page):
        """測試股票創建功能"""
        
        # 導航到股票列表頁面
        await page.goto('http://localhost:3000')
        await page.wait_for_load_state('networkidle')
        
        # 點擊添加股票按鈕
        await page.click('button:has-text("添加股票")')
        await page.wait_for_selector('.el-dialog')
        
        # 填寫股票信息
        await page.fill('input[placeholder="請輸入股票代碼"]', 'TEST001.SZ')
        await page.fill('input[placeholder="請輸入股票名稱"]', '測試股票001')
        await page.select_option('select', 'SZ')  # 選擇深圳市場
        await page.fill('input[placeholder="請輸入當前價格"]', '10.50')
        
        # 提交表單
        await page.click('button:has-text("確定")')
        
        # 等待表單提交完成
        await page.wait_for_timeout(2000)
        
        # 驗證股票是否添加成功（檢查頁面是否顯示新股票）
        await page.wait_for_selector('text=TEST001.SZ')
        
        # 通過API驗證股票是否真的被創建
        response = requests.get('http://localhost:5001/api/stocks/TEST001.SZ')
        assert response.status_code == 200
        stock_data = response.json()
        assert stock_data['stock_code'] == 'TEST001.SZ'
        assert stock_data['stock_name'] == '測試股票001'
        assert stock_data['market'] == 'SZ'
        assert float(stock_data['current_price']) == 10.50
    
    @pytest.mark.asyncio
    async def test_stock_update_functionality(self, page: Page):
        """測試股票更新功能"""
        
        # 先通過API創建一個測試股票
        test_stock = {
            'stock_code': 'TEST002.SH',
            'stock_name': '測試股票002',
            'market': 'SH',
            'current_price': 15.75
        }
        requests.post('http://localhost:5001/api/stocks', json=test_stock)
        
        # 導航到股票列表頁面
        await page.goto('http://localhost:3000')
        await page.wait_for_load_state('networkidle')
        
        # 找到測試股票並點擊編輯按鈕
        stock_row = page.locator('tr:has-text("TEST002.SH")')
        await stock_row.locator('button:has-text("編輯")').click()
        await page.wait_for_selector('.el-dialog')
        
        # 修改股票信息
        await page.fill('input[placeholder="請輸入股票名稱"]', '測試股票002更新')
        await page.fill('input[placeholder="請輸入當前價格"]', '18.90')
        
        # 提交表單
        await page.click('button:has-text("確定")')
        
        # 等待更新完成
        await page.wait_for_timeout(2000)
        
        # 驗證更新是否成功
        await page.wait_for_selector('text=測試股票002更新')
        
        # 通過API驗證股票是否真的被更新
        response = requests.get('http://localhost:5001/api/stocks/TEST002.SH')
        assert response.status_code == 200
        stock_data = response.json()
        assert stock_data['stock_name'] == '測試股票002更新'
        assert float(stock_data['current_price']) == 18.90
    
    @pytest.mark.asyncio
    async def test_stock_delete_functionality(self, page: Page):
        """測試股票刪除功能"""
        
        # 先通過API創建一個測試股票
        test_stock = {
            'stock_code': 'TEST003.HK',
            'stock_name': '測試股票003',
            'market': 'HK',
            'current_price': 25.30
        }
        requests.post('http://localhost:5001/api/stocks', json=test_stock)
        
        # 導航到股票列表頁面
        await page.goto('http://localhost:3000')
        await page.wait_for_load_state('networkidle')
        
        # 找到測試股票並點擊刪除按鈕
        stock_row = page.locator('tr:has-text("TEST003.HK")')
        await stock_row.locator('button:has-text("刪除")').click()
        
        # 確認刪除
        await page.click('button:has-text("確定")')
        
        # 等待刪除完成
        await page.wait_for_timeout(2000)
        
        # 驗證股票是否被刪除（頁面上不應該再顯示該股票）
        await page.wait_for_function(
            'document.querySelector("tr:has-text(\"TEST003.HK\")") === null'
        )
        
        # 通過API驗證股票是否真的被刪除
        response = requests.get('http://localhost:5001/api/stocks/TEST003.HK')
        assert response.status_code == 404
    
    @pytest.mark.asyncio
    async def test_stock_list_display(self, page: Page):
        """測試股票列表顯示功能"""
        
        # 先通過API創建多個測試股票
        test_stocks = [
            {
                'stock_code': 'TEST001.SZ',
                'stock_name': '測試股票001',
                'market': 'SZ',
                'current_price': 10.50
            },
            {
                'stock_code': 'TEST002.SH',
                'stock_name': '測試股票002',
                'market': 'SH',
                'current_price': 15.75
            },
            {
                'stock_code': 'TESTUS',
                'stock_name': '測試美股',
                'market': 'US',
                'current_price': 125.80
            }
        ]
        
        for stock in test_stocks:
            requests.post('http://localhost:5001/api/stocks', json=stock)
        
        # 導航到股票列表頁面
        await page.goto('http://localhost:3000')
        await page.wait_for_load_state('networkidle')
        
        # 驗證所有測試股票都顯示在列表中
        for stock in test_stocks:
            await page.wait_for_selector(f'text={stock["stock_code"]}')
            await page.wait_for_selector(f'text={stock["stock_name"]}')
    
    @pytest.mark.asyncio
    async def test_stock_form_validation(self, page: Page):
        """測試股票表單驗證功能"""
        
        # 導航到股票列表頁面
        await page.goto('http://localhost:3000')
        await page.wait_for_load_state('networkidle')
        
        # 點擊添加股票按鈕
        await page.click('button:has-text("添加股票")')
        await page.wait_for_selector('.el-dialog')
        
        # 嘗試提交空表單
        await page.click('button:has-text("確定")')
        
        # 驗證是否顯示驗證錯誤信息
        await page.wait_for_selector('.el-form-item__error')
        
        # 填寫無效的股票代碼
        await page.fill('input[placeholder="請輸入股票代碼"]', 'INVALID')
        await page.click('button:has-text("確定")')
        
        # 驗證是否顯示股票代碼格式錯誤
        error_message = await page.locator('.el-form-item__error').text_content()
        assert '股票代碼格式不正確' in error_message
        
        # 填寫有效的股票代碼但缺少其他必填字段
        await page.fill('input[placeholder="請輸入股票代碼"]', 'TEST001.SZ')
        await page.click('button:has-text("確定")')
        
        # 驗證是否顯示其他字段的驗證錯誤
        error_elements = await page.locator('.el-form-item__error').all()
        assert len(error_elements) > 0


if __name__ == '__main__':
    pytest.main([__file__, '-v', '--tb=short'])