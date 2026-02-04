<template>
  <div class="min-h-screen flex flex-col bg-black dark:bg-gray-900">
    <!-- 顶部导航区域容器 -->
    <div class="sticky top-0 z-50 bg-black shadow-md">
      <!-- 第一行：Logo + 一级菜单 + 用户信息 -->
      <header class="relative z-20 bg-black border-b border-gray-800">
        <div
          class="container mx-auto px-4 h-16 flex items-center justify-between"
        >
          <!-- Logo -->
          <div class="flex items-center gap-2 shrink-0 mr-8">
            <span
              class="i-carbon-cloud-service-management text-blue-600 text-2xl"
            ></span>
            <h1
              class="text-lg font-bold bg-gradient-to-r from-blue-600 to-blue-800 bg-clip-text text-transparent hidden sm:block"
            >
              WX公众号下载平台
            </h1>
            <h1
              class="text-lg font-bold bg-gradient-to-r from-blue-600 to-blue-800 bg-clip-text text-transparent sm:hidden"
            >
              WX平台
            </h1>
          </div>

          <!-- 一级菜单栏 (中间部分) - 仅管理员或已登录用户显示 -->
          <div
            v-if="licenseStore.isLoggedIn && shouldShowMenu"
            class="flex-1 overflow-visible"
          >
            <div class="flex items-center gap-4 overflow-x-visible">
              <div
                v-for="route in topRoutes"
                :key="route.name"
                class="relative group"
                @mouseenter="hoveredLevel1Menu = String(route.name)"
                @mouseleave="hoveredLevel1Menu = null"
              >
                <!-- 一级菜单按钮 -->
                <router-link
                  :to="{ name: route.children?.[0]?.name || route.name }"
                  custom
                  v-slot="{ navigate }"
                >
                  <button
                    @click="handleMenuClick(route, navigate)"
                    class="flex items-center gap-2 px-4 py-2 text-sm font-medium rounded-lg transition-all duration-200 outline-none"
                    :class="[
                      isRouteActive(route)
                        ? 'text-blue-500'
                        : 'text-gray-400 hover:text-white',
                    ]"
                  >
                    <span
                      v-if="route.meta?.icon"
                      :class="`i-${route.meta.icon} text-lg`"
                    ></span>
                    <span>{{ route.meta?.title }}</span>
                    <!-- 指示器 -->
                    <span
                      v-if="hasChildren(route)"
                      class="i-carbon-chevron-down ml-1 text-xs opacity-50 transition-transform duration-200"
                      :class="
                        hoveredLevel1Menu === route.name ? 'rotate-180' : ''
                      "
                    ></span>
                  </button>
                </router-link>

                <!-- 二级下拉菜单 (悬浮) -->
                <Transition name="dropdown">
                  <div
                    v-if="hasChildren(route)"
                    class="absolute top-full left-1/2 -translate-x-1/2 bg-transparent w-[120px]"
                    v-show="hoveredLevel1Menu === route.name"
                  >
                    <!-- 下拉菜单内容容器 -->
                    <div
                      class="bg-black/95 rounded-b-lg rounded-t-none border-x border-b border-gray-800/50 shadow-xl overflow-hidden py-2 backdrop-blur-sm"
                    >
                      <template v-for="child in getVisibleChildren(route)" :key="child.name">
                        <router-link
                          :to="{ name: child.name }"
                          class="flex items-center gap-3 px-4 py-2.5 text-sm transition-colors hover:bg-gray-800"
                          :class="
                            isActiveChildRoute(String(child.name))
                              ? 'text-blue-400'
                              : 'text-gray-400 hover:text-white'
                          "
                        >
                          <span
                            v-if="child.meta?.icon"
                            :class="`i-${child.meta.icon}`"
                          ></span>

                          <span class="flex-1 truncate">{{
                            child.meta?.title
                          }}</span>

                          <!-- 三级菜单箭头 -->
                          <span
                            v-if="hasChildren(child)"
                            class="i-carbon-chevron-right text-xs opacity-50"
                          ></span>
                        </router-link>
                      </template>
                    </div>
                  </div>
                </Transition>
              </div>
            </div>
          </div>

          <!-- 右侧区域：登录按钮或用户信息 -->
          <div class="flex items-center gap-4 ml-4">
            <!-- 卡密切换按钮（多卡时显示） -->
            <div
              v-if="showCardSwitcher"
              class="relative"
              @mouseenter="showCardDropdown = true"
              @mouseleave="showCardDropdown = false"
            >
              <button
                class="flex items-center gap-2 px-3 py-1.5 text-sm font-medium text-blue-400 hover:text-blue-300 border border-blue-500/30 hover:border-blue-500/50 rounded-lg transition-colors"
              >
                <span class="i-carbon-chip text-lg"></span>
                <span>{{ activeCardIndex + 1 }} / {{ currentAppCards.length }}</span>
                <span class="i-carbon-chevron-down text-xs"></span>
              </button>

              <!-- 卡密下拉列表 -->
              <Transition name="dropdown">
                <div
                  v-if="showCardDropdown"
                  class="absolute right-0 top-full mt-2 bg-black/95 border border-gray-700 rounded-lg shadow-xl py-2 min-w-[280px]"
                >
                  <div class="px-4 py-2 text-xs text-gray-500 border-b border-gray-800">
                    选择卡密 ({{ currentAppCards.length }} 张)
                  </div>
                  <button
                    v-for="(card, index) in currentAppCards"
                    :key="card.card_id"
                    @click="switchCard(index)"
                    class="w-full px-4 py-3 text-left hover:bg-gray-800 transition-colors flex items-start gap-3"
                    :class="{ 'bg-gray-800': index === activeCardIndex }"
                  >
                    <div class="flex-1 min-w-0">
                      <div class="flex items-center gap-2 mb-1">
                        <span class="text-blue-400 font-medium text-sm truncate">
                          {{ card.card_key }}
                        </span>
                        <span
                          v-if="index === activeCardIndex"
                          class="i-carbon-checkmark text-green-500 text-xs"
                        ></span>
                      </div>
                      <div class="text-xs text-gray-500">
                        <span
                          class="inline-block px-1.5 py-0.5 rounded"
                          :class="{
                            'bg-green-500/20 text-green-400': card.status === 'used',
                            'bg-yellow-500/20 text-yellow-400': card.status === 'pending',
                            'bg-red-500/20 text-red-400': card.status === 'expired',
                          }"
                        >
                          {{ card.status }}
                        </span>
                        <span class="ml-2">
                          {{ card.permissions?.join(", ") || "无权限" }}
                        </span>
                      </div>
                      <div class="text-xs text-gray-600 mt-1">
                        有效期至: {{ formatDate(card.expire_time) }}
                      </div>
                    </div>
                  </button>
                </div>
              </Transition>
            </div>

            <!-- 未登录时显示登录按钮 -->
            <div v-if="!licenseStore.isLoggedIn">
              <router-link
                to="/login"
                class="flex items-center gap-1.5 px-4 py-2 text-sm font-medium text-white bg-blue-600 hover:bg-blue-700 rounded-lg transition-colors"
              >
                <span class="i-carbon-login"></span>
                <span>登录</span>
              </router-link>
            </div>

            <!-- 已登录用户信息 -->
            <div
              v-if="licenseStore.isLoggedIn"
              class="flex items-center gap-4 border-l border-gray-700 pl-4"
            >
              <!-- 应用信息 -->
              <div
                v-if="appStore.currentApp"
                class="hidden md:flex items-center text-sm text-blue-400 bg-blue-50 px-3 py-1.5 rounded-full"
              >
                <span class="i-carbon-application mr-1.5"></span>
                <span>{{ appStore.currentApp.app_name }}</span>
              </div>
              
              <!-- 用户信息 -->
              <div
                class="hidden md:flex items-center text-sm text-gray-500 bg-gray-100 px-3 py-1.5 rounded-full"
              >
                <span class="i-carbon-user mr-1.5 text-gray-400"></span>
                <span>{{ licenseStore.userInfo?.username || "已登录用户" }}</span>
                <span
                  v-if="licenseStore.userInfo?.role === 'admin'"
                  class="ml-2 px-1.5 py-0.5 text-xs bg-purple-100 text-purple-700 rounded"
                >
                  管理员
                </span>
              </div>
              <button
                @click="handleLogout"
                class="flex items-center gap-1.5 px-3 py-1.5 text-sm font-medium text-gray-600 hover:text-red-600 hover:bg-red-50 rounded-lg transition-colors"
                title="退出登录"
              >
                <span class="i-carbon-logout"></span>
                <span class="hidden sm:inline">退出</span>
              </button>
            </div>
          </div>
        </div>
      </header>
    </div>

    <main class="flex-1 transition-all duration-300">
      <RouterView v-slot="{ Component, route }">
        <transition :name="getTransitionName" appear mode="out-in">
          <keep-alive v-if="route.meta?.keepAlive">
            <component :is="Component" :key="route.fullPath" />
          </keep-alive>
          <component :is="Component" v-else :key="route.fullPath" />
        </transition>
      </RouterView>
    </main>

    <footer
      class="py-6 mt-auto bg-white dark:bg-black border-t dark:border-gray-800"
    >
      <div class="container mx-auto px-4 text-center text-gray-500 text-xs">
        <p>
          &copy; {{ new Date().getFullYear() }} WX Public Crawl Platform. All
          rights reserved.
        </p>
      </div>
    </footer>
  </div>
</template>

<script setup lang="ts">
import { useLicenseStore } from "@/stores/licenseStore";
import { useAppStore } from "@/stores/appStore";
import type { CardInfo } from "@/services/licenseService";
import { useRouter, useRoute } from "vue-router";
import { onMounted, computed, ref } from "vue";
import { hasRoutePermission } from "@/utils/permission";

const licenseStore = useLicenseStore();
const appStore = useAppStore();
const router = useRouter();
const route = useRoute();

// 状态管理
const hoveredLevel1Menu = ref<string | null>(null); // 当前鼠标悬停的一级菜单
const showCardDropdown = ref(false); // 是否显示卡密下拉菜单
const activeCardIndex = ref(0); // 当前选中的卡密索引

// 计算是否显示菜单（管理员或已登录用户）
const shouldShowMenu = computed(() => {
  if (!licenseStore.isLoggedIn) return false;
  // 管理员显示所有菜单
  if (licenseStore.userInfo?.role === 'admin') return true;
  // 普通用户有卡密也显示菜单
  if (licenseStore.userInfo?.has_card && licenseStore.cards.length > 0) return true;
  return false;
});

// 计算是否显示卡密切换器（多卡时显示）
const showCardSwitcher = computed(() => {
  return (
    licenseStore.isLoggedIn &&
    licenseStore.userInfo?.role !== 'admin' &&
    currentAppCards.value.length >= 1
  );
});

// 筛选当前应用下的卡密
const currentAppCards = computed(() => {
  if (!licenseStore.cards || licenseStore.cards.length === 0) return [];
  if (!appStore.currentApp) return [];
  console.log("✓ 当前应用下的卡密", licenseStore.cards, appStore.currentApp);
  const cards = licenseStore.cards.filter(
    card => card.app_id === appStore.currentApp?.app_id
  );
  console.log("✓ 当前应用下的卡密--", cards);
  return cards;
});

// 获取当前激活卡密的权限列表
const currentPermissions = computed(() => {
  // 管理员拥有所有权限
  if (licenseStore.userInfo?.role === 'admin') {
    return ['all'];
  }
  
  // 获取当前卡密的权限
  const currentCard = currentAppCards.value[activeCardIndex.value];
  return currentCard?.permissions || [];
});

// 检查路由是否有权限访问
const checkRoutePermission = (routePath: string) => {
  const isAdmin = licenseStore.userInfo?.role === 'admin';
  return hasRoutePermission(routePath, currentPermissions.value, isAdmin);
};

// 获取一级路由（顶部菜单）- 根据权限过滤
const topRoutes = computed(() => {
  const routes = router.options.routes;
  const isAdmin = licenseStore.userInfo?.role === 'admin';
  console.log("✓ 检查路由是否有权限访问--routes", routes);
  return routes
    .filter((r: any) => {
      // 基础过滤：必须有标题且不隐藏
      if (!r.meta || !r.meta.title || r.meta?.hideInMenu || r.path.includes(":")) {
        return false;
      }
      
      // 管理员显示所有路由
      if (isAdmin) {
        return true;
      }
      console.log("✓ 检查路由是否有权限访问--r.name", r.name);
      console.log("✓ 检查路由是否有权限访问--r.path", r.path);
      console.log("✓ 检查路由是否有权限访问--checkRoutePermission", currentPermissions.value, isAdmin);

      // 普通用户需要检查权限
      // 优先使用路由名称，因为权限映射中使用的是路由名称
      const routeIdentifier = r.name || r.path;
      return checkRoutePermission(routeIdentifier);
    })
    .sort((a: any, b: any) => (a.meta?.sort || 999) - (b.meta?.sort || 999));
});

// 判断一级路由是否处于"激活"状态
const isRouteActive = (parentRoute: any) => {
  const currentName = route.name as string;
  return (
    currentName &&
    typeof currentName === "string" &&
    (currentName.includes(parentRoute.name) ||
      parentRoute.children?.some((c: any) => c.name === currentName))
  );
};

// 判断二级子路由是否激活
const isActiveChildRoute = (childName: string) => {
  return route.name === childName;
};

// 判断是否有子菜单
const hasChildren = (route: any) => {
  return route.children && route.children.length > 0;
};

// 获取可见的子路由 - 根据权限过滤
const getVisibleChildren = (parentRoute: any) => {
  if (!parentRoute.children) return [];
  const isAdmin = licenseStore.userInfo?.role === 'admin';
  
  return parentRoute.children.filter((c: any) => {
    // 基础过滤：不隐藏的子路由
    if (c.meta?.hidden) {
      return false;
    }
    
    // 管理员显示所有子路由
    if (isAdmin) {
      return true;
    }
    
    // 普通用户需要检查权限
    // 优先使用路由名称，因为权限映射中使用的是路由名称
    const routeIdentifier = c.name || c.path;
    return checkRoutePermission(routeIdentifier);
  });
};

// 获取过渡动画名称
const getTransitionName = computed(() => {
  return route.meta?.transitionName || 'fade';
});

const handleMenuClick = (route: any, navigate: () => void) => {
  if (route.children && route.children.length > 0) {
    const firstChild =
      route.children.find((c: any) => !c.meta?.hidden) || route.children[0];
    router.push({ name: firstChild.name });
  } else {
    navigate();
  }
};

// 切换卡密
const switchCard = (index: number) => {
  activeCardIndex.value = index;
  showCardDropdown.value = false;
  // TODO: 切换卡密后可以触发相关业务逻辑
  console.log("切换到卡密:", currentAppCards.value[index]?.card_key);
};

// 格式化日期
const formatDate = (dateStr: string) => {
  if (!dateStr) return "永久";
  const date = new Date(dateStr);
  return date.toLocaleDateString("zh-CN");
};

onMounted(() => {
  console.log("✓ App mounted");
  licenseStore.initialize();
  // 初始化应用信息
  appStore.initialize();
});

const handleLogout = async () => {
  await licenseStore.clearUserInfo();
  // 清除应用信息
  await appStore.clearCurrentApp();
  // 重置卡密选择
  activeCardIndex.value = 0;
  router.push({ name: "Login" });
};
</script>

<style>
/* 通用隐藏滚动条 */
.scrollbar-hide::-webkit-scrollbar {
  display: none;
}
.scrollbar-hide {
  -ms-overflow-style: none;
  scrollbar-width: none;
}

/* 遮罩渐变效果，提示可横向滚动 */
.mask-fade {
  mask-image: linear-gradient(
    to right,
    transparent,
    black 10px,
    black 90%,
    transparent
  );
  -webkit-mask-image: linear-gradient(
    to right,
    transparent,
    black 10px,
    black 90%,
    transparent
  );
}

/* 下拉菜单动画 */
.dropdown-enter-active,
.dropdown-leave-active {
  transition: all 0.3s ease;
  transform-origin: top;
  overflow: hidden;
}

.dropdown-enter-from,
.dropdown-leave-to {
  opacity: 0;
  transform: scaleY(0);
}

/* 页面切换过渡动画 */
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.3s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}
</style>
