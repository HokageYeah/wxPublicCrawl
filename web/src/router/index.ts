import { createRouter, createWebHistory } from 'vue-router'

/**
 * 动态导入所有路由模块
 * 使用 Vite 的 glob 导入功能，自动发现 modules 目录下的所有路由文件
 */
const modules = import.meta.glob('./modules/**/*.ts')

/**
 * 构建路由配置
 * 遍历所有动态导入的模块，提取路由配置
 */
const routes: any[] = []

// 处理所有模块
Object.values(modules).forEach((module) => {
  // 获取模块的 default 导出
  const routeConfig = (module as any).default

  if (routeConfig && typeof routeConfig === 'object') {
    // 直接添加整个模块路由（包含子路由）
    routes.push(routeConfig)
  }
})

/**
 * 创建路由实例
 */
const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes,
  // 滚动行为
  scrollBehavior() {
    return { top: 0, behavior: 'smooth' }
  }
})

/**
 * 全局前置守卫
 * 可以在这里实现权限验证、登录状态检查等
 */
router.beforeEach((to) => {
  // 设置页面标题
  const title = (to.meta?.title as string) || '微信公众号爬虫'
  document.title = `${title} - 微信公众号爬虫工具`

  // 检查路由是否需要认证
  const requiresAuth = to.meta?.requiresAuth as boolean
  if (requiresAuth) {
    // TODO: 实现登录状态检查逻辑
    // const isLoggedIn = checkLoginStatus()
    // if (!isLoggedIn) {
    //   router.push('/crawl-desktop/wx-public-crawl/login')
    //   return false
    // }
  }

  return true
})

/**
 * 全局后置守卫
 * 可以在这里实现页面加载完成后的逻辑
 */
router.afterEach(() => {
  // TODO: 页面加载完成后的逻辑
  // 例如：统计、日志记录等
})

export default router
