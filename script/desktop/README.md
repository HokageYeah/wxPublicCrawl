# 跨平台桌面脚本使用说明

本目录包含跨平台的桌面应用管理脚本，支持 Windows、macOS 和 Linux。

## 📁 脚本列表

| 脚本名称 | 功能 | 平台支持 |
|---------|------|----------|
| `general_build.py` | 跨平台打包脚本 | ✅ Windows<br>✅ macOS<br>✅ Linux |
| `general_view_logs.py` | 实时查看日志工具 | ✅ Windows<br>✅ macOS<br>✅ Linux |
| `build_mac.sh` | macOS 专用打包脚本（传统） | macOS |
| `view_logs.sh` | macOS 专用日志查看（传统） | macOS |

---

## 🚀 快速开始

### 方式一：使用跨平台脚本（推荐）

#### 1. 打包应用

```bash
# Windows, macOS, Linux 通用
python script/desktop/general_build.py
```

#### 2. 查看实时日志

```bash
# Windows, macOS, Linux 通用
python script/desktop/general_view_logs.py
```

---

### 方式二：使用平台专用脚本（传统）

#### macOS 用户

```bash
# 打包应用
./script/desktop/build_mac.sh

# 查看日志
./script/desktop/view_logs.sh
```

---

## 📦 general_build.py 功能详解

### 主要功能

1. ✅ 检查 Python 环境
2. ✅ 检查 Node.js 环境
3. ✅ 创建/检查虚拟环境
4. ✅ 安装 Python 依赖
5. ✅ 构建前端资源
6. ✅ 清理旧打包文件
7. ✅ PyInstaller 打包
8. ✅ macOS 安全属性处理

### 平台区分

| 平台 | Python 命令 | pip 路径 | 日志目录 |
|------|------------|----------|----------|
| Windows | `python` | `venv/Scripts/pip.exe` | `%APPDATA%/wx公众号工具/logs` |
| macOS | `python3` | `venv/bin/pip` | `~/Library/Logs/wx公众号工具` |
| Linux | `python3` | `venv/bin/pip` | `~/.local/share/wx公众号工具/logs` |

### 使用方法

```bash
# 1. 确保在项目根目录
cd /Users/yuye/YeahWork/Python项目/wxPublicCrawl

# 2. 运行打包脚本
python script/desktop/general_build.py

# 3. 等待打包完成（可能需要几分钟）
# 4. 查看输出文件
#    - Windows: dist/wx公众号工具.exe
#    - macOS: dist/wx公众号工具.app
#    - Linux: dist/wx公众号工具
```

---

## 📋 general_view_logs.py 功能详解

### 主要功能

1. ✅ 自动定位各平台日志目录
2. ✅ 查找最新的日志文件
3. ✅ 实时滚动显示日志内容
4. ✅ 支持中断退出（Ctrl+C）
5. ✅ 彩色输出，易于阅读

### 平台日志目录

| 平台 | 日志目录 | 日志格式 |
|------|---------|---------|
| macOS | `~/Library/Logs/wx公众号工具` | `app_YYYY-MM-DD_HHMMSS.log` |
| Windows | `%APPDATA%/wx公众号工具/logs` | `app_YYYY-MM-DD_HHMMSS.log` |
| Linux | `~/.local/share/wx公众号工具/logs` | `app_YYYY-MM-DD_HHMMSS.log` |

### 使用方法

```bash
# 1. 先运行一次桌面应用（生成日志）
# Windows
dist\wx公众号工具.exe

# macOS
open dist/wx公众号工具.app

# Linux
./dist/wx公众号工具

# 2. 查看实时日志
python script/desktop/general_view_logs.py

# 3. 日志会实时滚动显示，按 Ctrl+C 退出
```

### 特殊功能

#### 显示最新日志文件信息

脚本会显示：
- 📄 日志文件路径
- 🕐 最后修改时间
- 📊 文件大小

#### 智能提示

如果没有找到日志文件，会提示：
- ✅ 确保已运行过桌面应用
- ✅ 检查日志目录路径
- ✅ 日志文件格式说明

---

## 🎨 彩色输出

所有跨平台脚本都支持彩色输出，提升可读性。

### 颜色含义

| 颜色 | 用途 | 示例 |
|------|------|------|
| 🔵 蓝色 | 标题、目录、重要信息 | `==========标题==========` |
| 🟡 黄色 | 信息提示、步骤说明 | `▶ [1/8] 检查 Python` |
| 🟢 绿色 | 成功信息、完成状态 | `✓ Python 正常` |
| 🔴 红色 | 错误信息 | `❌ 命令执行失败` |
| ⚠️ 黄色+图标 | 警告信息 | `⚠️  这可能需要几分钟` |

### Windows 颜色支持

脚本会自动在 Windows 10+ 上启用 ANSI 颜色支持。

---

## 🔧 跨平台实现细节

### 1. Python 版本检测

```python
# Windows
if IS_WINDOWS:
    python_cmd = "python"
    pip_exe = "venv/Scripts/pip.exe"

# macOS/Linux
else:
    python_cmd = "python3"
    pip_exe = "venv/bin/pip"
```

### 2. 日志目录定位

```python
# macOS: Apple 推荐的标准位置
log_dir = Path.home() / "Library" / "Logs" / "wx公众号工具"

# Windows: 使用环境变量
log_dir = Path(os.environ.get('APPDATA')) / "wx公众号工具" / "logs"

# Linux: XDG 标准目录
log_dir = Path.home() / ".local" / "share" / "wx公众号工具" / "logs"
```

### 3. 实时日志查看

```python
# Windows: 使用 PowerShell Get-Content -Wait
subprocess.Popen(['powershell', '-Command', 'Get-Content -Path file -Wait'])

# macOS/Linux: 使用 tail -f
subprocess.Popen(['tail', '-f', file])
```

---

## 📝 注意事项

### Windows 用户

1. **编码问题**：确保使用 UTF-8 编码运行脚本
2. **PowerShell**：日志查看使用 PowerShell，需要 Windows PowerShell 3.0+
3. **权限**：可能需要管理员权限安装依赖

### macOS 用户

1. **Python 版本**：建议使用 Python 3.9+
2. **Node.js**：需要 Node.js 14+ 版本
3. **安全属性**：脚本会自动处理 macOS 的隔离属性

### Linux 用户

1. **依赖**：确保已安装 `python3-venv` 或使用系统 Python 的 venv 模块
2. **依赖包**：可能需要安装 `python3-dev` 等开发包

---

## 🐛 常见问题

### Q1: Windows 上显示乱码

**原因**：终端编码问题

**解决**：
```cmd
# 设置代码页为 UTF-8
chcp 65001
python script/desktop/general_build.py
```

### Q2: 找不到日志文件

**原因**：应用未运行或日志目录不同

**解决**：
1. 确保先运行桌面应用
2. 检查日志目录是否存在
3. 查看脚本显示的日志目录路径

### Q3: macOS 打包后无法打开

**原因**：macOS 安全限制

**解决**：
```bash
# 移除隔离属性（脚本已自动处理）
xattr -cr dist/wx公众号工具.app

# 右键应用 -> 打开
```

### Q4: Windows 日志查看失败

**原因**：PowerShell 版本过低或权限问题

**解决**：
1. 更新 PowerShell 到 5.1+
2. 使用管理员权限运行

---

## 📚 相关文件

- `wx_crawler.spec` - PyInstaller 打包配置
- `requirements.txt` - Python 依赖（macOS/Linux）
- `requirements-windows.txt` - Python 依赖（Windows）
- `.env` - 环境变量配置

---

## ✨ 更新日志

### 2026-01-07

- ✅ 创建跨平台打包脚本 `general_build.py`
- ✅ 创建跨平台日志查看工具 `general_view_logs.py`
- ✅ 添加彩色输出支持（Windows/macOS/Linux）
- ✅ 统一 Python 虚拟环境中的 pip 使用方式
- ✅ 自动处理各平台日志目录定位

---

## 🤝 贡献

如有改进建议，欢迎提交 Issue 或 Pull Request。

## 📄 许可

遵循项目主许可证。
