from fastapi import APIRouter, Query
from app.schemas.common_data import ApiResponseData
from app.services.sogou_wx_public import fetch_sogou_wx_public_list, fetch_wx_public_detail
from app.schemas.wx_data import sogou_ArticleDetailRequest
import httpx
from app.utils.wx_article_handle import save_html_to_local
router = APIRouter()

# 搜索微信公众号信息列表
@router.get("/search-wx-public-list",response_model=ApiResponseData)
async def search_wx_articles(query: str = Query(..., description="搜索关键词"), page: int = Query(1, description="页码")):
    """搜索微信公众号信息列表"""
    result = await fetch_sogou_wx_public_list(query, page)
    return result

# 获取微信公众号详情
@router.post("/get-wx-public-detail",response_model=ApiResponseData)
async def post_wx_public_detail(params: sogou_ArticleDetailRequest):
    """获取微信公众号详情"""
    result = await fetch_wx_public_detail(params)
    return result

# 测试接口获取微信公众号详情
@router.get("/get-wx-public-detail-test", response_model=ApiResponseData)
async def post_wx_public_detail_test():
    """获取微信公众号详情"""
    # 更完整的请求头，模拟真实浏览器
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
        "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
        "Accept-Encoding": "gzip, deflate, br",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1",
        "Cache-Control": "max-age=0",
        "Referer": "https://weixin.sogou.com/weixin?type=2&query=cocos"
    }
    
    # 创建一个会话，保持 cookie 
    # follow_redirects=True 自动重定向
    async with httpx.AsyncClient(verify=False, follow_redirects=True) as client:
        # 先访问搜索页面获取 cookie
        await client.get("https://weixin.sogou.com/weixin?type=2&query=cocos", headers=headers)
        
        # 然后访问目标链接
        url = "https://weixin.sogou.com/link?url=dn9a_-gY295K0Rci_xozVXfdMkSQTLW6cwJThYulHEtVjXrGTiVgSzu7xHzaV7sGNbAmGL4m6kWX4BndQj73zVqXa8Fplpd9Nn5E4Qek59ga-_kH19z3COTNyl7C6oJwhrz6roEomB0PZcVAvhOOv1A7fNGnLxfJHEMEYPYWPVK1cycoT33zwetqdAsyqxn53usUvtM3PqOiJ3FkNqubMnYseisAksLPKfzxKHkYDz7RBTvOs_yFDYWAzmL2Y6fHermL26hhqGZFH6In5Ei3zg..&type=2&query=cocos&token=5D25D8F0453F20842F291A8E52C9A08F2F543E7E682D8392"
        response = await client.get(url, headers=headers)
        html_content = response.text
        # 如果返回的是重定向页面，尝试提取真实 URL 并访问
        if "setTimeout(function ()" in html_content and "window.location.replace" in html_content:
            import re
            # 提取重定向 URL
            url_parts = re.findall(r"url \+= '([^']+)'", html_content)
            if url_parts:
                real_url = "".join(url_parts).replace(" ", "")
                # 访问真实 URL
                final_response = await client.get(real_url, headers=headers)
                # print('final_response', final_response.text)
                save_html_to_local(final_response.text, 'test', 'sogou_wx_public')
                return final_response.text
        
        # return html_content
