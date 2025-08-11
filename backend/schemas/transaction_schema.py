# -*- coding: utf-8 -*-
"""
股票管理系統 - 交易記錄數據驗證Schema

定義交易記錄相關的數據驗證和序列化規則。
"""

from marshmallow import Schema, fields, validate, validates, ValidationError, post_load
from datetime import date

class TransactionSchema(Schema):
    """交易記錄基礎Schema"""
    
    id = fields.Int(dump_only=True)
    transaction_id = fields.Int(dump_only=True)
    stock_code = fields.Str(required=True, validate=validate.Length(min=1, max=20))
    transaction_type = fields.Str(required=True, validate=validate.OneOf(['BUY', 'SELL']))
    transaction_date = fields.Date(required=True)
    price = fields.Decimal(required=True, places=4)
    shares = fields.Decimal(required=True, places=4)
    total_amount = fields.Decimal(dump_only=True, places=2)
    commission = fields.Decimal(places=2, load_default=0)
    notes = fields.Str(allow_none=True)
    created_at = fields.DateTime(dump_only=True)
    updated_at = fields.DateTime(dump_only=True)
    
    # 關聯股票信息
    stock_name = fields.Str(dump_only=True)
    market = fields.Str(dump_only=True)

class TransactionCreateSchema(Schema):
    """創建交易記錄Schema"""
    
    stock_code = fields.Str(
        required=True,
        validate=[
            validate.Length(min=1, max=20, error='股票代碼長度必須在1-20字符之間'),
            validate.Regexp(r'^[A-Z0-9.]+$', error='股票代碼只能包含大寫字母、數字和點號')
        ],
        error_messages={'required': '股票代碼不能為空'}
    )
    
    transaction_type = fields.Str(
        required=True,
        validate=validate.OneOf(['buy', 'sell', 'BUY', 'SELL'], error='交易類型必須是buy或sell'),
        error_messages={'required': '交易類型不能為空'}
    )
    
    transaction_date = fields.Date(
        required=True,
        error_messages={'required': '交易日期不能為空'}
    )
    
    price = fields.Decimal(
        required=True,
        places=4,
        validate=validate.Range(min=0.0001, error='價格必須大於0'),
        error_messages={'required': '價格不能為空'}
    )
    
    shares = fields.Decimal(
        required=True,
        places=4,
        validate=validate.Range(min=0.0001, error='股數必須大於0'),
        error_messages={'required': '股數不能為空'}
    )
    
    commission = fields.Decimal(
        places=2,
        validate=validate.Range(min=0, error='手續費不能為負數'),
        load_default=0
    )
    
    notes = fields.Str(
        validate=validate.Length(max=500, error='備註長度不能超過500字符'),
        allow_none=True
    )
    
    @validates('transaction_date')
    def validate_transaction_date(self, value, **kwargs):
        """驗證交易日期"""
        if value > date.today():
            raise ValidationError('交易日期不能是未來日期')
        return value
    
    @post_load
    def process_data(self, data, **kwargs):
        """處理加載後的數據"""
        # 確保股票代碼為大寫
        if 'stock_code' in data:
            data['stock_code'] = data['stock_code'].upper()
        
        # 確保交易類型為大寫
        if 'transaction_type' in data:
            data['transaction_type'] = data['transaction_type'].upper()
        
        return data

class TransactionUpdateSchema(Schema):
    """更新交易記錄Schema"""
    
    stock_code = fields.Str(
        validate=[
            validate.Length(min=1, max=20, error='股票代碼長度必須在1-20字符之間'),
            validate.Regexp(r'^[A-Z0-9.]+$', error='股票代碼只能包含大寫字母、數字和點號')
        ]
    )
    
    transaction_type = fields.Str(
        validate=validate.OneOf(['buy', 'sell', 'BUY', 'SELL'], error='交易類型必須是buy或sell')
    )
    
    transaction_date = fields.Date()
    
    price = fields.Decimal(
        places=4,
        validate=validate.Range(min=0.0001, error='價格必須大於0')
    )
    
    shares = fields.Decimal(
        places=4,
        validate=validate.Range(min=0.0001, error='股數必須大於0')
    )
    
    commission = fields.Decimal(
        places=2,
        validate=validate.Range(min=0, error='手續費不能為負數')
    )
    
    notes = fields.Str(
        validate=validate.Length(max=500, error='備註長度不能超過500字符'),
        allow_none=True
    )
    
    @validates('transaction_date')
    def validate_transaction_date(self, value, **kwargs):
        """驗證交易日期"""
        if value and value > date.today():
            raise ValidationError('交易日期不能是未來日期')
        return value
    
    @post_load
    def process_data(self, data, **kwargs):
        """處理加載後的數據"""
        # 確保股票代碼為大寫
        if 'stock_code' in data:
            data['stock_code'] = data['stock_code'].upper()
        
        # 確保交易類型為大寫
        if 'transaction_type' in data:
            data['transaction_type'] = data['transaction_type'].upper()
        
        return data