<template>
  <div class="login-container">
    <!-- 背景光效 -->
    <div class="glow-bg">
      <div class="glow-1"></div>
      <div class="glow-2"></div>
    </div>

    <!-- 登录卡片 -->
    <div class="login-card">
      <div class="login-header">
        <div class="logo">
          <svg viewBox="0 0 24 24" class="logo-icon">
            <path
              fill="currentColor"
              d="M12,1L3,5V11C3,16.55 6.84,21.74 12,23C17.16,21.74 21,16.55 21,11V5L12,1M12,11.5A2.5,2.5 0 0,1 14.5,14C14.5,15.03 13.87,15.91 13,16.29V18H11V16.29C10.13,15.91 9.5,15.03 9.5,14A2.5,2.5 0 0,1 12,11.5Z"
            />
          </svg>
        </div>
        <h1 class="title">身份验证</h1>
        <p class="subtitle">欢迎回来，请登录您的账户</p>
      </div>

      <form @submit.prevent="handleLogin" class="login-form">
        <div class="form-group">
          <div class="input-wrapper">
            <select
              v-model="loginForm.app_key"
              required
              :disabled="loading"
              class="stylish-input select-input"
            >
              <option value="" disabled selected>选择应用</option>
              <option
                v-for="app in appList"
                :key="app.app_key"
                :value="app.app_key"
              >
                {{ app.app_name }}
              </option>
            </select>
            <span class="input-icon">📱</span>
          </div>
        </div>

        <div class="form-group">
          <div class="input-wrapper">
            <input
              v-model="loginForm.username"
              type="text"
              placeholder="用户名"
              required
              :disabled="loading"
              class="stylish-input"
            />
            <span class="input-icon">👤</span>
          </div>
        </div>

        <div class="form-group">
          <div class="input-wrapper">
            <input
              v-model="loginForm.password"
              type="password"
              placeholder="密码"
              required
              :disabled="loading"
              class="stylish-input"
            />
            <span class="input-icon">🔒</span>
          </div>
        </div>

        <div class="form-options">
          <label class="remember-me">
            <input type="checkbox" v-model="rememberMe" />
            <span>记住我</span>
          </label>
        </div>

        <button type="submit" class="submit-btn" :disabled="loading">
          <span v-if="!loading">立即登录</span>
          <div v-else class="loader"></div>
        </button>
      </form>

      <div class="register-footer">
        还没有账户？
        <router-link to="/register" class="link">立即注册</router-link>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from "vue";
import { useRouter } from "vue-router";
import {
  login,
  getPublicAppList,
  type AppSimpleInfo,
} from "@/services/licenseService";
import { useLicenseStore } from "@/stores/licenseStore";
import { useAppStore } from "@/stores/appStore";
// 注意：项目可能没有全局通知组件，这里使用简单的 alert 或如果是 Ant Design/Element 则需要引入
// 暂且使用原生的或假设有 message 系统

const router = useRouter();
const licenseStore = useLicenseStore();
const appStore = useAppStore();

const loginForm = reactive({
  username: "",
  password: "",
  app_key: "",
});

const appList = ref<AppSimpleInfo[]>([]);
const loading = ref(false);
const rememberMe = ref(false);

const fetchAppList = async () => {
  try {
    const response = await getPublicAppList();
    appList.value = response.apps;
    // 如果只有一个应用，默认选中
    if (appList.value.length === 1) {
      loginForm.app_key = appList.value[0].app_key;
    }
  } catch (error) {
    console.error("加载应用列表失败:", error);
  }
};

onMounted(() => {
  fetchAppList();
  // 初始化应用信息
  appStore.initialize();
});

const handleLogin = async () => {
  loading.value = true;
  try {
    // 获取设备指纹作为device_id
    const { getDeviceId } = await import('@/utils/fingerprint')
    const deviceId = await getDeviceId()
    const result = await login({
      username: loginForm.username,
      password: loginForm.password,
      app_key: loginForm.app_key,
      device_id: deviceId,
    });

    // 1. 先设置 Token（需要 token 才能调用卡密接口）
    await licenseStore.setToken(result.token);
    
    // 2. 设置基础用户信息
    await licenseStore.setUserInfo({
      role: result.role,
      has_card: result.has_card,
      user_status: result.user_status,
      username: result.username,
    });

    // 3. 保存应用信息到独立的 store
    const app_info = appList.value.find(app => app.app_key === loginForm.app_key);
    if (app_info) {
      await appStore.setCurrentApp(app_info as AppSimpleInfo);
    }

    // 4. 获取卡密信息并合并到用户信息中，然后统一保存到本地
    await licenseStore.fetchCards();

    // 5. 保存会话到后端
    await licenseStore.saveSessionToBackend();

    // 登录成功跳转
    // 你可以根据需要调整跳转路径
    router.push("/");
  } catch (error: any) {
    alert("登录失败: " + (error.message || "未知错误"));
  } finally {
    loading.value = false;
  }
};
</script>

<style scoped>
.login-container {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #0f172a;
  position: relative;
  overflow: hidden;
  font-family:
    "Inter",
    -apple-system,
    system-ui,
    sans-serif;
  color: #fff;
}

/* 玻璃拟态背景光效 */
.glow-bg {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  pointer-events: none;
}

.glow-1 {
  position: absolute;
  top: -10%;
  right: -10%;
  width: 600px;
  height: 600px;
  background: radial-gradient(
    circle,
    rgba(99, 102, 241, 0.2) 0%,
    rgba(99, 102, 241, 0) 70%
  );
  border-radius: 50%;
  filter: blur(60px);
  animation: pulse 8s infinite alternate;
}

.glow-2 {
  position: absolute;
  bottom: -10%;
  left: -10%;
  width: 600px;
  height: 600px;
  background: radial-gradient(
    circle,
    rgba(168, 85, 247, 0.2) 0%,
    rgba(168, 85, 247, 0) 70%
  );
  border-radius: 50%;
  filter: blur(60px);
  animation: pulse 8s infinite alternate-reverse;
}

@keyframes pulse {
  from {
    transform: scale(1);
    opacity: 0.5;
  }
  to {
    transform: scale(1.2);
    opacity: 0.8;
  }
}

/* 登录卡片 */
.login-card {
  width: 100%;
  max-width: 440px;
  padding: 48px;
  background: rgba(30, 41, 59, 0.7);
  backdrop-filter: blur(20px);
  -webkit-backdrop-filter: blur(20px);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 24px;
  box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.5);
  z-index: 1;
  transform: translateY(0);
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

.login-card:hover {
  transform: translateY(-5px);
  border-color: rgba(255, 255, 255, 0.2);
}

.login-header {
  text-align: center;
  margin-bottom: 40px;
}

.logo-icon {
  width: 64px;
  height: 64px;
  color: #6366f1;
  margin-bottom: 16px;
  filter: drop-shadow(0 0 15px rgba(99, 102, 241, 0.5));
}

.title {
  font-size: 28px;
  font-weight: 700;
  letter-spacing: -0.025em;
  margin-bottom: 8px;
  background: linear-gradient(to right, #fff, #94a3b8);
  -webkit-background-clip: text;
  background-clip: text;
  -webkit-text-fill-color: transparent;
}

.subtitle {
  color: #94a3b8;
  font-size: 15px;
}

/* 表单样式 */
.login-form {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.form-group {
  position: relative;
}

.input-wrapper {
  position: relative;
  display: flex;
  align-items: center;
}

.stylish-input {
  width: 100%;
  padding: 14px 16px 14px 48px;
  background: rgba(15, 23, 42, 0.6);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 12px;
  color: #fff;
  font-size: 15px;
  transition: all 0.2s;
  outline: none;
}

.stylish-input:focus {
  background: rgba(15, 23, 42, 0.8);
  border-color: #6366f1;
  box-shadow: 0 0 0 4px rgba(99, 102, 241, 0.1);
}

.select-input {
  appearance: none;
  cursor: pointer;
}

.select-input option {
  background: #1e293b;
  color: #fff;
}

.input-icon {
  position: absolute;
  left: 16px;
  font-size: 18px;
  opacity: 0.6;
}

/* 选项样式 */
.form-options {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 14px;
}

.remember-me {
  display: flex;
  align-items: center;
  gap: 8px;
  cursor: pointer;
  color: #94a3b8;
}

.remember-me input {
  accent-color: #6366f1;
}

.forgot-link {
  color: #6366f1;
  text-decoration: none;
  transition: opacity 0.2s;
}

.forgot-link:hover {
  opacity: 0.8;
}

/* 按钮样式 */
.submit-btn {
  margin-top: 10px;
  padding: 14px;
  background: linear-gradient(135deg, #6366f1 0%, #a855f7 100%);
  border: none;
  border-radius: 12px;
  color: white;
  font-size: 16px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 10px 15px -3px rgba(99, 102, 241, 0.3);
}

.submit-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 20px 25px -5px rgba(99, 102, 241, 0.4);
  filter: brightness(1.1);
}

.submit-btn:active {
  transform: translateY(0);
}

.submit-btn:disabled {
  opacity: 0.7;
  cursor: not-allowed;
  transform: none;
}

/* 加载动画 */
.loader {
  width: 20px;
  height: 20px;
  border: 2px solid rgba(255, 255, 255, 0.3);
  border-top-color: #fff;
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}

.register-footer {
  text-align: center;
  margin-top: 32px;
  font-size: 14px;
  color: #94a3b8;
}

.link {
  color: #6366f1;
  text-decoration: none;
  font-weight: 500;
  margin-left: 4px;
}

.link:hover {
  text-decoration: underline;
}

/* 响应式适配 */
@media (max-width: 480px) {
  .login-card {
    padding: 32px 24px;
    border-radius: 0;
    backdrop-filter: none;
    background: #0f172a;
    border: none;
  }
}
</style>
