# 桌面应用打包快速入门

## 🎯 方案可行性

**✅ 你的方案完全可行！** 可以打包成桌面应用在 Mac 和 Windows 上运行。

## ⚠️ 最重要的限制

**PyInstaller 不支持交叉编译**

- 在 Mac 上打包 → 只能生成 Mac 应用
- 在 Windows 上打包 → 只能生成 Windows 应用
- **无法在一个平台为另一个平台打包**

**解决方案**: 需要在两个平台上分别打包。

## 🚀 快速开始

### 在 Mac 上打包

```bash
# 1. 运行打包脚本
./build_mac.sh

# 2. 测试应用
open dist/WxPublicCrawler.app

# 3. 创建分发包
cd dist
zip -r WxPublicCrawler-mac.zip WxPublicCrawler.app
```

### 在 Windows 上打包

```batch
REM 1. 运行打包脚本
build_windows.bat

REM 2. 测试应用
dist\WxPublicCrawler\WxPublicCrawler.exe

REM 3. 创建分发包
cd dist
tar -a -c -f WxPublicCrawler-windows.zip WxPublicCrawler
```

## 📋 打包前准备

### 必需条件

1. **Python 3.9+**
   ```bash
   python3 --version  # Mac
   python --version   # Windows
   ```

2. **Node.js**
   ```bash
   node --version
   npm --version
   ```

3. **依赖安装**
   ```bash
   pip install -r requirements.txt
   pip install pyinstaller pywebview
   cd web && npm install && cd ..
   ```

4. **前端构建**
   ```bash
   cd web
   npm run build  # 生成 web/dist
   cd ..
   ```

## 📁 关键文件

| 文件 | 用途 |
|------|------|
| `wx_crawler.spec` | PyInstaller 配置文件（已优化） |
| `build_mac.sh` | Mac 自动打包脚本 |
| `build_windows.bat` | Windows 自动打包脚本 |
| `run_desktop.py` | 桌面应用入口文件 |
| `web/dist/` | 前端构建产物（必需） |

## 🔧 已优化的配置

### 移除的内容（重要）

❌ **不再打包以下内容**：

1. `.env` 文件（包含敏感信息）
2. `alembic.ini`（数据库迁移配置）
3. `app` 目录（PyInstaller 自动处理）
4. MySQL Connector 插件（改用 SQLite）

### 新增的内容

✅ **新增以下优化**：

1. 自动创建 Mac .app 包
2. 排除不需要的模块以减小体积
3. 添加更多隐藏导入以避免运行时错误
4. 支持添加应用图标
5. **使用 SQLite 数据库**（适合桌面应用）

### 数据库配置

**桌面应用默认使用 SQLite**，无需安装数据库服务器：

- **Mac**: `~/Library/Application Support/WxPublicCrawler/wxpublic.db`
- **Windows**: `%APPDATA%\Local\WxPublicCrawler\wxpublic.db`
- **Linux**: `~/.local/share/WxPublicCrawler/wxpublic.db`

数据库文件会在首次启动时自动创建。

## 📦 预期结果

### Mac

```
dist/
└── WxPublicCrawler.app/     # Mac 应用包
    ├── Contents/
    │   ├── MacOS/
    │   │   └── WxPublicCrawler   # 可执行文件
    │   ├── Resources/
    │   │   └── web/
    │   │       └── dist/         # 前端资源
    │   └── Info.plist
```

**应用大小**: 约 80-120 MB

### Windows

```
dist/
└── WxPublicCrawler/
    ├── WxPublicCrawler.exe      # 可执行文件
    ├── web/
    │   └── dist/                # 前端资源
    └── _internal/               # 依赖文件
```

**应用大小**: 约 60-100 MB

## 🐛 常见问题

### 1. 打包后运行提示找不到模块

**解决**: 在 `wx_crawler.spec` 的 `hiddenimports` 中添加缺失的模块：

```python
hiddenimports=[
    # ... 其他模块
    'missing_module_name',  # 添加缺失的模块
],
```

### 2. 前端页面空白或资源 404

**检查清单**:
- [ ] `web/dist` 目录存在且不为空
- [ ] `wx_crawler.spec` 中包含 `('web/dist', 'web/dist')`
- [ ] `run_desktop.py` 中的 URL 正确

### 3. Mac 提示"无法打开"

```bash
# 移除隔离属性（build_mac.sh 已自动处理）
xattr -cr dist/WxPublicCrawler.app
```

### 4. Windows Defender 报毒

这是正常现象，PyInstaller 打包的应用常被误报。

**解决方案**:
- 添加到 Windows Defender 白名单
- 或购买代码签名证书

### 5. 应用启动慢

第一次启动会较慢（5-10秒），因为需要：
- 解压临时文件
- 启动 FastAPI 服务器
- 加载 WebView

**优化建议**: 在 `run_desktop.py` 中增加启动等待时间。

## 📖 详细文档

查看完整的打包指南：[DESKTOP_PACKAGING_GUIDE.md](./docs/DESKTOP_PACKAGING_GUIDE.md)

内容包括：
- 详细的配置说明
- 图标制作方法
- 分发方案建议
- 完整的故障排除指南

## 🎨 添加应用图标（可选）

### 准备图标

1. **Mac**: 需要 `.icns` 格式（1024x1024）
2. **Windows**: 需要 `.ico` 格式（256x256）

### 在线转换工具

- PNG to ICNS: https://cloudconvert.com/png-to-icns
- PNG to ICO: https://convertio.co/png-ico/

### 启用图标

在 `wx_crawler.spec` 中取消注释：

```python
exe = EXE(
    ...
    icon='icon.ico' if is_windows else 'icon.icns' if is_mac else None,
    ...
)

# Mac 特定
if is_mac:
    app = BUNDLE(
        ...
        icon='icon.icns',  # 取消注释这一行
        ...
    )
```

## 📊 打包流程图

```
前端构建 (npm run build)
    ↓
清理旧文件 (rm -rf build dist)
    ↓
PyInstaller 分析 (wx_crawler.spec)
    ↓
收集依赖和资源
    ↓
生成可执行文件
    ↓
[Mac] 创建 .app 包
    ↓
完成
```

## ✅ 发布前检查清单

打包前：

- [ ] 前端已构建 (`web/dist` 存在)
- [ ] 所有依赖已安装
- [ ] `.env` 等敏感文件未打包
- [ ] 版本号已更新
- [ ] 图标已准备（可选）

打包后测试：

- [ ] 应用能正常启动
- [ ] 前端页面正常显示
- [ ] API 接口正常工作
- [ ] 数据库读写正常
- [ ] 文件保存路径正确
- [ ] 日志正常记录
- [ ] 在干净的系统上测试（无 Python 环境）

## 🚀 分发建议

### Mac

**推荐**: 创建 DMG 安装包

```bash
# 使用 create-dmg（需要安装）
brew install create-dmg

create-dmg \
  --volname "公众号爬虫助手" \
  --window-pos 200 120 \
  --window-size 800 400 \
  --icon-size 100 \
  --icon "WxPublicCrawler.app" 200 190 \
  --hide-extension "WxPublicCrawler.app" \
  --app-drop-link 600 185 \
  "WxPublicCrawler-Installer.dmg" \
  "dist/"
```

### Windows

**推荐**: 使用 Inno Setup 创建安装程序

1. 下载 [Inno Setup](https://jrsoftware.org/isinfo.php)
2. 创建 installer.iss 脚本
3. 生成 Setup.exe 安装程序

## 💡 总结

你的方案 **完全可行**，主要注意：

1. ✅ 在 Mac 和 Windows 上**分别打包**
2. ✅ 使用提供的自动化脚本
3. ✅ 不要打包敏感信息
4. ✅ 充分测试打包后的应用
5. ✅ 准备好分发方案

**祝打包顺利！** 🎉

如有问题，查看详细文档或提出 issue。

