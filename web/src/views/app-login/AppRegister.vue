<template>
  <div class="register-container">
    <!-- 背景光效 -->
    <div class="glow-bg">
      <div class="glow-1"></div>
      <div class="glow-2"></div>
    </div>

    <!-- 注册卡片 -->
    <div class="register-card">
      <div class="register-header">
        <div class="logo">
          <svg viewBox="0 0 24 24" class="logo-icon">
            <path
              fill="currentColor"
              d="M12,2A10,10 0 0,1 22,12A10,10 0 0,1 12,22A10,10 0 0,1 2,12A10,10 0 0,1 12,2M12,4A8,8 0 0,0 4,12A8,8 0 0,0 12,20A8,8 0 0,0 20,12A8,8 0 0,0 12,4M15,10.5V11.5A1.5,1.5 0 0,1 16.5,13A1.5,1.5 0 0,1 15,14.5V15.5A1.5,1.5 0 0,1 13.5,17H12.5V18.5H11.5V17H10.5A1.5,1.5 0 0,1 9,15.5V14.5A1.5,1.5 0 0,1 7.5,13A1.5,1.5 0 0,1 9,11.5V10.5A1.5,1.5 0 0,1 10.5,9H11.5V7.5H12.5V9H13.5A1.5,1.5 0 0,1 15,10.5M13.5,11.5V10.5H10.5V11.5H13.5M10.5,14.5V15.5H13.5V14.5H10.5Z"
            />
          </svg>
        </div>
        <h1 class="title">创建新账户</h1>
        <p class="subtitle">加入我们，开始您的智能抓取之旅</p>
      </div>

      <form @submit.prevent="handleRegister" class="register-form">
        <div class="form-group">
          <div class="input-wrapper">
            <input
              v-model="registerForm.username"
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
              v-model="registerForm.password"
              :type="showPassword ? 'text' : 'password'"
              placeholder="密码"
              required
              :disabled="loading"
              class="stylish-input"
            />
            <span class="input-icon">🔒</span>
            <button
              type="button"
              class="eye-btn"
              @click="showPassword = !showPassword"
              tabindex="-1"
            >
              {{ showPassword ? "👁️" : "👁️‍🗨️" }}
            </button>
          </div>
        </div>

        <div class="form-group">
          <div class="input-wrapper">
            <input
              v-model="confirmPassword"
              :type="showConfirmPassword ? 'text' : 'password'"
              placeholder="确认密码"
              required
              :disabled="loading"
              class="stylish-input"
            />
            <span class="input-icon">🛡️</span>
            <button
              type="button"
              class="eye-btn"
              @click="showConfirmPassword = !showConfirmPassword"
              tabindex="-1"
            >
              {{ showConfirmPassword ? "👁️" : "👁️‍🗨️" }}
            </button>
          </div>
        </div>

        <button type="submit" class="submit-btn" :disabled="loading">
          <span v-if="!loading">立即注册</span>
          <div v-else class="loader"></div>
        </button>
      </form>

      <div class="login-footer">
        已有账户？
        <router-link to="/login" class="link">前往登录</router-link>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive } from "vue";
import { useRouter } from "vue-router";
import { register } from "@/services/licenseService";
import { useLicenseStore } from "@/stores/licenseStore";

const router = useRouter();
const licenseStore = useLicenseStore();

const registerForm = reactive({
  username: "",
  password: "",
});

const confirmPassword = ref("");
const showPassword = ref(false);
const showConfirmPassword = ref(false);
const loading = ref(false);

const handleRegister = async () => {
  if (registerForm.password !== confirmPassword.value) {
    alert("两次输入的密码不一致");
    return;
  }

  loading.value = true;
  try {
    const result = await register({
      username: registerForm.username,
      password: registerForm.password,
    });

    // 注册成功通常也会自动登录，返回 token 和 userInfo
    await licenseStore.setToken(result.token);
    await licenseStore.setUserInfo(result.userInfo);

    alert("注册成功！");
    router.push("/");
  } catch (error: any) {
    alert("注册失败: " + (error.message || "未知错误"));
  } finally {
    loading.value = false;
  }
};
</script>

<style scoped>
.register-container {
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
  left: -10%;
  width: 600px;
  height: 600px;
  background: radial-gradient(
    circle,
    rgba(16, 185, 129, 0.15) 0%,
    rgba(16, 185, 129, 0) 70%
  );
  border-radius: 50%;
  filter: blur(60px);
  animation: pulse 8s infinite alternate;
}

.glow-2 {
  position: absolute;
  bottom: -10%;
  right: -10%;
  width: 600px;
  height: 600px;
  background: radial-gradient(
    circle,
    rgba(99, 102, 241, 0.15) 0%,
    rgba(99, 102, 241, 0) 70%
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

/* 注册卡片 */
.register-card {
  width: 100%;
  max-width: 480px;
  padding: 40px;
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

.register-card:hover {
  transform: translateY(-5px);
  border-color: rgba(255, 255, 255, 0.2);
}

.register-header {
  text-align: center;
  margin-bottom: 32px;
}

.logo-icon {
  width: 56px;
  height: 56px;
  color: #10b981;
  margin-bottom: 16px;
  filter: drop-shadow(0 0 15px rgba(16, 185, 129, 0.5));
}

.title {
  font-size: 26px;
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
  font-size: 14px;
}

/* 表单样式 */
.register-form {
  display: flex;
  flex-direction: column;
  gap: 16px;
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
  padding: 12px 16px 12px 48px;
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
  border-color: #10b981;
  box-shadow: 0 0 0 4px rgba(16, 185, 129, 0.1);
}

.input-icon {
  position: absolute;
  left: 16px;
  font-size: 18px;
  opacity: 0.6;
}

.eye-btn {
  position: absolute;
  right: 12px;
  background: none;
  border: none;
  color: #fff;
  cursor: pointer;
  opacity: 0.6;
  font-size: 18px;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: opacity 0.2s;
  padding: 4px;
}

.eye-btn:hover {
  opacity: 1;
}

/* 条款样式 */
.form-terms {
  margin: 4px 0;
  font-size: 13px;
}

.terms-label {
  display: flex;
  align-items: flex-start;
  gap: 10px;
  cursor: pointer;
  color: #94a3b8;
  line-height: 1.4;
}

.terms-label input {
  margin-top: 3px;
  accent-color: #10b981;
}

.terms-label a {
  color: #10b981;
  text-decoration: none;
}

.terms-label a:hover {
  text-decoration: underline;
}

/* 按钮样式 */
.submit-btn {
  margin-top: 8px;
  padding: 12px;
  background: linear-gradient(135deg, #10b981 0%, #3b82f6 100%);
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
  box-shadow: 0 10px 15px -3px rgba(16, 185, 129, 0.3);
}

.submit-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 20px 25px -5px rgba(16, 185, 129, 0.4);
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

.login-footer {
  text-align: center;
  margin-top: 24px;
  font-size: 14px;
  color: #94a3b8;
}

.link {
  color: #10b981;
  text-decoration: none;
  font-weight: 500;
  margin-left: 4px;
}

.link:hover {
  text-decoration: underline;
}

/* 响应式适配 */
@media (max-width: 480px) {
  .register-card {
    padding: 32px 20px;
    border-radius: 0;
    backdrop-filter: none;
    background: #0f172a;
    border: none;
  }
}
</style>
