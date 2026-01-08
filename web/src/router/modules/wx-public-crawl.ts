/**
 * 微信公众号爬虫模块路由
 * 包含：登录、搜索公众号、文章列表等页面
 */
import { type RouteRecordRaw } from 'vue-router'
import WeChatLogin from '../../views/wx-public-crawl/WeChatLogin.vue'
import SearchPublic from '../../views/wx-public-crawl/SearchPublic.vue'
import ArticleList from '../../views/wx-public-crawl/ArticleList.vue'

const routes: Array<RouteRecordRaw> = [
  {
    path: 'login',
    name: 'wx-public-crawl-login',
    component: WeChatLogin,
    meta: {
      title: '登录',
      requiresAuth: false
    }
  },
  {
    path: 'search',
    name: 'wx-public-crawl-search',
    component: SearchPublic,
    meta: {
      title: '搜索公众号',
      requiresAuth: true
    }
  },
  {
    path: 'articles',
    name: 'wx-public-crawl-articles',
    component: ArticleList,
    meta: {
      title: '文章列表',
      requiresAuth: true
    }
  }
]

export default {
  path: '/wx-public-crawl',
  name: 'wx-public-crawl',
  meta: {
    title: '微信公众号爬虫',
    icon: 'carbon-text-link-analysis',
    description: '微信公众号文章爬取和管理工具'
  },
  children: routes
}
