"""
AI助手服务层
处理AI助手相关的业务逻辑
"""
from typing import Optional, Dict, Any, List
from loguru import logger
import json
from app.ai.llm.mcp_llm_connect import MCPLLMConnect
from app.schemas.common_data import ApiResponseData, PlatformEnum


TAG = "AI_ASSISTANT_SERVICE"

# 全局连接器实例
_global_connector: Optional[MCPLLMConnect] = None


async def init_ai_assistant_service(llm_conn=None, user_id: Optional[str] = None) -> bool:
    """
    初始化AI助手服务
    
    这个函数会：
    1. 创建MCPLLMConnect连接器实例
    2. 调用async_init()完成异步初始化
    3. 连接器会自动创建AI客户端和MCP管理器
    
    Args:
        llm_conn: 已废弃，保留以兼容旧代码
        user_id: 用户ID，用于加载用户专属的LLM配置
        
    Returns:
        bool: 初始化是否成功
    """
    global _global_connector
    
    logger.bind(tag=TAG).info("=" * 80)
    logger.bind(tag=TAG).info(f"🚀 开始初始化AI助手服务... (user_id: {user_id})")
    logger.bind(tag=TAG).info("=" * 80)
    
    try:
        # 1. 创建连接器实例（同步），传递user_id以加载用户配置
        logger.bind(tag=TAG).info("📝 创建MCP-LLM连接器实例...")
        _global_connector = MCPLLMConnect(user_id=user_id)
        logger.bind(tag=TAG).info("✅ 连接器实例创建成功")
        
        # 2. 异步初始化（连接MCP服务器、加载工具等）
        logger.bind(tag=TAG).info("🔌 开始异步初始化...")
        init_success = await _global_connector.async_init()
        
        if not init_success:
            logger.bind(tag=TAG).warning(
                "⚠️  AI助手初始化部分失败\n"
                "   - 基础对话功能可用\n"
                "   - MCP工具功能不可用\n"
                "   - 建议检查MCP服务器状态"
            )
            # 不抛出异常，允许应用继续运行
            return False
        
        logger.bind(tag=TAG).info("=" * 80)
        logger.bind(tag=TAG).info("✅ AI助手服务初始化成功！")
        logger.bind(tag=TAG).info("=" * 80)
        
        return True
        
    except Exception as e:
        logger.bind(tag=TAG).error("=" * 80)
        logger.bind(tag=TAG).error(f"❌ AI助手初始化失败: {e}", exc_info=True)
        logger.bind(tag=TAG).error("=" * 80)
        
        # 清理全局连接器
        _global_connector = None
        
        # 不抛出异常，允许应用继续运行
        return False


def get_ai_connector() -> Optional[MCPLLMConnect]:
    """
    获取全局连接器实例
    
    Returns:
        MCPLLMConnect: 连接器实例，如果未初始化则返回None
    """
    return _global_connector


async def query_ai_assistant(
    query: str,
    enable_tools: bool = True,
    temperature: Optional[float] = None,
    system_message: Optional[str] = None,
    extra_body: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    向AI助手发送查询
    
    Args:
        query: 用户查询内容
        enable_tools: 是否启用工具调用
        temperature: 温度参数
        system_message: 系统消息（可选）
        extra_body: API 额外参数（如 enable_thinking 等）
        
    Returns:
        Dict: 包含AI响应、工具调用信息等的字典
    """
    logger.bind(tag=TAG).info(f"收到AI查询: {query}")
    
    try:
        # 1. 检查连接器是否已初始化
        connector = get_ai_connector()
        if connector is None:
            logger.bind(tag=TAG).error("AI助手服务未初始化")
            return {
                "success": False,
                "response": "AI助手服务未初始化，请先启动MCP服务",
                "error": "Service not initialized",
                "tool_calls_count": 0,
                "tool_calls": []
            }
        
        # 2. 设置默认系统消息
        if system_message is None:
            system_message = "你是一个有用的AI助手。当用户需要查询天气、进行计算或查找知识时，请使用相应的工具。"
        
        # 3. 发送查询到AI
        response_text = await connector.query(
            user_message=query,
            system_message=system_message,
            temperature=temperature,
            enable_tools=enable_tools,
            extra_body=extra_body
        )
        
        # 4. 获取统计信息
        stats = connector.get_stats()
        tool_calls_count = stats['tool_calls']['total_calls']
        
        # 5. 获取工具调用流程（从对话历史中提取）
        tool_calls_info = _extract_tool_calls_from_history(connector)
        
        logger.bind(tag=TAG).info(
            f"AI查询完成 - 工具调用: {tool_calls_count}次"
        )
        
        return {
            "success": True,
            "response": response_text,
            "tool_calls_count": tool_calls_count,
            "tool_calls": tool_calls_info,
            "error": None
        }
        
    except Exception as e:
        logger.bind(tag=TAG).error(f"AI查询失败: {e}", exc_info=True)
        return {
            "success": False,
            "response": "抱歉，处理您的请求时出现错误。",
            "tool_calls_count": 0,
            "tool_calls": [],
            "error": str(e)
        }


def _extract_tool_calls_from_history(connector: MCPLLMConnect) -> List[Dict[str, Any]]:
    """
    从连接器的对话历史中提取工具调用信息
    
    Args:
        connector: MCP-LLM连接器实例
        
    Returns:
        List[Dict]: 工具调用信息列表
    """
    tool_calls = []
    
    try:
        # 从对话历史中提取工具调用
        conversation_history = connector.conversation_history
        
        for message in conversation_history:
            # 检查是否是工具调用消息
            if message.get("role") == "assistant" and "tool_calls" in message:
                for tool_call in message.get("tool_calls", []):
                    logger.bind(tag=TAG).debug(f"工具调用信息- tool_call: {json.dumps(tool_call, ensure_ascii=False, indent=2)}")
                    
                    # ============ Kimi-K2.5 兼容性处理 ============
                    # Kimi-K2.5 可能返回异常格式：name 或 arguments 为空字符串
                    # 需要过滤和清理这些无效数据
                    
                    tool_name = tool_call.get("function", {}).get("name", "unknown")
                    tool_args = tool_call.get("function", {}).get("arguments", {})
                    
                    # 跳过无效的工具调用（name 为空）
                    if not tool_name or not tool_name.strip():
                        logger.bind(tag=TAG).warning(
                            f"⚠️ Kimi兼容处理: 跳过工具名称为空的调用"
                        )
                        continue
                    
                    # 处理 arguments：如果是空字符串，转为空字典
                    if isinstance(tool_args, str):
                        if not tool_args or not tool_args.strip():
                            logger.bind(tag=TAG).debug(
                                f"⚠️ Kimi兼容处理: 工具 [{tool_name}] 的参数为空字符串，转为空字典"
                            )
                            tool_args = "{}"  # 保持字符串格式，后续在API层处理
                    
                    tool_info = {
                        "tool_name": tool_name,
                        "arguments": tool_args,
                        "result": "",  # 结果在下一条消息中
                        "success": True,
                        "execution_time": None
                    }
                    logger.bind(tag=TAG).debug(f"工具调用信息- tool_info: {json.dumps(tool_info, ensure_ascii=False, indent=2)}")
                    tool_calls.append(tool_info)
            
            # 检查是否是工具结果消息
            elif message.get("role") == "tool":
                if tool_calls:  # 如果有待补充结果的工具调用
                    # 将结果添加到最后一个工具调用
                    tool_calls[-1]["result"] = message.get("content", "")
        
        # 如果历史中没有详细信息，从统计中获取
        if not tool_calls:
            stats = connector.get_stats()
            tools_used = stats.get('tool_calls', {}).get('tools_used', {})
            for tool_name, count in tools_used.items():
                tool_calls.append({
                    "tool_name": tool_name,
                    "arguments": {},
                    "result": f"已调用{count}次",
                    "success": True,
                    "execution_time": None
                })
        
    except Exception as e:
        logger.bind(tag=TAG).warning(f"提取工具调用信息失败: {e}")
    
    return tool_calls


async def clear_ai_history() -> Dict[str, Any]:
    """
    清空AI对话历史
    
    Returns:
        Dict: 操作结果
    """
    try:
        connector = get_ai_connector()
        if connector is None:
            return {
                "success": False,
                "message": "AI助手服务未初始化"
            }
        
        connector.clear_history()
        logger.bind(tag=TAG).info("对话历史已清空")
        
        return {
            "success": True,
            "message": "对话历史已清空"
        }
        
    except Exception as e:
        logger.bind(tag=TAG).error(f"清空历史失败: {e}")
        return {
            "success": False,
            "message": f"清空失败: {str(e)}"
        }


async def get_ai_stats() -> Dict[str, Any]:
    """
    获取AI助手统计信息
    
    Returns:
        Dict: 统计信息
    """
    try:
        connector = get_ai_connector()
        if connector is None:
            return {
                "success": False,
                "stats": {},
                "message": "AI助手服务未初始化"
            }
        
        stats = connector.get_stats()
        
        return {
            "success": True,
            "stats": stats
        }
        
    except Exception as e:
        logger.bind(tag=TAG).error(f"获取统计信息失败: {e}")
        return {
            "success": False,
            "stats": {},
            "message": f"获取失败: {str(e)}"
        }


async def check_ai_health() -> Dict[str, Any]:
    """
    检查AI助手服务健康状态
    
    Returns:
        Dict: 健康状态信息
    """
    connector = get_ai_connector()
    
    return {
        "status": "ok" if connector is not None else "not_initialized",
        "ai_available": connector is not None,
        "message": "AI助手服务正常" if connector is not None else "AI助手服务未初始化"
    }

