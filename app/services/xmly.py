import httpx
import time
import base64
from typing import Dict, Any, Optional
from fastapi import HTTPException, Request
from loguru import logger

from app.schemas.xmly_data import (
    XmlyQrcodeResponse,
    XmlyQrcodeStatusResponse,
    XmlyUserInfo,
    XmlyLoginStatusResponse
)
from app.services.system import system_manager
from app.decorators.request_decorator import extract_wx_credentials


# 喜马拉雅API基础URL
XMLY_BASE_URL = "https://passport.ximalaya.com"

# 公共请求头
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "application/json, text/plain, */*",
    "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
    "Referer": "https://www.ximalaya.com/",
    "Origin": "https://www.ximalaya.com",
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
                user_info=None
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
            user_info=user_info
        )

    except Exception as e:
        logger.error(f"获取喜马拉雅登录状态失败: {e}")
        return XmlyLoginStatusResponse(
            is_logged_in=False,
            user_info=None
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

            return json_data

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

            return json_data

    except httpx.HTTPStatusError as e:
        logger.error(f"HTTP错误: {e}")
        raise HTTPException(status_code=e.response.status_code, detail=f"HTTP错误: {e}")
    except httpx.RequestError as e:
        logger.error(f"请求错误: {e}")
        raise HTTPException(status_code=500, detail=f"请求错误: {e}")
    except Exception as e:
        logger.error(f"未知错误: {e}")
        raise HTTPException(status_code=500, detail=f"未知错误: {e}")


