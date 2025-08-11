# -*- coding: utf-8 -*-
"""
股票管理系統 - API路由包

包含所有API路由的定義和註冊。
"""

from flask import Blueprint

# 創建API藍圖
api_bp = Blueprint('api', __name__, url_prefix='/api')

# 導入所有路由模塊
from . import stocks
from . import transactions
from . import dividends
from . import portfolio
from . import prices

__all__ = ['api_bp']