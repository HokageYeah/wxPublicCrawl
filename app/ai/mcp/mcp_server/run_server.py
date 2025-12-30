"""
启动FastMCP服务器
用于开发和测试
"""
import sys
import os
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(project_root))

# 打印调试信息（可选）
print(f"项目根目录: {project_root}")
print(f"Python路径已添加: {str(project_root)}")

from loguru import logger
from app.ai.mcp.mcp_server.fastmcp_server import FastmcpServer

TAG = "MCP_SERVER"


def main():
    """启动MCP服务器"""
    logger.bind(tag=TAG).info("="*60)
    logger.bind(tag=TAG).info("启动FastMCP服务器")
    logger.bind(tag=TAG).info("="*60)
    
    try:
        # 创建服务器实例
        server = FastmcpServer()
        
        # 启动服务器
        logger.bind(tag=TAG).info("服务器配置:")
        logger.bind(tag=TAG).info("  - 传输方式: streamable-http")
        logger.bind(tag=TAG).info("  - 地址: http://localhost:8008/mcp")
        logger.bind(tag=TAG).info("  - 可用工具: weather, calculator")
        logger.bind(tag=TAG).info("="*60)
        
        server.run(
            transport="streamable-http",
            host="localhost",
            port=8008
        )
        
    except KeyboardInterrupt:
        logger.bind(tag=TAG).info("\n服务器已停止")
    except Exception as e:
        logger.bind(tag=TAG).error(f"服务器启动失败: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()

