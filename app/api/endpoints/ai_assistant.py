"""
AI助手API接口
提供AI对话功能，支持自动调用MCP工具
"""
from fastapi import APIRouter, HTTPException, Body
from pydantic import BaseModel, field_validator
from typing import Optional, Dict, Any
from loguru import logger
import json
from app.schemas.common_data import ApiResponseData, PlatformEnum
from app.services.ai_assistant import (
    init_ai_assistant_service,
    query_ai_assistant,
    clear_ai_history,
    get_ai_stats,
    check_ai_health
)


TAG = "AI_ASSISTANT_API"

router = APIRouter()


# 请求模型
class AIQueryRequest(BaseModel):
    """AI查询请求"""
    # 用户输入的查询内容
    query: str
    # 是否启用工具
    enable_tools: bool = True
    # 温度
    temperature: Optional[float] = None
    # API 额外参数（如 enable_thinking 等）
    # 示例: {"enable_thinking": False} - 禁用思考模式（Kimi-K2.5 需要）
    extra_body: Optional[Dict[str, Any]] = None


class ToolCallInfo(BaseModel):
    """工具调用信息"""
    # 工具名称
    tool_name: str
    # 工具参数
    arguments: Dict[str, Any]
    # 执行结果
    result: str
    # 是否成功
    success: bool
    # 执行时间（可选）
    execution_time: Optional[float] = None

    # 做json转义
    @field_validator('arguments', mode='before')
    @classmethod
    def parse_arguments(cls, v: Any) -> Dict[str, Any]:
        if isinstance(v, str):
            return json.loads(v)
        return v


class AIQueryResponse(BaseModel):
    """AI查询响应"""
    # AI的响应结果
    response: str
    # 工具调用次数
    tool_calls_count: int = 0
    # 工具调用流程列表
    tool_calls: list[ToolCallInfo] = []
    # 是否成功
    success: bool = True
    # 错误信息
    error: Optional[str] = None


async def init_ai_assistant(llm_conn=None):
    """
    初始化AI助手（在应用启动时调用）
    
    委托给服务层处理实际的初始化逻辑
    
    Args:
        llm_conn: 已废弃，保留以兼容旧代码
        
    Returns:
        bool: 初始化是否成功
    """
    return await init_ai_assistant_service(llm_conn)

@router.post("/query", response_model=ApiResponseData)
async def ai_query(request: AIQueryRequest) -> ApiResponseData:
    """
    AI查询接口
    
    用户输入查询，AI会自动决定是否调用MCP工具
    
    支持的功能：
    - 天气查询（如："查询北京的天气"）
    - 计算器（如："计算 10+20"）
    - 知识库查询（如："什么是Python"）
    - 普通对话（如："你好"）
    
    Args:
        request: 包含查询内容的请求
        
    Returns:
        ApiResponseData: 统一的API响应格式
    """
    logger.bind(tag=TAG).info(f"收到AI查询: {request.query}")
    
    # 调用服务层处理业务逻辑
    result = await query_ai_assistant(
        query=request.query,
        enable_tools=request.enable_tools,
        temperature=request.temperature,
        extra_body=request.extra_body
    )
    # 构建 AIQueryResponse 对象
    # ============ Kimi-K2.5 兼容性处理 ============
    # 安全解析工具调用参数，处理空字符串等异常情况
    tool_calls_list = []
    for tool_call in result.get("tool_calls", []):
        try:
            # 获取 arguments 字段
            arguments = tool_call.get("arguments", {})
            
            # 如果是字符串，尝试解析为 JSON
            if isinstance(arguments, str):
                # Kimi-K2.5 兼容：空字符串或空白字符串转为空字典
                if not arguments or not arguments.strip():
                    logger.bind(tag=TAG).debug(
                        f"⚠️ Kimi兼容处理: 工具 [{tool_call.get('tool_name')}] "
                        f"的参数为空字符串，使用空字典"
                    )
                    arguments = {}
                else:
                    arguments = json.loads(arguments)
            
            # 构建 ToolCallInfo 对象
            tool_calls_list.append(ToolCallInfo(**{
                **tool_call,
                "arguments": arguments
            }))
            
        except json.JSONDecodeError as e:
            # JSON 解析失败，记录警告并使用空字典
            logger.bind(tag=TAG).warning(
                f"⚠️ 工具调用参数JSON解析失败: {e}\n"
                f"   工具: {tool_call.get('tool_name')}\n"
                f"   原始参数: {tool_call.get('arguments')}\n"
                f"   使用空字典代替"
            )
            tool_calls_list.append(ToolCallInfo(**{
                **tool_call,
                "arguments": {}
            }))
        except Exception as e:
            # 其他异常，记录错误并跳过该工具调用
            logger.bind(tag=TAG).error(
                f"❌ 处理工具调用信息失败: {e}\n"
                f"   工具: {tool_call.get('tool_name')}"
            )
    
    response_data = AIQueryResponse(
        response=result.get("response", ""),
        tool_calls_count=result.get("tool_calls_count", 0),
        tool_calls=tool_calls_list,
        success=result.get("success", False),
        error=result.get("error")
    )
    logger.bind(tag=TAG).debug(f"AIQueryResponse对象: {json.dumps(response_data.model_dump(), ensure_ascii=False, indent=2)}")
    # 返回统一的 ApiResponseData 格式
    return response_data.model_dump()


@router.post("/clear-history", response_model=ApiResponseData)
async def clear_history() -> ApiResponseData:
    """清空对话历史"""
    logger.bind(tag=TAG).info("请求清空对话历史")
    
    # 调用服务层
    result = await clear_ai_history()
    
    # 返回统一格式
    return ApiResponseData(
        platform=PlatformEnum.WX_PUBLIC,
        api="clear_history",
        data=result,
        ret=[],
        v=1
    )


@router.get("/stats", response_model=ApiResponseData)
async def get_stats() -> ApiResponseData:
    """获取AI助手统计信息"""
    logger.bind(tag=TAG).info("请求获取AI助手统计信息")
    
    # 调用服务层
    result = await get_ai_stats()
    
    # 返回统一格式
    return ApiResponseData(
        platform=PlatformEnum.WX_PUBLIC,
        api="get_stats",
        data=result,
        ret=[],
        v=1
    )


@router.get("/health", response_model=ApiResponseData)
async def health_check() -> ApiResponseData:
    """健康检查"""
    logger.bind(tag=TAG).info("请求健康检查")
    
    # 调用服务层
    result = await check_ai_health()
    
    # 返回统一格式
    return ApiResponseData(
        platform=PlatformEnum.WX_PUBLIC,
        api="health_check",
        data=result,
        ret=[],
        v=1
    )

