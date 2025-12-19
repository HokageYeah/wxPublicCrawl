// import axios from 'axios';
import api from '@/utils/request';
import type { 
  SessionIdResponse,
  PreloginRequest,
  PreloginResponse,
  StartLoginRequest,
  StartLoginResponse,
  WebreportRequest,
  QRCodeStatusResponse,
  LoginInfoResponse,
  UserInfoResponse
} from '@/types/wechat';

// Create axios instance with base URL
// In dev: /web-api proxy handles it
// In prod: direct to /api/v1
// const baseURL = import.meta.env.DEV ? '/web-api/api/v1/wx/public' : '/api/v1/wx/public';
// console.log('mport.meta.env.DEV---', import.meta.env.DEV)
// const api = axios.create({
//   baseURL,
//   withCredentials: true, // Important for cookies
// });

// API endpoints
export const wechatService = {
  /**
   * Generate a session ID for the login flow
   */
  generateSessionId: async (): Promise<string> => {
    const data = await api.get<SessionIdResponse>('/login/generate-session-id');
    return data?.session_id || '';
  },

  /**
   * Step 1: Prelogin - Get ignore password list
   */
  prelogin: async (params: PreloginRequest = {}): Promise<PreloginResponse> => {
    const data = await api.post<PreloginResponse>('/login/prelogin', params);
    return data;
  },

  /**
   * Step 2: Start login - Get QR code
   */
  startLogin: async (params: StartLoginRequest): Promise<StartLoginResponse> => {
    console.log('startLogin params', params);
    const data = await api.post<StartLoginResponse>('/login/startlogin', params);
    return data;
  },

  /**
   * Step 3: Web report - Report device info
   */
  webReport: async (params: WebreportRequest): Promise<any> => {
    console.log('webReport params', params);
    const data = await api.post<any>('/login/webreport', params);
    return data;
  },

  /**
   * Step 4: Get WeChat login QR code
   * 处理接口返回的图片数据，转换为可显示的URL
   */
  getLoginQRCode: async (): Promise<string> => {
    try {
      // 使用 getBlob 方法获取二进制数据（自动设置 responseType: 'blob'）
      const blob = await api.getBlob('/login/get-wx-login-qrcode');
      
      console.log('二维码获取成功:', {
        size: blob.size,
        type: blob.type
      });
      
      // 创建对象URL用于显示图片
      const objectUrl = URL.createObjectURL(blob);
      console.log('创建对象 URL:', objectUrl);
      
      return objectUrl;
    } catch (error) {
      console.error('获取二维码失败:', error);
      throw error;
    }
  },

  /**
   * Step 5: Get QR code status
   */
  getQRCodeStatus: async (): Promise<QRCodeStatusResponse> => {
    const data = await api.post<QRCodeStatusResponse>('/login/get-qrcode-status');
    return data;
  },

  /**
   * Step 6: Get login info after successful login
   */
  getLoginInfo: async (): Promise<LoginInfoResponse> => {
    const data = await api.post<LoginInfoResponse>('/login/get-login-info');
    return data;
  },

  /**
   * Step 7: Verify user info with token
   */
  verifyUserInfo: async (token: string): Promise<UserInfoResponse> => {
    const data = await api.post<UserInfoResponse>(`/login/verify-user-info?rq_token=${token}`);
    return data;
  },

  /**
   * Step 8: Get personal login info via redirect URL
   */
  redirectLoginInfo: async (redirectUrl: string): Promise<any> => {
    const data = await api.post<any>('/login/redirect-login-info', { redirect_url: redirectUrl });
    return data;
  }
}; 