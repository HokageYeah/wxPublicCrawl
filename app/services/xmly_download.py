"""
喜马拉雅曲目下载相关服务
"""
import httpx
import time
import asyncio
import os
import re
from typing import Dict, Any, List, Optional
from fastapi import HTTPException, Request
from loguru import logger
from app.utils.xmly_helper import decrypt_url
import aiofiles
from app.utils.download_manager import DownloadManager
from app.services.system import system_manager


from app.services.xmly import (
    load_xmly_session,
    global_xmly_cookies,
    global_xmly_token
)
from app.decorators.request_decorator import extract_wx_credentials, add_xmly_sign
from app.models.user_behavior import BehaviorType

# 公共请求头
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "application/json, text/plain, */*",
    "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
    "Referer": "https://www.ximalaya.com/",
    "Origin": "https://www.ximalaya.com",
}


@add_xmly_sign(headers)
@extract_wx_credentials(
    global_xmly_cookies,
    global_xmly_token,
    cookie_header_name='X-XMLY-Cookies',
    token_header_name='X-XMLY-Token',
    state_cookie_key='xmly_cookies',
    state_token_key='xmly_token'
)
async def get_track_play_url(request: Request, album_id: str, user_id: str, track_id: str) -> Dict[str, Any]:
    """
    获取喜马拉雅音频播放链接

    Args:
        request: FastAPI Request对象
        album_id: 专辑ID
        user_id: 用户ID
        track_id: 曲目ID

    Returns:
        Dict: 包含播放链接的音频信息
        {
            "success": True,
            "data": {
                "trackId": "曲目ID",
                "title": "曲目标题",
                "intro": "简介",
                "coverSmall": "封面URL",
                "duration": 时长,
                "playUrls": {
                    "high": "高品质播放链接(M4A)",
                    "medium": "中品质播放链接(MP3_64)",
                    "low": "低品质播放链接(MP3_32)"
                }
            }
        }

    Raises:
        HTTPException: 请求失败时抛出
    """
    import aiohttp

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

    logger.info(f"开始获取音频播放链接: albumId={album_id}, userId={user_id}, trackId={track_id}")

    try:
        # 创建 aiohttp session
        session = aiohttp.ClientSession()

        # 调用 _async_analyze_sound 解析音频详情
        sound_info = await _async_analyze_sound(track_id, session, headers, merged_cookies)

        # 关闭 session
        await session.close()

        # 检测是否触发速率限制
        if sound_info == "RATE_LIMITED":
            logger.warning("获取音频播放链接触发速率限制")
            raise HTTPException(status_code=429, detail="请求过于频繁，请稍后再试")

        if sound_info is False or sound_info == 0:
            logger.error(f"获取音频播放链接失败: {sound_info}")
            raise HTTPException(status_code=400, detail="获取音频播放链接失败或未授权")

        # 解析成功，返回播放链接信息
        result = {
            "success": True,
            "trackId": sound_info.get("trackId", ""),
            "title": sound_info.get("name", ""),
            "intro": sound_info.get("intro", ""),
            "coverSmall": sound_info.get("coverSmall", ""),
            "duration": 0,  # API 返回中没有 duration 字段
            "playUrls": {
                "high": sound_info.get(2, ""),      # M4A_64/M4A_128
                "medium": sound_info.get(1, ""),    # MP3_64
                "low": sound_info.get(0, "")       # MP3_32
            }
        }

        logger.info(f"成功获取音频播放链接: trackId={track_id}, title={result['title']}")
        return result

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"获取音频播放链接异常: {e}")
        raise HTTPException(status_code=500, detail=f"获取音频播放链接失败: {str(e)}")


# async def get_track_download_info(request: Request, track_id: str) -> Dict[str, Any]:
#     """
#     获取单个曲目的下载信息

#     Args:
#         request: FastAPI Request对象
#         track_id: 曲目ID

#     Returns:
#         Dict: 曲目下载信息

#     Raises:
#         HTTPException: 请求失败时抛出
#     """
#     # 从 request.state 中获取装饰器处理后的 cookies 和 token
#     merged_cookies = request.state.xmly_cookies
#     final_token = request.state.xmly_token

#     # 如果cookies为空，尝试从session加载
#     if not merged_cookies or len(merged_cookies) == 0:
#         session = load_xmly_session()
#         if not session:
#             raise HTTPException(status_code=401, detail="未登录，请先登录")
#         merged_cookies = session['cookies']
#         final_token = session['user_info'].get('token', '')
#         logger.info("从session中加载喜马拉雅登录信息")

#     # 构造下载信息URL
#     url = f"https://www.ximalaya.com/mobile-playpage/track/v3/baseInfo/{int(time.time() * 1000)}"
#     params = {
#         "device": "web",
#         "trackId": track_id,
#         "trackQualityLevel": 2
#     }

#     try:
#         async with httpx.AsyncClient(verify=False, timeout=30.0) as client:
#             logger.info(f"正在获取曲目下载信息，trackId: {track_id}")
#             logger.info(f"下载信息请求headers: {headers}")
#             logger.info(f"下载信息请求cookies: {merged_cookies}")
#             logger.info(f"下载信息请求params: {params}")

#             # 发送GET请求
#             response = await client.get(url, headers=headers, cookies=merged_cookies, params=params)
#             response.raise_for_status()

#             # 解析JSON响应
#             json_data = response.json()
#             # logger.info(f"曲目下载信息响应: {json_data}")
#             sound_name = json_data["trackInfo"]["title"]
#             intro = json_data["trackInfo"].get("intro", "")
#             trackId = json_data["trackInfo"]["trackId"]
#             cover_url = json_data["trackInfo"]["coverSmall"] or ""
#             encrypted_url_list = json_data["trackInfo"]["playUrlList"]

#             sound_info = {
#                 "name": sound_name,
#                 "intro": intro,
#                 "trackId": trackId,
#                 "coverSmall": cover_url,
#                 0: "",
#                 1: "",
#                 2: ""
#             }
#             for encrypted_url in encrypted_url_list:
#                 if encrypted_url["type"] == "M4A_128" or encrypted_url["type"] == "M4A_64":
#                     sound_info[2] = decrypt_url(encrypted_url["url"])
#                 elif encrypted_url["type"] == "MP3_64":
#                     sound_info[1] = decrypt_url(encrypted_url["url"])
#                 elif encrypted_url["type"] == "MP3_32":
#                     sound_info[0] = decrypt_url(encrypted_url["url"])
#             logger.info(f'ID为{track_id}的声音解析成功！sound_info: {sound_info}')

#             return sound_info

#     except httpx.HTTPStatusError as e:
#         logger.error(f"HTTP错误: {e}")
#         raise HTTPException(status_code=e.response.status_code, detail=str(e))
#     except httpx.RequestError as e:
#         logger.error(f"请求错误: {e}")
#         raise HTTPException(status_code=500, detail=str(e))
#     except Exception as e:
#         logger.error(f"未知错误: {e}")
#         raise HTTPException(status_code=500, detail=str(e))

@add_xmly_sign(headers)
@extract_wx_credentials(
    global_xmly_cookies,
    global_xmly_token,
    cookie_header_name='X-XMLY-Cookies',
    token_header_name='X-XMLY-Token',
    state_cookie_key='xmly_cookies',
    state_token_key='xmly_token'
)
async def batch_get_tracks_download_info(request: Request, track_ids: List[str], album_id: str = "", album_name: str = "", user_id: str = "") -> Dict[str, Any]:
    """
    批量获取多个曲目的下载信息（并启动后台下载任务）

    Args:
        request: FastAPI Request对象
        track_ids: 曲目ID列表
        album_id: 专辑ID
        album_name: 专辑名称

    Returns:
        Dict: 批量下载信息，包含成功和失败的统计，以及每个音频的下载进度

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

    # 获取下载路径（使用 get_download_path 方法）
    from app.services.system import system_manager
    download_path = None
    if user_id:
        download_path = system_manager.get_download_path(user_id, BehaviorType.XIMALAYA_DOWNLOAD_PATH)
    
    logger.info(f"用户 {user_id} 的喜马拉雅下载路径: {download_path}")
    if not download_path:
        logger.warning(f"用户 {user_id} 未设置下载路径，使用默认路径")
        # 使用 DownloadManager 默认路径
        download_manager = DownloadManager()
    else:
        logger.info(f"使用下载路径: {download_path}")
        download_manager = DownloadManager(download_path)

    # 串行获取多个曲目的下载信息（避免触发限速）
    import aiohttp
    session = aiohttp.ClientSession()
    sounds = []
    success_results = []
    failed_results = []

    for idx, track_id in enumerate(track_ids, 1):
        try:
            logger.info(f"[{idx}/{len(track_ids)}] 获取曲目 {track_id} 下载信息")

            # 解析音频详情(获取下载URL)
            sound_info = await _async_analyze_sound(track_id, session, headers, merged_cookies)
            logger.info(f"音频详情解析结果: {sound_info}")

            # 检测是否触发速率限制
            if sound_info == "RATE_LIMITED":
                logger.warning("触发速率限制，等待到下个2分钟节点")
                await download_manager.wait_until_next_minute(2)
                # 重试当前音频
                logger.info(f"重试音频: {track_id}")
                sound_info = await _async_analyze_sound(track_id, session, headers, merged_cookies)
                logger.info(f"重试后音频详情解析结果: {sound_info}")

                # 如果重试后还是限速，标记为失败
                if sound_info == "RATE_LIMITED":
                    logger.error(f"曲目 {track_id} 经过重试后仍然触发限速")
                    failed_results.append({
                        "trackId": track_id,
                        "error": "触发速率限制",
                        "status": "failed",
                        "progress": 0
                    })
                    continue

            if sound_info is False or sound_info == 0:
                logger.error(f"音频详情解析失败: {sound_info}")
                failed_results.append({
                    "trackId": track_id,
                    "error": "解析失败或未授权",
                    "status": "failed",
                    "progress": 0
                })
                continue

            # 解析成功，构建适合下载管理器的音频信息
            sound_data = {
                "trackId": sound_info.get("trackId", ""),
                "title": sound_info.get("name", ""),
                "albumTitle": album_name,
                "albumId": album_id,
                "intro": sound_info.get("intro", ""),
                "duration": 0,
                "coverSmall": sound_info.get("coverSmall", ""),
                "anchorName": "",
                0: sound_info.get(0, ""),
                1: sound_info.get(1, ""),
                2: sound_info.get(2, "")
            }
            sounds.append(sound_data)

            success_results.append({
                "trackId": track_id,
                "data": sound_info,
                "albumId": album_id,
                "albumName": album_name,
                "status": "success",
                "progress": 100
            })

            # 请求间隔，避免触发限速（除了最后一个）
            if idx < len(track_ids):
                logger.info("等待10秒后处理下一个曲目...")
                await asyncio.sleep(10)

        except Exception as e:
            error_msg = str(e)
            logger.error(f"获取曲目 {track_id} 下载信息时出错: {error_msg}")

            # 检测速率限制
            if download_manager.is_rate_limited(error_msg):
                logger.warning("检测到速率限制错误，等待到下个2分钟节点")
                await download_manager.wait_until_next_minute(2)
                # 不标记为失败，继续下一个
                continue
            else:
                failed_results.append({
                    "trackId": track_id,
                    "error": error_msg,
                    "status": "failed",
                    "progress": 0
                })

    await session.close()
    logger.info(f"批量获取曲目下载信息完成：成功 {len(success_results)} 个，失败 {len(failed_results)} 个")

    # 如果有成功的音频且提供了专辑信息，启动后台下载任务
    if sounds and album_id and album_name:
        try:
            # 创建后台任务启动下载
            logger.info(f"启动后台下载任务：专辑 {album_name} ({album_id})，共 {len(sounds)} 个音频")

            # 使用 asyncio.create_task 启动后台下载
            asyncio.create_task(
                _background_download_album(
                    sounds=sounds,
                    album_id=int(album_id),
                    album_name=album_name,
                    merged_cookies=merged_cookies,
                    download_manager=download_manager
                )
            )
        except Exception as e:
            logger.error(f"启动后台下载任务失败: {e}")
            # 不影响返回结果，只记录错误

    return {
        "success": success_results,
        "failed": failed_results,
        "total": len(track_ids),
        "success_count": len(success_results),
        "failed_count": len(failed_results),
        "downloading": True if sounds and album_id and album_name else False,
        "message": "下载任务已启动" if sounds and album_id and album_name else "下载信息获取成功"
    }


async def _background_download_album(sounds: List[Dict], album_id: int, album_name: str,
                                   merged_cookies: Dict, download_manager: DownloadManager):
    """
    后台下载专辑音频的任务

    Args:
        sounds: 音频列表
        album_id: 专辑ID
        album_name: 专辑名称
        merged_cookies: cookies字典
        download_manager: 下载管理器实例
    """
    try:
        logger.info(f"开始后台下载专辑: {album_name}")

        # 1. 获取专辑封面
        album_cover = sounds[0].get("coverSmall", "") if sounds else ""

        # 2. 保存专辑解析结果到 JSON 文件
        await download_manager.save_album_info(
            album_id, album_name, album_cover, sounds, "audio"
        )

        # 3. 加载下载进度
        progress = await download_manager.load_progress(album_name)
        if not progress:
            logger.error("无法加载下载进度文件")
            return

        logger.info(f"下载进度: {download_manager.get_download_summary(progress)}")

        # 4. 获取待下载列表
        pending_ids = download_manager.get_pending_downloads(progress)
        logger.info(f"待下载列表: {pending_ids}")
        if not pending_ids:
            logger.info("所有音频已下载完成!")
            return

        logger.info(f"开始下载 {len(pending_ids)} 个音频...")

        # 5. 创建会话
        import aiohttp
        session = aiohttp.ClientSession()

        # 6. 逐个下载音频
        for idx, track_id in enumerate(pending_ids, 1):
            # 查找对应的sound信息
            sound = next((s for s in sounds if str(s.get("trackId")) == track_id), None)
            if not sound:
                continue

            try:
                # 从sounds中查找对应的sound信息（已经解析好的）
                # 不需要再解析，直接下载
                sound_info = {
                    "name": sound.get("title", ""),
                    "intro": sound.get("intro", ""),
                    "trackId": sound.get("trackId", ""),
                    "coverSmall": sound.get("coverSmall", ""),
                    0: sound.get(0, ""),
                    1: sound.get(1, ""),
                    2: sound.get(2, "")
                }

                # 6.2 下载音频文件
                # 优先使用最高音质(2)，降级到中等音质(1)
                quality = 2
                sound_url = sound_info.get(quality, "")
                if not sound_url and quality == 2:
                    sound_url = sound_info.get(1, "")  # 降级到中等音质
                    quality = 1

                if not sound_url:
                    await download_manager.update_download_status(
                        album_name, track_id, "failed", "无可用下载链接", album_id
                    )
                    continue

                # 执行下载
                download_success = await _download_single_audio(
                    sound_info["name"], sound_url, album_name, session, download_manager
                )

                if download_success:
                    # 6.3 下载成功 - 更新进度并写入metadata
                    await download_manager.update_download_status(
                        album_name, track_id, "success", None, album_id
                    )

                    # 构建metadata条目
                    process_title = _replace_invalid_chars(sound_info["name"])
                    local_path = f"{_replace_invalid_chars(album_name)}/{process_title}.mp3"

                    track_metadata = {
                        "track_id": str(sound_info.get("trackId", "")),
                        "title": sound_info.get("name", ""),
                        "cover_url": sound_info.get("coverSmall", ""),
                        "local_path": local_path,
                        "author": sound.get("anchorName", ""),
                        "duration": sound.get("duration", 0),
                        "intro": sound_info.get("intro", "")
                    }

                    # 追加到metadata.json
                    await download_manager.append_to_metadata(album_name, track_metadata)

                    logger.info(f"[{idx}/{len(pending_ids)}] 下载成功: {sound_info['name']}")
                else:
                    # 下载失败
                    await download_manager.update_download_status(
                        album_name, track_id, "failed", "下载文件失败", album_id
                    )
                    logger.error(f"[{idx}/{len(pending_ids)}] 下载失败: {sound_info['name']}")

            except Exception as e:
                error_msg = str(e)
                logger.error(f"下载音频 {track_id} 时出错: {error_msg}")
                await download_manager.update_download_status(
                    album_name, track_id, "failed", error_msg, album_id
                )

        await session.close()


        # 7. 显示最终统计
        final_progress = await download_manager.load_progress(album_name)
        summary = download_manager.get_download_summary(final_progress)
        logger.info(summary)

        # 8. 检查是否全部完成
        if download_manager.is_album_complete(final_progress):
            logger.info("专辑下载完成!")
            # 更新全局状态为 completed
            await download_manager.update_album_status(
                album_id, album_name, "completed",
                total_count=final_progress["total_count"],
                success_count=final_progress["success_count"]
            )
        else:
            logger.warning("部分音频下载失败,可重新运行继续下载")
            # 保持 processing 状态
            await download_manager.update_album_status(
                album_id, album_name, "processing",
                total_count=final_progress["total_count"],
                success_count=final_progress["success_count"]
            )

    except Exception as e:
        logger.error(f"后台下载任务异常: {e}")
        import traceback
        logger.error(traceback.format_exc())


async def _async_analyze_sound(sound_id: str, session, headers: Dict, merged_cookies: Dict) -> Dict:
    """
    协程解析声音

    Args:
        sound_id: 音频ID
        session: aiohttp会话
        headers: 请求头
        merged_cookies: cookies字典

    Returns:
        Dict: 音频信息
    """
    url = f"https://www.ximalaya.com/mobile-playpage/track/v3/baseInfo/{int(time.time() * 1000)}"
    params = {
        "device": "web",
        "trackId": sound_id,
        "trackQualityLevel": 2
    }
    logger.info(f"开始解析音频详情URL: {url}")
    logger.info(f"开始解析音频详情params: {params}")
    logger.info(f"开始解析音频详情session: {session}")
    try:
        import aiohttp
        async with session.get(url, headers=headers, cookies=merged_cookies, params=params, timeout=60) as response:
            response_text = await response.text()
            logger.debug(f"API响应状态码: {response.status}")
            logger.debug(f"API响应内容: {response_text[:500]}...")  # 只打印前500字符

            import json
            response_json = json.loads(response_text)

            # 检查是否有错误信息（可能是速率限制或其他错误）
            if "ret" in response_json and response_json["ret"] != 0:
                error_msg = response_json.get("msg", "未知错误")
                logger.error(f"API返回错误: ret={response_json['ret']}, msg={error_msg}")

                # 检查是否是速率限制
                rate_limit_keywords = ["系统繁忙", "请求过于频繁", "Too Many Requests", "429"]
                if any(keyword in error_msg for keyword in rate_limit_keywords):
                    logger.warning(f"检测到速率限制: {error_msg}")
                    return "RATE_LIMITED"

                # 其他错误
                return False

            # 检查是否有 trackInfo
            if "trackInfo" not in response_json:
                logger.error(f"API响应中缺少 trackInfo 字段")
                logger.debug(f"完整响应: {response_json}")
                return False

            # 解析音频信息
            sound_name = response_json["trackInfo"]["title"]
            intro = response_json["trackInfo"].get("intro", "")
            trackId = response_json["trackInfo"]["trackId"]
            cover_url = response_json["trackInfo"]["coverSmall"] or ""
            encrypted_url_list = response_json["trackInfo"]["playUrlList"]
    except Exception as e:
        logger.error(f'ID为{sound_id}的声音解析失败! {e}')
        return False

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
    logger.info(f'ID为{sound_id}的声音解析成功!')
    return sound_info


async def _download_single_audio(sound_name: str, sound_url: str, album_name: str,
                              session, download_manager: DownloadManager) -> bool:
    """
    下载单个音频文件

    Args:
        sound_name: 音频名称
        sound_url: 下载URL
        album_name: 专辑名称
        session: aiohttp会话
        download_manager: 下载管理器

    Returns:
        bool: 下载是否成功
    """
    retries = 3
    logger.debug(f'开始下载声音{sound_name}')

    sound_name = _replace_invalid_chars(sound_name)

    if '?' in sound_url:
        file_type = sound_url.split('?')[0][-3:]
    else:
        file_type = sound_url[-3:]

    album_name = _replace_invalid_chars(album_name)
    cache_path = download_manager._get_album_cache_path(album_name)
    file_path = f"{cache_path}/{sound_name}.{file_type}"

    # 检查文件是否已存在
    if os.path.exists(file_path):
        logger.info(f'{sound_name}已存在,跳过下载')
        return True

    # 重试下载
    while retries > 0:
        try:
            import aiohttp
            async with session.get(sound_url, headers=headers, timeout=120) as response:
                if response.status == 429:  # Too Many Requests
                    raise Exception("请求过于频繁")

                async with aiofiles.open(file_path, mode="wb") as f:
                    await f.write(await response.content.read())

            logger.debug(f'{sound_name}下载完成')
            return True

        except Exception as e:
            logger.debug(f'{sound_name}第{4 - retries}次下载失败: {str(e)}')

            # 检测速率限制错误
            if download_manager.is_rate_limited(str(e)):
                raise  # 向上传播速率限制错误

            retries -= 1

            if retries > 0:
                await asyncio.sleep(2)  # 重试前等待2秒

    logger.debug(f'{sound_name}经过三次重试后下载失败')
    return False


def _replace_invalid_chars(name: str) -> str:
    """替换文件名中的非法字符"""
    invalid_chars = ['/', '\\', ':', '*', '?', '"', '<', '>', '|']
    for char in invalid_chars:
        if char in name:
            name = name.replace(char, " ")
    return name
