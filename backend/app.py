# -*- coding: utf-8 -*-
"""
股票管理系統 - Flask主應用

這是股票管理系統的主要Flask應用文件，負責：
- 應用初始化和配置
- 路由註冊
- 數據庫初始化
- CORS配置
- 中間件註冊
"""

from flask import Flask, jsonify
from flask_cors import CORS
import os
from datetime import datetime

# 導入配置
from config import get_config

# 導入數據庫管理器
from database import init_database

# 導入API路由
from api import api_bp

# 導入中間件
from middleware import register_error_handlers

def create_app(config_name=None):
    """應用工廠函數"""
    # 創建Flask應用實例
    app = Flask(__name__)
    
    # 加載配置
    if config_name is None:
        config_name = os.environ.get('FLASK_ENV', 'development')
    
    config_class = get_config()
    app.config.from_object(config_class)
    
    # 初始化數據庫
    init_database(
        database_url=app.config.get('SQLALCHEMY_DATABASE_URI'),
        echo=app.config.get('DEBUG', False)
    )
    
    # 配置CORS
    CORS(app, origins=app.config.get('CORS_ORIGINS', '*'))
    
    # 註冊中間件
    register_error_handlers(app)
    
    # 註冊藍圖
    app.register_blueprint(api_bp)
    
    return app

# 創建應用實例
app = create_app()

# 基本路由
@app.route('/')
def index():
    """首頁路由 - 返回API狀態信息"""
    return jsonify({
        'message': '股票管理系統API',
        'version': '1.0.0',
        'status': 'running',
        'timestamp': datetime.now().isoformat()
    })

@app.route('/api/health')
def health_check():
    """健康檢查端點"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat()
    })

# 錯誤處理
@app.errorhandler(404)
def not_found(error):
    """處理404錯誤"""
    return jsonify({
        'error': 'Not Found',
        'message': '請求的資源不存在',
        'status_code': 404
    }), 404

@app.errorhandler(500)
def internal_error(error):
    """處理500錯誤"""
    return jsonify({
        'error': 'Internal Server Error',
        'message': '服務器內部錯誤',
        'status_code': 500
    }), 500

if __name__ == '__main__':
    # 確保數據庫表存在
    from database import get_db_manager
    db_manager = get_db_manager()
    db_manager.create_tables()
    
    # 啟動開發服務器
    app.run(
        host='0.0.0.0',
        port=5001,  # 使用指定的後端端口
        debug=True
    )