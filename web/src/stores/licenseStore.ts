import { defineStore } from 'pinia';
import { ref } from 'vue';
import type { UserInfo } from '@/services/licenseService';

/**
 * 卡密服务状态管理
 */
export const useLicenseStore = defineStore('license', () => {
  // 用户信息
  const userInfo = ref<UserInfo | null>(null);
  
  // 登录 Token
  const token = ref<string>('');
  
  // 是否已登录
  const isLoggedIn = ref<boolean>(false);
  
  // 卡密状态
  const licenseStatus = ref<string>('');
  
  /**
   * 设置用户信息
   */
  const setUserInfo = (info: UserInfo | null) => {
    userInfo.value = info;
    isLoggedIn.value = !!info;
    
    // 同步卡密状态
    if (info?.licenseStatus) {
      licenseStatus.value = info.licenseStatus;
    }
  };
  
  /**
   * 设置登录 Token
   */
  const setToken = (newToken: string) => {
    token.value = newToken;
    
    // 保存到 localStorage
    if (newToken) {
      localStorage.setItem('license_token', newToken);
    } else {
      localStorage.removeItem('license_token');
    }
  };
  
  /**
   * 设置卡密状态
   */
  const setLicenseStatus = (status: string) => {
    licenseStatus.value = status;
  };
  
  /**
   * 清除用户信息（登出）
   */
  const clearUserInfo = () => {
    userInfo.value = null;
    token.value = '';
    isLoggedIn.value = false;
    licenseStatus.value = '';
    localStorage.removeItem('license_token');
  };
  
  /**
   * 从 localStorage 恢复 Token
   */
  const restoreToken = () => {
    const savedToken = localStorage.getItem('license_token');
    if (savedToken) {
      token.value = savedToken;
    }
  };
  
  // 初始化时恢复 Token
  restoreToken();
  
  return {
    userInfo,
    token,
    isLoggedIn,
    licenseStatus,
    setUserInfo,
    setToken,
    setLicenseStatus,
    clearUserInfo,
    restoreToken,
  };
});
