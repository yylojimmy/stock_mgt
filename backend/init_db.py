#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
股票管理系統 - 數據庫初始化腳本

用於創建數據庫表、添加索引、插入初始數據等操作。
"""

import os
import sys
from datetime import datetime, date
from decimal import Decimal

# 添加項目根目錄到Python路徑
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database import init_database, get_db_manager
from models import Stock, Transaction, Dividend

def create_database_tables():
    """創建數據庫表"""
    print("正在創建數據庫表...")
    
    # 初始化數據庫
    db_manager = init_database(echo=True)
    
    # 創建所有表
    db_manager.create_tables()
    
    print("數據庫表創建完成!")
    return db_manager

def add_database_indexes():
    """添加數據庫索引"""
    print("正在添加數據庫索引...")
    
    db_manager = get_db_manager()
    
    # 執行SQL語句添加索引
    from sqlalchemy import text
    
    with db_manager.session_scope() as session:
        # 為transactions表添加索引
        session.execute(text("""
            CREATE INDEX IF NOT EXISTS idx_transactions_stock_code 
            ON transactions(stock_code)
        """))
        
        session.execute(text("""
            CREATE INDEX IF NOT EXISTS idx_transactions_date 
            ON transactions(transaction_date)
        """))
        
        session.execute(text("""
            CREATE INDEX IF NOT EXISTS idx_transactions_type 
            ON transactions(transaction_type)
        """))
        
        # 為dividends表添加索引
        session.execute(text("""
            CREATE INDEX IF NOT EXISTS idx_dividends_stock_code 
            ON dividends(stock_code)
        """))
        
        session.execute(text("""
            CREATE INDEX IF NOT EXISTS idx_dividends_date 
            ON dividends(dividend_date)
        """))
        
        # 為stocks表添加索引
        session.execute(text("""
            CREATE INDEX IF NOT EXISTS idx_stocks_market 
            ON stocks(market)
        """))
        
        session.execute(text("""
            CREATE INDEX IF NOT EXISTS idx_stocks_name 
            ON stocks(stock_name)
        """))
    
    print("數據庫索引添加完成!")

def insert_sample_data():
    """插入示例數據"""
    print("正在插入示例數據...")
    
    db_manager = get_db_manager()
    
    with db_manager.session_scope() as session:
        # 檢查是否已有數據
        existing_stocks = session.query(Stock).count()
        if existing_stocks > 0:
            print(f"數據庫中已有 {existing_stocks} 條股票記錄，跳過示例數據插入")
            return
        
        # 創建示例股票
        sample_stocks = [
            Stock(
                stock_code='000001.SZ',
                stock_name='平安銀行',
                market='SZ',
                currency='CNY',
                current_price=Decimal('12.34'),
                price_update_time=datetime.now()
            ),
            Stock(
                stock_code='000002.SZ',
                stock_name='萬科A',
                market='SZ',
                currency='CNY',
                current_price=Decimal('18.56'),
                price_update_time=datetime.now()
            ),
            Stock(
                stock_code='600036.SH',
                stock_name='招商銀行',
                market='SH',
                currency='CNY',
                current_price=Decimal('45.67'),
                price_update_time=datetime.now()
            ),
            Stock(
                stock_code='0700.HK',
                stock_name='騰訊控股',
                market='HK',
                currency='HKD',
                current_price=Decimal('385.20'),
                price_update_time=datetime.now()
            ),
            Stock(
                stock_code='1398.HK',
                stock_name='工商銀行',
                market='HK',
                currency='HKD',
                current_price=Decimal('4.85'),
                price_update_time=datetime.now()
            )
        ]
        
        # 添加股票到會話
        for stock in sample_stocks:
            session.add(stock)
        
        # 提交股票數據
        session.commit()
        
        # 創建示例交易記錄
        sample_transactions = [
            Transaction.create_transaction(
                stock_code='000001.SZ',
                transaction_type='BUY',
                transaction_date=date(2024, 1, 15),
                price=Decimal('11.50'),
                shares=1000,
                commission=Decimal('5.00'),
                notes='首次買入平安銀行'
            ),
            Transaction.create_transaction(
                stock_code='000001.SZ',
                transaction_type='BUY',
                transaction_date=date(2024, 2, 20),
                price=Decimal('12.00'),
                shares=500,
                commission=Decimal('3.00'),
                notes='加倉平安銀行'
            ),
            Transaction.create_transaction(
                stock_code='600036.SH',
                transaction_type='BUY',
                transaction_date=date(2024, 1, 10),
                price=Decimal('42.30'),
                shares=200,
                commission=Decimal('4.23'),
                notes='買入招商銀行'
            ),
            Transaction.create_transaction(
                stock_code='0700.HK',
                transaction_type='BUY',
                transaction_date=date(2024, 3, 5),
                price=Decimal('380.00'),
                shares=100,
                commission=Decimal('15.00'),
                notes='買入騰訊控股'
            ),
            Transaction.create_transaction(
                stock_code='1398.HK',
                transaction_type='BUY',
                transaction_date=date(2024, 3, 10),
                price=Decimal('4.80'),
                shares=2000,
                commission=Decimal('8.00'),
                notes='買入工商銀行'
            ),
            Transaction.create_transaction(
                stock_code='1398.HK',
                transaction_type='BUY',
                transaction_date=date(2024, 3, 15),
                price=Decimal('4.90'),
                shares=1000,
                commission=Decimal('5.00'),
                notes='加倉工商銀行'
            )
        ]
        
        # 添加交易記錄到會話
        for transaction in sample_transactions:
            session.add(transaction)
        
        # 創建示例股息記錄
        sample_dividends = [
            Dividend.create_dividend(
                stock_code='000001.SZ',
                dividend_date=date(2024, 6, 15),
                dividend_per_share=Decimal('0.15'),
                shares_held=1500,  # 1000 + 500
                tax_amount=Decimal('11.25'),
                currency='CNY',
                notes='平安銀行2024年中期股息'
            ),
            Dividend.create_dividend(
                stock_code='600036.SH',
                dividend_date=date(2024, 7, 10),
                dividend_per_share=Decimal('1.20'),
                shares_held=200,
                tax_amount=Decimal('12.00'),
                currency='CNY',
                notes='招商銀行2024年中期股息'
            )
        ]
        
        # 添加股息記錄到會話
        for dividend in sample_dividends:
            session.add(dividend)
        
        # 提交所有數據
        session.commit()
        
        # 重新計算股票的平均成本和持股數
        for stock in sample_stocks:
            stock.recalculate_avg_cost(session)
            session.add(stock)
        
        session.commit()
    
    print("示例數據插入完成!")

def verify_database():
    """驗證數據庫結構和數據"""
    print("正在驗證數據庫...")
    
    db_manager = get_db_manager()
    
    with db_manager.session_scope() as session:
        # 檢查表是否存在
        from sqlalchemy import inspect
        inspector = inspect(db_manager.engine)
        tables = inspector.get_table_names()
        
        expected_tables = ['stocks', 'transactions', 'dividends']
        missing_tables = [table for table in expected_tables if table not in tables]
        
        if missing_tables:
            print(f"錯誤: 缺少數據表 {missing_tables}")
            return False
        
        print(f"✓ 所有必需的數據表都存在: {tables}")
        
        # 檢查數據統計
        stock_count = session.query(Stock).count()
        transaction_count = session.query(Transaction).count()
        dividend_count = session.query(Dividend).count()
        
        print(f"✓ 數據統計:")
        print(f"  - 股票記錄: {stock_count} 條")
        print(f"  - 交易記錄: {transaction_count} 條")
        print(f"  - 股息記錄: {dividend_count} 條")
        
        # 檢查外鍵約束
        try:
            # 嘗試查詢關聯數據
            stocks_with_transactions = session.query(Stock).join(Transaction).count()
            stocks_with_dividends = session.query(Stock).join(Dividend).count()
            
            print(f"✓ 外鍵約束正常:")
            print(f"  - 有交易記錄的股票: {stocks_with_transactions} 個")
            print(f"  - 有股息記錄的股票: {stocks_with_dividends} 個")
            
        except Exception as e:
            print(f"錯誤: 外鍵約束檢查失敗 - {e}")
            return False
    
    print("數據庫驗證完成!")
    return True

def reset_database():
    """重置數據庫（刪除所有表並重新創建）"""
    print("警告: 即將重置數據庫，所有數據將被刪除!")
    
    confirm = input("確認要繼續嗎? (yes/no): ")
    if confirm.lower() != 'yes':
        print("操作已取消")
        return
    
    db_manager = get_db_manager()
    
    # 刪除所有表
    db_manager.drop_tables()
    
    # 重新創建表
    db_manager.create_tables()
    
    # 添加索引
    add_database_indexes()
    
    print("數據庫重置完成!")

def main():
    """主函數"""
    import argparse
    
    parser = argparse.ArgumentParser(description='股票管理系統數據庫初始化工具')
    parser.add_argument('--reset', action='store_true', help='重置數據庫')
    parser.add_argument('--sample-data', action='store_true', help='插入示例數據')
    parser.add_argument('--verify', action='store_true', help='驗證數據庫')
    parser.add_argument('--indexes', action='store_true', help='添加數據庫索引')
    
    args = parser.parse_args()
    
    try:
        if args.reset:
            reset_database()
        else:
            # 創建數據庫表
            create_database_tables()
            
            # 添加索引
            if args.indexes or not args.verify:
                add_database_indexes()
            
            # 插入示例數據
            if args.sample_data:
                insert_sample_data()
        
        # 驗證數據庫
        if args.verify or not any([args.reset, args.sample_data, args.indexes]):
            verify_database()
        
        # 顯示數據庫信息
        db_manager = get_db_manager()
        db_info = db_manager.get_database_info()
        print(f"\n數據庫信息:")
        print(f"  - 數據庫URL: {db_info['database_url']}")
        print(f"  - 表數量: {db_info['table_count']}")
        if 'file_size' in db_info:
            print(f"  - 文件大小: {db_info['file_size']} 字節")
        
    except Exception as e:
        print(f"錯誤: {e}")
        sys.exit(1)
    
    print("\n數據庫初始化完成!")

if __name__ == '__main__':
    main()