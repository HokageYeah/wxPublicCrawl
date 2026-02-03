<template>
  <div class="default-home">
    <!-- 背景光效 -->
    <div class="glow-bg">
      <div class="glow-1"></div>
      <div class="glow-2"></div>
      <div class="glow-3"></div>
    </div>

    <!-- 主要内容区 -->
    <div class="content-wrapper">
      <!-- 品牌区域 -->
      <div class="brand-section">
        <div class="logo-container">
          <span class="i-carbon-cloud-service-management text-6xl text-blue-500"></span>
        </div>
        <h1 class="brand-title">
          WX公众号
          <span class="highlight">下载平台</span>
        </h1>
        <p class="brand-subtitle">
          专业的微信公众号内容采集与管理工具
        </p>
      </div>

      <!-- 功能特性 -->
      <div class="features-grid">
        <div class="feature-card">
          <div class="feature-icon">
            <span class="i-carbon-document-download text-2xl"></span>
          </div>
          <h3 class="feature-title">文章采集</h3>
          <p class="feature-desc">快速批量采集公众号文章，支持多种筛选条件</p>
        </div>

        <div class="feature-card">
          <div class="feature-icon">
            <span class="i-carbon-data-structured text-2xl"></span>
          </div>
          <h3 class="feature-title">数据管理</h3>
          <p class="feature-desc">完善的数据管理功能，支持导出和分类整理</p>
        </div>

        <div class="feature-card">
          <div class="feature-icon">
            <span class="i-carbon-save text-2xl"></span>
          </div>
          <h3 class="feature-title">本地存储</h3>
          <p class="feature-desc">文章内容本地存储，支持多种格式导出</p>
        </div>

        <div class="feature-card">
          <div class="feature-icon">
            <span class="i-carbon-speed-high text-2xl"></span>
          </div>
          <h3 class="feature-title">高效稳定</h3>
          <p class="feature-desc">采用先进的技术架构，确保采集效率</p>
        </div>
      </div>

      <!-- 登录/注册区域 -->
      <div v-if="false" class="auth-section">
        <p class="auth-hint">登录您的账户，开始使用全部功能</p>
        <div class="auth-buttons">
          <router-link to="/login" class="auth-btn primary">
            <span class="i-carbon-login text-lg"></span>
            <span>立即登录</span>
          </router-link>
          <router-link to="/register" class="auth-btn secondary">
            <span class="i-carbon-user-add text-lg"></span>
            <span>注册账户</span>
          </router-link>
        </div>
      </div>

      <!-- 统计信息 -->
      <div class="stats-section">
        <div class="stat-item">
          <span class="stat-number">1000+</span>
          <span class="stat-label">活跃用户</span>
        </div>
        <div class="stat-item">
          <span class="stat-number">50000+</span>
          <span class="stat-label">已采集文章</span>
        </div>
        <div class="stat-item">
          <span class="stat-number">99.9%</span>
          <span class="stat-label">服务可用性</span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
// 默认主页组件 - 未登录时显示
</script>

<style scoped>
.default-home {
  min-height: calc(100vh - 64px);
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #0f172a 0%, #1e293b 50%, #0f172a 100%);
  position: relative;
  overflow: hidden;
  padding: 2rem;
}

/* 背景光效 */
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
  top: -20%;
  left: -10%;
  width: 600px;
  height: 600px;
  background: radial-gradient(circle, rgba(59, 130, 246, 0.15) 0%, rgba(59, 130, 246, 0) 70%);
  border-radius: 50%;
  filter: blur(80px);
  animation: pulse 8s infinite alternate;
}

.glow-2 {
  position: absolute;
  bottom: -20%;
  right: -10%;
  width: 600px;
  height: 600px;
  background: radial-gradient(circle, rgba(99, 102, 241, 0.15) 0%, rgba(99, 102, 241, 0) 70%);
  border-radius: 50%;
  filter: blur(80px);
  animation: pulse 8s infinite alternate-reverse;
}

.glow-3 {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  width: 800px;
  height: 800px;
  background: radial-gradient(circle, rgba(16, 185, 129, 0.05) 0%, rgba(16, 185, 129, 0) 70%);
  border-radius: 50%;
  filter: blur(100px);
  animation: pulse 12s infinite alternate;
}

@keyframes pulse {
  0% {
    transform: scale(1);
    opacity: 0.5;
  }
  100% {
    transform: scale(1.1);
    opacity: 0.8;
  }
}

.content-wrapper {
  position: relative;
  z-index: 1;
  max-width: 1200px;
  width: 100%;
}

/* 品牌区域 */
.brand-section {
  text-align: center;
  margin-bottom: 4rem;
}

.logo-container {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 100px;
  height: 100px;
  background: linear-gradient(135deg, rgba(59, 130, 246, 0.2), rgba(99, 102, 241, 0.2));
  border-radius: 24px;
  margin-bottom: 1.5rem;
  box-shadow: 0 8px 32px rgba(59, 130, 246, 0.3);
  animation: float 6s ease-in-out infinite;
}

@keyframes float {
  0%, 100% {
    transform: translateY(0);
  }
  50% {
    transform: translateY(-10px);
  }
}

.brand-title {
  font-size: 3rem;
  font-weight: 800;
  color: white;
  margin-bottom: 1rem;
  letter-spacing: -0.02em;
}

.brand-title .highlight {
  background: linear-gradient(135deg, #3b82f6, #6366f1);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.brand-subtitle {
  font-size: 1.25rem;
  color: #94a3b8;
  max-width: 600px;
  margin: 0 auto;
}

/* 功能特性 */
.features-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 1.5rem;
  margin-bottom: 4rem;
}

.feature-card {
  background: rgba(255, 255, 255, 0.05);
  backdrop-filter: blur(10px);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 16px;
  padding: 2rem;
  transition: all 0.3s ease;
}

.feature-card:hover {
  transform: translateY(-5px);
  background: rgba(255, 255, 255, 0.08);
  border-color: rgba(59, 130, 246, 0.3);
  box-shadow: 0 20px 40px rgba(0, 0, 0, 0.3);
}

.feature-icon {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 56px;
  height: 56px;
  background: linear-gradient(135deg, rgba(59, 130, 246, 0.2), rgba(99, 102, 241, 0.2));
  border-radius: 14px;
  margin-bottom: 1rem;
  color: #60a5fa;
}

.feature-title {
  font-size: 1.25rem;
  font-weight: 600;
  color: white;
  margin-bottom: 0.5rem;
}

.feature-desc {
  color: #94a3b8;
  font-size: 0.95rem;
  line-height: 1.6;
}

/* 登录注册区域 */
.auth-section {
  text-align: center;
  margin-bottom: 3rem;
}

.auth-hint {
  color: #94a3b8;
  margin-bottom: 1.5rem;
  font-size: 1.1rem;
}

.auth-buttons {
  display: flex;
  gap: 1rem;
  justify-content: center;
  flex-wrap: wrap;
}

.auth-btn {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.875rem 2rem;
  border-radius: 12px;
  font-size: 1rem;
  font-weight: 600;
  text-decoration: none;
  transition: all 0.3s ease;
  cursor: pointer;
}

.auth-btn.primary {
  background: linear-gradient(135deg, #3b82f6, #6366f1);
  color: white;
  border: none;
  box-shadow: 0 4px 20px rgba(59, 130, 246, 0.4);
}

.auth-btn.primary:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 30px rgba(59, 130, 246, 0.5);
}

.auth-btn.secondary {
  background: rgba(255, 255, 255, 0.1);
  color: white;
  border: 1px solid rgba(255, 255, 255, 0.2);
}

.auth-btn.secondary:hover {
  background: rgba(255, 255, 255, 0.15);
  border-color: rgba(255, 255, 255, 0.3);
  transform: translateY(-2px);
}

/* 统计区域 */
.stats-section {
  display: flex;
  justify-content: center;
  gap: 4rem;
  flex-wrap: wrap;
}

.stat-item {
  text-align: center;
}

.stat-number {
  display: block;
  font-size: 2.5rem;
  font-weight: 800;
  background: linear-gradient(135deg, #3b82f6, #60a5fa);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.stat-label {
  color: #94a3b8;
  font-size: 0.95rem;
}

/* 响应式 */
@media (max-width: 768px) {
  .brand-title {
    font-size: 2rem;
  }

  .features-grid {
    grid-template-columns: 1fr;
  }

  .stats-section {
    gap: 2rem;
  }

  .stat-number {
    font-size: 2rem;
  }
}
</style>
