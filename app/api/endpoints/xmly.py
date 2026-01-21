from fastapi import APIRouter, Depends, HTTPException, Response, Request
from loguru import logger

from app.services.xmly import (
    fetch_xmly_generate_qrcode,
    fetch_xmly_check_qrcode_status_with_cookies,
    save_xmly_session,
    get_xmly_login_status,
    clear_xmly_session,
    decode_qrcode_image,
    subscribe_album,
    unsubscribe_album,
    search_album,
    get_album_detail,
    get_tracks_list,
    get_subscribed_albums
)
from app.services.xmly_download import batch_get_tracks_download_info, get_track_play_url
from app.services.system import system_manager
from app.schemas.common_data import ApiResponseData
from app.schemas.xmly_data import (
    XmlyQrcodeResponse,
    XmlyQrcodeStatusResponse,
    XmlyLoginStatusResponse,
    CheckQrcodeStatusRequest,
    SubscribeAlbumRequest,
    SubscribeAlbumResponse,
    SearchAlbumRequest,
    SearchAlbumResponse,
    GetAlbumDetailRequest,
    GetTracksListRequest,
    GetTrackPlayUrlRequest,
    GetSubscribedAlbumsRequest
)

router = APIRouter()


# 喜马拉雅登录流程
@router.post("/login/generate-qrcode", response_model=ApiResponseData)
async def generate_qrcode():
    """
    喜马拉雅登录流程 - 第一步：生成二维码

    返回二维码的base64编码图片和qrId
    qrId用于后续轮询二维码状态
    """
    try:
        # 生成二维码
        qrcode_response = await fetch_xmly_generate_qrcode()

        return {
            "qrId": qrcode_response.qrId,
            "img": qrcode_response.img
        }
    except HTTPException as e:
        logger.error(f"生成二维码失败: {e.detail}")
        raise e
    except Exception as e:
        logger.error(f"生成二维码异常: {e}")
        raise HTTPException(status_code=500, detail=f"生成二维码失败: {str(e)}")


@router.post("/login/check-qrcode-status", response_model=ApiResponseData)
async def check_qrcode_status(params: CheckQrcodeStatusRequest, response: Response):
    """
    喜马拉雅登录流程 - 第二步：检查二维码状态

    Args:
        qrId: 二维码ID

    Returns:
        如果未扫码，返回状态码32000
        如果扫码成功，返回用户信息并保存会话
    """
    try:
        # 检查二维码状态
        result = await fetch_xmly_check_qrcode_status_with_cookies(params.qrId)

        status_data = result['status_data']
        cookies = result['cookies']

        # 检查返回码
        ret = status_data.get('ret', 0)

        # 未扫码
        if ret == 32000:
            return {
                "code": 32000,
                "msg": "等待扫码",
                "scanned": False,
                "user_info": None
            }

        # 扫码成功
        if ret == 0:
            logger.info("用户扫码成功，开始保存会话信息")

            # 保存会话
            save_success = save_xmly_session(status_data, cookies)

            if not save_success:
                logger.error("保存会话失败")
                raise HTTPException(status_code=500, detail="保存会话失败")
            # 构造用户信息
            user_info = {
                "uid": status_data.get('uid'),
                "mobileMask": status_data.get('mobileMask'),
                "token": status_data.get('token'),
                "avatar": status_data.get('avatar'),
                "loginType": status_data.get('loginType')
            }
            logger.info(f"用户扫码成功，开始保存会话信息: {user_info}")
            return {
                "scanned": True,
                "user_info": user_info,
                "code": 0,
                "msg": "登录成功",
                "cookies": cookies or "",
                "token": ''
            }

        # 其他状态
        return {
            "scanned": False,
            "user_info": None,
            "code": ret,
            "msg": status_data.get('msg', '未知状态')
        }

    except HTTPException as e:
        logger.error(f"检查二维码状态失败: {e.detail}")
        raise e
    except Exception as e:
        logger.error(f"检查二维码状态异常: {e}")
        raise HTTPException(status_code=500, detail=f"检查二维码状态失败: {str(e)}")


@router.get("/login/get-session", response_model=ApiResponseData)
async def get_session():
    """
    获取喜马拉雅当前登录状态

    Returns:
        返回当前登录状态和用户信息（如果已登录）
    """
    try:
        login_status = get_xmly_login_status()

        if not login_status.is_logged_in:
            return {
                "is_logged_in": False,
                "user_info": None,
                "cookies": None
            }

        return {
            "is_logged_in": True,
            "user_info": login_status.user_info.dict() if login_status.user_info else None,
            "cookies": login_status.cookies
        }

    except Exception as e:
        logger.error(f"获取登录状态异常: {e}")
        raise HTTPException(status_code=500, detail=f"获取登录状态失败: {str(e)}")


@router.delete("/login/logout", response_model=ApiResponseData)
async def logout():
    """
    退出喜马拉雅登录

    清除本地保存的会话信息
    """
    try:
        success = clear_xmly_session()

        if success:
            logger.info("喜马拉雅登出成功")
            return {
                "code": 0,
                "msg": "登出成功"
            }
        else:
            logger.error("喜马拉雅登出失败")
            raise HTTPException(status_code=500, detail="登出失败")

    except Exception as e:
        logger.error(f"登出异常: {e}")
        raise HTTPException(status_code=500, detail=f"登出失败: {str(e)}")


# 生成二维码图片接口（用于直接返回图片）
@router.get("/login/qrcode-image")
async def get_qrcode_image():
    """
    生成二维码并返回图片（直接返回图片格式）

    Content-Type: image/png
    """
    try:
        # 生成二维码
        qrcode_response = await fetch_xmly_generate_qrcode()

        # 解码图片
        img_data = decode_qrcode_image(qrcode_response.img)

        # 返回图片
        return Response(content=img_data, media_type="image/png")

    except HTTPException as e:
        logger.error(f"获取二维码图片失败: {e.detail}")
        raise e
    except Exception as e:
        logger.error(f"获取二维码图片异常: {e}")
        raise HTTPException(status_code=500, detail=f"获取二维码图片失败: {str(e)}")


# 喜马拉雅专辑订阅接口
@router.post("/subscription/subscribe", response_model=ApiResponseData)
async def xmly_subscribe_album(request: Request, params: SubscribeAlbumRequest):
    """
    订阅喜马拉雅专辑

    Args:
        albumId: 专辑ID

    Returns:
        {ret: 200, msg: "订阅专辑成功"}
    """
    try:
        # 调用服务层函数，装饰器会自动处理cookie和token
        result = await subscribe_album(request, params.albumId)
        return result

    except HTTPException as e:
        logger.error(f"订阅专辑失败: {e.detail}")
        raise e
    except Exception as e:
        logger.error(f"订阅专辑异常: {e}")
        raise HTTPException(status_code=500, detail=f"订阅专辑失败: {str(e)}")


# 喜马拉雅取消订阅专辑接口
@router.post("/subscription/unsubscribe", response_model=ApiResponseData)
async def xmly_unsubscribe_album(request: Request, params: SubscribeAlbumRequest):
    """
    取消订阅喜马拉雅专辑

    Args:
        albumId: 专辑ID

    Returns:
        {ret: 200, msg: "取消订阅专辑成功"}
    """
    try:
        # 调用服务层函数，装饰器会自动处理cookie和token
        result = await unsubscribe_album(request, params.albumId)
        return result

    except HTTPException as e:
        logger.error(f"取消订阅专辑失败: {e.detail}")
        raise e
    except Exception as e:
        logger.error(f"取消订阅专辑异常: {e}")
        raise HTTPException(status_code=500, detail=f"取消订阅专辑失败: {str(e)}")


# 喜马拉雅搜索专辑接口
@router.post("/album/search", response_model=ApiResponseData)
async def xmly_search_album(request: Request, params: SearchAlbumRequest):
    """
    根据关键词搜索喜马拉雅专辑

    Args:
        kw: 搜索关键词

    Returns:
        包含专辑列表、分页信息等
    """
    try:
        # 调用服务层函数，装饰器会自动处理cookie和token
        result = await search_album(request, params.kw)
        # 将result转换为json
        result_json = result.model_dump_json()
        logger.info(f"搜索专辑返回结果: {result_json}")
        return result_json

    except HTTPException as e:
        logger.error(f"搜索专辑失败: {e.detail}")
        raise e
    except Exception as e:
        logger.error(f"搜索专辑异常: {e}")
        raise HTTPException(status_code=500, detail=f"搜索专辑失败: {str(e)}")


# 喜马拉雅专辑详情查询接口
@router.post("/album/detail", response_model=ApiResponseData)
async def xmly_get_album_detail(request: Request, params: GetAlbumDetailRequest):
    """
    根据专辑ID查询喜马拉雅专辑详情

    Args:
        albumId: 专辑ID

    Returns:
        专辑详情信息
    """
    try:
        # 调用服务层函数，装饰器会自动处理cookie和token
        result = await get_album_detail(request, params.albumId)
        # 将result转换为json
        result_json = result.model_dump_json()
        logger.info(f"专辑详情返回结果: {result_json}")
        return result_json

    except HTTPException as e:
        logger.error(f"查询专辑详情失败: {e.detail}")
        raise e
    except Exception as e:
        logger.error(f"查询专辑详情异常: {e}")
        raise HTTPException(status_code=500, detail=f"查询专辑详情失败: {str(e)}")


# 喜马拉雅曲目列表查询接口
@router.post("/album/tracks", response_model=ApiResponseData)
async def xmly_get_tracks_list(request: Request, params: GetTracksListRequest):
    """
    根据专辑ID获取曲目列表（分页）

    Args:
        albumId: 专辑ID
        pageNum: 页码，默认1
        pageSize: 每页数量，默认30

    Returns:
        曲目列表和分页信息
    """
    try:
        # 调用服务层函数，装饰器会自动处理cookie和token
        result = await get_tracks_list(request, params.albumId, params.pageNum, params.pageSize)
        # 将result转换为json
        result_json = result.model_dump_json()
        logger.info(f"曲目列表返回结果: {result_json}")
        return result_json

    except HTTPException as e:
        logger.error(f"查询曲目列表失败: {e.detail}")
        raise e
    except Exception as e:
        logger.error(f"查询曲目列表异常: {e}")
        raise HTTPException(status_code=500, detail=f"查询曲目列表失败: {str(e)}")


# 喜马拉雅批量曲目下载信息接口（也支持单个曲目）
@router.post("/track/batch-download-info", response_model=ApiResponseData)
async def xmly_batch_get_tracks_download_info(request: Request, params: dict):
    """
    批量获取多个曲目的下载信息（也支持单个曲目）

    Args:
        trackIds: 曲目ID列表（单个曲目时传入包含一个ID的数组）
        albumId: 专辑ID
        albumName: 专辑名称
        userId: 用户ID
    Returns:
        批量下载信息，包含成功和失败的统计
    """
    try:
        # 调用服务层函数，装饰器会自动处理cookie和token
        track_ids = params.get("trackIds", [])
        album_id = params.get("albumId", "")
        album_name = params.get("albumName", "")
        user_id = params.get("userId", "")
        result = await batch_get_tracks_download_info(request, track_ids, album_id, album_name, user_id)
        logger.info(f"批量曲目下载信息返回结果: {result}")
        return result

    except HTTPException as e:
        logger.error(f"批量获取曲目下载信息失败: {e.detail}")
        raise e
    except Exception as e:
        logger.error(f"批量获取曲目下载信息异常: {e}")
        raise HTTPException(status_code=500, detail=f"批量获取曲目下载信息失败: {str(e)}")


# 喜马拉雅查询专辑下载状态接口
@router.post("/album/download-status", response_model=ApiResponseData)
async def xmly_get_album_download_status(request: Request, params: dict):
    """
    查询专辑的下载状态（所有音频的下载状态）

    Args:
        userId: 用户ID
        albumId: 专辑ID
        trackIds: 曲目ID列表（可选，用于过滤）

    Returns:
        专辑下载状态，包括每个音频的下载状态
    """
    try:
        user_id = params.get("userId", "")
        album_id = params.get("albumId", "")

        if not user_id or not album_id:
            return {
                "success": False,
                "message": "参数不完整",
                "data": None
            }

        # 调用服务层获取专辑下载状态
        status = await  system_manager.get_ximalaya_album_download_status(user_id, album_id)

        return status

    except Exception as e:
        logger.error(f"查询专辑下载状态失败: {e}")
        raise HTTPException(status_code=500, detail=f"查询专辑下载状态失败: {str(e)}")


# 喜马拉雅获取音频播放链接接口
@router.post("/track/play-url", response_model=ApiResponseData)
async def xmly_get_track_play_url(request: Request, params: GetTrackPlayUrlRequest):
    """
    获取喜马拉雅音频播放链接

    Args:
        albumId: 专辑ID
        userId: 用户ID
        trackId: 曲目ID

    Returns:
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
    """
    try:
        # 调用服务层函数，装饰器会自动处理cookie和token
        result = await get_track_play_url(request, params.albumId, params.userId, params.trackId)
        logger.info(f"获取音频播放链接返回结果: {result}")
        return result

    except HTTPException as e:
        logger.error(f"获取音频播放链接失败: {e.detail}")
        raise e
    except Exception as e:
        logger.error(f"获取音频播放链接异常: {e}")
        raise HTTPException(status_code=500, detail=f"获取音频播放链接失败: {str(e)}")


# 喜马拉雅获取用户订阅专辑列表接口
@router.post("/subscription/subscribed-albums", response_model=ApiResponseData)
async def xmly_get_subscribed_albums(request: Request, params: GetSubscribedAlbumsRequest):
    """
    获取用户订阅的专辑列表

    Args:
        num: 页码，默认1
        size: 每页数量，默认30
        subType: 订阅类型，1-最近常听，2-最新更新，3-最近订阅，默认3
        category: 分类，默认all

    Returns:
        {
            "ret": 200,
            "data": {
                "albumsInfo": [...],  // 专辑信息列表
                "privateSub": false,
                "pageNum": 1,
                "pageSize": 30,
                "totalCount": 1,
                "uid": 187981619,
                "currentUid": 187981619,
                "categoryCode": "all",
                "categoryArray": [...]  // 分类数组
            }
        }
    """
    try:
        # 调用服务层函数，装饰器会自动处理cookie和token
        result = await get_subscribed_albums(
            request,
            params.num,
            params.size,
            params.subType,
            params.category
        )
        # 将result转换为json
        result_json = result.model_dump_json()
        logger.info(f"获取订阅专辑列表返回结果: {result_json}")
        return result_json

    except HTTPException as e:
        logger.error(f"获取订阅专辑列表失败: {e.detail}")
        raise e
    except Exception as e:
        logger.error(f"获取订阅专辑列表异常: {e}")
        raise HTTPException(status_code=500, detail=f"获取订阅专辑列表失败: {str(e)}")


