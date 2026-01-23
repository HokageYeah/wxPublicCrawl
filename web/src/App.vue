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

          <!-- 一级菜单栏 (中间部分) -->
          <div class="flex-1 overflow-visible">
            <div class="flex items-center gap-4 overflow-x-visible">
              <div
                v-for="route in topRoutes"
                :key="route.name"
                class="relative group"
                @mouseenter="hoveredLevel1Menu = route.name as string"
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
                      <router-link
                        v-for="child in route.children?.filter((c: any) => !c.meta?.hidden)"
                        :key="child.name"
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
                        <!-- <span
                          v-else
                          class="i-carbon-circle-dash text-xs opacity-50"
                        ></span> -->

                        <span class="flex-1 truncate">{{
                          child.meta?.title
                        }}</span>

                        <!-- 三级菜单箭头 -->
                        <span
                          v-if="hasChildren(child)"
                          class="i-carbon-chevron-right text-xs opacity-50"
                        ></span>
                      </router-link>
                    </div>
                  </div>
                </Transition>
              </div>
            </div>
          </div>

          <!-- 用户信息 (右侧) -->
          <div
            v-if="wechatStore.isLoggedIn"
            class="flex items-center gap-4 ml-4 border-l border-gray-700 pl-4"
          >
            <div
              class="hidden md:flex items-center text-sm text-gray-500 bg-gray-100 px-3 py-1.5 rounded-full"
            >
              <span class="i-carbon-user mr-1.5 text-gray-400"></span>
              <span>{{ wechatStore.userInfo?.nick_name || "已登录用户" }}</span>
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
import { useWechatLoginStore } from "@/stores/wechatLoginStore";
import { useRouter, useRoute } from "vue-router";
import { onMounted, computed, ref } from "vue";

const wechatStore = useWechatLoginStore();
const router = useRouter();
const route = useRoute();

// 状态管理
const hoveredLevel1Menu = ref<string | null>(null); // 当前鼠标悬停的一级菜单

// 获取一级路由（顶部菜单）
const topRoutes = computed(() => {
  const routes = router.options.routes;
  return routes
    .filter(
      (r: any) =>
        r.meta && r.meta.title && !r.meta?.hideInMenu && !r.path.includes(":")
    )
    .sort((a: any, b: any) => (a.meta?.sort || 999) - (b.meta?.sort || 999));
});

// 判断一级路由是否处于“激活”状态
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

// 获取过渡动画名称
const getTransitionName = computed(() => {
  // 可以根据路由元数据返回不同的过渡动画名称
  return route.meta?.transitionName || 'fade';
});

const handleMenuClick = (route: any, navigate: () => void) => {
  // 如果有子菜单，且当前不在该一级菜单下，则跳转到第一个子菜单
  if (route.children && route.children.length > 0) {
    const firstChild =
      route.children.find((c: any) => !c.meta?.hidden) || route.children[0];
    router.push({ name: firstChild.name });
  } else {
    navigate();
  }
};

onMounted(() => {
  console.log("✓ App mounted");
  if (!wechatStore.isLoggedIn) {
    wechatStore.initialize();
  }
});

const handleLogout = async () => {
  await wechatStore.logout();
  router.push({ name: "wx-public-crawl-login" });
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
