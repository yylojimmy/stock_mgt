# -*- coding: utf-8 -*-
"""
股票管理系統 - 股息記錄API路由

提供股息記錄的CRUD操作API。
"""

from flask import request, jsonify
from sqlalchemy.exc import IntegrityError
from sqlalchemy import desc
from datetime import datetime
from decimal import Decimal

from . import api_bp
from database import session_scope
from models import Dividend, Stock
from schemas.dividend_schema import DividendSchema, DividendCreateSchema, DividendUpdateSchema
from middleware.error_handler import ValidationException, NotFoundException, DatabaseException

# 初始化序列化器
dividend_schema = DividendSchema()
dividends_schema = DividendSchema(many=True)
dividend_create_schema = DividendCreateSchema()
dividend_update_schema = DividendUpdateSchema()

@api_bp.route('/dividends', methods=['GET'])
def get_dividends():
    """獲取股息記錄列表"""
    try:
        # 獲取查詢參數
        page = request.args.get('page', 1, type=int)
        per_page = min(request.args.get('per_page', 20, type=int), 100)
        stock_code = request.args.get('stock_code')
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        currency = request.args.get('currency')
        
        with session_scope() as session:
            # 構建查詢
            query = session.query(Dividend)
            
            # 按股票代碼篩選
            if stock_code:
                query = query.filter(Dividend.stock_code == stock_code)
            
            # 按日期範圍篩選
            if start_date:
                try:
                    start_dt = datetime.strptime(start_date, '%Y-%m-%d').date()
                    query = query.filter(Dividend.dividend_date >= start_dt)
                except ValueError:
                    raise ValidationException('開始日期格式錯誤，請使用YYYY-MM-DD格式')
            
            if end_date:
                try:
                    end_dt = datetime.strptime(end_date, '%Y-%m-%d').date()
                    query = query.filter(Dividend.dividend_date <= end_dt)
                except ValueError:
                    raise ValidationException('結束日期格式錯誤，請使用YYYY-MM-DD格式')
            
            # 按幣種篩選
            if currency:
                query = query.filter(Dividend.currency == currency)
            
            # 按股息日期倒序排列
            query = query.order_by(desc(Dividend.dividend_date), desc(Dividend.created_at))
            
            # 分頁
            total = query.count()
            dividends = query.offset((page - 1) * per_page).limit(per_page).all()
            
            # 序列化數據
            result = dividends_schema.dump(dividends)
            
            return jsonify({
                'success': True,
                'data': result,
                'pagination': {
                    'page': page,
                    'per_page': per_page,
                    'total': total,
                    'pages': ((total + per_page - 1) // per_page) if per_page else 0
                }
            })
            
    except ValidationException as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 400
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'獲取股息記錄失敗: {str(e)}'
        }), 500

@api_bp.route('/dividends/<int:dividend_id>', methods=['GET'])
def get_dividend(dividend_id):
    """獲取單個股息記錄詳情"""
    try:
        with session_scope() as session:
            dividend = session.query(Dividend).filter(
                Dividend.dividend_id == dividend_id
            ).first()
            
            if not dividend:
                raise NotFoundException(f'股息記錄 {dividend_id} 不存在')
            
            result = dividend_schema.dump(dividend)
            
            return jsonify({
                'success': True,
                'data': result
            })
            
    except NotFoundException as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 404
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'獲取股息記錄失敗: {str(e)}'
        }), 500

@api_bp.route('/dividends', methods=['POST'])
def create_dividend():
    """創建股息記錄"""
    try:
        # 驗證請求數據
        json_data = request.get_json()
        if not json_data:
            raise ValidationException('請求數據不能為空')
        
        # 數據驗證
        validated_data = dividend_create_schema.load(json_data)
        
        with session_scope() as session:
            # 檢查股票是否存在
            stock = session.query(Stock).filter(
                Stock.stock_code == validated_data['stock_code']
            ).first()
            
            if not stock:
                raise NotFoundException(f'股票 {validated_data["stock_code"]} 不存在')
            
            # 創建股息記錄
            dividend = Dividend(
                stock_code=validated_data['stock_code'],
                dividend_date=validated_data['dividend_date'],
                dividend_per_share=Decimal(str(validated_data['dividend_per_share'])),
                total_dividend=Decimal(str(validated_data['total_dividend'])),
                tax_amount=Decimal(str(validated_data.get('tax_amount', 0))),
                net_dividend=Decimal(str(validated_data['total_dividend'])) - Decimal(str(validated_data.get('tax_amount', 0))),
                currency=validated_data.get('currency', 'HKD'),
                notes=validated_data.get('notes')
            )
            
            session.add(dividend)
            session.commit()
            
            # 返回創建的股息記錄
            result = dividend_schema.dump(dividend)
            
            return jsonify({
                'success': True,
                'data': result,
                'message': '股息記錄創建成功'
            }), 201
            
    except ValidationException as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 400
    except NotFoundException as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 404
    except IntegrityError as e:
        return jsonify({
            'success': False,
            'message': '數據完整性錯誤，請檢查輸入數據'
        }), 400
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'創建股息記錄失敗: {str(e)}'
        }), 500

@api_bp.route('/dividends/<int:dividend_id>', methods=['PUT'])
def update_dividend(dividend_id):
    """更新股息記錄"""
    try:
        # 驗證請求數據
        json_data = request.get_json()
        if not json_data:
            raise ValidationException('請求數據不能為空')
        
        # 數據驗證
        validated_data = dividend_update_schema.load(json_data)
        
        with session_scope() as session:
            # 查找股息記錄
            dividend = session.query(Dividend).filter(
                Dividend.dividend_id == dividend_id
            ).first()
            
            if not dividend:
                raise NotFoundException(f'股息記錄 {dividend_id} 不存在')
            
            # 更新股息記錄
            for field, value in validated_data.items():
                if field in ['dividend_per_share', 'total_dividend', 'tax_amount'] and value is not None:
                    setattr(dividend, field, Decimal(str(value)))
                elif field == 'net_dividend':
                    # net_dividend 會自動計算，不直接設置
                    continue
                elif value is not None:
                    setattr(dividend, field, value)
            
            # 重新計算淨股息
            dividend.net_dividend = dividend.total_dividend - dividend.tax_amount
            dividend.updated_at = datetime.utcnow()
            
            session.commit()
            
            # 返回更新後的股息記錄
            result = dividend_schema.dump(dividend)
            
            return jsonify({
                'success': True,
                'data': result,
                'message': '股息記錄更新成功'
            })
            
    except ValidationException as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 400
    except NotFoundException as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 404
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'更新股息記錄失敗: {str(e)}'
        }), 500

@api_bp.route('/dividends/<int:dividend_id>', methods=['DELETE'])
def delete_dividend(dividend_id):
    """刪除股息記錄"""
    try:
        with session_scope() as session:
            # 查找股息記錄
            dividend = session.query(Dividend).filter(
                Dividend.dividend_id == dividend_id
            ).first()
            
            if not dividend:
                raise NotFoundException(f'股息記錄 {dividend_id} 不存在')
            
            # 刪除股息記錄
            session.delete(dividend)
            session.commit()
            
            return jsonify({
                'success': True,
                'message': '股息記錄刪除成功'
            })
            
    except NotFoundException as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 404
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'刪除股息記錄失敗: {str(e)}'
        }), 500

@api_bp.route('/dividends/stats', methods=['GET'])
def get_dividend_stats():
    """獲取股息統計信息"""
    try:
        stock_code = request.args.get('stock_code')
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        currency = request.args.get('currency')
        
        with session_scope() as session:
            # 構建查詢
            query = session.query(Dividend)
            
            if stock_code:
                query = query.filter(Dividend.stock_code == stock_code)
            
            if start_date:
                try:
                    start_dt = datetime.strptime(start_date, '%Y-%m-%d').date()
                    query = query.filter(Dividend.dividend_date >= start_dt)
                except ValueError:
                    raise ValidationException('開始日期格式錯誤，請使用YYYY-MM-DD格式')
            
            if end_date:
                try:
                    end_dt = datetime.strptime(end_date, '%Y-%m-%d').date()
                    query = query.filter(Dividend.dividend_date <= end_dt)
                except ValueError:
                    raise ValidationException('結束日期格式錯誤，請使用YYYY-MM-DD格式')
            
            if currency:
                query = query.filter(Dividend.currency == currency)
            
            dividends = query.all()
            
            # 計算統計數據
            total_dividends = len(dividends)
            total_gross_dividend = sum(d.total_dividend for d in dividends)
            total_tax_amount = sum(d.tax_amount for d in dividends)
            total_net_dividend = sum(d.net_dividend for d in dividends)
            
            # 按幣種分組統計
            currency_stats = {}
            for dividend in dividends:
                curr = dividend.currency
                if curr not in currency_stats:
                    currency_stats[curr] = {
                        'count': 0,
                        'total_gross': 0,
                        'total_tax': 0,
                        'total_net': 0
                    }
                
                currency_stats[curr]['count'] += 1
                currency_stats[curr]['total_gross'] += float(dividend.total_dividend)
                currency_stats[curr]['total_tax'] += float(dividend.tax_amount)
                currency_stats[curr]['total_net'] += float(dividend.net_dividend)
            
            # 按股票分組統計
            stock_stats = {}
            for dividend in dividends:
                stock_code = dividend.stock_code
                if stock_code not in stock_stats:
                    stock_stats[stock_code] = {
                        'stock_code': stock_code,
                        'count': 0,
                        'total_dividend': 0,
                        'total_tax': 0,
                        'net_dividend': 0
                    }
                
                stock_stats[stock_code]['count'] += 1
                stock_stats[stock_code]['total_dividend'] += float(dividend.total_dividend)
                stock_stats[stock_code]['total_tax'] += float(dividend.tax_amount)
                stock_stats[stock_code]['net_dividend'] += float(dividend.net_dividend)
            
            # 按月份分組統計（月度趨勢）
            monthly_stats = {}
            for dividend in dividends:
                month_key = dividend.dividend_date.strftime('%Y-%m')
                if month_key not in monthly_stats:
                    monthly_stats[month_key] = {
                        'month': month_key,
                        'count': 0,
                        'total_dividend': 0,
                        'total_tax': 0,
                        'net_dividend': 0
                    }
                
                monthly_stats[month_key]['count'] += 1
                monthly_stats[month_key]['total_dividend'] += float(dividend.total_dividend)
                monthly_stats[month_key]['total_tax'] += float(dividend.tax_amount)
                monthly_stats[month_key]['net_dividend'] += float(dividend.net_dividend)
            
            # 轉換幣種統計格式
            by_currency = {}
            for curr, data in currency_stats.items():
                by_currency[curr] = {
                    'total_dividend': data['total_gross'],
                    'total_tax': data['total_tax'],
                    'net_dividend': data['total_net'],
                    'count': data['count']
                }
            
            stats = {
                'total_records': total_dividends,
                'total_dividend': float(total_gross_dividend),
                'total_tax': float(total_tax_amount),
                'net_dividend': float(total_net_dividend),
                'by_currency': by_currency,
                'by_stock': list(stock_stats.values()),
                'monthly_trend': list(monthly_stats.values())
            }
            
            return jsonify({
                'success': True,
                'data': stats
            })
            
    except ValidationException as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 400
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'獲取股息統計失敗: {str(e)}'
        }), 500