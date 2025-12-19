from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


# 定义请求体模型
class ArticleDetailRequest(BaseModel):
    article_link: str = Field(..., description="文章链接, 必填")
    wx_public_id: str = Field(..., description="公众号ID, 必填")
    wx_public_name: str = Field(..., description="公众号名称, 必填")
    is_upload_to_aliyun: bool = Field(False, description="是否上传到阿里云, 非必填")
    is_save_to_local: bool = Field(False, description="是否保存到本地, 非必填")
    save_to_local_path: str = Field("", description="保存到本地路径, 非必填")
    save_to_local_file_name: str = Field("", description="保存到本地文件名, 非必填")

class ArticleListRequest(BaseModel):
    wx_public_id: str = Field(..., description="公众号ID, 必填")
    begin: int = Field(0, description="开始位置, 必填")
    count: int = Field(5, description="数量, 必填")
    query: str = Field("", description="搜索关键词, 非必填")

class WXCookie(BaseModel):
    slave_sid: str = Field(..., description="slave_sid, 必填")
    slave_user: str = Field(..., description="slave_user, 必填")

class CookieTokenRequest(BaseModel):
    cookie: WXCookie = Field(..., description="cookie, 必填")
    token: str = Field(..., description="token, 必填")

# 微信公众号登录相关请求体
class PreloginRequest(BaseModel):
    action: str = Field("prelogin", description="预登录动作, 默认为prelogin")

class WebreportRequest(BaseModel):
    devicetype: int = Field(1, description="设备类型, 默认为1")
    optype: int = Field(1, description="操作类型, 默认为1")
    page_state: int = Field(3, description="页面状态, 默认为3")
    log_id: int = Field(19015, description="日志ID, 默认为19015")
    sessionid: Optional[str] = Field(None, description="会话ID, 非必填")

class StartLoginRequest(BaseModel):
    userlang: str = Field("zh_CN", description="用户语言, 默认为zh_CN")
    redirect_url: str = Field("", description="重定向URL, 默认为空")
    login_type: int = Field(3, description="登录类型, 默认为3")
    sessionid: Optional[str] = Field(None, description="会话ID, 非必填")

class RedirectLoginInfoRequest(BaseModel):
    redirect_url: str = Field(..., description="重定向URL, 必填")
    
# 搜狗微信公众号详情请求体
class sogou_ArticleDetailRequest(BaseModel):
    url: str = Field(..., description="微信公众号详情链接, 必填")
    title: str = Field(..., description="公众号名称, 必填")
    is_upload_to_aliyun: bool = Field(False, description="是否上传到阿里云, 非必填")
    is_save_to_local: bool = Field(False, description="是否保存到本地, 非必填")
    save_to_local_path: str = Field("", description="保存到本地路径, 非必填")
    save_to_local_file_name: str = Field("", description="保存到本地文件名, 非必填")

class ArticleItem(BaseModel):
    aid: str
    title: str

class CheckDownloadRequest(BaseModel):
    base_path: str = Field(..., description="下载根目录")
    wx_public_name: str = Field(..., description="公众号名称")
    articles: list[ArticleItem] = Field(..., description="文章列表")