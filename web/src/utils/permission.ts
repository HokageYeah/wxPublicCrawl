/**
 * 权限路由对照配置
 * 定义后台下发的权限标识与前端路由的映射关系
 */

/**
 * 权限标识枚举
 */
export enum Permission {
  /** 喜马拉雅 */
  XIMALAYA = 'ximalaya',
  /** LLM配置 */
  LLM_CONFIG = 'llmconfig',
  /** 微信公众号 */
  WECHAT_PUBLIC = 'wechatpublic',
}

/**
 * 权限到路由路径的映射关系
 * key: 后台下发的权限标识
 * value: 对应的前端路由路径和路由名称（包含父路由和子路由）
 * 
 * 说明：
 * - 路径格式：/parent-path（父路由）
 * - 路由名称格式：parent-name, parent-child-name（父路由和子路由名称）
 * - 权限检查时优先使用路由名称匹配
 */
export const PERMISSION_ROUTE_MAP: Record<string, string[]> = {
  // ==================== 喜马拉雅权限 ====================
  // 对应路由模块：web/src/router/modules/xmly-crawl.ts
  // 后台下发权限标识：'ximalaya'
  [Permission.XIMALAYA]: [
    '/xmly-crawl',
    'xmly-crawl',
    'xmly-crawl-login',
    'xmly-crawl-search-album',
    'xmly-crawl-subscribed-albums',
    'xmly-crawl-album-detail',
  ],
  
  // ==================== LLM配置权限 ====================
  // 对应路由模块：web/src/router/modules/llm-config.ts
  // 后台下发权限标识：'llmconfig'
  [Permission.LLM_CONFIG]: [
    '/llm-config',
    'llm-config',
    'llm-config-list',
  ],
  
  // ==================== 微信公众号权限 ====================
  // 对应路由模块：web/src/router/modules/wx-public-crawl.ts
  // 后台下发权限标识：'wechatpublic'
  [Permission.WECHAT_PUBLIC]: [
    '/wx-public-crawl',
    'wx-public-crawl',
    'wx-public-crawl-login',
    'wx-public-crawl-search',
    'wx-public-crawl-articles',
  ],
};

/**
 * 检查用户是否有权限访问指定路由
 * @param routePath 路由路径或路由名称
 * @param userPermissions 用户拥有的权限列表
 * @param isAdmin 是否是管理员
 * @returns 是否有权限
 */
export function hasRoutePermission(
  routePath: string,
  userPermissions: string[],
  isAdmin: boolean = false
): boolean {
  // 管理员拥有所有权限
  if (isAdmin) {
    return true;
  }

  // 公开路由（不需要权限）
  const publicRoutes = [
    '/',
    '/login',
    '/home',
    'Login',
    'DefaultHome',
  ];
  
  if (publicRoutes.includes(routePath)) {
    return true;
  }

  // 检查用户是否有权限访问该路由
  for (const permission of userPermissions) {
    const allowedRoutes = PERMISSION_ROUTE_MAP[permission.toLowerCase()] || [];
    
    // 检查路由路径或路由名称是否匹配
    if (allowedRoutes.some(route => 
      routePath === route || 
      routePath.startsWith(route) ||
      routePath.includes(route)
    )) {
      return true;
    }
  }

  return false;
}

/**
 * 获取用户有权限访问的所有路由路径
 * @param userPermissions 用户拥有的权限列表
 * @param isAdmin 是否是管理员
 * @returns 有权限的路由路径列表
 */
export function getAuthorizedRoutes(
  userPermissions: string[],
  isAdmin: boolean = false
): string[] {
  // 管理员拥有所有路由
  if (isAdmin) {
    return Object.values(PERMISSION_ROUTE_MAP).flat();
  }

  const authorizedRoutes: string[] = [];
  
  for (const permission of userPermissions) {
    const routes = PERMISSION_ROUTE_MAP[permission.toLowerCase()] || [];
    authorizedRoutes.push(...routes);
  }

  return [...new Set(authorizedRoutes)]; // 去重
}

/**
 * 检查路由名称是否需要权限验证
 * @param routeName 路由名称
 * @returns 是否需要权限验证
 */
export function requiresPermission(routeName: string): boolean {
  // 公开路由不需要权限验证
  const publicRoutes = [
    'Login',
    'DefaultHome',
  ];
  
  return !publicRoutes.includes(routeName);
}
