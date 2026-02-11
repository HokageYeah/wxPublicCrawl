# 路由模块化开发指南

## 概述

本项目使用模块化的路由架构，通过 Vite 的 `glob` 功能动态导入路由模块，实现自动发现和配置。

## 目录结构

```
web/src/
├── router/
│   ├── index.ts              # 路由主配置文件
│   ├── modules/               # 路由模块目录
│   │   ├── wx-public-crawl.ts # 微信公众号爬虫模块
│   │   └── ...             # 其他业务模块
│   └── README.md             # 本文档
└── views/
    └── wx-public-crawl/
        ├── WeChatLogin.vue      # 登录页面
        ├── SearchPublic.vue    # 搜索公众号页面
        └── ArticleList.vue     # 文章列表页面
```

## 模块文件格式

### 1. 创建模块文件

在 `router/modules/` 目录下创建新的路由模块文件，例如 `new-module.ts`：

```typescript
/**
 * 新功能模块路由
 * 包含：页面列表、详情页等
 */
import { type RouteRecordRaw } from 'vue-router'
import Page1 from '../../views/new-module/Page1.vue'
import Page2 from '../../views/new-module/Page2.vue'

// ✅ 使用数组变量创建子路由
const routes: Array<RouteRecordRaw> = [
  {
    path: 'page1',
    name: 'new-module-page1',
    component: Page1,
    meta: {
      title: '页面1',
      requiresAuth: true
    }
  },
  {
    path: 'page2',
    name: 'new-module-page2',
    component: Page2,
    meta: {
      title: '页面2',
      requiresAuth: false
    }
  }
]

export default {
  path: '/new-module',
  name: 'new-module',
  meta: {
    title: '新功能模块',
    icon: 'carbon-settings',
    description: '模块描述'
  },
  children: routes  // ✅ 导出数组变量
}
```

**重要**：
- ✅ **必须使用** `const routes: Array<RouteRecordRaw> = []` 创建子路由数组
- ✅ **必须导出** `children: routes` 数组变量，不能直接内联数组
- ❌ **不能直接导出** `children: [...]` 内联数组（会导致路由无法正确加载）
```

### 2. 模块导出格式

每个模块文件必须 `export default` 一个路由配置对象：

```typescript
export default {
  // 路由路径（必填）
  path: string,

  // 路由名称（必填，必须全局唯一）
  name: string,

  // 子路由（可选）
  children?: RouteRecordRaw[],

  // 路由元信息（可选）
  meta?: {
    title: string,           // 页面标题
    icon?: string,            // 图标（使用 carbon 图标）
    description?: string,      // 描述
    requiresAuth?: boolean,     // 是否需要登录
    hideInMenu?: boolean,      // 是否在菜单中隐藏
    // ... 其他自定义元信息
  }
}
```

## 现有模块

### 微信公众号爬虫模块

**文件**: `router/modules/wx-public-crawl.ts`

**路由结构**:
```
/wx-public-crawl
├── /login          # 登录页面
├── /search         # 搜索公众号
└── /articles        # 文章列表
```

**组件**:
- `WeChatLogin.vue` - 微信登录页面
- `SearchPublic.vue` - 搜索公众号页面
- `ArticleList.vue` - 文章列表页面

## 路由配置

### 动态导入机制

```typescript
// 自动发现 modules 目录下的所有 .ts 文件
const modules = import.meta.glob<RouteModule>('./modules/**/*.ts')

// 提取所有模块的路由配置
const routes = [
  {
    path: '/',
    redirect: '/wx-public-crawl/login'  // 默认重定向
  },
  ...Object.values(modules).map((module) => module.default)
]
```

### 路由守卫

#### 全局前置守卫

```typescript
router.beforeEach((to, from, next) => {
  // 设置页面标题
  const title = to.meta?.title as string || '微信公众号爬虫'
  document.title = `${title} - 微信公众号爬虫工具`

  // 检查认证状态
  const requiresAuth = to.meta?.requiresAuth as boolean
  if (requiresAuth) {
    if (!checkLoginStatus()) {
      next('/wx-public-crawl/login')
      return
    }
  }

  next()
})
```

#### 全局后置守卫

```typescript
router.afterEach((to, from) => {
  // 页面加载完成后的逻辑
  // 例如：统计、日志记录
})
```

### 滚动行为

```typescript
scrollBehavior(to, from, savedPosition) {
  // 1. 恢复滚动位置（前进/后退）
  if (savedPosition) {
    return savedPosition
  }

  // 2. 锚点跳转
  if (to.hash) {
    return {
      el: to.hash,
      behavior: 'smooth'
    }
  }

  // 3. 滚动到顶部
  return { top: 0, behavior: 'smooth' }
}
```

## 添加新模块步骤

### Step 1: 创建视图组件

在 `views/` 下创建模块目录和组件：

```bash
mkdir -p web/src/views/new-module
```

创建 Vue 组件文件：

```vue
<!-- views/new-module/Page1.vue -->
<template>
  <div>
    <h1>页面1</h1>
  </div>
</template>

<script setup lang="ts">
// 组件逻辑
</script>
```

### Step 2: 创建路由模块

在 `router/modules/` 下创建路由配置：

```typescript
// router/modules/new-module.ts
import Page1 from '../../views/new-module/Page1.vue'

export default {
  path: '/new-module',
  name: 'new-module',
  meta: {
    title: '新功能模块'
  },
  children: [
    {
      path: 'page1',
      name: 'new-module-page1',
      component: Page1
    }
  ]
}
```

### Step 3: 自动注册

路由会自动被导入并注册，无需修改 `router/index.ts`！

### Step 4: 访问新路由

```typescript
// 编程式导航
import { useRouter } from 'vue-router'
const router = useRouter()
router.push({ name: 'new-module-page1' })

// 或使用路径
router.push('/new-module/page1')
```

```vue
<!-- 模板中导航 -->
<router-link to="/new-module/page1">页面1</router-link>
```

## 路由命名规范

### 模块级路由名称

格式: `[module-name]`

示例:
- `wx-public-crawl` - 微信公众号爬虫模块
- `new-module` - 新功能模块

### 页面级路由名称

格式: `[module-name]-[page-name]`

示例:
- `wx-public-crawl-login` - 登录页面
- `wx-public-crawl-search` - 搜索页面
- `new-module-page1` - 新模块页面1

### 嵌套路由名称

如果有多级嵌套，继续追加层级：

格式: `[module-name]-[parent]-[child]`

示例:
- `settings-profile-avatar` - 设置 > 个人资料 > 头像

## 路由元信息（Meta）

### 标准元字段

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| title | string | 是 | 页面标题 |
| requiresAuth | boolean | 否 | 是否需要登录 |
| icon | string | 否 | 图标（使用 carbon 图标） |
| description | string | 否 | 模块描述 |
| hideInMenu | boolean | 否 | 是否在菜单中隐藏 |

### 自定义元字段

可以添加任意自定义字段：

```typescript
meta: {
  title: '页面标题',
  roles: ['admin', 'editor'],      // 允许的角色
  permissions: ['read', 'write'],   // 需要的权限
  layout: 'full-width',             // 布局类型
  keepAlive: true                   // 是否缓存页面
}
```

## 最佳实践

### 1. 模块划分原则

- ✅ 按业务功能划分（如：公众号爬虫、用户管理等）
- ✅ 单一职责：每个模块只负责一个业务领域
- ✅ 模块独立：模块之间尽量减少耦合

### 2. 路由命名规范

- ✅ 使用 kebab-case（短横线命名）
- ✅ 名称要有明确的含义
- ✅ 避免重复和冲突

### 3. 组件组织

```
views/
└── [module-name]/           # 模块目录
    ├── components/           # 模块私有组件
    ├── composables/           # 模块私有组合式函数
    ├── types/                # 模块私有类型定义
    └── [page-names].vue      # 页面组件
```

### 4. 权限控制

```typescript
meta: {
  requiresAuth: true,           // 需要登录
  roles: ['admin'],            // 需要管理员角色
  permissions: ['write:article'] // 需要写入文章权限
}
```

然后在路由守卫中实现：

```typescript
router.beforeEach((to, from, next) => {
  const user = getCurrentUser()

  // 检查登录状态
  if (to.meta.requiresAuth && !user) {
    next('/wx-public-crawl/login')
    return
  }

  // 检查角色权限
  if (to.meta.roles && !to.meta.roles.includes(user.role)) {
    next('/403')
    return
  }

  next()
})
```

### 5. 性能优化

#### 路由懒加载

对于大型模块，可以使用懒加载：

```typescript
export default {
  path: '/new-module',
  name: 'new-module',
  children: [
    {
      path: 'page1',
      name: 'new-module-page1',
      // 懒加载组件
      component: () => import('../../views/new-module/Page1.vue')
    }
  ]
}
```

#### 路由预加载

在应用启动时预加载重要模块：

```typescript
// 预加载登录模块
const loginModule = await import('./modules/wx-public-crawl.ts')
```

## 常见问题

### Q: 如何修改默认首页？

A: 修改 `router/index.ts` 中的重定向路径：

```typescript
{
  path: '/',
  redirect: '/new-module/page1'  // 修改为你的首页
}
```

### Q: 如何禁用某个模块？

A: 删除或重命名 `modules/` 目录下的对应文件：

```bash
# 方法1: 删除模块文件
rm router/modules/wx-public-crawl.ts

# 方法2: 重命名（临时禁用）
mv router/modules/wx-public-crawl.ts router/modules/wx-public-crawl.ts.disabled
```

### Q: 如何在模块之间共享组件？

A: 将共享组件放在 `src/components/` 目录（模块外部）：

```
web/src/
├── components/          # 全局共享组件
│   ├── Button.vue
│   └── Table.vue
└── views/
    └── [module-name]/
        └── components/  # 模块私有组件
            └── ModuleCard.vue
```

### Q: 路由名称冲突怎么办？

A: 使用模块名称作为前缀，确保唯一性：

```typescript
// ❌ 错误：名称可能冲突
export default {
  name: 'page1',  // 可能与其他模块的 page1 冲突
  children: [...]
}

// ✅ 正确：使用模块前缀
export default {
  name: 'new-module',
  children: [
    {
      name: 'new-module-page1',  // 唯一
    }
  ]
}
```

## 相关资源

- [Vue Router 官方文档](https://router.vuejs.org/)
- [Vite Glob 导入](https://vitejs.dev/guide/features.html#glob-import)
- [Carbon Design System](https://carbondesignsystem.com/) - 图标库

---

*最后更新: 2026-01-08*

