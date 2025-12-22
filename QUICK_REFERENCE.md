# 快速参考卡片 🚀

## 📦 打包

```bash
script/desktop/build_mac.sh         # 打包 macOS 应用
script/desktop/build_windows.bat    # 打包 Windows 应用
```

## 🚀 启动应用

```bash
# 方式1：图形界面（推荐）
open dist/WxPublicCrawler.app

# 方式2：终端调试
./dist/WxPublicCrawler/WxPublicCrawler

# 方式3：快速测试
script/desktop/test_app.sh
```

## 📋 查看日志

```bash
# 实时查看日志（推荐）
script/desktop/view_logs.sh

# 手动查看
tail -f ~/Library/Logs/WxPublicCrawler/app_*.log

# 搜索错误
grep -i error ~/Library/Logs/WxPublicCrawler/app_*.log
```

## 🛠️ 维护命令

```bash
script/desktop/kill_app.sh   # 清理应用实例
script/desktop/test_app.sh   # 测试打包应用
script/desktop/view_logs.sh  # 查看日志
lsof -ti:18000               # 查看端口占用
```

## 📁 重要目录

| 用途 | 路径 |
|------|------|
| 数据库 | `~/Library/Application Support/WxPublicCrawler/wxpublic.db` |
| 临时文件 | `~/Library/Application Support/WxPublicCrawler/temp/` |
| 日志文件 | `~/Library/Logs/WxPublicCrawler/` |
| 应用包 | `dist/WxPublicCrawler.app` |

## 🐛 常见错误

| 错误 | 原因 | 解决 |
|------|------|------|
| `[Errno 48] address already in use` | 端口占用 | `./kill_app.sh` |
| `[Errno 30] Read-only file system` | 写入只读目录 | 使用 `get_temp_file_path()` |
| `ValidationError` | 环境变量缺失 | 检查 `ENV=desktop` |
| `mysql_native_password not supported` | MySQL 驱动问题 | 使用 SQLite |

## 🔍 调试技巧

```bash
# 1. 查看应用是否在运行
lsof -ti:18000

# 2. 查看最新日志
script/desktop/view_logs.sh

# 3. 测试打包应用
script/desktop/test_app.sh

# 4. 清理并重新打包
script/desktop/kill_app.sh && rm -rf dist build && script/desktop/build_mac.sh

# 5. 查看数据库
sqlite3 ~/Library/Application\ Support/WxPublicCrawler/wxpublic.db ".tables"
```

## 📄 view_logs.sh 原理

```bash
# 1. 定位日志目录
LOG_DIR="$HOME/Library/Logs/WxPublicCrawler"

# 2. 查找最新日志
LATEST=$(ls -t "$LOG_DIR"/app_*.log 2>/dev/null | head -1)

# 3. 实时监控
tail -f "$LATEST"
```

**核心命令解释：**

- `ls -t` → 按时间排序（最新在前）
- `2>/dev/null` → 隐藏错误输出
- `head -1` → 只取第一行
- `tail -f` → 持续监控文件变化
- `Ctrl+C` → 退出监控

## 🎯 工作流程

### 开发阶段

```bash
# 1. 修改代码
vim app/...

# 2. 本地测试
python run_desktop.py

# 3. 打包测试
script/desktop/build_mac.sh

# 4. 快速验证
script/desktop/test_app.sh
```

### 问题排查

```bash
# 1. 清理环境
script/desktop/kill_app.sh

# 2. 查看日志
script/desktop/view_logs.sh

# 3. 重新打包
rm -rf dist build && script/desktop/build_mac.sh

# 4. 测试运行
script/desktop/test_app.sh
```

## 🔒 文件系统规则

### ❌ 不能写入（只读）

```python
# 应用包内部（.app/Contents/...）
with open('file.txt', 'w') as f:  # ❌ 失败
    f.write(data)
```

### ✅ 可以写入

```python
from app.utils.src_path import get_temp_file_path

# 用户数据目录
path = get_temp_file_path('file.txt')
with open(path, 'w') as f:  # ✅ 成功
    f.write(data)
```

## 📊 环境变量

| 变量 | 开发环境 | 桌面应用 |
|------|---------|---------|
| `ENV` | `development` | `desktop` |
| `DB_DRIVER` | `mysql` / `sqlite` | `sqlite` |
| `DEBUG` | `True` | `False` |

## 🎨 访问地址

| 环境 | 地址 |
|------|------|
| 开发环境 | `http://localhost:18000` |
| 桌面应用 | `http://127.0.0.1:18000/crawl-desktop/` |

## 📞 帮助

详细文档：

- [DESKTOP_APP_GUIDE.md](./DESKTOP_APP_GUIDE.md) - 完整使用指南
- [PACKAGING_QUICKSTART.md](./PACKAGING_QUICKSTART.md) - 打包说明
- [FIX_REPEATED_LOGGING.md](./FIX_REPEATED_LOGGING.md) - 日志修复说明

---

💡 **提示**：遇到问题先运行 `./view_logs.sh` 查看日志！

