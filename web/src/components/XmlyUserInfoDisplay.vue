<template>
  <div class="card p-8 bg-gray-50 dark:bg-gray-800 shadow-md hover:shadow-lg transition-all duration-300 transform hover:-translate-y-1">
    <!-- User info header -->
    <div class="flex items-center mb-6">
      <div class="w-16 h-16 rounded-full overflow-hidden mr-4 bg-orange-500 flex items-center justify-center text-white text-2xl font-bold">
        {{ userInfo.mobileMask ? userInfo.mobileMask.charAt(0) : 'U' }}
      </div>

      <div>
        <h2 class="text-xl font-bold text-gray-900 dark:text-white">喜马拉雅用户</h2>
        <p class="text-gray-600 dark:text-gray-300 text-sm">{{ userInfo.mobileMask || 'Unknown User' }}</p>
      </div>
    </div>

    <!-- Login success message -->
    <div class="mb-6">
      <div class="flex items-center text-green-600 dark:text-green-400 mb-2">
        <div class="i-carbon-checkmark-filled mr-2"></div>
        <span class="font-medium">登录成功</span>
      </div>
      <p class="text-sm text-gray-600 dark:text-gray-400">您已成功使用喜马拉雅登录，可以开始使用系统功能。</p>
    </div>

    <!-- User details -->
    <div class="mb-6 bg-gray-100 dark:bg-gray-700 p-4 rounded-lg border border-gray-200 dark:border-gray-600">
      <h3 class="font-semibold mb-2 text-gray-900 dark:text-white">账号信息</h3>

      <div class="grid grid-cols-1 md:grid-cols-2 gap-3">
        <div class="flex items-center p-2 rounded bg-orange-50 dark:bg-gray-800 hover:bg-orange-100 dark:hover:bg-gray-750 transition-colors duration-200">
          <span class="text-gray-500 dark:text-gray-400 mr-2 min-w-20">用户ID:</span>
          <span class="text-gray-900 dark:text-white font-medium">{{ userInfo.uid }}</span>
        </div>

        <div class="flex items-center p-2 rounded bg-orange-50 dark:bg-gray-800 hover:bg-orange-100 dark:hover:bg-gray-750 transition-colors duration-200">
          <span class="text-gray-500 dark:text-gray-400 mr-2 min-w-20">手机号:</span>
          <span class="text-gray-900 dark:text-white font-medium">{{ userInfo.mobileMask }}</span>
        </div>

        <div v-if="userInfo.loginType" class="flex items-center p-2 rounded bg-orange-50 dark:bg-gray-800 hover:bg-orange-100 dark:hover:bg-gray-750 transition-colors duration-200">
          <span class="text-gray-500 dark:text-gray-400 mr-2 min-w-20">登录类型:</span>
          <span class="text-gray-900 dark:text-white font-medium">{{ userInfo.loginType }}</span>
        </div>

        <div v-if="userInfo.token" class="flex items-center p-2 rounded bg-orange-50 dark:bg-gray-800 hover:bg-orange-100 dark:hover:bg-gray-750 transition-colors duration-200">
          <span class="text-gray-500 dark:text-gray-400 mr-2 min-w-20">Token:</span>
          <span class="text-xs text-gray-900 dark:text-white font-medium truncate">{{ truncateToken(userInfo.token) }}</span>
        </div>

        <div v-if="userInfo.avatar" class="flex items-center p-2 rounded bg-orange-50 dark:bg-gray-800 hover:bg-orange-100 dark:hover:bg-gray-750 transition-colors duration-200">
          <span class="text-gray-500 dark:text-gray-400 mr-2 min-w-20">头像:</span>
          <span class="text-xs text-gray-900 dark:text-white font-medium truncate">{{ userInfo.avatar }}</span>
        </div>
      </div>
    </div>

    <!-- Actions -->
    <div class="flex justify-end space-x-3">
      <button @click="onLogout" class="px-4 py-2 rounded-md bg-gray-200 hover:bg-gray-300 dark:bg-gray-700 dark:hover:bg-gray-600 text-gray-700 dark:text-gray-300 transition-colors duration-200 flex items-center">
        <span class="i-carbon-logout mr-1"></span>
        退出登录
      </button>
      <button @click="onContinue" class="btn-primary bg-orange-500 hover:bg-orange-600 px-4 py-2 rounded-md hover:shadow-md transition-shadow duration-200">
        继续使用
      </button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { XmlyUserInfo } from '@/types/xmly';

defineProps<{
  userInfo: XmlyUserInfo;
}>();

const emit = defineEmits<{
  (e: 'continue'): void;
  (e: 'logout'): void;
}>();

const truncateToken = (token: string): string => {
  if (!token) return '';
  return token.length > 20 ? `${token.substring(0, 20)}...` : token;
};

const onContinue = () => {
  emit('continue');
};

const onLogout = () => {
  emit('logout');
};
</script>

<style scoped>
.min-w-20 {
  min-width: 5rem;
}
</style>
