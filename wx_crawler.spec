# -*- mode: python ; coding: utf-8 -*-
import sys
import os
import platform

block_cipher = None

# 根据平台设置不同的配置
is_mac = platform.system() == 'Darwin'
is_windows = platform.system() == 'Windows'

# 添加项目根目录到 python 路径，以帮助查找模块
sys.path.insert(0, os.path.abspath('.'))

a = Analysis(
    ['run_desktop.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('web/dist', 'web/dist'),  # 包含前端构建产物（必需）
        # 注意：不要打包 .env 文件（包含敏感信息）
        # 注意：不要打包 app 目录（Analysis 会自动处理）
        # 如果需要其他静态资源，在这里添加
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
        
        # 数据库相关 - SQLite（桌面应用默认使用）
        'sqlalchemy.sql.default_comparator',
        'pysqlite3',  # SQLite 驱动
        
        # 项目模块
        'app.services.wx_public',
        'app.services.sogou_wx_public',
        'app.services.system',
        'app.api.endpoints.wx_public',
        'app.api.endpoints.sogou_wx_public',
        'app.api.endpoints.system',
        
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
        'test',
        'unittest',
        # 桌面应用使用 SQLite，排除 MySQL 相关模块
        'mysql.connector.plugins',
        'pymysql',
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
    debug=False,  # 发布版本设为 False，调试时可设为 True
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,  # GUI 模式设为 False，调试时可设为 True 查看日志
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    # icon='icon.ico' if is_windows else 'icon.icns' if is_mac else None,  # 取消注释以添加图标
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
        # icon='icon.icns',  # 取消注释以添加 Mac 图标（.icns 格式）
        bundle_identifier='com.wxcrawler.desktop',
        info_plist={
            'NSHighResolutionCapable': 'True',
            'LSUIElement': False,  # False = 显示在 Dock
            'CFBundleShortVersionString': '1.0.0',
            'CFBundleVersion': '1.0.0',
            'NSAppTransportSecurity': {
                'NSAllowsArbitraryLoads': True  # 允许本地 HTTP 请求
            },
        },
    )
