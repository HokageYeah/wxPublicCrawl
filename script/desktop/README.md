# 桌面应用构建脚本

本目录包含构建和管理桌面应用的所有脚本。

## 📁 脚本列表

| 脚本 | 平台 | 功能说明 |
|------|------|---------|
| **build_mac.sh** | macOS | 构建 macOS 桌面应用 (.app) |
| **build_windows.bat** | Windows | 构建 Windows 桌面应用 (.exe) |
| **kill_app.sh** | macOS | 终止运行中的应用实例并清理锁文件 |
| **test_app.sh** | macOS | 快速测试打包后的应用 |
| **view_logs.sh** | macOS | 实时查看应用日志 |

## 🚀 使用方法

### 方式1：从项目根目录运行（推荐）

所有脚本都会**自动切换到项目根目录**，所以可以从任何位置运行：

```bash
# 从项目根目录
cd /path/to/wxPublicCrawl
script/desktop/build_mac.sh          # macOS 打包
script/desktop/build_windows.bat     # Windows 打包
script/desktop/test_app.sh           # 测试应用
script/desktop/view_logs.sh          # 查看日志
script/desktop/kill_app.sh           # 清理应用

# 或从脚本目录
cd script/desktop
./build_mac.sh
./test_app.sh
./view_logs.sh
./kill_app.sh
```

### 方式2：创建项目根目录的快捷方式（可选）

如果你希望在项目根目录也能快速访问这些脚本，可以创建符号链接：

```bash
# 在项目根目录创建符号链接
cd /path/to/wxPublicCrawl
ln -s script/desktop/build_mac.sh build_mac.sh
ln -s script/desktop/kill_app.sh kill_app.sh
ln -s script/desktop/test_app.sh test_app.sh
ln -s script/desktop/view_logs.sh view_logs.sh

# 然后就可以直接运行
./build_mac.sh
./test_app.sh
```

## 📋 详细说明

### 1. build_mac.sh - macOS 打包脚本

**功能**：构建 macOS 桌面应用

**步骤**：
1. 检查 Python 和 Node.js 环境
2. 创建/检查虚拟环境
3. 安装 Python 依赖
4. 构建前端项目
5. 清理旧的打包文件
6. 使用 PyInstaller 打包
7. 处理 macOS 安全属性

**使用**：

```bash
# 从任何位置运行
script/desktop/build_mac.sh

# 或进入脚本目录
cd script/desktop
./build_mac.sh
```

**输出**：
- `dist/WxPublicCrawler.app` - macOS 应用包
- `dist/WxPublicCrawler/WxPublicCrawler` - 可执行文件

**时间**：首次约 5-10 分钟，后续约 2-3 分钟

### 2. build_windows.bat - Windows 打包脚本

**功能**：构建 Windows 桌面应用

**步骤**：与 macOS 类似，但输出为 Windows 可执行文件

**使用**：

```batch
REM 从任何位置运行
script\desktop\build_windows.bat

REM 或进入脚本目录
cd script\desktop
build_windows.bat
```

**输出**：
- `dist\WxPublicCrawler\WxPublicCrawler.exe` - Windows 可执行文件

### 3. kill_app.sh - 清理应用

**功能**：
- 终止占用端口 18000 的进程
- 清理应用锁文件

**使用**：

```bash
script/desktop/kill_app.sh
```

**适用场景**：
- 应用无法启动（端口被占用）
- 应用异常退出后清理
- 重新打包前清理环境

### 4. test_app.sh - 快速测试

**功能**：
- 自动清理旧实例
- 启动应用并后台运行
- 显示启动日志
- 提供访问链接和管理命令

**使用**：

```bash
script/desktop/test_app.sh
```

**输出示例**：

```
============================================================
  测试打包后的桌面应用
============================================================
项目目录: /Users/yuye/YeahWork/Python项目/wxPublicCrawl

✓ 找到打包文件

[1/3] 清理旧实例...
✓ 完成

[2/3] 启动应用...
✓ 应用已启动 (PID: 12345)

[3/3] 等待应用启动...
✓ 应用正在运行

============================================================
  应用信息
============================================================
进程 ID: 12345
访问地址: http://127.0.0.1:18000
日志文件: /tmp/wx_test.log

📊 查看完整日志：
   tail -f /tmp/wx_test.log

📊 查看标准日志：
   script/desktop/view_logs.sh

🌐 在浏览器打开：
   open http://127.0.0.1:18000/crawl-desktop/

🛑 停止应用：
   script/desktop/kill_app.sh
   或
   kill 12345
```

### 5. view_logs.sh - 查看日志

**功能**：
- 定位 macOS 标准日志目录
- 查找最新的日志文件
- 实时监控日志内容

**使用**：

```bash
# 启动实时日志查看
script/desktop/view_logs.sh

# 按 Ctrl+C 退出
```

**工作原理**：

```bash
# 1. 日志目录
~/Library/Logs/WxPublicCrawler/

# 2. 查找最新日志
ls -t app_*.log | head -1

# 3. 实时监控
tail -f latest.log
```

**日志位置**：
- macOS: `~/Library/Logs/WxPublicCrawler/app_YYYYMMDD_HHMMSS.log`
- Windows: `%LOCALAPPDATA%\WxPublicCrawler\Logs\`

## 🔧 技术细节

### 自动路径处理

所有脚本都包含自动路径切换逻辑：

**macOS/Linux (bash)**:

```bash
# 获取脚本所在目录
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# 切换到项目根目录（上两级）
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
cd "$PROJECT_ROOT"
```

**Windows (bat)**:

```batch
REM 获取脚本所在目录
set "SCRIPT_DIR=%~dp0"

REM 切换到项目根目录（上两级）
cd /d "%SCRIPT_DIR%..\.."
set "PROJECT_ROOT=%CD%"
```

### 为什么需要路径处理？

脚本需要访问项目文件：
- `web/` - 前端源码目录
- `requirements.txt` - Python 依赖
- `wx_crawler.spec` - PyInstaller 配置
- `venv/` - 虚拟环境
- `dist/` - 输出目录

通过自动切换到项目根目录，确保无论从哪里运行脚本，路径引用都是正确的。

## 📂 目录结构

```
wxPublicCrawl/                          # 项目根目录
├── script/
│   └── desktop/                        # 桌面脚本目录
│       ├── build_mac.sh               # macOS 打包
│       ├── build_windows.bat          # Windows 打包
│       ├── kill_app.sh                # 清理应用
│       ├── test_app.sh                # 测试应用
│       ├── view_logs.sh               # 查看日志
│       └── README.md                  # 本文件
├── web/                                # 前端代码
├── app/                                # 后端代码
├── dist/                               # 打包输出
├── requirements.txt                    # Python 依赖
└── wx_crawler.spec                     # PyInstaller 配置
```

## 🔄 工作流程

### 完整开发流程

```bash
# 1. 修改代码
vim app/...

# 2. 本地测试
python run_desktop.py

# 3. 打包应用
script/desktop/build_mac.sh

# 4. 测试打包
script/desktop/test_app.sh

# 5. 查看日志（在另一个终端）
script/desktop/view_logs.sh

# 6. 发现问题，清理重来
script/desktop/kill_app.sh
script/desktop/build_mac.sh
```

### 问题排查流程

```bash
# 1. 应用无法启动
script/desktop/kill_app.sh             # 清理
script/desktop/view_logs.sh            # 查看日志

# 2. 重新打包
rm -rf dist build
script/desktop/build_mac.sh

# 3. 测试
script/desktop/test_app.sh
```

## 🎯 常见问题

### Q: 脚本提示找不到文件？
A: 脚本会自动切换到项目根目录，确保文件结构完整。检查是否在正确的项目中运行。

### Q: 可以从任何位置运行这些脚本吗？
A: 可以！脚本包含自动路径处理，会自动切换到项目根目录。

### Q: Windows 脚本在 macOS 上能用吗？
A: 不能。`build_windows.bat` 只能在 Windows 上运行，`build_mac.sh` 只能在 macOS 上运行。

### Q: 如何在项目根目录快速访问这些脚本？
A: 创建符号链接（见上文"方式2"），或直接使用相对路径 `script/desktop/xxx.sh`。

### Q: 脚本修改后需要重新打包吗？
A: 不需要。这些脚本是开发工具，不会被打包到应用中。

## 📚 相关文档

- [DESKTOP_APP_GUIDE.md](../../DESKTOP_APP_GUIDE.md) - 桌面应用完整使用指南
- [QUICK_REFERENCE.md](../../QUICK_REFERENCE.md) - 快速参考卡片
- [PACKAGING_QUICKSTART.md](../../PACKAGING_QUICKSTART.md) - 打包快速入门

## 💡 提示

1. **首次打包**：需要下载依赖，时间较长，请耐心等待
2. **虚拟环境**：脚本会自动创建和激活虚拟环境
3. **权限问题**：macOS 需要执行权限 `chmod +x *.sh`
4. **实时日志**：使用 `view_logs.sh` 在另一个终端窗口查看日志
5. **端口冲突**：遇到端口占用，运行 `kill_app.sh`

---

**最后更新**: 2025-12-22  
**脚本位置**: `script/desktop/`

