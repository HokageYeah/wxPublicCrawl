import licenseRequest from "@/utils/licenseRequest";

/**
 * 卡密绑定服务 API
 * 用于用户注册、登录、卡密绑定等功能
 */

// 类型定义
export interface RegisterParams {
  username: string;
  password: string;
  email?: string;
  phone?: string;
}

export interface LoginParams {
  username: string;
  password: string;
  app_key: string;
}

export interface AppSimpleInfo {
  app_key: string;
  app_name: string;
}

export interface AppSimpleListResponse {
  total: number;
  apps: AppSimpleInfo[];
}

export interface BindLicenseParams {
  licenseKey: string;
  userId?: string;
}

export interface UserInfo {
  id: string;
  username: string;
  email?: string;
  phone?: string;
  licenseStatus?: string;
  licenseExpireTime?: string;
  createdAt?: string;
}

export interface LoginResponse {
  token: string;
  userInfo: UserInfo;
}

/**
 * 用户注册
 */
export const register = (params: RegisterParams) => {
  return licenseRequest.post<LoginResponse>("/api/v1/auth/register", params);
};

/**
 * 用户登录
 */
export const login = (params: LoginParams) => {
  return licenseRequest.post<LoginResponse>("/api/v1/auth/login", params);
};

/**
 * 用户登出
 */
export const logout = () => {
  return licenseRequest.post("/api/v1/auth/logout");
};

/**
 * 获取公开应用列表
 */
export const getPublicAppList = () => {
  return licenseRequest.get<AppSimpleListResponse>("/api/v1/app/public/list");
};

/**
 * 获取用户信息
 */
export const getUserInfo = () => {
  return licenseRequest.get<UserInfo>("/api/v1/user/info");
};

/**
 * 绑定卡密
 */
export const bindLicense = (params: BindLicenseParams) => {
  return licenseRequest.post("/api/v1/license/bind", params);
};

/**
 * 验证卡密
 */
export const validateLicense = (licenseKey: string) => {
  return licenseRequest.get(`/api/v1/license/validate/${licenseKey}`);
};

/**
 * 获取卡密信息
 */
export const getLicenseInfo = () => {
  return licenseRequest.get("/api/v1/license/info");
};

/**
 * 刷新 Token
 */
export const refreshToken = () => {
  return licenseRequest.post<{ token: string }>("/api/v1/auth/refresh");
};
