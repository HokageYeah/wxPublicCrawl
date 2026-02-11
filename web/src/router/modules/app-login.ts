import type { RouteRecordRaw } from "vue-router";

const appLoginRoutes: RouteRecordRaw[] = [
  {
    path: "/",
    name: "DefaultHome",
    component: () => import("@/views/default/DefaultHome.vue"),
    meta: {
      title: "首页",
      hideInMenu: true,
    },
  },
  {
    path: "/login",
    name: "Login",
    component: () => import("@/views/app-login/AppLogin.vue"),
    meta: {
      title: "登录",
      hideInMenu: true,
    },
  },
  {
    path: "/register",
    name: "Register",
    component: () => import("@/views/app-login/AppRegister.vue"),
    meta: {
      title: "注册",
      hideInMenu: true,
    },
  },
];

export default appLoginRoutes;
