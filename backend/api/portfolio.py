# -*- coding: utf-8 -*-
"""
股票管理系統 - 投資組合API路由

提供投資組合分析和統計API。
"""

from flask import request, jsonify
from sqlalchemy import func, desc
from datetime import datetime, date, timedelta
from decimal import Decimal
from collections import defaultdict

from . import api_bp
from database import session_scope
from models import Stock, Transaction, Dividend
from middleware.error_handler import ValidationException, NotFoundException

@api_bp.route('/portfolio/summary', methods=['GET'])
def get_portfolio_summary():
    """獲取投資組合概覽"""
    try:
        with session_scope() as session:
            # 獲取所有持倉股票
            stocks = session.query(Stock).filter(Stock.total_shares > 0).all()
            
            total_market_value = Decimal('0')
            total_cost = Decimal('0')
            total_dividend = Decimal('0')
            holdings_count = len(stocks)
            
            holdings = []
            
            for stock in stocks:
                # 計算市值（使用當前價格或平均成本）
                current_price = stock.current_price or stock.avg_cost
                market_value = current_price * stock.total_shares
                cost_value = stock.avg_cost * stock.total_shares
                
                # 計算盈虧
                unrealized_pnl = market_value - cost_value
                unrealized_pnl_pct = (unrealized_pnl / cost_value * 100) if cost_value > 0 else Decimal('0')
                
                # 獲取該股票的股息總額
                dividend_sum = session.query(func.sum(Dividend.net_dividend)).filter(
                    Dividend.stock_code == stock.stock_code
                ).scalar() or Decimal('0')
                
                total_market_value += market_value
                total_cost += cost_value
                total_dividend += dividend_sum
                
                holdings.append({
                    'stock_code': stock.stock_code,
                    'stock_name': stock.stock_name,
                    'market': stock.market,
                    'shares': float(stock.total_shares),
                    'avg_cost': float(stock.avg_cost),
                    'current_price': float(current_price),
                    'cost_value': float(cost_value),
                    'market_value': float(market_value),
                    'unrealized_pnl': float(unrealized_pnl),
                    'unrealized_pnl_pct': float(unrealized_pnl_pct),
                    'dividend_received': float(dividend_sum),
                    'weight': float((market_value / total_market_value * 100) if total_market_value > 0 else 0)
                })
            
            # 計算總體統計
            total_unrealized_pnl = total_market_value - total_cost
            total_unrealized_pnl_pct = (total_unrealized_pnl / total_cost * 100) if total_cost > 0 else Decimal('0')
            total_return = total_unrealized_pnl + total_dividend
            total_return_pct = (total_return / total_cost * 100) if total_cost > 0 else Decimal('0')
            
            # 重新計算權重
            for holding in holdings:
                holding['weight'] = float((Decimal(str(holding['market_value'])) / total_market_value * 100) if total_market_value > 0 else 0)
            
            summary = {
                'total_market_value': float(total_market_value),
                'total_cost': float(total_cost),
                'total_profit_loss': float(total_unrealized_pnl),
                'total_return_rate': float(total_unrealized_pnl_pct),
                'total_dividend': float(total_dividend),
                'total_return': float(total_return),
                'total_return_pct': float(total_return_pct),
                'holdings_count': holdings_count,
                'holdings': sorted(holdings, key=lambda x: x['market_value'], reverse=True)
            }
            
            return jsonify({
                'success': True,
                'data': summary
            })
            
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'獲取投資組合概覽失敗: {str(e)}'
        }), 500

@api_bp.route('/portfolio/analysis', methods=['GET'])
def get_portfolio_analysis():
    """獲取投資組合分析"""
    try:
        with session_scope() as session:
            # 獲取所有持倉股票
            stocks = session.query(Stock).filter(Stock.total_shares > 0).all()
            
            if not stocks:
                return jsonify({
                    'success': True,
                    'data': {
                        'market_allocation': [],
                        'sector_allocation': [],
                        'top_holdings': []
                    }
                })
            
            total_market_value = Decimal('0')
            market_allocation = defaultdict(Decimal)
            sector_allocation = defaultdict(Decimal)
            holdings = []
            
            for stock in stocks:
                current_price = stock.current_price or stock.avg_cost
                market_value = current_price * stock.total_shares
                total_market_value += market_value
                
                # 按市場分組
                market_allocation[stock.market] += market_value
                
                # 按行業分組（如果有行業信息）
                sector = getattr(stock, 'sector', '其他')
                sector_allocation[sector] += market_value
                
                holdings.append({
                    'stock_code': stock.stock_code,
                    'stock_name': stock.stock_name,
                    'market': stock.market,
                    'market_value': float(market_value),
                    'weight': 0  # 稍後計算
                })
            
            # 計算權重並排序
            for holding in holdings:
                holding['weight'] = float(Decimal(str(holding['market_value'])) / total_market_value * 100)
            
            holdings.sort(key=lambda x: x['market_value'], reverse=True)
            
            # 格式化市場配置
            market_data = []
            for market, value in market_allocation.items():
                market_data.append({
                    'market': market,
                    'value': float(value),
                    'weight': float(value / total_market_value * 100)
                })
            market_data.sort(key=lambda x: x['value'], reverse=True)
            
            # 格式化行業配置
            sector_data = []
            for sector, value in sector_allocation.items():
                sector_data.append({
                    'sector': sector,
                    'value': float(value),
                    'weight': float(value / total_market_value * 100)
                })
            sector_data.sort(key=lambda x: x['value'], reverse=True)
            
            analysis = {
                'total_market_value': float(total_market_value),
                'market_allocation': market_data,
                'sector_allocation': sector_data,
                'top_holdings': holdings[:10]  # 前10大持倉
            }
            
            return jsonify({
                'success': True,
                'data': analysis
            })
            
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'獲取投資組合分析失敗: {str(e)}'
        }), 500

@api_bp.route('/portfolio/performance', methods=['GET'])
def get_portfolio_performance():
    """獲取投資組合績效分析"""
    try:
        # 獲取查詢參數
        period = request.args.get('period', '1y')  # 1m, 3m, 6m, 1y, all
        
        # 計算日期範圍
        end_date = date.today()
        if period == '1m':
            start_date = end_date - timedelta(days=30)
        elif period == '3m':
            start_date = end_date - timedelta(days=90)
        elif period == '6m':
            start_date = end_date - timedelta(days=180)
        elif period == '1y':
            start_date = end_date - timedelta(days=365)
        else:  # all
            start_date = None
        
        with session_scope() as session:
            # 構建交易查詢
            transaction_query = session.query(Transaction)
            dividend_query = session.query(Dividend)
            
            if start_date:
                transaction_query = transaction_query.filter(Transaction.transaction_date >= start_date)
                dividend_query = dividend_query.filter(Dividend.dividend_date >= start_date)
            
            transactions = transaction_query.order_by(Transaction.transaction_date).all()
            dividends = dividend_query.order_by(Dividend.dividend_date).all()
            
            # 計算績效指標
            total_invested = sum(t.total_amount + t.commission for t in transactions if t.transaction_type == 'buy')
            total_sold = sum(t.total_amount - t.commission for t in transactions if t.transaction_type == 'sell')
            total_dividends = sum(d.net_dividend for d in dividends)
            
            # 獲取當前持倉市值
            current_holdings = session.query(Stock).filter(Stock.total_shares > 0).all()
            current_market_value = sum(
                (stock.current_price or stock.avg_cost) * stock.total_shares 
                for stock in current_holdings
            )
            
            net_invested = total_invested - total_sold
            total_return = current_market_value + total_sold + total_dividends - total_invested
            total_return_pct = (total_return / total_invested * 100) if total_invested > 0 else Decimal('0')
            
            # 計算年化收益率（簡化計算）
            if start_date and total_invested > 0:
                days_diff = (end_date - start_date).days
                if days_diff > 0:
                    annualized_return = (total_return_pct * 365 / days_diff)
                else:
                    annualized_return = Decimal('0')
            else:
                annualized_return = Decimal('0')
            
            performance = {
                'period': period,
                'start_date': start_date.strftime('%Y-%m-%d') if start_date else None,
                'end_date': end_date.strftime('%Y-%m-%d'),
                'total_invested': float(total_invested),
                'total_sold': float(total_sold),
                'net_invested': float(net_invested),
                'current_market_value': float(current_market_value),
                'total_dividends': float(total_dividends),
                'total_return': float(total_return),
                'total_return_pct': float(total_return_pct),
                'annualized_return_pct': float(annualized_return),
                'transaction_count': len(transactions),
                'dividend_count': len(dividends)
            }
            
            return jsonify({
                'success': True,
                'data': performance
            })
            
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'獲取投資組合績效失敗: {str(e)}'
        }), 500

@api_bp.route('/portfolio/dividend-analysis', methods=['GET'])
def get_dividend_analysis():
    """獲取股息分析"""
    try:
        # 獲取查詢參數
        year = request.args.get('year', datetime.now().year, type=int)
        
        with session_scope() as session:
            # 獲取指定年份的股息記錄
            start_date = date(year, 1, 1)
            end_date = date(year, 12, 31)
            
            dividends = session.query(Dividend).filter(
                Dividend.dividend_date >= start_date,
                Dividend.dividend_date <= end_date
            ).order_by(Dividend.dividend_date).all()
            
            # 按月份統計
            monthly_dividends = defaultdict(Decimal)
            stock_dividends = defaultdict(Decimal)
            currency_dividends = defaultdict(Decimal)
            
            total_gross = Decimal('0')
            total_tax = Decimal('0')
            total_net = Decimal('0')
            
            for dividend in dividends:
                month_key = dividend.dividend_date.strftime('%Y-%m')
                monthly_dividends[month_key] += dividend.net_dividend
                stock_dividends[dividend.stock_code] += dividend.net_dividend
                currency_dividends[dividend.currency] += dividend.net_dividend
                
                total_gross += dividend.total_dividend
                total_tax += dividend.tax_amount
                total_net += dividend.net_dividend
            
            # 格式化月度數據
            monthly_data = []
            for month in range(1, 13):
                month_key = f"{year}-{month:02d}"
                monthly_data.append({
                    'month': month_key,
                    'amount': float(monthly_dividends.get(month_key, Decimal('0')))
                })
            
            # 格式化股票股息數據
            stock_data = []
            for stock_code, amount in stock_dividends.items():
                # 獲取股票名稱
                stock = session.query(Stock).filter(Stock.stock_code == stock_code).first()
                stock_data.append({
                    'stock_code': stock_code,
                    'stock_name': stock.stock_name if stock else stock_code,
                    'amount': float(amount)
                })
            stock_data.sort(key=lambda x: x['amount'], reverse=True)
            
            # 格式化幣種數據
            currency_data = []
            for currency, amount in currency_dividends.items():
                currency_data.append({
                    'currency': currency,
                    'amount': float(amount)
                })
            currency_data.sort(key=lambda x: x['amount'], reverse=True)
            
            # 計算股息率（基於當前持倉）
            current_holdings = session.query(Stock).filter(Stock.total_shares > 0).all()
            total_market_value = sum(
                (stock.current_price or stock.avg_cost) * stock.total_shares 
                for stock in current_holdings
            )
            
            dividend_yield = (total_net / total_market_value * 100) if total_market_value > 0 else Decimal('0')
            
            analysis = {
                'year': year,
                'total_gross_dividend': float(total_gross),
                'total_tax_amount': float(total_tax),
                'total_net_dividend': float(total_net),
                'dividend_yield_pct': float(dividend_yield),
                'dividend_count': len(dividends),
                'monthly_dividends': monthly_data,
                'stock_dividends': stock_data,
                'currency_dividends': currency_data
            }
            
            return jsonify({
                'success': True,
                'data': analysis
            })
            
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'獲取股息分析失敗: {str(e)}'
        }), 500