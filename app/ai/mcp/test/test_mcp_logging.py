"""
测试 MCP Server 日志功能
运行此脚本验证日志是否正常输出
"""
import sys
from pathlib import Path

# 添加项目根目录到路径
project_root = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(project_root))

from loguru import logger
from app.ai.mcp.mcp_server.server_manager import get_mcp_server_manager
import time


def test_mcp_logging():
    """测试 MCP Server 日志输出"""
    
    logger.info("="*60)
    logger.info("开始测试 MCP Server 日志功能")
    logger.info("="*60)
    
    # 获取 MCP Server 管理器
    manager = get_mcp_server_manager()
    
    try:
        # 1. 启动 MCP Server
        logger.info("步骤1: 启动 MCP Server")
        manager.start_server(host="127.0.0.1", port=8008)
        
        # 等待服务器完全启动
        logger.info("等待服务器启动...")
        time.sleep(5)
        
        # 2. 检查服务器状态
        logger.info("步骤2: 检查服务器状态")
        status = manager.get_server_status()
        logger.info(f"服务器状态: {status}")
        
        if status["is_running"]:
            logger.success("✅ MCP Server 启动成功！")
            logger.info("请查看上方日志，应该能看到 [MCP_SERVER] 或 [MCP-Server-stdout] 标签的日志")
        else:
            logger.error("❌ MCP Server 启动失败")
            return False
        
        # 3. 等待一段时间，让用户查看日志
        logger.info("步骤3: 服务器将保持运行 30 秒，请观察日志输出")
        logger.info("提示: 你可以在另一个终端使用 curl 测试工具调用：")
        logger.info("  curl -X POST http://127.0.0.1:8008/mcp/v1/tools/call \\")
        logger.info("    -H 'Content-Type: application/json' \\")
        logger.info("    -d '{\"tool\":\"weather\",\"params\":{\"location\":\"北京\"}}'")
        
        for i in range(30, 0, -5):
            logger.info(f"剩余 {i} 秒...")
            time.sleep(5)
        
        # 4. 停止服务器
        logger.info("步骤4: 停止 MCP Server")
        manager.stop_server()
        
        logger.success("="*60)
        logger.success("✅ 测试完成！")
        logger.success("="*60)
        logger.success("检查要点:")
        logger.success("1. 启动日志是否正常显示（包含 [MCP_SERVER] 标签）")
        logger.success("2. 子进程输出是否被捕获（包含 [MCP-Server-stdout] 标签）")
        logger.success("3. 如果测试了工具调用，是否看到 [MCP工具] 标签的日志")
        logger.success("4. 停止日志是否正常显示")
        
        return True
        
    except KeyboardInterrupt:
        logger.warning("用户中断测试")
        manager.stop_server()
        return False
        
    except Exception as e:
        logger.error(f"测试失败: {e}", exc_info=True)
        manager.stop_server()
        return False


def test_subprocess_mode():
    """测试子进程模式的日志捕获"""
    import subprocess
    
    logger.info("="*60)
    logger.info("测试子进程日志捕获功能")
    logger.info("="*60)
    
    # 运行一个简单的 Python 命令
    process = subprocess.Popen(
        [sys.executable, "-c", "print('Hello from subprocess'); import time; time.sleep(2); print('Goodbye')"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        bufsize=1
    )
    
    # 读取输出
    import threading
    
    def read_output(pipe, name):
        for line in iter(pipe.readline, b''):
            if line:
                decoded = line.decode('utf-8', errors='ignore').rstrip()
                logger.info(f"[TEST-{name}] {decoded}")
        pipe.close()
    
    stdout_thread = threading.Thread(target=read_output, args=(process.stdout, "stdout"), daemon=True)
    stderr_thread = threading.Thread(target=read_output, args=(process.stderr, "stderr"), daemon=True)
    
    stdout_thread.start()
    stderr_thread.start()
    
    process.wait()
    
    logger.success("✅ 子进程日志捕获测试完成！")


if __name__ == "__main__":
    logger.info("MCP Server 日志功能测试脚本")
    logger.info("这个脚本会启动 MCP Server 并测试日志输出")
    logger.info("")
    
    choice = input("请选择测试类型:\n1. 完整测试（启动 MCP Server）\n2. 仅测试子进程日志捕获\n请输入选项 (1/2): ").strip()
    
    if choice == "1":
        success = test_mcp_logging()
        sys.exit(0 if success else 1)
    elif choice == "2":
        test_subprocess_mode()
        sys.exit(0)
    else:
        logger.error("无效的选项")
        sys.exit(1)

