import httpx
import urllib.parse
import time
import math
import random
from typing import Dict, Any
from fastapi import HTTPException, Request
import logging
from loguru import logger
from app.schemas.wx_data import ArticleDetailRequest, ArticleListRequest, CookieTokenRequest, PreloginRequest, WebreportRequest, StartLoginRequest
import json
from app.utils.wx_article_handle import save_html_to_local, parse_wx_common_data, upload_to_aliyun
from bs4 import BeautifulSoup
from app.utils.src_path import get_temp_file_path
from app.decorators.request_decorator import extract_wx_credentials
# from PIL import Image
cookies = {
    # "appmsglist_action_3964406050": "card",
    # "RK": "ja198JWedK",
    # "ptcz": "7ebea765d075dffa6ef04c81508c0ef29c004910a7de50ef4633e50b9dd7434f",
    # "uin": "o2410292164",
    # "rewardsn": "",
    # "ua_id": "19NhLcjPInWpmsVLAAAAAIM_YaNha4ekik8fWssHpDM=",
    # "_clck": "10obs8|1|fw1|0",
    # "wxuin": "47635853929480",
    "mm_lang": "zh_CN",
    # "uuid": "6f292948090057fcd00f7d9674b27b46",
    # "rand_info": "CAESIHiKJrBtZF3Nj0pH/eWbld4llPH7qXV2f30yVSzzeen8",
    # "slave_bizuin": "3964406050",
    # "data_bizuin": "3964406050",
    # "bizuin": "3964406050",
    # "data_ticket": "b1gFFOVFXWJSOPFv0x0kdWNGqnLvTLJDdroZ3mTQuqaINx+2qd30rDuheprNxukk",
    "slave_sid": "WDlkVDhLOFllMDh4SEt4ZjMwUVlRcTg3VnQzd01ERTVjZWw4Q1pvSklsejMyZGlxYVNzME5aUFk4UHM0UWJFZG9URG5GeUdOMllqMGxGSmJBY3BMOUZuS1Z4Tjdzb3Y4UjEyYW45ZTNDOWljamZQMnFlZloxdWNFbFkwUzNCNWhWUGRjRm5qcDFvWGVKRU9y",
    "slave_user": "gh_82bb5e0f80e3",
    # "xid": "2bf279896be76b2a04adde420df9a89f",
    # "_clsk": "9ll88u|1747636404886|6|1|mp.weixin.qq.com/weheat-agent/payload/record"
}
token = "159333899"

# 错误处理
def handle_error(base_resp):
    ret = base_resp.get('ret',0)
    err_msg = base_resp.get('err_msg','')
    if ret != 0:
        raise HTTPException(status_code=400, detail=f"HTTP错误: {err_msg}")
    return base_resp

@extract_wx_credentials(cookies, token)
async def fetch_wx_public(request: Request, query: str, begin: int, count: int):
    """获取微信公众号"""
    # 从 request.state 中获取装饰器处理后的 cookies 和 token
    merged_cookies = request.state.wx_cookies
    final_token = request.state.wx_token
    
    print('🔍 [DEBUG] 查询参数 query:', query)
    
    url = f"https://mp.weixin.qq.com/cgi-bin/searchbiz?action=search_biz&begin={begin}&count={count}&query={query}&token={final_token}&lang=zh_CN&f=json&ajax=1"

    try:
        async with httpx.AsyncClient(verify=False) as client:
            logging.info(f"正在请求URL: {url}")
            logger.info(f"正在请求cookies: {merged_cookies}，token: {final_token}")
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
            }
            # 使用合并后的 cookies
            response = await client.get(url, headers=headers, timeout=10, cookies=merged_cookies)
            response.raise_for_status()
            # 整理成json
            json_data = json.loads(response.text)
            base_resp = json_data.get('base_resp', {})
            handle_error(base_resp)
            return json_data.get('list', [])
    except httpx.HTTPStatusError as e:
        raise HTTPException(status_code=e.response.status_code, detail=f"HTTP错误: {e}")
    except httpx.RequestError as e:
        raise HTTPException(status_code=500, detail=f"请求错误: {e}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"未知错误: {e}")

@extract_wx_credentials(cookies, token)
async def fetch_wx_article_list(request: Request, params: ArticleListRequest):
    """使用Query参数获取微信公众号文章详情"""
    # 从 request.state 中获取装饰器处理后的 cookies 和 token
    merged_cookies = request.state.wx_cookies
    final_token = request.state.wx_token
    if len(params.query) <= 0:
        url = f"https://mp.weixin.qq.com/cgi-bin/appmsgpublish?sub=list&begin={params.begin}&count={params.count}&fakeid={params.wx_public_id}&type=101_1&free_publish_type=1&sub_action=list_ex&token={final_token}&lang=zh_CN&f=json&ajax=1"
    else:
        url = f"https://mp.weixin.qq.com/cgi-bin/appmsgpublish?sub=search&search_field=7&begin={params.begin}&count={params.count}&query={params.query}&fakeid={params.wx_public_id}&type=101_1&free_publish_type=1&sub_action=list_ex&token={final_token}&lang=zh_CN&f=json&ajax=1"
    print('url', url)
    try:
        async with httpx.AsyncClient(verify=False) as client:
            response = await client.get(url,timeout=10,cookies=merged_cookies)
            response.raise_for_status()
            json_data = json.loads(response.text)
            base_resp = json_data.get('base_resp',{})
            handle_error(base_resp)
            publish_page = json_data.get('publish_page',"")
            publish_page_obj = json.loads(publish_page,)
            publish_page_obj['publish_list'] = [json.loads(item["publish_info"]) for item in publish_page_obj['publish_list']]
            return publish_page_obj
    except httpx.HTTPStatusError as e:
        raise HTTPException(status_code=e.response.status_code, detail=f"HTTP错误: {e}")


@extract_wx_credentials(cookies, token)
async def fetch_wx_article_detail_by_link(request: Request, request_data: ArticleDetailRequest):
    """根据文章链接请求得到文章详情（需要传递公众号id以及公众号名称，做网站本地化保存使用）"""
    # 从 request.state 中获取装饰器处理后的 cookies 和 token
    merged_cookies = request.state.wx_cookies
    final_token = request.state.wx_token
    article_link = request_data.article_link
    wx_public_id = request_data.wx_public_id
    wx_public_name = request_data.wx_public_name
    is_upload_to_aliyun = request_data.is_upload_to_aliyun # 是否上传到阿里云
    is_save_to_local = request_data.is_save_to_local # 是否保存到本地
    save_to_local_path = request_data.save_to_local_path # 保存到本地路径
    save_to_local_file_name = request_data.save_to_local_file_name # 保存到本地文件名
    
    try:
        # 主动抛出异常，设置返回相应体
        # raise HTTPException(status_code=400, detail="测试异常")
        # 抛出一个业务异常
        async with httpx.AsyncClient(verify=False) as client:
            logging.info(f"正在请求文章详情URL: {article_link}")
            
            headers = {
                "Referer": article_link,
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
            }
            response = await client.get(article_link, headers=headers, cookies=merged_cookies)
            response.raise_for_status()
            # 返回一个html
            html_content = response.text
            oss_file_path = ""
            local_file_path = ""
            if is_save_to_local:
                # 存储html到本地
                kwargs = {
                    "wx_public_name": wx_public_name,
                    "wx_public_id": wx_public_id,
                    "path_name": 'wx_public' if save_to_local_path == '' else '',
                    "save_to_local_path": save_to_local_path,
                    "save_to_local_file_name": save_to_local_file_name
                }
                local_file_path = save_html_to_local(html_content, **kwargs)
            if local_file_path != "" and is_upload_to_aliyun:
                oss_file_path = upload_to_aliyun(local_file_path)
            return {
                "local_file_path": local_file_path,
                "oss_file_path": oss_file_path
            }
    except httpx.HTTPStatusError as e:
        raise HTTPException(status_code=e.response.status_code, detail=f"HTTP错误: {e}")
    except httpx.RequestError as e:
        raise HTTPException(status_code=500, detail=f"请求错误: {e}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"未知错误: {e}")
    
async def fetch_set_wx_cookie_token(params: CookieTokenRequest):
    """设置cookie、token"""
    # 设置全局变量
    global cookies, token
    # 判断cookies的类型
    if isinstance(params.cookie, str):
        # 将cookie转换为字典
        cookies = json.loads(params.cookie)
    else:
        cookies = params.cookie.__dict__
    token = params.token
    print('cookies---token', cookies, token)
    return {"message": "cookie、token设置成功"}


# ------------------------------------------------------------
# 微信公众号登录流程
# ------------------------------------------------------------


# 公共请求头
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "Content-Type": "application/x-www-form-urlencoded",
    "Referer": "https://mp.weixin.qq.com/",
}
cookies = {}
newsessionid = ""
token = ""


def restore_cookies_and_token(session_cookies: Dict[str, Any], session_token: str = ""):
    """从会话数据中恢复全局cookies和token
    
    Args:
        session_cookies: 会话中保存的cookies
        session_token: 会话中保存的token (可选)
    """
    global cookies, token
    if session_cookies:
        cookies = session_cookies
        print(f"✓ 已恢复 cookies: {len(cookies)} 个")
    if session_token:
        token = session_token
        print(f"✓ 已恢复 token")


# 微信公众号登录流程 - 第一步：预登录获取忽略密码列表
async def fetch_prelogin(request_data: PreloginRequest):
    """微信公众号登录流程 - 第一步：预登录获取忽略密码列表
    
    POST /cgi-bin/bizlogin
    Host: https://mp.weixin.qq.com
    action=prelogin
    """
    url = "https://mp.weixin.qq.com/cgi-bin/bizlogin"
    
    data = {
        "action": request_data.action
    }
    
    
    try:
        async with httpx.AsyncClient(verify=False) as client:
            logging.info(f"正在请求预登录URL: {url}")
            response = await client.post(url, data=data, headers=headers, timeout=10)
            print('第一步：预登录获取忽略密码列表---response', response.text)
            print('第一步：预登录获取忽略密码列表---cookie', response.cookies)
            response.raise_for_status()
            
            # 解析响应
            json_data = json.loads(response.text)
            base_resp = json_data.get('base_resp', {})
            handle_error(base_resp)
            
            # 返回预登录结果
            return json_data
    except httpx.HTTPStatusError as e:
        raise HTTPException(status_code=e.response.status_code, detail=f"HTTP错误: {e}")
    except httpx.RequestError as e:
        raise HTTPException(status_code=500, detail=f"请求错误: {e}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"未知错误: {e}")
    
# 微信公众号登录流程 - 第二步：开始登录
async def fetch_startlogin(request_data: StartLoginRequest):
    """微信公众号登录流程 - 第二步：开始登录
    
    POST /cgi-bin/bizlogin?action=startlogin
    Host: https://mp.weixin.qq.com
    
    userlang=zh_CN
    redirect_url=
    login_type=3
    sessionid=sessionid
    """
    url = "https://mp.weixin.qq.com/cgi-bin/bizlogin?action=startlogin"
    global newsessionid
    newsessionid = await generate_session_id()
    data = {
        "userlang": request_data.userlang,
        "redirect_url": request_data.redirect_url,
        "login_type": request_data.login_type,
        "sessionid": request_data.sessionid or newsessionid
    }
    
    try:
        async with httpx.AsyncClient(verify=False) as client:
            logging.info(f"正在请求获取二维码URL: {url}")
            response = await client.post(url, data=data, headers=headers, timeout=10)
            print('第二步：获取二维码---response', response.text)
            print('第二步：获取二维码---cookie---data', response.cookies, data)
            global cookies
            cookies = {cookie[0]: cookie[1] for cookie in response.cookies.items()}
            # 构建cookie字符串
            cookie_str = '; '.join([f"{k}={v}" for k, v in cookies.items()])
            print('第二步：获取二维码---cookie_str', cookie_str)
            print('第二步：获取二维码---cookies', cookies)
            response.raise_for_status()
            
            # 解析响应
            json_data = json.loads(response.text)
            base_resp = json_data.get('base_resp', {})
            handle_error(base_resp)
            
            # 返回二维码信息
            return {
                **json_data,
                'cookie_str': cookie_str,
                'cookies': cookies
            }
    except httpx.HTTPStatusError as e:
        raise HTTPException(status_code=e.response.status_code, detail=f"HTTP错误: {e}")
    except httpx.RequestError as e:
        raise HTTPException(status_code=500, detail=f"请求错误: {e}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"未知错误: {e}")

# 微信公众号登录流程 - 第三步：上报信息
async def fetch_webreport(request_data: WebreportRequest):
    """微信公众号登录流程 - 第三步：上报信息
    
    POST /cgi-bin/webreport
    Host: https://mp.weixin.qq.com
    reportJson={"devicetype":1,"newsessionid":"172059629456827","optype":1,"page_state":3,"log_id":19015}
    """
    url = "https://mp.weixin.qq.com/cgi-bin/webreport"
    
    # 构建reportJson
    report_json = {
        "devicetype": request_data.devicetype,
        "newsessionid": request_data.sessionid or newsessionid,
        "optype": request_data.optype,
        "page_state": request_data.page_state,
        "log_id": request_data.log_id
    }
    print('report_json', report_json)
    
    data = {
        "reportJson": json.dumps(report_json)
    }
    
    try:
        async with httpx.AsyncClient(verify=False) as client:
            logging.info(f"正在请求上报URL: {url}")
            response = await client.post(url, data=data, headers=headers, timeout=10)
            # print('response--------', response.json())
            print('第三步：上报信息---response', response.text)
            print('第三步：上报信息---cookie', response.cookies)
            print('第三步：上报信息---data', data)
            response.raise_for_status()
            
            # 返回上报结果
            return {**response.json(), "newsessionid": report_json["newsessionid"]}
    except httpx.HTTPStatusError as e:
        raise HTTPException(status_code=e.response.status_code, detail=f"HTTP错误: {e}")
    except httpx.RequestError as e:
        raise HTTPException(status_code=500, detail=f"请求错误: {e}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"未知错误: {e}")

# 微信公众号登录流程 - 第四步：获取微信登录二维码
async def fetch_get_wx_login_qrcode(request: Request):
    """获取微信登录二维码
    
    返回二维码图像的二进制数据
    """
    random_num = int(time.time() * 1000)    # 当前时间戳（毫秒）
    url = f"https://mp.weixin.qq.com/cgi-bin/scanloginqrcode?action=getqrcode&random={random_num}"
    
    # 获取请求头中的cookie
    cookies_str = request.headers.get('Cookie', '')
    if not cookies_str:
        # 如果没有cookie，使用默认cookie
        cookies = {}
        logger.warning("No cookies found in request headers, using default empty cookies")
    else:
        # 解析cookie
        try:
            cookies = {cookie.split('=')[0].strip(): cookie.split('=')[1].strip() 
                    for cookie in cookies_str.split(';') if '=' in cookie}
        except Exception as e:
            logger.error(f"Error parsing cookies: {e}")
            cookies = {}
    
    logger.info(f"第四步：获取微信登录二维码---cookies: {cookies}")
    
    try:
        async with httpx.AsyncClient(verify=False) as client:
            response = await client.get(url, timeout=10, cookies=cookies)
            
            # 检查响应状态
            if response.status_code != 200:
                logger.error(f"获取二维码失败，状态码: {response.status_code}")
                raise HTTPException(status_code=response.status_code, 
                                  detail=f"获取二维码失败: {response.text}")
            
            # 记录二维码大小
            logger.info(f"二维码大小: {len(response.content)} bytes")
            
            # 保存二维码到本地文件用于调试
            # 获取临时文件路径
            # 在 .app 包模式下：
            # 当前工作目录 (CWD) 被设置为 .app 包内部
            # 这个目录是只读的（macOS 安全机制）
            # 所以无法写入文件
            qrcode_file_path = get_temp_file_path('qrcode.png')
            with open(qrcode_file_path, 'wb') as f:
                f.write(response.content)
            print('二维码保存路径:', qrcode_file_path)
                
            # 直接返回二进制内容
            return response.content
    except Exception as e:
        logger.error(f"获取二维码时发生错误: {e}")
        raise HTTPException(status_code=500, detail=f"获取二维码失败: {str(e)}")


# 微信公众号登录流程 - 第五步：获取二维码状态
async def fetch_get_qrcode_status(request: Request):
    """获取二维码状态"""
    url = "https://mp.weixin.qq.com/cgi-bin/scanloginqrcode?action=ask&fingerprint=9b1ea719e1ba482a27d45364d3c7f877&token=&lang=zh_CN&f=json"
    async with httpx.AsyncClient(verify=False) as client:
        cookies =  request.headers.get('Cookie')
        # 转换成对象
        cookies = {cookie.split('=')[0]: cookie.split('=')[1] for cookie in cookies.split(';')}
        response = await client.get(url, timeout=10, cookies=cookies)
        print('第五步：获取二维码状态---cookies-----', cookies)
        print('第五步：获取二维码状态---response', response.text)
        response.raise_for_status()
        json_data = json.loads(response.text)
        base_resp = json_data.get('base_resp', {})
        handle_error(base_resp)
        return json_data

# 微信公众号登录流程 - 第六步：获取登录信息
async def fetch_get_login_info(request: Request):
    """获取登录信息"""
    url = "https://mp.weixin.qq.com/cgi-bin/bizlogin?action=login"
    global newsessionid
    data = {
        "userlang": "zh_CN",
        "redirect_url": "",
        "cookie_forbidden": 0,
        "cookie_cleaned": 0,
        "plugin_used": 0,
        "login_type": 3,
        "fingerprint": "",
        "token": "",
    }
    async with httpx.AsyncClient(verify=False) as client:
        request_cookies =  request.headers.get('Cookie')
        # 转换成对象
        request_cookies = {cookie.split('=')[0]: cookie.split('=')[1] for cookie in request_cookies.split(';')}
        response = await client.post(url, data=data, timeout=10, headers=headers, cookies=request_cookies)
        print('第六步：获取登录信息---response', response.text)
        print('第六步：获取登录信息---cookie', request_cookies)
        print('第六步：获取登录信息---data', data)
        response.raise_for_status()

        response_cookies = {cookie[0]: cookie[1] for cookie in response.cookies.items()}
        # 构建cookie字符串
        cookie_str = '; '.join([f"{k}={v}" for k, v in response_cookies.items()])
        print('第六步：获取登录信息---response-cookie_str', cookie_str)
        print('第六步：获取登录信息---response-cookies', response_cookies)
        response.raise_for_status()
        
        # 解析响应
        json_data = json.loads(response.text)
        base_resp = json_data.get('base_resp', {})
        handle_error(base_resp)
        redirect_url = json_data.get('redirect_url', '')
        # /cgi-bin/home?t=home/index&lang=zh_CN&token=21304194"
        # 获取token
        global token, cookies
        token = redirect_url.split('token=')[1]
        cookies = response_cookies
        print('第六步：获取登录信息---global token', token)
        print('第六步：获取登录信息---global cookies', cookies)
        return {
            **json_data,
            'cookie_str': cookie_str,
            'token': token
        }
# 微信公众号登录流程 - 第七步：验证用户信息
async def fetch_verify_user_info(request: Request, rq_token: str):
    """验证用户信息"""
    global token
    if not rq_token:
        rq_token = token
    print('第七步：验证用户信息---rq_token', rq_token)
    url = f"https://mp.weixin.qq.com/cgi-bin/home?action=get_finder_live_info&fingerprint=77d0c4a6149482d13b8a9b1dea06ad99&token={rq_token}&lang=zh_CN&f=json&ajax=1"
    async with httpx.AsyncClient(verify=False) as client:
        request_cookies =  request.headers.get('Cookie')
        # 转换成对象
        request_cookies = {cookie.split('=')[0]: cookie.split('=')[1] for cookie in request_cookies.split(';')}
        response = await client.get(url, timeout=10, cookies=request_cookies)
        print('第七步：验证用户信息---response', response.text)
        print('第七步：验证用户信息---cookie', request_cookies)
        response.raise_for_status()
        return response.text
    
# 微信公众号登录流程 - 第八步：根据重定向获取微信公众号个人登录信息
async def fetch_redirect_login_info(request: Request, redirect_url: str):
    """根据重定向获取微信公众号个人登录信息"""
        # 请求重定向地址根据重定向地址获取微信公众号个人登录信息
    url = f"https://mp.weixin.qq.com{redirect_url}"
    async with httpx.AsyncClient(verify=False) as client:
        request_cookies =  request.headers.get('Cookie')
        # 转换成对象
        request_cookies = {cookie.split('=')[0]: cookie.split('=')[1] for cookie in request_cookies.split(';')}
        response = await client.get(url, timeout=10, cookies=request_cookies, headers=headers)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'lxml')
        # 解析HTML获取wx.commonData
        wx_data = parse_wx_common_data(response.text)
        # 解析出
        print('第七步：根据重定向获取微信公众号个人登录信息---重定向地址--wx_data', wx_data)
        return {
            "userInfo": wx_data,
            "cookies": request_cookies,
            "token": token
        }
    

async def generate_session_id():
    """生成会话ID
    
    JavaScript逻辑: this.sessionid = new Date().getTime() + "" + Math.floor(Math.random() * 100);
    """
    timestamp = int(time.time() * 1000)  # 获取当前时间戳（毫秒）
    random_num = math.floor(random.random() * 100)  # 生成0-99的随机数
    session_id = f"{timestamp}{random_num}"  # 拼接成会话ID
    print('session_id----------', session_id)
    return session_id


async def export_articles_to_excel(articles: list, save_path: str, file_name: str):
    """
    将文章列表导出到Excel文件
    
    参数:
        articles: 文章列表，包含aid, title, publish_time, update_time, link
        save_path: 保存路径
        file_name: 文件名（不含扩展名）
        
    返回:
        dict: 包含保存路径和文件名的结果
    """
    import pandas as pd
    import os
    from pathlib import Path
    
    try:
        logger.info(f"开始导出文章到Excel，共 {len(articles)} 篇文章")
        
        # 将Pydantic模型转换为字典（如果传入的是模型对象）
        article_dicts = []
        for article in articles:
            # 如果是Pydantic模型，转换为字典
            if hasattr(article, 'model_dump'):
                article_dict = article.model_dump()
            elif hasattr(article, 'dict'):
                article_dict = article.dict()
            else:
                article_dict = article
            article_dicts.append(article_dict)
        
        # 创建DataFrame，按照指定顺序：aid, title, publish_time, update_time, link
        df_data = []
        for article in article_dicts:
            df_data.append({
                "文章ID": article.get("aid", "") if isinstance(article, dict) else getattr(article, "aid", ""),
                "文章标题": article.get("title", "") if isinstance(article, dict) else getattr(article, "title", ""),
                "发布时间": article.get("publish_time", "") if isinstance(article, dict) else getattr(article, "publish_time", ""),
                "更新时间": article.get("update_time", "") if isinstance(article, dict) else getattr(article, "update_time", ""),
                "文章链接": article.get("link", "") if isinstance(article, dict) else getattr(article, "link", "")
            })
        
        df = pd.DataFrame(df_data)
        
        # 确保保存路径存在
        save_dir = Path(save_path)
        save_dir.mkdir(parents=True, exist_ok=True)
        
        # 构建完整文件路径
        full_path = save_dir / f"{file_name}.xlsx"
        
        # 导出到Excel
        df.to_excel(full_path, index=False, engine='openpyxl')
        
        logger.info(f"文章导出成功: {full_path}")
        
        return {
            "success": True,
            "file_path": str(full_path),
            "article_count": len(articles)
        }
        
    except ImportError as e:
        logger.error(f"缺少必要的库: {e}")
        raise HTTPException(status_code=500, detail=f"缺少必要的库，请安装 pandas 和 openpyxl: pip install pandas openpyxl")
    except Exception as e:
        logger.error(f"导出Excel失败: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"导出Excel失败: {str(e)}")