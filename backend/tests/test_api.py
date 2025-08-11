# -*- coding: utf-8 -*-
"""
股票管理系統 - API測試用例

測試所有API端點的功能和數據驗證。
"""

import pytest
import json
from datetime import date, datetime
from decimal import Decimal

from app import create_app
from database import init_database, session_scope
from models import Stock, Transaction, Dividend

@pytest.fixture
def app():
    """創建測試應用"""
    app = create_app()
    app.config['TESTING'] = True
    
    with app.app_context():
        # 初始化測試數據庫（內存數據庫）
        db_manager = init_database('sqlite:///:memory:', echo=False)
        # 創建數據庫表
        db_manager.create_tables()
        yield app
        # 清理數據庫
        db_manager.close()

@pytest.fixture
def client(app):
    """創建測試客戶端"""
    return app.test_client()

@pytest.fixture(autouse=True)
def clean_db(app):
    """每個測試前清理數據庫"""
    with app.app_context():
        with session_scope() as session:
            # 清理所有表的數據
            session.query(Dividend).delete()
            session.query(Transaction).delete()
            session.query(Stock).delete()
            session.commit()

@pytest.fixture
def sample_stock(app):
    """創建測試股票數據"""
    with app.app_context():
        with session_scope() as session:
            stock = Stock(
                stock_code='0700.HK',
                stock_name='騰訊控股',
                market='HK',
                total_shares=Decimal('100'),
                avg_cost=Decimal('400.50'),
                current_price=Decimal('420.00')
            )
            session.add(stock)
            session.commit()
            # 刷新對象以確保它在會話關閉後仍可用
            session.refresh(stock)
            # 創建一個分離的對象副本
            stock_data = {
                'stock_code': stock.stock_code,
                'stock_name': stock.stock_name,
                'market': stock.market,
                'total_shares': stock.total_shares,
                'avg_cost': stock.avg_cost,
                'current_price': stock.current_price
            }
        # 創建一個新的Stock對象，不與任何會話關聯
        detached_stock = Stock(**stock_data)
        return detached_stock

class TestStockAPI:
    """股票API測試"""
    
    def test_get_stocks_empty(self, client):
        """測試獲取空股票列表"""
        response = client.get('/api/stocks')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] is True
        assert data['data'] == []
    
    def test_create_stock(self, client):
        """測試創建股票"""
        stock_data = {
            'stock_code': '0700.HK',
            'stock_name': '騰訊控股',
            'market': 'HK',
            'current_price': 420.00
        }

        response = client.post('/api/stocks',
                             data=json.dumps(stock_data),
                             content_type='application/json')
        
        assert response.status_code == 201
        data = json.loads(response.data)
        assert data['success'] is True
        assert data['data']['stock_code'] == '0700.HK'
        assert data['data']['stock_name'] == '騰訊控股'
    
    def test_create_stock_invalid_data(self, client):
        """測試創建股票時的數據驗證"""
        # 缺少必填字段
        stock_data = {
            'stock_name': '騰訊控股'
        }
        
        response = client.post('/api/stocks',
                             data=json.dumps(stock_data),
                             content_type='application/json')
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert data['success'] is False
    
    def test_get_stock_by_id(self, client, sample_stock):
        """測試根據ID獲取股票"""
        response = client.get(f'/api/stocks/{sample_stock.stock_code}')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] is True
        assert data['data']['stock_code'] == '0700.HK'
    
    def test_get_stock_not_found(self, client):
        """測試獲取不存在的股票"""
        response = client.get('/api/stocks/999')
        assert response.status_code == 404
        data = json.loads(response.data)
        assert data['success'] is False
    
    def test_update_stock(self, client, sample_stock):
        """測試更新股票"""
        update_data = {
            'stock_name': '騰訊控股更新',
            'current_price': 450.00
        }
        
        response = client.put(f'/api/stocks/{sample_stock.stock_code}',
                             data=json.dumps(update_data),
                             content_type='application/json')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] is True
        assert data['data']['stock_name'] == '騰訊控股更新'
    
    def test_delete_stock(self, client, sample_stock):
        """測試刪除股票"""
        response = client.delete(f'/api/stocks/{sample_stock.stock_code}')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] is True
        
        # 確認股票已被刪除
        response = client.get(f'/api/stocks/{sample_stock.stock_code}')
        assert response.status_code == 404

class TestTransactionAPI:
    """交易記錄API測試"""
    
    def test_create_transaction(self, client, sample_stock):
        """測試創建交易記錄"""
        transaction_data = {
            'stock_code': '0700.HK',
            'transaction_type': 'BUY',
            'transaction_date': '2024-01-15',
            'price': 400.50,
            'shares': 100,
            'commission': 10.00,
            'notes': '首次買入'
        }
        
        response = client.post('/api/transactions',
                             data=json.dumps(transaction_data),
                             content_type='application/json')
        
        assert response.status_code == 201
        data = json.loads(response.data)
        assert data['success'] is True
        assert data['data']['stock_code'] == '0700.HK'
        assert data['data']['transaction_type'] == 'BUY'
    
    def test_create_transaction_invalid_stock(self, client):
        """測試創建交易記錄時股票不存在"""
        transaction_data = {
            'stock_code': 'INVALID',
            'transaction_type': 'BUY',
            'transaction_date': '2024-01-15',
            'price': 400.50,
            'shares': 100
        }
        
        response = client.post('/api/transactions',
                             data=json.dumps(transaction_data),
                             content_type='application/json')
        
        assert response.status_code == 404
        data = json.loads(response.data)
        assert data['success'] is False
    
    def test_get_transactions(self, client):
        """測試獲取交易記錄列表"""
        response = client.get('/api/transactions')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] is True
        assert 'pagination' in data
    
    def test_get_transactions_with_filters(self, client):
        """測試帶篩選條件的交易記錄查詢"""
        response = client.get('/api/transactions?stock_code=0700.HK&transaction_type=BUY')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] is True

class TestDividendAPI:
    """股息記錄API測試"""
    
    def test_create_dividend(self, client, sample_stock):
        """測試創建股息記錄"""
        dividend_data = {
            'stock_code': '0700.HK',
            'dividend_date': '2024-03-15',
            'dividend_per_share': 2.40,
            'total_dividend': 240.00,
            'tax_amount': 24.00,
            'currency': 'HKD',
            'notes': '年度股息'
        }
        
        response = client.post('/api/dividends',
                             data=json.dumps(dividend_data),
                             content_type='application/json')
        
        assert response.status_code == 201
        data = json.loads(response.data)
        assert data['success'] is True
        assert data['data']['stock_code'] == '0700.HK'
        assert float(data['data']['dividend_per_share']) == 2.40
    
    def test_get_dividends(self, client):
        """測試獲取股息記錄列表"""
        response = client.get('/api/dividends')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] is True
        assert 'pagination' in data
    
    def test_get_dividend_stats(self, client):
        """測試獲取股息統計"""
        response = client.get('/api/dividends/stats')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] is True

class TestPortfolioAPI:
    """投資組合API測試"""
    
    def test_get_portfolio_summary(self, client):
        """測試獲取投資組合概覽"""
        response = client.get('/api/portfolio/summary')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] is True
        assert 'total_market_value' in data['data']
        assert 'total_cost' in data['data']
    
    def test_get_portfolio_analysis(self, client):
        """測試獲取投資組合分析"""
        response = client.get('/api/portfolio/analysis')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] is True
        assert 'market_allocation' in data['data']
    
    def test_get_portfolio_performance(self, client):
        """測試獲取投資組合績效"""
        response = client.get('/api/portfolio/performance?period=1y')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] is True
        assert 'total_return_pct' in data['data']
    
    def test_get_dividend_analysis(self, client):
        """測試獲取股息分析"""
        response = client.get('/api/portfolio/dividend-analysis?year=2024')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] is True
        assert 'monthly_dividends' in data['data']

class TestDataValidation:
    """數據驗證測試"""
    
    def test_stock_code_validation(self, client):
        """測試股票代碼驗證"""
        # 無效的股票代碼格式
        stock_data = {
            'stock_code': 'invalid-code',
            'stock_name': '測試股票',
            'market': 'HKEX'
        }
        
        response = client.post('/api/stocks',
                             data=json.dumps(stock_data),
                             content_type='application/json')
        
        assert response.status_code == 400
    
    def test_date_validation(self, client, sample_stock):
        """測試日期驗證"""
        # 未來日期
        from datetime import date, timedelta
        future_date = (date.today() + timedelta(days=1)).strftime('%Y-%m-%d')
        
        transaction_data = {
            'stock_code': '0700.HK',
            'transaction_type': 'BUY',
            'transaction_date': future_date,
            'price': 400.50,
            'shares': 100
        }
        
        response = client.post('/api/transactions',
                             data=json.dumps(transaction_data),
                             content_type='application/json')
        
        assert response.status_code == 400
    
    def test_decimal_validation(self, client, sample_stock):
        """測試數值驗證"""
        # 負數價格
        transaction_data = {
            'stock_code': '0700.HK',
            'transaction_type': 'BUY',
            'transaction_date': '2024-01-15',
            'price': -100,
            'shares': 100
        }
        
        response = client.post('/api/transactions',
                             data=json.dumps(transaction_data),
                             content_type='application/json')
        
        assert response.status_code == 400

class TestErrorHandling:
    """錯誤處理測試"""
    
    def test_invalid_json(self, client):
        """測試無效JSON格式"""
        response = client.post('/api/stocks',
                             data='invalid json',
                             content_type='application/json')
        
        assert response.status_code == 400
    
    def test_missing_content_type(self, client):
        """測試缺少Content-Type"""
        response = client.post('/api/stocks',
                             data=json.dumps({'stock_code': 'TEST'}))
        
        assert response.status_code == 400
    
    def test_method_not_allowed(self, client):
        """測試不允許的HTTP方法"""
        response = client.patch('/api/stocks')
        assert response.status_code == 405

if __name__ == '__main__':
    pytest.main([__file__])