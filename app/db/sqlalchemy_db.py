# src/sql/sql_connect_db.py
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.pool import QueuePool
from typing import Generator
import logging
from app.config.database_config import get_database_config, DATABASE_URL
# 创建基类，用于声明模型
Base = declarative_base()

class Database:
    def __init__(self):
        self.db_config = get_database_config()
        self.db_url = str(DATABASE_URL)
        self._engine = None
        self._session_factory = None

    def connect(self) -> None:
        """初始化数据库连接"""
        try:
            # SQLite 不需要连接池配置
            is_sqlite = self.db_url.startswith('sqlite:///')
            
            if is_sqlite:
                # SQLite 配置
                self._engine = create_engine(
                    self.db_url,
                    echo=self.db_config['echo'],
                    connect_args={"check_same_thread": False}  # SQLite 特定配置
                )
            else:
                # MySQL 等其他数据库配置
                self._engine = create_engine(
                    self.db_url,
                    poolclass=QueuePool,
                    pool_size=self.db_config['pool_size'],
                    max_overflow=self.db_config['max_overflow'],
                    pool_timeout=self.db_config['pool_timeout'],
                    pool_recycle=self.db_config['pool_recycle'],
                    echo=self.db_config['echo']
                )
            
            # 创建会话工厂
            self._session_factory = sessionmaker(
                bind=self._engine,
                autocommit=False,
                autoflush=False
            )

            # 测试连接
            session = self._session_factory()
            try:
                session.execute(text("SELECT 1"))
                logging.info(f"sqlalchemy数据库连接成功 - 数据库类型: {'SQLite' if is_sqlite else 'MySQL'}")
                
                # 如果是 SQLite，创建表结构
                if is_sqlite:
                    Base.metadata.create_all(self._engine)
                    logging.info("SQLite 数据库表结构已创建")
                    
            finally:
                session.close()

        except Exception as e:
            logging.error(f"sqlalchemy数据库连接失败: {e}")
            logging.warning("应用将在没有数据库的情况下启动，某些功能可能不可用")
            # 桌面应用不抛出异常，允许在没有数据库的情况下启动
            # raise  # 注释掉这行，让应用继续运行

    def get_session(self) -> Generator[Session, None, None]:
        """获取数据库会话"""
        if not self._session_factory:
            logging.warning("数据库未连接，某些功能可能不可用")
            raise RuntimeError("数据库未初始化。如果您是桌面应用用户，请检查数据库配置。")
            
        session = self._session_factory()
        try:
            yield session
        finally:
            session.close()

    def close(self) -> None:
        """关闭数据库连接"""
        if self._engine:
            self._engine.dispose()
            logging.info("sqlalchemy数据库连接已关闭")

# 创建全局数据库实例
database = Database()

# 获取数据库会话的依赖函数
def get_sqlalchemy_db() -> Generator[Session, None, None]:
    """获取数据库会话"""
    db = next(database.get_session())
    try:
        return db
    except Exception as e:
        db.close()
        logging.error(f"获取数据库会话失败: {e}")
        raise
    finally:
        print('数据库会话关闭')
        db.close()
