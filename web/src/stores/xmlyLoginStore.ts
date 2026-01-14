import { defineStore } from 'pinia';
import { XmlyLoginStep, XmlyQRCodeStatus } from '@/types/xmly';
import { xmlyService } from '@/services/xmlyService';

export const useXmlyLoginStore = defineStore('xmlyLogin', {
  state: () => ({
    qrId: '',
    qrCodeImg: '',
    qrCodeStatus: XmlyQRCodeStatus.WAITING,
    currentStep: XmlyLoginStep.INIT,
    error: null as string | null,
    userInfo: null as XmlyUserInfo | null,
    isLoggedIn: false,
    pollingInterval: null as number | null,
    pollingCount: 0,
    maxPollingCount: 60, // 最多轮询60次（约60秒）
  }),

  getters: {
    isLoading: (state) => {
      return state.currentStep === XmlyLoginStep.INIT;
    },

    qrCodeStateText: (state) => {
      switch (state.qrCodeStatus) {
        case XmlyQRCodeStatus.WAITING:
          return '请使用喜马拉雅App扫描二维码登录';
        case XmlyQRCodeStatus.SCANNED:
          return '扫描成功，正在登录...';
        case XmlyQRCodeStatus.EXPIRED:
          return '二维码已过期，请重新生成';
        default:
          return '未知状态';
      }
    }
  },

  actions: {
    async initialize() {
      try {
        console.log('正在从后端加载喜马拉雅用户会话...');
        const sessionResponse = await xmlyService.getSession();

        if (sessionResponse.is_logged_in && sessionResponse.user_info) {
          this.userInfo = sessionResponse.user_info;
          this.isLoggedIn = true;
          this.currentStep = XmlyLoginStep.LOGIN_SUCCESS;
          console.log('✓ 从后端恢复用户登录状态', this.userInfo);
        } else {
          console.log('未找到有效的喜马拉雅会话');
        }
      } catch (error) {
        console.error('加载喜马拉雅用户会话失败:', error);
      }
    },

    async startLoginFlow() {
      // 检查是否已有会话
      if (this.isLoggedIn) {
        console.log('用户已登录，无需重新扫码');
        return;
      }

      try {
        // 重置状态
        this.error = null;
        this.currentStep = XmlyLoginStep.INIT;
        this.qrCodeStatus = XmlyQRCodeStatus.WAITING;
        this.userInfo = null;
        this.isLoggedIn = false;
        this.pollingCount = 0;

        // Step 1: 生成二维码
        this.currentStep = XmlyLoginStep.INIT;
        await this.generateQrcode();

      } catch (err: any) {
        console.error('登录流程错误:', err);
        this.error = err.message || '生成二维码失败';
        this.currentStep = XmlyLoginStep.ERROR;
      }
    },

    async generateQrcode() {
      try {
        console.log('正在生成喜马拉雅登录二维码...');
        const response = await xmlyService.generateQrcode();

        this.qrId = response.qrId;
        // 将base64图片转换为data URL
        this.qrCodeImg = `data:image/png;base64,${response.img}`;
        this.currentStep = XmlyLoginStep.QRCODE_GENERATED;

        console.log('✓ 二维码生成成功，qrId:', response.qrId);

        // 开始轮询
        this.startPolling();
      } catch (error: any) {
        console.error('生成二维码失败:', error);
        this.error = error.response?.data?.detail || '生成二维码失败，请重试';
        this.currentStep = XmlyLoginStep.ERROR;
      }
    },

    startPolling() {
      console.log('开始轮询二维码状态...');

      if (this.pollingInterval) {
        clearInterval(this.pollingInterval);
      }

      this.pollingInterval = window.setInterval(async () => {
        try {
          this.pollingCount++;

          // 检查是否超过最大轮询次数
          if (this.pollingCount > this.maxPollingCount) {
            console.log('轮询超时，二维码已过期');
            this.stopPolling();
            this.qrCodeStatus = XmlyQRCodeStatus.EXPIRED;
            this.error = '二维码已过期，请重新生成';
            this.currentStep = XmlyLoginStep.ERROR;
            return;
          }

          console.log(`第 ${this.pollingCount} 次轮询...`);

          // 检查二维码状态
          const statusResponse = await xmlyService.checkQrcodeStatus({ qrId: this.qrId });

          // 未扫码
          if (statusResponse.code === 32000) {
            this.qrCodeStatus = XmlyQRCodeStatus.WAITING;
            console.log('等待扫码...');
          }
          // 扫码成功
          else if (statusResponse.code === 0 && statusResponse.scanned && statusResponse.user_info) {
            console.log('✓ 用户扫码成功');
            this.qrCodeStatus = XmlyQRCodeStatus.SCANNED;
            this.currentStep = XmlyLoginStep.QRCODE_SCANNED;

            // 停止轮询
            this.stopPolling();

            // 保存用户信息
            this.userInfo = statusResponse.user_info;
            this.isLoggedIn = true;
            this.currentStep = XmlyLoginStep.LOGIN_SUCCESS;

            console.log('✓ 登录成功', this.userInfo);

            // 自动保存会话到后端
            await this.saveSessionToBackend();
          }
        } catch (error: any) {
          console.error('轮询二维码状态失败:', error);
          this.error = error.response?.data?.detail || '检查二维码状态失败';
        }
      }, 1000); // 每秒轮询一次
    },

    stopPolling() {
      if (this.pollingInterval) {
        clearInterval(this.pollingInterval);
        this.pollingInterval = null;
        console.log('✓ 停止轮询');
      }
    },

    async saveSessionToBackend() {
      try {
        // 注意：喜马拉雅的会话已经在后端保存了，这里主要是为了记录
        console.log('✓ 喜马拉雅会话已保存到后端');
      } catch (error) {
        console.error('保存喜马拉雅会话到后端失败:', error);
      }
    },

    async logout() {
      try {
        console.log('正在退出喜马拉雅登录...');

        // 清除后端会话
        await xmlyService.logout();
        console.log('✓ 后端会话已清除');
      } catch (error) {
        console.error('清除后端会话失败:', error);
      } finally {
        // 重置状态
        this.reset();
        console.log('✓ 用户已退出登录');
      }
    },

    reset() {
      this.stopPolling();

      this.qrId = '';
      this.qrCodeImg = '';
      this.qrCodeStatus = XmlyQRCodeStatus.WAITING;
      this.currentStep = XmlyLoginStep.INIT;
      this.error = null;
      this.userInfo = null;
      this.isLoggedIn = false;
      this.pollingCount = 0;
    },

    cleanup() {
      this.stopPolling();
    }
  }
});
