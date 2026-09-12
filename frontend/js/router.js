/* ============================================================
   前端路由（Vue Router）
   - 登录页为公开路由；其余均 requiresAuth
   - 路由守卫：未登录跳转登录页；按角色拦截越权页面（权限隔离）
   - 每个业务页面都有独立 URL 路由（满足“所有页面通过路由访问”）
   ============================================================ */
window.PM = window.PM || {};
(function () {
  const { createRouter, createWebHistory } = VueRouter;

  const routes = [
    { path: "/login", component: PM.Login, meta: { public: true } },
    {
      path: "/",
      component: PM.Layout,
      meta: { requiresAuth: true },
      children: [
        { path: "", redirect: "workspace" },
        { path: "workspace", component: PM.Workspace },

        // 学习模块（学生）
        { path: "learn/courses", component: PM.LearnCourses },
        { path: "learn/today", component: PM.LearnToday },
        { path: "learn/ai-tutor", component: PM.LearnAiTutor },
        { path: "learn/homework", component: PM.LearnHomework },
        { path: "learn/experiment", component: PM.LearnExperiment },
        { path: "learn/quiz", component: PM.LearnQuizCenter },
        { path: "learn/quiz/:id", component: PM.LearnQuizDo },
        { path: "learn/quiz-import", component: PM.LearnQuizImport },
        { path: "learn/materials", component: PM.LearnMaterials },
        { path: "learn/records", component: PM.LearnRecords },
        { path: "learn/ai-debug", component: PM.LearnAiDebug },
        { path: "learn/ai-review", component: PM.LearnAiReview },

        // 教学模块（教师）
        { path: "teach/courses", component: PM.TeachCourses },
        { path: "teach/lesson-plan", component: PM.TeachLessonPlan },
        { path: "teach/ppt", component: PM.TeachPpt },
        { path: "teach/textbook", component: PM.TeachTextbook },
        { path: "teach/knowledge", component: PM.TeachKnowledge },
        { path: "teach/question", component: PM.TeachQuestion },
        { path: "teach/experiment", component: PM.TeachExperiment },
        { path: "teach/homework", component: PM.TeachHomework },
        { path: "teach/analytics", component: PM.TeachAnalytics },
        { path: "teach/ai-summary", component: PM.TeachAiSummary },

        // 公共模块
        { path: "ai", component: PM.AICenter },
        { path: "growth", component: PM.Growth },
        { path: "profile", component: PM.Profile },
      ],
    },
    { path: "/:pathMatch(.*)*", redirect: "/workspace" },
  ];

  const router = createRouter({ history: createWebHistory(), routes });

  // 全局前置守卫：鉴权 + 权限隔离
  router.beforeEach(async (to, from, next) => {
    if (to.path === "/login") {
      return PM.store.loggedIn ? next("/workspace") : next();
    }
    if (!PM.store.loggedIn) {
      const r = await PM.api("/api/auth/me");
      if (r.code !== 0) return next("/login");
      PM.setUser(r.user);
    }
    // 越权拦截：学生不能进教学模块，教师不能进学生专属学习模块
    if (to.path.startsWith("/teach") && PM.store.role !== "teacher") return next("/workspace");
    if (to.path.startsWith("/learn") && PM.store.role !== "student") return next("/workspace");
    next();
  });

  PM.router = router;
})();
