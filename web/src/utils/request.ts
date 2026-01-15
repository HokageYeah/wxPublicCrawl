import axios from 'axios';
import type { AxiosInstance, AxiosRequestConfig, AxiosResponse, InternalAxiosRequestConfig, AxiosError } from 'axios';

// 定义服务器响应的数据结构
interface ApiResponse<T = any> {
  platform: string;
  api: string;
  ret: string[];
  v: number;
  data: T;
}

// 定义错误码映射
const ERROR_CODE_MAP: Record<string, string> = {
  'ERROR::': '请求失败',
  'INVALID_PARAMS::': '参数无效',
  'UNAUTHORIZED::': '未授权',
  'FORBIDDEN::': '禁止访问',
  'NOT_FOUND::': '资源未找到',
  'TIMEOUT::': '请求超时',
  'SERVER_ERROR::': '服务器错误',
};

// 错误类
class ApiError extends Error {
  public code: string;
  public api?: string;
  public platform?: string;
  public originalResponse?: any;

  constructor(message: string, code: string, api?: string, platform?: string, originalResponse?: any) {
    super(message);
    this.name = 'ApiError';
    this.code = code;
    this.api = api;
    this.platform = platform;
    this.originalResponse = originalResponse;
  }
}

class Request {
  private instance: AxiosInstance;
  private baseConfig: AxiosRequestConfig = {
    baseURL: import.meta.env.VITE_API_BASE_URL,
    timeout: 200000,
    withCredentials: true,
  };
  
  // 自定义请求头配置
  private customHeaderGetters: Array<() => { key: string; value: any }> = [];

  constructor(config: AxiosRequestConfig) {
    console.log('import.meta.env.VITE_API_BASE_URL------', import.meta.env);
    this.instance = axios.create(Object.assign(this.baseConfig, config));

    // 请求拦截器
    this.instance.interceptors.request.use(
      (config: InternalAxiosRequestConfig) => {
        // 从所有注册的自定义请求头 getter 函数中获取并设置请求头
        if (this.customHeaderGetters.length > 0) {
          this.customHeaderGetters.forEach(getter => {
            try {
              const header = getter();
              if (header && header.key && header.value !== undefined) {
                config.headers[header.key] = header.value;
                console.log(`✅ 已设置自定义请求头 ${header.key}:`, header.value);
              }
            } catch (error) {
              console.error(`设置自定义请求头时出错:`, error);
            }
          });
        }
        
        return config;
      },
      (error: AxiosError) => {
        console.error('请求拦截器错误:', error);
        return Promise.reject(error);
      }
    );

    // 响应拦截器
    this.instance.interceptors.response.use(
      (response: AxiosResponse<ApiResponse>) => {
        const { data, headers } = response;
        console.log('response.data------', data); 
        console.log('response.headers------', headers); 

        // 检查是否为二进制数据（Blob、ArrayBuffer 等）
        const contentType = headers['content-type'] || '';
        const isBinaryData = data instanceof Blob || 
                            data instanceof ArrayBuffer || 
                            contentType.includes('image/') || 
                            contentType.includes('application/octet-stream') ||
                            contentType.includes('application/pdf');
        
        // 如果是二进制数据，直接返回
        if (isBinaryData) {
          console.log('检测到二进制数据，直接返回:', {
            type: data instanceof Blob ? 'Blob' : data instanceof ArrayBuffer ? 'ArrayBuffer' : 'Other',
            contentType,
            size: data instanceof Blob ? data.size : data instanceof ArrayBuffer ? data.byteLength : 'unknown'
          });
          return data;
        }
        
        // 检查响应数据格式（JSON 数据）
        if (!data || typeof data !== 'object') {
          console.error('响应数据格式错误:', data);
          return Promise.reject(new ApiError('响应数据格式错误', 'INVALID_RESPONSE'));
        }

        // 检查 ret 字段
        if (!data.ret || !Array.isArray(data.ret) || data.ret.length === 0) {
          console.error('响应状态字段缺失或格式错误:', data);
          return Promise.reject(new ApiError('响应状态字段缺失', 'INVALID_RESPONSE', data.api, data.platform, data));
        }

        const statusCode = data.ret[0];
        
        // 判断请求是否成功
        if (statusCode.startsWith('SUCCESS::')) {
          // 请求成功，直接返回 data 字段
          return data.data;
        } else {
          // 请求失败，解析错误信息
          const errorMsg = this.parseErrorMessage(statusCode);
          console.error('API 请求失败:', {
            api: data.api,
            platform: data.platform,
            statusCode,
            errorMsg,
            fullResponse: data
          });
          
          return Promise.reject(new ApiError(
            errorMsg,
            statusCode.split('::')[0] || 'ERROR',
            data.api,
            data.platform,
            data
          ));
        }
      },
      (error: AxiosError) => {
        // HTTP 状态码错误或网络错误
        console.error('响应拦截器错误:', error);
        
        if (error.response) {
          // 服务器返回了错误状态码
          const { status, statusText, data } = error.response;
          let errorMessage = `HTTP ${status}: ${statusText}`;
          
          // 尝试从响应中提取错误信息
          if (data && typeof data === 'object') {
            const apiData = data as any;
            if (apiData.ret && Array.isArray(apiData.ret) && apiData.ret[0]) {
              errorMessage = this.parseErrorMessage(apiData.ret[0]);
            } else if (apiData.detail) {
              errorMessage = apiData.detail;
            } else if (apiData.message) {
              errorMessage = apiData.message;
            }
          }
          
          return Promise.reject(new ApiError(
            errorMessage,
            `HTTP_${status}`,
            error.config?.url,
            undefined,
            error.response
          ));
        } else if (error.request) {
          // 请求已发出但没有收到响应
          return Promise.reject(new ApiError(
            '网络请求失败，请检查网络连接',
            'NETWORK_ERROR',
            error.config?.url
          ));
        } else {
          // 请求配置出错
          return Promise.reject(new ApiError(
            error.message || '请求配置错误',
            'REQUEST_ERROR',
            error.config?.url
          ));
        }
      }
    );
  }

  /**
   * 解析错误消息
   * @param statusCode 状态码字符串，格式如 "ERROR::错误信息"
   * @returns 解析后的错误信息
   */
  private parseErrorMessage(statusCode: string): string {
    if (!statusCode) return '未知错误';
    
    const parts = statusCode.split('::');
    if (parts.length >= 2) {
      // 返回 :: 后面的具体错误信息
      return parts.slice(1).join('::');
    }
    
    // 如果没有具体信息，尝试从错误码映射中查找
    const errorPrefix = parts[0] + '::';
    return ERROR_CODE_MAP[errorPrefix] || statusCode;
  }

  /**
   * 添加自定义请求头 getter 函数
   * @param getter 返回自定义请求头配置的函数，格式为 { key: string; value: any }
   */
  public addCustomHeaderGetter(getter: () => { key: string; value: any }): void {
    this.customHeaderGetters.push(getter);
  }

  /**
   * 移除自定义请求头 getter 函数
   * @param getter 要移除的 getter 函数
   */
  public removeCustomHeaderGetter(getter: () => { key: string; value: any }): void {
    const index = this.customHeaderGetters.indexOf(getter);
    if (index > -1) {
      this.customHeaderGetters.splice(index, 1);
    }
  }

  /**
   * 清空所有自定义请求头 getter 函数
   */
  public clearCustomHeaderGetters(): void {
    this.customHeaderGetters = [];
  }

  /**
   * 设置获取 cookies 的函数（向后兼容方法）
   * @param headerName 请求头名称，例如 'X-WX-Cookies'
   * @param getter 返回 cookies 对象的函数
   */
  public setCookiesGetter(headerName: string, getter: () => Record<string, any>): void {
    this.addCustomHeaderGetter(() => {
      const cookies = getter();
      if (cookies && Object.keys(cookies).length > 0) {
        // 将 cookies 对象转换为 Cookie 字符串
        const cookieStr = Object.entries(cookies)
          .map(([key, value]) => `${key}=${value}`)
          .join('; ');
        return { key: headerName, value: cookieStr };
      }
      return { key: headerName, value: '' };
    });
  }

  /**
   * 设置获取 token 的函数（向后兼容方法）
   * @param headerName 请求头名称，例如 'X-WX-Token'
   * @param getter 返回 token 字符串的函数
   */
  public setTokenGetter(headerName: string, getter: () => string): void {
    this.addCustomHeaderGetter(() => {
      const token = getter();
      return { key: headerName, value: token };
    });
  }

  public request<T = any>(config: AxiosRequestConfig): Promise<T> {
    return this.instance.request(config);
  }

  public get<T = any>(url: string, config?: AxiosRequestConfig): Promise<T> {
    return this.instance.get(url, config);
  }

  public post<T = any>(url: string, data?: any, config?: AxiosRequestConfig): Promise<T> {
    return this.instance.post(url, data, config);
  }

  public put<T = any>(url: string, data?: any, config?: AxiosRequestConfig): Promise<T> {
    return this.instance.put(url, data, config);
  }

  public delete<T = any>(url: string, config?: AxiosRequestConfig): Promise<T> {
    return this.instance.delete(url, config);
  }

  public patch<T = any>(url: string, data?: any, config?: AxiosRequestConfig): Promise<T> {
    return this.instance.patch(url, data, config);
  }

  /**
   * 获取二进制数据（如图片、文件等）
   * 自动设置 responseType 为 'blob'
   */
  public getBlob(url: string, config?: AxiosRequestConfig): Promise<Blob> {
    return this.instance.get(url, {
      ...config,
      responseType: 'blob'
    });
  }

  /**
   * 获取 ArrayBuffer 数据
   * 自动设置 responseType 为 'arraybuffer'
   */
  public getArrayBuffer(url: string, config?: AxiosRequestConfig): Promise<ArrayBuffer> {
    return this.instance.get(url, {
      ...config,
      responseType: 'arraybuffer'
    });
  }

  /**
   * 下载文件
   * 自动处理文件下载逻辑
   */
  public async downloadFile(url: string, filename?: string, config?: AxiosRequestConfig): Promise<void> {
    const blob = await this.getBlob(url, config);
    
    // 创建下载链接
    const downloadUrl = window.URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = downloadUrl;
    
    // 设置文件名
    if (filename) {
      link.download = filename;
    } else {
      // 尝试从响应头获取文件名
      const disposition = config?.headers?.['content-disposition'];
      if (disposition && disposition.includes('filename=')) {
        const matches = /filename[^;=\n]*=((['"]).*?\2|[^;\n]*)/.exec(disposition);
        if (matches && matches[1]) {
          link.download = matches[1].replace(/['"]/g, '');
        }
      }
    }
    
    // 触发下载
    document.body.appendChild(link);
    link.click();
    
    // 清理
    document.body.removeChild(link);
    window.URL.revokeObjectURL(downloadUrl);
  }
}

// 导出错误类供外部使用
export { ApiError };
export type { ApiResponse };

// 导出默认实例
export default new Request({});
