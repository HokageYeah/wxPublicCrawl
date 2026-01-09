/**
 * 微信公众号爬虫模块路由
 * 包含：登录、搜索公众号、文章列表等页面
 */
import { type RouteRecordRaw } from "vue-router";

const routes: Array<RouteRecordRaw> = [
  {
    path: "/wx-public-crawl",
    name: "wx-public-crawl",
    meta: {
      title: "微信公众号爬虫",
      icon: "carbon-text-link-analysis",
      description: "微信公众号文章爬取和管理工具",
      sort: 1,
    },
    children: [
      {
        path: "login",
        name: "wx-public-crawl-login",
        component: () => import("@/views/wx-public-crawl/WeChatLogin.vue"),
        meta: {
          title: "登录",
          requiresAuth: false,
        },
      },
      {
        path: "search",
        name: "wx-public-crawl-search",
        component: () => import("@/views/wx-public-crawl/SearchPublic.vue"),
        meta: {
          title: "搜索公众号",
          requiresAuth: true,
          hidden: true,
        },
      },
      {
        path: "articles",
        name: "wx-public-crawl-articles",
        component: () => import("@/views/wx-public-crawl/ArticleList.vue"),
        meta: {
          title: "文章列表",
          requiresAuth: true,
          hidden: true,
        },
      },
    ],
  },
];

export default routes;
