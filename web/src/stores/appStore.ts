import { defineStore } from "pinia";
import { ref, computed } from "vue";
import type { AppSimpleInfo } from "@/services/licenseService";
import { sessionService } from "@/services/sessionService";

/**
 * 当前登录应用信息管理
 * 用于存储用户当前选择登录的应用信息
 * 使用 pinia-plugin-persistedstate 实现持久化
 */
export const useAppStore = defineStore("app", () => {
  // 当前选中的应用信息
  const currentApp = ref<AppSimpleInfo | null>(null);

  // 平台标识
  const PLATFORM = "app";

  /**
   * 初始化：从后端加载应用信息
   */
  const initialize = async () => {
    try {
      console.log("正在从后端加载应用信息...");
      const sessionResponse = await sessionService.loadSession(PLATFORM);
      debugger
      if (sessionResponse.logged_in && sessionResponse.app_info) {
        currentApp.value = sessionResponse.app_info as AppSimpleInfo;
        console.log("✓ 从后端恢复应用登录状态", currentApp.value.app_name);
      }
    } catch (error) {
      console.error("加载应用信息失败:", error);
    }
  };

  /**
   * 设置当前应用信息并保存到后端
   */
  const setCurrentApp = async (app: AppSimpleInfo | null) => {
    currentApp.value = app;

    if (app) {
      await saveSessionToBackend();
      console.log("✓ 应用信息已保存", app.app_name);
    }
  };

  /**
   * 将当前状态保存到后端
   */
  const saveSessionToBackend = async () => {
    if (currentApp.value) {
      try {
        // 保存应用信息到后端会话
        await sessionService.saveSession(
          {},
          {},
          "",
          PLATFORM,
          currentApp.value,
        );
        console.log("✓ 应用会话已同步到后端");
      } catch (error) {
        console.error("同步应用会话失败:", error);
      }
    }
  };

  /**
   * 清除应用信息
   */
  const clearCurrentApp = async () => {
    currentApp.value = null;

    try {
      await sessionService.clearSession(PLATFORM);
      console.log("✓ 后端应用会话已清除");
    } catch (error) {
      console.error("清除后端应用会话失败:", error);
    }
  };

  /**
   * 获取应用名称显示
   */
  const getAppDisplayName = computed(() => {
    if (!currentApp.value) return "未选择应用";
    return currentApp.value.app_name;
  });

  /**
   * 检查应用是否有效
   */
  const isAppValid = computed(() => {
    if (!currentApp.value) return false;
    return currentApp.value.app_status === "active";
  });

  // 执行初始化
  initialize();

  return {
    currentApp,
    isAppValid,
    getAppDisplayName,
    setCurrentApp,
    clearCurrentApp,
    initialize,
  };
}, {
  persist: {
    key: 'app-store',
    paths: ['currentApp'],
  },
} as any);
