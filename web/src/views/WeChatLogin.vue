<template>
  <div class="max-w-2xl mx-auto py-8">
    <h1 class="text-2xl font-bold mb-8 text-center">微信扫码登录</h1>
    
    <div class="grid grid-cols-1 md:grid-cols-1 gap-8">
      <!-- Loading state -->
      <div v-if="wechatStore.isLoading" class="card p-12 flex justify-center items-center">
        <LoadingSpinner :label="loadingLabel" />
      </div>
      
      <!-- Error state -->
      <div v-else-if="wechatStore.error" class="card p-8">
        <div class="flex items-center text-error mb-4">
          <div class="i-carbon-warning-filled mr-2"></div>
          <span class="text-lg font-semibold">登录过程中出现错误</span>
        </div>
        <p class="mb-4 text-sm">{{ wechatStore.error }}</p>
        <button @click="restart" class="btn-primary">重试</button>
      </div>
      
      <!-- Login success state -->
      <div v-else-if="wechatStore.loginComplete && wechatStore.userInfo" class="col-span-1 md:col-span-1">
        <UserInfoDisplay 
          :user-info="wechatStore.userInfo" 
          @continue="onContinue"
          @logout="onLogout"
        />
        
        <!-- 添加一个用于调试的区域，可选 -->
        <div class="mt-4 card p-4 bg-gray-50 dark:bg-gray-800 hover:shadow-lg transition-all duration-300 transform hover:-translate-y-1">
          <details class="group">
            <summary class="cursor-pointer text-sm text-gray-700 dark:text-gray-300 font-medium flex items-center">
              <span class="i-carbon-view mr-2"></span>
              <span>查看完整用户数据</span>
              <span class="ml-2 transition-transform duration-300 group-open:rotate-180">
                <span class="i-carbon-chevron-down"></span>
              </span>
            </summary>
            <pre class="mt-3 text-xs overflow-auto bg-blue-50 dark:bg-gray-700 p-3 rounded-md shadow-inner border border-gray-200 dark:border-gray-600 text-gray-800 dark:text-gray-200">{{ JSON.stringify(wechatStore.userInfo, null, 2) }}</pre>
          </details>
        </div>
      </div>
      
      <!-- QR code login state -->
      <div v-else class="col-span-1 md:col-span-1">
        <QRCodeDisplay
          :qr-code-url="wechatStore.qrCodeUrl"
          :status="wechatStore.qrCodeStatus"
          :status-text="wechatStore.qrCodeStateText"
          :error-message="wechatStore.error"
          @refresh="restart"
        />
        
        <!-- Login steps -->
        <div class="card mt-8 p-6">
          <h3 class="text-lg font-semibold mb-4">登录步骤</h3>
          <ol class="space-y-3">
            <li class="flex items-center" :class="{ 'text-primary': wechatStore.currentStep === LoginStep.INIT || completedSteps.includes(LoginStep.INIT) }">
              <div class="w-6 h-6 rounded-full flex items-center justify-center mr-2 border" :class="stepStyle(LoginStep.INIT)">
                {{ completedSteps.includes(LoginStep.INIT) ? '✓' : '1' }}
              </div>
              <span>初始化登录流程</span>
            </li>
            <li class="flex items-center" :class="{ 'text-primary': wechatStore.currentStep === LoginStep.QRCODE_GENERATED || completedSteps.includes(LoginStep.QRCODE_GENERATED) }">
              <div class="w-6 h-6 rounded-full flex items-center justify-center mr-2 border" :class="stepStyle(LoginStep.QRCODE_GENERATED)">
                {{ completedSteps.includes(LoginStep.QRCODE_GENERATED) ? '✓' : '2' }}
              </div>
              <span>生成二维码</span>
            </li>
            <li class="flex items-center" :class="{ 'text-primary': wechatStore.currentStep === LoginStep.QRCODE_SCANNED || completedSteps.includes(LoginStep.QRCODE_SCANNED) }">
              <div class="w-6 h-6 rounded-full flex items-center justify-center mr-2 border" :class="stepStyle(LoginStep.QRCODE_SCANNED)">
                {{ completedSteps.includes(LoginStep.QRCODE_SCANNED) ? '✓' : '3' }}
              </div>
              <span>扫描二维码</span>
            </li>
            <li class="flex items-center" :class="{ 'text-primary': wechatStore.currentStep === LoginStep.QRCODE_CONFIRMED || completedSteps.includes(LoginStep.QRCODE_CONFIRMED) }">
              <div class="w-6 h-6 rounded-full flex items-center justify-center mr-2 border" :class="stepStyle(LoginStep.QRCODE_CONFIRMED)">
                {{ completedSteps.includes(LoginStep.QRCODE_CONFIRMED) ? '✓' : '4' }}
              </div>
              <span>确认登录</span>
            </li>
            <li class="flex items-center" :class="{ 'text-primary': wechatStore.currentStep === LoginStep.LOGIN_SUCCESS || completedSteps.includes(LoginStep.LOGIN_SUCCESS) }">
              <div class="w-6 h-6 rounded-full flex items-center justify-center mr-2 border" :class="stepStyle(LoginStep.LOGIN_SUCCESS)">
                {{ completedSteps.includes(LoginStep.LOGIN_SUCCESS) ? '✓' : '5' }}
              </div>
              <span>登录成功</span>
            </li>
          </ol>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, onUnmounted } from 'vue';
import { useRouter } from 'vue-router';
import { useWechatLoginStore } from '@/stores/wechatLoginStore';
import { LoginStep } from '@/types/wechat';
import QRCodeDisplay from '@/components/QRCodeDisplay.vue';
import LoadingSpinner from '@/components/LoadingSpinner.vue';
import UserInfoDisplay from '@/components/UserInfoDisplay.vue';

const wechatStore = useWechatLoginStore();

// 不再需要解构store值，直接使用store实例

// 移除watch块

// Computed properties
const loadingLabel = computed(() => {
  switch (wechatStore.currentStep) {
    case LoginStep.PRELOGIN:
      return '正在初始化登录...';
    case LoginStep.STARTLOGIN:
      return '正在获取二维码...';
    case LoginStep.WEBREPORT:
      return '正在准备登录环境...';
    default:
      return '加载中...';
  }
});

// 添加一个辅助函数来比较步骤顺序
const getStepOrder = (step: LoginStep): number => {
  const orderMap: Record<LoginStep, number> = {
    [LoginStep.INIT]: 0,
    [LoginStep.PRELOGIN]: 1,
    [LoginStep.STARTLOGIN]: 2,
    [LoginStep.WEBREPORT]: 3,
    [LoginStep.QRCODE_GENERATED]: 4,
    [LoginStep.QRCODE_SCANNED]: 5,
    [LoginStep.QRCODE_CONFIRMED]: 6,
    [LoginStep.LOGIN_SUCCESS]: 7,
    [LoginStep.VERIFY_SUCCESS]: 8,
    [LoginStep.REDIRECT_SUCCESS]: 9,
    [LoginStep.ERROR]: -1
  };
  return orderMap[step];
};

// 使用辅助函数比较步骤
const isStepCompleted = (step: LoginStep): boolean => {
  return getStepOrder(wechatStore.currentStep) > getStepOrder(step);
};

const completedSteps = computed(() => {
  const steps: LoginStep[] = [];
  
  if (wechatStore.currentStep === LoginStep.QRCODE_GENERATED || isStepCompleted(LoginStep.QRCODE_GENERATED)) {
    steps.push(LoginStep.INIT);
  }
  
  if (wechatStore.currentStep === LoginStep.QRCODE_SCANNED || isStepCompleted(LoginStep.QRCODE_SCANNED)) {
    steps.push(LoginStep.QRCODE_GENERATED);
  }
  
  if (wechatStore.currentStep === LoginStep.QRCODE_CONFIRMED || isStepCompleted(LoginStep.QRCODE_CONFIRMED)) {
    steps.push(LoginStep.QRCODE_SCANNED);
  }
  
  if (wechatStore.currentStep === LoginStep.LOGIN_SUCCESS || isStepCompleted(LoginStep.LOGIN_SUCCESS)) {
    steps.push(LoginStep.QRCODE_CONFIRMED);
  }
  
  if (wechatStore.currentStep === LoginStep.VERIFY_SUCCESS || isStepCompleted(LoginStep.VERIFY_SUCCESS)) {
    steps.push(LoginStep.LOGIN_SUCCESS);
  }
  
  return steps;
});

// Methods
const stepStyle = (step: LoginStep) => {
  if (completedSteps.value.includes(step)) {
    return 'bg-primary text-white border-primary';
  }
  
  if (wechatStore.currentStep === step) {
    return 'border-primary text-primary';
  }
  
  return 'border-gray-600 text-gray-400';
};

const restart = () => {
  wechatStore.reset();
  wechatStore.startLoginFlow();
};

const router = useRouter();

const onContinue = () => {
  // Handle the continue action after successful login
  // This could redirect to another page or trigger a callback
  console.log('Login complete, redirecting to search...');
  router.push('/search');
};

const onLogout = () => {
  // 处理退出登录
  wechatStore.logout();
  console.log('用户已退出登录');
};

// Lifecycle hooks
onMounted(() => {
  // 初始化用户状态 - 检查本地存储
  wechatStore.initialize();
  
  // 如果用户未登录，则启动登录流程
  if (!wechatStore.isLoggedIn) {
    console.log('WeChatLogin组件已挂载，启动登录流程');
    wechatStore.startLoginFlow();
  } else {
    console.log('用户已登录，无需启动登录流程');
  }
});

onUnmounted(() => {
  // Clean up when the component is unmounted
  console.log('WeChatLogin组件已卸载，清理资源');
  wechatStore.cleanup();
});
</script> 