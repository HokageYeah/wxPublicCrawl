"""
MCP与LLM连接器
负责连接FastMCP客户端与AI客户端，提供混合查询能力
实现AI模型与MCP工具的协同工作
"""
import json
from typing import Optional, List, Dict, Any, Callable
from loguru import logger

from app.ai.llm.ai_client import AIClient
from app.ai.mcp.mcp_client.client_manager import MCPClientManager
from app.ai.utils.functionHandler import FunctionHandler

TAG = "MCP_LLM_CONNECT"


class MCPLLMConnect:
    """
    MCP与LLM连接器
    
    核心功能：
    1. 整合AIClient和MCPClientManager
    2. 实现Function Calling机制
    3. 处理工具调用循环（AI调用工具 -> 获取结果 -> AI处理结果）
    4. 支持多轮对话和上下文管理
    5. 提供混合查询能力（AI推理 + 工具执行）
    
    使用场景：
    - AI需要使用外部工具完成任务
    - 需要实时数据或外部API调用
    - 复杂的多步骤任务编排
    
    示例：
        # 初始化
        connector = MCPLLMConnect(mcp_manager)
        
        # 发送查询（AI会自动调用需要的工具）
        result = await connector.query("帮我翻到第5页")
        
        # AI会：
        # 1. 理解用户意图
        # 2. 调用 next_page 工具
        # 3. 处理工具返回结果
        # 4. 生成最终回复
    """
    
    def __init__(
        self,
        mcp_manager: MCPClientManager = None,
        ai_client: Optional[AIClient] = None,
        max_tool_calls: int = 15,
        auto_execute_tools: bool = True
    ):
        """
        初始化MCP与LLM连接器
        
        Args:
            mcp_manager: MCP客户端管理器实例
            ai_client: AI客户端实例，如果为None则创建默认实例
            max_tool_calls: 单次对话中最大工具调用次数（防止无限循环）
            auto_execute_tools: 是否自动执行AI请求的工具调用
        """
        self.mcp_manager = mcp_manager or MCPClientManager(self)
        self.ai_client = ai_client or AIClient(enable_history=True)
        self.max_tool_calls = max_tool_calls
        self.auto_execute_tools = auto_execute_tools
        self.func_handler = FunctionHandler(self) # 函数处理

        # 对话历史（包含工具调用）
        self.conversation_history: List[Dict[str, Any]] = []
        
        # 工具调用统计
        self.tool_call_stats = {
            "total_calls": 0,
            "successful_calls": 0,
            "failed_calls": 0,
            "tools_used": {}
        }
        
        logger.bind(tag=TAG).info(
            f"🔧 MCP-LLM连接器实例已创建\n"
            f"   AI模型: {self.ai_client.model}\n"
            f"   最大工具调用: {max_tool_calls}\n"
            f"   自动执行工具: {auto_execute_tools}"
        )
    
    async def async_init(self):
        """
        异步初始化方法，必须在使用前调用
        
        初始化流程：
        1. 初始化MCP客户端管理器（连接到MCP服务器）
        2. 加载可用工具
        3. 注册工具到AI客户端
        
        Returns:
            bool: 初始化是否成功
        """
        logger.bind(tag=TAG).info("🚀 开始异步初始化MCP-LLM连接器...")
        
        try:
            # 1. 初始化MCP客户端
            logger.bind(tag=TAG).info("🔌 正在初始化MCP客户端管理器...")
            init_success = await self.mcp_manager.init_mcp_clients()
            
            if not init_success:
                logger.bind(tag=TAG).warning(
                    "⚠️  MCP客户端初始化失败，可能的原因：\n"
                    "   1. MCP服务器未启动\n"
                    "   2. 配置文件错误\n"
                    "   3. 网络连接问题"
                )
                return False
            
            logger.bind(tag=TAG).info("✅ MCP客户端管理器初始化成功")
            
            # 2. 获取可用工具信息
            all_tools = self.mcp_manager.get_all_tools()
            logger.bind(tag=TAG).info(
                f"📦 已加载工具列表:\n"
                f"   - MCP工具数量: {len(all_tools)}\n"
                f"   - MCP客户端数量: {len(self.mcp_manager.clients)}"
            )
            
            # 3. 打印工具详情
            if all_tools:
                logger.bind(tag=TAG).debug("可用MCP工具:")
                for tool in all_tools:
                    logger.bind(tag=TAG).debug(
                        f"   • {tool.get('name', 'N/A')}: {tool.get('description', 'N/A')}"
                    )
            
            # 4. 检查本地Function Handler
            func_count = len(self.func_handler.functions_desc) if self.func_handler else 0
            logger.bind(tag=TAG).info(f"📦 本地注册函数数量: {func_count}")
            
            logger.bind(tag=TAG).info(
                "✅ MCP-LLM连接器初始化完成！\n"
                f"   - AI模型: {self.ai_client.model}\n"
                f"   - MCP工具: {len(all_tools)}个\n"
                f"   - 本地函数: {func_count}个\n"
                f"   - 总可用功能: {len(all_tools) + func_count}个"
            )
            
            return True
            
        except Exception as e:
            logger.bind(tag=TAG).error(
                f"❌ MCP-LLM连接器初始化失败: {e}",
                exc_info=True
            )
            return False
    
    async def query(
        self,
        user_message: str,
        system_message: Optional[str] = None,
        temperature: Optional[float] = None,
        enable_tools: bool = True
    ) -> str:
        """
        发送查询并获取响应（支持自动工具调用）
        
        工作流程：
        1. 构建消息列表（包含对话历史）
        2. 获取可用的MCP工具列表
        3. 调用AI模型（带工具定义）
        4. 检查AI是否请求工具调用
        5. 如果有工具调用：
           a. 执行工具
           b. 将结果添加到对话
           c. 重新请求AI（最多max_tool_calls次）
        6. 返回最终回复
        
        Args:
            user_message: 用户消息
            system_message: 系统消息（可选）
            temperature: 温度参数（可选）
            enable_tools: 是否启用工具调用
            
        Returns:
            str: AI的最终回复
        """
        logger.bind(tag=TAG).info(
            f"📨 收到用户查询: {user_message[:50]}{'...' if len(user_message) > 50 else ''}"
        )
        
        try:
            # 1. 构建消息列表
            messages = self._build_messages(user_message, system_message)
            
            # 2. 获取可用工具
            tools = self._get_available_tools() if enable_tools else None
            
            if tools:
                logger.bind(tag=TAG).info(
                    f"🔧 可用工具数量: {len(tools)}"
                )
                logger.bind(tag=TAG).debug(
                    f"工具列表: {[t['function']['name'] for t in tools]}"
                )
            
            # 3. 开始对话循环（支持多轮工具调用）
            final_response = await self._conversation_loop(
                messages=messages,
                tools=tools,
                temperature=temperature
            )
            
            logger.bind(tag=TAG).info("✅ 查询完成")
            
            return final_response
            
        except Exception as e:
            logger.bind(tag=TAG).error(f"查询失败: {e}", exc_info=True)
            return f"抱歉，处理您的请求时出现错误: {e}"
    
    async def _conversation_loop(
        self,
        messages: List[Dict[str, Any]],
        tools: Optional[List[Dict[str, Any]]],
        temperature: Optional[float]
    ) -> str:
        """
        对话循环（处理工具调用）
        
        Args:
            messages: 消息列表
            tools: 工具定义列表
            temperature: 温度参数
            
        Returns:
            str: 最终回复
        """
        tool_call_count = 0
        
        while tool_call_count < self.max_tool_calls:
            # 调用AI模型
            response = await self._call_ai_with_tools(
                messages=messages,
                tools=tools,
                temperature=temperature
            )
            
            # 检查是否有工具调用请求
            tool_calls = self._extract_tool_calls(response)
            
            if not tool_calls:
                # 没有工具调用，返回AI的文本回复
                final_text = self._extract_text_response(response)
                
                # 保存到对话历史
                self.conversation_history.append({
                    "role": "assistant",
                    "content": final_text
                })
                
                logger.bind(tag=TAG).info(
                    f"💬 AI回复（无工具调用）: {final_text[:50]}..."
                )
                
                return final_text
            
            # 有工具调用
            tool_call_count += len(tool_calls)
            logger.bind(tag=TAG).info(
                f"🔧 AI请求调用 {len(tool_calls)} 个工具 "
                f"(总计: {tool_call_count}/{self.max_tool_calls})"
            )
            
            # 保存AI的工具调用请求
            self.conversation_history.append({
                "role": "assistant",
                "content": None,
                "tool_calls": tool_calls
            })
            
            # 执行所有工具调用
            tool_results = []
            for tool_call in tool_calls:
                result = await self._execute_tool_call(tool_call)
                tool_results.append(result)
                
                # 添加工具结果到消息列表
                messages.append({
                    "role": "tool",
                    "tool_call_id": tool_call.get("id"),
                    "name": tool_call["function"]["name"],
                    "content": json.dumps(result, ensure_ascii=False)
                })
            
            # 继续循环，让AI处理工具结果
            logger.bind(tag=TAG).debug("继续对话循环，让AI处理工具结果...")
        
        # 达到最大工具调用次数
        logger.bind(tag=TAG).warning(
            f"⚠️  达到最大工具调用次数 ({self.max_tool_calls})"
        )
        return "抱歉，任务过于复杂，已达到最大工具调用次数限制。"
    
    async def _call_ai_with_tools(
        self,
        messages: List[Dict[str, Any]],
        tools: Optional[List[Dict[str, Any]]],
        temperature: Optional[float]
    ) -> Any:
        """
        调用AI模型（带工具定义）
        
        Args:
            messages: 消息列表
            tools: 工具定义
            temperature: 温度参数
            
        Returns:
            AI响应对象
        """
        try:
            # 调用OpenAI API
            response = await self.ai_client.client.chat.completions.create(
                model=self.ai_client.model,
                messages=messages,
                tools=tools,
                tool_choice="auto" if tools else None,
                temperature=temperature if temperature is not None else self.ai_client.temperature,
                max_tokens=self.ai_client.max_tokens
            )
            
            return response
            
        except Exception as e:
            logger.bind(tag=TAG).error(f"调用AI模型失败: {e}", exc_info=True)
            raise
    
    def _extract_tool_calls(self, response: Any) -> List[Dict[str, Any]]:
        """
        从AI响应中提取工具调用请求
        
        Args:
            response: AI响应对象
            
        Returns:
            工具调用列表
        """
        try:
            if not response.choices:
                return []
            
            message = response.choices[0].message
            
            if hasattr(message, 'tool_calls') and message.tool_calls:
                tool_calls = []
                for tc in message.tool_calls:
                    tool_calls.append({
                        "id": tc.id,
                        "type": tc.type,
                        "function": {
                            "name": tc.function.name,
                            "arguments": tc.function.arguments
                        }
                    })
                return tool_calls
            
            return []
            
        except Exception as e:
            logger.bind(tag=TAG).error(f"提取工具调用失败: {e}")
            return []
    
    def _extract_text_response(self, response: Any) -> str:
        """
        从AI响应中提取文本内容
        
        Args:
            response: AI响应对象
            
        Returns:
            文本内容
        """
        try:
            if response.choices:
                message = response.choices[0].message
                return message.content or ""
            return ""
        except Exception as e:
            logger.bind(tag=TAG).error(f"提取文本响应失败: {e}")
            return ""
    
    async def _execute_tool_call(self, tool_call: Dict[str, Any]) -> Dict[str, Any]:
        """
        执行单个工具调用
        
        Args:
            tool_call: 工具调用定义
            
        Returns:
            工具执行结果
        """
        tool_name = tool_call["function"]["name"]
        tool_args_str = tool_call["function"]["arguments"]
        
        try:
            # 解析参数
            tool_args = json.loads(tool_args_str)
            
            logger.bind(tag=TAG).info(
                f"🔧 执行工具: {tool_name}\n"
                f"   参数: {tool_args}"
            )
            
            # 调用MCP管理器执行工具
            result = await self.mcp_manager.execute_tool(tool_name, tool_args)
            
            # 更新统计
            self.tool_call_stats["total_calls"] += 1
            self.tool_call_stats["successful_calls"] += 1
            self.tool_call_stats["tools_used"][tool_name] = \
                self.tool_call_stats["tools_used"].get(tool_name, 0) + 1
            
            logger.bind(tag=TAG).info(f"✅ 工具执行成功: {tool_name}")
            
            # 格式化结果
            return {
                "success": True,
                "result": self._format_tool_result(result),
                "tool_name": tool_name
            }
            
        except json.JSONDecodeError as e:
            logger.bind(tag=TAG).error(f"工具参数JSON解析失败: {e}")
            self.tool_call_stats["total_calls"] += 1
            self.tool_call_stats["failed_calls"] += 1
            
            return {
                "success": False,
                "error": f"参数格式错误: {e}",
                "tool_name": tool_name
            }
            
        except Exception as e:
            logger.bind(tag=TAG).error(
                f"工具执行失败 [{tool_name}]: {e}",
                exc_info=True
            )
            self.tool_call_stats["total_calls"] += 1
            self.tool_call_stats["failed_calls"] += 1
            
            return {
                "success": False,
                "error": str(e),
                "tool_name": tool_name
            }
    
    def _format_tool_result(self, result: Any) -> str:
        """
        格式化工具执行结果为字符串
        
        支持多种格式：
        - 字符串：直接返回
        - 字典/列表：转为JSON
        - MCP响应对象：提取content中的text
        - TextContent对象列表：提取所有text并合并
        
        Args:
            result: 工具执行结果
            
        Returns:
            格式化后的字符串
        """
        try:
            logger.bind(tag=TAG).debug(f"格式化工具结果类型: {type(result)}, 值: {result}")
            
            # 1. 如果是字符串，直接返回
            if isinstance(result, str):
                logger.bind(tag=TAG).debug(f"✅ 结果是字符串: {result}")
                return result
            
            # 2. 如果是MCP响应对象（有content属性）
            if hasattr(result, 'content'):
                logger.bind(tag=TAG).debug(f"检测到MCP响应对象，提取content")
                content_texts = []
                for item in result.content:
                    if hasattr(item, 'text'):
                        content_texts.append(item.text)
                formatted = '\n'.join(content_texts)
                logger.bind(tag=TAG).debug(f"✅ 从MCP响应对象提取文本: {formatted}")
                return formatted
            
            # 3. 如果是列表，检查是否是TextContent对象列表
            if isinstance(result, list):
                # 检查列表是否非空且第一个元素有text属性
                if result and hasattr(result[0], 'text'):
                    logger.bind(tag=TAG).debug(f"检测到TextContent对象列表")
                    texts = []
                    for item in result:
                        if hasattr(item, 'text'):
                            texts.append(item.text)
                    formatted = '\n'.join(texts)
                    logger.bind(tag=TAG).debug(f"✅ 从TextContent列表提取文本: {formatted}")
                    return formatted
                
                # 普通列表，尝试转为JSON
                try:
                    formatted = json.dumps(result, ensure_ascii=False, indent=2)
                    logger.bind(tag=TAG).debug(f"✅ 列表转为JSON: {formatted}")
                    return formatted
                except (TypeError, ValueError) as e:
                    logger.bind(tag=TAG).warning(f"列表无法JSON序列化: {e}，使用str转换")
                    formatted = str(result)
                    return formatted
            
            # 4. 如果是字典，转为JSON
            if isinstance(result, dict):
                try:
                    formatted = json.dumps(result, ensure_ascii=False, indent=2)
                    logger.bind(tag=TAG).debug(f"✅ 字典转为JSON: {formatted}")
                    return formatted
                except (TypeError, ValueError) as e:
                    logger.bind(tag=TAG).warning(f"字典无法JSON序列化: {e}，使用str转换")
                    formatted = str(result)
                    return formatted
            
            # 5. 其他类型，尝试直接转为字符串
            formatted = str(result)
            logger.bind(tag=TAG).debug(f"✅ 其他类型转为字符串: {formatted}")
            return formatted
            
        except Exception as e:
            logger.bind(tag=TAG).error(f"❌ 格式化工具结果失败: {e}", exc_info=True)
            # 兜底：返回字符串形式
            return str(result)
    
    def _build_messages(
        self,
        user_message: str,
        system_message: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        构建消息列表
        
        Args:
            user_message: 用户消息
            system_message: 系统消息
            
        Returns:
            消息列表
        """
        messages = []
        
        # 添加系统消息
        if system_message:
            messages.append({
                "role": "system",
                "content": system_message
            })
        
        # 添加对话历史（可选）
        # messages.extend(self.conversation_history)
        
        # 添加当前用户消息
        messages.append({
            "role": "user",
            "content": user_message
        })
        
        # 保存到对话历史
        self.conversation_history.append({
            "role": "user",
            "content": user_message
        })
        
        return messages
    
    def _get_available_tools(self) -> Optional[List[Dict[str, Any]]]:
        """
        获取所有可用的MCP工具
        
        Returns:
            工具定义列表
        """
        try:
            tools = self.mcp_manager.get_all_tools()
            return tools if tools else None
        except Exception as e:
            logger.bind(tag=TAG).error(f"获取工具列表失败: {e}")
            return None
    
    async def stream_query(
        self,
        user_message: str,
        system_message: Optional[str] = None,
        temperature: Optional[float] = None,
        enable_tools: bool = False
    ):
        """
        流式查询（暂不支持工具调用）
        
        Args:
            user_message: 用户消息
            system_message: 系统消息
            temperature: 温度参数
            enable_tools: 是否启用工具（流式暂不支持）
            
        Yields:
            str: 逐步生成的内容片段
        """
        if enable_tools:
            logger.bind(tag=TAG).warning(
                "流式模式暂不支持工具调用，将禁用工具功能"
            )
        
        # 使用AI客户端的流式方法
        async for chunk in self.ai_client.stream_chat(
            user_message=user_message,
            system_message=system_message,
            temperature=temperature
        ):
            yield chunk
    
    def clear_history(self):
        """清空对话历史"""
        self.conversation_history.clear()
        self.ai_client.clear_history()
        logger.bind(tag=TAG).info("对话历史已清空")
    
    def get_stats(self) -> Dict[str, Any]:
        """
        获取工具调用统计信息
        
        Returns:
            统计信息字典
        """
        return {
            "tool_calls": self.tool_call_stats,
            "conversation_length": len(self.conversation_history),
            "available_tools": len(self.mcp_manager.get_all_tools() or [])
        }
    
    def get_conversation_history(self) -> List[Dict[str, Any]]:
        """获取对话历史"""
        return self.conversation_history.copy()


# 便捷函数
async def create_mcp_llm_connector(
    mcp_manager: MCPClientManager,
    **kwargs
) -> MCPLLMConnect:
    """
    创建MCP-LLM连接器（便捷函数）
    
    Args:
        mcp_manager: MCP客户端管理器
        **kwargs: 其他参数传递给MCPLLMConnect
        
    Returns:
        配置好的连接器实例
    """
    connector = MCPLLMConnect(mcp_manager, **kwargs)
    logger.bind(tag=TAG).info("✅ MCP-LLM连接器创建成功")
    return connector

