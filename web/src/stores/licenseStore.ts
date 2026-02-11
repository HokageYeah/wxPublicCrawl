import { defineStore } from "pinia";
import { ref, computed } from "vue";
import type { UserInfo, CardInfo } from "@/services/licenseService";
import { sessionService } from "@/services/sessionService";
import { getMyCards } from "@/services/licenseService";
import licenseRequest from "@/utils/licenseRequest";
import api from "@/utils/request"; // 导入主请求实例，用于设置全局权限请求头

/**
 * 卡密服务状态管理
 * 数据持久化通过 pinia-plugin-persistedstate 实现
 */
export const useLicenseStore = defineStore("license", () => {
  // 用户信息
  const userInfo = ref<UserInfo | null>(null);

  // 登录 Token
  const token = ref<string>("");

  // 是否已登录
  const isLoggedIn = ref<boolean>(false);

  // 卡密状态
  const licenseStatus = ref<string>("");

  // 用户卡密列表
  const cards = ref<CardInfo[]>([]);

  // 平台标识
  const PLATFORM = "license";

  // 设备ID
  const deviceId = ref<string>("");

  /**
   * 初始化：从后端加载会话
   */
  const initialize = async () => {
    try {
      console.log("正在从后端加载许可证会话...");
      const sessionResponse = await sessionService.loadSession(PLATFORM);
      const { getDeviceId } = await import('@/utils/fingerprint')
      deviceId.value = await getDeviceId()
      console.log("✓ 已获取设备指纹作为device_id", deviceId.value);

      if (sessionResponse.logged_in && sessionResponse.user_info) {
        userInfo.value = sessionResponse.user_info as UserInfo;
        token.value = sessionResponse.token || "";
        isLoggedIn.value = true;

        if (userInfo.value?.licenseStatus) {
          licenseStatus.value = userInfo.value.licenseStatus;
        }

        console.log("✓ 从后端恢复许可证登录状态", userInfo.value.username);

        // 设置请求头拦截器
        setupRequestInterceptor();

        // // 获取卡密信息
        // await fetchCards();
      }
    } catch (error) {
      console.error("加载许可证会话失败:", error);
    }
  };

  /**
   * 设置请求头拦截器，自动携带 Token
   * 同时设置主请求实例和 licenseRequest 实例
   */
  const setupRequestInterceptor = () => {
    // 为 licenseRequest 设置 Authorization 头
    licenseRequest.addCustomHeaderGetter(() => ({
      key: "Authorization",
      value: token.value ? `Bearer ${token.value}` : "",
    }));

    // 为主请求实例设置 Authorization 头（用于权限校验）
    api.addCustomHeaderGetter(() => ({
      key: "Authorization",
      value: token.value ? `Bearer ${token.value}` : "",
    }));

    // 为主请求实例设置 X-Device-Id 头（用于权限校验）
    // 只发送第一个卡密的设备ID（单个字符串）
    // 如果卡密没有 device_id 字段，则使用 card_id 作为设备标识
    api.addCustomHeaderGetter(() => {
      // let deviceId = "";
      if (cards.value && cards.value.length > 0) {
        // 只取第一个卡密的设备ID
        // const firstCard = cards.value[0];
        // deviceId = firstCard.device_id || String(firstCard.card_id);
        // 获取设备指纹作为device_id
        // const { getDeviceId } = await import('@/utils/fingerprint')
        // deviceId = await getDeviceId()
        // 9b1ea719e1ba482a27d45364d3c7f877
        console.log("✓ 已获取设备指纹作为device_id", deviceId.value);
      }
      return {
        key: "X-Device-Id",
        value: deviceId.value,
      };
    });

    console.log("✓ 已为主请求实例和 licenseRequest 设置权限请求头拦截器");
  };

  /**
   * 设置用户信息（不立即同步到后端）
   */
  const setUserInfo = async (info: UserInfo | null) => {
    userInfo.value = info;
    isLoggedIn.value = !!info;

    if (info?.licenseStatus) {
      licenseStatus.value = info.licenseStatus;
    }
    // 注意：这里不立即保存到后端，等待卡密信息获取后一起保存
  };

  /**
   * 设置登录 Token（不立即同步到后端）
   */
  const setToken = async (newToken: string) => {
    token.value = newToken;
    // 设置请求头拦截器，以便后续请求可以携带 token
    setupRequestInterceptor();
    // 注意：这里不立即保存到后端，等待用户信息和卡密信息一起保存
  };

  /**
   * 将当前状态保存到后端
   */
  const saveSessionToBackend = async () => {
    if (userInfo.value || token.value) {
      try {
        await sessionService.saveSession(
          userInfo.value || {},
          {}, // 许可证系统通常不需要额外的 cookies
          token.value,
          PLATFORM,
        );
        console.log("✓ 许可证会话已同步到后端");
      } catch (error) {
        console.error("同步许可证会话失败:", error);
      }
    }
  };

  /**
   * 设置卡密状态
   */
  const setLicenseStatus = (status: string) => {
    licenseStatus.value = status;
  };

  /**
   * 获取用户的卡密列表并保存到本地
   */
  const fetchCards = async () => {
    try {
      const response = await getMyCards();
      cards.value = response.cards || [];
      
      // 更新用户信息中的卡密状态
      if (userInfo.value) {
        userInfo.value.has_card = response.has_card;
        userInfo.value.cards = response.cards;
      }
      console.log("✓ 已获取用户卡密信息", cards.value.length, "张卡密");
    } catch (error) {
      console.error("获取卡密信息失败:", error);
    }
  };

  /**
   * 设置卡密列表
   */
  const setCards = (cardList: CardInfo[]) => {
    cards.value = cardList;
  };

  /**
   * 清除用户信息（登出）
   */
  const clearUserInfo = async () => {
    userInfo.value = null;
    token.value = "";
    isLoggedIn.value = false;
    licenseStatus.value = "";
    cards.value = [];

    try {
      await sessionService.clearSession(PLATFORM);
      console.log("✓ 后端许可证会话已清除");
    } catch (error) {
      console.error("清除后端许可证会话失败:", error);
    }
  };

  // 执行初始化
  initialize();

  return {
    userInfo,
    token,
    isLoggedIn,
    licenseStatus,
    cards,
    setUserInfo,
    setToken,
    setLicenseStatus,
    setCards,
    clearUserInfo,
    initialize,
    fetchCards,
    saveSessionToBackend,
  };
}, {
  persist: {
    key: 'license-store',
    paths: ['userInfo', 'token', 'isLoggedIn', 'licenseStatus', 'cards'],
  },
} as any);
