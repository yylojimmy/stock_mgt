# -*- coding: utf-8 -*-
"""
股票管理系統 - 錯誤處理中間件

統一處理應用中的各種錯誤和異常。
"""

from flask import jsonify, request
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from marshmallow import ValidationError
from werkzeug.exceptions import BadRequest
import traceback
import logging

# 設置日誌
logger = logging.getLogger(__name__)

def register_error_handlers(app):
    """註冊錯誤處理器"""
    
    @app.errorhandler(400)
    def bad_request(error):
        """處理400錯誤 - 請求錯誤"""
        return jsonify({
            'success': False,
            'error': 'Bad Request',
            'message': '請求格式錯誤或缺少必要參數',
            'status_code': 400
        }), 400
    
    @app.errorhandler(401)
    def unauthorized(error):
        """處理401錯誤 - 未授權"""
        return jsonify({
            'success': False,
            'error': 'Unauthorized',
            'message': '未授權訪問，請檢查認證信息',
            'status_code': 401
        }), 401
    
    @app.errorhandler(403)
    def forbidden(error):
        """處理403錯誤 - 禁止訪問"""
        return jsonify({
            'success': False,
            'error': 'Forbidden',
            'message': '禁止訪問，權限不足',
            'status_code': 403
        }), 403
    
    @app.errorhandler(404)
    def not_found(error):
        """處理404錯誤 - 資源不存在"""
        return jsonify({
            'success': False,
            'error': 'Not Found',
            'message': '請求的資源不存在',
            'status_code': 404,
            'path': request.path
        }), 404
    
    @app.errorhandler(405)
    def method_not_allowed(error):
        """處理405錯誤 - 方法不允許"""
        return jsonify({
            'success': False,
            'error': 'Method Not Allowed',
            'message': f'請求方法 {request.method} 不被允許',
            'status_code': 405,
            'allowed_methods': list(error.valid_methods) if hasattr(error, 'valid_methods') else []
        }), 405
    
    @app.errorhandler(409)
    def conflict(error):
        """處理409錯誤 - 資源衝突"""
        return jsonify({
            'success': False,
            'error': 'Conflict',
            'message': '資源衝突，請檢查數據是否已存在',
            'status_code': 409
        }), 409
    
    @app.errorhandler(422)
    def unprocessable_entity(error):
        """處理422錯誤 - 無法處理的實體"""
        return jsonify({
            'success': False,
            'error': 'Unprocessable Entity',
            'message': '請求格式正確但語義錯誤',
            'status_code': 422
        }), 422
    
    @app.errorhandler(429)
    def too_many_requests(error):
        """處理429錯誤 - 請求過多"""
        return jsonify({
            'success': False,
            'error': 'Too Many Requests',
            'message': '請求過於頻繁，請稍後再試',
            'status_code': 429
        }), 429
    
    @app.errorhandler(500)
    def internal_server_error(error):
        """處理500錯誤 - 服務器內部錯誤"""
        logger.error(f'服務器內部錯誤: {error}', exc_info=True)
        
        return jsonify({
            'success': False,
            'error': 'Internal Server Error',
            'message': '服務器內部錯誤，請聯繫管理員',
            'status_code': 500
        }), 500
    
    @app.errorhandler(502)
    def bad_gateway(error):
        """處理502錯誤 - 網關錯誤"""
        return jsonify({
            'success': False,
            'error': 'Bad Gateway',
            'message': '網關錯誤，上游服務不可用',
            'status_code': 502
        }), 502
    
    @app.errorhandler(503)
    def service_unavailable(error):
        """處理503錯誤 - 服務不可用"""
        return jsonify({
            'success': False,
            'error': 'Service Unavailable',
            'message': '服務暫時不可用，請稍後再試',
            'status_code': 503
        }), 503
    
    @app.errorhandler(BadRequest)
    def handle_bad_request(error):
        """處理BadRequest錯誤，包括JSON解析錯誤"""
        logger.warning(f'BadRequest錯誤: {error.description}')
        
        # 檢查是否是JSON解析錯誤
        if 'JSON' in str(error.description):
            message = 'JSON格式錯誤，請檢查請求數據格式'
        elif 'Content-Type' in str(error.description):
            message = '請求Content-Type必須為application/json'
        else:
            message = error.description or '請求格式錯誤'
        
        return jsonify({
            'success': False,
            'error': 'Bad Request',
            'message': message,
            'status_code': 400
        }), 400
    
    @app.errorhandler(ValidationError)
    def handle_validation_error(error):
        """處理Marshmallow驗證錯誤"""
        logger.warning(f'數據驗證錯誤: {error.messages}')
        
        return jsonify({
            'success': False,
            'error': 'Validation Error',
            'message': '數據驗證失敗',
            'details': error.messages,
            'status_code': 400
        }), 400
    
    @app.errorhandler(SQLAlchemyError)
    def handle_database_error(error):
        """處理數據庫錯誤"""
        logger.error(f'數據庫錯誤: {error}', exc_info=True)
        
        # 根據錯誤類型返回不同的響應
        if isinstance(error, IntegrityError):
            return jsonify({
                'success': False,
                'error': 'Database Integrity Error',
                'message': '數據完整性錯誤，可能是重複數據或外鍵約束違反',
                'status_code': 409
            }), 409
        
        return jsonify({
            'success': False,
            'error': 'Database Error',
            'message': '數據庫操作失敗，請稍後再試',
            'status_code': 500
        }), 500
    
    @app.errorhandler(ValueError)
    def handle_value_error(error):
        """處理值錯誤"""
        logger.warning(f'值錯誤: {error}')
        
        return jsonify({
            'success': False,
            'error': 'Value Error',
            'message': f'數據值錯誤: {str(error)}',
            'status_code': 400
        }), 400
    
    @app.errorhandler(TypeError)
    def handle_type_error(error):
        """處理類型錯誤"""
        logger.error(f'類型錯誤: {error}', exc_info=True)
        
        return jsonify({
            'success': False,
            'error': 'Type Error',
            'message': '數據類型錯誤',
            'status_code': 400
        }), 400
    
    @app.errorhandler(KeyError)
    def handle_key_error(error):
        """處理鍵錯誤"""
        logger.warning(f'鍵錯誤: {error}')
        
        return jsonify({
            'success': False,
            'error': 'Key Error',
            'message': f'缺少必要的字段: {str(error)}',
            'status_code': 400
        }), 400
    
    @app.errorhandler(Exception)
    def handle_generic_exception(error):
        """處理通用異常"""
        logger.error(f'未處理的異常: {error}', exc_info=True)
        
        # 在開發環境中返回詳細錯誤信息
        if app.debug:
            return jsonify({
                'success': False,
                'error': 'Unhandled Exception',
                'message': str(error),
                'traceback': traceback.format_exc(),
                'status_code': 500
            }), 500
        
        # 在生產環境中返回通用錯誤信息
        return jsonify({
            'success': False,
            'error': 'Internal Server Error',
            'message': '服務器內部錯誤，請聯繫管理員',
            'status_code': 500
        }), 500

def create_error_response(error_type, message, status_code=400, details=None):
    """創建標準錯誤響應"""
    response_data = {
        'success': False,
        'error': error_type,
        'message': message,
        'status_code': status_code
    }
    
    if details:
        response_data['details'] = details
    
    return jsonify(response_data), status_code

def create_success_response(data=None, message=None, status_code=200):
    """創建標準成功響應"""
    response_data = {
        'success': True,
        'status_code': status_code
    }
    
    if data is not None:
        response_data['data'] = data
    
    if message:
        response_data['message'] = message
    
    return jsonify(response_data), status_code

class APIException(Exception):
    """自定義API異常類"""
    
    def __init__(self, message, status_code=400, error_type=None, details=None):
        super().__init__(message)
        self.message = message
        self.status_code = status_code
        self.error_type = error_type or 'API Error'
        self.details = details
    
    def to_dict(self):
        """轉換為字典格式"""
        result = {
            'success': False,
            'error': self.error_type,
            'message': self.message,
            'status_code': self.status_code
        }
        
        if self.details:
            result['details'] = self.details
        
        return result

class ValidationException(APIException):
    """數據驗證異常"""
    
    def __init__(self, message, details=None):
        super().__init__(message, 400, 'Validation Error', details)

class NotFoundException(APIException):
    """資源不存在異常"""
    
    def __init__(self, message):
        super().__init__(message, 404, 'Not Found')

class ConflictException(APIException):
    """資源衝突異常"""
    
    def __init__(self, message):
        super().__init__(message, 409, 'Conflict')

class DatabaseException(APIException):
    """數據庫操作異常"""
    
    def __init__(self, message):
        super().__init__(message, 500, 'Database Error')