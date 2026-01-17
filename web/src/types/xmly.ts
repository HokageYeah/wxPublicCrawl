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
