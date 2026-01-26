# -*- mode: python ; coding: utf-8 -*-
# ============================================================================
# PyInstaller 配置文件（自动生成）
# ============================================================================
# 平台: Darwin
# 生成时间: 自动
# ============================================================================

import sys
import os
import platform

# 加密配置（None = 不加密）
block_cipher = None

# ============================================================================
# 平台检测
# ============================================================================
is_mac = platform.system() == 'Darwin'       # macOS
is_windows = platform.system() == 'Windows'  # Windows

# 添加项目根目录到 Python 路径（确保能找到 app 模块）
sys.path.insert(0, os.path.abspath('.'))

# ============================================================================
# Analysis 阶段：分析依赖关系
# ============================================================================
# NOTE: Node.js 二进制文件会在打包前动态添加到 binaries
a = Analysis(
    ['run_desktop.py'],
    pathex=[],
    binaries=[(r'/Users/yuye/YeahWork/Python项目/wxPublicCrawl/script/desktop/node_binaries/node', 'nodejs')],
    datas=[
        ('web/dist', 'web/dist'),
        ('app/ai/prompt', 'app/ai/prompt'),
        ('app/utils/js-code', 'app/utils/js-code'),
        ('app/ai/mcp/mcp_client/mcp_settings.json', 'app/ai/mcp/mcp_client'),
        ('app/ai/mcp/mcp_client/client_manager.py', 'app/ai/mcp/mcp_client'),
        ('app/ai/mcp/mcp_client/fastmcp_client.py', 'app/ai/mcp/mcp_client'),
        ('app/ai/mcp/mcp_server/run_server.py', 'app/ai/mcp/mcp_server'),
        ('app/ai/mcp/mcp_server/fastmcp_server.py', 'app/ai/mcp/mcp_server'),
        ('app/ai/mcp/mcp_server/server_manager.py', 'app/ai/mcp/mcp_server'),
        (r'/Users/yuye/YeahWork/Python项目/wxPublicCrawl/script/desktop/playwright_browsers', 'playwright_browsers'),
        ('.env', '.'),
        ('.env.desktop', '.'),
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
        'uvicorn.lifespan',
        'uvicorn.lifespan.on',
        'sqlalchemy.sql.default_comparator',
        'pysqlite3',
        'fastmcp',
        'fastmcp.server',
        'fastmcp.client',
        'fastmcp.client.client',
        'fastmcp.utilities',
        'fastmcp.utilities.exceptions',
        'mcp',
        'mcp.server',
        'mcp.server.fastmcp',
        'mcp.client',
        'mcp.client.streamable_http',
        'mcp.client.stdio',
        'mcp.types',
        'app.ai.mcp.mcp_server.fastmcp_server',
        'app.ai.mcp.mcp_server.server_manager',
        'app.ai.mcp.mcp_client.client_manager',
        'app.ai.mcp.mcp_client.fastmcp_client',
        'app.ai.llm.ai_client',
        'app.ai.llm.mcp_llm_connect',
        'app.ai.utils.functionHandler',
        'app.ai.utils.prompt_manager',
        'app.ai.utils.register',
        'app.services.wx_public',
        'app.services.sogou_wx_public',
        'app.services.system',
        'app.services.ai_assistant',
        'app.api.endpoints.wx_public',
        'app.api.endpoints.sogou_wx_public',
        'app.api.endpoints.system',
        'pkg_resources.py2_warn',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        'matplotlib',
        'PIL',
        'PyQt5',
        'tkinter',
        'test',
        'unittest',
        'mysql.connector.plugins',
        'pymysql',
    ],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

# ============================================================================
# EXE 阶段：创建可执行文件
# ============================================================================
exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='wx公众号工具',
    debug=False,
    strip=False,
    upx=True,
    console=False,  # Windows 显示控制台便于调试

    # --------------------------------------------------------------------
    # 🎨 应用图标配置（macOS）
    # --------------------------------------------------------------------
    icon='resources/icon.icns',  # macOS 图标（.icns 格式）
    # 使用方法：
    # 1. 准备 icon.icns 文件（推荐 512x512）
    # 2. 放置在 resources/ 目录
    # 3. 取消上面的注释
    # 4. 在线转换工具：https://cloudconvert.com/png-to-icns

    bootloader_ignore_signals=False,
    argv_emulation=False,
    disable_windowed_traceback=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)

# ============================================================================
# COLLECT 阶段：收集所有文件
# ============================================================================
coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='wx公众号工具',
)

# ============================================================================
# BUNDLE 阶段：创建 macOS .app 包（仅 macOS）
# ============================================================================
if is_mac:
    app = BUNDLE(
        coll,
        name='wx公众号工具.app',

        # --------------------------------------------------------------------
        # 🎨 应用图标（macOS Bundle）
        # --------------------------------------------------------------------
        icon='resources/icon.icns',  # .app 包的图标
        # 使用方法：
        # 1. 准备 icon.icns 文件（macOS 图标格式）
        # 2. 放置在 resources/ 目录
        # 3. 取消此行注释
        # 4. 可以使用在线工具将 PNG 转换为 ICNS：
        #    https://cloudconvert.com/png-to-icns

        bundle_identifier='com.wxcrawler.desktop',
        info_plist={
            'NSHighResolutionCapable': 'True',
            'LSUIElement': False,
            'CFBundleShortVersionString': '1.0.0',
            'CFBundleVersion': '1.0.0',
            'NSAppTransportSecurity': {
                'NSAllowsArbitraryLoads': True
            },
        },
    )
