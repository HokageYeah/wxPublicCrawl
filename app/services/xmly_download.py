"""
喜马拉雅曲目下载相关服务
"""
import httpx
import time
import asyncio
from typing import Dict, Any, List
from fastapi import HTTPException, Request
from loguru import logger
from app.utils.xmly_helper import decrypt_url
import aiofiles


from app.services.xmly import (
    load_xmly_session,
    global_xmly_cookies,
    global_xmly_token
)
from app.decorators.request_decorator import extract_wx_credentials, add_xmly_sign

# 公共请求头
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "application/json, text/plain, */*",
    "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
    "Referer": "https://www.ximalaya.com/",
    "Origin": "https://www.ximalaya.com",
}


async def get_track_download_info(request: Request, track_id: str) -> Dict[str, Any]:
    """
    获取单个曲目的下载信息

    Args:
        request: FastAPI Request对象
        track_id: 曲目ID

    Returns:
        Dict: 曲目下载信息

    Raises:
        HTTPException: 请求失败时抛出
    """
    # 从 request.state 中获取装饰器处理后的 cookies 和 token
    merged_cookies = request.state.xmly_cookies
    final_token = request.state.xmly_token
    
    # 如果cookies为空，尝试从session加载
    if not merged_cookies or len(merged_cookies) == 0:
        session = load_xmly_session()
        if not session:
            raise HTTPException(status_code=401, detail="未登录，请先登录")
        merged_cookies = session['cookies']
        final_token = session['user_info'].get('token', '')
        logger.info("从session中加载喜马拉雅登录信息")

    # 构造下载信息URL
    url = f"https://www.ximalaya.com/mobile-playpage/track/v3/baseInfo/{int(time.time() * 1000)}"
    params = {
        "device": "web",
        "trackId": track_id,
        "trackQualityLevel": 2
    }

    try:
        async with httpx.AsyncClient(verify=False, timeout=30.0) as client:
            logger.info(f"正在获取曲目下载信息，trackId: {track_id}")
            logger.info(f"下载信息请求headers: {headers}")
            logger.info(f"下载信息请求cookies: {merged_cookies}")
            logger.info(f"下载信息请求params: {params}")

            # 发送GET请求
            response = await client.get(url, headers=headers, cookies=merged_cookies, params=params)
            response.raise_for_status()

            # 解析JSON响应
            json_data = response.json()
            # logger.info(f"曲目下载信息响应: {json_data}")
            sound_name = json_data["trackInfo"]["title"]
            intro = json_data["trackInfo"].get("intro", "")
            trackId = json_data["trackInfo"]["trackId"]
            cover_url = json_data["trackInfo"]["coverSmall"] or ""
            encrypted_url_list = json_data["trackInfo"]["playUrlList"]

            sound_info = {
                "name": sound_name, 
                "intro": intro, 
                "trackId": trackId,
                "coverSmall": cover_url,
                0: "", 
                1: "", 
                2: ""
            }
            for encrypted_url in encrypted_url_list:
                if encrypted_url["type"] == "M4A_128" or encrypted_url["type"] == "M4A_64":
                    sound_info[2] = decrypt_url(encrypted_url["url"])
                elif encrypted_url["type"] == "MP3_64":
                    sound_info[1] = decrypt_url(encrypted_url["url"])
                elif encrypted_url["type"] == "MP3_32":
                    sound_info[0] = decrypt_url(encrypted_url["url"])
            logger.info(f'ID为{track_id}的声音解析成功！sound_info: {sound_info}')

            return sound_info

    except httpx.HTTPStatusError as e:
        logger.error(f"HTTP错误: {e}")
        raise HTTPException(status_code=e.response.status_code, detail=str(e))
    except httpx.RequestError as e:
        logger.error(f"请求错误: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        logger.error(f"未知错误: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@add_xmly_sign(headers)
@extract_wx_credentials(
    global_xmly_cookies,
    global_xmly_token,
    cookie_header_name='X-XMLY-Cookies',
    token_header_name='X-XMLY-Token',
    state_cookie_key='xmly_cookies',
    state_token_key='xmly_token'
)
async def batch_get_tracks_download_info(request: Request, track_ids: List[str], album_id: str = "", album_name: str = "") -> Dict[str, Any]:
    """
    批量获取多个曲目的下载信息

    Args:
        request: FastAPI Request对象
        track_ids: 曲目ID列表
        album_id: 专辑ID
        album_name: 专辑名称

    Returns:
        Dict: 批量下载信息

    Raises:
        HTTPException: 请求失败时抛出
    """
    # 从 request.state 中获取装饰器处理后的 cookies 和 token
    merged_cookies = request.state.xmly_cookies
    final_token = request.state.xmly_token

    # 如果cookies为空，尝试从session加载
    if not merged_cookies or len(merged_cookies) == 0:
        session = load_xmly_session()
        if not session:
            raise HTTPException(status_code=401, detail="未登录，请先登录")
        merged_cookies = session['cookies']
        final_token = session['user_info'].get('token', '')
        logger.info("从session中加载喜马拉雅登录信息")

    # 并发获取多个曲目的下载信息
    tasks = []
    for track_id in track_ids:
        task = get_track_download_info(request, track_id)
        tasks.append(task)

    results = await asyncio.gather(*tasks, return_exceptions=True)

    # 处理结果
    success_results = []
    failed_results = []

    for i, result in enumerate(results):
        if isinstance(result, Exception):
            logger.error(f"获取曲目 {track_ids[i]} 下载信息失败: {result}")
            failed_results.append({
                "trackId": track_ids[i],
                "error": str(result)
            })
        else:
            success_results.append({
                "trackId": track_ids[i],
                "data": result,
                "albumId": album_id,
                "albumName": album_name
            })

    return {
        "success": success_results,
        "failed": failed_results,
        "total": len(track_ids),
        "success_count": len(success_results),
        "failed_count": len(failed_results)
    }
