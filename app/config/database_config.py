import os
from typing import Dict, Any
from dotenv import load_dotenv
from app.core.config import settings

# ✅ 添加缓存标志，防止重复打印
_config_printed = False

def get_database_config():
    """根据当前环境获取数据库配置"""
    global _config_printed
    
    env = os.getenv("ENV", "development").lower()
    
    # ✅ 只在开发环境且未打印过时才打印
    if env in ("development", "dev", "test") and not _config_printed:
        print("\n当前数据库环境信息:")
        print("----------------------------------------")
        print(f"database_config.py---- ENV: {env}")
        print(f"database_config.py---- DB_NAME: {os.getenv('DB_NAME')}") 
        print(f"database_config.py---- settings.DB_NAME: {settings.DB_NAME}") 
        print(f"database_config.py---- settings.DB_CHARSET: {settings.Config.env_file}") 
        print("----------------------------------------")
        _config_printed = True
    
    return {
        "driver": settings.DB_DRIVER,
        "username": settings.DB_USER,
        "password": settings.DB_PASSWORD,
        "host": settings.DB_HOST,
        "port": settings.DB_PORT,
        "database": settings.DB_NAME,
        "charset": settings.DB_CHARSET,
        "echo": settings.DB_ECHO,
        "pool_size": settings.DB_POOL_SIZE,
        "max_overflow": settings.DB_MAX_OVERFLOW,
        "pool_recycle": settings.DB_POOL_RECYCLE,
        "pool_timeout": settings.DB_POOL_TIMEOUT,
    }

# ✅ 添加缓存，防止重复调用
_database_url_cache = None
_db_path_printed = False

def get_database_url() -> str:
    """获取当前环境的数据库URL"""
    global _database_url_cache, _db_path_printed
    
    # ✅ 如果已经生成过，直接返回缓存
    if _database_url_cache is not None:
        return _database_url_cache
    
    config = get_database_config()
    driver = config['driver']
    
    # SQLite 使用不同的 URL 格式
    if driver == "sqlite":
        # 获取用户数据目录
        import platform
        if platform.system() == 'Darwin':  # Mac
            data_dir = os.path.expanduser('~/Library/Application Support/wx公众号工具')
        elif platform.system() == 'Windows':
            data_dir = os.path.expanduser('~/AppData/Local/wx公众号工具')
        else:  # Linux
            data_dir = os.path.expanduser('~/.local/share/wx公众号工具')
        
        # 确保目录存在 exist_ok=True 表示如果目录存在则不创建
        os.makedirs(data_dir, exist_ok=True)
        
        # SQLite 数据库文件路径
        db_file = os.path.join(data_dir, 'wxpublic.db')
        
        # ✅ 只打印一次
        if not _db_path_printed:
            print(f"database_config.py---- SQLite 数据库路径: {db_file}")
            _db_path_printed = True
        
        _database_url_cache = f"sqlite:///{db_file}"
    else:
        # MySQL 等其他数据库
        _database_url_cache = f"{driver}://{config['username']}:{config['password']}@{config['host']}:{config['port']}/{config['database']}?charset={config['charset']}"
    
    return _database_url_cache

# ✅ 使用惰性求值：只在被访问时才调用函数
# 而不是在模块导入时就执行
def get_database_url_lazy():
    """延迟获取数据库URL（供外部使用）"""
    return get_database_url()

# ✅ 为了兼容旧代码，保留这个变量，但使用属性访问
class DatabaseURLProxy:
    """数据库URL代理，延迟求值"""
    def __str__(self):
        return get_database_url()  # 使用时才获取URL
    
    def __repr__(self): 
        return get_database_url()  # 使用时才获取URL

# ✅ 导出代理对象而不是直接调用函数
DATABASE_URL = DatabaseURLProxy()