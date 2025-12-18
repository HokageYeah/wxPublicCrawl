from fastapi import APIRouter, Depends, HTTPException, Query, Body
from app.schemas.common_data import ApiResponseData
from app.decorators.cache_decorator import ttl_cache, timed_cache, get_cache
from app.services.test_api import get_wx_hot_topics, search_wx_accounts
from loguru import logger
from typing import Annotated
from fastapi import Cookie, Header, APIRouter
from fastapi import WebSocket, WebSocketException, status

router = APIRouter()
# 测试loguru日志、cachetools缓存接口
@router.get("/hot-topics", response_model=ApiResponseData)
async def get_hot_topics(count: int = Query(10, description="话题数量", ge=1, le=50)):
    """获取热门话题（使用TTL缓存装饰器）
    
    此端点演示了如何使用 loguru 日志和 cachetools TTL缓存
    - 结果将被缓存60秒
    - 可以通过查看日志观察缓存是否生效
    """
    logger.info(f"API请求: 获取热门话题，数量: {count}")

    logger.error(f"API请求: 获取热门话题，数量: {count}")
    
    # 获取缓存信息（可选）
    cache = get_cache("wx_hot_topics")
    cache_info = {
        "cache_name": "wx_hot_topics",
        "cache_size": len(cache) if cache else 0,
        "cache_keys": list(cache.keys()) if cache else []
    }
    logger.debug(f"缓存信息: {cache_info}")
    
    # 调用缓存装饰的函数
    result = await get_wx_hot_topics(count) 
    
    # 构建API响应
    return {
        "data": result,
        "ret": ["SUCCESS::获取热门话题成功"],
    }


@router.get("/search-accounts", response_model=ApiResponseData)
async def search_accounts(
    keyword: str = Query(..., description="搜索关键词"),
    limit: int = Query(5, description="结果数量限制", ge=1, le=20)
):
    """搜索微信公众号账号（使用简单时间缓存装饰器）
    
    此端点演示了如何使用 loguru 日志和 cachetools 简单时间缓存
    - 结果将被缓存30秒
    - 可以通过查看日志观察缓存是否生效
    """
    logger.info(f"API请求: 搜索公众号，关键词: {keyword}，限制: {limit}")
    
    # 调用缓存装饰的异步函数
    result = await search_wx_accounts(keyword, limit)
    
    # 构建API响应
    return {
        "data": result,
        "platform": "WX_PUBLIC",
        "api": "search-accounts",
        "ret": ["SUCCESS::搜索公众号成功"],
        "v": "1.0"
    }

# 测试设置cookie
@router.get("/items/cookie")
async def read_items(ads_cookie: Annotated[str | None, Cookie()] = None):
    print('ads_cookie----', ads_cookie)
    return {"ads_cookie": ads_cookie}

# 测试设置header
@router.get("/items/header")
async def read_items(ads_header: Annotated[str | None, Header()] = None):
    print('ads_header----', ads_header)
    return {"ads_header": ads_header}

# 测试请求头重复的情况
@router.get("/items/header-repeat")
async def read_items(X_Token: Annotated[list[str] | None, Header(alias="X-Token")] = None):
    print('X_Token----', X_Token)
    return {"X_Token": X_Token}


async def get_cookie_or_token(
    websocket: WebSocket,
    session: Annotated[str | None, Cookie()] = None,
    token: Annotated[str | None, Query()] = None,
):
    if session is None and token is None:
        raise WebSocketException(code=status.WS_1008_POLICY_VIOLATION)
    return session or token

# 测试websocket链接
@router.websocket("/items/{item_id}/ws")
async def websocket_endpoint(
    *,
    websocket: WebSocket,
    item_id: str,
    q: int | None = None,
    cookie_or_token: Annotated[str, Depends(get_cookie_or_token)],
):
    await websocket.accept()
    while True:
        data = await websocket.receive_text()
        await websocket.send_text(
            f"Session cookie or query token value is: {cookie_or_token}"
        )
        if q is not None:
            await websocket.send_text(f"Query parameter q is: {q}")
        await websocket.send_text(f"Message text was: {data}, for item ID: {item_id}")

@router.websocket("/simple-ws")
async def simple_websocket(websocket: WebSocket):
    await websocket.accept()
    while True:
        data = await websocket.receive_text()
        await websocket.send_text(f"You sent: {data}")


