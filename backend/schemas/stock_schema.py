# -*- coding: utf-8 -*-
"""
股票管理系統 - 股票數據驗證Schema

定義股票相關的數據驗證和序列化規則。
"""

from marshmallow import Schema, fields, validate, validates, ValidationError
import re

class StockSchema(Schema):
    """股票基礎Schema"""
    
    stock_code = fields.Str(required=True, validate=validate.Length(min=1, max=20))
    stock_name = fields.Str(required=True, validate=validate.Length(min=1, max=100))
    market = fields.Str(required=True, validate=validate.OneOf(['SZ', 'SH', 'HK', 'US']))
    currency = fields.Str(validate=validate.OneOf(['CNY', 'HKD', 'USD']), load_default='CNY')
    current_price = fields.Decimal(places=4, allow_none=True)
    price_update_time = fields.DateTime(allow_none=True)
    total_shares = fields.Decimal(places=4, allow_none=True)
    avg_cost = fields.Decimal(places=4, allow_none=True)
    created_at = fields.DateTime(dump_only=True)
    updated_at = fields.DateTime(dump_only=True)
    
    @validates('stock_code')
    def validate_stock_code(self, value, **kwargs):
        """驗證股票代碼格式"""
        if not value:
            raise ValidationError('股票代碼不能為空')
        
        # 定義不同市場的股票代碼格式
        patterns = {
            'SZ': r'^[0-9]{6}\.SZ$',  # 深圳: 000001.SZ
            'SH': r'^[0-9]{6}\.SH$',  # 上海: 600000.SH
            'HK': r'^[0-9]{4,5}\.HK$',  # 香港: 0700.HK 或 00700.HK
            'US': r'^[A-Z]{1,5}$'     # 美股: AAPL
        }
        
        # 檢查是否符合任一市場格式
        valid = False
        for market, pattern in patterns.items():
            if re.match(pattern, value.upper()):
                valid = True
                break
        
        if not valid:
            raise ValidationError(
                '股票代碼格式不正確。格式要求：'
                'SZ市場(000001.SZ)、SH市場(600000.SH)、'
                'HK市場(0700.HK)、US市場(AAPL)'
            )
        
        return value.upper()
    
    @validates('current_price')
    def validate_current_price(self, value, **kwargs):
        """驗證當前價格"""
        if value is not None and value < 0:
            raise ValidationError('價格不能為負數')
        return value
    
    @validates('total_shares')
    def validate_total_shares(self, value, **kwargs):
        """驗證持股數量"""
        if value is not None and value < 0:
            raise ValidationError('持股數量不能為負數')
        return value
    
    @validates('avg_cost')
    def validate_avg_cost(self, value, **kwargs):
        """驗證平均成本"""
        if value is not None and value < 0:
            raise ValidationError('平均成本不能為負數')
        return value

class StockCreateSchema(Schema):
    """創建股票Schema"""
    
    class Meta:
        unknown = 'EXCLUDE'  # 忽略未知字段
    
    stock_code = fields.Str(
        required=True, 
        validate=validate.Length(min=1, max=20),
        error_messages={'required': '股票代碼是必填項'}
    )
    stock_name = fields.Str(
        required=True, 
        validate=validate.Length(min=1, max=100),
        error_messages={'required': '股票名稱是必填項'}
    )
    market = fields.Str(
        required=True, 
        validate=validate.OneOf(['SZ', 'SH', 'HK', 'US']),
        error_messages={'required': '市場類型是必填項'}
    )
    currency = fields.Str(
        validate=validate.OneOf(['CNY', 'HKD', 'USD']), 
        load_default='CNY'
    )
    current_price = fields.Decimal(
        places=4, 
        allow_none=True,
        validate=validate.Range(min=0, error='價格不能為負數')
    )
    total_shares = fields.Decimal(
        places=4, 
        allow_none=True,
        validate=validate.Range(min=0, error='持股數量不能為負數')
    )
    avg_cost = fields.Decimal(
        places=4, 
        allow_none=True,
        validate=validate.Range(min=0, error='平均成本不能為負數')
    )
    
    @validates('stock_code')
    def validate_stock_code(self, value, **kwargs):
        """驗證股票代碼格式"""
        if not value:
            raise ValidationError('股票代碼不能為空')
        
        value = value.upper().strip()
        
        # 定義不同市場的股票代碼格式
        patterns = {
            'SZ': r'^[0-9]{6}\.SZ$',
            'SH': r'^[0-9]{6}\.SH$', 
            'HK': r'^[0-9]{4,5}\.HK$',
            'US': r'^[A-Z]{1,5}$'
        }
        
        # 檢查格式
        valid = any(re.match(pattern, value) for pattern in patterns.values())
        
        if not valid:
            raise ValidationError(
                '股票代碼格式不正確。支持格式：'
                'SZ市場(000001.SZ)、SH市場(600000.SH)、'
                'HK市場(0700.HK)、US市場(AAPL)'
            )
        
        return value
    
    @validates('stock_name')
    def validate_stock_name(self, value, **kwargs):
        """驗證股票名稱"""
        if not value or not value.strip():
            raise ValidationError('股票名稱不能為空')
        
        return value.strip()
        
        # 檢查是否包含特殊字符
        invalid_chars = ['<', '>', '&', '"', "'", '\n', '\r', '\t']
        if any(char in value for char in invalid_chars):
            raise ValidationError('股票名稱不能包含特殊字符')

class StockUpdateSchema(Schema):
    """更新股票Schema"""
    
    stock_name = fields.Str(
        validate=validate.Length(min=1, max=100),
        allow_none=True
    )
    market = fields.Str(
        validate=validate.OneOf(['SZ', 'SH', 'HK', 'US']),
        allow_none=True
    )
    currency = fields.Str(
        validate=validate.OneOf(['CNY', 'HKD', 'USD']),
        allow_none=True
    )
    current_price = fields.Decimal(
        places=4,
        validate=validate.Range(min=0, error='價格不能為負數'),
        allow_none=True
    )
    
    @validates('stock_name')
    def validate_stock_name(self, value, **kwargs):
        """驗證股票名稱"""
        if value is not None:
            if not value.strip():
                raise ValidationError('股票名稱不能為空')
            
            # 檢查特殊字符
            invalid_chars = ['<', '>', '&', '"', "'", '\n', '\r', '\t']
            if any(char in value for char in invalid_chars):
                raise ValidationError('股票名稱不能包含特殊字符')
        return value.strip() if value else value

class StockSearchSchema(Schema):
    """股票搜索Schema"""
    
    q = fields.Str(
        required=True,
        validate=validate.Length(min=1, max=50),
        error_messages={'required': '搜索關鍵詞是必填項'}
    )
    limit = fields.Int(
        validate=validate.Range(min=1, max=50),
        load_default=10
    )
    market = fields.Str(
        validate=validate.OneOf(['SZ', 'SH', 'HK', 'US']),
        allow_none=True
    )

class StockListSchema(Schema):
    """股票列表查詢Schema"""
    
    page = fields.Int(
        validate=validate.Range(min=1),
        load_default=1
    )
    per_page = fields.Int(
        validate=validate.Range(min=1, max=100),
        load_default=20
    )
    market = fields.Str(
        validate=validate.OneOf(['SZ', 'SH', 'HK', 'US']),
        allow_none=True
    )
    search = fields.Str(
        validate=validate.Length(max=50),
        allow_none=True
    )
    sort_by = fields.Str(
        validate=validate.OneOf(['stock_code', 'stock_name', 'current_price', 'market_value']),
        load_default='stock_code'
    )
    sort_order = fields.Str(
        validate=validate.OneOf(['asc', 'desc']),
        load_default='asc'
    )