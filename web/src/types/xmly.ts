// 喜马拉雅登录步骤枚举
export enum XmlyLoginStep {
  INIT = "INIT", // 初始化
  QRCODE_GENERATED = "QRCODE_GENERATED", // 生成二维码
  QRCODE_SCANNED = "QRCODE_SCANNED", // 扫描二维码
  LOGIN_SUCCESS = "LOGIN_SUCCESS", // 登录成功
  ERROR = "ERROR", // 错误
}

// 二维码状态枚举
export enum XmlyQRCodeStatus {
  WAITING = 0, // 等待扫码（对应32000）
  SCANNED = 1, // 已扫码
  EXPIRED = 2, // 二维码已过期
}

// 喜马拉雅用户信息
export interface XmlyUserInfo {
  uid: number;
  mobileMask: string;
  token?: string;
  avatar?: string;
  loginType?: string;
}

// 生成二维码响应
export interface GenerateQrcodeResponse {
  qrId: string;
  img: string;
}

// 检查二维码状态请求
export interface CheckQrcodeStatusRequest {
  qrId: string;
}

// 检查二维码状态响应
export interface CheckQrcodeStatusResponse {
  code: number; // 32000等待扫码，0扫码成功
  msg: string;
  scanned: boolean;
  user_info?: XmlyUserInfo | null;
  token?: string;
  cookies?: Record<string, any>;
}

// 会话响应
export interface SessionResponse {
  is_logged_in: boolean;
  user_info?: XmlyUserInfo | null;
  cookies?: Record<string, any> | null;
}

// 专辑价格类型
export interface AlbumPriceType {
  free_track_count: number; // 免费音频数量
  price_unit: string; // 价格单位
  price_type_id: number; // 价格类型ID
  price: string; // 价格
  total_track_count: number; // 总音频数量
  id: number; // ID
  discounted_price: string; // 折扣价格
}

// 搜索专辑结果
export interface SearchAlbumResult {
  playCount: number; // 播放次数
  coverPath: string; // 封面路径
  title: string; // 专辑标题
  uid: number; // 用户ID
  url: string; // 专辑链接
  categoryPinyin: string; // 分类拼音
  categoryId: number; // 分类ID
  intro: string; // 专辑简介
  albumId: number; // 专辑ID
  isPaid: boolean; // 是否付费
  isFinished: number; // 0未完结，2已完结
  categoryTitle: string; // 分类标题
  createdAt: number; // 创建时间戳
  isV: boolean; // 是否加V
  updatedAt: number; // 更新时间戳
  isVipFree: boolean; // 是否VIP免费
  nickname: string; // 主播昵称
  anchorPic: string; // 主播头像
  customTitle?: string; // 自定义标题
  verifyType: number; // 认证类型
  vipFreeType: number; // VIP免费类型
  tracksCount: number; // 声音数量
  priceTypes: AlbumPriceType[]; // 价格类型列表
  anchorUrl: string; // 主播主页链接
  richTitle: string; // 富文本标题
  vipType: number; // VIP类型
  albumSubscript: number; // 专辑订阅数
  displayPriceWithUnit?: string; // 带单位的显示价格
  discountedPriceWithUnit?: string; // 带单位的折扣价格
  isSubscribed?: boolean; // 前端附加字段，用于记录订阅状态
}

// 搜索专辑分页信息
export interface SearchAlbumPagination {
  pageSize: number; // 每页数量
  currentPage: number; // 当前页码
  total: number; // 总数
  totalPage: number; // 总页数
}

// 搜索专辑响应
export interface SearchAlbumResponse {
  ret: string[]; // 返回码列表 e.g. ['SUCCESS::搜索专辑成功']
  kw?: string; // 搜索关键词
  docs: SearchAlbumResult[]; // 专辑列表
  pagination?: SearchAlbumPagination; // 分页信息
  msg?: string; // 兼容可能得错误返回消息
  code?: number; // 状态码
}

// -- 专辑详情页相关类型 --

export interface SubscriptInfo {
  albumSubscriptValue: number;
  url: string;
}

export interface AlbumPageMainInfo {
  anchorUid: number;
  albumStatus: number;
  showApplyFinishBtn: boolean;
  showEditBtn: boolean;
  showTrackManagerBtn: boolean;
  showInformBtn: boolean;
  cover: string;
  albumTitle: string;
  updateDate: string;
  createDate: string;
  playCount: number;
  isPaid: boolean;
  isFinished: number; // 0: 未完结, 2: 完结
  isSubscribe: boolean;
  richIntro: string;
  shortIntro: string;
  detailRichIntro: string;
  isPublic: boolean;
  hasBuy: boolean;
  vipType: number;
  canCopyText: boolean;
  subscribeCount: number;
  sellingPoint: any; // 具体结构待定
  subscriptInfo: SubscriptInfo;
  albumSubscript: number;
  tags: string[];
  categoryId: number;
  ximiVipFreeType: number;
  joinXimi: boolean;
  freeExpiredTime: number;
  categoryTitle: string;
  anchorName: string;
  visibleStatus: number;
}

export interface AlbumDetailData {
  albumId: number;
  isSelfAlbum: boolean;
  currentUid: number;
  albumPageMainInfo: AlbumPageMainInfo;
  isTemporaryVIP: boolean;
}

export interface AlbumDetailResponse {
  ret: number; // 200
  msg: string;
  data: AlbumDetailData;
}

// -- 曲目列表相关类型 --

export interface TrackInfo {
  index: number; // 曲目序号
  trackId: number; // 曲目ID
  isPaid: boolean; // 是否付费
  tag: number; // 标签
  title: string; // 曲目标题
  playCount: number; // 播放量
  showLikeBtn: boolean; // 是否显示点赞按钮
  isLike: boolean; // 是否已点赞
  showShareBtn: boolean; // 是否显示分享按钮
  showCommentBtn: boolean; // 是否显示评论按钮
  showForwardBtn: boolean; // 是否显示转发按钮
  createDateFormat: string; // 创建日期格式
  url: string; // 曲目URL
  duration: number; // 时长（秒）
  isVideo: boolean; // 是否视频
  isVipFirst: boolean; // 是否VIP首播
  breakSecond: number; // 播放断点
  length: number; // 音频长度
  albumId: number; // 专辑ID
  albumTitle: string; // 专辑标题
  albumCoverPath: string; // 专辑封面路径
  anchorId: number; // 主播ID
  anchorName: string; // 主播名称
  ximiVipFreeType: number; // 喜米VIP免费类型
  joinXimi: boolean; // 是否加入喜米
  videoCover?: string; // 视频封面
}

export interface TracksListData {
  currentUid: number; // 当前用户ID
  albumId: number; // 专辑ID
  trackTotalCount: number; // 曲目总数
  sort: number; // 排序方式
  tracks: TrackInfo[]; // 曲目列表
  pageNum: number; // 当前页码
  pageSize: number; // 每页数量
  superior: any[]; // 上级信息
  lastPlayTrackId?: number; // 最后播放曲目ID
}

export interface TracksListResponse {
  ret: number; // 200
  data: TracksListData;
}

// ========== 曲目下载相关类型 ==========

// 曲目播放URL信息
export interface TrackPlayUrl {
  huaweiSound: boolean; // 是否华为音效
  type: string; // 音频类型（M4A_64, MP3_64, MP3_32等）
  fileSize: number; // 文件大小
  sampleSize: number; // 采样大小
  url: string; // 播放URL
  qualityLevel: number; // 音质等级
  uploadId: string; // 上传ID
  width: number; // 宽度
  height: number; // 高度
  version: number; // 版本
}

// 曲目专辑信息
export interface TrackAlbumInfo {
  albumId: number; // 专辑ID
  title: string; // 专辑标题
  coverLarge: string; // 大封面URL
  ageLevel: number; // 年龄等级
  freeListenStatus: number; // 免费收听状态
  albumType: number; // 专辑类型
  status: number; // 状态
  offlineType: number; // 离线类型
  isPaid: boolean; // 是否付费
  isPodcastAlbum: boolean; // 是否播客专辑
  isAutoBuy: boolean; // 是否自动购买
}

// 曲目下载信息
export interface TrackDownloadInfo {
  trackId: number; // 曲目ID
  title: string; // 曲目标题
  type: number; // 类型
  categoryId: number; // 分类ID
  categoryTitle: string; // 分类标题
  headSkip: number; // 跳过头部
  tailSkip: number; // 跳过尾部
  paidType: number; // 付费类型
  processState: number; // 处理状态
  createdAt: number; // 创建时间戳
  coverSmall: string; // 小封面URL
  coverMiddle: string; // 中封面URL
  coverLarge: string; // 大封面URL
  videoCover: string; // 视频封面
  uid: number; // 用户ID
  nickname: string; // 昵称
  isLike: boolean; // 是否点赞
  isPublic: boolean; // 是否公开
  likes: number; // 点赞数
  comments: number; // 评论数
  shares: number; // 分享数
  userSource: number; // 用户来源
  status: number; // 状态
  duration: number; // 时长（秒）
  sampleDuration: number; // 采样时长
  isPaid: boolean; // 是否付费
  isFree: boolean; // 是否免费
  isAuthorized: boolean; // 是否已授权
  isVideo: boolean; // 是否视频
  isDraft: boolean; // 是否草稿
  isRichAudio: boolean; // 是否富音频
  isAntiLeech: boolean; // 是否防盗链
  vipFirstStatus: number; // VIP首播状态
  ximiFirstStatus: number; // 喜米首播状态
  playUrlList: TrackPlayUrl[]; // 播放URL列表
}

// 曲目下载响应数据
export interface TrackDownloadResponseData {
  extendInfo: Record<string, any>; // 扩展信息
  trackInfo: TrackDownloadInfo; // 曲目信息
  childAlbumInWhiteList: boolean; // 是否在白名单中
  isEnjoying: boolean; // 是否正在播放
  offlineVisibleType: number; // 离线可见类型
  hasShqAuthorized: boolean; // 是否有喜玛授权
  isXimiUhqTrack: boolean; // 是否喜玛UHQ曲目
  isXimiUhqAuthorized: boolean; // 是否喜玛UHQ授权
  playtimes: number; // 播放次数
  albumInfo: TrackAlbumInfo; // 专辑信息
  version: number; // 版本号
  hasAlbumRealFinished: boolean; // 专辑是否真实完结
}

// 曲目下载响应
export interface TrackDownloadResponse {
  ret: number; // 返回码
  msg: string; // 返回消息
  data: TrackDownloadResponseData; // 曲目下载信息数据
}

// 获取曲目标题下载信息请求
export interface GetTrackDownloadInfoRequest {
  trackId: string; // 曲目ID
}

// 批量获取曲目标题下载信息请求
export interface BatchGetTrackDownloadInfoRequest {
  trackIds: string[]; // 曲目ID列表
}

// 批量下载信息结果项
export interface BatchDownloadResultItem {
  trackId: string; // 曲目ID
  data: TrackDownloadResponseData; // 曲目数据
  error: string | null; // 错误信息
}

// 批量下载信息响应数据
export interface BatchDownloadResponseData {
  success: BatchDownloadResultItem[]; // 成功的结果
  failed: Record<string, any>[]; // 失败的结果
  total: number; // 总数
  success_count: number; // 成功数量
  failed_count: number; // 失败数量
}

// ========== 音频播放相关类型 ==========

// 音频播放URL（高/中/低品质）
export interface PlayUrls {
  high: string; // 高品质播放链接(M4A)
  medium: string; // 中品质播放链接(MP3_64)
  low: string; // 低品质播放链接(MP3_32)
}

// 音频播放链接数据
export interface TrackPlayUrlData {
  trackId: string; // 曲目ID
  title: string; // 曲目标题
  intro: string; // 简介
  coverSmall: string; // 封面URL
  duration: number; // 时长（秒）
  playUrls: PlayUrls; // 播放链接
}

// 音频播放链接响应
export interface TrackPlayUrlResponse {
  success: boolean; // 是否成功
  data: TrackPlayUrlData; // 音频播放链接数据
}

// 获取音频播放链接请求
export interface GetTrackPlayUrlRequest {
  albumId: string; // 专辑ID
  userId: string; // 用户ID
  trackId: string; // 曲目ID
}

// 当前播放的音频信息
export interface CurrentTrack {
  trackId: string;
  title: string;
  intro: string;
  coverSmall: string;
  albumTitle?: string;
  duration: number;
  playUrls: PlayUrls;
}

// ========== 订阅专辑相关类型 ==========

// 订阅专辑主播信息
export interface SubscribedAlbumAnchor {
  anchorUrl: string; // 主播URL
  anchorNickName: string; // 主播昵称
  anchorUid: number; // 主播用户ID
  anchorCoverPath: string; // 主播头像路径
  logoType: number; // logo类型
}

// 订阅专辑信息
export interface SubscribedAlbumInfo {
  id: number; // 专辑ID
  title: string; // 专辑标题
  subTitle: string; // 副标题
  description: string; // 描述
  coverPath: string; // 封面路径
  isFinished: boolean; // 是否完结
  isPaid: boolean; // 是否付费
  anchor: SubscribedAlbumAnchor; // 主播信息
  playCount: number; // 播放量
  trackCount: number; // 曲目数量
  albumUrl: string; // 专辑URL
  albumStatus: number; // 专辑状态
  lastUptrackAt: number; // 最后更新时间戳
  lastUptrackAtStr: string; // 最后更新时间字符串
  serialState: number; // 连载状态
  isTop: boolean; // 是否置顶
  categoryCode: string; // 分类编码
  categoryTitle: string; // 分类标题
  lastUptrackUrl: string; // 最后更新URL
  lastUptrackTitle: string; // 最后更新标题
  vipType: number; // VIP类型
  albumSubscript: number; // 专辑订阅数
  albumScore: string; // 专辑评分
}

// 订阅专辑分类
export interface SubscribedAlbumCategory {
  code: string; // 分类编码
  title: string; // 分类标题
  count: number; // 该分类下的专辑数量
}

// 订阅专辑数据
export interface SubscribedAlbumsData {
  albumsInfo: SubscribedAlbumInfo[]; // 专辑信息列表
  privateSub: boolean; // 是否私人订阅
  pageNum: number; // 当前页码
  pageSize: number; // 每页数量
  totalCount: number; // 总数量
  uid: number; // 用户ID
  currentUid: number; // 当前用户ID
  categoryCode: string; // 当前分类编码
  categoryArray: SubscribedAlbumCategory[]; // 分类数组
}

// 订阅专辑响应
export interface SubscribedAlbumsResponse {
  ret: number; // 返回码，200表示成功
  data: SubscribedAlbumsData; // 订阅专辑数据
}

// 获取订阅专辑请求
export interface GetSubscribedAlbumsRequest {
  num?: number; // 页码，默认1
  size?: number; // 每页数量，默认30
  subType?: number; // 订阅类型，1-最近常听，2-最新更新，3-最近订阅，默认3
  category?: string; // 分类，默认all
}
