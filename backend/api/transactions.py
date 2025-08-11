# -*- coding: utf-8 -*-
"""
股票管理系統 - 交易記錄API路由

提供交易記錄的CRUD操作API。
"""

from flask import request, jsonify
from sqlalchemy.exc import IntegrityError
from sqlalchemy import desc
from datetime import datetime
from decimal import Decimal
from marshmallow import ValidationError

from . import api_bp
from database import session_scope
from models import Transaction, Stock
from schemas.transaction_schema import TransactionSchema, TransactionCreateSchema, TransactionUpdateSchema
from middleware.error_handler import ValidationException, NotFoundException, DatabaseException

# 初始化序列化器
transaction_schema = TransactionSchema()
transactions_schema = TransactionSchema(many=True)
transaction_create_schema = TransactionCreateSchema()
transaction_update_schema = TransactionUpdateSchema()

@api_bp.route('/transactions', methods=['GET'])
def get_transactions():
    """獲取交易記錄列表"""
    try:
        # 獲取查詢參數
        page = request.args.get('page', 1, type=int)
        per_page = min(request.args.get('per_page', 20, type=int), 100)
        stock_code = request.args.get('stock_code')
        transaction_type = request.args.get('transaction_type')
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        
        with session_scope() as session:
            # 構建查詢
            query = session.query(Transaction)
            
            # 按股票代碼篩選
            if stock_code:
                query = query.filter(Transaction.stock_code == stock_code)
            
            # 按交易類型篩選（轉換為大寫以匹配數據庫）
            if transaction_type:
                transaction_type = transaction_type.upper()
                query = query.filter(Transaction.transaction_type == transaction_type)
            
            # 按日期範圍篩選
            if start_date:
                try:
                    start_dt = datetime.strptime(start_date, '%Y-%m-%d').date()
                    query = query.filter(Transaction.transaction_date >= start_dt)
                except ValueError:
                    raise ValidationException('開始日期格式錯誤，請使用YYYY-MM-DD格式')
            
            if end_date:
                try:
                    end_dt = datetime.strptime(end_date, '%Y-%m-%d').date()
                    query = query.filter(Transaction.transaction_date <= end_dt)
                except ValueError:
                    raise ValidationException('結束日期格式錯誤，請使用YYYY-MM-DD格式')
            
            # 按交易日期倒序排列
            query = query.order_by(desc(Transaction.transaction_date), desc(Transaction.created_at))
            
            # 分頁
            total = query.count()
            transactions = query.offset((page - 1) * per_page).limit(per_page).all()
            
            # 序列化數據
            result = transactions_schema.dump(transactions)
            
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
            'message': f'獲取交易記錄失敗: {str(e)}'
        }), 500

@api_bp.route('/transactions/<int:transaction_id>', methods=['GET'])
def get_transaction(transaction_id):
    """獲取單個交易記錄詳情"""
    try:
        with session_scope() as session:
            transaction = session.query(Transaction).filter(
                Transaction.id == transaction_id
            ).first()
            
            if not transaction:
                raise NotFoundException(f'交易記錄 {transaction_id} 不存在')
            
            result = transaction_schema.dump(transaction)
            
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
            'message': f'獲取交易記錄失敗: {str(e)}'
        }), 500

@api_bp.route('/transactions', methods=['POST'])
def create_transaction():
    """創建交易記錄"""
    try:
        # 驗證請求數據
        json_data = request.get_json()
        if not json_data:
            raise ValidationException('請求數據不能為空')
        
        # 數據驗證
        validated_data = transaction_create_schema.load(json_data)
        
        with session_scope() as session:
            # 檢查股票是否存在
            stock = session.query(Stock).filter(
                Stock.stock_code == validated_data['stock_code']
            ).first()
            
            if not stock:
                raise NotFoundException(f'股票 {validated_data["stock_code"]} 不存在')
            
            # 創建交易記錄
            transaction = Transaction(
                stock_code=validated_data['stock_code'],
                transaction_type=validated_data['transaction_type'],
                transaction_date=validated_data['transaction_date'],
                price=Decimal(str(validated_data['price'])),
                shares=Decimal(str(validated_data['shares'])),
                total_amount=Decimal(str(validated_data['price'])) * Decimal(str(validated_data['shares'])),
                commission=Decimal(str(validated_data.get('commission', 0))),
                notes=validated_data.get('notes')
            )
            
            session.add(transaction)
            session.flush()  # 獲取ID
            
            # 更新股票持倉信息
            if validated_data['transaction_type'] == 'buy':
                # 買入：更新平均成本和持股數量
                total_cost = stock.avg_cost * stock.total_shares
                new_cost = transaction.price * transaction.shares + transaction.commission
                new_shares = stock.total_shares + transaction.shares
                
                if new_shares > 0:
                    stock.avg_cost = (total_cost + new_cost) / new_shares
                stock.total_shares = new_shares
                
            elif validated_data['transaction_type'] == 'sell':
                # 賣出：減少持股數量
                if stock.total_shares < transaction.shares:
                    raise ValidationException('賣出股數不能超過持有股數')
                
                stock.total_shares -= transaction.shares
                
                # 如果全部賣出，重置平均成本
                if stock.total_shares == 0:
                    stock.avg_cost = Decimal('0')
            
            stock.updated_at = datetime.utcnow()
            
            session.commit()
            
            # 返回創建的交易記錄
            result = transaction_schema.dump(transaction)
            
            return jsonify({
                'success': True,
                'data': result,
                'message': '交易記錄創建成功'
            }), 201
            
    except ValidationError as e:
        return jsonify({
            'success': False,
            'message': f'數據驗證失敗: {e.messages}'
        }), 400
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
            'message': f'創建交易記錄失敗: {str(e)}'
        }), 500

@api_bp.route('/transactions/<int:transaction_id>', methods=['PUT'])
def update_transaction(transaction_id):
    """更新交易記錄"""
    try:
        # 驗證請求數據
        json_data = request.get_json()
        if not json_data:
            raise ValidationException('請求數據不能為空')
        
        # 數據驗證
        validated_data = transaction_update_schema.load(json_data)
        
        with session_scope() as session:
            # 查找交易記錄
            transaction = session.query(Transaction).filter(
                Transaction.id == transaction_id
            ).first()
            
            if not transaction:
                raise NotFoundException(f'交易記錄 {transaction_id} 不存在')
            
            # 保存原始數據用於回滾股票信息
            original_stock_code = transaction.stock_code
            original_type = transaction.transaction_type
            original_shares = transaction.shares
            original_price = transaction.price
            original_commission = transaction.commission
            
            # 獲取相關股票
            stock = session.query(Stock).filter(
                Stock.stock_code == original_stock_code
            ).first()
            
            if not stock:
                raise NotFoundException(f'股票 {original_stock_code} 不存在')
            
            # 先回滾原交易對股票的影響
            if original_type == 'buy':
                # 回滾買入：減少持股，重新計算平均成本
                if stock.total_shares >= original_shares:
                    total_cost = stock.avg_cost * stock.total_shares
                    original_cost = original_price * original_shares + original_commission
                    new_shares = stock.total_shares - original_shares
                    
                    if new_shares > 0:
                        stock.avg_cost = (total_cost - original_cost) / new_shares
                    else:
                        stock.avg_cost = Decimal('0')
                    
                    stock.total_shares = new_shares
                    
            elif original_type == 'sell':
                # 回滾賣出：增加持股
                stock.total_shares += original_shares
            
            # 更新交易記錄
            for field, value in validated_data.items():
                if field in ['price', 'shares', 'commission'] and value is not None:
                    setattr(transaction, field, Decimal(str(value)))
                elif field == 'total_amount':
                    # total_amount 會自動計算，不直接設置
                    continue
                elif value is not None:
                    setattr(transaction, field, value)
            
            # 重新計算總金額
            transaction.total_amount = transaction.price * transaction.shares
            
            # 應用新交易對股票的影響
            if transaction.transaction_type == 'buy':
                # 新買入
                total_cost = stock.avg_cost * stock.total_shares
                new_cost = transaction.price * transaction.shares + transaction.commission
                new_shares = stock.total_shares + transaction.shares
                
                if new_shares > 0:
                    stock.avg_cost = (total_cost + new_cost) / new_shares
                stock.total_shares = new_shares
                
            elif transaction.transaction_type == 'sell':
                # 新賣出
                if stock.total_shares < transaction.shares:
                    raise ValidationException('賣出股數不能超過持有股數')
                
                stock.total_shares -= transaction.shares
                
                if stock.total_shares == 0:
                    stock.avg_cost = Decimal('0')
            
            stock.updated_at = datetime.utcnow()
            
            session.commit()
            
            # 返回更新後的交易記錄
            result = transaction_schema.dump(transaction)
            
            return jsonify({
                'success': True,
                'data': result,
                'message': '交易記錄更新成功'
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
            'message': f'更新交易記錄失敗: {str(e)}'
        }), 500

@api_bp.route('/transactions/<int:transaction_id>', methods=['DELETE'])
def delete_transaction(transaction_id):
    """刪除交易記錄"""
    try:
        with session_scope() as session:
            # 查找交易記錄
            transaction = session.query(Transaction).filter(
                Transaction.id == transaction_id
            ).first()
            
            if not transaction:
                raise NotFoundException(f'交易記錄 {transaction_id} 不存在')
            
            # 獲取相關股票
            stock = session.query(Stock).filter(
                Stock.stock_code == transaction.stock_code
            ).first()
            
            if stock:
                # 回滾交易對股票的影響
                if transaction.transaction_type == 'buy':
                    # 回滾買入：減少持股，重新計算平均成本
                    if stock.total_shares >= transaction.shares:
                        total_cost = stock.avg_cost * stock.total_shares
                        transaction_cost = transaction.price * transaction.shares + transaction.commission
                        new_shares = stock.total_shares - transaction.shares
                        
                        if new_shares > 0:
                            stock.avg_cost = (total_cost - transaction_cost) / new_shares
                        else:
                            stock.avg_cost = Decimal('0')
                        
                        stock.total_shares = new_shares
                        
                elif transaction.transaction_type == 'sell':
                    # 回滾賣出：增加持股
                    stock.total_shares += transaction.shares
                
                stock.updated_at = datetime.utcnow()
            
            # 刪除交易記錄
            session.delete(transaction)
            session.commit()
            
            return jsonify({
                'success': True,
                'message': '交易記錄刪除成功'
            })
            
    except NotFoundException as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 404
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'刪除交易記錄失敗: {str(e)}'
        }), 500

@api_bp.route('/transactions/stats', methods=['GET'])
def get_transaction_stats():
    """獲取交易統計信息"""
    try:
        stock_code = request.args.get('stock_code')
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        
        with session_scope() as session:
            # 構建查詢
            query = session.query(Transaction)
            
            if stock_code:
                query = query.filter(Transaction.stock_code == stock_code)
            
            if start_date:
                try:
                    start_dt = datetime.strptime(start_date, '%Y-%m-%d').date()
                    query = query.filter(Transaction.transaction_date >= start_dt)
                except ValueError:
                    raise ValidationException('開始日期格式錯誤，請使用YYYY-MM-DD格式')
            
            if end_date:
                try:
                    end_dt = datetime.strptime(end_date, '%Y-%m-%d').date()
                    query = query.filter(Transaction.transaction_date <= end_dt)
                except ValueError:
                    raise ValidationException('結束日期格式錯誤，請使用YYYY-MM-DD格式')
            
            transactions = query.all()
            
            # 計算統計數據
            total_transactions = len(transactions)
            buy_count = sum(1 for t in transactions if (t.transaction_type or '').upper() == 'BUY')
            sell_count = sum(1 for t in transactions if (t.transaction_type or '').upper() == 'SELL')
            
            total_buy_amount = sum(t.total_amount for t in transactions if (t.transaction_type or '').upper() == 'BUY')
            total_sell_amount = sum(t.total_amount for t in transactions if (t.transaction_type or '').upper() == 'SELL')
            total_commission = sum(t.commission for t in transactions)
            
            buy_shares = sum(t.shares for t in transactions if (t.transaction_type or '').upper() == 'BUY')
            sell_shares = sum(t.shares for t in transactions if (t.transaction_type or '').upper() == 'SELL')
            
            stats = {
                'total_transactions': total_transactions,
                'buy_count': buy_count,
                'sell_count': sell_count,
                'total_buy_amount': float(total_buy_amount),
                'total_sell_amount': float(total_sell_amount),
                'total_commission': float(total_commission),
                'buy_shares': float(buy_shares),
                'sell_shares': float(sell_shares),
                'net_shares': float(buy_shares - sell_shares),
                'net_amount': float(total_sell_amount - total_buy_amount - total_commission)
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
            'message': f'獲取交易統計失敗: {str(e)}'
        }), 500