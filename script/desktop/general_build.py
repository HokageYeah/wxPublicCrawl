#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
import subprocess
import shutil
import platform
from pathlib import Path


# =========================
# 工具函数
# =========================

def run(cmd, cwd=None):
    """执行命令，失败直接退出（等价 set -e）"""
    print(f"\n>>> {cmd}")
    result = subprocess.run(
        cmd,
        cwd=cwd,
        shell=True,
        text=True
    )
    if result.returncode != 0:
        print(f"\n❌ 命令执行失败: {cmd}")
        sys.exit(result.returncode)


def header(title):
    print("\n" + "=" * 40)
    print(f"  {title}")
    print("=" * 40)


def info(msg):
    print(f"▶ {msg}")


def success(msg):
    print(f"✓ {msg}")


def error(msg):
    print(f"❌ {msg}")
    sys.exit(1)


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

    print(f"项目目录: {PROJECT_ROOT}")

    # 1. Python
    info("[1/8] 检查 Python")
    run("python --version" if IS_WINDOWS else "python3 --version")
    success("Python 正常")

    # 2. Node.js
    info("[2/8] 检查 Node.js")
    run("node --version")
    run("npm --version")
    success("Node.js 正常")

    # 3. 虚拟环境
    info("[3/8] 检查虚拟环境")
    venv_dir = PROJECT_ROOT / "venv"
    if not venv_dir.exists():
        info("创建虚拟环境...")
        run("python -m venv venv" if IS_WINDOWS else "python3 -m venv venv")
    success("虚拟环境 OK")

    # 4. Python 依赖（⭐平台区分）
    info("[4/8] 安装 Python 依赖")

    if IS_WINDOWS:
        activate = venv_dir / "Scripts" / "activate"
        requirements_file = PROJECT_ROOT / "requirements-windows.txt"
    else:
        activate = venv_dir / "bin" / "activate"
        requirements_file = PROJECT_ROOT / "requirements.txt"

    if not requirements_file.exists():
        error(f"未找到依赖文件: {requirements_file.name}")

    pip_cmd = (
        f'"{activate}" && '
        f'pip install --upgrade pip && '
        f'pip install -r "{requirements_file}" && '
        f'pip install pyinstaller pywebview'
    )

    run(pip_cmd)
    success(f"Python 依赖安装完成（{requirements_file.name}）")

    # 5. 前端构建
    info("[5/8] 构建前端")
    web_dir = PROJECT_ROOT / "web"

    if not (web_dir / "node_modules").exists():
        run("npm install", cwd=web_dir)

    run("npm run build:only", cwd=web_dir)

    if not (web_dir / "dist").exists():
        error("前端构建失败，dist 不存在")

    success("前端构建完成")

    # 6. 清理旧文件
    info("[6/8] 清理旧文件")
    for name in ("dist", "build"):
        path = PROJECT_ROOT / name
        if path.exists():
            shutil.rmtree(path, ignore_errors=True)
    success("清理完成")

    # 7. PyInstaller 打包
    info("[7/8] 开始打包")

    # 注入桌面端环境变量配置 下面的这行代码其实没有用处，需要在启动desktop的时候手动设置环境变量
    # python_cmd = "python" if IS_WINDOWS else "python3"
    # run(f"{python_cmd} -m app.scripts.set_env desktop")
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
        info("[8/8] 处理 macOS 安全属性")
        run("xattr -cr dist/wx公众号工具.app")
        success("安全属性处理完成")

    header("✓ 打包成功")

    if IS_WINDOWS:
        print("输出文件: dist/wx公众号工具.exe")
    else:
        print("输出文件: dist/wx公众号工具.app")


if __name__ == "__main__":
    main()
