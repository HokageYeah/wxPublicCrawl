<template>
  <div class="min-h-screen flex flex-col">
    <header class="bg-black shadow-sm sticky top-0 z-50">
      <div class="container mx-auto px-4 h-16 flex items-center justify-between">
        <div class="flex items-center gap-2">
            <span class="i-carbon-cloud-service-management text-blue-600 text-2xl"></span>
            <h1 class="text-lg font-bold bg-gradient-to-r from-blue-600 to-blue-800 bg-clip-text text-transparent">WX公众号下载平台</h1>
        </div>

        <!-- 可滑动的一级菜单栏 -->
        <div class="flex items-center gap-4">
          <!-- 菜单容器 - 可横向滚动 -->
          <div class="flex items-center gap-2 overflow-x-auto scrollbar-hide relative">
            <div
              v-for="route in topRoutes"
              :key="route.name"
              class="relative"
              @mouseenter="handleMenuEnter(route.name)"
              @mouseleave="handleMenuLeave"
            >
              <!-- 一级菜单项 -->
              <router-link
                :to="{ name: route.children?.[0]?.name }"
                class="flex items-center gap-2 px-4 py-2 text-sm font-medium rounded-lg transition-colors whitespace-nowrap"
                :class="[
                  isActiveRoute(route.name) ? 'bg-blue-600 text-white' : 'text-gray-300 hover:text-white hover:bg-gray-800',
                  hasChildren(route) ? 'cursor-default' : ''
                ]"
                @click="handleMenuClick(route)"
              >
                <span v-if="route.meta?.icon" :class="`i-${route.meta.icon} text-lg`"></span>
                <span>{{ route.meta?.title }}</span>
                <!-- 有二级菜单时显示箭头 -->
                <span v-if="hasChildren(route)" class="i-carbon-chevron-down ml-1 text-xs"></span>
              </router-link>

              <!-- 二级下拉菜单 -->
              <Transition name="dropdown">
                <div
                  v-if="activeMenu === route.name && hasChildren(route) && route.children?.length"
                  class="absolute left-0 top-full mt-1 bg-gray-900 rounded-lg shadow-xl min-w-48 overflow-hidden z-50"
                  @click.stop
                >
                  <router-link
                    v-for="child in route.children"
                    :key="child.name"
                    :to="{ name: child.name }"
                    class="flex items-center gap-2 px-4 py-3 text-sm text-gray-300 hover:text-white hover:bg-gray-800 transition-colors whitespace-nowrap"
                    :class="isActiveChildRoute(child.name) ? 'bg-blue-600 text-white' : ''"
                  >
                    <span v-if="child.meta?.icon" :class="`i-${child.meta.icon} text-lg`"></span>
                    <span>{{ child.meta?.title }}</span>
                  </router-link>
                </div>
              </Transition>
            </div>
          </div>

          <!-- 用户信息 -->
          <div v-if="wechatStore.isLoggedIn" class="flex items-center gap-4 ml-4 border-l border-gray-700 pl-4">
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
import { useWechatLoginStore } from '@/stores/wechatLoginStore'
import { useRouter, useRoute } from 'vue-router'
import { onMounted, computed, ref } from 'vue'

const wechatStore = useWechatLoginStore()
const router = useRouter()
const route = useRoute()

// 当前激活的一级菜单
const activeMenu = ref<string | null>(null)

// 获取一级路由（顶部菜单）
const topRoutes = computed(() => {
  // 从当前路由获取所有父级路由
  const routes = router.getRoutes()
  // 过滤出作为顶级菜单的路由（包含meta且没有父级）
  return routes
    .filter((r: any) => r.meta && r.meta.title && !r.meta?.hideInMenu && !r.path.includes(':'))
    .sort((a: any, b: any) => (a.meta?.sort || 999) - (b.meta?.sort || 999))
})

// 判断路由是否激活（一级菜单）
const isActiveRoute = (routeName: string) => {
  const currentName = route.name as string
  return currentName?.includes(routeName)
}

// 判断子路由是否激活
const isActiveChildRoute = (childName: string) => {
  const currentName = route.name as string
  return currentName === childName
}

// 判断是否有子菜单
const hasChildren = (route: any) => {
  return route.children && route.children.length > 0
}

// 鼠标进入菜单
const handleMenuEnter = (routeName: string) => {
  if (hasChildren(topRoutes.value.find((r: any) => r.name === routeName))) {
    activeMenu.value = routeName
  }
}

// 鼠标离开菜单
const handleMenuLeave = () => {
  // 延迟关闭，给用户时间点击子菜单
  setTimeout(() => {
    activeMenu.value = null
  }, 100)
}

// 点击菜单项
const handleMenuClick = (route: any) => {
  // 如果有子菜单，阻止导航
  if (hasChildren(route)) {
    // 不做任何事，保持下拉菜单打开
  } else {
    // 跳转到子路由
    if (route.children?.[0]) {
      router.push({ name: route.children[0].name })
    }
  }
}

onMounted(() => {
  console.log('✓ 已设置 cookies getter')
  if (!wechatStore.isLoggedIn) {
    wechatStore.initialize();
  }
})

const handleLogout = async () => {
  await wechatStore.logout()
  // 退出后跳转到登录页
  router.push({ name: 'wx-public-crawl-login' })
}
</script>

<style>
/* 隐藏滚动条但保留滚动功能 */
.scrollbar-hide::-webkit-scrollbar {
  display: none;
}

.scrollbar-hide {
  -ms-overflow-style: none;
  scrollbar-width: none;
}

/* 美化滚动条（非隐藏模式） */
::-webkit-scrollbar {
  height: 6px;
  width: 6px;
}

::-webkit-scrollbar-track {
  background: rgba(255, 255, 255, 0.1);
}

::-webkit-scrollbar-thumb {
  background: rgba(255, 255, 255, 0.3);
  border-radius: 3px;
}

::-webkit-scrollbar-thumb:hover {
  background: rgba(255, 255, 255, 0.5);
}

/* 下拉菜单动画 */
.dropdown-enter-active {
  animation: dropdown-in 0.2s ease-out;
}

.dropdown-leave-active {
  animation: dropdown-out 0.15s ease-in;
}

@keyframes dropdown-in {
  0% {
    opacity: 0;
    transform: translateY(-10px);
  }
  100% {
    opacity: 1;
    transform: translateY(0);
  }
}

@keyframes dropdown-out {
  0% {
    opacity: 1;
    transform: translateY(0);
  }
  100% {
    opacity: 0;
    transform: translateY(-5px);
  }
}
</style>