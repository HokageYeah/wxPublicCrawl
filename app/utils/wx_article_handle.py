from bs4 import BeautifulSoup
import re
import os
from datetime import datetime
from app.utils.src_path import root_path
import json
import argparse
import alibabacloud_oss_v2 as oss
from app.core.config import settings
def parse_sogou_articles(html_content):
    """解析搜狗微信搜索结果中的文章链接和标题"""
    articles = []
    
    try:
        soup = BeautifulSoup(html_content, 'html.parser')
        # print('soup-------', soup)
        # 查找每一条数据
        data_list = soup.select('div.txt-box')
        print('data_list-------', data_list)
        for data in data_list:
            # 获取链接
            title_link = data.select('h3 > a')
            # 获取链接
            href = title_link[0].get('href', '')
            # 获取标题文本
            title_text = title_link[0].get_text(strip=True)
            # 清理标题中的特殊标记
            title_text = re.sub(r'<!--red_beg-->|<!--red_end-->', '', title_text)
            # 获取内容简介
            content = data.select('p.txt-info')
            content_str = content[0].get_text(strip=True)
            content_str = re.sub(r'<!--red_beg-->|<!--red_end-->', '', content_str)
            # 获取开发者
            publisher_time_list = data.select('div.s-p')
            publisher = publisher_time_list[0].select('span.all-time-y2')
            publisher_str = publisher[0].get_text(strip=True)
            # 获取时间
            time = publisher_time_list[0].select('script')
            time_str = time[0].get_text(strip=True)
            date_time = None
            # document.write(timeConvert('1743501316'))
            # 使用正则表达式提取时间戳
            time_pattern = r"timeConvert\('(\d+)'\)"
            time_match = re.search(time_pattern, time_str)
            if time_match:
                timestamp = time_match.group(1)
                # 将时间戳转换为日期时间、在转换成字符串
                date_time = datetime.fromtimestamp(int(timestamp))
                date_time = date_time.strftime('%Y-%m-%d %H:%M:%S')
            articles.append({
                "title": title_text,
                "href": href,
                "publisher": publisher_str,
                "dateTime": date_time,
                "content": content_str
            })            
    except Exception as e:
        print(f"解析HTML时出错: {e}")
    
    return articles

# 存储html到本地 wx_public_id可以不传
# 参数说明：
# html_content: html内容
# wx_public_name: 公众号名称
# path_name: 路径名称
# wx_public_id: 公众号ID
# is_save_to_local_path: 保存到本地路径
# is_save_to_local_file_name: 保存到本地文件名
def save_html_to_local(html_content: str, wx_public_name: str, path_name: str = 'wx_public', wx_public_id: str = None, save_to_local_path: str = '', save_to_local_file_name: str = ''):
    # 使用正则表达式替换所有的 //res.wx.qq.com 为 https://res.wx.qq.com
    import re
    pattern = r'(["\']\s*)(//res\.wx\.qq\.com)'
    updated_html = re.sub(pattern, r'\1https://res.wx.qq.com', html_content)
    
    # 也替换没有引号包裹的情况
    pattern2 = r'([^"\':])(//res\.wx\.qq\.com)'
    updated_html = re.sub(pattern2, r'\1https://res.wx.qq.com', updated_html)
    
    # 提取html标题
    soup = BeautifulSoup(updated_html, 'lxml')
    # 获取 og:title 和 twitter:title 的内容
    og_title = soup.find('meta', property='og:title')
    twitter_title = soup.find('meta', property='twitter:title')
    
    # 安全地获取标题
    title = soup.title.string if soup.title else None
    if not title and og_title and 'content' in og_title.attrs:
        title = og_title['content']
    elif not title and twitter_title and 'content' in twitter_title.attrs:
        title = twitter_title['content']
    
    # 如果仍然没有标题，使用时间戳
    if not title:
        import time
        title = f"article_{int(time.time())}"
    
    # 处理标题中的非法字符（文件名不能包含的字符）
    title = re.sub(r'[\\/*?:"<>|]', "_", title)

    # 拼接保存路径
    path_str = ''
    if len(path_name) > 0 and path_name != '':
        path_str = os.path.join(root_path, 'crawlFiles', path_name)
    else:
        path_str = os.path.join(root_path, save_to_local_path)
    print("标题:", title)
    print('保存路径:', path_str)
    print('公众号ID:', wx_public_id)
    print('公众号名称:', wx_public_name)
    
    # 如果目录不存在，则创建目录
    if not os.path.exists(path_str):
        os.makedirs(path_str, exist_ok=True)
    
    # 如果传入的save_to_local_file_name存在则用save_to_local_file_name这个，不存在用wx_public_name
    # 使用lambad表达式
    wx_public_name_path = os.path.join(path_str, wx_public_name if save_to_local_file_name == '' else save_to_local_file_name)
    wx_article_path = os.path.join(wx_public_name_path, title)
    print('文章保存路径:', wx_article_path)
    
    # 如果目录不存在，则创建目录
    if not os.path.exists(wx_public_name_path):
        os.makedirs(wx_public_name_path, exist_ok=True)
    
    # 存储html到本地
    with open(f"{wx_article_path}.html", "w", encoding="utf-8") as f:
        f.write(updated_html)
    # 返回文件路径
    return f"{wx_article_path}.html"


bucket_name = settings.BUCKET_NAME
region = settings.REGION
endpoint = settings.ENDPOINT
def upload_to_aliyun(local_file_path: str):
    # 上传到阿里云
    # 直接设置访问凭证
    credentials_provider = oss.credentials.StaticCredentialsProvider(
        access_key_id=settings.ACCESS_KEY_ID,
        access_key_secret=settings.ACCESS_KEY_SECRET
    )

    # 加载SDK的默认配置，并设置凭证提供者
    cfg = oss.config.load_default()
    cfg.credentials_provider = credentials_provider
    # 设置配置中的区域信息
    cfg.region = region
    # 如果提供了endpoint参数，则设置配置中的endpoint
    cfg.endpoint = endpoint

    # 使用配置好的信息创建OSS客户端
    client = oss.Client(cfg)

    # 获取文件名
    file_name = os.path.basename(local_file_path)
    # 获取文件内容
    file_content = open(local_file_path, 'r', encoding='utf-8').read()

    # 定义要上传的数据内容
    data = file_content.encode('utf-8')  # 确保内容使用 UTF-8 编码
    key = f"wx_public/{file_name}"

    try:
        # 执行上传对象的请求，指定存储空间名称、对象名称和数据内容
        result = client.put_object(oss.PutObjectRequest(
            bucket=bucket_name,
            key=key,
            body=data,
        ))
        # 输出请求的结果状态码、请求ID、内容MD5、ETag、CRC64校验码和版本ID，用于检查请求是否成功
        print(f'status code: {result.status_code},'
                f' request id: {result.request_id},'
                f' content md5: {result.content_md5},'
                f' etag: {result.etag},'
                f' hash crc64: {result.hash_crc64},'
                f' version id: {result.version_id},'
            )
        # 返回文件路径
        oss_file_path = f'https://{bucket_name}.{endpoint}/{key}'
        # 判断是否上传成功
        if result.status_code == 200:
            # 文件路径
            print(f'file path: {oss_file_path}')
            return oss_file_path
        else:
            return None
    except Exception as e:
        print(f"Upload error: {str(e)}")
        return None



def parse_wx_common_data(html_content: str) -> dict:
    """
    从HTML内容中解析window.wx.commonData数据
    
    方法1: 使用正则表达式解析
    """
    try:
        # 查找 window.wx.commonData 的定义
        pattern = r'window\.wx\.commonData\s*=\s*({.*?});'
        match = re.search(pattern, html_content, re.DOTALL)
        
        if not match:
            raise ValueError("未找到window.wx.commonData定义")
        
        # 获取JavaScript对象字符串
        js_object_str = match.group(1)
        
        # 清理和转换JavaScript对象为JSON
        # 判断js_object_str 是什么类型
        # 提取数据
        result = extract_wx_data_fields(js_object_str)
        print("提取的数据:")
        for key, value in result.items():
            print(f"{key}: {value}")
        
        # 转换为JSON
        json_result = parse_wx_object_to_json(js_object_str)
        print("\nJSON格式:")
        print(json_result)
        print('parse_wx_common_data----json_data----', json_result)
        # 只返回data部分
        return json.loads(json_result)
            
    except Exception as e:
        print(f"解析wx.commonData失败: {e}")
        return {}

def extract_wx_data_fields(js_object_str: str) -> dict:
    """
    从JavaScript对象字符串中提取指定的字段
    """
    result = {}
    
    # 定义要提取的字段及其正则表达式模式
    patterns = {
        'nick_name': r'nick_name:\s*["\']([^"\']*)["\']',
        'user_name': r'user_name:\s*["\']([^"\']*)["\']',
        'uin_base64': r'uin_base64:\s*["\']([^"\']*)["\']',
        'uin': r'uin:\s*["\']([^"\']*)["\']',
        'ticket': r'ticket:\s*["\']([^"\']*)["\']',
        't': r't:\s*["\']([^"\']*)["\']'
    }
    
    try:
        for field, pattern in patterns.items():
            match = re.search(pattern, js_object_str)
            if match:
                value = match.group(1)
                result[field] = value
            else:
                result[field] = None
        
        return result
        
    except Exception as e:
        print(f"提取字段失败: {e}")
        return {}

def parse_wx_object_to_json(js_object_str: str) -> str:
    """
    解析JavaScript对象并返回JSON字符串
    """
    # 提取指定字段
    extracted_data = extract_wx_data_fields(js_object_str)
    
    # 转换为JSON
    return json.dumps(extracted_data, ensure_ascii=False, indent=2)
