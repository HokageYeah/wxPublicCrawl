"""
启动FastMCP服务器
用于开发和测试
"""
import sys
import os
from pathlib import Path

# 计算项目根目录
# __file__ = .../app/ai/mcp/mcp_server/run_server.py
# parent 1: mcp_server/ -> mcp/
# parent 2: mcp/ -> ai/
# parent 3: ai/ -> app/
# parent 4: app/ -> wxPublicCrawl/
script_path = Path(__file__).resolve()
project_root = script_path.parent.parent.parent.parent.parent  # 5个parent才能到项目根目录

# 添加项目根目录到Python路径
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from loguru import logger
from app.ai.mcp.mcp_server.fastmcp_server import FastmcpServer

TAG = "MCP_SERVER"


def main():
    """启动MCP服务器"""
    # 打印初始化信息（这些会被 server_manager 捕获）
    logger.bind(tag=TAG).info(f"Script路径: {script_path}")
    logger.bind(tag=TAG).info(f"项目根目录: {project_root}")
    logger.bind(tag=TAG).info(f"sys.path[0]: {sys.path[0]}")
    logger.bind(tag=TAG).info(f"项目根目录存在: {project_root.exists()}")
    logger.bind(tag=TAG).info("="*60)
    logger.bind(tag=TAG).info("启动FastMCP服务器")
    logger.bind(tag=TAG).info("="*60)
    
    try:
        # 创建服务器实例
        server = FastmcpServer()
        
        # 启动服务器
        logger.bind(tag=TAG).info("服务器配置:")
        logger.bind(tag=TAG).info("  - 传输方式: streamable-http")
        logger.bind(tag=TAG).info("  - 地址: http://127.0.0.1:8008/mcp")
        logger.bind(tag=TAG).info("  - 可用工具: weather, calculator, knowledge_base, get_wx_articles")
        logger.bind(tag=TAG).info("="*60)
        
        server.run(
            transport="streamable-http",
            host="127.0.0.1",  # 使用 IPv4 避免冲突
            port=8008
        )
        
    except KeyboardInterrupt:
        logger.bind(tag=TAG).info("\n服务器已停止")
    except Exception as e:
        logger.bind(tag=TAG).error(f"服务器启动失败: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()

