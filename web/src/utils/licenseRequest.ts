import { Request } from './request';

/**
 * 卡密绑定服务专用的请求实例
 * 用于调用运行在 8003 端口的卡密绑定、注册、登录系统
 */
class LicenseRequest extends Request {
  constructor() {
    super({
      baseURL: import.meta.env.VITE_LICENSE_API_BASE_URL,
      timeout: 200000,
      withCredentials: true,
    });
    console.log('卡密服务 API 基础路径:', import.meta.env.VITE_LICENSE_API_BASE_URL);
  }
}

// 导出卡密服务专用实例
export default new LicenseRequest();
