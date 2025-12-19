<template>
  <div class="min-h-screen flex flex-col">
    <header class="bg-black shadow-sm sticky top-0 z-50">
      <div class="container mx-auto px-4 h-16 flex items-center justify-between">
        <div class="flex items-center gap-2">
            <span class="i-carbon-cloud-service-management text-blue-600 text-2xl"></span>
            <h1 class="text-lg font-bold bg-gradient-to-r from-blue-600 to-blue-800 bg-clip-text text-transparent">WX公众号下载平台</h1>
        </div>
        
        <div v-if="wechatStore.isLoggedIn" class="flex items-center gap-4">
            <div class="hidden md:flex items-center text-sm text-gray-500 bg-gray-100 px-3 py-1.5 rounded-full">
                <span class="i-carbon-user mr-1.5 text-gray-400"></span>
                <span>{{ wechatStore.userInfo?.nick_name || '已登录用户' }}</span>
            </div>
            <button 
                @click="handleLogout" 
                class="flex items-center gap-1.5 px-3 py-1.5 text-sm font-medium text-gray-600 hover:text-red-600 hover:bg-red-50 rounded-lg transition-colors"
                title="退出登录"
            >
                <span class="i-carbon-logout"></span>
                <span>退出</span>
            </button>
        </div>
      </div>
    </header>
    
    <main class="flex-1 transition-all duration-300">
      <RouterView />
    </main>
    
    <footer class="py-6 mt-auto sticky bottom-0 bg-black z-50">
        <div class="container mx-auto px-4 text-center text-gray-400 text-xs">
            <p>&copy; {{ new Date().getFullYear() }} WX Public Crawl Platform. All rights reserved.</p>
        </div>
    </footer>
  </div>
</template>

<script setup lang="ts">
import { useRouter } from 'vue-router';
import { useWechatLoginStore } from '@/stores/wechatLoginStore';

const router = useRouter();
const wechatStore = useWechatLoginStore();

const handleLogout = () => {
    if (confirm('确定要退出登录吗？')) {
        wechatStore.logout();
        router.push('/');
    }
};
</script> 