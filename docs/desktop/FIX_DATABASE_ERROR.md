# 修复数据库连接错误

## 问题描述

打包后的应用启动失败，错误信息：
```
Authentication plugin 'mysql_native_password' is not supported
No module named 'mysql.connector.plugins.mysql_native_password'
```

## 根本原因

1. PyInstaller 没有正确打包 MySQL Connector 的认证插件模块
2. 桌面应用使用 MySQL 数据库不合适（需要用户自己安装和配置 MySQL 服务器）

## ✅ 解决方案

**桌面应用使用 SQLite 数据库**，更适合桌面应用场景：
- ✅ 无需安装数据库服务器
- ✅ 数据文件存储在用户目录
- ✅ 轻量级、快速
- ✅ 完全便携

## 🔧 已完成的修复

### 1. 修改 `app/core/config.py`

将默认数据库驱动改为 SQLite：

```python
# 数据库配置
DB_DRIVER: Optional[str] = "sqlite"  # desktop 环境默认使用 sqlite
DB_ECHO: Optional[bool] = False  # 桌面应用默认不输出 SQL 日志
```

### 2. 修改 `app/config/database_config.py`

添加 SQLite 数据库 URL 生成逻辑：

```python
def get_database_url() -> str:
    """获取当前环境的数据库URL"""
    config = get_database_config()
    driver = config['driver']
    
    # SQLite 使用不同的 URL 格式
    if driver == "sqlite":
        # 数据库存储在用户数据目录
        # Mac: ~/Library/Application Support/WxPublicCrawler/wxpublic.db
        # Windows: ~/AppData/Local/WxPublicCrawler/wxpublic.db
        # Linux: ~/.local/share/WxPublicCrawler/wxpublic.db
        ...
```

### 3. 修改 `app/db/sqlalchemy_db.py`

- 添加 SQLite 特定配置
- 自动创建数据库表结构
- 数据库连接失败时不抛出异常，允许应用继续运行

```python
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
                connect_args={"check_same_thread": False}
            )
            # 自动创建表结构
            Base.metadata.create_all(self._engine)
        ...
    except Exception as e:
        logging.error(f"数据库连接失败: {e}")
        logging.warning("应用将在没有数据库的情况下启动")
        # 不抛出异常，让应用继续运行
```

### 4. 修改 `wx_crawler.spec`

- 移除 MySQL Connector 的隐藏导入
- 排除 MySQL 相关模块以减小体积
- 添加 SQLite 支持

```python
hiddenimports=[
    # ... 其他模块
    'pysqlite3',  # SQLite 驱动
],
excludes=[
    # ... 其他模块
    'mysql.connector.plugins',  # 排除 MySQL 插件
    'pymysql',
],
```

## 🚀 重新打包步骤

### 步骤 1: 清理旧文件

```bash
cd "/Users/yuye/YeahWork/Python项目/wxPublicCrawl"

# 修改权限并删除
chmod -R 755 dist 2>/dev/null || true
rm -rf dist build
```

### 步骤 2: 重新打包

```bash
./build_mac.sh
```

### 步骤 3: 测试应用

```bash
# 方式 1: 查看详细日志
./dist/WxPublicCrawler/WxPublicCrawler

# 方式 2: 打开应用
open dist/WxPublicCrawler.app
```

## 📋 预期的成功输出

如果修复成功，你应该看到：

```
当前环境: development
配置文件 .env 不存在，使用默认配置

当前数据库环境信息:
----------------------------------------
database_config.py---- ENV: development
database_config.py---- SQLite 数据库路径: /Users/yuye/Library/Application Support/WxPublicCrawler/wxpublic.db
----------------------------------------

日志系统初始化完成 - 使用 loguru
sqlalchemy数据库连接成功 - 数据库类型: SQLite
SQLite 数据库表结构已创建

INFO:     Started server process [xxxxx]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://127.0.0.1:18000
```

然后应用窗口会打开并显示界面。

## 📁 数据库文件位置

SQLite 数据库文件会自动创建在：

### Mac
```
~/Library/Application Support/WxPublicCrawler/wxpublic.db
```

### Windows
```
%APPDATA%\Local\WxPublicCrawler\wxpublic.db
```

### Linux
```
~/.local/share/WxPublicCrawler/wxpublic.db
```

## 🔄 如果仍想使用 MySQL（高级用户）

如果你确实需要使用 MySQL（比如服务器部署），可以通过环境变量配置：

### 方式 1: 设置环境变量

在启动前设置：

```bash
export DB_DRIVER="mysql+mysqlconnector"
export DB_HOST="localhost"
export DB_PORT="3306"
export DB_NAME="wx_public_dev"
export DB_USER="root"
export DB_PASSWORD="your_password"
./dist/WxPublicCrawler/WxPublicCrawler
```

### 方式 2: 修复 MySQL Connector 打包（复杂）

在 `wx_crawler.spec` 中添加：

```python
hiddenimports=[
    # ... 其他模块
    'mysql.connector.locales.eng.client_error',
    'mysql.connector.plugins',
    'mysql.connector.plugins.mysql_native_password',
    'mysql.connector.plugins.caching_sha2_password',
    'mysql.connector.plugins.sha256_password',
],
```

但这需要确保打包环境中 MySQL Connector 完整安装。

## 🐛 故障排除

### 数据库文件权限错误

如果看到权限错误：

```bash
# Mac
chmod 755 ~/Library/Application\ Support/WxPublicCrawler
chmod 644 ~/Library/Application\ Support/WxPublicCrawler/wxpublic.db

# Windows（在 PowerShell 中）
# 通常不会有权限问题
```

### 数据库文件损坏

如果数据库文件损坏，删除后会自动重新创建：

```bash
# Mac
rm ~/Library/Application\ Support/WxPublicCrawler/wxpublic.db

# 重启应用，数据库会自动重新创建
```

### 查看数据库内容

可以使用 SQLite 工具查看数据库：

```bash
# 安装 sqlite3（Mac 自带）
sqlite3 ~/Library/Application\ Support/WxPublicCrawler/wxpublic.db

# 查看表
.tables

# 查看表结构
.schema

# 退出
.quit
```

### 数据迁移（从 MySQL 到 SQLite）

如果你之前使用 MySQL 并想迁移数据：

1. 导出 MySQL 数据：
```bash
mysqldump -u root -p wx_public_dev > backup.sql
```

2. 使用工具转换（如 [mysql2sqlite](https://github.com/dumblob/mysql2sqlite)）

3. 导入到 SQLite：
```bash
sqlite3 ~/Library/Application\ Support/WxPublicCrawler/wxpublic.db < converted.sql
```

## 📊 SQLite vs MySQL 对比

| 特性 | SQLite | MySQL |
|------|--------|-------|
| 安装 | ✅ 无需安装 | ❌ 需要安装服务器 |
| 配置 | ✅ 零配置 | ❌ 需要配置 |
| 便携性 | ✅ 单文件，完全便携 | ❌ 依赖服务器 |
| 性能 | ✅ 适合单用户 | ✅ 适合多用户 |
| 并发 | ⚠️ 有限的写并发 | ✅ 高并发 |
| 适用场景 | ✅ 桌面应用 | ✅ 服务器应用 |

**结论**: 桌面应用使用 SQLite 是最佳选择。

## ✅ 验证修复

运行以下命令验证修改：

```bash
# 1. 检查配置文件
grep "DB_DRIVER:" app/core/config.py
# 应该看到: DB_DRIVER: Optional[str] = "sqlite"

# 2. 检查数据库配置
grep -A 20 "def get_database_url" app/config/database_config.py
# 应该看到 SQLite 相关逻辑

# 3. 检查 spec 文件
grep "pysqlite3" wx_crawler.spec
# 应该看到: 'pysqlite3',
```

## 📚 相关文档

- [SQLite 官方文档](https://www.sqlite.org/docs.html)
- [SQLAlchemy SQLite 方言](https://docs.sqlalchemy.org/en/20/dialects/sqlite.html)

---

**修复时间**: 2025-12-19  
**修复内容**: 
1. 桌面应用改用 SQLite 数据库
2. 数据库连接失败时不影响应用启动
3. 优化打包配置，移除 MySQL 依赖

