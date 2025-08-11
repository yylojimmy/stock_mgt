# -*- coding: utf-8 -*-
"""
股票管理系統 - 股價API路由

提供股票價格獲取和更新API。
"""

from flask import request, jsonify
from . import api_bp

@api_bp.route('/prices/current', methods=['GET'])
def get_current_prices():
    """獲取當前股價"""
    return jsonify({
        'success': True,
        'data': [],
        'message': '當前股價API - 開發中'
    })

@api_bp.route('/prices/refresh', methods=['POST'])
def refresh_prices():
    """刷新股價"""
    return jsonify({
        'success': True,
        'message': '刷新股價API - 開發中'
    })

@api_bp.route('/prices/<stock_code>', methods=['GET'])
def get_stock_price(stock_code):
    """獲取特定股票價格"""
    return jsonify({
        'success': True,
        'data': {
            'stock_code': stock_code,
            'current_price': 0,
            'change': 0,
            'change_percent': 0
        },
        'message': '股票價格API - 開發中'
    })