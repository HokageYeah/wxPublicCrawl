#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
运行应用的入口脚本
确保从项目根目录运行，以便正确导入app包
"""

import os
import sys
import asyncio
import platform
# 最开始添项目根目录到python的路径
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
print('project_root---1', __file__)
print('project_root---2', os.path.abspath(__file__))
print('project_root---3', os.path.dirname(os.path.dirname(__file__)))
print('project_root---4', os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
print('project_root---5', os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
sys.path.append(project_root)

if __name__ == "__main__":
    from app.main import app
    import uvicorn
    import logging
    
    logging.info("启动应用服务器...")
    # 获取命令行参数
    args = sys.argv
    
    # Windows 系统特殊处理：禁用 reload 模式
    # 原因：reload 模式会创建子进程，子进程的 asyncio.run() 会忽略事件循环策略
    is_windows = platform.system() == 'Windows'
    use_reload = not is_windows  # Windows 上禁用 reload
    
    if is_windows:
        print("=" * 80)
        print("⚠️  Windows 系统：已禁用热重载功能 (reload=False)")
        print("⚠️  原因：Python 3.13 + Playwright 兼容性问题")
        print("⚠️  修改代码后需手动重启服务器")
        print("=" * 80)
    
    # 判断是否包含n8n参数
    if len(args) > 1 and args[1] == "n8n":
        # docker、cloudflare内网穿透
        print("使用192.168.1.101作为host启动服务器...")
        uvicorn.run("app.main:app", host="192.168.1.101", port=8002, reload=use_reload)
    else:
        # 默认使用localhost
        print("使用127.0.0.1作为host启动服务器...")
        uvicorn.run("app.main:app", host="127.0.0.1", port=8002, reload=use_reload)