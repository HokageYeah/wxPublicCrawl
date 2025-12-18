# -*- mode: python ; coding: utf-8 -*-
import sys
import os

block_cipher = None

# 添加项目根目录到 python 路径，以帮助查找模块
sys.path.insert(0, os.path.abspath('.'))

a = Analysis(
    ['run_desktop.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('web/dist', 'web/dist'),  # 包含前端构建产物
        ('alembic.ini', '.'),      # 如果需要，包含 alembic 配置
        ('app', 'app'),            # 显式包含 app 包（虽然 Analysis 通常能找到导入）
        # .env 文件通常不打包，而是期望在当前工作目录中，或者我们打包默认配置
        # ('src/.env', '.'),
    ],
    hiddenimports=[
        'uvicorn.logging',
        'uvicorn.loops',
        'uvicorn.loops.auto',
        'uvicorn.protocols',
        'uvicorn.protocols.http',
        'uvicorn.protocols.http.auto',
        'uvicorn.protocols.websockets',
        'uvicorn.protocols.websockets.auto',
        'uvicorn.lifespan.on',
        'mysql.connector.locales.eng.client_error',
        'app.services.wx_public', # 确保服务被找到
        'app.api.endpoints.wx_public',
        'app.api.endpoints.sogou_wx_public',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
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
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False, # 设置为 True 用于调试，GUI 模式请设置为 False
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
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
