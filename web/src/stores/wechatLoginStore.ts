import { defineStore } from 'pinia';
import { LoginStep, QRCodeStatus } from '@/types/wechat';
import { wechatService } from '@/services/wechatService';

export const useWechatLoginStore = defineStore('wechatLogin', {
  // 状态定义
  state: () => ({
    sessionId: '',
    qrCodeUrl: '',
    qrCodeStatus: QRCodeStatus.WAITING,
    currentStep: LoginStep.INIT,
    error: null as string | null,
    token: '',
    redirectUrl: '',
    userInfo: null as any,
    loginComplete: false,
    statusPollingInterval: null as number | null,
    createdBlobUrls: [] as string[]
  }),

  // 计算属性
  getters: {
    isLoading: (state) => {
      return [
        LoginStep.PRELOGIN,
        LoginStep.STARTLOGIN,
        LoginStep.WEBREPORT,
      ].includes(state.currentStep);
    },
    
    qrCodeStateText: (state) => {
      switch (state.qrCodeStatus) {
        case QRCodeStatus.WAITING:
          return '请使用微信扫描二维码登录';
        case QRCodeStatus.SCANNED:
          return '已扫描，请在微信上确认登录';
        case QRCodeStatus.CONFIRMED:
          return '已确认，正在登录...';
        case QRCodeStatus.EXPIRED:
          return '二维码已过期，请刷新页面重试';
        default:
          return '未知状态';
      }
    },
    
    // 判断用户是否已登录
    isLoggedIn: (state) => {
      return !!state.userInfo && state.loginComplete;
    }
  },

  // 操作方法
  actions: {
    // 初始化 - 检查本地存储的用户信息
    initialize() {
      try {
        // 从 localStorage 读取用户信息
        const savedUserInfo = localStorage.getItem('wxUserInfo');
        if (savedUserInfo) {
          const userData = JSON.parse(savedUserInfo);
          // 恢复用户登录状态
          this.userInfo = userData;
          this.loginComplete = true;
          this.currentStep = LoginStep.REDIRECT_SUCCESS;
          console.log('从本地存储恢复用户登录状态', userData);
        }
      } catch (error) {
        console.error('读取本地存储的用户信息失败:', error);
        // 清除可能损坏的数据
        localStorage.removeItem('wxUserInfo');
      }
    },
    
    // 保存用户信息到本地存储
    saveUserInfoToLocalStorage() {
      if (this.userInfo) {
        try {
          localStorage.setItem('wxUserInfo', JSON.stringify(this.userInfo));
          console.log('用户信息已保存到本地存储');
        } catch (error) {
          console.error('保存用户信息到本地存储失败:', error);
        }
      }
    },
    
    // 退出登录
    logout() {
      // 清除本地存储的用户信息
      localStorage.removeItem('wxUserInfo');
      
      // 重置状态
      this.reset();
      
      console.log('用户已退出登录');
    },

    async startLoginFlow() {
      // 检查是否已有本地存储的用户信息
      if (this.isLoggedIn) {
        console.log('用户已登录，无需重新扫码');
        return;
      }
      
      try {
        // 重置状态
        this.error = null;
        this.currentStep = LoginStep.INIT;
        this.qrCodeStatus = QRCodeStatus.WAITING;
        this.token = '';
        this.redirectUrl = '';
        this.userInfo = null;
        this.loginComplete = false;
        
        // 清理之前的Blob URL
        if (this.qrCodeUrl && this.qrCodeUrl.startsWith('blob:')) {
          URL.revokeObjectURL(this.qrCodeUrl);
          this.createdBlobUrls = this.createdBlobUrls.filter(url => url !== this.qrCodeUrl);
        }
        this.qrCodeUrl = '';
        
        if (this.statusPollingInterval) {
          window.clearInterval(this.statusPollingInterval);
          this.statusPollingInterval = null;
        }
        
        // Step 1: Generate session ID
        this.currentStep = LoginStep.INIT;
        this.sessionId = await wechatService.generateSessionId();
        console.log('sessionId', this.sessionId);
        
        // Step 2: Prelogin
        this.currentStep = LoginStep.PRELOGIN;
        await wechatService.prelogin();
        
        // Step 3: Start login
        this.currentStep = LoginStep.STARTLOGIN;
        await wechatService.startLogin({
          userlang: 'zh_CN',
          redirect_url: '',
          login_type: 3,
          sessionid: this.sessionId,
        });
        
        // Step 4: Web report
        this.currentStep = LoginStep.WEBREPORT;
        await wechatService.webReport({
          devicetype: 1,
          optype: 1,
          page_state: 3,
          log_id: 19015,
        });
        
        // Step 5: Get QR code
        try {
          // 获取二维码
          this.qrCodeUrl = await wechatService.getLoginQRCode();
          console.log('QR code URL set:', this.qrCodeUrl);
          this.currentStep = LoginStep.QRCODE_GENERATED;
          
          // 如果是Blob URL，添加到列表中以便后续清理
          if (this.qrCodeUrl && this.qrCodeUrl.startsWith('blob:')) {
            this.createdBlobUrls.push(this.qrCodeUrl);
          }
          
          // Start polling for QR code status
          this.startStatusPolling();
        } catch (qrError: any) {
          console.error('获取二维码失败:', qrError);
          this.error = qrError.message || '获取二维码失败，请刷新页面重试';
          this.currentStep = LoginStep.ERROR;
        }
        
      } catch (err: any) {
        console.error('登录流程错误:', err);
        this.error = err.message || 'Failed to start login flow';
        this.currentStep = LoginStep.ERROR;
      }
    },
    
    startStatusPolling() {
      // Check status every 2 seconds
      this.statusPollingInterval = window.setInterval(async () => {
        try {
          const statusResponse = await wechatService.getQRCodeStatus();
          this.qrCodeStatus = statusResponse.status;
          console.log('QR code status:', this.qrCodeStatus);
          
          // Handle status changes
          if (this.qrCodeStatus === QRCodeStatus.SCANNED) {
            this.currentStep = LoginStep.QRCODE_SCANNED;
          } else if (this.qrCodeStatus === QRCodeStatus.CONFIRMED) {
            this.currentStep = LoginStep.QRCODE_CONFIRMED;
            await this.handleConfirmedLogin();
          } else if (this.qrCodeStatus === QRCodeStatus.EXPIRED) {
            this.stopStatusPolling();
          }
        } catch (err: any) {
          console.error('获取二维码状态失败:', err);
          this.error = err.message || 'Failed to check QR code status';
        }
      }, 2000);
    },
    
    stopStatusPolling() {
      if (this.statusPollingInterval) {
        window.clearInterval(this.statusPollingInterval);
        this.statusPollingInterval = null;
      }
    },
    
    async handleConfirmedLogin() {
      try {
        // Stop polling
        this.stopStatusPolling();
        // Step 6: Get login info
        const loginInfoResponse = await wechatService.getLoginInfo();
        this.token = loginInfoResponse.token;
        this.redirectUrl = loginInfoResponse.redirect_url;
        this.currentStep = LoginStep.LOGIN_SUCCESS;
        console.log('loginInfoResponse', loginInfoResponse);
        
        // Step 7: Verify user info
        const verifyResponse = await wechatService.verifyUserInfo(this.token);
        // 此时先不设置 userInfo，等待重定向响应
        console.log('verifyResponse', verifyResponse);
        
        // Step 8: Redirect login info
        const redirectResponse = await wechatService.redirectLoginInfo(this.redirectUrl);
        // 使用重定向响应中的用户数据
        this.userInfo = redirectResponse;
        this.currentStep = LoginStep.REDIRECT_SUCCESS;
        this.loginComplete = true;
        console.log('redirectResponse', redirectResponse);
        
        // 保存用户信息到本地存储
        this.saveUserInfoToLocalStorage();
      } catch (err: any) {
        console.error('登录完成流程失败:', err);
        this.error = err.message || 'Failed to complete login';
        this.currentStep = LoginStep.ERROR;
        this.stopStatusPolling();
      }
    },
    
    reset() {
      this.stopStatusPolling();
      
      // 清理Blob URL
      if (this.qrCodeUrl && this.qrCodeUrl.startsWith('blob:')) {
        URL.revokeObjectURL(this.qrCodeUrl);
      }
      
      this.sessionId = '';
      this.qrCodeUrl = '';
      this.qrCodeStatus = QRCodeStatus.WAITING;
      this.currentStep = LoginStep.INIT;
      this.error = null;
      this.token = '';
      this.redirectUrl = '';
      this.userInfo = null;
      this.loginComplete = false;
    },
    
    cleanup() {
      this.stopStatusPolling();
      
      // 清理所有创建的Blob URLs
      this.createdBlobUrls.forEach(url => {
        if (url && url.startsWith('blob:')) {
          URL.revokeObjectURL(url);
        }
      });
      this.createdBlobUrls = [];
      
      // 清理当前使用的Blob URL
      if (this.qrCodeUrl && this.qrCodeUrl.startsWith('blob:')) {
        URL.revokeObjectURL(this.qrCodeUrl);
      }
      this.qrCodeUrl = '';
    }
  }
}); 