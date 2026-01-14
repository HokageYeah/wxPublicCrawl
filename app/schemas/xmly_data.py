from datetime import datetime
from typing import Optional, Dict, Any

from pydantic import BaseModel, Field


# 喜马拉雅二维码生成响应模型
class XmlyQrcodeResponse(BaseModel):
    """喜马拉雅生成二维码接口响应"""
    ret: int = Field(..., description="返回码，0表示成功")
    msg: str = Field(..., description="返回消息")
    qrId: str = Field(..., description="二维码ID，用于后续状态查询")
    img: str = Field(..., description="base64编码的二维码图片")


# 喜马拉雅二维码状态查询响应模型
class XmlyQrcodeStatusResponse(BaseModel):
    """喜马拉雅二维码状态查询接口响应"""
    ret: int = Field(..., description="返回码，32000表示未扫码，0表示扫码成功")
    msg: str = Field(..., description="返回消息")
    bizKey: Optional[str] = Field(None, description="业务键")
    uid: Optional[int] = Field(None, description="用户ID")
    token: Optional[str] = Field(None, description="用户令牌")
    userType: Optional[str] = Field(None, description="用户类型")
    isFirst: Optional[bool] = Field(None, description="是否首次登录")
    toSetPwd: Optional[bool] = Field(None, description="是否需要设置密码")
    loginType: Optional[str] = Field(None, description="登录类型")
    mobileMask: Optional[str] = Field(None, description="手机号掩码，如188****0615")
    mobileCipher: Optional[str] = Field(None, description="手机号加密串")
    captchaInfo: Optional[str] = Field(None, description="验证码信息")
    avatar: Optional[str] = Field(None, description="头像URL")
    thirdpartyAvatar: Optional[str] = Field(None, description="第三方头像")
    thirdpartyNickname: Optional[str] = Field(None, description="第三方昵称")
    smsKey: Optional[str] = Field(None, description="短信键")
    thirdpartyId: Optional[str] = Field(None, description="第三方ID")
    authCode: Optional[str] = Field(None, description="授权码")

# 检查二维码状态传递参数qrId
class CheckQrcodeStatusRequest(BaseModel):
    qrId: str = Field(..., description="二维码ID")

# 喜马拉雅用户信息模型
class XmlyUserInfo(BaseModel):
    """喜马拉雅用户信息"""
    uid: int = Field(..., description="用户ID")
    mobileMask: str = Field(..., description="手机号掩码")
    token: Optional[str] = Field(None, description="用户令牌")
    avatar: Optional[str] = Field(None, description="头像URL")
    loginType: Optional[str] = Field(None, description="登录类型")


# 喜马拉雅会话数据模型
class XmlySessionData(BaseModel):
    """喜马拉雅会话数据"""
    user_info: XmlyUserInfo = Field(..., description="用户信息")
    cookies: Dict[str, str] = Field(..., description="Cookie信息")
    created_at: str = Field(..., description="创建时间")
    expires_at: str = Field(..., description="过期时间")


# 喜马拉雅登录状态响应模型
class XmlyLoginStatusResponse(BaseModel):
    """喜马拉雅登录状态响应"""
    is_logged_in: bool = Field(..., description="是否已登录")
    user_info: Optional[XmlyUserInfo] = Field(None, description="用户信息，未登录时为None")
