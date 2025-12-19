from fastapi import APIRouter
import subprocess
import platform
import os
from app.services.system import fetch_select_folder
from app.schemas.common_data import ApiResponseData

# 9. 检查文章是否已下载
from app.schemas.wx_data import CheckDownloadRequest
import re
from app.utils.src_path import root_path
router = APIRouter()

@router.get("/select-folder", response_model=ApiResponseData)
async def select_folder():
    result = fetch_select_folder()
    return result


@router.post("/check-downloaded", response_model=ApiResponseData)
async def check_downloaded_status(params: CheckDownloadRequest):
    """检查文章是否已下载"""
    # 构造保存路径
    # 逻辑与 save_html_to_local 保持一致
    # 1. 确定根路径
    if not params.base_path:
        return [] # 没有路径则默认未下载
        
    path_str = params.base_path
    # 如果是相对路径 (不常见，但为了兼容性)
    if not os.path.isabs(path_str):
        path_str = os.path.join(root_path, path_str)
        
    # 2. 确定公众号路径
    wx_public_path = os.path.join(path_str, params.wx_public_name)
    
    downloaded_aids = []
    
    if os.path.exists(wx_public_path):
        for article in params.articles:
            # 3. 处理标题 (与 save_html_to_local 一致)
            title = article.title
            
            # 模拟 save_html_to_local 中的标题处理逻辑
            # 注意：这里我们假设 save_html_to_local 使用的是从HTML解析的标题或者 fallback 的 title
            # 通常 article.title 与 HTML title 是一致的，但如果有特殊字符处理需要一致
            # save_html_to_local 中: title = re.sub(r'[\\/*?:"<>|]', "_", title)
            cleaned_title = re.sub(r'[\\/*?:"<>|]', "_", title)
            
            file_path = os.path.join(wx_public_path, f"{cleaned_title}.html")
            
            if os.path.exists(file_path):
                downloaded_aids.append(article.aid)
                
    return downloaded_aids