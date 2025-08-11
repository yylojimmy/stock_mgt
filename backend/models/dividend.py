# -*- coding: utf-8 -*-
"""
股票管理系統 - 股息記錄模型

定義股息收入記錄的數據模型，包括股息發放日期、金額等信息。
"""

from datetime import datetime, date
from sqlalchemy import Column, Integer, String, Enum, Date, DECIMAL, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from database import Base

class Dividend(Base):
    """股息記錄模型"""
    
    __tablename__ = 'dividends'
    
    # 主鍵字段
    id = Column(Integer, primary_key=True, autoincrement=True, comment='股息ID')
    
    # 外鍵字段
    stock_code = Column(String(20), ForeignKey('stocks.stock_code', ondelete='CASCADE'), 
                       nullable=False, comment='股票代碼')
    
    # 股息信息字段
    dividend_date = Column(Date, nullable=False, comment='股息發放日期')
    dividend_per_share = Column(DECIMAL(10, 4), nullable=False, comment='每股股息')
    total_dividend = Column(DECIMAL(15, 2), nullable=False, comment='總股息金額')
    tax_amount = Column(DECIMAL(10, 2), default=0, comment='稅額')
    net_dividend = Column(DECIMAL(15, 2), nullable=False, comment='稅後股息')
    currency = Column(Enum('CNY', 'HKD', 'USD', name='dividend_currency_enum'), 
                     default='CNY', comment='股息幣種')
    
    # 備註字段
    notes = Column(Text, comment='備註')
    
    # 時間戳字段
    created_at = Column(DateTime, default=datetime.utcnow, comment='記錄創建時間')
    
    # 關聯關係
    stock = relationship('Stock', back_populates='dividends')
    
    def __repr__(self):
        """字符串表示"""
        return f'<Dividend {self.id}: {self.stock_code} - {self.dividend_per_share} per share>'
    
    def to_dict(self):
        """轉換為字典格式"""
        return {
            'id': self.id,
            'stock_code': self.stock_code,
            'dividend_date': self.dividend_date.isoformat() if self.dividend_date else None,
            'dividend_per_share': float(self.dividend_per_share) if self.dividend_per_share else 0,
            'total_dividend': float(self.total_dividend) if self.total_dividend else 0,
            'tax_amount': float(self.tax_amount) if self.tax_amount else 0,
            'net_dividend': float(self.net_dividend) if self.net_dividend else 0,
            'currency': self.currency,
            'notes': self.notes,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
    
    @classmethod
    def create_dividend(cls, stock_code, dividend_date, dividend_per_share, 
                       shares_held, tax_amount=0, currency='CNY', notes=None):
        """創建股息記錄"""
        # 計算總股息金額
        total_dividend = float(dividend_per_share) * float(shares_held)
        
        # 計算稅後股息
        net_dividend = total_dividend - float(tax_amount)
        
        return cls(
            stock_code=stock_code,
            dividend_date=dividend_date,
            dividend_per_share=dividend_per_share,
            total_dividend=total_dividend,
            tax_amount=tax_amount,
            net_dividend=net_dividend,
            currency=currency,
            notes=notes
        )
    
    def validate_dividend(self, session):
        """驗證股息記錄的有效性"""
        errors = []
        
        # 驗證股票代碼是否存在
        from .stock import Stock
        stock = session.query(Stock).filter(Stock.stock_code == self.stock_code).first()
        if not stock:
            errors.append(f'股票代碼 {self.stock_code} 不存在')
        
        # 驗證每股股息
        if self.dividend_per_share <= 0:
            errors.append('每股股息必須大於0')
        
        # 驗證股息日期
        if self.dividend_date > date.today():
            errors.append('股息發放日期不能是未來日期')
        
        # 驗證稅額不能超過總股息
        if float(self.tax_amount) > float(self.total_dividend):
            errors.append('稅額不能超過總股息金額')
        
        # 驗證稅後股息計算
        expected_net = float(self.total_dividend) - float(self.tax_amount)
        if abs(float(self.net_dividend) - expected_net) > 0.01:
            errors.append('稅後股息計算錯誤')
        
        return errors
    
    def calculate_yield_rate(self, stock_price_at_date=None):
        """計算股息收益率"""
        if stock_price_at_date and stock_price_at_date > 0:
            return (float(self.dividend_per_share) / float(stock_price_at_date)) * 100
        return 0
    
    def get_display_info(self):
        """獲取用於顯示的股息信息"""
        return {
            'id': self.id,
            'stock_code': self.stock_code,
            'stock_name': self.stock.stock_name if self.stock else '',
            'dividend_date': self.dividend_date.strftime('%Y-%m-%d') if self.dividend_date else '',
            'dividend_per_share': float(self.dividend_per_share) if self.dividend_per_share else 0,
            'total_dividend': float(self.total_dividend) if self.total_dividend else 0,
            'tax_amount': float(self.tax_amount) if self.tax_amount else 0,
            'net_dividend': float(self.net_dividend) if self.net_dividend else 0,
            'currency': self.currency,
            'currency_display': self._get_currency_display(),
            'notes': self.notes or '',
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S') if self.created_at else ''
        }
    
    def _get_currency_display(self):
        """獲取幣種顯示名稱"""
        currency_map = {
            'CNY': '人民幣',
            'HKD': '港幣',
            'USD': '美元'
        }
        return currency_map.get(self.currency, self.currency)
    
    @staticmethod
    def get_annual_dividend_summary(session, stock_code, year):
        """獲取指定股票的年度股息統計"""
        from sqlalchemy import func, extract
        
        result = session.query(
            func.count(Dividend.id).label('dividend_count'),
            func.sum(Dividend.total_dividend).label('total_dividend'),
            func.sum(Dividend.net_dividend).label('total_net_dividend'),
            func.avg(Dividend.dividend_per_share).label('avg_dividend_per_share')
        ).filter(
            Dividend.stock_code == stock_code,
            extract('year', Dividend.dividend_date) == year
        ).first()
        
        return {
            'stock_code': stock_code,
            'year': year,
            'dividend_count': result.dividend_count or 0,
            'total_dividend': float(result.total_dividend) if result.total_dividend else 0,
            'total_net_dividend': float(result.total_net_dividend) if result.total_net_dividend else 0,
            'avg_dividend_per_share': float(result.avg_dividend_per_share) if result.avg_dividend_per_share else 0
        }