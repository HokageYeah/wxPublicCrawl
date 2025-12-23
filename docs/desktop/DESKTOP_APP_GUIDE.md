# 桌面应用使用指南

## 📦 打包后的应用结构

```
dist/
├── wx公众号工具.app           # macOS 应用包（双击运行）
└── wx公众号工具/
    └── wx公众号工具          # 可执行文件（终端运行）
```

## 🚀 启动方式

### 方式1：图形界面启动（推荐）

```bash
open dist/wx公众号工具.app 
```

- ✅ 无终端窗口，后台运行
- ✅ 应用图标显示在 Dock
- ❌ **看不到日志输出**

### 方式2：终端启动（调试用）

```bash
./dist/wx公众号工具/wx公众号工具
```

- ✅ 可以看到实时日志
- ✅ 方便调试和排查问题
- ❌ 终端窗口必须保持打开

## 📋 查看日志

### macOS 日志位置

应用日志保存在 macOS 标准日志目录：

```bash
~/Library/Logs/wx公众号工具/
```

日志文件命名规则：`app_YYYYMMDD_HHMMSS.log`

例如：`app_20251222_163845.log`

### 实时查看日志

使用提供的脚本：

```bash
script/desktop/view_logs.sh
```

**脚本工作原理：**

1. **定位日志目录**
   ```bash
   LOG_DIR="$HOME/Library/Logs/wx公众号工具"
   ```
   - `$HOME` = 用户主目录 `/Users/yuye`
   - macOS 标准日志位置：`~/Library/Logs/应用名称`

2. **创建目录（如果不存在）**
   ```bash
   mkdir -p "$LOG_DIR"
   ```
   - `-p` = 递归创建，不报错

3. **查找最新日志文件**
   ```bash
   LATEST=$(ls -t "$LOG_DIR"/app_*.log 2>/dev/null | head -1)
   ```
   - `ls -t` = 按修改时间排序（最新在前）
   - `2>/dev/null` = 隐藏错误信息
   - `head -1` = 只取第一行（最新文件）

4. **实时监控日志**
   ```bash
   tail -f "$LATEST"
   ```
   - `tail` = 显示文件末尾
   - `-f` = follow 模式，持续监控新增内容
   - 按 `Ctrl+C` 退出

### 手动查看日志

```bash
# 查看最新日志
tail -f ~/Library/Logs/wx公众号工具/app_*.log | head -100

# 查看所有日志文件
ls -lt ~/Library/Logs/wx公众号工具/

# 搜索错误信息
grep -i error ~/Library/Logs/wx公众号工具/app_*.log
```

## 🗂️ 文件系统说明

### 为什么需要特殊处理？

macOS `.app` 包是**只读**的：

```
wx公众号工具.app /
├── Contents/
    ├── MacOS/           # 可执行文件（只读）
    └── Resources/       # 资源文件（只读）
```

❌ **不能在这里写入文件！**

### 可写目录

应用使用 macOS 标准用户数据目录：

| 目录用途 | 路径 | 说明 |
|---------|------|------|
| **数据库** | `~/Library/Application Support/wx公众号工具/wxpublic.db` | SQLite 数据库 |
| **临时文件** | `~/Library/Application Support/wx公众号工具/temp/` | 二维码、缓存等 |
| **日志文件** | `~/Library/Logs/wx公众号工具/` | 应用日志 |

### 代码实现

```python
# app/utils/src_path.py

def get_writable_dir(subdir='temp'):
    """获取可写目录路径"""
    if platform.system() == 'Darwin':  # macOS
        base_dir = os.path.expanduser('~/Library/Application Support/wx公众号工具')
    elif platform.system() == 'Windows':
        base_dir = os.path.expanduser('~/AppData/Local/wx公众号工具')
    else:  # Linux
        base_dir = os.path.expanduser('~/.local/share/wx公众号工具')
    
    target_dir = os.path.join(base_dir, subdir)
    os.makedirs(target_dir, exist_ok=True)
    return target_dir

def get_temp_file_path(filename):
    """获取临时文件的完整路径"""
    temp_dir = get_writable_dir('temp')
    return os.path.join(temp_dir, filename)
```

### 使用示例

```python
# ❌ 错误：写入当前目录（只读）
with open('qrcode.png', 'wb') as f:
    f.write(data)

# ✅ 正确：写入可写目录
from app.utils.src_path import get_temp_file_path

qrcode_path = get_temp_file_path('qrcode.png')
with open(qrcode_path, 'wb') as f:
    f.write(data)
# 实际路径：~/Library/Application Support/wx公众号工具/temp/qrcode.png
```

## 🐛 常见问题排查

### 1. 应用无法启动

**症状**：双击 `.app` 后立即退出

**排查步骤**：

```bash
# 1. 终端启动查看错误
./dist/wx公众号工具/wx公众号工具

# 2. 查看系统日志
./view_logs.sh

# 3. 检查端口占用
lsof -ti:18000

# 4. 清理并重启
script/desktop/kill_app.sh
open dist/wx公众号工具.app 
```

### 2. 文件写入失败

**错误信息**：
```
[Errno 30] Read-only file system: 'filename'
```

**原因**：试图在 `.app` 包内写入文件

**解决**：使用 `get_temp_file_path()` 或 `get_writable_dir()`

### 3. 数据库连接失败

**检查数据库文件**：

```bash
ls -lh ~/Library/Application\ Support/wx公众号工具/wxpublic.db
```

**查看数据库内容**：

```bash
sqlite3 ~/Library/Application\ Support/wx公众号工具/wxpublic.db

sqlite> .tables
sqlite> .schema
sqlite> .quit
```

### 4. 端口已被占用

**错误信息**：
```
[Errno 48] address already in use
```

**解决**：

```bash
# 查找并终止占用进程
lsof -ti:18000 | xargs kill -9

# 或使用清理脚本
script/desktop/kill_app.sh
```

## 📊 日志级别

应用使用不同的日志级别：

| 级别 | 说明 | 使用场景 |
|------|------|---------|
| **INFO** | 正常信息 | 应用启动、请求处理 |
| **WARNING** | 警告信息 | 降级处理、兼容性问题 |
| **ERROR** | 错误信息 | 异常、失败 |
| **DEBUG** | 调试信息 | 仅开发环境 |

**桌面环境（ENV=desktop）**：
- ✅ 只输出 INFO、WARNING、ERROR
- ❌ 不输出 DEBUG 和配置打印

**开发环境（ENV=development）**：
- ✅ 输出所有级别
- ✅ 包含配置信息、路径信息

## 🔄 开发 vs 生产

| 特性 | 开发环境 | 桌面应用 |
|------|---------|---------|
| **启动方式** | `python run_desktop.py` | `open dist/wx公众号工具.app ` |
| **ENV** | `development` | `desktop` |
| **数据库** | MySQL 或 SQLite | SQLite |
| **日志输出** | 终端 + 文件 | 仅文件 |
| **调试信息** | ✅ 显示 | ❌ 隐藏 |
| **配置文件** | `.env` | 内置默认 |

## 🛠️ 维护命令

```bash
# 查看应用状态
lsof -ti:18000

# 查看日志
./view_logs.sh

# 清理应用
script/desktop/kill_app.sh

# 重新打包
script/desktop/build_mac.sh

# 测试打包结果
./dist/wx公众号工具/wx公众号工具

# 正式启动
open dist/wx公众号工具.app 
```

## 📁 完整目录结构

```
wx公众号工具/
├── 用户数据（可读写）
│   ├── ~/Library/Application Support/wx公众号工具/
│   │   ├── wxpublic.db                    # SQLite 数据库
│   │   └── temp/
│   │       └── qrcode.png                 # 临时二维码
│   └── ~/Library/Logs/wx公众号工具/
│       └── app_YYYYMMDD_HHMMSS.log       # 应用日志
│
└── 应用包（只读）
    ├── dist/wx公众号工具.app /
    │   └── Contents/
    │       ├── MacOS/wx公众号工具      # 主程序
    │       └── Resources/                  # 前端资源
    └── dist/wx公众号工具/
        └── wx公众号工具                # 调试用可执行文件
```

## 🎯 最佳实践

1. **开发阶段**：
   - 使用 `python run_desktop.py` 开发
   - 实时查看终端输出
   - 快速迭代调试

2. **测试打包**：
   - 使用 `./dist/wx公众号工具/wx公众号工具` 测试
   - 打开 `./view_logs.sh` 监控日志
   - 确认所有功能正常

3. **正式使用**：
   - 使用 `open dist/wx公众号工具.app ` 启动
   - 后台运行，无终端干扰
   - 出问题时查看日志文件

---

**最后更新**: 2025-12-22  
**适用版本**: wx公众号工具 v1.0

