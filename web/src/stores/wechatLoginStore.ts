import { defineStore } from "pinia";
import { LoginStep, QRCodeStatus } from "@/types/wechat";
import { wechatService } from "@/services/wechatService";
import { sessionService } from "@/services/sessionService"; // 新增
import type { UserInfo, SessionResponse } from "@/services/sessionService";
import api from "@/utils/request";

export const useWechatLoginStore = defineStore("wechatLogin", {
  state: () => ({
    sessionId: "",
    qrCodeUrl: "",
    qrCodeStatus: QRCodeStatus.WAITING,
    currentStep: LoginStep.INIT,
    error: null as string | null,
    token: "",
    redirectUrl: "",
    userInfo: null as any,
    cookies: {} as Record<string, any>, // 新增：存储cookies
    loginComplete: false,
    statusPollingInterval: null as number | null,
    createdBlobUrls: [] as string[],
  }),

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
          return "请使用微信扫描二维码登录";
        case QRCodeStatus.SCANNED:
          return "已扫描，请在微信上确认登录";
        case QRCodeStatus.CONFIRMED:
          return "已确认，正在登录...";
        case QRCodeStatus.EXPIRED:
          return "二维码已过期，请刷新页面重试";
        default:
          return "未知状态";
      }
    },

    isLoggedIn: (state) => {
      return !!state.userInfo && state.loginComplete;
    },
  },

  actions: {
    // ✅ 修改：从后端加载会话
    async initialize() {
      try {
        console.log("正在从后端加载用户会话...");
        const sessionResponse = await sessionService.loadSession();

        if (sessionResponse.logged_in && sessionResponse.user_info) {
          this.userInfo = sessionResponse.user_info;
          // alert('用户已登录'+ JSON.stringify(sessionResponse));
          this.cookies = sessionResponse.cookies || {}; // 恢复cookies
          this.token = sessionResponse.token || ""; // 恢复token
          this.loginComplete = true;
          this.currentStep = LoginStep.REDIRECT_SUCCESS;
          console.log("✓ 从后端恢复用户登录状态", this.userInfo);
          console.log(
            "✓ 从后端恢复 cookies",
            Object.keys(this.cookies).length,
            "个"
          );
          console.log("✓ 从后端恢复 token", this.token);
          // 在应用设置了cookie和token后调用 getter，让所有请求都能自动携带
          api.setCookiesGetter("X-WX-Cookies", () => this.cookies);
          api.setTokenGetter("X-WX-Token", () => this.token);
        } else {
          console.log("未找到有效的用户会话");
        }
      } catch (error) {
        console.error("加载用户会话失败:", error);
      }
    },

    // ✅ 修改：保存会话到后端
    async saveUserInfoToLocalStorage() {
      if (this.userInfo) {
        try {
          const success = await sessionService.saveSession(
            this.userInfo,
            this.cookies,
            this.token
          );
          if (success) {
            console.log("✓ 用户信息、cookies和token已保存到后端");
          } else {
            console.error("✗ 保存用户信息到后端失败");
          }
        } catch (error) {
          console.error("保存用户信息失败:", error);
        }
      }
    },

    // ✅ 修改：退出登录
    async logout() {
      try {
        // 清除后端会话
        await sessionService.clearSession();
        console.log("✓ 后端会话已清除");
      } catch (error) {
        console.error("清除后端会话失败:", error);
      }

      // 重置状态
      this.reset();
      console.log("用户已退出登录");
    },

    async startLoginFlow() {
      // 检查是否已有会话
      if (this.isLoggedIn) {
        console.log("用户已登录，无需重新扫码");
        return;
      }

      try {
        // 重置状态
        this.error = null;
        this.currentStep = LoginStep.INIT;
        this.qrCodeStatus = QRCodeStatus.WAITING;
        this.token = "";
        this.redirectUrl = "";
        this.userInfo = null;
        this.loginComplete = false;

        // 清理之前的Blob URL
        if (this.qrCodeUrl && this.qrCodeUrl.startsWith("blob:")) {
          URL.revokeObjectURL(this.qrCodeUrl);
          this.createdBlobUrls = this.createdBlobUrls.filter(
            (url) => url !== this.qrCodeUrl
          );
        }
        this.qrCodeUrl = "";

        if (this.statusPollingInterval) {
          window.clearInterval(this.statusPollingInterval);
          this.statusPollingInterval = null;
        }

        // Step 1: Generate session ID
        this.currentStep = LoginStep.INIT;
        this.sessionId = await wechatService.generateSessionId();

        // Step 2: Prelogin
        this.currentStep = LoginStep.PRELOGIN;
        await wechatService.prelogin();

        // Step 3: Start login
        this.currentStep = LoginStep.STARTLOGIN;
        await wechatService.startLogin({
          userlang: "zh_CN",
          redirect_url: "",
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
          this.qrCodeUrl = await wechatService.getLoginQRCode();
          this.currentStep = LoginStep.QRCODE_GENERATED;

          if (this.qrCodeUrl && this.qrCodeUrl.startsWith("blob:")) {
            this.createdBlobUrls.push(this.qrCodeUrl);
          }

          this.startStatusPolling();
        } catch (qrError: any) {
          console.error("获取二维码失败:", qrError);
          this.error = qrError.message || "获取二维码失败，请刷新页面重试";
          this.currentStep = LoginStep.ERROR;
        }
      } catch (err: any) {
        console.error("登录流程错误:", err);
        this.error = err.message || "Failed to start login flow";
        this.currentStep = LoginStep.ERROR;
      }
    },

    startStatusPolling() {
      this.statusPollingInterval = window.setInterval(async () => {
        try {
          const statusResponse = await wechatService.getQRCodeStatus();
          this.qrCodeStatus = statusResponse.status;

          if (this.qrCodeStatus === QRCodeStatus.SCANNED) {
            this.currentStep = LoginStep.QRCODE_SCANNED;
          } else if (this.qrCodeStatus === QRCodeStatus.CONFIRMED) {
            this.currentStep = LoginStep.QRCODE_CONFIRMED;
            await this.handleConfirmedLogin();
          } else if (this.qrCodeStatus === QRCodeStatus.EXPIRED) {
            this.stopStatusPolling();
          }
        } catch (err: any) {
          console.error("获取二维码状态失败:", err);
          this.error = err.message || "Failed to check QR code status";
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
        console.log("handleConfirmedLogin------");
        this.stopStatusPolling();

        const loginInfoResponse = await wechatService.getLoginInfo();
        this.token = loginInfoResponse.token;
        this.redirectUrl = loginInfoResponse.redirect_url;

        // 提取并保存cookies
        if (
          loginInfoResponse.headers &&
          loginInfoResponse.headers["set-cookie"]
        ) {
          const cookieStr = loginInfoResponse.headers["set-cookie"];
          this.cookies = this.parseCookieString(cookieStr);
          console.log(
            "✓ 已提取 cookies:",
            Object.keys(this.cookies).length,
            "个"
          );
        }

        this.currentStep = LoginStep.LOGIN_SUCCESS;

        const verifyResponse = await wechatService.verifyUserInfo(this.token);

        const redirectResponse = await wechatService.redirectLoginInfo(
          this.redirectUrl
        );
        this.userInfo = redirectResponse.userInfo;
        this.cookies = redirectResponse.cookies;
        this.token = redirectResponse.token; // 更新token（可能已更新）
        // 在应用设置了cookie和token后调用 getter，让所有请求都能自动携带
        api.setCookiesGetter("X-WX-Cookies", () => this.cookies);
        api.setTokenGetter("X-WX-Token", () => this.token);
        this.currentStep = LoginStep.REDIRECT_SUCCESS;
        this.loginComplete = true;

        // ✅ 保存到后端
        await this.saveUserInfoToLocalStorage();
      } catch (err: any) {
        console.error("登录完成流程失败:", err);
        this.error = err.message || "Failed to complete login";
        this.currentStep = LoginStep.ERROR;
        this.stopStatusPolling();
      }
    },

    reset() {
      this.stopStatusPolling();

      if (this.qrCodeUrl && this.qrCodeUrl.startsWith("blob:")) {
        URL.revokeObjectURL(this.qrCodeUrl);
      }

      this.sessionId = "";
      this.qrCodeUrl = "";
      this.qrCodeStatus = QRCodeStatus.WAITING;
      this.currentStep = LoginStep.INIT;
      this.error = null;
      this.token = "";
      this.redirectUrl = "";
      this.userInfo = null;
      this.cookies = {}; // 清除cookies
      this.loginComplete = false;
    },

    // 解析Cookie字符串
    parseCookieString(cookieStr: string): Record<string, any> {
      const cookies: Record<string, any> = {};
      if (!cookieStr) return cookies;

      const pairs = cookieStr.split(";");
      pairs.forEach((pair) => {
        const [key, value] = pair.trim().split("=");
        if (key && value) {
          cookies[key] = value;
        }
      });
      return cookies;
    },

    cleanup() {
      this.stopStatusPolling();

      this.createdBlobUrls.forEach((url) => {
        if (url && url.startsWith("blob:")) {
          URL.revokeObjectURL(url);
        }
      });
      this.createdBlobUrls = [];

      if (this.qrCodeUrl && this.qrCodeUrl.startsWith("blob:")) {
        URL.revokeObjectURL(this.qrCodeUrl);
      }
      this.qrCodeUrl = "";
    },
  },
});
