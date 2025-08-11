# -*- coding: utf-8 -*-
"""
股票管理系統 - 股票API路由

提供股票基本信息的CRUD操作API。
"""

from flask import request, jsonify
from sqlalchemy.exc import IntegrityError
from datetime import datetime
from decimal import Decimal
from marshmallow import ValidationError
from werkzeug.exceptions import BadRequest, UnsupportedMediaType

from . import api_bp
from database import session_scope
from models import Stock
from schemas.stock_schema import StockSchema, StockCreateSchema, StockUpdateSchema

# 初始化序列化器
stock_schema = StockSchema()
stocks_schema = StockSchema(many=True)
stock_create_schema = StockCreateSchema()
stock_update_schema = StockUpdateSchema()

@api_bp.route('/stocks', methods=['GET'])
def get_stocks():
    """獲取所有股票列表"""
    try:
        # 獲取查詢參數
        page = request.args.get('page', 1, type=int)
        per_page = min(request.args.get('per_page', 20, type=int), 100)
        market = request.args.get('market')
        search = request.args.get('search')
        
        with session_scope() as session:
            # 構建查詢
            query = session.query(Stock)
            
            # 按市場篩選
            if market:
                query = query.filter(Stock.market == market)
            
            # 按名稱或代碼搜索
            if search:
                search_term = f'%{search}%'
                query = query.filter(
                    (Stock.stock_name.like(search_term)) |
                    (Stock.stock_code.like(search_term))
                )
            
            # 排序
            query = query.order_by(Stock.stock_code)
            
            # 分頁
            total = query.count()
            stocks = query.offset((page - 1) * per_page).limit(per_page).all()
            
            # 計算額外信息
            stocks_data = []
            for stock in stocks:
                stock_dict = stock.to_dict()
                stock_dict.update({
                    'market_value': stock.calculate_market_value(),
                    'profit_loss': stock.calculate_profit_loss(),
                    'profit_loss_rate': stock.calculate_profit_loss_rate()
                })
                stocks_data.append(stock_dict)
            
            return jsonify({
                'success': True,
                'data': stocks_data,
                'pagination': {
                    'page': page,
                    'per_page': per_page,
                    'total': total,
                    'pages': ((total + per_page - 1) // per_page) if per_page else 0
                }
            })
            
    except Exception as e:
        return jsonify({
            'success': False,
            'error': '獲取股票列表失敗',
            'message': str(e)
        }), 500

@api_bp.route('/stocks/<stock_code>', methods=['GET'])
def get_stock(stock_code):
    """獲取特定股票詳情"""
    try:
        with session_scope() as session:
            stock = session.query(Stock).filter(Stock.stock_code == stock_code).first()
            
            if not stock:
                return jsonify({
                    'success': False,
                    'error': '股票不存在',
                    'message': f'股票代碼 {stock_code} 不存在'
                }), 404
            
            # 獲取詳細信息
            stock_dict = stock.to_dict()
            stock_dict.update({
                'market_value': stock.calculate_market_value(),
                'profit_loss': stock.calculate_profit_loss(),
                'profit_loss_rate': stock.calculate_profit_loss_rate(),
                'transaction_count': len(stock.transactions),
                'dividend_count': len(stock.dividends)
            })
            
            return jsonify({
                'success': True,
                'data': stock_dict
            })
            
    except Exception as e:
        return jsonify({
            'success': False,
            'error': '獲取股票詳情失敗',
            'message': str(e)
        }), 500

@api_bp.route('/stocks', methods=['POST'])
def create_stock():
    """創建新股票記錄"""
    try:
        # 驗證請求數據
        try:
            json_data = request.get_json(force=True)
        except BadRequest as e:
            if 'JSON' in str(e.description):
                return jsonify({
                    'success': False,
                    'error': 'JSON格式錯誤',
                    'message': 'JSON格式錯誤，請檢查請求數據格式'
                }), 400
            else:
                return jsonify({
                    'success': False,
                    'error': '請求錯誤',
                    'message': str(e.description)
                }), 400
        except UnsupportedMediaType as e:
            return jsonify({
                'success': False,
                'error': 'Content-Type錯誤',
                'message': '請求Content-Type必須為application/json'
            }), 400
        
        if not json_data:
            return jsonify({
                'success': False,
                'error': '無效的請求數據',
                'message': '請提供JSON格式的數據'
            }), 400
        
        # 數據驗證
        errors = stock_create_schema.validate(json_data)
        if errors:
            return jsonify({
                'success': False,
                'error': '數據驗證失敗',
                'message': errors
            }), 400
        
        with session_scope() as session:
            # 檢查股票是否已存在
            existing_stock = session.query(Stock).filter(
                Stock.stock_code == json_data['stock_code']
            ).first()
            
            if existing_stock:
                return jsonify({
                    'success': False,
                    'error': '股票已存在',
                    'message': f'股票代碼 {json_data["stock_code"]} 已存在'
                }), 409
            
            # 創建新股票
            stock = Stock(
                stock_code=json_data['stock_code'],
                stock_name=json_data['stock_name'],
                market=json_data['market'],
                currency=json_data.get('currency', 'CNY'),
                current_price=Decimal(str(json_data.get('current_price', 0))),
                price_update_time=datetime.utcnow() if json_data.get('current_price') else None
            )
            
            session.add(stock)
            session.commit()
            
            return jsonify({
                'success': True,
                'data': stock.to_dict(),
                'message': '股票創建成功'
            }), 201
            
    except ValidationError as e:
        return jsonify({
            'success': False,
            'error': '數據驗證失敗',
            'message': e.messages
        }), 400
    except IntegrityError as e:
        return jsonify({
            'success': False,
            'error': '數據完整性錯誤',
            'message': '股票代碼已存在或數據格式錯誤'
        }), 409
    except Exception as e:
        return jsonify({
            'success': False,
            'error': '創建股票失敗',
            'message': str(e)
        }), 500

@api_bp.route('/stocks/<stock_code>', methods=['PUT'])
def update_stock(stock_code):
    """更新股票信息"""
    try:
        # 驗證請求數據
        json_data = request.get_json()
        if not json_data:
            return jsonify({
                'success': False,
                'error': '無效的請求數據',
                'message': '請提供JSON格式的數據'
            }), 400
        
        # 數據驗證
        errors = stock_update_schema.validate(json_data)
        if errors:
            return jsonify({
                'success': False,
                'error': '數據驗證失敗',
                'message': errors
            }), 400
        
        with session_scope() as session:
            stock = session.query(Stock).filter(Stock.stock_code == stock_code).first()
            
            if not stock:
                return jsonify({
                    'success': False,
                    'error': '股票不存在',
                    'message': f'股票代碼 {stock_code} 不存在'
                }), 404
            
            # 更新股票信息
            if 'stock_name' in json_data:
                stock.stock_name = json_data['stock_name']
            if 'market' in json_data:
                stock.market = json_data['market']
            if 'currency' in json_data:
                stock.currency = json_data['currency']
            if 'current_price' in json_data:
                stock.current_price = Decimal(str(json_data['current_price']))
                stock.price_update_time = datetime.utcnow()
            
            stock.updated_at = datetime.utcnow()
            session.commit()
            
            return jsonify({
                'success': True,
                'data': stock.to_dict(),
                'message': '股票信息更新成功'
            })
            
    except Exception as e:
        return jsonify({
            'success': False,
            'error': '更新股票失敗',
            'message': str(e)
        }), 500

@api_bp.route('/stocks/<stock_code>', methods=['DELETE'])
def delete_stock(stock_code):
    """刪除股票記錄"""
    try:
        with session_scope() as session:
            stock = session.query(Stock).filter(Stock.stock_code == stock_code).first()
            
            if not stock:
                return jsonify({
                    'success': False,
                    'error': '股票不存在',
                    'message': f'股票代碼 {stock_code} 不存在'
                }), 404
            
            # 檢查是否有關聯的交易記錄
            if stock.transactions:
                return jsonify({
                    'success': False,
                    'error': '無法刪除股票',
                    'message': f'股票 {stock_code} 存在交易記錄，請先刪除相關交易記錄'
                }), 409
            
            # 檢查是否有關聯的股息記錄
            if stock.dividends:
                return jsonify({
                    'success': False,
                    'error': '無法刪除股票',
                    'message': f'股票 {stock_code} 存在股息記錄，請先刪除相關股息記錄'
                }), 409
            
            session.delete(stock)
            session.commit()
            
            return jsonify({
                'success': True,
                'message': f'股票 {stock_code} 刪除成功'
            })
            
    except Exception as e:
        return jsonify({
            'success': False,
            'error': '刪除股票失敗',
            'message': str(e)
        }), 500

@api_bp.route('/stocks/search', methods=['GET'])
def search_stocks():
    """股票代碼搜索和自動補全"""
    try:
        query_term = request.args.get('q', '').strip()
        limit = min(request.args.get('limit', 10, type=int), 50)
        
        if not query_term:
            return jsonify({
                'success': True,
                'data': []
            })
        
        with session_scope() as session:
            # 搜索股票代碼和名稱
            search_term = f'%{query_term}%'
            stocks = session.query(Stock).filter(
                (Stock.stock_code.like(search_term)) |
                (Stock.stock_name.like(search_term))
            ).limit(limit).all()
            
            # 格式化搜索結果
            results = []
            for stock in stocks:
                results.append({
                    'stock_code': stock.stock_code,
                    'stock_name': stock.stock_name,
                    'market': stock.market,
                    'current_price': float(stock.current_price) if stock.current_price else 0,
                    'display_text': f'{stock.stock_code} - {stock.stock_name}'
                })
            
            return jsonify({
                'success': True,
                'data': results,
                'query': query_term
            })
            
    except Exception as e:
        return jsonify({
            'success': False,
            'error': '搜索失敗',
            'message': str(e)
        }), 500