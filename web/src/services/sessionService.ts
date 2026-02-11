import api from "@/utils/request";
export interface UserInfo {
  // 根据你的实际用户信息结构定义
  [key: string]: any;
}

export interface AppInfo {
  app_name: string;
  app_id: string;
  app_key: string;
  app_status: string;
  app_created_at: string;
}

export interface SessionResponse {
  success: boolean;
  logged_in: boolean;
  user_info: UserInfo | null;
  app_info: AppInfo | null;
  cookies?: Record<string, any>; // 微信请求必带参数
  token?: string; // 微信请求必带参数
}

export const sessionService = {
  saveSession: async (
    user_info: UserInfo,
    cookies?: Record<string, any>,
    token?: string,
    platform: string = "wx",
    app_info?: AppInfo,
  ): Promise<boolean> => {
    const data = await api.post("/system/session/save", {
      user_info,
      cookies: cookies || {},
      token: token || "",
      platform,
      app_info,
    });
    return data.success;
  },
  loadSession: async (platform: string = "wx"): Promise<SessionResponse> => {
    const data = await api.get("/system/session/load", {
      params: { platform },
    });
    return data;
  },
  clearSession: async (platform: string = "wx"): Promise<boolean> => {
    const data = await api.post("/system/session/clear", { platform });
    return data.success;
  },
};
