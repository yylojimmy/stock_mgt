# -*- coding: utf-8 -*-
"""
股票管理系統 - 股息記錄數據驗證Schema

定義股息記錄相關的數據驗證和序列化規則。
"""

from marshmallow import Schema, fields, validate, validates, ValidationError, post_load
from datetime import date

class DividendSchema(Schema):
    """股息記錄基礎Schema"""
    
    dividend_id = fields.Int(dump_only=True)
    stock_code = fields.Str(required=True, validate=validate.Length(min=1, max=20))
    dividend_date = fields.Date(required=True)
    dividend_per_share = fields.Decimal(required=True, places=4)
    total_dividend = fields.Decimal(required=True, places=2)
    tax_amount = fields.Decimal(places=2, load_default=0)
    net_dividend = fields.Decimal(dump_only=True, places=2)
    currency = fields.Str(validate=validate.OneOf(['CNY', 'HKD', 'USD', 'EUR', 'GBP', 'JPY']), load_default='HKD')
    notes = fields.Str(allow_none=True)
    created_at = fields.DateTime(dump_only=True)
    updated_at = fields.DateTime(dump_only=True)
    
    # 關聯股票信息
    stock_name = fields.Str(dump_only=True)
    market = fields.Str(dump_only=True)

class DividendCreateSchema(Schema):
    """創建股息記錄Schema"""
    
    stock_code = fields.Str(
        required=True,
        validate=[
            validate.Length(min=1, max=20, error='股票代碼長度必須在1-20字符之間'),
            validate.Regexp(r'^[A-Z0-9.]+$', error='股票代碼只能包含大寫字母、數字和點號')
        ],
        error_messages={'required': '股票代碼不能為空'}
    )
    
    dividend_date = fields.Date(
        required=True,
        error_messages={'required': '股息日期不能為空'}
    )
    
    dividend_per_share = fields.Decimal(
        required=True,
        places=4,
        validate=validate.Range(min=0.0001, error='每股股息必須大於0'),
        error_messages={'required': '每股股息不能為空'}
    )
    
    total_dividend = fields.Decimal(
        required=True,
        places=2,
        validate=validate.Range(min=0.01, error='總股息必須大於0'),
        error_messages={'required': '總股息不能為空'}
    )
    
    tax_amount = fields.Decimal(
        places=2,
        validate=validate.Range(min=0, error='稅額不能為負數'),
        load_default=0
    )
    
    currency = fields.Str(
        validate=[
            validate.Length(equal=3, error='幣種代碼必須是3個字符'),
            validate.OneOf(['HKD', 'USD', 'CNY', 'EUR', 'GBP', 'JPY'], error='不支持的幣種')
        ],
        load_default='HKD'
    )
    
    notes = fields.Str(
        validate=validate.Length(max=500, error='備註長度不能超過500字符'),
        allow_none=True
    )
    
    @validates('dividend_date')
    def validate_dividend_date(self, value, **kwargs):
        """驗證股息日期"""
        if value > date.today():
            raise ValidationError('股息日期不能是未來日期')
        return value
    
    @post_load
    def process_data(self, data, **kwargs):
        """處理加載後的數據"""
        # 確保股票代碼為大寫
        if 'stock_code' in data:
            data['stock_code'] = data['stock_code'].upper()
        
        # 確保幣種代碼為大寫
        if 'currency' in data:
            data['currency'] = data['currency'].upper()
        
        return data

class DividendUpdateSchema(Schema):
    """更新股息記錄Schema"""
    
    stock_code = fields.Str(
        validate=[
            validate.Length(min=1, max=20, error='股票代碼長度必須在1-20字符之間'),
            validate.Regexp(r'^[A-Z0-9.]+$', error='股票代碼只能包含大寫字母、數字和點號')
        ]
    )
    
    dividend_date = fields.Date()
    
    dividend_per_share = fields.Decimal(
        places=4,
        validate=validate.Range(min=0.0001, error='每股股息必須大於0')
    )
    
    total_dividend = fields.Decimal(
        places=2,
        validate=validate.Range(min=0.01, error='總股息必須大於0')
    )
    
    tax_amount = fields.Decimal(
        places=2,
        validate=validate.Range(min=0, error='稅額不能為負數')
    )
    
    currency = fields.Str(
        validate=[
            validate.Length(equal=3, error='幣種代碼必須是3個字符'),
            validate.OneOf(['HKD', 'USD', 'CNY', 'EUR', 'GBP', 'JPY'], error='不支持的幣種')
        ]
    )
    
    notes = fields.Str(
        validate=validate.Length(max=500, error='備註長度不能超過500字符'),
        allow_none=True
    )
    
    @validates('dividend_date')
    def validate_dividend_date(self, value, **kwargs):
        """驗證股息日期"""
        if value and value > date.today():
            raise ValidationError('股息日期不能是未來日期')
        return value
    
    @post_load
    def process_data(self, data, **kwargs):
        """處理加載後的數據"""
        # 確保股票代碼為大寫
        if 'stock_code' in data:
            data['stock_code'] = data['stock_code'].upper()
        
        # 確保幣種代碼為大寫
        if 'currency' in data:
            data['currency'] = data['currency'].upper()
        
        return data