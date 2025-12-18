// Common API response format
export interface ApiResponseData<T = any> {
  platform: string;
  api: string;
  data: T;
  ret: string[];
  v: number;
}

// Session ID response
export interface SessionIdResponse {
  session_id: string;
}

// Prelogin request/response
export interface PreloginRequest {
  action?: string;
}

export interface PreloginResponse {
  base_resp: {
    ret: number;
    err_msg: string;
  };
  needCaptcha: boolean;
}

// Startlogin request/response
export interface StartLoginRequest {
  userlang: string;
  redirect_url: string;
  login_type: number;
  sessionid: string;
}

export interface StartLoginResponse {
  redirect_url: string;
  cookie_str: string;
}

// Webreport request/response
export interface WebreportRequest {
  devicetype: number;
  optype: number;
  page_state: number;
  log_id: number;
}

// QR Code status response
export interface QRCodeStatusResponse {
  status: number;
  user_category: number;
  wx_code: string;
}

// Login info response
export interface LoginInfoResponse {
  redirect_url: string;
  token: string;
  cookie_str: string;
}

// User info response
export interface UserInfoResponse {
  user_info: {
    user_name: string;
    avatar: string;
    nickname: string;
  };
  authorized: boolean;
}

// Login state machine
export enum LoginStep {
  INIT = 'init', // 初始化  
  PRELOGIN = 'prelogin', // 预登录
  STARTLOGIN = 'startlogin', // 开始登录
  WEBREPORT = 'webreport', // 网页报告
  QRCODE_GENERATED = 'qrcode_generated', // 二维码生成
  QRCODE_SCANNED = 'qrcode_scanned', // 二维码扫描
  QRCODE_CONFIRMED = 'qrcode_confirmed', // 已确认
  LOGIN_SUCCESS = 'login_success', // 登录成功
  VERIFY_SUCCESS = 'verify_success', // 验证成功
  REDIRECT_SUCCESS = 'redirect_success', // 重定向成功
  ERROR = 'error' // 错误
}

// QR Code status enum
export enum QRCodeStatus {
  WAITING = 0,     // Waiting for scan 中文：等待扫描
  CONFIRMED = 1,   // Confirmed 中文：已确认
  EXPIRED = 3,     // Expired 中文：已过期
  SCANNED = 4,     // Scanned but not confirmed 中文：已扫描
} 