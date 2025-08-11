# -*- coding: utf-8 -*-
"""
股票管理系統 - 交易記錄模型

定義股票交易記錄的數據模型，包括買入、賣出等交易信息。
"""

from datetime import datetime, date
from sqlalchemy import Column, Integer, String, Enum, Date, DECIMAL, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from database import Base

class Transaction(Base):
    """交易記錄模型"""
    
    __tablename__ = 'transactions'
    
    # 主鍵字段
    id = Column(Integer, primary_key=True, autoincrement=True, comment='交易ID')
    
    # 外鍵字段
    stock_code = Column(String(20), ForeignKey('stocks.stock_code', ondelete='CASCADE'), 
                       nullable=False, comment='股票代碼')
    
    # 交易信息字段
    transaction_type = Column(Enum('BUY', 'SELL', name='transaction_type_enum'), 
                             nullable=False, comment='交易類型')
    transaction_date = Column(Date, nullable=False, comment='交易日期')
    price = Column(DECIMAL(10, 4), nullable=False, comment='交易價格')
    shares = Column(DECIMAL(15, 4), nullable=False, comment='交易股數')
    total_amount = Column(DECIMAL(15, 2), nullable=False, comment='交易總額')
    commission = Column(DECIMAL(10, 2), default=0, comment='手續費')
    
    # 備註字段
    notes = Column(Text, comment='備註')
    
    # 時間戳字段
    created_at = Column(DateTime, default=datetime.utcnow, comment='記錄創建時間')
    
    # 關聯關係
    stock = relationship('Stock', back_populates='transactions')
    
    def __repr__(self):
        """字符串表示"""
        return f'<Transaction {self.id}: {self.transaction_type} {self.shares} shares of {self.stock_code}>'
    
    def to_dict(self):
        """轉換為字典格式"""
        return {
            'id': self.id,
            'stock_code': self.stock_code,
            'transaction_type': self.transaction_type,
            'transaction_date': self.transaction_date.isoformat() if self.transaction_date else None,
            'price': float(self.price) if self.price else 0,
            'shares': float(self.shares) if self.shares else 0,
            'total_amount': float(self.total_amount) if self.total_amount else 0,
            'commission': float(self.commission) if self.commission else 0,
            'notes': self.notes,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
    
    @classmethod
    def create_transaction(cls, stock_code, transaction_type, transaction_date, 
                          price, shares, commission=0, notes=None):
        """創建交易記錄"""
        # 計算交易總額
        total_amount = float(price) * float(shares) + float(commission)
        
        # 如果是賣出，總額應該是收入減去手續費
        if transaction_type == 'SELL':
            total_amount = float(price) * float(shares) - float(commission)
        
        return cls(
            stock_code=stock_code,
            transaction_type=transaction_type,
            transaction_date=transaction_date,
            price=price,
            shares=shares,
            total_amount=total_amount,
            commission=commission,
            notes=notes
        )
    
    def validate_transaction(self, session):
        """驗證交易記錄的有效性"""
        errors = []
        
        # 驗證股票代碼是否存在
        from .stock import Stock
        stock = session.query(Stock).filter(Stock.stock_code == self.stock_code).first()
        if not stock:
            errors.append(f'股票代碼 {self.stock_code} 不存在')
        
        # 驗證交易數量
        if self.shares <= 0:
            errors.append('交易股數必須大於0')
        
        # 驗證交易價格
        if self.price <= 0:
            errors.append('交易價格必須大於0')
        
        # 驗證交易日期
        if self.transaction_date > date.today():
            errors.append('交易日期不能是未來日期')
        
        # 如果是賣出，檢查是否有足夠的持股
        if self.transaction_type == 'SELL' and stock:
            if float(self.shares) > float(stock.total_shares):
                errors.append(f'賣出股數({self.shares})超過持有股數({stock.total_shares})')
        
        return errors
    
    def calculate_net_amount(self):
        """計算淨交易金額（扣除手續費）"""
        if self.transaction_type == 'BUY':
            return float(self.total_amount) - float(self.commission)
        else:  # SELL
            return float(self.total_amount) + float(self.commission)
    
    def get_display_info(self):
        """獲取用於顯示的交易信息"""
        return {
            'id': self.id,
            'stock_code': self.stock_code,
            'stock_name': self.stock.stock_name if self.stock else '',
            'transaction_type': self.transaction_type,
            'transaction_type_display': '買入' if self.transaction_type == 'BUY' else '賣出',
            'transaction_date': self.transaction_date.strftime('%Y-%m-%d') if self.transaction_date else '',
            'price': float(self.price) if self.price else 0,
            'shares': float(self.shares) if self.shares else 0,
            'total_amount': float(self.total_amount) if self.total_amount else 0,
            'commission': float(self.commission) if self.commission else 0,
            'net_amount': self.calculate_net_amount(),
            'notes': self.notes or '',
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S') if self.created_at else ''
        }