import { type RouteRecordRaw } from "vue-router";

/**
 * 喜马拉雅听书模块路由
 * 包含：登录、搜索有声书、列表等功能
 */
const routes: Array<RouteRecordRaw> = [
  {
    path: "/xmly-crawl",
    name: "xmly-crawl",
    meta: {
      title: "喜马拉雅听书",
      icon: "carbon-sport-and-activity",
      description: "喜马拉雅听书下载和管理工具",
      sort: 2,
    },
    children: [
      {
        path: "login",
        name: "xmly-crawl-login",
        component: () => import("@/views/xmly-crawl/XmlyLogin.vue"),
        meta: {
          title: "登录",
          requiresAuth: false,
        },
      },
      {
        path: "search-album",
        name: "xmly-crawl-search-album",
        component: () => import("@/views/xmly-crawl/xmlySearchAlbum.vue"),
        meta: {
          title: "搜索专辑",
          requiresAuth: true,
        },
      },
      {
        path: "subscribed-albums",
        name: "xmly-crawl-subscribed-albums",
        component: () => import("@/views/xmly-crawl/XmlySubscribedAlbum.vue"),
        meta: {
          title: "订阅专辑",
          requiresAuth: true,
        },
      },
      {
        path: "album-detail",
        name: "xmly-crawl-album-detail",
        component: () => import("@/views/xmly-crawl/XmlyAlbumDetail.vue"),
        meta: {
          title: "专辑详情",
          requiresAuth: true,
          hideInMenu: true,
          hidden: true,
        },
      },
    ],
  },
];

export default routes;
