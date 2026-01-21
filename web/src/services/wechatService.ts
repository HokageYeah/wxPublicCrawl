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
import dayjs from 'dayjs';

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
   * 生成登录流程的会话ID
   */
  generateSessionId: async (): Promise<string> => {
    const data = await api.get<SessionIdResponse>('/login/generate-session-id');
    return data?.session_id || '';
  },

  /**
   * 步骤1：预登录 - 获取忽略密码列表
   */
  prelogin: async (params: PreloginRequest = {}): Promise<PreloginResponse> => {
    const data = await api.post<PreloginResponse>('/login/prelogin', params);
    return data;
  },

  /**
   * 步骤2：开始登录 - 获取二维码
   */
  startLogin: async (params: StartLoginRequest): Promise<StartLoginResponse> => {
    console.log('startLogin params', params);
    const data = await api.post<StartLoginResponse>('/login/startlogin', params);
    return data;
  },

  /**
   * 步骤3：设备报告 - 上报设备信息
   */
  webReport: async (params: WebreportRequest): Promise<any> => {
    console.log('webReport params', params);
    const data = await api.post<any>('/login/webreport', params);
    return data;
  },

  /**
   * 步骤4：获取微信登录二维码
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
   * 步骤5：获取二维码状态
   */
  getQRCodeStatus: async (): Promise<QRCodeStatusResponse> => {
    const data = await api.post<QRCodeStatusResponse>('/login/get-qrcode-status');
    return data;
  },

  /**
   * 步骤6：登录成功后获取登录信息
   */
  getLoginInfo: async (): Promise<LoginInfoResponse> => {
    const data = await api.post<LoginInfoResponse>('/login/get-login-info');
    return data;
  },

  /**
   * 步骤7：使用token验证用户信息
   */
  verifyUserInfo: async (token: string): Promise<UserInfoResponse> => {
    const data = await api.post<UserInfoResponse>(`/login/verify-user-info?rq_token=${token}`);
    return data;
  },

  /**
   * 步骤8：通过重定向URL获取个人信息
   */
  redirectLoginInfo: async (redirectUrl: string): Promise<any> => {
    const data = await api.post<any>('/login/redirect-login-info', { redirect_url: redirectUrl });
    return data;
  },

  /**
   * 获取公众号文章列表（分页）
   */
  getArticleList: async (params: {
    wx_public_id: string;
    begin: number;
    count: number;
    query?: string;
  }): Promise<any> => {
    const data = await api.post<any>('/get-wx-article-list', params);
    return data;
  },

  /**
   * 获取公众号所有文章（循环调用，直到获取所有文章）
   * 调用时间间隔：3-8秒
   */
  getAllArticles: async (
    wx_public_id: string,
    onProgress?: (current: number, total: number, message: string) => void
  ): Promise<any[]> => {
    const allArticles: any[] = [];
    let begin = 0;
    const count = 20; // 每页获取数量
    let totalCount = 0;
    
    try {
      // 首先调用一次获取总数
      const firstResponse = await wechatService.getArticleList({
        wx_public_id,
        begin: 0,
        count: count,
        query: ''
      });
      
      if (firstResponse && typeof firstResponse === 'object' && 'total_count' in firstResponse) {
        totalCount = firstResponse.total_count as number;
        onProgress?.(0, totalCount, `开始获取，预计共 ${totalCount} 篇文章`);
      }
      
      // 如果有第一页的文章，添加到列表
      if (firstResponse && typeof firstResponse === 'object' && 'publish_list' in firstResponse && Array.isArray(firstResponse.publish_list)) {
        const publishList = firstResponse.publish_list as any[];
        const articles = publishList.map((item: any) => {
          const info = item.appmsgex ? item.appmsgex[0] : item;
          if (!info) return null;
          return {
            aid: info.aid || (info.appmsgid + '_' + info.itemidx),
            title: info.title || '无标题',
            link: info.link,
            update_time: info.update_time,
            publish_time: dayjs(info.update_time * 1000).format('YYYY-MM-DD HH:mm:ss')
          };
        }).filter((item: any) => item !== null);
        
        allArticles.push(...articles);
        onProgress?.(allArticles.length, totalCount, `已获取 ${allArticles.length}/${totalCount} 篇文章`);
      }
      
      // 更新起始位置
      begin += count;
      
      // 循环获取剩余文章
      while (true) {
        // 如果已经获取所有文章，结束循环
        if (totalCount > 0 && allArticles.length >= totalCount) {
          onProgress?.(allArticles.length, totalCount, '获取完成！');
          break;
        }
        
        // 随机延迟 3-8 秒
        const delay = Math.random() * 5000 + 3000;
        await new Promise(resolve => setTimeout(resolve, delay));
        
        // 调用接口获取下一页
        const response = await wechatService.getArticleList({
          wx_public_id,
          begin,
          count,
          query: ''
        });
        
        if (response && typeof response === 'object' && 'publish_list' in response && Array.isArray(response.publish_list) && response.publish_list.length > 0) {
          const publishList = response.publish_list as any[];
          const articles = publishList.map((item: any) => {
            const info = item.appmsgex ? item.appmsgex[0] : item;
            if (!info) return null;
            return {
              aid: info.aid || (info.appmsgid + '_' + info.itemidx),
              title: info.title || '无标题',
              link: info.link,
              update_time: info.update_time,
              publish_time: dayjs(info.update_time * 1000).format('YYYY-MM-DD HH:mm:ss')
            };
          }).filter((item: any) => item !== null);
          
          allArticles.push(...articles);
          onProgress?.(allArticles.length, totalCount, `已获取 ${allArticles.length}/${totalCount} 篇文章`);
          
          // 如果返回的文章数少于请求数，说明已经是最后一页
          if (response.publish_list.length < count) {
            onProgress?.(allArticles.length, totalCount, '获取完成！');
            break;
          }
          
          // 更新起始位置
          begin += count;
        } else {
          // 没有更多文章
          onProgress?.(allArticles.length, totalCount, '获取完成！');
          break;
        }
      }
      
      return allArticles;
    } catch (error) {
      console.error('获取所有文章失败:', error);
      throw error;
    }
  },

    /**
   * 导出文章到Excel
   */
  exportArticlesToExcel: async (articles: any[], save_path: string, file_name: string): Promise<any> => {
    const data = await api.post<any>('/export-articles-to-excel', { articles, save_path, file_name });
    return data;
  },
};