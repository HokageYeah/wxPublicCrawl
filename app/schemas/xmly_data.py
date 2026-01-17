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
    cookies: Optional[Dict[str, str]] = Field(None, description="Cookie信息，未登录时为None")


# 喜马拉雅订阅专辑请求模型
class SubscribeAlbumRequest(BaseModel):
    """订阅专辑请求"""
    albumId: str = Field(..., description="专辑ID")


# 喜马拉雅订阅专辑响应模型
class SubscribeAlbumResponse(BaseModel):
    """订阅专辑响应"""
    ret: int = Field(..., description="返回码，200表示成功")
    msg: str = Field(..., description="返回消息")


# 专辑价格类型模型
class AlbumPriceType(BaseModel):
    """专辑价格类型"""
    free_track_count: int = Field(..., description="免费音频数量")
    price_unit: str = Field(..., description="价格单位")
    price_type_id: int = Field(..., description="价格类型ID")
    price: str = Field(..., description="价格")
    total_track_count: int = Field(..., description="总音频数量")
    id: int = Field(..., description="专辑ID")
    discounted_price: str = Field(..., description="折扣价格")


# 搜索专辑结果模型
class SearchAlbumResult(BaseModel):
    """搜索专辑结果"""
    playCount: int = Field(..., description="播放量")
    coverPath: str = Field(..., description="封面路径")
    title: str = Field(..., description="专辑标题")
    uid: int = Field(..., description="用户ID")
    url: str = Field(..., description="专辑URL")
    categoryPinyin: str = Field(..., description="分类拼音")
    categoryId: int = Field(..., description="分类ID")
    intro: str = Field(..., description="专辑简介")
    albumId: int = Field(..., description="专辑ID")
    isPaid: bool = Field(..., description="是否付费")
    isFinished: int = Field(..., description="是否完结，0未完结，2已完结")
    categoryTitle: str = Field(..., description="分类标题")
    createdAt: int = Field(..., description="创建时间戳")
    isV: bool = Field(..., description="是否V认证")
    updatedAt: int = Field(..., description="更新时间戳")
    isVipFree: bool = Field(..., description="是否VIP免费")
    nickname: str = Field(..., description="主播昵称")
    anchorPic: str = Field(..., description="主播头像")
    customTitle: Optional[str] = Field(None, description="自定义标题")
    verifyType: int = Field(..., description="认证类型")
    vipFreeType: int = Field(..., description="VIP免费类型")
    tracksCount: int = Field(..., description="音频数量")
    priceTypes: list[AlbumPriceType] = Field(default_factory=list, description="价格类型列表")
    anchorUrl: str = Field(..., description="主播URL")
    richTitle: str = Field(..., description="富文本标题")
    vipType: int = Field(..., description="VIP类型")
    albumSubscript: int = Field(..., description="专辑订阅数")
    displayPriceWithUnit: Optional[str] = Field(None, description="带单位的价格显示")
    discountedPriceWithUnit: Optional[str] = Field(None, description="带单位的折扣价格显示")


# 搜索专辑分页信息模型
class SearchAlbumPagination(BaseModel):
    """搜索专辑分页信息"""
    pageSize: int = Field(..., description="每页数量")
    currentPage: int = Field(..., description="当前页码")
    total: int = Field(..., description="总数量")
    totalPage: int = Field(..., description="总页数")


# 搜索专辑响应模型
class SearchAlbumResponse(BaseModel):
    """搜索专辑响应"""
    ret: list[str] = Field(..., description="返回码列表，如 ['SUCCESS::搜索专辑成功'] 或 ['ERROR::搜索失败']")
    kw: Optional[str] = Field(None, description="搜索关键词")
    docs: list[SearchAlbumResult] = Field(default_factory=list, description="专辑列表")
    pagination: Optional[SearchAlbumPagination] = Field(None, description="分页信息")


# 搜索专辑请求模型
class SearchAlbumRequest(BaseModel):
    """搜索专辑请求"""
    kw: str = Field(..., description="搜索关键词")


# 订阅信息模型
class SubscriptInfo(BaseModel):
    """订阅信息"""
    albumSubscriptValue: int = Field(..., description="专辑订阅值")
    url: str = Field(..., description="URL")


# 专辑页面主要信息模型
class AlbumPageMainInfo(BaseModel):
    """专辑页面主要信息"""
    anchorUid: int = Field(..., description="主播用户ID")
    albumStatus: int = Field(..., description="专辑状态")
    showApplyFinishBtn: bool = Field(..., description="是否显示申请完结按钮")
    showEditBtn: bool = Field(..., description="是否显示编辑按钮")
    showTrackManagerBtn: bool = Field(..., description="是否显示音频管理按钮")
    showInformBtn: bool = Field(..., description="是否显示举报按钮")
    cover: str = Field(..., description="专辑封面URL")
    albumTitle: str = Field(..., description="专辑标题")
    updateDate: str = Field(..., description="更新日期")
    createDate: str = Field(..., description="创建日期")
    playCount: int = Field(..., description="播放量")
    isPaid: bool = Field(..., description="是否付费")
    isFinished: int = Field(..., description="是否完结，0未完结，1已完结")
    isSubscribe: bool = Field(..., description="是否已订阅")
    richIntro: str = Field(..., description="富文本简介")
    shortIntro: str = Field(..., description="简短简介")
    detailRichIntro: str = Field(..., description="详细富文本简介")
    isPublic: bool = Field(..., description="是否公开")
    hasBuy: bool = Field(..., description="是否已购买")
    vipType: int = Field(..., description="VIP类型")
    canCopyText: bool = Field(..., description="是否可复制文本")
    subscribeCount: int = Field(..., description="订阅数")
    sellingPoint: Dict[str, Any] = Field(default_factory=dict, description="卖点信息")
    subscriptInfo: SubscriptInfo = Field(..., description="订阅信息")
    albumSubscript: int = Field(..., description="专辑订阅状态")
    tags: list[str] = Field(default_factory=list, description="标签列表")
    categoryId: int = Field(..., description="分类ID")
    ximiVipFreeType: int = Field(..., description="喜米VIP免费类型")
    joinXimi: bool = Field(..., description="是否加入喜米")
    freeExpiredTime: int = Field(..., description="免费过期时间")
    categoryTitle: str = Field(..., description="分类标题")
    anchorName: str = Field(..., description="主播昵称")
    visibleStatus: int = Field(..., description="可见状态")
    personalDescription: str = Field(default="", description="个人描述")
    bigshotRecommend: str = Field(default="", description="大咖推荐")
    outline: str = Field(default="", description="大纲")
    customTitle: Optional[str] = Field(None, description="自定义标题")
    produceTeam: str = Field(default="", description="制作团队")
    recommendReason: str = Field(default="", description="推荐理由")
    albumSeoTitle: Optional[str] = Field(None, description="专辑SEO标题")


# 专辑详情数据模型
class AlbumDetailData(BaseModel):
    """专辑详情数据"""
    albumId: int = Field(..., description="专辑ID")
    isSelfAlbum: bool = Field(..., description="是否自己的专辑")
    currentUid: int = Field(..., description="当前用户ID")
    albumPageMainInfo: AlbumPageMainInfo = Field(..., description="专辑主要信息")
    isTemporaryVIP: bool = Field(..., description="是否临时VIP")


# 专辑详情响应模型
class AlbumDetailResponse(BaseModel):
    """专辑详情响应"""
    ret: int = Field(..., description="返回码，200表示成功")
    msg: str = Field(..., description="返回消息")
    data: AlbumDetailData = Field(..., description="专辑详情数据")


# 获取专辑详情请求模型
class GetAlbumDetailRequest(BaseModel):
    """获取专辑详情请求"""
    albumId: str = Field(..., description="专辑ID")
