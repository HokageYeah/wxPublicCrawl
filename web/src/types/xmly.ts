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
}

// 会话响应
export interface SessionResponse {
  is_logged_in: boolean;
  user_info?: XmlyUserInfo | null;
}
