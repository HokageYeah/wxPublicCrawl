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
        auto_execute_tools: bool = True,
        user_id: Optional[str] = None
    ):
        """
        初始化MCP与LLM连接器
        
        Args:
            mcp_manager: MCP客户端管理器实例
            ai_client: AI客户端实例，如果为None则创建默认实例
            max_tool_calls: 单次对话中最大工具调用次数（防止无限循环）
            auto_execute_tools: 是否自动执行AI请求的工具调用
            user_id: 用户ID，用于从数据库获取用户专属LLM配置
        """
        self.mcp_manager = mcp_manager or MCPClientManager(self)
        self.ai_client = ai_client or AIClient(enable_history=True, use_db_config=True, user_id=user_id)
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
                    function = tool.get('function', {})
                    logger.bind(tag=TAG).debug(
                        f"   • {function.get('name', 'N/A')}: {function.get('description', 'N/A')}"
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
        enable_tools: bool = True,
        extra_body: Optional[Dict[str, Any]] = None
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
            extra_body: API 额外参数（如 enable_thinking 等）
            
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
                temperature=temperature,
                extra_body=extra_body
            )
            
            logger.bind(tag=TAG).info("✅ 查询完成")
            
            return final_response
            
        except ValueError as e:
            # 业务错误（如速率限制等），直接返回错误信息
            logger.bind(tag=TAG).warning(f"业务错误: {e}")
            return str(e)
            
        except Exception as e:
            # 系统错误，记录详细日志并返回简化信息
            logger.bind(tag=TAG).error(f"查询失败: {e}", exc_info=True)
            return f"抱歉，处理您的请求时出现系统错误，请稍后再试"
    
    async def _conversation_loop(
        self,
        messages: List[Dict[str, Any]],
        tools: Optional[List[Dict[str, Any]]],
        temperature: Optional[float],
        extra_body: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        对话循环（处理工具调用）
        
        Args:
            messages: 消息列表
            tools: 工具定义列表
            temperature: 温度参数
            extra_body: API 额外参数
            
        Returns:
            str: 最终回复
        """
        tool_call_count = 0
        # ============ Kimi-K2.5 无限循环检测 ============
        # 记录连续失败的工具调用，防止无限循环
        consecutive_failures = 0
        max_consecutive_failures = 3  # 连续失败 3 次则停止
        last_error_signature = None  # 记录上次的错误特征
        
        while tool_call_count < self.max_tool_calls:
            # 调用AI模型
            response = await self._call_ai_with_tools(
                messages=messages,
                tools=tools,
                temperature=temperature,
                extra_body=extra_body
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
            
            # ✨ 关键修复：先将 assistant 的 tool_calls 消息添加到 messages
            # DeepSeek 要求严格的消息顺序：user → assistant(tool_calls) → tool
            messages.append({
                "role": "assistant",
                "content": None,
                "tool_calls": tool_calls
            })
            
            # 保存AI的工具调用请求到历史
            self.conversation_history.append({
                "role": "assistant",
                "content": None,
                "tool_calls": tool_calls
            })
            
            # 执行所有工具调用
            tool_results = []
            all_failed = True  # 检测是否所有工具都失败了
            
            for tool_call in tool_calls:
                result = await self._execute_tool_call(tool_call)
                tool_results.append(result)
                
                # 检查是否成功
                if isinstance(result, dict) and result.get("success"):
                    all_failed = False
                
                # 添加工具结果到消息列表（紧跟在 assistant message 之后）
                messages.append({
                    "role": "tool",
                    "tool_call_id": tool_call.get("id"),
                    "name": tool_call["function"]["name"],
                    # 只传递纯结果，去除元数据包装
                    "content": result.get("result", str(result)) if isinstance(result, dict) else str(result)
                })
            
            # ============ Kimi-K2.5 无限循环检测 ============
            # 如果所有工具调用都失败，检测是否陷入循环
            if all_failed:
                # 生成错误特征（工具名称 + 错误类型）
                error_signature = "|".join([
                    f"{r.get('tool_name', 'unknown')}:{r.get('error', '')[:50]}"
                    for r in tool_results if isinstance(r, dict)
                ])
                
                if error_signature == last_error_signature:
                    consecutive_failures += 1
                    logger.bind(tag=TAG).warning(
                        f"⚠️ 检测到连续失败 ({consecutive_failures}/{max_consecutive_failures})：{error_signature[:100]}"
                    )
                    
                    if consecutive_failures >= max_consecutive_failures:
                        model_name = self.ai_client.model
                        logger.bind(tag=TAG).error(
                            f"❌ {model_name} 无限循环检测：连续 {consecutive_failures} 次相同错误，强制退出"
                        )
                        return (
                            f"抱歉，我在处理您的请求时遇到了技术问题。\n"
                            f"问题原因：工具调用反复失败（{tool_calls[0]['function']['name'] if tool_calls else 'unknown'}）\n"
                            f"模型：{model_name}\n"
                            f"建议：请尝试换一种方式描述您的需求，或稍后再试。"
                        )
                else:
                    consecutive_failures = 1
                    last_error_signature = error_signature
            else:
                # 有成功的调用，重置计数器
                consecutive_failures = 0
                last_error_signature = None
            
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
        temperature: Optional[float],
        extra_body: Optional[Dict[str, Any]] = None
    ) -> Any:
        """
        调用AI模型（带工具定义）
        
        Args:
            messages: 消息列表
            tools: 工具定义
            temperature: 温度参数
            extra_body: API 额外参数（如 enable_thinking 等）
                       如果不传，默认禁用 thinking（某些模型需要）
        
        Returns:
            AI响应对象
        """
        try:
            # 如果没有传入 extra_body，使用默认配置（禁用 thinking）
            # 👉 关键：禁止 thinking 可避免某些模型（如 Kimi-K2.5）的兼容性问题
            if extra_body is None:
                extra_body = {"enable_thinking": False}
            
            # 调用OpenAI API
            response = await self.ai_client.client.chat.completions.create(
                model=self.ai_client.model,
                messages=messages,
                tools=tools,
                tool_choice="auto" if tools else None,
                temperature=temperature if temperature is not None else self.ai_client.temperature,
                max_tokens=self.ai_client.max_tokens,
                extra_body=extra_body
            )
            
            return response
            
        except Exception as e:
            # 增强错误处理：处理 OpenAI SDK 和 HTTP 错误
            import httpx
            from openai import RateLimitError, APIError, APIStatusError
            
            # ============ 处理 OpenAI RateLimitError（429）============
            if isinstance(e, RateLimitError):
                # OpenAI SDK 已经包装了 429 错误
                error_msg = (
                    f"API 速率限制：已达到请求上限\n"
                    f"模型: {self.ai_client.model}\n"
                    f"错误信息: {str(e)}\n"
                    f"建议: 请等待 60 秒后重试，或升级 API 计划"
                )
                logger.bind(tag=TAG).warning(f"⚠️ {error_msg}")
                raise ValueError(error_msg)
            
            # ============ 处理其他 OpenAI API 错误 ============
            elif isinstance(e, APIStatusError):
                # 其他 API 状态错误（400, 401, 403, 500等）
                status_code = e.status_code
                error_detail = str(e)
                error_msg = f"API 请求失败 (HTTP {status_code}): {error_detail}"
                logger.bind(tag=TAG).error(error_msg)
                raise ValueError(error_msg)
            
            elif isinstance(e, APIError):
                # 通用 API 错误
                error_msg = f"API 错误: {str(e)}"
                logger.bind(tag=TAG).error(error_msg)
                raise ValueError(error_msg)
            
            # ============ 处理原始 HTTP 错误（兼容旧逻辑）============
            elif isinstance(e, httpx.HTTPStatusError):
                status_code = e.response.status_code
                headers = e.response.headers
                
                # 处理速率限制错误（429）
                if status_code == 429:
                    # 提取速率限制信息
                    remaining = headers.get('modelscope-ratelimit-model-requests-remaining', '未知')
                    limit = headers.get('modelscope-ratelimit-model-requests-limit', '未知')
                    retry_after = headers.get('retry-after', '60')
                    
                    error_msg = (
                        f"API 速率限制：已达到请求上限\n"
                        f"模型: {self.ai_client.model}\n"
                        f"限制: {limit} 次/分钟\n"
                        f"剩余: {remaining} 次\n"
                        f"建议: 请等待 {retry_after} 秒后重试，或升级 API 计划"
                    )
                    logger.bind(tag=TAG).warning(f"⚠️ {error_msg}")
                    raise ValueError(error_msg)
                
                # 处理其他 HTTP 错误
                else:
                    try:
                        error_detail = self._extract_error_message(e.response, status_code)
                    except Exception as extract_err:
                        logger.bind(tag=TAG).debug(f"提取错误信息失败: {extract_err}")
                        error_detail = str(e)
                    
                    error_msg = f"API 请求失败 (HTTP {status_code}): {error_detail}"
                    logger.bind(tag=TAG).error(error_msg)
                    raise ValueError(error_msg)
            
            # ============ 其他未知异常 ============
            else:
                logger.bind(tag=TAG).error(f"调用AI模型失败: {e}", exc_info=True)
                raise
    
    def _extract_error_message(self, response, status_code: int) -> str:
        """
        从错误响应中提取错误信息（兼容多种格式）
        
        Args:
            response: HTTP 响应对象
            status_code: HTTP 状态码
            
        Returns:
            提取的错误信息（保证不会抛出异常）
        """
        try:
            error_body = response.json()
            logger.bind(tag=TAG).debug(f"错误响应体: {error_body}")
            
            # 尝试多种错误格式
            if isinstance(error_body, dict):
                # 格式1: {"error": {"message": "..."}}
                if "error" in error_body:
                    error_obj = error_body["error"]
                    if isinstance(error_obj, dict) and "message" in error_obj:
                        return error_obj["message"]
                    elif isinstance(error_obj, str):
                        return error_obj
                
                # 格式2: {"message": "..."}
                if "message" in error_body:
                    return error_body["message"]
                
                # 格式3: {"errors": [...]}
                if "errors" in error_body:
                    errors = error_body["errors"]
                    if isinstance(errors, list) and errors:
                        # 如果是字典列表，尝试提取 message
                        first_error = errors[0]
                        if isinstance(first_error, dict) and "message" in first_error:
                            return first_error["message"]
                        return str(first_error)
                    elif isinstance(errors, str):
                        return errors
                
                # 格式4: {"detail": "..."}
                if "detail" in error_body:
                    detail = error_body["detail"]
                    if isinstance(detail, str):
                        return detail
                    return str(detail)
            
            # 如果都没匹配，返回整个JSON（限制长度）
            json_str = json.dumps(error_body, ensure_ascii=False)
            return json_str[:500] if len(json_str) > 500 else json_str
            
        except Exception as parse_error:
            # JSON 解析失败，尝试获取文本
            logger.bind(tag=TAG).debug(f"JSON解析错误响应失败: {parse_error}")
            try:
                text = response.text
                logger.bind(tag=TAG).debug(f"错误响应文本: {text[:200]}")
                return text[:200] if len(text) > 200 else text
            except Exception as text_error:
                logger.bind(tag=TAG).debug(f"获取响应文本失败: {text_error}")
                return f"HTTP {status_code} 错误（无法解析响应内容）"
    
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
                raw_tool_calls = []
                for tc in message.tool_calls:
                    raw_tool_calls.append({
                        "id": tc.id,
                        "type": tc.type,
                        "function": {
                            "name": tc.function.name,
                            "arguments": tc.function.arguments
                        }
                    })
                
                # ============ Kimi-K2.5 高级兼容：修复拆分的工具调用 ============
                # Kimi-K2.5 可能将一个正确的工具调用拆成两个：
                # 1. {name: "weather", arguments: ""}
                # 2. {name: "", arguments: '{"location":"罗山"}'}
                # 需要尝试合并或过滤这些异常调用
                
                # 获取当前模型名称，用于日志显示
                model_name = self.ai_client.model
                tool_calls = self._fix_split_tool_calls(raw_tool_calls, model_name)
                return tool_calls
            
            return []
            
        except Exception as e:
            logger.bind(tag=TAG).error(f"提取工具调用失败: {e}")
            return []
    
    def _fix_split_tool_calls(
        self, 
        tool_calls: List[Dict[str, Any]], 
        model_name: str = "unknown"
    ) -> List[Dict[str, Any]]:
        """
        修复 Kimi-K2.5 拆分的工具调用
        
        Kimi-K2.5 特殊问题：将一个工具调用拆成两个：
        - 第一个：有 name 但 arguments 为空
        - 第二个：name 为空但 arguments 正确
        
        策略：
        1. 尝试合并相邻的拆分调用
        2. 过滤掉无法修复的无效调用
        
        Args:
            tool_calls: 原始工具调用列表
            model_name: 模型名称（用于日志显示）
            
        Returns:
            修复后的工具调用列表
        """
        if len(tool_calls) <= 1:
            return tool_calls
        
        fixed_calls = []
        i = 0
        
        while i < len(tool_calls):
            current = tool_calls[i]
            current_name = current.get("function", {}).get("name", "")
            current_args = current.get("function", {}).get("arguments", "")
            
            # 检查当前调用是否有效
            has_valid_name = current_name and current_name.strip()
            has_valid_args = current_args and current_args.strip()
            
            # 如果当前调用完全有效，直接添加
            if has_valid_name and has_valid_args:
                fixed_calls.append(current)
                i += 1
                continue
            
            # 检查是否可以与下一个调用合并（Kimi 拆分修复）
            if i + 1 < len(tool_calls):
                next_call = tool_calls[i + 1]
                next_name = next_call.get("function", {}).get("name", "")
                next_args = next_call.get("function", {}).get("arguments", "")
                
                # 情况1: 当前有 name 无 args，下一个无 name 有 args
                if has_valid_name and not has_valid_args and not (next_name and next_name.strip()) and next_args and next_args.strip():
                    # 合并这两个调用
                    merged_call = {
                        "id": current.get("id"),  # 使用第一个的 ID
                        "type": current.get("type"),
                        "function": {
                            "name": current_name,
                            "arguments": next_args  # 使用第二个的参数
                        }
                    }
                    fixed_calls.append(merged_call)
                    logger.bind(tag=TAG).info(
                        f"🔧 [{model_name}] 工具调用修复：合并拆分调用\n"
                        f"   - 原始: [{current_name}, 空参数] + [空名称, {next_args[:50]}...]\n"
                        f"   - 修复后: [{current_name}, {next_args[:50]}...]"
                    )
                    i += 2  # 跳过下一个（已合并）
                    continue
            
            # 无法合并，检查是否应该过滤
            if has_valid_name and not has_valid_args:
                # 有名称但无参数 - 过滤掉（因为总是会失败）
                logger.bind(tag=TAG).warning(
                    f"⚠️ [{model_name}] 工具调用修复：过滤无参数调用 [{current_name}]"
                )
                i += 1
                continue
            
            if not has_valid_name:
                # 无名称 - 过滤掉
                logger.bind(tag=TAG).warning(
                    f"⚠️ [{model_name}] 工具调用修复：过滤无名称调用"
                )
                i += 1
                continue
            
            # 其他情况，保留原样
            fixed_calls.append(current)
            i += 1
        
        if len(fixed_calls) != len(tool_calls):
            logger.bind(tag=TAG).info(
                f"🔧 [{model_name}] 工具调用修复：{len(tool_calls)} 个调用 → {len(fixed_calls)} 个有效调用"
            )
        
        return fixed_calls
    
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
        
        # ============ Kimi-K2.5 兼容性处理 ============
        # 某些模型（如 Kimi-K2.5）可能返回异常的工具调用格式：
        # 1. name 为空字符串但 arguments 正常
        # 2. arguments 为空字符串但 name 正常
        # 需要过滤掉这些无效的工具调用
        
        model_name = self.ai_client.model
        
        # 检查 tool_name 是否有效
        if not tool_name or not tool_name.strip():
            logger.bind(tag=TAG).warning(
                f"⚠️ [{model_name}] 兼容处理: 工具名称为空，跳过此工具调用\n"
                f"   原始数据: {tool_call}"
            )
            self.tool_call_stats["total_calls"] += 1
            self.tool_call_stats["failed_calls"] += 1
            
            return {
                "success": False,
                "error": f"工具名称为空（可能是 {model_name} 模型响应异常）",
                "tool_name": tool_name or "unknown"
            }
        
        try:
            # 解析参数 - 兼容空字符串情况
            # Kimi-K2.5 有时会返回空字符串作为 arguments
            if not tool_args_str or not tool_args_str.strip():
                logger.bind(tag=TAG).warning(
                    f"⚠️ [{model_name}] 兼容处理: 工具 [{tool_name}] 的参数为空，使用空字典"
                )
                tool_args = {}
            else:
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
            logger.bind(tag=TAG).error(
                f"❌ 工具参数JSON解析失败: {e}\n"
                f"   工具名称: {tool_name}\n"
                f"   参数字符串: '{tool_args_str}'"
            )
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

