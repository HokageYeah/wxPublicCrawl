import httpx
import time
import base64
from typing import Dict, Any, Optional
from fastapi import HTTPException, Request
from loguru import logger
from urllib.parse import quote

from app.schemas.xmly_data import (
    XmlyQrcodeResponse,
    XmlyQrcodeStatusResponse,
    XmlyUserInfo,
    XmlyLoginStatusResponse,
    SearchAlbumResponse,
    SearchAlbumResult,
    SearchAlbumPagination,
    AlbumPriceType,
    AlbumDetailResponse,
    AlbumDetailData,
    AlbumPageMainInfo,
    SubscriptInfo,
    TracksListResponse,
    TracksListData,
    TrackInfo,
    SubscribedAlbumsResponse,
    SubscribedAlbumsData,
    SubscribedAlbumInfo,
    SubscribedAlbumAnchor,
    SubscribedAlbumCategory
)
from app.services.system import system_manager
from app.decorators.request_decorator import extract_wx_credentials, add_xmly_sign
from app.utils.slider_solver import SliderSolver
from app.utils.sign_generator import XimalayaSignNode
from app.utils.xmly_helper import handle_xmly_risk_verification


# 喜马拉雅API基础URL
XMLY_BASE_URL = "https://passport.ximalaya.com"

# 初始化滑块验证器和签名生成器
try:
    slider_solver = SliderSolver(headless=True)  # 滑块验证解决器（Docker环境必须使用headless模式）
    logger.info("✅ 滑块验证器初始化成功")
except Exception as e:
    logger.error(f"❌ 滑块验证器初始化失败: {e}")
    slider_solver = None

try:
    sign_generator = XimalayaSignNode()
    logger.info("✅ 签名生成器初始化成功")
except Exception as e:
    logger.error(f"❌ 签名生成器初始化失败: {e}")
    sign_generator = None

# 公共请求头
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "application/json, text/plain, */*",
    "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
    "Referer": "https://www.ximalaya.com/",
    "Origin": "https://www.ximalaya.com",
    # 注意：xm-sign 不在这里设置，因为：
    # 1. 每次请求都需要新的签名
    # 2. get_xm_sign() 可能返回 None
    # 3. 应该在需要时动态生成
}


async def fetch_xmly_generate_qrcode() -> XmlyQrcodeResponse:
    """
    生成喜马拉雅登录二维码

    Returns:
        XmlyQrcodeResponse: 包含二维码ID和base64编码的图片

    Raises:
        HTTPException: 请求失败时抛出
    """
    url = f"{XMLY_BASE_URL}/web/qrCode/gen?level=L&source=喜马拉雅网页端"

    try:
        async with httpx.AsyncClient(verify=False, timeout=10.0) as client:
            logger.info(f"正在请求喜马拉雅生成二维码接口: {url}")
            response = await client.get(url, headers=headers)
            response.raise_for_status()

            # 解析JSON响应
            json_data = response.json()

            # 检查返回码
            if json_data.get('ret') != 0:
                error_msg = json_data.get('msg', '未知错误')
                logger.error(f"生成二维码失败: {error_msg}")
                raise HTTPException(status_code=400, detail=f"生成二维码失败: {error_msg}")

            # 构造响应对象
            result = XmlyQrcodeResponse(
                ret=json_data['ret'],
                msg=json_data['msg'],
                qrId=json_data['qrId'],
                img=json_data['img']
            )

            logger.info(f"二维码生成成功，qrId: {result.qrId}")
            return result

    except httpx.HTTPStatusError as e:
        logger.error(f"HTTP错误: {e}")
        raise HTTPException(status_code=e.response.status_code, detail=f"HTTP错误: {e}")
    except httpx.RequestError as e:
        logger.error(f"请求错误: {e}")
        raise HTTPException(status_code=500, detail=f"请求错误: {e}")
    except Exception as e:
        logger.error(f"未知错误: {e}")
        raise HTTPException(status_code=500, detail=f"未知错误: {e}")


async def fetch_xmly_check_qrcode_status(qrId: str, cookies: Optional[Dict[str, str]] = None) -> XmlyQrcodeStatusResponse:
    """
    检查喜马拉雅二维码状态

    Args:
        qrId: 二维码ID
        cookies: Cookie字典（可选，用于保持会话）

    Returns:
        XmlyQrcodeStatusResponse: 二维码状态或用户信息

    Raises:
        HTTPException: 请求失败时抛出
    """
    timestamp = int(time.time() * 1000)  # 当前时间戳（毫秒）
    url = f"{XMLY_BASE_URL}/web/qrCode/check/{qrId}/{timestamp}"

    try:
        async with httpx.AsyncClient(verify=False, timeout=10.0) as client:
            logger.info(f"正在检查二维码状态: {url}")

            # 设置请求cookies
            request_cookies = cookies or {}
            response = await client.get(url, headers=headers, cookies=request_cookies)
            response.raise_for_status()

            # 解析JSON响应
            json_data = response.json()

            # 构造响应对象
            result = XmlyQrcodeStatusResponse(
                ret=json_data.get('ret', 0),
                msg=json_data.get('msg', ''),
                bizKey=json_data.get('bizKey'),
                uid=json_data.get('uid'),
                token=json_data.get('token'),
                userType=json_data.get('userType'),
                isFirst=json_data.get('isFirst'),
                toSetPwd=json_data.get('toSetPwd'),
                loginType=json_data.get('loginType'),
                mobileMask=json_data.get('mobileMask'),
                mobileCipher=json_data.get('mobileCipher'),
                captchaInfo=json_data.get('captchaInfo'),
                avatar=json_data.get('avatar'),
                thirdpartyAvatar=json_data.get('thirdpartyAvatar'),
                thirdpartyNickname=json_data.get('thirdpartyNickname'),
                smsKey=json_data.get('smsKey'),
                thirdpartyId=json_data.get('thirdpartyId'),
                authCode=json_data.get('authCode')
            )

            # 记录响应cookies
            response_cookies = {cookie.name: cookie.value for cookie in response.cookies}
            if response_cookies:
                logger.info(f"响应Cookies: {list(response_cookies.keys())}")

            # 如果扫码成功（ret=0），记录用户信息
            if result.ret == 0 and result.uid:
                logger.info(f"用户扫码成功，uid: {result.uid}, mobileMask: {result.mobileMask}")

            return result

    except httpx.HTTPStatusError as e:
        logger.error(f"HTTP错误: {e}")
        raise HTTPException(status_code=e.response.status_code, detail=f"HTTP错误: {e}")
    except httpx.RequestError as e:
        logger.error(f"请求错误: {e}")
        raise HTTPException(status_code=500, detail=f"请求错误: {e}")
    except Exception as e:
        logger.error(f"未知错误: {e}")
        raise HTTPException(status_code=500, detail=f"未知错误: {e}")


def decode_qrcode_image(img_base64: str) -> bytes:
    """
    解码base64编码的二维码图片

    Args:
        img_base64: base64编码的图片字符串

    Returns:
        bytes: 二进制图片数据
    """
    try:
        # 移除可能存在的data URL前缀
        if img_base64.startswith('data:image'):
            img_base64 = img_base64.split(',')[1]

        # Base64解码
        img_data = base64.b64decode(img_base64)
        logger.info(f"二维码图片解码成功，大小: {len(img_data)} bytes")
        return img_data
    except Exception as e:
        logger.error(f"二维码图片解码失败: {e}")
        raise HTTPException(status_code=500, detail=f"二维码图片解码失败: {e}")


async def fetch_xmly_check_qrcode_status_with_cookies(qrId: str) -> Dict[str, Any]:
    """
    检查喜马拉雅二维码状态并获取cookies

    Args:
        qrId: 二维码ID

    Returns:
        Dict: 包含状态数据和响应cookies

    Raises:
        HTTPException: 请求失败时抛出
    """
    timestamp = int(time.time() * 1000)  # 当前时间戳（毫秒）
    url = f"{XMLY_BASE_URL}/web/qrCode/check/{qrId}/{timestamp}"

    try:
        async with httpx.AsyncClient(verify=False, timeout=10.0) as client:
            logger.info(f"正在检查二维码状态: {url}")
            response = await client.get(url, headers=headers)
            response.raise_for_status()

            # 解析JSON响应
            json_data = response.json()
            logger.info(f"检查二维码状态响应: {json_data}")
            logger.info(f"检查二维码状态响应cookies: {response.cookies}")

            # 提取响应cookies
            response_cookies = {cookie[0]: cookie[1] for cookie in response.cookies.items()}
            # 构建cookie字符串
            cookie_str = '; '.join([f"{k}={v}" for k, v in response_cookies.items()])
            logger.info(f"检查二维码状态响应cookie字符串: {cookie_str}")
            logger.info(f"检查二维码状态响应cookies: {response_cookies}")
            # 构造返回数据
            result = {
                'status_data': json_data,
                'cookies': response_cookies
            }

            # 如果扫码成功（ret=0），记录用户信息和cookies
            if json_data.get('ret') == 0:
                logger.info(f"用户扫码成功，uid: {json_data.get('uid')}, mobileMask: {json_data.get('mobileMask')}")
                logger.info(f"获取到的Cookies: {list(response_cookies.keys())}")

            return result

    except httpx.HTTPStatusError as e:
        logger.error(f"HTTP错误: {e}")
        raise HTTPException(status_code=e.response.status_code, detail=f"HTTP错误: {e}")
    except httpx.RequestError as e:
        logger.error(f"请求错误: {e}")
        raise HTTPException(status_code=500, detail=f"请求错误: {e}")
    except Exception as e:
        logger.error(f"未知错误: {e}")
        raise HTTPException(status_code=500, detail=f"未知错误: {e}")


def save_xmly_session(status_data: Dict[str, Any], cookies: Dict[str, str]) -> bool:
    """
    保存喜马拉雅登录会话

    Args:
        status_data: 扫码成功后的状态数据
        cookies: 响应cookies

    Returns:
        bool: 是否保存成功
    """
    try:
        # 构造用户信息
        user_info = {
            'uid': status_data.get('uid'),
            'mobileMask': status_data.get('mobileMask'),
            'token': status_data.get('token'),
            'avatar': status_data.get('avatar'),
            'loginType': status_data.get('loginType'),
            'isFirst': status_data.get('isFirst'),
            'toSetPwd': status_data.get('toSetPwd')
        }

        # 调用system_manager保存会话
        success = system_manager.save_platform_session(
            platform='xmly',
            user_info=user_info,
            cookies=cookies,
            token=status_data.get('token', ''),
            expires_days=7  # 会话有效期为7天
        )

        return success

    except Exception as e:
        logger.error(f"保存喜马拉雅会话失败: {e}")
        return False


def load_xmly_session() -> Optional[Dict[str, Any]]:
    """
    加载喜马拉雅登录会话

    Returns:
        Optional[Dict]: 包含 user_info, cookies 和 token，如果会话不存在或已过期则返回 None
    """
    try:
        return system_manager.load_platform_session('xmly')
    except Exception as e:
        logger.error(f"加载喜马拉雅会话失败: {e}")
        return None


def clear_xmly_session() -> bool:
    """
    清除喜马拉雅登录会话

    Returns:
        bool: 是否清除成功
    """
    try:
        return system_manager.clear_platform_session('xmly')
    except Exception as e:
        logger.error(f"清除喜马拉雅会话失败: {e}")
        return False


def get_xmly_login_status() -> XmlyLoginStatusResponse:
    """
    获取喜马拉雅登录状态

    Returns:
        XmlyLoginStatusResponse: 登录状态信息
    """
    try:
        session = load_xmly_session()

        if session is None:
            return XmlyLoginStatusResponse(
                is_logged_in=False,
                user_info=None,
                cookies=None
            )

        # 构造用户信息对象
        user_info = XmlyUserInfo(
            uid=session['user_info']['uid'],
            mobileMask=session['user_info']['mobileMask'],
            token=session['user_info'].get('token'),
            avatar=session['user_info'].get('avatar'),
            loginType=session['user_info'].get('loginType')
        )

        return XmlyLoginStatusResponse(
            is_logged_in=True,
            user_info=user_info,
            cookies=session.get('cookies')
        )

    except Exception as e:
        logger.error(f"获取喜马拉雅登录状态失败: {e}")
        return XmlyLoginStatusResponse(
            is_logged_in=False,
            user_info=None,
            cookies=None
        )


# NOTE: 订阅接口使用装饰器处理cookie/token，参考微信接口实现模式
# 全局cookies用于存储session中的cookies，如果请求头中有自定义cookies则优先使用
global_xmly_cookies: Dict[str, str] = {}
global_xmly_token: str = ""

@extract_wx_credentials(
    global_xmly_cookies, 
    global_xmly_token,
    cookie_header_name='X-XMLY-Cookies',
    token_header_name='X-XMLY-Token',
    state_cookie_key='xmly_cookies',
    state_token_key='xmly_token'
)
async def subscribe_album(request: Request, album_id: str) -> Dict[str, Any]:
    """
    订阅喜马拉雅专辑

    Args:
        request: FastAPI Request对象
        album_id: 专辑ID

    Returns:
        Dict: 订阅结果 {ret: 200, msg: "订阅专辑成功"}

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

    url = "https://www.ximalaya.com/revision/subscription/setSubscriptionAlbum"

    try:
        async with httpx.AsyncClient(verify=False, timeout=10.0) as client:
            logger.info(f"正在订阅专辑: albumId={album_id}")

            # 构造请求数据
            data = {"albumId": album_id}

            # 发送POST请求
            response = await client.post(url, headers=headers, cookies=merged_cookies, json=data)
            response.raise_for_status()

            # 解析JSON响应
            json_data = response.json()
            logger.info(f"订阅专辑响应: {json_data}")

            return json_data.get('msg', '')

    except httpx.HTTPStatusError as e:
        logger.error(f"HTTP错误: {e}")
        raise HTTPException(status_code=e.response.status_code, detail=f"HTTP错误: {e}")
    except httpx.RequestError as e:
        logger.error(f"请求错误: {e}")
        raise HTTPException(status_code=500, detail=f"请求错误: {e}")
    except Exception as e:
        logger.error(f"未知错误: {e}")
        raise HTTPException(status_code=500, detail=f"未知错误: {e}")


@extract_wx_credentials(
    global_xmly_cookies, 
    global_xmly_token,
    cookie_header_name='X-XMLY-Cookies',
    token_header_name='X-XMLY-Token',
    state_cookie_key='xmly_cookies',
    state_token_key='xmly_token'
)
async def unsubscribe_album(request: Request, album_id: str) -> Dict[str, Any]:
    """
    取消订阅喜马拉雅专辑

    Args:
        request: FastAPI Request对象
        album_id: 专辑ID

    Returns:
        Dict: 取消订阅结果 {ret: 200, msg: "取消订阅专辑成功"}

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

    url = "https://www.ximalaya.com/revision/subscription/cancelSubscriptionAlbum"

    try:
        async with httpx.AsyncClient(verify=False, timeout=10.0) as client:
            logger.info(f"正在取消订阅专辑: albumId={album_id}")

            # 构造请求数据
            data = {"albumId": album_id}

            # 发送POST请求
            response = await client.post(url, headers=headers, cookies=merged_cookies, json=data)
            response.raise_for_status()

            # 解析JSON响应
            json_data = response.json()
            logger.info(f"取消订阅专辑响应: {json_data}")

            return json_data.get('msg', '')

    except httpx.HTTPStatusError as e:
        logger.error(f"HTTP错误: {e}")
        raise HTTPException(status_code=e.response.status_code, detail=f"HTTP错误: {e}")
    except httpx.RequestError as e:
        logger.error(f"请求错误: {e}")
        raise HTTPException(status_code=500, detail=f"请求错误: {e}")
    except Exception as e:
        logger.error(f"未知错误: {e}")
        raise HTTPException(status_code=500, detail=f"未知错误: {e}")


@add_xmly_sign(headers, keyword_param='keyword')
@extract_wx_credentials(
    global_xmly_cookies,
    global_xmly_token,
    cookie_header_name='X-XMLY-Cookies',
    token_header_name='X-XMLY-Token',
    state_cookie_key='xmly_cookies',
    state_token_key='xmly_token'
)
async def search_album(request: Request, keyword: str) -> SearchAlbumResponse:
    """
    根据关键词搜索喜马拉雅专辑

    Args:
        request: FastAPI Request对象
        keyword: 搜索关键词

    Returns:
        SearchAlbumResponse: 搜索结果，包含专辑列表和分页信息

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

    # 构造搜索URL
    url = "https://www.ximalaya.com/revision/search/main"
    params = {
        "core": "all",
        "kw": keyword,
        "spellchecker": "true",
        "device": "iPhone",
        "live": "true"
    }
    logger.info(f"搜索专辑请求headers: {headers}")
    try:
        async with httpx.AsyncClient(verify=False, timeout=10.0) as client:
            logger.info(f"正在搜索专辑，关键词: {keyword}")
            # 发送GET请求（headers 已经由装饰器自动添加 xm-sign 和 Referer）
            response = await client.get(url, headers=headers, cookies=merged_cookies, params=params)
            response.raise_for_status()

            # 解析JSON响应
            json_data = response.json()
            logger.info(f"搜索专辑响应: {json_data}")
            logger.info(f"搜索专辑响应: ret={json_data.get('ret')}")

            # 处理响应（包括风险验证）
            json_data = await handle_xmly_risk_verification(
                client, url, headers, merged_cookies, params,
                keyword, slider_solver, sign_generator, json_data
            )

            # 提取专辑数据
            data = json_data.get('data', {})
            album_data = data.get('album', {})
            docs_data = album_data.get('docs', [])

            # 解析专辑数据为SearchAlbumResult对象列表
            album_results = []
            for doc in docs_data:
                # 解析价格类型列表
                price_types_data = doc.get('priceTypes', [])
                price_types = []
                for pt in price_types_data:
                    price_types.append(AlbumPriceType(
                        free_track_count=pt.get('free_track_count', 0),
                        price_unit=pt.get('price_unit', ''),
                        price_type_id=pt.get('price_type_id', 0),
                        price=pt.get('price', ''),
                        total_track_count=pt.get('total_track_count', 0),
                        id=pt.get('id', 0),
                        discounted_price=pt.get('discounted_price', '')
                    ))
                
                album_results.append(SearchAlbumResult(
                    playCount=doc.get('playCount', 0),
                    coverPath=doc.get('coverPath', ''),
                    title=doc.get('title', ''),
                    uid=doc.get('uid', 0),
                    url=doc.get('url', ''),
                    categoryPinyin=doc.get('categoryPinyin', ''),
                    categoryId=doc.get('categoryId', 0),
                    intro=doc.get('intro', ''),
                    albumId=doc.get('albumId', 0),
                    isPaid=doc.get('isPaid', False),
                    isFinished=doc.get('isFinished', 0),
                    categoryTitle=doc.get('categoryTitle', ''),
                    createdAt=doc.get('createdAt', 0),
                    isV=doc.get('isV', False),
                    updatedAt=doc.get('updatedAt', 0),
                    isVipFree=doc.get('isVipFree', False),
                    nickname=doc.get('nickname', ''),
                    anchorPic=doc.get('anchorPic', ''),
                    customTitle=doc.get('customTitle'),
                    verifyType=doc.get('verifyType', 0),
                    vipFreeType=doc.get('vipFreeType', 0),
                    tracksCount=doc.get('tracksCount', 0),
                    priceTypes=price_types,
                    anchorUrl=doc.get('anchorUrl', ''),
                    richTitle=doc.get('richTitle', ''),
                    vipType=doc.get('vipType', 0),
                    albumSubscript=doc.get('albumSubscript', 0),
                    displayPriceWithUnit=doc.get('displayPriceWithUnit'),
                    discountedPriceWithUnit=doc.get('discountedPriceWithUnit')
                ))

            # 构造分页信息
            pagination = SearchAlbumPagination(
                pageSize=album_data.get('pageSize', 0),
                currentPage=album_data.get('currentPage', 0),
                total=album_data.get('total', 0),
                totalPage=album_data.get('totalPage', 0)
            )

            logger.info(f"搜索成功，找到 {len(album_results)} 个专辑，总共 {pagination.total} 个")
            
            return SearchAlbumResponse(
                ret=["SUCCESS::搜索专辑成功"],
                kw=data.get('kw', keyword),
                docs=album_results,
                pagination=pagination
            )

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
async def get_album_detail(request: Request, album_id: str) -> AlbumDetailResponse:
    """
    根据专辑ID查询喜马拉雅专辑详情

    Args:
        request: FastAPI Request对象
        album_id: 专辑ID

    Returns:
        AlbumDetailResponse: 专辑详情数据

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

    # 构造专辑详情URL
    url = "https://www.ximalaya.com/revision/album/v1/simple"
    params = {
        "albumId": album_id
    }

    try:
        async with httpx.AsyncClient(verify=False, timeout=10.0) as client:
            logger.info(f"正在查询专辑详情，albumId: {album_id}")

            # 设置正确的Referer为专辑页面
            headers["Referer"] = f"https://www.ximalaya.com/album/{album_id}"

            logger.info(f"请求headers: {headers}")
            logger.info(f"请求cookies: {merged_cookies}")
            logger.info(f"请求params: {params}")

            # 发送GET请求（headers 已经由装饰器自动添加 xm-sign，Referer已覆盖）
            response = await client.get(url, headers=headers, cookies=merged_cookies, params=params)
            response.raise_for_status()

            # 解析JSON响应
            json_data = response.json()
            # logger.info(f"专辑详情响应: {json_data}")
            logger.info(f"专辑详情响应: ret={json_data.get('ret')}")

            # 检查返回码
            if json_data.get('ret') != 200:
                error_msg = json_data.get('msg', '未知错误')
                logger.error(f"查询专辑详情失败: {error_msg}")
                raise HTTPException(status_code=400, detail=f"查询专辑详情失败: {error_msg}")

            # 处理响应（包括风险验证）
            json_data = await handle_xmly_risk_verification(
                client, url, headers, merged_cookies, params,
                album_id, slider_solver, sign_generator, json_data,
                verify_url=f"https://www.ximalaya.com/album/{album_id}"
            )

            # 提取数据
            data = json_data.get('data', {})
            # logger.info(f"专辑详情数据data: {data}")

            # 解析专辑页面主要信息
            album_page_main_info = data.get('albumPageMainInfo', {})
            subscript_info_data = album_page_main_info.get('subscriptInfo', {})

            subscript_info = SubscriptInfo(
                albumSubscriptValue=subscript_info_data.get('albumSubscriptValue', -1),
                url=subscript_info_data.get('url', '')
            )

            album_page_main_info_obj = AlbumPageMainInfo(
                anchorUid=album_page_main_info.get('anchorUid', 0),
                albumStatus=album_page_main_info.get('albumStatus', 0),
                showApplyFinishBtn=album_page_main_info.get('showApplyFinishBtn', False),
                showEditBtn=album_page_main_info.get('showEditBtn', False),
                showTrackManagerBtn=album_page_main_info.get('showTrackManagerBtn', False),
                showInformBtn=album_page_main_info.get('showInformBtn', False),
                cover=album_page_main_info.get('cover', ''),
                albumTitle=album_page_main_info.get('albumTitle', ''),
                updateDate=album_page_main_info.get('updateDate', ''),
                createDate=album_page_main_info.get('createDate', ''),
                playCount=album_page_main_info.get('playCount', 0),
                isPaid=album_page_main_info.get('isPaid', False),
                isFinished=album_page_main_info.get('isFinished', 0),
                isSubscribe=album_page_main_info.get('isSubscribe', False),
                richIntro=album_page_main_info.get('richIntro', ''),
                shortIntro=album_page_main_info.get('shortIntro', ''),
                detailRichIntro=album_page_main_info.get('detailRichIntro', ''),
                isPublic=album_page_main_info.get('isPublic', True),
                hasBuy=album_page_main_info.get('hasBuy', False),
                vipType=album_page_main_info.get('vipType', 0),
                canCopyText=album_page_main_info.get('canCopyText', False),
                subscribeCount=album_page_main_info.get('subscribeCount', 0),
                sellingPoint=album_page_main_info.get('sellingPoint', {}),
                subscriptInfo=subscript_info,
                albumSubscript=album_page_main_info.get('albumSubscript', -1),
                tags=album_page_main_info.get('tags', []),
                categoryId=album_page_main_info.get('categoryId', 0),
                ximiVipFreeType=album_page_main_info.get('ximiVipFreeType', 0),
                joinXimi=album_page_main_info.get('joinXimi', False),
                freeExpiredTime=album_page_main_info.get('freeExpiredTime', 0),
                categoryTitle=album_page_main_info.get('categoryTitle', ''),
                anchorName=album_page_main_info.get('anchorName', ''),
                visibleStatus=album_page_main_info.get('visibleStatus', 0),
                personalDescription=album_page_main_info.get('personalDescription', ''),
                bigshotRecommend=album_page_main_info.get('bigshotRecommend', ''),
                outline=album_page_main_info.get('outline', ''),
                customTitle=album_page_main_info.get('customTitle'),
                produceTeam=album_page_main_info.get('produceTeam', ''),
                recommendReason=album_page_main_info.get('recommendReason', ''),
                albumSeoTitle=album_page_main_info.get('albumSeoTitle')
            )

            # 构造专辑详情数据
            album_detail_data = AlbumDetailData(
                albumId=data.get('albumId', 0),
                isSelfAlbum=data.get('isSelfAlbum', False),
                currentUid=data.get('currentUid', 0),
                albumPageMainInfo=album_page_main_info_obj,
                isTemporaryVIP=data.get('isTemporaryVIP', False)
            )

            logger.info(f"专辑详情查询成功，专辑ID: {album_detail_data.albumId}, 标题: {album_detail_data.albumPageMainInfo.albumTitle}")

            return AlbumDetailResponse(
                ret=json_data.get('ret', 200),
                msg=json_data.get('msg', '成功'),
                data=album_detail_data
            )

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
async def get_tracks_list(request: Request, album_id: str, page_num: int = 1, page_size: int = 30) -> TracksListResponse:
    """
    根据专辑ID获取曲目列表（分页）

    Args:
        request: FastAPI Request对象
        album_id: 专辑ID
        page_num: 页码，默认1
        page_size: 每页数量，默认30

    Returns:
        TracksListResponse: 曲目列表数据

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

    # 构造曲目列表URL
    url = "https://www.ximalaya.com/revision/album/v1/getTracksList"
    params = {
        "albumId": album_id,
        "pageNum": page_num,
        "pageSize": page_size
    }

    try:
        async with httpx.AsyncClient(verify=False, timeout=10.0) as client:
            logger.info(f"正在获取曲目列表，albumId: {album_id}, pageNum: {page_num}, pageSize: {page_size}")

            # 设置正确的Referer为专辑页面
            headers["Referer"] = f"https://www.ximalaya.com/album/{album_id}"

            logger.info(f"get_tracks_list---请求headers: {headers}")
            logger.info(f"get_tracks_list---请求cookies: {merged_cookies}")
            logger.info(f"get_tracks_list---请求params: {params}")

            # 发送GET请求（headers 已经由装饰器自动添加 xm-sign，Referer已覆盖）
            response = await client.get(url, headers=headers, cookies=merged_cookies, params=params)
            response.raise_for_status()

            # 解析JSON响应
            json_data = response.json()
            logger.info(f"曲目列表响应: ret={json_data.get('ret')}")

            # 处理响应（包括风险验证）
            json_data = await handle_xmly_risk_verification(
                client, url, headers, merged_cookies, params,
                album_id, slider_solver, sign_generator, json_data,
                verify_url=f"https://www.ximalaya.com/album/{album_id}"
            )


            # 提取数据
            data = json_data.get('data', {})

            # 解析曲目列表
            tracks_data = data.get('tracks', [])
            tracks_list = []
            for track in tracks_data:
                tracks_list.append(TrackInfo(
                    index=track.get('index', 0),
                    trackId=track.get('trackId', 0),
                    isPaid=track.get('isPaid', False),
                    tag=track.get('tag', 0),
                    title=track.get('title', ''),
                    playCount=track.get('playCount', 0),
                    showLikeBtn=track.get('showLikeBtn', True),
                    isLike=track.get('isLike', False),
                    showShareBtn=track.get('showShareBtn', True),
                    showCommentBtn=track.get('showCommentBtn', True),
                    showForwardBtn=track.get('showForwardBtn', True),
                    createDateFormat=track.get('createDateFormat', ''),
                    url=track.get('url', ''),
                    duration=track.get('duration', 0),
                    isVideo=track.get('isVideo', False),
                    isVipFirst=track.get('isVipFirst', False),
                    breakSecond=track.get('breakSecond', 0),
                    length=track.get('length', 0),
                    albumId=track.get('albumId', 0),
                    albumTitle=track.get('albumTitle', ''),
                    albumCoverPath=track.get('albumCoverPath', ''),
                    anchorId=track.get('anchorId', 0),
                    anchorName=track.get('anchorName', ''),
                    ximiVipFreeType=track.get('ximiVipFreeType', 0),
                    joinXimi=track.get('joinXimi', False),
                    videoCover=track.get('videoCover')
                ))

            # 构造曲目列表数据
            tracks_list_data = TracksListData(
                currentUid=data.get('currentUid', 0),
                albumId=data.get('albumId', 0),
                trackTotalCount=data.get('trackTotalCount', 0),
                sort=data.get('sort', 0),
                tracks=tracks_list,
                pageNum=data.get('pageNum', page_num),
                pageSize=data.get('pageSize', page_size),
                superior=data.get('superior', []),
                lastPlayTrackId=data.get('lastPlayTrackId')
            )

            logger.info(f"曲目列表获取成功，专辑ID: {tracks_list_data.albumId}, 总数: {tracks_list_data.trackTotalCount}, 当前页: {tracks_list_data.pageNum}")

            return TracksListResponse(
                ret=json_data.get('ret', 200),
                data=tracks_list_data
            )

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
    global_cookies={},
    global_token='',
    cookie_header_name='X-XMLY-Cookies',
    token_header_name='X-XMLY-Token',
    state_cookie_key='xmly_cookies',
    state_token_key='xmly_token'
)
async def get_subscribed_albums(request: Request, num: int = 1, size: int = 30, sub_type: int =3, category: str = 'all') -> SubscribedAlbumsResponse:
    """
    获取用户订阅的专辑列表

    Args:
        request: FastAPI Request对象
        num: 页码，默认1
        size: 每页数量，默认30
        sub_type: 订阅类型，1-最近常听，2-最新更新，3-最近订阅，默认3
        category: 分类，默认all

    Returns:
        SubscribedAlbumsResponse: 订阅专辑数据

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

    # 构造订阅专辑列表URL
    url = "https://www.ximalaya.com/revision/album/v1/sub/comprehensive"
    params = {
        "num": num,
        "size": size,
        "subType": sub_type,
        "category": category
    }

    try:
        async with httpx.AsyncClient(verify=False, timeout=10.0) as client:
            logger.info(f"正在获取订阅专辑列表，num: {num}, size: {size}, subType: {sub_type}, category: {category}")

            # 设置正确的Referer
            headers["Referer"] = "https://www.ximalaya.com/my/subscribed"

            logger.info(f"get_subscribed_albums---请求headers: {headers}")
            logger.info(f"get_subscribed_albums---请求cookies: {merged_cookies}")
            logger.info(f"get_subscribed_albums---请求params: {params}")
            # 覆盖merged_cookies中的web_login 字段，为当前时间
            # merged_cookies['web_login'] = str(int(time.time()))
            logger.info(f"get_subscribed_albums---请求cookies: {merged_cookies}")

            # 发送GET请求
            response = await client.get(url, params=params, headers=headers, cookies=merged_cookies)
            response.raise_for_status()
            logger.info(f"get_subscribed_albums---响应: {response.text}")

            json_data = response.json()

            # 处理响应（包括风险验证）
            json_data = await handle_xmly_risk_verification(
                client, url, headers, merged_cookies, params,
                '', slider_solver, sign_generator, json_data,
                verify_url=f"https://www.ximalaya.com/my/subscribed"
            )

            # 检查返回码
            ret = json_data.get('ret', 0)
            if ret != 200:
                logger.error(f"获取订阅专辑列表失败，返回码: {ret}, 消息: {json_data.get('msg', '')}")
                raise HTTPException(status_code=400, detail=json_data.get('msg', '获取订阅专辑列表失败'))

            # 提取数据
            data = json_data.get('data', {})

            # 解析专辑列表
            albums_data = data.get('albumsInfo', [])
            albums_list = []
            for album in albums_data:
                # 解析主播信息
                anchor_data = album.get('anchor', {})
                anchor = SubscribedAlbumAnchor(
                    anchorUrl=anchor_data.get('anchorUrl', ''),
                    anchorNickName=anchor_data.get('anchorNickName', ''),
                    anchorUid=anchor_data.get('anchorUid', 0),
                    anchorCoverPath=anchor_data.get('anchorCoverPath', ''),
                    logoType=anchor_data.get('logoType', 0)
                )

                # 解析专辑信息
                albums_list.append(SubscribedAlbumInfo(
                    id=album.get('id', 0),
                    title=album.get('title', ''),
                    subTitle=album.get('subTitle', ''),
                    description=album.get('description', ''),
                    coverPath=album.get('coverPath', ''),
                    isFinished=album.get('isFinished', False),
                    isPaid=album.get('isPaid', False),
                    anchor=anchor,
                    playCount=album.get('playCount', 0),
                    trackCount=album.get('trackCount', 0),
                    albumUrl=album.get('albumUrl', ''),
                    albumStatus=album.get('albumStatus', 0),
                    lastUptrackAt=album.get('lastUptrackAt', 0),
                    lastUptrackAtStr=album.get('lastUptrackAtStr', ''),
                    serialState=album.get('serialState', 0),
                    isTop=album.get('isTop', False),
                    categoryCode=album.get('categoryCode', ''),
                    categoryTitle=album.get('categoryTitle', ''),
                    lastUptrackUrl=album.get('lastUptrackUrl', ''),
                    lastUptrackTitle=album.get('lastUptrackTitle', ''),
                    vipType=album.get('vipType', 0),
                    albumSubscript=album.get('albumSubscript', 0),
                    albumScore=album.get('albumScore', '0.0')
                ))

            # 解析分类数组
            category_array_data = data.get('categoryArray', [])
            category_list = []
            for cat in category_array_data:
                category_list.append(SubscribedAlbumCategory(
                    code=cat.get('code', ''),
                    title=cat.get('title', ''),
                    count=cat.get('count', 0)
                ))

            # 构造订阅专辑数据
            subscribed_albums_data = SubscribedAlbumsData(
                albumsInfo=albums_list,
                privateSub=data.get('privateSub', False),
                pageNum=data.get('pageNum', num),
                pageSize=data.get('pageSize', size),
                totalCount=data.get('totalCount', 0),
                uid=data.get('uid', 0),
                currentUid=data.get('currentUid', 0),
                categoryCode=data.get('categoryCode', category),
                categoryArray=category_list
            )

            logger.info(f"订阅专辑列表获取成功，总数: {subscribed_albums_data.totalCount}, 当前页: {subscribed_albums_data.pageNum}")

            return SubscribedAlbumsResponse(
                ret=json_data.get('ret', 200),
                data=subscribed_albums_data
            )

    except httpx.HTTPStatusError as e:
        logger.error(f"HTTP错误: {e}")
        raise HTTPException(status_code=e.response.status_code, detail=str(e))
    except httpx.RequestError as e:
        logger.error(f"请求错误: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        logger.error(f"未知错误: {e}")
        raise HTTPException(status_code=500, detail=str(e))
