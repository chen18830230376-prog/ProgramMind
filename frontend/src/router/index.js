import {
  createRouter,
  createWebHistory
} from "vue-router"

const routes = [
  // 登录页面
  {
    path: "/login",
    component: () => import("../views/Login/Login.vue")
  },

  // 默认进入登录页
  {
    path: "/",
    redirect: "/login"
  },

  // 主系统
  {
    path: "/app",
    component: () => import("../layouts/MainLayout.vue"),
    children: [
      {
        path: "",
        redirect: "/app/workspace"
      },
      {
        path: "workspace",
        component: () => import("../views/Workspace/Home.vue")
      },
      {
        path: "knowledge",
        component: () => import("../views/Knowledge/KnowledgeMap.vue")
      },
      {
        path: "dashboard",
        component: () => import("../views/Dashboard/Dashboard.vue")
      },
      {
        path: "growth",
        component: () => import("../views/Growth/GrowthTimeline.vue")
      },
      {
        path: "navigation",
        component: () => import("../views/Navigation/Navigation.vue")
      },
      {
        path: "report",
        component: () => import("../views/Report/GrowthReport.vue")
      }
    ]
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

export default router