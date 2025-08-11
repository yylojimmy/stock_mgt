# -*- coding: utf-8 -*-
"""
股票管理系統 - 數據庫配置

負責數據庫連接、會話管理和基礎操作。
"""

import os
from sqlalchemy import create_engine, event
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy.pool import StaticPool
from contextlib import contextmanager

# 創建基礎模型類
Base = declarative_base()

class DatabaseManager:
    """數據庫管理器"""
    
    def __init__(self, database_url=None, echo=False):
        """初始化數據庫管理器"""
        self.database_url = database_url or self._get_default_database_url()
        self.echo = echo
        self.engine = None
        self.SessionLocal = None
        self.Session = None
        
        self._setup_database()
    
    def _get_default_database_url(self):
        """獲取默認數據庫URL"""
        # 確保data目錄存在
        data_dir = os.path.join(os.path.dirname(__file__), 'data')
        os.makedirs(data_dir, exist_ok=True)
        
        # 根據環境變量決定數據庫文件名
        env = os.environ.get('FLASK_ENV', 'development')
        if env == 'testing':
            return 'sqlite:///:memory:'
        elif env == 'production':
            db_file = os.path.join(data_dir, 'stock_prod.db')
        else:
            db_file = os.path.join(data_dir, 'stock_dev.db')
        
        return f'sqlite:///{db_file}'
    
    def _setup_database(self):
        """設置數據庫連接"""
        # 創建數據庫引擎
        if 'sqlite' in self.database_url:
            # SQLite特殊配置
            self.engine = create_engine(
                self.database_url,
                echo=self.echo,
                poolclass=StaticPool,
                connect_args={
                    'check_same_thread': False,
                    'timeout': 20
                }
            )
            
            # 啟用SQLite外鍵約束
            @event.listens_for(self.engine, 'connect')
            def set_sqlite_pragma(dbapi_connection, connection_record):
                cursor = dbapi_connection.cursor()
                cursor.execute('PRAGMA foreign_keys=ON')
                cursor.execute('PRAGMA journal_mode=WAL')
                cursor.execute('PRAGMA synchronous=NORMAL')
                cursor.execute('PRAGMA cache_size=1000')
                cursor.execute('PRAGMA temp_store=MEMORY')
                cursor.close()
        else:
            # 其他數據庫配置
            self.engine = create_engine(
                self.database_url,
                echo=self.echo,
                pool_pre_ping=True,
                pool_recycle=300
            )
        
        # 創建會話工廠
        self.SessionLocal = sessionmaker(
            autocommit=False,
            autoflush=False,
            bind=self.engine
        )
        
        # 創建線程安全的會話
        self.Session = scoped_session(self.SessionLocal)
    
    def create_tables(self):
        """創建所有數據表"""
        # 導入所有模型以確保它們被註冊
        from models import Stock, Transaction, Dividend
        
        # 創建所有表
        Base.metadata.create_all(bind=self.engine)
        
        print("數據庫表創建完成")
    
    def drop_tables(self):
        """刪除所有數據表"""
        Base.metadata.drop_all(bind=self.engine)
        print("數據庫表已刪除")
    
    def get_session(self):
        """獲取數據庫會話"""
        return self.Session()
    
    @contextmanager
    def session_scope(self):
        """提供事務性會話上下文管理器"""
        session = self.get_session()
        try:
            yield session
            session.commit()
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()
    
    def close(self):
        """關閉數據庫連接"""
        if self.Session:
            self.Session.remove()
        if self.engine:
            self.engine.dispose()
    
    def get_database_info(self):
        """獲取數據庫信息"""
        with self.session_scope() as session:
            # 獲取表信息
            from sqlalchemy import inspect
            inspector = inspect(self.engine)
            tables = inspector.get_table_names()
            
            info = {
                'database_url': self.database_url,
                'tables': tables,
                'table_count': len(tables)
            }
            
            # 如果是SQLite，獲取文件大小
            if 'sqlite' in self.database_url and '/:memory:' not in self.database_url:
                db_file = self.database_url.replace('sqlite:///', '')
                if os.path.exists(db_file):
                    info['file_size'] = os.path.getsize(db_file)
                    info['file_path'] = db_file
            
            return info
    
    def backup_database(self, backup_path):
        """備份數據庫"""
        if 'sqlite' not in self.database_url:
            raise ValueError("目前只支持SQLite數據庫備份")
        
        import shutil
        
        # 獲取源數據庫文件路徑
        source_path = self.database_url.replace('sqlite:///', '')
        
        if not os.path.exists(source_path):
            raise FileNotFoundError(f"數據庫文件不存在: {source_path}")
        
        # 確保備份目錄存在
        backup_dir = os.path.dirname(backup_path)
        os.makedirs(backup_dir, exist_ok=True)
        
        # 複製數據庫文件
        shutil.copy2(source_path, backup_path)
        
        return {
            'source_path': source_path,
            'backup_path': backup_path,
            'backup_size': os.path.getsize(backup_path)
        }
    
    def restore_database(self, backup_path):
        """恢復數據庫"""
        if 'sqlite' not in self.database_url:
            raise ValueError("目前只支持SQLite數據庫恢復")
        
        import shutil
        
        if not os.path.exists(backup_path):
            raise FileNotFoundError(f"備份文件不存在: {backup_path}")
        
        # 獲取目標數據庫文件路徑
        target_path = self.database_url.replace('sqlite:///', '')
        
        # 關閉現有連接
        self.close()
        
        # 恢復數據庫文件
        shutil.copy2(backup_path, target_path)
        
        # 重新初始化數據庫連接
        self._setup_database()
        
        return {
            'backup_path': backup_path,
            'target_path': target_path,
            'restored_size': os.path.getsize(target_path)
        }

# 全局數據庫管理器實例
db_manager = None

def init_database(database_url=None, echo=False):
    """初始化數據庫"""
    global db_manager
    db_manager = DatabaseManager(database_url, echo)
    return db_manager

def get_db_manager():
    """獲取數據庫管理器實例"""
    global db_manager
    if db_manager is None:
        db_manager = DatabaseManager()
    return db_manager

def get_session():
    """獲取數據庫會話（便捷函數）"""
    return get_db_manager().get_session()

@contextmanager
def session_scope():
    """會話上下文管理器（便捷函數）"""
    with get_db_manager().session_scope() as session:
        yield session