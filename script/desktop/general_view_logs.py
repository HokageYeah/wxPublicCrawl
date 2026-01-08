#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
import subprocess
import platform
from pathlib import Path
from datetime import datetime

# 导入公共日志颜色模块
from log_color import color_print, header, info, success, error, warning, Colors


# =========================
# 平台判断
# =========================

SYSTEM = platform.system()
IS_WINDOWS = SYSTEM == "Windows"
IS_MAC = SYSTEM == "Darwin"
IS_LINUX = SYSTEM == "Linux"


# =========================
# 日志目录定位
# =========================

def get_log_directory():
    """获取各平台的日志目录
    
    返回:
        Path: 日志目录的路径对象
    """
    if IS_MAC:
        # macOS: ~/Library/Logs/应用名称（Apple 推荐位置）
        home = Path.home()
        log_dir = home / "Library" / "Logs" / "wx公众号工具"
        
    elif IS_WINDOWS:
        # Windows: %APPDATA%/应用名称/logs 或 %LOCALAPPDATA%/应用名称/logs
        # 优先使用 APPDATA
        appdata = os.environ.get('APPDATA', os.environ.get('LOCALAPPDATA'))
        if appdata:
            log_dir = Path(appdata) / "wx公众号工具" / "logs"
        else:
            # 降级方案：使用用户主目录
            home = Path.home()
            log_dir = home / "AppData" / "Local" / "wx公众号工具" / "logs"
        
    else:  # Linux
        # Linux: ~/.local/share/应用名称/logs
        home = Path.home()
        log_dir = home / ".local" / "share" / "wx公众号工具" / "logs"
    
    return log_dir


# =========================
# 查找最新日志文件
# =========================

def find_latest_log_file(log_dir):
    """查找最新的日志文件
    
    Args:
        log_dir: 日志目录路径
        
    返回:
        Path: 最新日志文件的路径，如果没有则返回 None
    """
    if not log_dir.exists():
        return None
    
    # 查找所有 app_*.log 或 app_*.log.zip 文件
    log_files = []
    for pattern in ["app_*.log", "app_*.log.zip"]:
        log_files.extend(log_dir.glob(pattern))
    
    if not log_files:
        return None
    
    # 按修改时间排序（最新的在前）
    log_files.sort(key=lambda f: f.stat().st_mtime, reverse=True)
    
    # 返回最新的文件
    return log_files[0]


# =========================
# 实时查看日志
# =========================

def tail_file_windows(file_path):
    """Windows 实时查看文件（使用 PowerShell）"""
    color_print(f"\n使用 PowerShell 查看日志: {file_path}", fg_color=Colors.CYAN)
    color_print("按 Ctrl+C 退出\n", fg_color=Colors.YELLOW)
    
    # 使用 PowerShell 的 Get-Content -Wait 参数实时监控
    ps_command = f'Get-Content -Path "{file_path}" -Wait -Tail 50'
    
    try:
        # 运行 PowerShell 命令
        process = subprocess.Popen(
            ['powershell', '-Command', ps_command],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            bufsize=1  # 行缓冲
        )
        
        # 实时读取输出
        for line in iter(process.stdout.readline, ''):
            if line:
                print(line.rstrip())
                
    except KeyboardInterrupt:
        color_print("\n\n已停止查看日志", fg_color=Colors.YELLOW)
        process.terminate()
        process.wait()
    except Exception as e:
        error(f"查看日志失败: {e}")


def tail_file_unix(file_path):
    """Unix/Linux/macOS 实时查看文件（使用 tail -f）"""
    color_print(f"\n使用 tail -f 查看日志: {file_path}", fg_color=Colors.CYAN)
    color_print("按 Ctrl+C 退出\n", fg_color=Colors.YELLOW)
    
    try:
        # 运行 tail -f 命令
        process = subprocess.Popen(
            ['tail', '-f', '-n', '50', str(file_path)],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            bufsize=1  # 行缓冲
        )
        
        # 实时读取输出
        for line in iter(process.stdout.readline, ''):
            if line:
                print(line.rstrip())
                
    except KeyboardInterrupt:
        color_print("\n\n已停止查看日志", fg_color=Colors.YELLOW)
        process.terminate()
        process.wait()
    except Exception as e:
        error(f"查看日志失败: {e}")


# =========================
# 主流程
# =========================

def main():
    header("公众号爬虫助手 - 实时日志查看工具")
    
    # 1. 获取日志目录
    log_dir = get_log_directory()
    color_print(f"日志目录: {log_dir}", fg_color=Colors.BLUE)
    
    # 2. 确保日志目录存在
    if not log_dir.exists():
        color_print("\n日志目录不存在", fg_color=Colors.YELLOW)
        color_print("\n提示：", fg_color=Colors.GREEN)
        color_print("  1. 确保已运行过桌面应用", fg_color=Colors.WHITE)
        if IS_MAC:
            color_print(f"     open dist/wx公众号工具.app", fg_color=Colors.CYAN)
        elif IS_WINDOWS:
            color_print(f"     dist\\wx公众号工具.exe", fg_color=Colors.CYAN)
        elif IS_LINUX:
            color_print(f"     ./dist/wx公众号工具", fg_color=Colors.CYAN)
        
        color_print(f"  2. 检查日志目录：{log_dir}", fg_color=Colors.WHITE)
        sys.exit(0)
    
    # 3. 查找最新的日志文件
    latest_log = find_latest_log_file(log_dir)
    
    if not latest_log:
        color_print("\n没有找到日志文件", fg_color=Colors.YELLOW)
        color_print("\n提示：", fg_color=Colors.GREEN)
        color_print("  1. 确保已运行过桌面应用", fg_color=Colors.WHITE)
        if IS_MAC:
            color_print(f"     open dist/wx公众号工具.app", fg_color=Colors.CYAN)
        elif IS_WINDOWS:
            color_print(f"     dist\\wx公众号工具.exe", fg_color=Colors.CYAN)
        elif IS_LINUX:
            color_print(f"     ./dist/wx公众号工具", fg_color=Colors.CYAN)
        
        color_print(f"  2. 检查日志目录：{log_dir}", fg_color=Colors.WHITE)
        color_print(f"  3. 日志文件格式：app_*.log 或 app_*.log.zip", fg_color=Colors.WHITE)
        sys.exit(0)
    
    # 4. 显示找到的日志文件信息
    color_print(f"\n找到最新日志: {latest_log}", fg_color=Colors.GREEN)
    mtime = datetime.fromtimestamp(latest_log.stat().st_mtime)
    color_print(f"最后修改: {mtime.strftime('%Y-%m-%d %H:%M:%S')}", fg_color=Colors.CYAN)
    color_print(f"文件大小: {latest_log.stat().st_size} 字节", fg_color=Colors.CYAN)
    
    # 5. 实时查看日志
    color_print(f"\n开始实时查看日志...\n", fg_color=Colors.GREEN, style=Colors.BOLD)
    
    if IS_WINDOWS:
        tail_file_windows(latest_log)
    else:  # macOS, Linux
        tail_file_unix(latest_log)


if __name__ == "__main__":
    main()
