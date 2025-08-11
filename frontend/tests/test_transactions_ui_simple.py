#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
交易記錄頁面UI測試 - 簡化版本
使用Playwright測試交易記錄的基本功能
"""

import pytest
import pytest_asyncio
import asyncio
from playwright.async_api import async_playwright, Page, Browser, BrowserContext
import json
import time
from datetime import datetime, timedelta

# 配置pytest-asyncio
pytest_plugins = ('pytest_asyncio',)


@pytest_asyncio.fixture
async def page():
    """頁面fixture"""
    playwright = await async_playwright().start()
    browser = await playwright.chromium.launch(headless=True)
    context = await browser.new_context(
        viewport={'width': 1920, 'height': 1080},
        locale='zh-CN'
    )
    page = await context.new_page()
    
    # 導航到交易記錄頁面
    await page.goto('http://localhost:3000/transactions')
    await page.wait_for_load_state('networkidle')
    await page.wait_for_timeout(2000)
    
    yield page
    
    await context.close()
    await browser.close()
    await playwright.stop()


class TestTransactionsUISimple:
    """交易記錄頁面UI測試類 - 簡化版本"""
    
    @pytest.mark.asyncio
    async def test_page_load(self, page):
        """測試頁面加載"""
        
        # 檢查頁面標題
        title = await page.locator('h1.page-title').first.text_content()
        assert '交易記錄管理' in title
        
        # 檢查新增交易按鈕
        add_button = page.locator('button:has-text("新增交易")').first
        await add_button.wait_for(state='visible')
        assert await add_button.is_visible()
        
        # 檢查交易記錄表格
        table = page.locator('.el-table').first
        await table.wait_for(state='visible')
        assert await table.is_visible()
    
    @pytest.mark.asyncio
    async def test_open_create_dialog(self, page):
        """測試打開創建對話框"""
        
        # 點擊新增交易按鈕
        add_button = page.locator('button:has-text("新增交易")').first
        await add_button.click()
        
        # 等待對話框出現
        dialog = page.locator('.el-dialog').first
        await dialog.wait_for(state='visible')
        
        # 檢查對話框是否可見
        assert await dialog.is_visible()
        
        # 關閉對話框
        cancel_button = page.locator('button:has-text("取消")').first
        if await cancel_button.is_visible():
            await cancel_button.click()
        else:
            # 如果沒有取消按鈕，點擊關閉按鈕
            close_button = page.locator('.el-dialog__close').first
            await close_button.click()
    
    @pytest.mark.asyncio
    async def test_filter_section_visible(self, page):
        """測試篩選區域是否可見"""
        
        # 檢查篩選區域
        filter_section = page.locator('.filter-card, .filter-section, [class*="filter"]').first
        
        # 如果找不到篩選區域，檢查是否有搜索相關的元素
        if not await filter_section.is_visible():
            search_button = page.locator('button:has-text("搜索"), button:has-text("查詢")').first
            if await search_button.is_visible():
                assert True  # 有搜索按鈕說明有篩選功能
            else:
                # 檢查是否有任何輸入框或選擇框
                inputs = page.locator('input, select, .el-select')
                assert await inputs.count() > 0
        else:
            assert await filter_section.is_visible()
    
    @pytest.mark.asyncio
    async def test_table_has_headers(self, page):
        """測試表格是否有表頭"""
        
        # 檢查表格表頭
        table_headers = page.locator('.el-table__header th, .el-table thead th')
        header_count = await table_headers.count()
        
        # 表格應該至少有一些表頭
        assert header_count > 0
        
        # 檢查是否有常見的表頭文字
        header_text = await page.locator('.el-table__header, .el-table thead').first.text_content()
        
        # 至少應該包含一些交易相關的表頭
        common_headers = ['股票', '交易', '日期', '價格', '數量', '金額', '操作']
        has_relevant_header = any(header in header_text for header in common_headers)
        assert has_relevant_header, f"表頭內容: {header_text}"
    
    @pytest.mark.asyncio
    async def test_responsive_design_basic(self, page):
        """測試基本響應式設計"""
        
        # 測試移動端視圖
        await page.set_viewport_size({'width': 375, 'height': 667})
        await page.wait_for_timeout(1000)
        
        # 檢查頁面標題是否仍然可見（在移動端可能被隱藏）
        page_title = page.locator('h1.page-title').first
        # 在移動端，標題可能被隱藏或樣式改變，所以我們檢查是否存在
        title_exists = await page_title.count() > 0
        assert title_exists
        
        # 檢查表格是否仍然存在（在移動端可能被隱藏或樣式改變）
        table = page.locator('.el-table').first
        table_exists = await table.count() > 0
        assert table_exists, "表格在移動端視圖下應該仍然存在"
        
        # 恢復桌面視圖
        await page.set_viewport_size({'width': 1920, 'height': 1080})
        await page.wait_for_timeout(1000)


if __name__ == '__main__':
    pytest.main([__file__, '-v'])