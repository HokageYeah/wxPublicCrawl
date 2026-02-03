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
  device_id?: string;
}

export interface AppSimpleInfo {
  app_name: string;
  app_id: string;
  app_key: string;
  app_status: string;
  app_created_at: string;
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
  // 用户角色
  role?: 'admin' | 'user';
  // 卡密信息
  has_card?: boolean;
  cards?: CardInfo[];
}

export interface CardInfo {
  card_id: number;
  card_key: string;
  expire_time: string;
  permissions: string[];
  bind_devices: number;
  max_device_count: number;
  status: string;
  remark?: string;
  app_name: string;
  app_id: string;
  app_key: string;
  app_status: string;
  app_created_at: string;
}

export interface MyCardsResponse {
  has_card: boolean;
  cards: CardInfo[];
}

export interface LoginResponse {
  token: string;
  userInfo: UserInfo;
  app_info: AppSimpleInfo;
}

/**
 * 用户注册
 */
export const register = (params: RegisterParams) => {
  return licenseRequest.post<LoginResponse>("/auth/register", params);
};

/**
 * 用户登录
 */
export const login = (params: LoginParams) => {
  return licenseRequest.post<LoginResponse>("/auth/login", params);
};

/**
 * 用户登出
 */
export const logout = () => {
  return licenseRequest.post("/auth/logout");
};

/**
 * 获取公开应用列表
 */
export const getPublicAppList = () => {
  return licenseRequest.get<AppSimpleListResponse>("/app/public/list");
};

/**
 * 获取用户信息
 */
export const getUserInfo = () => {
  return licenseRequest.get<UserInfo>("/user/info");
};

/**
 * 绑定卡密
 */
export const bindLicense = (params: BindLicenseParams) => {
  return licenseRequest.post("/license/bind", params);
};

/**
 * 验证卡密
 */
export const validateLicense = (licenseKey: string) => {
  return licenseRequest.get(`/license/validate/${licenseKey}`);
};

/**
 * 获取卡密信息
 */
export const getLicenseInfo = () => {
  return licenseRequest.get("/license/info");
};

/**
 * 刷新 Token
 */
export const refreshToken = () => {
  return licenseRequest.post<{ token: string }>("/auth/refresh");
};

/**
 * 查询我的卡密
 */
export const getMyCards = () => {
  return licenseRequest.get<MyCardsResponse>("/card/my");
};
