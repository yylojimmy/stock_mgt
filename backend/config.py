# -*- coding: utf-8 -*-
"""
股票管理系統 - 配置文件

包含應用的各種配置設置，支持不同環境的配置。
"""

import os
from datetime import timedelta

class Config:
    """基礎配置類"""
    
    # 基本配置
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    
    # 數據庫配置
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_RECORD_QUERIES = True
    
    # API配置
    API_VERSION = '1.0.0'
    API_TITLE = '股票管理系統API'
    
    # 分頁配置
    ITEMS_PER_PAGE = 20
    MAX_ITEMS_PER_PAGE = 100
    
    # 股票數據API配置
    STOCK_API_TIMEOUT = 30  # 秒
    STOCK_DATA_CACHE_TIMEOUT = 300  # 5分鐘緩存
    
    # 定時任務配置
    SCHEDULER_API_ENABLED = True
    SCHEDULER_TIMEZONE = 'Asia/Hong_Kong'
    
    # CORS配置
    CORS_ORIGINS = ['http://localhost:3000', 'http://127.0.0.1:3000']
    
    @staticmethod
    def init_app(app):
        """初始化應用配置"""
        pass

class DevelopmentConfig(Config):
    """開發環境配置"""
    
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = os.environ.get('DEV_DATABASE_URL') or \
        'sqlite:///' + os.path.join(os.path.dirname(__file__), 'data', 'stock_dev.db')
    
    # 開發環境允許所有來源的CORS請求
    CORS_ORIGINS = '*'

class ProductionConfig(Config):
    """生產環境配置"""
    
    DEBUG = False
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///' + os.path.join(os.path.dirname(__file__), 'data', 'stock_prod.db')
    
    # 生產環境的安全配置
    SESSION_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'

class TestingConfig(Config):
    """測試環境配置"""
    
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'  # 內存數據庫
    WTF_CSRF_ENABLED = False

# 配置字典
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}

# 獲取當前配置
def get_config():
    """獲取當前環境的配置"""
    env = os.environ.get('FLASK_ENV', 'development')
    return config.get(env, config['default'])