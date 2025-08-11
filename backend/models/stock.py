# -*- coding: utf-8 -*-
"""
股票管理系統 - 股票模型

定義股票基本信息的數據模型，包括股票代碼、名稱、價格等信息。
"""

from datetime import datetime
from sqlalchemy import Column, String, Enum, DECIMAL, DateTime, Text
from sqlalchemy.orm import relationship
from database import Base

class Stock(Base):
    """股票基本信息模型"""
    
    __tablename__ = 'stocks'
    
    # 主鍵字段
    stock_code = Column(String(20), primary_key=True, comment='股票代碼')
    
    # 基本信息字段
    stock_name = Column(String(100), nullable=False, comment='股票名稱')
    market = Column(Enum('SZ', 'SH', 'HK', 'US', name='market_enum'), 
                   nullable=False, comment='市場類型')
    currency = Column(Enum('CNY', 'HKD', 'USD', name='currency_enum'), 
                     default='CNY', comment='交易幣種')
    
    # 價格相關字段
    current_price = Column(DECIMAL(10, 4), default=0, comment='當前價格')
    price_update_time = Column(DateTime, comment='價格更新時間')
    
    # 持倉相關字段
    total_shares = Column(DECIMAL(15, 4), default=0, comment='總持股數')
    avg_cost = Column(DECIMAL(10, 4), default=0, comment='平均成本價')
    
    # 時間戳字段
    created_at = Column(DateTime, default=datetime.utcnow, comment='創建時間')
    updated_at = Column(DateTime, default=datetime.utcnow, 
                       onupdate=datetime.utcnow, comment='更新時間')
    
    # 關聯關係
    transactions = relationship('Transaction', back_populates='stock', 
                               cascade='all, delete-orphan')
    dividends = relationship('Dividend', back_populates='stock', 
                            cascade='all, delete-orphan')
    
    def __repr__(self):
        """字符串表示"""
        return f'<Stock {self.stock_code}: {self.stock_name}>'
    
    def to_dict(self):
        """轉換為字典格式"""
        return {
            'stock_code': self.stock_code,
            'stock_name': self.stock_name,
            'market': self.market,
            'currency': self.currency,
            'current_price': float(self.current_price) if self.current_price else 0,
            'price_update_time': self.price_update_time.isoformat() if self.price_update_time else None,
            'total_shares': float(self.total_shares) if self.total_shares else 0,
            'avg_cost': float(self.avg_cost) if self.avg_cost else 0,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
    
    def calculate_market_value(self):
        """計算市值"""
        if self.current_price and self.total_shares:
            return float(self.current_price) * float(self.total_shares)
        return 0
    
    def calculate_profit_loss(self):
        """計算盈虧金額"""
        market_value = self.calculate_market_value()
        cost_value = float(self.avg_cost) * float(self.total_shares) if self.avg_cost and self.total_shares else 0
        return market_value - cost_value
    
    def calculate_profit_loss_rate(self):
        """計算盈虧比例"""
        cost_value = float(self.avg_cost) * float(self.total_shares) if self.avg_cost and self.total_shares else 0
        if cost_value > 0:
            profit_loss = self.calculate_profit_loss()
            return (profit_loss / cost_value) * 100
        return 0
    
    def update_price(self, new_price):
        """更新股票價格"""
        self.current_price = new_price
        self.price_update_time = datetime.utcnow()
    
    def recalculate_avg_cost(self, session):
        """重新計算平均成本價"""
        from .transaction import Transaction
        
        # 獲取所有買入交易
        buy_transactions = session.query(Transaction).filter(
            Transaction.stock_code == self.stock_code,
            Transaction.transaction_type == 'BUY'
        ).all()
        
        # 獲取所有賣出交易
        sell_transactions = session.query(Transaction).filter(
            Transaction.stock_code == self.stock_code,
            Transaction.transaction_type == 'SELL'
        ).all()
        
        # 計算總買入金額和股數
        total_buy_amount = sum(float(t.total_amount) for t in buy_transactions)
        total_buy_shares = sum(float(t.shares) for t in buy_transactions)
        
        # 計算總賣出股數
        total_sell_shares = sum(float(t.shares) for t in sell_transactions)
        
        # 計算當前持股數
        current_shares = total_buy_shares - total_sell_shares
        self.total_shares = current_shares
        
        # 計算平均成本價（加權平均）
        if current_shares > 0 and total_buy_amount > 0:
            self.avg_cost = total_buy_amount / total_buy_shares
        else:
            self.avg_cost = 0
            self.total_shares = 0