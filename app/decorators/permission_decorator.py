"""
权限校验装饰器
用于对单个端点进行权限校验
"""
import logging
from functools import wraps
from typing import Callable, Optional
from fastapi import HTTPException, status, Request
import httpx

from app.core.config import settings

# 配置日志
logger = logging.getLogger(__name__)


def require_permission(permission: str):
    """
    权限校验装饰器
    
    使用示例:
        @require_permission("wechatpublic")
        async def my_endpoint(request: Request):
            ...
    
    Args:
        permission: 权限标识 (wechatpublic, llmconfig, ximalaya 等)
    
    Raises:
        HTTPException: 当权限校验失败时抛出
    """
    def decorator(func: Callable):
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            # 从参数中获取 Request 对象
            request = None
            for arg in args:
                if isinstance(arg, Request):
                    request = arg
                    break
            
            if not request:
                # 尝试从 kwargs 中获取
                request = kwargs.get("request")
            
            if not request:
                logger.error("装饰器无法获取 Request 对象")
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="服务器内部错误: 无法获取请求对象"
                )
            
            # 从请求头获取 token
            token = request.headers.get("Authorization", "").replace("Bearer ", "")
            if not token:
                logger.warning(f"请求缺少 Authorization 头")
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="缺少授权令牌"
                )
            
            # 从请求头获取 device_id
            device_id_str = request.headers.get("X-Device-Id", "")
            device_ids = [d.strip() for d in device_id_str.split(",") if d.strip()] if device_id_str else []
            
            if not device_ids:
                logger.warning(f"请求缺少 X-Device-Id 头")
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="缺少设备ID"
                )
            
            # 调用权限校验
            is_allowed, error_msg = await _check_permission(
                token=token,
                permission=permission,
                device_ids=device_ids
            )
            
            if not is_allowed:
                logger.warning(f"权限校验失败: {error_msg}")
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=error_msg or "权限验证失败"
                )
            
            logger.debug(f"权限校验通过: {permission}")
            
            # 调用原始函数
            return await func(*args, **kwargs)
        
        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            # 同步函数版本 - 提示使用异步版本
            raise RuntimeError(
                "权限校验装饰器只支持异步函数，请将函数定义为 async def"
            )
        
        # 根据函数类型返回对应的包装器
        import asyncio
        return async_wrapper if asyncio.iscoroutinefunction(func) else sync_wrapper
    
    return decorator


async def _check_permission(
    token: str,
    permission: str,
    device_ids: list[str]
) -> tuple[bool, Optional[str]]:
    """
    调用卡密系统 API 检查权限
    
    Args:
        token: 用户令牌
        permission: 权限标识
        device_ids: 设备ID列表
        
    Returns:
        (是否允许, 错误信息)
    """
    if not settings.PERMISSION_API_URL:
        logger.error("未配置 PERMISSION_API_URL")
        return False, "权限系统配置错误"
    
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.post(
                settings.PERMISSION_API_URL,
                json={
                    "permission": permission,
                    "device_id": device_ids
                },
                headers={
                    "Content-Type": "application/json",
                    "Authorization": f"Bearer {token}"
                }
            )
            
            if response.status_code == 200:
                data = response.json()
                allowed = data.get("allowed", False)
                message = data.get("message", "")
                
                if allowed:
                    logger.info(f"权限校验通过: {permission}, 设备: {device_ids}")
                    return True, None
                else:
                    logger.warning(f"权限校验失败: {message}")
                    return False, message
            else:
                logger.error(f"权限校验API返回错误状态码: {response.status_code}")
                return False, f"权限校验服务错误: {response.status_code}"
                
    except httpx.TimeoutException:
        logger.error("权限校验API请求超时")
        return False, "权限校验服务超时"
    except Exception as e:
        logger.error(f"权限校验失败: {str(e)}")
        return False, f"权限校验异常: {str(e)}"


# 使用示例
"""
from fastapi import APIRouter, Request
from app.decorators.permission_decorator import require_permission

router = APIRouter()

@router.get("/wx/public/articles")
@require_permission("wechatpublic")
async def get_articles(request: Request):
    # 此端点需要 wechatpublic 权限
    return {"articles": []}

@router.get("/wx/public/llm-config/models")
@require_permission("llmconfig")
async def get_models(request: Request):
    # 此端点需要 llmconfig 权限
    return {"models": []}

@router.get("/wx/public/xmly/albums")
@require_permission("ximalaya")
async def get_albums(request: Request):
    # 此端点需要 ximalaya 权限
    return {"albums": []}
"""
