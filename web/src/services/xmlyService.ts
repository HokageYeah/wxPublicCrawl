import api from '@/utils/request';
import type {
  GenerateQrcodeResponse,
  CheckQrcodeStatusRequest,
  CheckQrcodeStatusResponse,
  SessionResponse,
  XmlyUserInfo
} from '@/types/xmly';

// 基础URL

/**
 * 喜马拉雅听书API服务
 * 提供登录、会话管理等功能
 */
export const xmlyService = {
  /**
   * 生成喜马拉雅登录二维码
   * @returns Promise<GenerateQrcodeResponse> 包含qrId和base64编码的二维码图片
   */
  generateQrcode: async (): Promise<GenerateQrcodeResponse> => {
    const data = await api.post<GenerateQrcodeResponse>('/xmly/login/generate-qrcode');
    return data;
  },

  /**
   * 检查二维码状态（轮询接口）
   * @param params qrId 二维码ID
   * @returns Promise<CheckQrcodeStatusResponse> 包含扫码状态和用户信息
   */
  checkQrcodeStatus: async (params: CheckQrcodeStatusRequest): Promise<CheckQrcodeStatusResponse> => {
    const data = await api.post<CheckQrcodeStatusResponse>('/xmly/login/check-qrcode-status', params);
    return data;
  },

  /**
   * 获取当前登录状态
   * @returns Promise<SessionResponse> 包含登录状态和用户信息
   */
  getSession: async (): Promise<SessionResponse> => {
    const data = await api.get<SessionResponse>('/xmly/login/get-session');
    return data;
  },

  /**
   * 退出登录
   * @returns Promise<any> 退出结果
   */
  logout: async (): Promise<any> => {
    const data = await api.delete('/xmly/login/logout');
    return data;
  },

  /**
   * 获取二维码图片（直接返回图片格式）
   * 注意：喜马拉雅接口返回的是base64字符串，不需要额外请求
   * 此方法保留用于一致性，实际图片已包含在generateQrcode响应中
   * @returns Promise<Blob> 二进制图片数据
   */
  getQrcodeImage: async (): Promise<Blob> => {
    const qrcodeResponse = await this.generateQrcode();
    const base64Data = qrcodeResponse.img;

    // 移除可能存在的data URL前缀
    const base64Clean = base64Data.replace(/^data:image\/\w+;base64,/, '');

    // 将base64转换为Blob
    const byteCharacters = atob(base64Clean);
    const byteNumbers = new Array(byteCharacters.length);
    for (let i = 0; i < byteCharacters.length; i++) {
      byteNumbers[i] = byteCharacters.charCodeAt(i);
    }
    const byteArray = new Uint8Array(byteNumbers);
    const blob = new Blob([byteArray], { type: 'image/png' });

    console.log('二维码获取成功:', {
      size: blob.size,
      type: blob.type
    });

    return blob;
  }
};
