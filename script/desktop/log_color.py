#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
日志颜色公共模块
提供跨平台的彩色输出功能
支持 Windows、macOS 和 Linux
"""

import sys
import platform


# =========================
# 颜色定义（跨平台）
# =========================

class Colors:
    """ANSI 颜色代码类 - 支持 Windows 和 Mac/Linux"""
    
    # 重置
    RESET = '\033[0m'
    
    # 前景色
    BLACK = '\033[30m'
    RED = '\033[31m'
    GREEN = '\033[32m'
    YELLOW = '\033[33m'
    BLUE = '\033[34m'
    MAGENTA = '\033[35m'
    CYAN = '\033[36m'
    WHITE = '\033[37m'
    
    # 亮色前景色
    BRIGHT_BLACK = '\033[90m'
    BRIGHT_RED = '\033[91m'
    BRIGHT_GREEN = '\033[92m'
    BRIGHT_YELLOW = '\033[93m'
    BRIGHT_BLUE = '\033[94m'
    BRIGHT_MAGENTA = '\033[95m'
    BRIGHT_CYAN = '\033[96m'
    BRIGHT_WHITE = '\033[97m'
    
    # 背景色
    BG_BLACK = '\033[40m'
    BG_RED = '\033[41m'
    BG_GREEN = '\033[42m'
    BG_YELLOW = '\033[43m'
    BG_BLUE = '\033[44m'
    BG_MAGENTA = '\033[45m'
    BG_CYAN = '\033[46m'
    BG_WHITE = '\033[47m'
    
    # 亮色背景色
    BG_BRIGHT_BLACK = '\033[100m'
    BG_BRIGHT_RED = '\033[101m'
    BG_BRIGHT_GREEN = '\033[102m'
    BG_BRIGHT_YELLOW = '\033[103m'
    BG_BRIGHT_BLUE = '\033[104m'
    BG_BRIGHT_MAGENTA = '\033[105m'
    BG_BRIGHT_CYAN = '\033[106m'
    BG_BRIGHT_WHITE = '\033[107m'
    
    # 样式
    BOLD = '\033[1m'
    DIM = '\033[2m'
    ITALIC = '\033[3m'
    UNDERLINE = '\033[4m'
    BLINK = '\033[5m'
    REVERSE = '\033[7m'
    HIDDEN = '\033[8m'
    STRIKETHROUGH = '\033[9m'

    @staticmethod
    def enable_windows_colors():
        """在 Windows 上启用 ANSI 颜色支持（Windows 10+）"""
        if platform.system() == 'Windows':
            try:
                import ctypes
                kernel32 = ctypes.windll.kernel32
                # 启用 ANSI 转义序列支持
                kernel32.SetConsoleMode(kernel32.GetStdHandle(-11), 7)
            except:
                pass  # 如果失败，就忽略


# 初始化颜色支持
Colors.enable_windows_colors()


# =========================
# 彩色打印函数
# =========================

def color_print(text, fg_color=None, bg_color=None, style=None):
    """彩色打印函数
    
    Args:
        text: 要打印的文本
        fg_color: 前景色代码
        bg_color: 背景色代码  
        style: 样式代码
    """
    color_code = ""
    
    if style:
        color_code += style
    if bg_color:
        color_code += bg_color
    if fg_color:
        color_code += fg_color
        
    if color_code:
        print(f"{color_code}{text}{Colors.RESET}")
    else:
        print(text)


def header(title, width=60):
    """显示标题
    
    Args:
        title: 标题文本
        width: 分隔线宽度（默认 60）
    """
    separator = '=' * width
    color_print(f"\n{separator}", fg_color=Colors.BLUE, style=Colors.BOLD)
    color_print(f"  {title}", fg_color=Colors.BLUE, style=Colors.BOLD)
    color_print(f"{separator}", fg_color=Colors.BLUE)


def info(msg):
    """显示信息
    
    Args:
        msg: 信息文本
    """
    color_print(f"▶ {msg}", fg_color=Colors.YELLOW, style=Colors.BOLD)


def success(msg):
    """显示成功信息
    
    Args:
        msg: 成功信息文本
    """
    color_print(f"✓ {msg}", fg_color=Colors.GREEN)


def error(msg, exit_code=1):
    """显示错误信息并退出
    
    Args:
        msg: 错误信息文本
        exit_code: 退出码（默认 1）
    """
    color_print(f"❌ {msg}", fg_color=Colors.RED)
    sys.exit(exit_code)


def warning(msg):
    """显示警告信息
    
    Args:
        msg: 警告信息文本
    """
    color_print(f"⚠️  {msg}", fg_color=Colors.YELLOW)


def step_info(step_num, total_steps, msg):
    """显示步骤信息
    
    Args:
        step_num: 当前步骤号
        total_steps: 总步骤数
        msg: 步骤描述
    """
    color_print(f"▶ [{step_num}/{total_steps}] {msg}", fg_color=Colors.YELLOW, style=Colors.BOLD)


def print_header(title, separator='=', width=60):
    """打印标题（别名，与 header 相同）
    
    Args:
        title: 标题文本
        separator: 分隔符（默认 '='）
        width: 分隔线宽度（默认 60）
    """
    header(title, width=width)

