@echo off
chcp 65001 >nul
setlocal EnableDelayedExpansion

REM ============================================================================
REM 自动切换到项目根目录
REM ============================================================================
REM 获取脚本所在目录
set "SCRIPT_DIR=%~dp0"
REM 切换到项目根目录（脚本在 script\desktop\ 下，所以需要上两级）
cd /d "%SCRIPT_DIR%..\.."
set "PROJECT_ROOT=%CD%"

echo ======================================
echo   公众号爬虫助手 - Windows 打包脚本
echo ======================================
echo 项目目录: %PROJECT_ROOT%
echo.

REM 1. 检查 Python 版本
echo [1/8] 检查 Python 版本...
python --version >nul 2>&1
if errorlevel 1 (
    echo [错误] 未找到 Python，请先安装 Python 3.9+
    pause
    exit /b 1
)
python --version
echo [√] Python 版本检查通过
echo.

REM 2. 检查 Node.js
echo [2/8] 检查 Node.js...
node --version >nul 2>&1
if errorlevel 1 (
    echo [错误] 未找到 Node.js，请先安装 Node.js
    pause
    exit /b 1
)
node --version
npm --version
echo [√] Node.js 检查通过
echo.

REM 3. 检查虚拟环境
echo [3/8] 检查 Python 虚拟环境...
if not exist venv (
    echo 创建虚拟环境...
    python -m venv venv
    echo [√] 虚拟环境创建成功
) else (
    echo [√] 虚拟环境已存在
)
echo.

REM 4. 激活虚拟环境并安装 Python 依赖
echo [4/8] 安装 Python 依赖...
call venv\Scripts\activate
python -m pip install --upgrade pip -q
pip install -r requirements.txt -q
pip install pyinstaller pywebview -q
echo [√] Python 依赖安装完成
echo.

REM 5. 构建前端
echo [5/8] 构建前端...
cd web

if not exist node_modules (
    echo 安装前端依赖...
    call npm install
)

echo 构建前端项目...
call npm run build:only

if not exist dist (
    echo [错误] 前端构建失败，dist 目录不存在
    cd ..
    pause
    exit /b 1
)

cd ..
echo [√] 前端构建完成
echo.

REM 6. 清理旧的打包文件
echo [6/8] 清理旧的打包文件...
if exist build rmdir /s /q build
if exist dist rmdir /s /q dist
echo [√] 清理完成
echo.

REM 7. 打包应用
echo [7/8] 开始打包应用...
echo 这可能需要几分钟时间，请耐心等待...
pyinstaller wx_crawler.spec

if not exist dist\wx公众号工具\wx公众号工具.exe (
    echo [错误] 打包失败，应用文件不存在
    pause
    exit /b 1
)

echo [√] 应用打包完成
echo.

REM 8. 完成
echo [8/8] 打包流程完成
echo.

echo ======================================
echo   √ 打包成功！
echo ======================================
echo.
echo 应用位置: dist\wx公众号工具\wx公众号工具.exe
echo.
echo 测试运行:
echo   dist\wx公众号工具\wx公众号工具.exe
echo.
echo 创建分发包:
echo   方式 1: ZIP 压缩包
echo   cd dist ^&^& tar -a -c -f wx公众号工具-windows.zip wx公众号工具
echo.
echo   方式 2: 创建安装程序（需要安装 Inno Setup）
echo   使用 Inno Setup 创建 installer.iss 文件
echo.

pause

