import { createRouter, createWebHistory } from "vue-router";

/**
 * 动态导入所有路由模块
 * 使用 Vite 的 glob 导入功能，自动发现 modules 目录下的所有路由文件
 */
const modules = import.meta.glob("./modules/**/*.ts", { eager: true });

/**
 * 构建路由配置
 * 遍历所有动态导入的模块，提取路由配置
 */
const routes: any[] = [];

console.log("routes: 所有的modules---", modules);
// 处理所有模块
Object.values(modules).forEach((module) => {
  console.log("routes: module---", module);
  // 获取模块的 default 导出
  const routeConfig = (module as any).default;

  console.log("routes: routeConfig---", routeConfig);

  if (routeConfig) {
    if (Array.isArray(routeConfig)) {
      // 如果是数组，使用 spread operator 添加
      routes.push(...routeConfig);
    } else if (typeof routeConfig === "object") {
      // 如果是对象，直接添加
      routes.push(routeConfig);
    }
  }
});

/**
 * 根据 meta.sort 排序路由
 * sort 值越小越靠前，没有 sort 的默认排在最后
 */
routes.sort((a, b) => {
  const sortA = a.meta?.sort ?? Infinity;
  const sortB = b.meta?.sort ?? Infinity;
  return sortA - sortB;
});

/**
 * 创建路由实例
 */
const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes,
  // 滚动行为
  scrollBehavior() {
    return { top: 0, behavior: "smooth" };
  },
});

import { useWechatLoginStore } from "@/stores/wechatLoginStore";
import { useXmlyLoginStore } from "@/stores/xmlyLoginStore";

/**
 * 全局前置守卫
 * 可以在这里实现权限验证、登录状态检查等
 */
router.beforeEach(async (to, _, next) => {
  // 设置页面标题
  const title = (to.meta?.title as string) || "微信公众号爬虫";
  document.title = `${title} - 微信公众号爬虫工具`;

  // 检查路由是否需要认证
  const requiresAuth = to.meta?.requiresAuth as boolean;

  if (requiresAuth) {
    const wechatStore = useWechatLoginStore();
    const xmlyStore = useXmlyLoginStore();

    // 如果未登录，尝试初始化会话（处理刷新页面的情况）
    if (!wechatStore.isLoggedIn) {
      await wechatStore.initialize();
    }
    console.log("xmlyStore.isLoggedIn------", xmlyStore.isLoggedIn);
    // 如果xmly未登录的话，尝试初始化会话
    if (!xmlyStore.isLoggedIn) {
      await xmlyStore.initialize();
    }

    // 再次检查登录状态
    if (!wechatStore.isLoggedIn) {
      alert("您还未登录，请先登录系统");
      next({ name: "wx-public-crawl-login" });
      return;
    }
  }

  next();
});

/**
 * 全局后置守卫
 * 可以在这里实现页面加载完成后的逻辑
 */
router.afterEach(() => {
  // TODO: 页面加载完成后的逻辑
  // 例如：统计、日志记录等
});

export default router;
