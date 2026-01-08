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

    # 7. PyInstaller 打包
    step_info(7, 8, "开始打包")

    # 注入桌面端环境变量配置 下面的这行代码其实没有用处，需要在启动desktop的时候手动设置环境变量
    # python_cmd = "python" if IS_WINDOWS else "python3"
    # run(f"{python_cmd} -m app.scripts.set_env desktop")
    warning("这可能需要几分钟时间，请耐心等待...")
    run("pyinstaller wx_crawler.spec")

    if IS_WINDOWS:
        exe_path = PROJECT_ROOT / "dist" / "wx公众号工具.exe"
        if not exe_path.exists():
            error("Windows 打包失败，exe 未生成")
    else:
        app_path = PROJECT_ROOT / "dist" / "wx公众号工具.app"
        if not app_path.exists():
            error("macOS 打包失败，app 未生成")

    success("应用打包完成")

    # 8. macOS 安全属性
    if IS_MAC:
        step_info(8, 8, "处理 macOS 安全属性")
        run("xattr -cr dist/wx公众号工具.app")
        success("安全属性处理完成")

    header("✓ 打包成功")

    if IS_WINDOWS:
        color_print("输出文件: dist/wx公众号工具.exe", fg_color=Colors.GREEN)
    else:
        color_print("输出文件: dist/wx公众号工具.app", fg_color=Colors.GREEN)


if __name__ == "__main__":
    main()
