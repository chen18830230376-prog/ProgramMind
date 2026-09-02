import {
  createRouter,
  createWebHistory
} from "vue-router"


const routes = [

  // =========================
  // 登录
  // =========================

  {
    path: "/login",

    name: "Login",

    component: () =>
      import("../views/Login/Login.vue"),

    meta: {
      requiresAuth: false
    }

  },


  // =========================
  // 主系统
  // =========================

  {
    path: "/",

    component: () =>
      import("../layouts/MainLayout.vue"),

    meta: {
      requiresAuth: true
    },

    children: [

      // 首页
      {
        path: "",

        redirect: "/workspace"

      },


      // 首页工作台
      {
        path: "workspace",

        name: "Workspace",

        component: () =>
          import("../views/Workspace/Home.vue"),

        meta: {
          requiresAuth: true
        }

      },


      // 知识地图
      {
        path: "knowledge",

        name: "Knowledge",

        component: () =>
          import("../views/Knowledge/KnowledgeMap.vue"),

        meta: {
          requiresAuth: true
        }

      },


      // 状态仪表盘
      {
        path: "dashboard",

        name: "Dashboard",

        component: () =>
          import("../views/Dashboard/Dashboard.vue"),

        meta: {
          requiresAuth: true
        }

      },


      // 成长轨迹
      {
        path: "growth",

        name: "Growth",

        component: () =>
          import("../views/Growth/GrowthTimeline.vue"),

        meta: {
          requiresAuth: true
        }

      },


      // 导航建议
      {
        path: "navigation",

        name: "Navigation",

        component: () =>
          import("../views/Navigation/Navigation.vue"),

        meta: {
          requiresAuth: true
        }

      },


      // 成长报告
      {
        path: "report",

        name: "Report",

        component: () =>
          import("../views/Report/GrowthReport.vue"),

        meta: {
          requiresAuth: true
        }

      }

    ]

  }

]


const router = createRouter({

  history: createWebHistory(),

  routes

})


// =========================
// 路由守卫
// =========================

router.beforeEach((to, from, next) => {

  const token =
    localStorage.getItem("token")


  // 需要登录，但是没有 Token
  if (
    to.meta.requiresAuth &&
    !token
  ) {

    next("/login")

    return

  }


  // 已经登录，还访问登录页
  if (
    to.path === "/login" &&
    token
  ) {

    next("/workspace")

    return

  }


  next()

})


export default router