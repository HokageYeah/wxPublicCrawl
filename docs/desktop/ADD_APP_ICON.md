# 添加应用图标指南

## 📝 快速步骤

### 1. 准备图标文件

**macOS (.icns)**:
- 推荐尺寸：512x512 或 1024x1024
- 格式：.icns（包含多个尺寸）

**Windows (.ico)**:
- 包含多个尺寸：16x16, 32x32, 48x48, 256x256
- 格式：.ico

### 2. 放置图标文件

```
wxPublicCrawl/
├── resources/          # 创建此目录
│   ├── icon.icns      # macOS 图标
│   └── icon.ico       # Windows 图标
└── wx_crawler.spec    # 配置文件
```

### 3. 修改 wx_crawler.spec

#### 方式1：在 EXE 部分添加（Windows/macOS 通用）

```python
exe = EXE(
    # ... 其他配置 ...
    
    # 添加图标（根据平台选择）
    icon='resources/icon.icns',  # macOS
    # 或
    icon='resources/icon.ico',   # Windows
)
```

#### 方式2：在 BUNDLE 部分添加（仅 macOS）

```python
if is_mac:
    app = BUNDLE(
        coll,
        name='WxPublicCrawler.app',
        icon='resources/icon.icns',  # .app 包图标
        # ... 其他配置 ...
    )
```

### 4. 重新打包

```bash
# macOS
script/desktop/build_mac.sh

# Windows
script\desktop\build_windows.bat
```

## 🎨 图标制作工具

### 在线工具

**PNG → ICNS (macOS)**:
- https://cloudconvert.com/png-to-icns
- https://anyconv.com/png-to-icns-converter/

**PNG → ICO (Windows)**:
- https://cloudconvert.com/png-to-ico
- https://www.icoconverter.com/

### 命令行工具

**macOS - 使用 iconutil**:

```bash
# 1. 创建 iconset 目录
mkdir icon.iconset

# 2. 准备不同尺寸的 PNG 图片
cp icon_16x16.png icon.iconset/icon_16x16.png
cp icon_32x32.png icon.iconset/icon_16x16@2x.png
cp icon_32x32.png icon.iconset/icon_32x32.png
cp icon_64x64.png icon.iconset/icon_32x32@2x.png
cp icon_128x128.png icon.iconset/icon_128x128.png
cp icon_256x256.png icon.iconset/icon_128x128@2x.png
cp icon_256x256.png icon.iconset/icon_256x256.png
cp icon_512x512.png icon.iconset/icon_256x256@2x.png
cp icon_512x512.png icon.iconset/icon_512x512.png
cp icon_1024x1024.png icon.iconset/icon_512x512@2x.png

# 3. 生成 .icns 文件
iconutil -c icns icon.iconset
```

**Windows - 使用 ImageMagick**:

```bash
# 安装 ImageMagick
# Windows: choco install imagemagick
# macOS: brew install imagemagick

# 生成 .ico 文件（包含多个尺寸）
magick convert icon.png -define icon:auto-resize=256,128,96,64,48,32,16 icon.ico
```

## 📋 图标规范

### macOS .icns 包含的尺寸

| 尺寸 | 标准 | Retina |
|------|------|--------|
| 16x16 | icon_16x16.png | icon_16x16@2x.png (32x32) |
| 32x32 | icon_32x32.png | icon_32x32@2x.png (64x64) |
| 128x128 | icon_128x128.png | icon_128x128@2x.png (256x256) |
| 256x256 | icon_256x256.png | icon_256x256@2x.png (512x512) |
| 512x512 | icon_512x512.png | icon_512x512@2x.png (1024x1024) |

### Windows .ico 推荐尺寸

- 16x16 (小图标)
- 32x32 (常规图标)
- 48x48 (大图标)
- 256x256 (超大图标)

## 🔧 完整示例

### 示例：添加统一图标

```python
# wx_crawler.spec

# ... 前面的配置 ...

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='WxPublicCrawler',
    debug=False,
    # ✨ 添加图标
    icon='resources/icon.icns' if is_mac else 'resources/icon.ico',
    # ... 其他配置 ...
)

# ... COLLECT 配置 ...

if is_mac:
    app = BUNDLE(
        coll,
        name='WxPublicCrawler.app',
        bundle_identifier='com.wxcrawler.desktop',
        # ✨ .app 包图标
        icon='resources/icon.icns',
        info_plist={
            'NSHighResolutionCapable': 'True',
            'LSUIElement': False,
            'CFBundleShortVersionString': '1.0.0',
            'CFBundleVersion': '1.0.0',
            # ✨ 显示名称（支持中文）
            'CFBundleDisplayName': '公众号爬虫助手',
            'NSAppTransportSecurity': {
                'NSAllowsArbitraryLoads': True
            },
        },
    )
```

## ✅ 验证图标

### macOS

```bash
# 1. 打包
script/desktop/build_mac.sh

# 2. 在 Finder 中查看
open dist/

# 3. 检查 .app 图标
# 应该显示自定义图标而不是默认图标
```

### Windows

```batch
REM 1. 打包
script\desktop\build_windows.bat

REM 2. 在资源管理器中查看
explorer dist\WxPublicCrawler

REM 3. 检查 .exe 图标
REM 应该显示自定义图标
```

## 🐛 常见问题

### Q: 图标不显示怎么办？

**A**: 
1. 检查图标文件路径是否正确
2. 确保图标文件存在
3. macOS 可能需要清除图标缓存：
   ```bash
   sudo rm -rf /Library/Caches/com.apple.iconservices.store
   sudo find /private/var/folders/ -name com.apple.iconservices -exec rm -rf {} \;
   killall Dock
   ```
4. Windows 可能需要重启或清除缓存：
   ```batch
   ie4uinit.exe -show
   ```

### Q: 图标模糊怎么办？

**A**: 
- 确保提供高分辨率的源图片（至少 512x512）
- macOS 使用 Retina 尺寸（@2x）
- Windows 包含多个尺寸的图标

### Q: 打包后图标没有变化？

**A**: 
- 确保重新打包前清理了旧文件：`rm -rf dist build`
- 检查 .spec 文件的 icon 配置是否正确
- 查看打包日志是否有图标相关的警告

## 📚 相关资源

- [Apple Human Interface Guidelines - App Icon](https://developer.apple.com/design/human-interface-guidelines/app-icons)
- [Windows App Icon Guidelines](https://learn.microsoft.com/en-us/windows/apps/design/style/iconography/app-icon-design)
- [PyInstaller Documentation - Adding an Icon](https://pyinstaller.org/en/stable/usage.html#cmdoption-icon)

---

**提示**: 图标是应用的第一印象，建议设计简洁、辨识度高的图标！

