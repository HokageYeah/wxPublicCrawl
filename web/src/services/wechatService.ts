import axios from 'axios';
import type { 
  ApiResponseData, 
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
const baseURL = import.meta.env.DEV ? '/web-api/api/v1/wx/public' : '/api/v1/wx/public';
console.log('mport.meta.env.DEV---', import.meta.env.DEV)
const api = axios.create({
  baseURL,
  withCredentials: true, // Important for cookies
});

// API endpoints
export const wechatService = {
  /**
   * Generate a session ID for the login flow
   */
  generateSessionId: async (): Promise<string> => {
    const response = await api.get<ApiResponseData<SessionIdResponse>>('/login/generate-session-id');
    return response.data.data.session_id;
  },

  /**
   * Step 1: Prelogin - Get ignore password list
   */
  prelogin: async (params: PreloginRequest = {}): Promise<ApiResponseData<PreloginResponse>> => {
    const response = await api.post<ApiResponseData<PreloginResponse>>('/login/prelogin', params);
    return response.data;
  },

  /**
   * Step 2: Start login - Get QR code
   */
  startLogin: async (params: StartLoginRequest): Promise<ApiResponseData<StartLoginResponse>> => {
    console.log('startLogin params', params);
    const response = await api.post<ApiResponseData<StartLoginResponse>>('/login/startlogin', params);
    return response.data;
  },

  /**
   * Step 3: Web report - Report device info
   */
  webReport: async (params: WebreportRequest): Promise<ApiResponseData<any>> => {
    console.log('webReport params', params);
    const response = await api.post<ApiResponseData<any>>('/login/webreport', params);
    return response.data;
  },

  /**
   * Step 4: Get WeChat login QR code
   * 处理接口返回的图片数据，转换为可显示的URL
   */
  getLoginQRCode: async (): Promise<string> => {
    try {
      // 直接请求二进制数据，指定responseType为blob
      const response = await api.get('/login/get-wx-login-qrcode', { 
        responseType: 'blob',
        headers: {
          Accept: 'image/jpeg,image/png,image/*'
        }
      });
      console.log('QR code response received');
      
      // 检查响应类型
      const contentType = response.headers['content-type'];
      console.log('Content-Type:', contentType);
      
      // 创建对象URL
      const blob = new Blob([response.data], { 
        type: contentType || 'image/png' 
      });
      
      // 打印blob信息以便调试
      console.log('Blob size:', blob.size);
      console.log('Blob type:', blob.type);
      
      // 直接创建对象URL
      const objectUrl = URL.createObjectURL(blob);
      console.log('Created Object URL:', objectUrl);
      return objectUrl;
    } catch (error) {
      console.error('Error fetching QR code:', error);
      throw error;
    }
  },

  /**
   * Step 5: Get QR code status
   */
  getQRCodeStatus: async (): Promise<ApiResponseData<QRCodeStatusResponse>> => {
    const response = await api.post<ApiResponseData<QRCodeStatusResponse>>('/login/get-qrcode-status');
    return response.data;
  },

  /**
   * Step 6: Get login info after successful login
   */
  getLoginInfo: async (): Promise<ApiResponseData<LoginInfoResponse>> => {
    const response = await api.post<ApiResponseData<LoginInfoResponse>>('/login/get-login-info');
    return response.data;
  },

  /**
   * Step 7: Verify user info with token
   */
  verifyUserInfo: async (token: string): Promise<ApiResponseData<UserInfoResponse>> => {
    const response = await api.post<ApiResponseData<UserInfoResponse>>(`/login/verify-user-info?rq_token=${token}`);
    return response.data;
  },

  /**
   * Step 8: Get personal login info via redirect URL
   */
  redirectLoginInfo: async (redirectUrl: string): Promise<ApiResponseData<any>> => {
    const response = await api.post<ApiResponseData<any>>('/login/redirect-login-info', { redirect_url: redirectUrl });
    return response.data;
  }
}; 