# 修复环境变量错误

## 问题描述

打包后的应用启动失败，错误信息：
```
pydantic_core._pydantic_core.ValidationError: 2 validation errors for Settings
ENVIRONMENT
  Field required [type=missing, input_value={}, input_type=dict]
N8N_WEBHOOK_URL
  Field required [type=missing, input_value={}, input_type=dict]
```

## 根本原因

`app/core/config.py` 中的 `Settings` 类有两个必需字段没有默认值：
- `ENVIRONMENT`
- `N8N_WEBHOOK_URL`

打包后的应用无法访问 `.env` 文件，导致这些字段验证失败。

## ✅ 已完成的修复

我已经修改了 `app/core/config.py`，做了以下改动：

### 1. 为必需字段添加默认值

```python
class Settings(BaseSettings):
    # ... 其他字段
    ENVIRONMENT: str = "desktop"  # 桌面应用默认为 desktop
    N8N_WEBHOOK_URL: str = ""     # 桌面应用默认为空
```

### 2. 改进配置文件加载逻辑

```python
# 检查配置文件是否存在
if os.path.exists(env_file):
    print(f"加载配置文件: {env_file}")
    load_dotenv(env_file, override=True)
else:
    print(f"配置文件 {env_file} 不存在，使用默认配置")
    # 对于打包后的桌面应用，配置文件不存在是正常的
```

## 🔧 重新打包步骤

### 方式 1: 使用打包脚本（推荐）

```bash
# 1. 手动删除旧的打包文件（如果权限不够）
rm -rf build
# 如果 dist 删除失败，可以：
chmod -R 755 dist
rm -rf dist

# 2. 运行打包脚本
./build_mac.sh
```

### 方式 2: 手动打包

```bash
# 1. 清理旧文件
rm -rf build
chmod -R 755 dist 2>/dev/null || true
rm -rf dist

# 2. 确保虚拟环境已激活
source venv/bin/activate

# 3. 确保前端已构建
cd web
npm run build:only
cd ..

# 4. 打包
pyinstaller wx_crawler.spec

# 5. 测试
open dist/wx公众号工具.app 
```

## 🧪 测试应用

### 测试 .app 包

```bash
open dist/wx公众号工具.app 
```

### 测试可执行文件（查看详细日志）

```bash
# 这样可以看到详细的启动日志
./dist/wx公众号工具/wx公众号工具
```

成功的输出应该是：
```
当前环境: development
配置文件 .env 不存在，使用默认配置
INFO:     Started server process [xxxxx]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://127.0.0.1:18000 (Press CTRL+C to quit)
```

## 📝 配置说明

### 默认配置

修复后，桌面应用使用以下默认配置：

```python
ENVIRONMENT = "desktop"
N8N_WEBHOOK_URL = ""
DEBUG = False
DB_HOST = "localhost"
DB_PORT = 3306
DB_NAME = "wx_public_dev"
DB_USER = "root"
DB_PASSWORD = "aa123456"
# ... 其他配置
```

### 如果需要自定义配置（可选）

如果用户需要不同的配置，可以通过以下方式：

#### 方式 1: 环境变量

在启动应用前设置环境变量：

```bash
export N8N_WEBHOOK_URL="https://your-webhook-url.com"
export DB_HOST="your-db-host"
export DB_PASSWORD="your-password"
./dist/wx公众号工具/wx公众号工具
```

#### 方式 2: 创建配置文件（未来改进）

可以在用户目录创建配置文件：

```bash
# Mac
~/Library/Application Support/wx公众号工具/config.ini

# Windows
%APPDATA%\wx公众号工具\config.ini
```

## 🐛 如果还有其他错误

### 数据库连接错误

如果看到数据库连接错误，说明应用试图连接数据库但连接失败。

**解决方案**：
1. 确保本地 MySQL 服务已启动
2. 检查数据库配置是否正确
3. 或者修改代码，让桌面应用使用 SQLite 数据库

### 端口被占用

如果看到端口 18000 被占用的错误：

```bash
# 查找占用端口的进程
lsof -i :18000

# 杀死该进程
kill -9 <PID>
```

### 前端资源加载失败

如果应用启动了但页面空白：

1. 检查 `web/dist` 是否存在且不为空
2. 检查 `wx_crawler.spec` 中是否包含 `('web/dist', 'web/dist')`
3. 重新构建前端：`cd web && npm run build:only && cd ..`

## 📊 验证修复

运行以下命令验证配置文件已正确修改：

```bash
# 查看修改后的配置文件
grep -A 2 "ENVIRONMENT:" app/core/config.py
grep -A 2 "N8N_WEBHOOK_URL:" app/core/config.py
```

应该看到：
```python
ENVIRONMENT: str = "desktop"  # 环境变量，桌面应用默认为 desktop
...
N8N_WEBHOOK_URL: str = ""  # n8n的webhook地址，桌面应用默认为空
```

## ✅ 预期结果

修复后，应用应该能够正常启动，并在浏览器窗口中显示界面。

如果还有问题，请检查终端输出的详细错误信息，并参考上述故障排除步骤。

---

**修复时间**: 2025-12-19  
**修复内容**: 为必需的配置字段添加默认值，改进配置文件加载逻辑

