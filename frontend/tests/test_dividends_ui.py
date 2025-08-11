#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
股息記錄頁面UI測試
使用Playwright測試股息記錄的CRUD功能
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
    
    # 導航到股息記錄頁面
    await page.goto('http://localhost:3000/dividends')
    await page.wait_for_load_state('networkidle')
    
    # 等待頁面關鍵元素加載完成
    await page.wait_for_selector('.dividend-list', timeout=10000)
    await page.wait_for_selector('.el-table', timeout=10000)
    await page.wait_for_timeout(3000)  # 額外等待數據加載
    
    yield page
    
    await context.close()
    await browser.close()
    await playwright.stop()


class TestDividendsUI:
    """股息記錄頁面UI測試類"""
    
    @pytest.mark.asyncio
    async def test_page_load(self, page):
        """測試頁面加載"""
        
        # 檢查統計卡片
        stats_component = page.locator('.dividend-stats').first
        await stats_component.wait_for(state='visible', timeout=10000)
        assert await stats_component.is_visible()
        
        # 檢查篩選區域
        filter_card = page.locator('.filter-card').first
        await filter_card.wait_for(state='visible')
        assert await filter_card.is_visible()
        
        # 檢查添加股息按鈕
        add_button = page.locator('button:has-text("添加股息")').first
        await add_button.wait_for(state='visible')
        assert await add_button.is_visible()
        
        # 檢查股息記錄表格
        table = page.locator('.el-table').first
        await table.wait_for(state='visible')
        assert await table.is_visible()
        
        # 檢查表格列標題
        headers = ['股息日期', '股票代碼', '每股股息', '總股息', '稅額', '淨股息', '幣種', '備註']
        for header in headers:
            header_element = page.locator(f'.el-table th:has-text("{header}")')
            assert await header_element.count() > 0
    
    @pytest.mark.asyncio
    async def test_filter_functionality(self, page):
        """測試篩選功能"""
        
        # 測試日期範圍篩選
        date_picker = page.locator('.filter-item:has-text("日期範圍") .el-date-editor').first
        await date_picker.wait_for(state='visible')
        assert await date_picker.is_visible()
        
        # 測試股票代碼篩選
        stock_select = page.locator('.filter-item:has-text("股票代碼") .el-select').first
        await stock_select.wait_for(state='visible')
        assert await stock_select.is_visible()
        
        # 測試幣種篩選
        currency_select = page.locator('.filter-item:has-text("幣種") .el-select').first
        await currency_select.wait_for(state='visible')
        assert await currency_select.is_visible()
        
        # 測試重置篩選按鈕
        reset_button = page.locator('button:has-text("重置篩選")').first
        await reset_button.wait_for(state='visible')
        assert await reset_button.is_visible()
    
    @pytest.mark.asyncio
    async def test_create_dividend(self, page):
        """測試創建股息記錄"""
        
        # 點擊添加股息按鈕
        add_button = page.locator('button:has-text("添加股息")').first
        await add_button.click()
        
        # 等待對話框出現
        dialog = page.locator('.el-dialog').first
        await dialog.wait_for(state='visible')
        
        # 檢查對話框標題
        dialog_title = await page.locator('.el-dialog__title').first.text_content()
        assert '新增股息記錄' in dialog_title
        
        # 填寫表單
        # 選擇股票代碼
        await page.wait_for_timeout(2000)  # 等待股票數據加載
        
        stock_select = page.locator('.el-dialog .el-form-item:has-text("股票代碼") .el-select').first
        await stock_select.wait_for(state='visible', timeout=10000)
        
        # 點擊股票選擇器
        await stock_select.click()
        await page.wait_for_timeout(1000)
        
        # 等待選項出現並選擇第一個
        try:
            await page.wait_for_selector('.el-select-dropdown:visible .el-option', timeout=10000)
            first_option = page.locator('.el-select-dropdown:visible .el-option').first
            await first_option.click(timeout=5000)
            print("成功選擇股票")
        except Exception as e:
            print(f"股票選擇失敗: {e}")
            # 嘗試手動輸入
            input_field = stock_select.locator('input').first
            await input_field.fill('1398.HK')
            await page.keyboard.press('Enter')
        
        # 設置股息日期（今天）
        today = datetime.now().strftime('%Y-%m-%d')
        date_input = page.locator('.el-dialog .el-form-item:has-text("股息日期") .el-date-editor input').first
        await date_input.click()
        await date_input.clear()
        await date_input.fill(today)
        await page.keyboard.press('Escape')
        
        # 輸入每股股息
        dividend_per_share_input = page.locator('.el-dialog .el-form-item:has-text("每股股息") .el-input-number input').first
        await dividend_per_share_input.fill('0.50')
        
        # 輸入總股息
        total_dividend_input = page.locator('.el-dialog .el-form-item:has-text("總股息") .el-input-number input').first
        await total_dividend_input.fill('500.00')
        
        # 輸入稅額
        tax_amount_input = page.locator('.el-dialog .el-form-item:has-text("稅額") .el-input-number input').first
        await tax_amount_input.fill('50.00')
        
        # 選擇幣種
        currency_select = page.locator('.el-dialog .el-form-item:has-text("幣種") .el-select').first
        await currency_select.click()
        await page.wait_for_timeout(500)
        
        # 選擇USD
        usd_option = page.locator('.el-select-dropdown:visible .el-option:has-text("USD")').first
        await usd_option.click()
        
        # 輸入備註
        notes_input = page.locator('.el-dialog .el-form-item:has-text("備註") .el-input__inner').first
        await notes_input.fill('測試股息記錄')
        
        # 提交表單
        submit_button = page.locator('.el-dialog button:has-text("確定")').first
        await submit_button.click()
        
        # 等待對話框關閉
        await dialog.wait_for(state='hidden', timeout=10000)
        
        # 等待成功消息
        await page.wait_for_selector('.el-message--success', timeout=10000)
        success_message = await page.locator('.el-message--success').first.text_content()
        assert '新增成功' in success_message
        
        # 驗證新記錄出現在表格中
        await page.wait_for_timeout(2000)
        table_rows = page.locator('.el-table tbody tr')
        row_count = await table_rows.count()
        assert row_count > 0
    
    @pytest.mark.asyncio
    async def test_edit_dividend(self, page):
        """測試編輯股息記錄"""
        
        # 等待表格加載
        await page.wait_for_selector('.el-table tbody tr', timeout=10000)
        
        # 查找第一行的編輯按鈕
        first_row = page.locator('.el-table tbody tr').first
        edit_button = first_row.locator('button:has-text("編輯")').first
        
        # 如果沒有編輯按鈕，可能需要點擊操作列的下拉菜單
        if not await edit_button.is_visible():
            # 查找操作列的下拉按鈕
            dropdown_button = first_row.locator('.el-dropdown-link, .el-button--text').first
            if await dropdown_button.is_visible():
                await dropdown_button.click()
                await page.wait_for_timeout(500)
                edit_button = page.locator('.el-dropdown-menu .el-dropdown-menu__item:has-text("編輯")').first
        
        await edit_button.click()
        
        # 等待編輯對話框出現
        dialog = page.locator('.el-dialog').first
        await dialog.wait_for(state='visible')
        
        # 檢查對話框標題
        dialog_title = await page.locator('.el-dialog__title').first.text_content()
        assert '編輯股息記錄' in dialog_title
        
        # 修改備註
        notes_input = page.locator('.el-dialog .el-form-item:has-text("備註") .el-input__inner').first
        await notes_input.clear()
        await notes_input.fill('已編輯的股息記錄')
        
        # 提交修改
        submit_button = page.locator('.el-dialog button:has-text("確定")').first
        await submit_button.click()
        
        # 等待對話框關閉
        await dialog.wait_for(state='hidden', timeout=10000)
        
        # 等待成功消息
        await page.wait_for_selector('.el-message--success', timeout=10000)
        success_message = await page.locator('.el-message--success').first.text_content()
        assert '更新成功' in success_message
    
    @pytest.mark.asyncio
    async def test_delete_dividend(self, page):
        """測試刪除股息記錄"""
        
        # 等待表格加載
        await page.wait_for_selector('.el-table tbody tr', timeout=10000)
        
        # 記錄刪除前的行數
        initial_rows = await page.locator('.el-table tbody tr').count()
        
        # 查找第一行的刪除按鈕
        first_row = page.locator('.el-table tbody tr').first
        delete_button = first_row.locator('button:has-text("刪除")').first
        
        # 如果沒有刪除按鈕，可能需要點擊操作列的下拉菜單
        if not await delete_button.is_visible():
            dropdown_button = first_row.locator('.el-dropdown-link, .el-button--text').first
            if await dropdown_button.is_visible():
                await dropdown_button.click()
                await page.wait_for_timeout(500)
                delete_button = page.locator('.el-dropdown-menu .el-dropdown-menu__item:has-text("刪除")').first
        
        await delete_button.click()
        
        # 等待確認對話框
        confirm_dialog = page.locator('.el-message-box').first
        await confirm_dialog.wait_for(state='visible')
        
        # 點擊確定按鈕
        confirm_button = page.locator('.el-message-box button:has-text("確定")').first
        await confirm_button.click()
        
        # 等待成功消息
        await page.wait_for_selector('.el-message--success', timeout=10000)
        success_message = await page.locator('.el-message--success').first.text_content()
        assert '刪除成功' in success_message
        
        # 驗證行數減少
        await page.wait_for_timeout(2000)
        final_rows = await page.locator('.el-table tbody tr').count()
        assert final_rows == initial_rows - 1
    
    @pytest.mark.asyncio
    async def test_batch_delete(self, page):
        """測試批量刪除"""
        
        # 等待表格加載
        await page.wait_for_selector('.el-table tbody tr', timeout=10000)
        
        # 檢查是否有多行數據
        rows = page.locator('.el-table tbody tr')
        row_count = await rows.count()
        
        if row_count < 2:
            # 如果數據不足，先創建一些測試數據
            await self.test_create_dividend(page)
            await page.wait_for_timeout(2000)
        
        # 選擇前兩行的複選框
        first_checkbox = page.locator('.el-table tbody tr').first.locator('.el-checkbox__input')
        await first_checkbox.click()
        
        second_checkbox = page.locator('.el-table tbody tr').nth(1).locator('.el-checkbox__input')
        await second_checkbox.click()
        
        # 查找批量刪除按鈕（可能在表格上方的工具欄中）
        batch_delete_button = page.locator('button:has-text("批量刪除")').first
        
        if await batch_delete_button.is_visible():
            await batch_delete_button.click()
            
            # 等待確認對話框
            confirm_dialog = page.locator('.el-message-box').first
            await confirm_dialog.wait_for(state='visible')
            
            # 點擊確定按鈕
            confirm_button = page.locator('.el-message-box button:has-text("確定")').first
            await confirm_button.click()
            
            # 等待成功消息
            await page.wait_for_selector('.el-message--success', timeout=10000)
            success_message = await page.locator('.el-message--success').first.text_content()
            assert '批量刪除成功' in success_message
    
    @pytest.mark.asyncio
    async def test_export_data(self, page):
        """測試數據導出功能"""
        
        # 查找導出按鈕
        export_button = page.locator('button:has-text("導出數據")').first
        await export_button.wait_for(state='visible')
        assert await export_button.is_visible()
        
        # 點擊導出按鈕
        await export_button.click()
        
        # 等待成功消息或下載開始
        try:
            await page.wait_for_selector('.el-message--success', timeout=5000)
            success_message = await page.locator('.el-message--success').first.text_content()
            assert '數據導出成功' in success_message
        except:
            # 如果沒有數據可導出
            await page.wait_for_selector('.el-message--warning', timeout=5000)
            warning_message = await page.locator('.el-message--warning').first.text_content()
            assert '沒有數據可導出' in warning_message
    
    @pytest.mark.asyncio
    async def test_statistics_display(self, page):
        """測試統計數據顯示"""
        
        # 檢查統計卡片是否顯示
        stats_component = page.locator('.dividend-stats').first
        await stats_component.wait_for(state='visible')
        
        # 檢查統計項目
        stat_items = page.locator('.dividend-stats .stat-item')
        stat_count = await stat_items.count()
        assert stat_count >= 4  # 至少應該有總股息、稅額、淨股息、記錄數量
        
        # 檢查統計數值是否顯示
        for i in range(min(4, stat_count)):
            stat_item = stat_items.nth(i)
            stat_value = stat_item.locator('.stat-value')
            assert await stat_value.is_visible()
    
    @pytest.mark.asyncio
    async def test_responsive_design(self, page):
        """測試響應式設計"""
        
        # 測試桌面視圖
        await page.set_viewport_size({'width': 1920, 'height': 1080})
        await page.wait_for_timeout(1000)
        
        # 檢查篩選區域在桌面視圖下的佈局
        filter_row = page.locator('.filter-row').first
        assert await filter_row.is_visible()
        
        # 測試平板視圖
        await page.set_viewport_size({'width': 768, 'height': 1024})
        await page.wait_for_timeout(1000)
        
        # 檢查元素仍然可見
        add_button = page.locator('button:has-text("添加股息")').first
        assert await add_button.is_visible()
        
        # 測試手機視圖
        await page.set_viewport_size({'width': 375, 'height': 667})
        await page.wait_for_timeout(1000)
        
        # 檢查關鍵元素在手機視圖下仍然可用
        table = page.locator('.el-table').first
        assert await table.is_visible()
        
        # 恢復桌面視圖
        await page.set_viewport_size({'width': 1920, 'height': 1080})
        await page.wait_for_timeout(1000)


if __name__ == '__main__':
    # 運行測試
    pytest.main([__file__, '-v', '--tb=short'])