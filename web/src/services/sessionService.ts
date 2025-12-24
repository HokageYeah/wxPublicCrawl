import api from '@/utils/request';
export interface UserInfo {
    // 根据你的实际用户信息结构定义
    [key: string]: any;
  }
  
export interface SessionResponse {
  success: boolean;
  logged_in: boolean;
  user_info: UserInfo | null;
  cookies?: Record<string, any>; // 微信请求必带参数
  token?: string; // 微信请求必带参数
}

export const sessionService = {
  saveSession: async (user_info: UserInfo, cookies?: Record<string, any>, token?: string): Promise<boolean> => {
      const data = await api.post('/system/session/save', { user_info, cookies: cookies || {}, token: token || '' });
      return data.success;
  },
  loadSession: async (): Promise<SessionResponse> => {
      const data = await api.get('/system/session/load');
      return data;
  },
  clearSession: async (): Promise<boolean> => {
      const data = await api.post('/system/session/clear');
      return data.success;
  }
}