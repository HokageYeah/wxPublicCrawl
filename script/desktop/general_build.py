#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
import subprocess
import shutil
import platform
from pathlib import Path

# 导入公共日志颜色模块
from log_color import color_print, header, info, success, error, warning, Colors, step_info


# =========================
# 平台判断
# =========================

SYSTEM = platform.system()
IS_WINDOWS = SYSTEM == "Windows"
IS_MAC = SYSTEM == "Darwin"


# =========================
# 项目根目录
# =========================

SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = SCRIPT_DIR.parent.parent
os.chdir(PROJECT_ROOT)


# =========================
# 工具函数
# =========================

def run(cmd, cwd=None):
    """执行命令，失败直接退出（等价 set -e）"""
    color_print(f"\n>>> {cmd}")
    result = subprocess.run(
        cmd,
        cwd=cwd,
        shell=True,
        text=True
    )
    if result.returncode != 0:
        error(f"命令执行失败: {cmd}")


# =========================
# 动态生成 spec 文件
# =========================

# def generate_spec_file():
#     """动态生成 wx_crawler.spec 文件"""
    
#     spec_path = PROJECT_ROOT / "wx_crawler.spec"
    
#     # spec 文件模板
#     spec_content = f'''# -*- mode: python ; coding: utf-8 -*-
# # ============================================================================
# # PyInstaller 配置文件（自动生成）
# # ============================================================================
# # 平台: {SYSTEM}
# # 生成时间: 自动
# # ============================================================================

# import sys
# import os
# import platform

# # 加密配置（None = 不加密）
# block_cipher = None

# # ============================================================================
# # 平台检测
# # ============================================================================
# is_mac = platform.system() == 'Darwin'       # macOS
# is_windows = platform.system() == 'Windows'  # Windows

# # 添加项目根目录到 Python 路径（确保能找到 app 模块）
# sys.path.insert(0, os.path.abspath('.'))

# # ============================================================================
# # Analysis 阶段：分析依赖关系
# # ============================================================================
# a = Analysis(
#     # --------------------------------------------------------------------
#     # 入口脚本：应用的主入口文件
#     # --------------------------------------------------------------------
#     ['run_desktop.py'],
    
#     # --------------------------------------------------------------------
#     # pathex：额外的搜索路径（已通过 sys.path 添加，这里留空）
#     # --------------------------------------------------------------------
#     pathex=[],
    
#     # --------------------------------------------------------------------
#     # binaries：需要打包的二进制文件（如 .dll、.so、.dylib）
#     # 格式：[('源路径', '目标路径')]
#     # --------------------------------------------------------------------
#     binaries=[],
    
#     # --------------------------------------------------------------------
#     # datas：需要打包的数据文件（非代码文件）
#     # 格式：[('源路径', '目标路径')]
#     # --------------------------------------------------------------------
#     datas=[
#         ('web/dist', 'web/dist'),  # Vue3 前端构建产物（HTML/CSS/JS）
#         ('app/ai/prompt', 'app/ai/prompt'),  # AI 提示词文件
        
#         # MCP 相关文件（完整打包）
#         ('app/ai/mcp/mcp_client/mcp_settings.json', 'app/ai/mcp/mcp_client'),  # MCP 设置文件
#         ('app/ai/mcp/mcp_client/client_manager.py', 'app/ai/mcp/mcp_client'),  # MCP 客户端管理器
#         ('app/ai/mcp/mcp_client/fastmcp_client.py', 'app/ai/mcp/mcp_client'),  # MCP 客户端实现
#         ('app/ai/mcp/mcp_server/run_server.py', 'app/ai/mcp/mcp_server'),  # MCP Server 启动脚本
#         ('app/ai/mcp/mcp_server/fastmcp_server.py', 'app/ai/mcp/mcp_server'),  # MCP Server 实现
#         ('app/ai/mcp/mcp_server/server_manager.py', 'app/ai/mcp/mcp_server'),  # MCP Server 管理器
        
#         ('.env', '.'),  # 打包 .env 文件到根目录
#         ('.env.desktop', '.'),  # 打包 .env.desktop 文件到根目录
#         # 如果有其他资源文件，在此添加：
#         # ('resources/images', 'resources/images'),
#         # ('config/default.yaml', 'config'),
#     ],
    
#     # --------------------------------------------------------------------
#     # hiddenimports：隐式导入的模块
#     # PyInstaller 无法自动检测的动态导入模块需手动声明
#     # --------------------------------------------------------------------
#     hiddenimports=[
#         # Uvicorn 相关（FastAPI 服务器）
#         'uvicorn.logging',
#         'uvicorn.loops',
#         'uvicorn.loops.auto',
#         'uvicorn.protocols',
#         'uvicorn.protocols.http',
#         'uvicorn.protocols.http.auto',
#         'uvicorn.protocols.websockets',
#         'uvicorn.protocols.websockets.auto',
#         'uvicorn.lifespan',
#         'uvicorn.lifespan.on',
        
#         # 数据库相关（SQLAlchemy + SQLite）
#         'sqlalchemy.sql.default_comparator',
#         'pysqlite3',  # SQLite 数据库驱动
        
#         # MCP 相关模块（Model-Control-Protocol）
#         'fastmcp',
#         'fastmcp.server',
#         'fastmcp.client',
#         'fastmcp.client.client',
#         'fastmcp.utilities',
#         'fastmcp.utilities.exceptions',
#         'mcp',
#         'mcp.server',
#         'mcp.server.fastmcp',
#         'mcp.client',
#         'mcp.client.streamable_http',
#         'mcp.client.stdio',
#         'mcp.types',
#         'app.ai.mcp.mcp_server.fastmcp_server',
#         'app.ai.mcp.mcp_server.server_manager',
#         'app.ai.mcp.mcp_client.client_manager',
#         'app.ai.mcp.mcp_client.fastmcp_client',
        
#         # AI 相关模块
#         'app.ai.llm.ai_client',
#         'app.ai.llm.mcp_llm_connect',
#         'app.ai.utils.functionHandler',
#         'app.ai.utils.prompt_manager',
#         'app.ai.utils.register',
        
#         # 项目业务模块（动态导入的服务和接口）
#         'app.services.wx_public',       # 微信公众号服务
#         'app.services.sogou_wx_public',  # 搜狗搜索服务
#         'app.services.system',           # 系统服务
#         'app.services.ai_assistant',     # AI 助手服务
#         'app.api.endpoints.wx_public',   # 微信公众号 API
#         'app.api.endpoints.sogou_wx_public',  # 搜狗搜索 API
#         'app.api.endpoints.system',      # 系统 API
        
#         # 其他必要模块
#         'pkg_resources.py2_warn',
#     ],
    
#     # --------------------------------------------------------------------
#     # hookspath：自定义 hook 脚本的路径（用于特殊打包需求）
#     # --------------------------------------------------------------------
#     hookspath=[],
    
#     # --------------------------------------------------------------------
#     # hooksconfig：hook 配置
#     # --------------------------------------------------------------------
#     hooksconfig={{}},
    
#     # --------------------------------------------------------------------
#     # runtime_hooks：运行时 hook（在应用启动前执行的脚本）
#     # --------------------------------------------------------------------
#     runtime_hooks=[],
    
#     # --------------------------------------------------------------------
#     # excludes：排除的模块（减小打包体积）
#     # 这些模块不会被打包，确保应用不依赖它们
#     # --------------------------------------------------------------------
#     excludes=[
#         'matplotlib',  # 图表库（未使用）
#         'PIL',         # 图像处理库（未使用）
#         'PyQt5',       # Qt 框架（未使用）
#         'tkinter',     # Tk GUI 库（未使用）
#         'test',        # 测试模块
#         'unittest',    # 单元测试
#         'mysql.connector.plugins',  # MySQL 插件（桌面版用 SQLite）
#         'pymysql',     # MySQL 驱动（桌面版用 SQLite）
#     ],
    
#     # --------------------------------------------------------------------
#     # Windows 特定配置
#     # --------------------------------------------------------------------
#     win_no_prefer_redirects=False,   # 不使用重定向
#     win_private_assemblies=False,    # 不使用私有程序集
    
#     # --------------------------------------------------------------------
#     # 加密配置
#     # --------------------------------------------------------------------
#     cipher=block_cipher,  # 字节码加密（None = 不加密）
    
#     # --------------------------------------------------------------------
#     # 归档配置
#     # --------------------------------------------------------------------
#     noarchive=False,  # 允许将 Python 模块归档为 PYZ
# )

# # ============================================================================
# # PYZ 阶段：创建 Python 归档文件
# # 将所有 Python 模块压缩为一个 .pyz 文件
# # ============================================================================
# pyz = PYZ(
#     a.pure,          # 纯 Python 模块
#     a.zipped_data,   # 压缩数据
#     cipher=block_cipher  # 加密配置
# )

# # ============================================================================
# # EXE 阶段：创建可执行文件
# # ============================================================================
# exe = EXE(
#     pyz,           # Python 归档文件
#     a.scripts,     # 脚本文件
#     [],            # 额外的二进制文件（空 = 使用 COLLECT）
    
#     # --------------------------------------------------------------------
#     # 基本配置
#     # --------------------------------------------------------------------
#     exclude_binaries=True,  # 不将二进制文件打包到 EXE（使用 COLLECT）
#     name='wx公众号工具', # 可执行文件名称
    
#     # --------------------------------------------------------------------
#     # 调试和优化
#     # --------------------------------------------------------------------
#     debug=False,     # 不启用调试模式（生产环境）
#     strip=False,     # 不剥离符号（保留调试信息）
#     upx=True,        # 使用 UPX 压缩（减小体积）
    
#     # --------------------------------------------------------------------
#     # 运行模式
#     # --------------------------------------------------------------------
#     console=True,    # 显示控制台窗口（调试用）
#                      # 改为 False 则隐藏控制台（纯 GUI 模式）
    
#     # --------------------------------------------------------------------
#     # 🎨 应用图标配置（在此添加图标）
#     # --------------------------------------------------------------------
#     icon='resources/icon.icns',  # macOS 图标（.icns 格式）
#     # icon='resources/icon.ico',   # Windows 图标（.ico 格式）
#     # 使用方法：
#     # 1. 准备图标文件
#     #    - macOS: icon.icns (推荐 512x512)
#     #    - Windows: icon.ico (包含多个尺寸：16x16, 32x32, 48x48, 256x256)
#     # 2. 放置在 resources/ 目录
#     # 3. 取消上面对应平台的注释
    
#     # --------------------------------------------------------------------
#     # macOS 特定配置
#     # --------------------------------------------------------------------
#     bootloader_ignore_signals=False,  # 不忽略信号
#     argv_emulation=False,             # 不模拟 argv（macOS）
    
#     # --------------------------------------------------------------------
#     # Windows 特定配置
#     # --------------------------------------------------------------------
#     disable_windowed_traceback=False,  # 不禁用窗口模式的 traceback
    
#     # --------------------------------------------------------------------
#     # 架构和签名
#     # --------------------------------------------------------------------
#     target_arch=None,          # 目标架构（None = 自动检测）
#     codesign_identity=None,    # macOS 代码签名身份（None = 不签名）
#     entitlements_file=None,    # macOS 权限文件（None = 无权限）
# )

# # ============================================================================
# # COLLECT 阶段：收集所有文件
# # 将可执行文件、依赖库、资源文件打包到一个目录
# # ============================================================================
# coll = COLLECT(
#     exe,           # 可执行文件
#     a.binaries,    # 二进制依赖（.dll/.so/.dylib）
#     a.zipfiles,    # ZIP 文件
#     a.datas,       # 数据文件（前端资源等）
    
#     # --------------------------------------------------------------------
#     # 优化配置
#     # --------------------------------------------------------------------
#     strip=False,     # 不剥离符号
#     upx=True,        # 使用 UPX 压缩二进制文件
#     upx_exclude=[],  # UPX 排除列表（某些库不兼容 UPX 压缩）
    
#     # --------------------------------------------------------------------
#     # 输出目录名称
#     # --------------------------------------------------------------------
#     name='wx公众号工具',  # 输出目录：dist/wx公众号工具/
# )

# # ============================================================================
# # BUNDLE 阶段：创建 macOS .app 包（仅 macOS）
# # ============================================================================
# if is_mac:
#     app = BUNDLE(
#         coll,  # 收集的文件
        
#         # --------------------------------------------------------------------
#         # 应用包名称
#         # --------------------------------------------------------------------
#         name='wx公众号工具.app',  # 最终输出：dist/wx公众号工具.app
        
#         # --------------------------------------------------------------------
#         # Bundle Identifier（macOS 应用唯一标识符）
#         # 格式：com.公司名.应用名
#         # --------------------------------------------------------------------
#         bundle_identifier='com.wxcrawler.desktop',
        
#         # --------------------------------------------------------------------
#         # 🎨 应用图标（macOS）
#         # --------------------------------------------------------------------
#         icon='resources/icon.icns',  # .app 包的图标
#         # 使用方法：
#         # 1. 准备 icon.icns 文件（macOS 图标格式）
#         # 2. 放置在 resources/ 目录
#         # 3. 取消此行注释
#         # 4. 可以使用在线工具将 PNG 转换为 ICNS：
#         #    https://cloudconvert.com/png-to-icns
        
#         # --------------------------------------------------------------------
#         # Info.plist 配置（macOS 应用信息）
#         # --------------------------------------------------------------------
#         info_plist={{
#             # 支持高分辨率（Retina）显示
#             'NSHighResolutionCapable': 'True',
            
#             # 是否为后台应用（False = 显示在 Dock）
#             'LSUIElement': False,
            
#             # 版本号（短版本，显示给用户）
#             'CFBundleShortVersionString': '1.0.0',
            
#             # 版本号（完整版本，内部使用）
#             'CFBundleVersion': '1.0.0',
            
#             # 网络安全配置（允许 HTTP 请求）
#             # 需要访问微信服务器（HTTPS）和本地服务器（HTTP）
#             'NSAppTransportSecurity': {{
#                 'NSAllowsArbitraryLoads': True  # 允许所有网络请求
#             }},
            
#             # 其他可选配置：
#             # 'CFBundleName': 'wx公众号工具',  # 应用名称
#             # 'CFBundleDisplayName': 'wx公众号工具',  # 显示名称（支持中文）
#             # 'NSHumanReadableCopyright': 'Copyright © 2025',  # 版权信息
#         }},
#     )
# '''

#     # 写入 spec 文件
#     try:
#         with open(spec_path, 'w', encoding='utf-8') as f:
#             f.write(spec_content)
        
#         success(f"Spec 文件生成成功: {spec_path}")
#         return spec_path
        
#     except Exception as e:
#         error(f"生成 spec 文件失败: {e}")



#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# 只需要修改 generate_spec_file() 函数中的图标配置部分

def generate_spec_file():
    """动态生成 wx_crawler.spec 文件"""
    
    spec_path = PROJECT_ROOT / "wx_crawler.spec"
    
    # ✅ 根据平台选择图标配置
    if IS_WINDOWS:
        # Windows: 使用 .ico 格式
        icon_config_exe = """
    # --------------------------------------------------------------------
    # 🎨 应用图标配置（Windows）
    # --------------------------------------------------------------------
    # icon='resources/icon.ico',  # Windows 图标（.ico 格式）
    # 使用方法：
    # 1. 准备 icon.ico 文件（包含多个尺寸：16x16, 32x32, 48x48, 256x256）
    # 2. 放置在 resources/ 目录
    # 3. 取消上面的注释
    # 4. 在线转换工具：https://convertio.co/zh/png-ico/
"""
        icon_config_bundle = ""  # Windows 不需要 BUNDLE
        
    elif IS_MAC:
        # macOS: 使用 .icns 格式
        icon_config_exe = """
    # --------------------------------------------------------------------
    # 🎨 应用图标配置（macOS）
    # --------------------------------------------------------------------
    # icon='resources/icon.icns',  # macOS 图标（.icns 格式）
    # 使用方法：
    # 1. 准备 icon.icns 文件（推荐 512x512）
    # 2. 放置在 resources/ 目录
    # 3. 取消上面的注释
    # 4. 在线转换工具：https://cloudconvert.com/png-to-icns
"""
        icon_config_bundle = """
        # --------------------------------------------------------------------
        # 🎨 应用图标（macOS Bundle）
        # --------------------------------------------------------------------
        # icon='resources/icon.icns',  # .app 包的图标
        # 使用方法：
        # 1. 准备 icon.icns 文件（macOS 图标格式）
        # 2. 放置在 resources/ 目录
        # 3. 取消此行注释
        # 4. 可以使用在线工具将 PNG 转换为 ICNS：
        #    https://cloudconvert.com/png-to-icns
"""
    else:
        # Linux
        icon_config_exe = """
    # --------------------------------------------------------------------
    # 🎨 应用图标配置（Linux）
    # --------------------------------------------------------------------
    # icon='resources/icon.png',  # Linux 图标（.png 格式）
"""
        icon_config_bundle = ""
    
    # spec 文件模板
    spec_content = f'''# -*- mode: python ; coding: utf-8 -*-
# ============================================================================
# PyInstaller 配置文件（自动生成）
# ============================================================================
# 平台: {SYSTEM}
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
a = Analysis(
    ['run_desktop.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('web/dist', 'web/dist'),
        ('app/ai/prompt', 'app/ai/prompt'),
        ('app/ai/mcp/mcp_client/mcp_settings.json', 'app/ai/mcp/mcp_client'),
        ('app/ai/mcp/mcp_client/client_manager.py', 'app/ai/mcp/mcp_client'),
        ('app/ai/mcp/mcp_client/fastmcp_client.py', 'app/ai/mcp/mcp_client'),
        ('app/ai/mcp/mcp_server/run_server.py', 'app/ai/mcp/mcp_server'),
        ('app/ai/mcp/mcp_server/fastmcp_server.py', 'app/ai/mcp/mcp_server'),
        ('app/ai/mcp/mcp_server/server_manager.py', 'app/ai/mcp/mcp_server'),
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
    hooksconfig={{}},
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
    console={"True" if IS_WINDOWS else "False"},  # Windows 显示控制台便于调试
{icon_config_exe}
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
{icon_config_bundle}
        bundle_identifier='com.wxcrawler.desktop',
        info_plist={{
            'NSHighResolutionCapable': 'True',
            'LSUIElement': False,
            'CFBundleShortVersionString': '1.0.0',
            'CFBundleVersion': '1.0.0',
            'NSAppTransportSecurity': {{
                'NSAllowsArbitraryLoads': True
            }},
        }},
    )
'''

    # 写入 spec 文件
    try:
        with open(spec_path, 'w', encoding='utf-8') as f:
            f.write(spec_content)
        
        success(f"Spec 文件生成成功: {spec_path}")
        
        # 提示图标使用
        if IS_WINDOWS:
            warning("提示：如需添加应用图标，请准备 icon.ico 文件并放在 resources/ 目录")
        elif IS_MAC:
            warning("提示：如需添加应用图标，请准备 icon.icns 文件并放在 resources/ 目录")
        
        return spec_path
        
    except Exception as e:
        error(f"生成 spec 文件失败: {e}")



# =========================
# 主流程
# =========================

def main():
    header("公众号爬虫助手 - 跨平台打包脚本")

    color_print(f"项目目录: {PROJECT_ROOT}", fg_color=Colors.BLUE)

    # 1. Python
    step_info(1, 8, "检查 Python")
    run("python --version" if IS_WINDOWS else "python3 --version")
    success("Python 正常")

    # 2. Node.js
    step_info(2, 8, "检查 Node.js")
    run("node --version")
    run("npm --version")
    success("Node.js 正常")

    # 3. 虚拟环境
    step_info(3, 8, "检查虚拟环境")
    venv_dir = PROJECT_ROOT / "venv"
    if not venv_dir.exists():
        info("创建虚拟环境...")
        run("python -m venv venv" if IS_WINDOWS else "python3 -m venv venv")
    success("虚拟环境 OK")

    # 4. Python 依赖（⭐平台区分）
    step_info(4, 8, "安装 Python 依赖")

    if IS_WINDOWS:
        pip_exe = venv_dir / "Scripts" / "pip.exe"
        requirements_file = PROJECT_ROOT / "requirements-windows.txt"
    else:
        pip_exe = venv_dir / "bin" / "pip"
        requirements_file = PROJECT_ROOT / "requirements.txt"

    if not requirements_file.exists():
        error(f"未找到依赖文件: {requirements_file.name}")

    # 直接使用虚拟环境中的 pip，不需要激活虚拟环境
    pip_cmd = (
        f'"{pip_exe}" install --upgrade pip && '
        f'"{pip_exe}" install -r "{requirements_file}" && '
        f'"{pip_exe}" install pyinstaller pywebview'
    )

    run(pip_cmd)
    success(f"Python 依赖安装完成（{requirements_file.name}）")

    # 5. 前端构建
    step_info(5, 8, "构建前端")
    web_dir = PROJECT_ROOT / "web"

    if not (web_dir / "node_modules").exists():
        run("npm install", cwd=web_dir)

    run("npm run build:only", cwd=web_dir)

    if not (web_dir / "dist").exists():
        error("前端构建失败，dist 不存在")

    success("前端构建完成")

    # 6. 清理旧文件
    step_info(6, 8, "清理旧文件")
    for name in ("dist", "build"):
        path = PROJECT_ROOT / name
        if path.exists():
            shutil.rmtree(path, ignore_errors=True)
    success("清理完成")

    # 7. 生成 spec 文件（⭐ 新增）
    step_info(7, 9, "生成 spec 文件")
    spec_path = generate_spec_file()
    warning(f"当前平台: {SYSTEM}")
    color_print(f"Spec 文件路径: {spec_path}", fg_color=Colors.CYAN)

    # 8. PyInstaller 打包
    step_info(8, 9, "开始打包")

    # 注入桌面端环境变量配置 下面的这行代码其实没有用处，需要在启动desktop的时候手动设置环境变量
    # python_cmd = "python" if IS_WINDOWS else "python3"
    # run(f"{python_cmd} -m app.scripts.set_env desktop")
    warning("这可能需要几分钟时间，请耐心等待...")
    run("pyinstaller wx_crawler.spec")

    if IS_WINDOWS:
        exe_path = PROJECT_ROOT / "dist" / "wx公众号工具" / "wx公众号工具.exe"
        if not exe_path.exists():
            error("Windows 打包失败，exe 未生成")
    else:
        app_path = PROJECT_ROOT / "dist" / "wx公众号工具.app"
        if not app_path.exists():
            error("macOS 打包失败，app 未生成")

    success("应用打包完成")

    # 9. macOS 安全属性
    if IS_MAC:
        step_info(9, 9, "处理 macOS 安全属性")
        run("xattr -cr dist/wx公众号工具.app")
        success("安全属性处理完成")

    # 10. 可选：清理 spec 文件
    cleanup_spec = input("\n是否删除临时 spec 文件？(y/n): ").strip().lower()
    if cleanup_spec in ['y', 'yes']:
        spec_path = PROJECT_ROOT / "wx_crawler.spec"
        if spec_path.exists():
            try:
                os.remove(spec_path)
                success("Spec 文件已删除")
            except Exception as e:
                warning(f"删除 spec 文件失败: {e}")

    header("✓ 打包成功")

    if IS_WINDOWS:
        color_print(f"输出文件: {PROJECT_ROOT / 'dist' / 'wx公众号工具' / 'wx公众号工具.exe'}", fg_color=Colors.GREEN)
    else:
        color_print("输出文件: dist/wx公众号工具.app", fg_color=Colors.GREEN)


if __name__ == "__main__":
    main()
