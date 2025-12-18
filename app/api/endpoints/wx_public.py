from fastapi import APIRouter, Depends, HTTPException, Query, Body, Response, Request
from sqlalchemy.orm import Session
from loguru import logger

from app.services.wx_public import (
    fetch_wx_public, 
    fetch_wx_article_list, 
    fetch_wx_article_detail_by_link,
    fetch_set_wx_cookie_token,
    fetch_prelogin,
    fetch_webreport,
    fetch_startlogin,
    generate_session_id,
    fetch_get_qrcode_status,
    fetch_get_wx_login_qrcode,
    fetch_get_login_info,
    fetch_redirect_login_info,
    fetch_verify_user_info,
)
from app.schemas.wx_data import ArticleDetailRequest, ArticleListRequest, CookieTokenRequest, PreloginRequest, WebreportRequest, StartLoginRequest, RedirectLoginInfoRequest
from app.schemas.common_data import ApiResponseData
from app.decorators.cache_decorator import ttl_cache, timed_cache, get_cache


router = APIRouter()


@router.get("/search-wx-public",response_model=ApiResponseData)
async def search_wx_articles(query: str = Query(..., description="搜索关键词"),
                             begin: int = Query(0, description="开始位置"),
                             count: int = Query(5, description="数量")):
    """搜索微信公众号"""
    result = await fetch_wx_public(query, begin, count)
    return result

# 根据公众号id搜索公众号文章列表
@router.post("/get-wx-article-list", response_model=ApiResponseData)
async def get_wx_article_list(params: ArticleListRequest):
    """使用公众号ID搜索公众号文章列表（使用Query参数）"""
    result = await fetch_wx_article_list(params)
    return result

# 根据文章链接请求得到文章详情（需要传递公众号id以及公众号名称，做网站本地化保存使用）
@router.post("/get-wx-article-detail-by-link", response_model=ApiResponseData)
async def get_wx_article_detail_by_link(params: ArticleDetailRequest):
    """根据文章链接请求得到文章详情（需要传递公众号id以及公众号名称，做网站本地化保存使用）
    
    此端点用于测试body参数的异常处理
    
    请求体示例:
    ```json
    {
        "article_link": "文章链接",
        "wx_public_id": "公众号ID",
        "wx_public_name": "公众号名称"
    }
    ```
    """
    result = await fetch_wx_article_detail_by_link(params)
    return result

# 设置cookie、token接口
@router.post("/set-wx-cookie-token", response_model=ApiResponseData)
async def set_wx_cookie_token(params: CookieTokenRequest):
    """设置cookie、token"""
    result = await fetch_set_wx_cookie_token(params)
    return result


# 微信二维码登录流程

# 1、预登录接口
@router.post("/login/prelogin", response_model=ApiResponseData)
async def prelogin(params: PreloginRequest = Body(default=None)):
    """微信公众号登录流程 - 第一步：预登录获取忽略密码列表
    
    POST /cgi-bin/bizlogin
    Host: https://mp.weixin.qq.com
    action=prelogin
    """
    if params is None:
        params = PreloginRequest()
    result = await fetch_prelogin(params)
    return result

# 2、登录流程已开始
@router.post("/login/startlogin", response_model=ApiResponseData)
async def startlogin(params: StartLoginRequest, response: Response):
    """微信公众号登录流程 - 第二步：获取二维码
    
    POST /cgi-bin/bizlogin?action=startlogin
    Host: https://mp.weixin.qq.com
    
    userlang=zh_CN
    redirect_url=
    login_type=3
    sessionid=sessionid
    """
    result = await fetch_startlogin(params)
    # 设置响应头中的Cookie
    if result.get('cookie_str'):
        response.headers['Set-Cookie'] = result['cookie_str']
    return {
        **result,
        'headers': {**response.headers}
    }

# 3、设备报告接口
@router.post("/login/webreport", response_model=ApiResponseData)
async def webreport(params: WebreportRequest):
    """微信公众号登录流程 - 第三步：上报设备信息
    
    POST /cgi-bin/webreport
    Host: https://mp.weixin.qq.com
    reportJson={"devicetype":1,"newsessionid":"172059629456827","optype":1,"page_state":3,"log_id":19015}
    """
    result = await fetch_webreport(params)
    return result

# 4、获取微信登录二维码
@router.get("/login/get-wx-login-qrcode")
async def get_wx_login_qrcode(request: Request, response: Response):
    """获取微信登录二维码
    
    返回二维码图像数据，并设置正确的Content-Type
    """
    try:
        result = await fetch_get_wx_login_qrcode(request)
        
        # 设置正确的Content-Type
        response.headers["Content-Type"] = "image/png"
        
        # 直接返回二进制数据
        return Response(content=result, media_type="image/png")
    except Exception as e:
        logger.error(f"获取二维码失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# 5、获取二维码状态
@router.post("/login/get-qrcode-status", response_model=ApiResponseData)
async def get_qrcode_status(request: Request):
    """获取二维码状态"""
    result = await fetch_get_qrcode_status(request)
    return result

# 6、登录成功获取登录信息
@router.post("/login/get-login-info", response_model=ApiResponseData)
async def get_login_info(request: Request, response: Response):
    """登录成功获取登录信息"""
    result = await fetch_get_login_info(request)
        # 设置响应头中的Cookie
    if result.get('cookie_str'):
        response.headers['Set-Cookie'] = result['cookie_str']
    print('登录成功获取登录信息---response.headers', response.headers)
    return {
        **result,
        'headers': {**response.headers}
    }
# 7、得到用户信息前验证
@router.post("/login/verify-user-info", response_model=ApiResponseData)
async def verify_user_info(request: Request, rq_token: str = Query(..., description="token")):
    """得到用户信息前验证"""
    result = await fetch_verify_user_info(request, rq_token)
    return result

# 8、根据重定向获取微信公众号个人登录信息
@router.post("/login/redirect-login-info", response_model=ApiResponseData)
async def redirect_login_info(request: Request, params: RedirectLoginInfoRequest):
    """根据重定向获取微信公众号个人登录信息"""
    result = await fetch_redirect_login_info(request, params.redirect_url)
    return result

# 生成会话ID辅助接口
@router.get("/login/generate-session-id", response_model=ApiResponseData)
async def get_session_id():
    """生成会话ID
    
    生成逻辑：new Date().getTime() + "" + Math.floor(Math.random() * 100)
    """
    session_id = await generate_session_id()
    return {"session_id": session_id}

