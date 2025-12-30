"""
FastMCP客户端实现
负责与单个MCP服务器建立连接和通信
"""
import os
from typing import Dict, Any, Optional, List, Union
from contextlib import AsyncExitStack

from loguru import logger
from fastmcp import Client
from fastmcp.client.transports import PythonStdioTransport, NodeStdioTransport


TAG = "FASTMCP_CLIENT"


class FastMCPClient:
    """
    FastMCP客户端
    
    支持两种传输方式：
    1. streamable-http: 通过HTTP与MCP服务器通信
    2. stdio: 通过标准输入输出与MCP服务器通信（支持Python和Node.js）
    
    功能：
    - 连接MCP服务器
    - 获取可用工具列表
    - 执行工具调用
    - 资源管理和清理
    """
    
    def __init__(self, name: str, config: Dict[str, Any]):
        """
        初始化FastMCP客户端
        
        Args:
            name: 客户端名称（用于日志标识）
            config: 客户端配置字典
        """
        self.name = name
        self.config = config
        self.client: Optional[Client] = None
        self.exit_stack = AsyncExitStack()
        self.tools: List[Any] = []
        
        logger.bind(tag=TAG).debug(f"[{name}] 客户端实例已创建")

    async def init_client(self):
        """
        初始化客户端连接
        
        根据配置的传输类型（HTTP或stdio）建立与MCP服务器的连接
        
        Raises:
            ValueError: 配置错误时抛出
            Exception: 连接失败时抛出
        """
        transport_type = self.config.get("transport", "stdio")
        
        logger.bind(tag=TAG).info(
            f"[{self.name}] 开始初始化MCP客户端 - 传输方式: {transport_type}"
        )
        
        try:
            if transport_type == "streamable-http":
                await self._init_http_client()
            else:
                await self._init_stdio_client()
            
            # 测试连接
            logger.bind(tag=TAG).debug(f"[{self.name}] 测试连接...")
            await self.client.ping()
            logger.bind(tag=TAG).info(f"[{self.name}] ✅ 连接测试成功")
            
            # 获取工具列表
            self.tools = await self.client.list_tools()
            tool_names = [tool.name if hasattr(tool, 'name') else str(tool) 
                         for tool in self.tools]
            
            logger.bind(tag=TAG).info(
                f"[{self.name}] 🔧 获取到 {len(self.tools)} 个工具: {tool_names}"
            )
            
        except Exception as e:
            logger.bind(tag=TAG).error(
                f"[{self.name}] ❌ 初始化客户端失败: {e}",
                exc_info=True
            )
            self.client = None
            raise
    
    async def _init_http_client(self):
        """初始化HTTP传输客户端"""
        base_url = self.config.get("url", "http://127.0.0.1:8000/mcp")
        
        # 确保URL以/结尾
        if not base_url.endswith('/'):
            base_url += '/'
        
        logger.bind(tag=TAG).info(f"[{self.name}] 📡 连接HTTP服务: {base_url}")
        
        # 创建HTTP传输并连接
        self.client = await self.exit_stack.enter_async_context(
            Client(base_url)
        )
    
    async def _init_stdio_client(self):
        """初始化stdio传输客户端"""
        command = self.config.get("command")
        args = self.config.get("args", [])
        
        if not command:
            raise ValueError(f"[{self.name}] stdio传输需要指定command参数")
        
        logger.bind(tag=TAG).info(
            f"[{self.name}] 📡 连接stdio服务: {command} {' '.join(args)}"
        )
        
        # 准备环境变量
        env = {**os.environ}
        if self.config.get("env"):
            env.update(self.config.get("env"))
            logger.bind(tag=TAG).debug(
                f"[{self.name}] 添加环境变量: {list(self.config.get('env').keys())}"
            )
        
        # 根据命令类型选择传输方式
        transport = self._create_transport(command, args, env)
        
        # 创建客户端并连接
        timeout = self.config.get("timeout", 15.0)
        self.client = await self.exit_stack.enter_async_context(
            Client(transport, timeout=timeout)
        )
        
        logger.bind(tag=TAG).debug(
            f"[{self.name}] 客户端创建成功，超时时间: {timeout}s"
        )
    
    def _create_transport(self, command: str, args: List[str], env: Dict[str, str]):
        """
        根据命令类型创建相应的传输对象
        
        Args:
            command: 命令
            args: 参数列表
            env: 环境变量字典
            
        Returns:
            传输对象（PythonStdioTransport或NodeStdioTransport）
        """
        cwd = self.config.get("cwd")
        
        # 处理npx命令
        if command == "npx":
            return self._create_npx_transport(args, env, cwd)
        
        # 处理JS文件
        elif command.endswith('.js'):
            logger.bind(tag=TAG).debug(
                f"[{self.name}] 使用NodeStdioTransport: {command}"
            )
            return NodeStdioTransport(
                script_path=command,
                args=args,
                env=env,
                cwd=cwd
            )
        
        # 处理Python脚本或其他命令
        else:
            logger.bind(tag=TAG).debug(
                f"[{self.name}] 使用PythonStdioTransport: {command}"
            )
            return PythonStdioTransport(
                script_path=command,
                args=args,
                env=env,
                cwd=cwd
            )
    
    def _create_npx_transport(self, args: List[str], env: Dict[str, str], cwd: Optional[str]):
        """
        创建npx命令的传输对象
        
        Args:
            args: npx参数列表
            env: 环境变量
            cwd: 工作目录
            
        Returns:
            NodeStdioTransport对象
        """
        logger.bind(tag=TAG).debug(f"[{self.name}] 处理npx命令: {args}")
        
        # 提取包名（第一个不以-开头的参数）
        package_args = [arg for arg in args if not arg.startswith("-")]
        
        if not package_args:
            raise ValueError(f"[{self.name}] npx命令必须包含包名参数")
        
        package_name = package_args[0]
        logger.bind(tag=TAG).info(f"[{self.name}] NPX包名: {package_name}")
        
        # 创建桥接脚本
        temp_dir = os.path.dirname(os.path.abspath(__file__))
        bridge_file = os.path.join(temp_dir, f"npx_bridge_{self.name}.js")
        
        self._create_npx_bridge_script(bridge_file, package_name)
        
        logger.bind(tag=TAG).debug(f"[{self.name}] 桥接脚本: {bridge_file}")
        
        return NodeStdioTransport(
            script_path=bridge_file,
            args=[],
            env=env,
            cwd=cwd
        )
    
    def has_tool(self, tool_name: str) -> bool:
        """
        检查工具是否存在
        
        Args:
            tool_name: 工具名称
            
        Returns:
            bool: True表示工具存在，False表示不存在
        """
        logger.bind(tag=TAG).debug(
            f"[{self.name}] 检查工具 [{tool_name}] 是否存在"
        )
        
        for tool in self.tools:
            try:
                # 尝试不同方式获取工具名称
                tool_name_value = self._get_tool_name(tool)
                
                if tool_name_value == tool_name:
                    logger.bind(tag=TAG).debug(
                        f"[{self.name}] ✓ 工具 [{tool_name}] 存在"
                    )
                    return True
                    
            except Exception as e:
                logger.bind(tag=TAG).warning(
                    f"[{self.name}] 检查工具时出错: {e}"
                )
                continue
        
        logger.bind(tag=TAG).debug(
            f"[{self.name}] ✗ 工具 [{tool_name}] 不存在"
        )
        return False
    
    def _get_tool_name(self, tool: Any) -> Optional[str]:
        """
        从工具对象中提取工具名称（兼容多种格式）
        
        Args:
            tool: 工具对象
            
        Returns:
            Optional[str]: 工具名称，如果无法提取则返回None
        """
        # 方式1: 字典格式
        if isinstance(tool, dict) and "name" in tool:
            return tool["name"]
        
        # 方式2: 对象属性
        if hasattr(tool, 'name'):
            return tool.name
        
        # 方式3: 可索引对象
        if hasattr(tool, '__getitem__'):
            try:
                return tool["name"]
            except (KeyError, TypeError):
                pass
        
        return None
    
    def get_tool(self) -> Optional[List[Dict[str, Any]]]:
        """
        获取可用工具列表（转换为标准格式）
        
        将MCP工具转换为LLM函数调用格式
        
        Returns:
            Optional[List[Dict[str, Any]]]: 工具列表，如果没有工具则返回None
        """
        if not self.tools:
            logger.bind(tag=TAG).warning(f"[{self.name}] 没有可用工具")
            return None
        
        result = []
        
        for tool in self.tools:
            try:
                # 检查工具是否有必要的属性
                if not hasattr(tool, 'name') or not hasattr(tool, 'description'):
                    logger.bind(tag=TAG).warning(
                        f"[{self.name}] 工具缺少必要属性: {tool}"
                    )
                    continue
                
                # 构建工具函数定义
                tool_def = {
                    "type": "function",
                    "function": {
                        "name": tool.name,
                        "description": tool.description,
                        "parameters": tool.inputSchema if hasattr(tool, 'inputSchema') else {}
                    }
                }
                
                # 如果工具有示例，添加到描述中
                if hasattr(tool, 'examples') and tool.examples:
                    examples_text = "\n\n示例:\n" + "\n".join(
                        [f"- {ex}" for ex in tool.examples]
                    )
                    tool_def["function"]["description"] += examples_text
                
                result.append(tool_def)
                
                logger.bind(tag=TAG).debug(
                    f"[{self.name}] ✓ 工具转换成功: {tool.name}"
                )
                
            except Exception as e:
                logger.bind(tag=TAG).error(
                    f"[{self.name}] 工具转换失败: {e}",
                    exc_info=True
                )
                continue
        
        logger.bind(tag=TAG).info(
            f"[{self.name}] 共转换 {len(result)} 个工具"
        )
        
        return result if result else None
    
    async def call_tool(self, tool_name: str, tool_args: Dict[str, Any]) -> Any:
        """
        调用MCP工具
        
        Args:
            tool_name: 工具名称
            tool_args: 工具参数字典
            
        Returns:
            Any: 工具执行结果
            
        Raises:
            ValueError: 客户端未初始化或工具调用失败
        """
        logger.bind(tag=TAG).info(
            f"[{self.name}] 🔧 调用工具: {tool_name}\n"
            f"   参数: {tool_args}"
        )
        
        try:
            # 检查客户端是否已初始化
            if not self.client:
                error_msg = f"[{self.name}] 客户端未初始化"
                logger.bind(tag=TAG).error(error_msg)
                raise ValueError(error_msg)
            
            # 检查工具是否存在（可选，仅用于日志）
            tool_exists = self.has_tool(tool_name)
            if not tool_exists:
                logger.bind(tag=TAG).warning(
                    f"[{self.name}] 工具 [{tool_name}] 不在工具列表中，尝试直接调用"
                )
            
            # 调用API
            logger.bind(tag=TAG).debug(f"[{self.name}] 正在执行远程调用...")
            response = await self.client.call_tool(tool_name, tool_args)
            
            # 检查响应是否为错误
            if hasattr(response, 'isError') and response.isError:
                error_text = (
                    response.content[0].text 
                    if hasattr(response, 'content') and response.content 
                    else "未知错误"
                )
                logger.bind(tag=TAG).error(
                    f"[{self.name}] ❌ 工具返回错误: {error_text}"
                )
            else:
                logger.bind(tag=TAG).info(
                    f"[{self.name}] ✅ 工具调用成功: {tool_name}"
                )
                logger.bind(tag=TAG).debug(f"[{self.name}] 响应: {response}")
            
            return response
            
        except Exception as e:
            logger.bind(tag=TAG).error(
                f"[{self.name}] ❌ 工具调用失败: {e}",
                exc_info=True
            )
            
            # 返回错误响应对象
            from types import SimpleNamespace
            
            error_content = SimpleNamespace(
                type='text',
                text=f"Error calling tool {tool_name}: {e}"
            )
            error_response = SimpleNamespace(
                content=[error_content],
                isError=True
            )
            
            return error_response
    
    async def cleanup(self):
        """
        清理客户端资源
        
        关闭连接并释放资源
        """
        logger.bind(tag=TAG).info(f"[{self.name}] 开始清理资源...")
        
        try:
            if self.exit_stack:
                await self.exit_stack.aclose()
                logger.bind(tag=TAG).debug(f"[{self.name}] ✓ 退出栈已关闭")
            
            self.client = None
            self.tools.clear()
            
            logger.bind(tag=TAG).info(f"[{self.name}] ✅ 资源清理完成")
            
        except Exception as e:
            logger.bind(tag=TAG).error(
                f"[{self.name}] 资源清理失败: {e}",
                exc_info=True
            )
            raise
    
    def _create_npx_bridge_script(self, script_path: str, package_name: str):
        """
        创建npx桥接脚本
        
        Args:
            script_path: 脚本文件路径
            package_name: NPM包名
        """
        logger.bind(tag=TAG).debug(
            f"[{self.name}] 创建桥接脚本: {script_path}"
        )
        
        script_content = f"""
// 自动生成的NPX桥接脚本 for {self.name}
// Package: {package_name}
const {{ execSync }} = require('child_process');
const path = require('path');
const fs = require('fs');

console.log('[NPX Bridge] Starting {package_name}...');

// 首先确保包已安装
try {{
    // 检查是否已安装
    require.resolve('{package_name}');
    console.log('[NPX Bridge] Package {package_name} is already installed');
}} catch (e) {{
    // 如果未安装，使用npx安装
    console.log('[NPX Bridge] Installing {package_name}...');
    execSync('npx -y {package_name}', {{ stdio: 'inherit' }});
}}

// 导入并运行包
try {{
    require('{package_name}');
}} catch (e) {{
    console.error('[NPX Bridge] Failed to run {package_name}:', e);
    process.exit(1);
}}
"""
        
        try:
            with open(script_path, "w", encoding="utf-8") as f:
                f.write(script_content)
            
            logger.bind(tag=TAG).info(
                f"[{self.name}] ✅ 桥接脚本已创建: {script_path}"
            )
            
        except Exception as e:
            logger.bind(tag=TAG).error(
                f"[{self.name}] 创建桥接脚本失败: {e}"
            )
            raise
    
    def get_status(self) -> Dict[str, Any]:
        """
        获取客户端状态信息（用于调试和监控）
        
        Returns:
            Dict: 客户端状态字典
        """
        return {
            "name": self.name,
            "connected": self.client is not None,
            "tool_count": len(self.tools),
            "tools": [self._get_tool_name(tool) for tool in self.tools],
            "config": {
                "transport": self.config.get("transport"),
                "url": self.config.get("url"),
                "command": self.config.get("command")
            }
        }