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
    ],
  },
];

export default routes;
