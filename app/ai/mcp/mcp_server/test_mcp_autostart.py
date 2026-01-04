#!/usr/bin/env python3
"""
测试 MCP Server 自动启动功能
运行此脚本将仅启动 FastAPI 服务（不启动 WebView），以便测试 MCP Server 是否正确启动
"""
import os
import sys
import time

# 设置环境变量
os.environ['ENV'] = 'desktop'

print("=" * 80)
print("测试 MCP Server 自动启动")
print("=" * 80)

# 导入 FastAPI 应用
print("\n[1/2] 导入 FastAPI 应用...")
try:
    from app.main import app
    print("✅ FastAPI 应用导入成功")
except Exception as e:
    print(f"❌ FastAPI 应用导入失败: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# 启动服务器
print("\n[2/2] 启动 Uvicorn 服务器...")
try:
    import uvicorn
    
    print("\n" + "=" * 80)
    print("服务器正在启动，请观察控制台输出")
    print("=" * 80)
    print("\n预期看到以下日志：")
    print("  1. 📝 初始化日志系统...")
    print("  2. 🗄️  初始化数据库连接...")
    print("  3. 🤖 初始化AI助手...")
    print("  4. 🔌 启动本地 MCP Server...")
    print("  5. ✅ MCP Server 启动完成 - 地址: http://localhost:8008/mcp")
    print("\n" + "=" * 80)
    print("启动中...\n")
    
    time.sleep(1)
    
    # 启动服务器（这会阻塞）
    uvicorn.run(
        app,
        host="127.0.0.1",
        port=8002,
        log_level="info"
    )
    
except KeyboardInterrupt:
    print("\n\n用户中断，正在退出...")
except Exception as e:
    print(f"\n\n❌ 服务器启动失败: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print("\n服务器已停止")
