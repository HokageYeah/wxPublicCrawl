"""
MCP客户端管理器
负责管理多个MCP客户端实例，包括初始化、工具注册、工具调用等
"""
import json
import os
from typing import Dict, Any, List, Optional
from pathlib import Path
from loguru import logger

from app.ai.mcp.mcp_client.fastmcp_client import FastMCPClient
from app.ai.utils.register import register_function, ToolType
from app.utils.src_path import get_resource_path


TAG = "MCP_MANAGER"


class MCPClientManager:
    """
    MCP客户端管理器
    
    功能：
    - 管理多个MCP客户端实例
    - 加载和解析MCP配置
    - 注册MCP工具到LLM函数注册表
    - 执行MCP工具调用
    - 资源清理
    """
    
    def __init__(self, llm_conn):
        """
        初始化MCP客户端管理器
        
        Args:
            llm_conn: LLM连接对象，用于调用工具和注册函数
        """
        self.llm_conn = llm_conn
        self.clients: Dict[str, FastMCPClient] = {}
        self.tools: List[Dict[str, Any]] = []
        self.config: Dict[str, Any] = {}
        self.mcp_server_url: str = ""
        self.mcp_servers: Dict[str, Any] = {}
        
        # 获取配置文件路径（支持打包后的路径）
        config_relative_path = "app/ai/mcp/mcp_client/mcp_settings.json"
        self.config_path = get_resource_path(config_relative_path)
        
        logger.bind(tag=TAG).info(f"MCP客户端管理器已初始化，配置文件: {self.config_path}")
    
    def load_config(self) -> bool:
        """
        加载MCP配置文件
        
        Returns:
            bool: 加载是否成功
        """
        try:
            if not os.path.exists(self.config_path):
                logger.bind(tag=TAG).error(f"配置文件不存在: {self.config_path}")
                return False
            
            with open(self.config_path, "r", encoding="utf-8") as f:
                self.config = json.load(f)
            
            self.mcp_server_url = self.config.get("mcp_server_url", "")
            self.mcp_servers = self.config.get("mcpServer", {})
            
            logger.bind(tag=TAG).info(
                f"✅ 配置加载成功 - 服务地址: {self.mcp_server_url}, "
                f"服务数量: {len(self.mcp_servers)}"
            )
            logger.bind(tag=TAG).debug(
                f"MCP服务列表: {list(self.mcp_servers.keys())}"
            )
            
            return True
            
        except json.JSONDecodeError as e:
            logger.bind(tag=TAG).error(f"配置文件JSON解析失败: {e}")
            return False
        except Exception as e:
            logger.bind(tag=TAG).error(f"加载配置文件失败: {e}")
            return False
    async def init_mcp_clients(self) -> bool:
        """
        初始化所有MCP客户端、连接MCP服务、获取工具列表
        
        工作流程：
        1. 加载配置文件
        2. 遍历所有MCP服务配置
        3. 为每个服务创建并初始化客户端
        4. 获取每个客户端的工具列表
        5. 注册工具到LLM函数注册表
        6. 更新LLM函数描述
        
        Returns:
            bool: 初始化是否成功
        """
        # 1. 加载配置
        if not self.load_config():
            logger.bind(tag=TAG).error("配置加载失败，跳过MCP客户端初始化")
            return False
        
        if not self.mcp_servers:
            logger.bind(tag=TAG).warning("没有配置MCP服务")
            return False
        
        logger.bind(tag=TAG).info(f"开始初始化 {len(self.mcp_servers)} 个MCP客户端...")
        
        success_count = 0
        fail_count = 0
        
        # 2. 遍历所有服务配置
        for server_name, server_config in self.mcp_servers.items():
            logger.bind(tag=TAG).info(f"📡 正在初始化MCP服务: {server_name}")
            
            try:
                # 3. 创建并初始化客户端
                client = FastMCPClient(name=server_name, config=server_config)
                await client.init_client()
                
                # 保存客户端实例
                self.clients[server_name] = client
                
                # 4. 获取工具列表
                client_tools = client.get_tool()
                
                if not client_tools:
                    logger.bind(tag=TAG).warning(
                        f"⚠️  服务 {server_name} 没有可用工具"
                    )
                    continue
                
                # 保存工具
                tool_count_before = len(self.tools)
                self.tools.extend(client_tools)
                new_tool_count = len(self.tools) - tool_count_before
                
                logger.bind(tag=TAG).info(
                    f"✅ 服务 {server_name} 初始化成功，"
                    f"获取到 {new_tool_count} 个工具"
                )
                
                # 5. 注册工具到函数注册表
                for tool in client_tools:
                    try:
                        tool_name = tool["function"]["name"]
                        func_name = f"mcp_{tool_name}"
                        
                        # 注册函数装饰器
                        register_function(
                            func_name, 
                            tool, 
                            ToolType.MCP_CLIENT
                        )(self.execute_tool)
                        
                        # 注册到LLM函数处理器
                        self.llm_conn.func_handler.function_registry.register_function(func_name)
                        
                        logger.bind(tag=TAG).debug(
                            f"  ✓ 工具已注册: {func_name}"
                        )
                        
                    except Exception as e:
                        logger.bind(tag=TAG).error(
                            f"  ✗ 工具注册失败 [{tool_name}]: {e}"
                        )
                        continue
                
                success_count += 1
                
            except Exception as e:
                fail_count += 1
                logger.bind(tag=TAG).error(
                    f"❌ 服务 {server_name} 初始化失败: {e}",
                    exc_info=True
                )
                continue
        
        # 6. 更新函数描述
        try:
            self.llm_conn.func_handler.upload_functions_desc()
            logger.bind(tag=TAG).info("✅ LLM函数描述已更新")
        except Exception as e:
            logger.bind(tag=TAG).error(f"更新LLM函数描述失败: {e}")
        
        # 总结
        logger.bind(tag=TAG).info(
            f"\n{'='*60}\n"
            f"MCP客户端初始化完成\n"
            f"  成功: {success_count}/{len(self.mcp_servers)}\n"
            f"  失败: {fail_count}/{len(self.mcp_servers)}\n"
            f"  工具总数: {len(self.tools)}\n"
            f"{'='*60}"
        )
        
        return success_count > 0

    def get_all_tools(self) -> List[Dict[str, Any]]:
        """
        获取所有已注册的MCP工具
        
        Returns:
            List[Dict[str, Any]]: 工具列表
        """
        return self.tools
    
    def is_mcp_tool(self, tool_name: str) -> bool:
        """
        判断指定名称的工具是否为MCP工具
        
        Args:
            tool_name: 工具名称
            
        Returns:
            bool: True表示是MCP工具，False表示不是
        """
        for tool in self.tools:
            function_def = tool.get("function")
            if function_def and function_def.get("name") == tool_name:
                logger.bind(tag=TAG).debug(f"工具 {tool_name} 是MCP工具")
                return True
        
        logger.bind(tag=TAG).debug(f"工具 {tool_name} 不是MCP工具")
        return False
    
    async def execute_tool(self, tool_name: str, tool_args: Dict[str, Any]) -> Any:
        """
        执行MCP工具调用
        
        工作流程：
        1. 移除 'mcp_' 前缀（如果有）
        2. 遍历所有客户端查找包含该工具的客户端
        3. 调用对应客户端的工具
        4. 返回结果
        
        Args:
            tool_name: 工具名称（可能带有 'mcp_' 前缀）
            tool_args: 工具参数字典
            
        Returns:
            Any: 工具执行结果
            
        Raises:
            ValueError: 工具未找到或执行失败时抛出
        """
        # 移除 'mcp_' 前缀（如果有）
        actual_tool_name = tool_name
        if tool_name.startswith("mcp_"):
            actual_tool_name = tool_name[4:]
            logger.bind(tag=TAG).debug(
                f"工具名称包含前缀，转换: {tool_name} -> {actual_tool_name}"
            )
        
        logger.bind(tag=TAG).info(
            f"🔧 执行MCP工具: {actual_tool_name}\n"
            f"   参数: {tool_args}"
        )
        
        try:
            # 遍历所有客户端，查找包含该工具的客户端
            for client_name, client in self.clients.items():
                if client.has_tool(actual_tool_name):
                    logger.bind(tag=TAG).info(
                        f"  ✓ 在客户端 [{client_name}] 中找到工具"
                    )
                    
                    # 执行工具调用
                    result = await client.call_tool(actual_tool_name, tool_args)
                    
                    logger.bind(tag=TAG).info(
                        f"  ✅ 工具执行成功: {actual_tool_name}"
                    )
                    logger.bind(tag=TAG).debug(f"  结果: {result}")
                    
                    return result
            
            # 工具未找到
            available_tools = [t["function"]["name"] for t in self.tools]
            error_msg = (
                f"工具 [{actual_tool_name}] 未找到\n"
                f"可用工具: {available_tools}"
            )
            logger.bind(tag=TAG).error(error_msg)
            raise ValueError(error_msg)
            
        except ValueError:
            # 重新抛出工具未找到的错误
            raise
        except Exception as e:
            error_msg = f"工具 [{actual_tool_name}] 执行失败: {e}"
            logger.bind(tag=TAG).error(error_msg, exc_info=True)
            raise ValueError(error_msg)
    
    async def cleanup(self):
        """
        清理所有MCP客户端资源
        
        关闭所有客户端连接并清理资源
        """
        logger.bind(tag=TAG).info("开始清理MCP客户端资源...")
        
        cleanup_count = 0
        fail_count = 0
        
        for client_name, client in self.clients.items():
            try:
                await client.cleanup()
                cleanup_count += 1
                logger.bind(tag=TAG).info(f"  ✓ 客户端 [{client_name}] 已清理")
            except Exception as e:
                fail_count += 1
                logger.bind(tag=TAG).error(
                    f"  ✗ 客户端 [{client_name}] 清理失败: {e}"
                )
        
        # 清空列表
        self.tools.clear()
        self.clients.clear()
        
        logger.bind(tag=TAG).info(
            f"✅ MCP资源清理完成 - 成功: {cleanup_count}, 失败: {fail_count}"
        )
    
    def get_client_status(self) -> Dict[str, Any]:
        """
        获取所有客户端的状态信息（用于调试和监控）
        
        Returns:
            Dict: 包含所有客户端状态的字典
        """
        status = {
            "total_clients": len(self.clients),
            "total_tools": len(self.tools),
            "clients": {}
        }
        
        for client_name, client in self.clients.items():
            status["clients"][client_name] = {
                "connected": client.client is not None,
                "tool_count": len(client.tools),
                "tools": [tool.name if hasattr(tool, 'name') else str(tool) 
                         for tool in client.tools]
            }
        
        return status