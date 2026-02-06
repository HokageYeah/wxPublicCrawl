"""
权限校验中间件
通过调用远程卡密系统API来验证请求权限
"""
import logging
from typing import Optional
from fastapi import Request, HTTPException, status
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
import httpx

from app.core.config import settings
from app.schemas.common_data import PlatformEnum

# 配置日志
logger = logging.getLogger(__name__)

# 路径前缀到权限标识的映射
# 注意：更具体的路径应该放在前面，以便优先匹配
PATH_PERMISSION_MAPPING = [
    ("/api/v1/wx/public/llm-config", "llmconfig"),
    ("/api/v1/wx/public/xmly", "ximalaya"),
    ("/api/v1/wx/public", "wechatpublic"),
    ("/api/v1/sogou/wx/public", "wechatpublic"),
]
# 定义一个不需要教教研路由的前缀集合，也就是黑明单
BLACKLIST_PERMISSION_PATH_PREFIXES = [
    "/api/v1/wx/public/system",
]


class PermissionMiddleware(BaseHTTPMiddleware):
    """
    权限校验中间件
    对特定路径前缀的请求进行权限校验
    """
    
    async def dispatch(self, request: Request, call_next):
        """
        处理请求，进行权限校验
        
        Args:
            request: FastAPI 请求对象
            call_next: 下一个中间件或路由处理器
            
        Returns:
            响应对象
        """
        path = request.url.path
        
        # 检查路径是否需要权限校验
        permission_type = self._get_permission_type(path)
        
        if permission_type:
            # 需要权限校验
            logger.debug(f"路径 {path} 需要权限校验，权限类型: {permission_type}")
            
            # 从请求头获取 token
            token = request.headers.get("Authorization", "").replace("Bearer ", "")
            if not token:
                logger.warning(f"请求 {path} 缺少 Authorization 头")
                return self._error_response(
                    "缺少授权令牌",
                    status.HTTP_401_UNAUTHORIZED,
                    path
                )
            
            # 从请求头获取 device_id（单个字符串）
            device_id = request.headers.get("X-Device-Id", "").strip()
            
            if not device_id:
                logger.warning(f"请求 {path} 缺少 X-Device-Id 头")
                return self._error_response(
                    "缺少设备ID",
                    status.HTTP_400_BAD_REQUEST,
                    path
                )
            
            # 调用权限校验API
            is_allowed, error_msg = await self._check_permission(
                token=token,
                permission=permission_type,
                device_id=device_id
            )
            print('权限校验结果', is_allowed, error_msg)
            if not is_allowed:
                logger.warning(f"权限校验失败: {error_msg}")
                return self._error_response(
                    error_msg or "权限验证失败",
                    status.HTTP_403_FORBIDDEN,
                    path
                )
            
            logger.debug(f"权限校验通过: {path}")
        
        # 继续处理请求
        response = await call_next(request)
        return response
    
    def _get_permission_type(self, path: str) -> Optional[str]:
        """
        根据路径前缀获取权限类型
        
        Args:
            path: 请求路径
            
        Returns:
            权限类型标识，如果不需要校验则返回 None
        """
        for prefix, permission in PATH_PERMISSION_MAPPING:
            print('你好啊---path---', path)
            print('你好啊---prefix---', prefix)
            for blacklist_prefix in BLACKLIST_PERMISSION_PATH_PREFIXES:
                if path.startswith(blacklist_prefix):
                    return None
            if path.startswith(prefix):
                return permission
        return None
    
    async def _check_permission(
        self,
        token: str,
        permission: str,
        device_id: str
    ) -> tuple[bool, Optional[str]]:
        """
        调用卡密系统 API 检查权限
        
        Args:
            token: 用户令牌
            permission: 权限标识
            device_id: 设备ID字符串
            
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
                        "device_id": device_id  # 卡密系统API期望数组格式
                    },
                    headers={
                        "Content-Type": "application/json",
                        "Authorization": f"Bearer {token}"
                    }
                )
                print('权限校验返回', response.json())
                
                if response.status_code == 200:
                    resp_data = response.json()
                    
                    # 检查是否是标准的 API 响应格式
                    if "data" in resp_data:
                        # 从 data 字段中提取权限校验结果
                        data = resp_data.get("data", {})
                        allowed = data.get("allowed", False)
                        message = data.get("message", "")
                        expire_time = data.get("expire_time", "")
                        
                        if allowed:
                            logger.info(f"权限校验通过: {permission}, 设备: {device_id}, 过期时间: {expire_time}")
                            return True, None
                        else:
                            logger.warning(f"权限校验失败: {message}")
                            return False, message
                    else:
                        # 兼容旧格式（直接返回 allowed 和 message）
                        allowed = resp_data.get("allowed", False)
                        message = resp_data.get("message", "")
                        
                        if allowed:
                            logger.info(f"权限校验通过: {permission}, 设备: {device_id}")
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
    
    def _error_response(
        self,
        error_message: str,
        status_code: int,
        path: str
    ) -> JSONResponse:
        """
        构造错误响应
        
        Args:
            error_message: 错误信息
            status_code: HTTP 状态码
            path: 请求路径
            
        Returns:
            JSON 响应对象
        """
        # 根据路径判断平台
        platform = PlatformEnum.UNKNOWN
        if "/wx/public" in path:
            platform = PlatformEnum.WX_PUBLIC
        elif "/sogou/wx/public" in path:
            platform = PlatformEnum.WX_PUBLIC
        
        return JSONResponse(
            status_code=status_code,
            content={
                "platform": platform,
                "ret": [f"ERROR::{error_message}"],
                "data": {},
                "v": settings.VERSION,
                "api": path.strip("/")
            }
        )
