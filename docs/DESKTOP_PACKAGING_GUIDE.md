# 桌面应用打包指南

## 技术栈概述

本项目使用以下技术栈打包为桌面应用：

- **后端**: FastAPI + Python
- **前端**: Vue 3 + TypeScript
- **桌面容器**: PyWebView (跨平台 WebView)
- **打包工具**: PyInstaller

## ✅ 可行性分析

**结论**: 该方案完全可行，可以在 Mac 和 Windows 上运行。

### 支持的平台

| 平台 | PyWebView 支持 | PyInstaller 支持 | WebView 引擎 |
|------|---------------|-----------------|-------------|
| macOS | ✅ | ✅ | WebKit |
| Windows | ✅ | ✅ | EdgeChromium / MSHTML |
| Linux | ✅ | ✅ | GTK WebKit |

## ⚠️ 重要限制

### PyInstaller 不支持交叉编译

这是**最关键**的限制：

- 在 Mac 上打包 → 只能生成 Mac 应用 (.app)
- 在 Windows 上打包 → 只能生成 Windows 应用 (.exe)
- **无法在一个平台上为另一个平台打包**

### 解决方案

需要准备两个打包环境：

1. **Mac 环境** (当前你所在的环境)
   - 打包生成 macOS 应用
   
2. **Windows 环境** (虚拟机 / 双系统 / 云服务器)
   - 打包生成 Windows 应用

## 📦 打包流程

### 前置准备（两个平台都需要）

1. **安装 Python 3.9+**
   ```bash
   python --version  # 确保 3.9 或更高版本
   ```

2. **安装依赖**
   ```bash
   # 创建虚拟环境
   python -m venv venv
   
   # 激活虚拟环境
   # Mac/Linux:
   source venv/bin/activate
   # Windows:
   venv\Scripts\activate
   
   # 安装 Python 依赖
   pip install -r requirements.txt
   pip install pyinstaller pywebview
   ```

3. **构建前端**
   ```bash
   cd web
   npm install
   npm run build  # 生成 web/dist 目录
   cd ..
   ```

### 在 Mac 上打包

```bash
# 1. 确保前端已构建
ls web/dist  # 确认目录存在

# 2. 清理之前的打包文件
rm -rf build dist

# 3. 使用 spec 文件打包
pyinstaller wx_crawler.spec

# 4. 打包完成
# 生成的应用在: dist/WxPublicCrawler/WxPublicCrawler
# 或者: dist/WxPublicCrawler.app (如果配置为 onefile)
```

**Mac 特定设置**：

如果需要创建 .app 包，修改 `wx_crawler.spec`：

```python
app = BUNDLE(
    coll,
    name='WxPublicCrawler.app',
    icon=None,  # 可以添加 .icns 图标文件
    bundle_identifier='com.yourcompany.wxpubliccrawler',
    info_plist={
        'NSHighResolutionCapable': 'True',
        'LSUIElement': False,  # False = 显示在 Dock
    },
)
```

### 在 Windows 上打包

```bash
# 1. 确保前端已构建
dir web\dist  # 确认目录存在

# 2. 清理之前的打包文件
rmdir /s /q build dist

# 3. 使用 spec 文件打包
pyinstaller wx_crawler.spec

# 4. 打包完成
# 生成的应用在: dist\WxPublicCrawler\WxPublicCrawler.exe
```

**Windows 特定设置**：

在 `wx_crawler.spec` 中添加图标（可选）：

```python
exe = EXE(
    ...
    icon='icon.ico',  # Windows 图标文件
    ...
)
```

## 🔧 优化配置文件

### 当前配置分析

你的 `wx_crawler.spec` 配置总体不错，但有几点需要注意：

#### 1. 数据文件路径

```python
datas=[
    ('web/dist', 'web/dist'),  # ✅ 正确
    ('alembic.ini', '.'),      # ⚠️ 如果不需要数据库迁移，可以移除
    ('app', 'app'),            # ⚠️ 通常不需要，Analysis 会自动处理
    ('.env', '.'),             # ⚠️ 建议不要打包 .env，而是让用户配置
],
```

**建议的配置**：

```python
datas=[
    ('web/dist', 'web/dist'),  # 前端资源
    # 如果需要其他静态资源，在这里添加
],
```

#### 2. 环境变量处理

**不要打包 .env 文件**，原因：
- 包含敏感信息（数据库密码等）
- 不同用户的配置不同

**推荐方案**：

创建 `app/config/default_config.py`：

```python
import os

class Config:
    # 默认配置
    DATABASE_URL = os.getenv('DATABASE_URL', 'sqlite:///./wxcrawl.db')
    API_HOST = os.getenv('API_HOST', '127.0.0.1')
    API_PORT = int(os.getenv('API_PORT', '18000'))
    
    @classmethod
    def load_from_user_config(cls):
        """从用户配置目录加载配置"""
        import platform
        if platform.system() == 'Darwin':  # Mac
            config_dir = os.path.expanduser('~/Library/Application Support/WxPublicCrawler')
        elif platform.system() == 'Windows':
            config_dir = os.path.expanduser('~/AppData/Local/WxPublicCrawler')
        else:  # Linux
            config_dir = os.path.expanduser('~/.config/WxPublicCrawler')
        
        config_file = os.path.join(config_dir, 'config.ini')
        # 加载配置逻辑...
```

#### 3. 日志文件路径

修改 `run_desktop.py`，将日志写入用户目录：

```python
import platform
import os

def get_user_data_dir():
    """获取用户数据目录"""
    if platform.system() == 'Darwin':  # Mac
        return os.path.expanduser('~/Library/Application Support/WxPublicCrawler')
    elif platform.system() == 'Windows':
        return os.path.expanduser('~/AppData/Local/WxPublicCrawler')
    else:  # Linux
        return os.path.expanduser('~/.local/share/WxPublicCrawler')

# 确保目录存在
USER_DATA_DIR = get_user_data_dir()
os.makedirs(USER_DATA_DIR, exist_ok=True)

# 配置日志路径
LOG_DIR = os.path.join(USER_DATA_DIR, 'logs')
os.makedirs(LOG_DIR, exist_ok=True)
```

### 优化后的 wx_crawler.spec

```python
# -*- mode: python ; coding: utf-8 -*-
import sys
import os
import platform

block_cipher = None

# 根据平台设置不同的配置
is_mac = platform.system() == 'Darwin'
is_windows = platform.system() == 'Windows'

# 添加项目根目录到 python 路径
sys.path.insert(0, os.path.abspath('.'))

a = Analysis(
    ['run_desktop.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('web/dist', 'web/dist'),  # 前端构建产物（必需）
        # 如果有其他静态资源，在这里添加
        # ('static', 'static'),
    ],
    hiddenimports=[
        # Uvicorn 相关
        'uvicorn.logging',
        'uvicorn.loops',
        'uvicorn.loops.auto',
        'uvicorn.protocols',
        'uvicorn.protocols.http',
        'uvicorn.protocols.http.auto',
        'uvicorn.protocols.websockets',
        'uvicorn.protocols.websockets.auto',
        'uvicorn.lifespan.on',
        
        # 数据库相关（如果使用 MySQL）
        'mysql.connector.locales.eng.client_error',
        
        # 项目模块
        'app.services.wx_public',
        'app.api.endpoints.wx_public',
        'app.api.endpoints.sogou_wx_public',
        'app.api.endpoints.system',
        
        # SQLAlchemy
        'sqlalchemy.sql.default_comparator',
        
        # 其他可能需要的模块
        'pkg_resources.py2_warn',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        # 排除不需要的模块以减小体积
        'matplotlib',
        'PIL',
        'PyQt5',
        'tkinter',
    ],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='WxPublicCrawler',
    debug=False,  # 发布版本设为 False
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,  # GUI 模式设为 False，调试时可设为 True
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='icon.ico' if is_windows else 'icon.icns' if is_mac else None,  # 图标文件
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='WxPublicCrawler',
)

# Mac 特定：创建 .app 包
if is_mac:
    app = BUNDLE(
        coll,
        name='WxPublicCrawler.app',
        icon='icon.icns',  # Mac 图标（.icns 格式）
        bundle_identifier='com.yourcompany.wxpubliccrawler',
        info_plist={
            'NSHighResolutionCapable': 'True',
            'LSUIElement': False,  # False = 显示在 Dock
            'CFBundleShortVersionString': '1.0.0',
            'CFBundleVersion': '1.0.0',
        },
    )
```

## 🎨 创建应用图标

### Mac 图标 (.icns)

1. 准备一张 1024x1024 的 PNG 图片
2. 使用在线工具转换：https://cloudconvert.com/png-to-icns
3. 或使用命令行：

```bash
mkdir icon.iconset
sips -z 16 16     icon.png --out icon.iconset/icon_16x16.png
sips -z 32 32     icon.png --out icon.iconset/icon_16x16@2x.png
sips -z 32 32     icon.png --out icon.iconset/icon_32x32.png
sips -z 64 64     icon.png --out icon.iconset/icon_32x32@2x.png
sips -z 128 128   icon.png --out icon.iconset/icon_128x128.png
sips -z 256 256   icon.png --out icon.iconset/icon_128x128@2x.png
sips -z 256 256   icon.png --out icon.iconset/icon_256x256.png
sips -z 512 512   icon.png --out icon.iconset/icon_256x256@2x.png
sips -z 512 512   icon.png --out icon.iconset/icon_512x512.png
sips -z 1024 1024 icon.png --out icon.iconset/icon_512x512@2x.png
iconutil -c icns icon.iconset
```

### Windows 图标 (.ico)

1. 准备一张 256x256 的 PNG 图片
2. 使用在线工具转换：https://convertio.co/png-ico/
3. 或使用 ImageMagick：

```bash
convert icon.png -define icon:auto-resize=256,128,64,48,32,16 icon.ico
```

## 📋 完整打包脚本

### Mac 打包脚本 (build_mac.sh)

```bash
#!/bin/bash
set -e

echo "=== 公众号爬虫助手 - Mac 打包脚本 ==="

# 1. 检查 Python 版本
echo "检查 Python 版本..."
python3 --version

# 2. 检查虚拟环境
if [ ! -d "venv" ]; then
    echo "创建虚拟环境..."
    python3 -m venv venv
fi

# 3. 激活虚拟环境
echo "激活虚拟环境..."
source venv/bin/activate

# 4. 安装依赖
echo "安装 Python 依赖..."
pip install -r requirements.txt
pip install pyinstaller pywebview

# 5. 构建前端
echo "构建前端..."
cd web
if [ ! -d "node_modules" ]; then
    npm install
fi
npm run build
cd ..

# 6. 清理旧的打包文件
echo "清理旧的打包文件..."
rm -rf build dist

# 7. 打包
echo "开始打包..."
pyinstaller wx_crawler.spec

# 8. 完成
echo "=== 打包完成 ==="
echo "应用位置: dist/WxPublicCrawler.app"
echo ""
echo "测试运行:"
echo "open dist/WxPublicCrawler.app"
```

### Windows 打包脚本 (build_windows.bat)

```batch
@echo off
echo === 公众号爬虫助手 - Windows 打包脚本 ===

REM 1. 检查 Python 版本
echo 检查 Python 版本...
python --version

REM 2. 检查虚拟环境
if not exist venv (
    echo 创建虚拟环境...
    python -m venv venv
)

REM 3. 激活虚拟环境
echo 激活虚拟环境...
call venv\Scripts\activate

REM 4. 安装依赖
echo 安装 Python 依赖...
pip install -r requirements.txt
pip install pyinstaller pywebview

REM 5. 构建前端
echo 构建前端...
cd web
if not exist node_modules (
    npm install
)
npm run build
cd ..

REM 6. 清理旧的打包文件
echo 清理旧的打包文件...
if exist build rmdir /s /q build
if exist dist rmdir /s /q dist

REM 7. 打包
echo 开始打包...
pyinstaller wx_crawler.spec

REM 8. 完成
echo === 打包完成 ===
echo 应用位置: dist\WxPublicCrawler\WxPublicCrawler.exe
echo.
echo 测试运行:
echo dist\WxPublicCrawler\WxPublicCrawler.exe

pause
```

## 🐛 常见问题

### 1. ModuleNotFoundError

**问题**: 打包后运行提示找不到模块

**解决**: 在 `hiddenimports` 中添加缺失的模块：

```python
hiddenimports=[
    # ... 其他模块
    'missing_module_name',
],
```

### 2. 前端资源加载失败

**问题**: 打包后前端页面空白或资源 404

**解决**: 
1. 确认 `web/dist` 已正确打包进去
2. 检查 `main.py` 中静态文件挂载路径
3. 确认 `run_desktop.py` 中的 URL 正确

### 3. 数据库文件路径问题

**问题**: 找不到数据库文件或无法写入

**解决**: 使用用户数据目录（见上文"日志文件路径"部分）

### 4. Mac 安全警告

**问题**: Mac 提示"无法打开，因为它来自身份不明的开发者"

**解决**:
```bash
# 方法 1: 在系统偏好设置中允许
# 系统偏好设置 > 安全性与隐私 > 通用 > 仍要打开

# 方法 2: 移除隔离属性
xattr -cr dist/WxPublicCrawler.app

# 方法 3: 代码签名（需要 Apple Developer 账号）
codesign --force --deep --sign - dist/WxPublicCrawler.app
```

### 5. Windows Defender 警告

**问题**: Windows Defender 报毒或阻止运行

**解决**:
- 正常现象，PyInstaller 打包的应用常被误报
- 添加到 Windows Defender 白名单
- 或获取代码签名证书（需购买）

### 6. 应用体积过大

**问题**: 打包后应用体积达到 100MB+

**优化方案**:
1. 排除不需要的模块（在 `excludes` 中添加）
2. 使用 UPX 压缩（已在 spec 中启用）
3. 移除未使用的 Python 包

## 📊 预期应用体积

| 平台 | 大致体积 | 说明 |
|------|---------|------|
| macOS | 80-120 MB | 包含 Python 运行时 + 依赖 |
| Windows | 60-100 MB | 包含 Python 运行时 + 依赖 |

## 🚀 分发建议

### Mac

1. **DMG 安装包** (推荐)
   - 使用工具：create-dmg 或 dmgbuild
   - 用户体验好，拖拽安装

2. **ZIP 压缩包**
   - 简单直接
   - 用户解压即用

### Windows

1. **安装程序** (推荐)
   - 使用 Inno Setup 或 NSIS 创建安装程序
   - 可以设置开始菜单快捷方式

2. **ZIP 压缩包**
   - 绿色版，无需安装

## 📝 发布检查清单

打包前检查：

- [ ] 前端已构建 (`web/dist` 存在)
- [ ] 所有依赖已安装
- [ ] `.env` 等敏感文件未打包
- [ ] 图标文件已准备
- [ ] 版本号已更新

打包后测试：

- [ ] 应用能正常启动
- [ ] 前端页面正常显示
- [ ] API 接口正常工作
- [ ] 数据库读写正常
- [ ] 文件保存路径正确
- [ ] 日志正常记录

## 🔗 相关资源

- [PyInstaller 官方文档](https://pyinstaller.org/)
- [PyWebView 官方文档](https://pywebview.flowrl.com/)
- [FastAPI 文档](https://fastapi.tiangolo.com/)
- [Vue 3 文档](https://vuejs.org/)

## 💡 总结

**你的方案完全可行**，主要注意以下几点：

1. ✅ 在 Mac 和 Windows 上**分别打包**
2. ✅ 使用用户数据目录存储配置和日志
3. ✅ 不要打包敏感信息（如 .env）
4. ✅ 充分测试打包后的应用
5. ✅ 准备好图标和分发方案

祝打包顺利！🎉

