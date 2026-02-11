/**
 * LLM配置管理模块路由
 * 包含：LLM配置列表、创建、编辑等功能
 */
import { type RouteRecordRaw } from "vue-router";

const routes: Array<RouteRecordRaw> = [
  {
    path: "/llm-config",
    name: "llm-config",
    meta: {
      title: "LLM配置管理",
      icon: "carbon-ai-services",
      description: "AI大模型配置和管理",
      sort: 2,
    },
    children: [
      {
        path: "",
        name: "llm-config-list",
        component: () => import("@/views/llm-config/llm-config.vue"),
        meta: {
          title: "配置管理",
          requiresAuth: false,
          keepAlive: true,
        },
      },
    ],
  },
];

export default routes;

