# -*- coding: utf-8 -*-
"""
股票管理系統 - 中間件包

包含所有中間件的定義和註冊。
"""

from .error_handler import register_error_handlers

__all__ = ['register_error_handlers']