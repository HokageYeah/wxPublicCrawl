from fastapi import APIRouter, Query
import subprocess
import platform
import os
from typing import Optional
from app.services.system import system_manager
from app.models.user_behavior import BehaviorType
from app.schemas.common_data import ApiResponseData

# 9. 检查文章是否已下载
from app.schemas.wx_data import CheckDownloadRequest
import re
from app.utils.src_path import root_path
router = APIRouter()

@router.get("/select-folder", response_model=ApiResponseData)
async def select_folder():
    result = system_manager.fetch_select_folder()
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


@router.post("/session/save", response_model=ApiResponseData)
async def save_session(data: dict):
    """保存用户会话 (包括cookies和token)"""
    platform = data.get('platform', 'wx')
    user_info = data.get('user_info', {})
    cookies = data.get('cookies', {})
    token = data.get('token', '')
    app_info = data.get('app_info', {})
    success = system_manager.save_platform_session(platform, user_info, cookies, token, app_info, expires_days=7)
    if success:
        return {"success": True, "message": "会话保存成功"}
    else:
        return {"success": False, "message": "会话保存失败"}


@router.get("/session/load", response_model=ApiResponseData)
async def load_session(platform: str = Query('wx', description="平台标识")):
    """加载用户会话"""
    user_info = system_manager.load_platform_session(platform)
    if user_info:
        return {
            "success": True,
            "logged_in": True,
            **user_info
        }
    else:
        return {
            "success": True,
            "logged_in": False,
            "user_info": None
        }


@router.post("/session/clear", response_model=ApiResponseData)
async def clear_session(data: dict = None):
    """清除用户会话"""
    platform = 'wx'
    if data:
        platform = data.get('platform', 'wx')
    success = system_manager.clear_platform_session(platform)
    return {"success": success}

# ------------------------------------------------------------
# 标签管理 API
# ------------------------------------------------------------

@router.get("/tags", response_model=ApiResponseData)
async def get_tags():
    """获取所有搜索标签"""
    tags = system_manager.get_tags()
    return tags

@router.post("/tags/init", response_model=ApiResponseData)
async def init_tags():
    """初始化默认标签（如果为空）"""
    system_manager.init_default_tags()
    return system_manager.get_tags()

@router.post("/tags", response_model=ApiResponseData)
async def add_tag(data: dict):
    """添加标签"""
    name = data.get("name")
    if not name:
        return {"success": False, "message": "标签名称不能为空"}
    return system_manager.add_tag(name)

@router.delete("/tags", response_model=ApiResponseData)
async def delete_tag(tag_id: int = Query(None, description="标签ID"), name: str = Query(None, description="标签名称")):
    """删除标签 (通过ID或名称)"""
    # 使用 query params: DELETE /system/tags?tag_id=1 或 DELETE /system/tags?name=郑州

    if tag_id:
        return system_manager.delete_tag(tag_id)
    elif name:
        return system_manager.delete_tag_by_name(name)
    else:
        return {"success": False, "message": "必须提供 tag_id 或 name"}


# ------------------------------------------------------------
# 用户行为管理 API
# ------------------------------------------------------------

@router.get("/user-behavior", response_model=ApiResponseData)
async def get_user_behavior(
    user_id: str = Query(..., description="用户ID（uin 或 nick_name）"),
    behavior_type: str = Query(..., description="行为类型")
):
    """获取用户行为值"""
    value = system_manager.get_user_behavior(user_id, behavior_type)
    if value is not None:
        return {"success": True, "value": value}
    else:
        return {"success": False, "message": "用户行为不存在"}


@router.post("/user-behavior", response_model=ApiResponseData)
async def set_user_behavior(data: dict):
    """设置用户行为（自动更新或创建）"""
    user_id = data.get("user_id")
    behavior_type = data.get("behavior_type")
    behavior_value = data.get("behavior_value")

    if not user_id or not behavior_type or not behavior_value:
        return {"success": False, "message": "参数不完整"}

    return system_manager.set_user_behavior(user_id, behavior_type, behavior_value)


@router.delete("/user-behavior", response_model=ApiResponseData)
async def delete_user_behavior(
    user_id: str = Query(..., description="用户ID（uin 或 nick_name）"),
    behavior_type: str = Query(..., description="行为类型")
):
    """删除用户行为"""
    success = system_manager.delete_user_behavior(user_id, behavior_type)
    if success:
        return {"success": True, "message": "删除成功"}
    else:
        return {"success": False, "message": "删除失败或记录不存在"}


@router.get("/user-behaviors", response_model=ApiResponseData)
async def get_all_user_behaviors(
    user_id: str = Query(..., description="用户ID（uin 或 nick_name）")
):
    """获取用户的所有行为记录"""
    behaviors = system_manager.get_all_user_behaviors(user_id)
    return {"success": True, "data": behaviors}


# ------------------------------------------------------------
# 便捷方法：常用用户行为 API
# ------------------------------------------------------------

@router.get("/download-path", response_model=ApiResponseData)
async def get_download_path(
    user_id: str = Query(..., description="用户ID（uin 或 nick_name）"),
    # 不传默认 BehaviorType.SAVE_DOWNLOAD_PATH
    behavior_type: str = Query(default=BehaviorType.SAVE_DOWNLOAD_PATH, description="行为类型，不传默认 BehaviorType.SAVE_DOWNLOAD_PATH")
):
    """获取下载路径（便捷方法）"""
    path = system_manager.get_download_path(user_id, behavior_type)
    if path is not None:
        return {"success": True, "path": path}
    else:
        return {"success": False, "message": "下载路径未设置", "path": ""}


@router.post("/download-path", response_model=ApiResponseData)
async def set_download_path(data: dict):
    """设置下载路径（便捷方法）"""
    user_id = data.get("user_id")
    download_path = data.get("download_path")
    # 不传默认 BehaviorType.SAVE_DOWNLOAD_PATH
    behavior_type = data.get("behavior_type", BehaviorType.SAVE_DOWNLOAD_PATH)
    if not user_id or not download_path:
        return {"success": False, "message": "参数不完整"}

    return system_manager.set_download_path(user_id, download_path, behavior_type)


@router.get("/save-to-local", response_model=ApiResponseData)
async def get_save_to_local(
    user_id: str = Query(..., description="用户ID（uin 或 nick_name）")
):
    """获取是否保存到本地（便捷方法）"""
    value = system_manager.get_save_to_local(user_id)
    if value is not None:
        return {"success": True, "value": value}
    else:
        return {"success": False, "message": "设置未初始化", "value": ""}


@router.post("/save-to-local", response_model=ApiResponseData)
async def set_save_to_local(data: dict):
    """设置是否保存到本地（便捷方法）"""
    user_id = data.get("user_id")
    save_to_local = data.get("save_to_local")

    if not user_id or not save_to_local:
        return {"success": False, "message": "参数不完整"}

    return system_manager.set_save_to_local(user_id, save_to_local)


@router.get("/upload-to-aliyun", response_model=ApiResponseData)
async def get_upload_to_aliyun(
    user_id: str = Query(..., description="用户ID（uin 或 nick_name）")
):
    """获取是否上传到阿里云（便捷方法）"""
    value = system_manager.get_upload_to_aliyun(user_id)
    if value is not None:
        return {"success": True, "value": value}
    else:
        return {"success": False, "message": "设置未初始化", "value": ""}


@router.post("/upload-to-aliyun", response_model=ApiResponseData)
async def set_upload_to_aliyun(data: dict):
    """设置是否上传到阿里云（便捷方法）"""
    user_id = data.get("user_id")
    upload_to_aliyun = data.get("upload_to_aliyun")

    if not user_id or not upload_to_aliyun:
        return {"success": False, "message": "参数不完整"}

    return system_manager.set_upload_to_aliyun(user_id, upload_to_aliyun)
