
import httpx
from fastapi import HTTPException
from app.utils.wx_article_handle import parse_sogou_articles, save_html_to_local
from app.schemas.wx_data import sogou_ArticleDetailRequest

async def fetch_sogou_wx_public_list(query: str, page: int = 1):
    """搜索微信公众号信息列表"""
    url = f"https://weixin.sogou.com/weixin?type=2&query={query}&page={page}"
    try:    
        async with httpx.AsyncClient(verify=False) as client:
            response = await client.get(url)
            html_content = response.text
            # 解析HTML内容并为href加前缀
            articles = [{**item, 'href': 'https://weixin.sogou.com' + item['href']} for item in parse_sogou_articles(html_content)]
            return articles
    except httpx.HTTPStatusError as e:
        raise HTTPException(status_code=e.response.status_code, detail=f"HTTP错误: {e}")
    except httpx.RequestError as e:
        raise HTTPException(status_code=500, detail=f"请求错误: {e}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"未知错误: {e}")
    

async def fetch_wx_public_detail(params: sogou_ArticleDetailRequest):
    """获取微信公众号详情"""
    try:
        # 创建一个会话，保持 cookie 
        # follow_redirects=True 自动重定向
        async with httpx.AsyncClient(verify=False, follow_redirects=True) as client:
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
                "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
                "Accept-Encoding": "gzip, deflate, br",
                "Connection": "keep-alive",
                "Upgrade-Insecure-Requests": "1",
                "Cache-Control": "max-age=0",
                "Referer": "https://weixin.sogou.com/weixin?type=2&query="
            }
            print('params.url----', params.url)
            # 先访问搜索页面获取 cookie
            await client.get("https://weixin.sogou.com/weixin?type=2&query=", headers=headers)
            # 然后访问目标链接
            response = await client.get(params.url, headers=headers)
            html_content = response.text

            is_upload_to_aliyun = params.is_upload_to_aliyun
            is_save_to_local = params.is_save_to_local
            save_to_local_path = params.save_to_local_path
            save_to_local_file_name = params.save_to_local_file_name
            print('html_content----', html_content)
             # 如果返回的是重定向页面，尝试提取真实 URL 并访问
            if "setTimeout(function ()" in html_content and "window.location.replace" in html_content:
                import re
                # 提取重定向 URL
                url_parts = re.findall(r"url \+= '([^']+)'", html_content)
                if url_parts and is_save_to_local:
                    real_url = "".join(url_parts).replace(" ", "")
                    # 访问真实 URL
                    final_response = await client.get(real_url, headers=headers)
                    kwargs = {
                        "wx_public_name": params.title,
                        "wx_public_id": '',
                        "path_name": 'sogou_wx_public',
                        "save_to_local_path": save_to_local_path,
                        "save_to_local_file_name": save_to_local_file_name
                    }
                    local_file_path = save_html_to_local(final_response.text, **kwargs)
                    # 暂无阿里云上传
                    # if local_file_path != "" and is_upload_to_aliyun:
                    #     oss_file_path = upload_to_aliyun(local_file_path)
                    return {
                        "local_file_path": local_file_path,
                        "path": f'已保存到本地：crawFile/sogou_wx_public/{params.title}.html'
                    }
    except httpx.HTTPStatusError as e:
        raise HTTPException(status_code=e.response.status_code, detail=f"HTTP错误: {e}")
    except httpx.RequestError as e:
        raise HTTPException(status_code=500, detail=f"请求错误: {e}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"未知错误: {e}")

        

