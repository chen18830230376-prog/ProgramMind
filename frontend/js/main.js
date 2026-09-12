/* ============================================================
   ProgramMind 前端启动入口（main.js）
   1. 创建 Vue 应用，注册 Element Plus 与全部图标
   2. 挂载路由
   3. 启动前恢复登录态（会话保持），随后挂载并移除首屏动画
   ============================================================ */
(function () {
  const app = Vue.createApp({
    template: "<router-view></router-view>",
  });

  // 注册 Element Plus 组件库
  app.use(ElementPlus);
  // 注册全部 Element Plus 图标为全局组件（菜单/按钮可直接 <IconName/> 使用）
  if (window.ElementPlusIconsVue) {
    for (const [name, comp] of Object.entries(window.ElementPlusIconsVue)) {
      app.component(name, comp);
    }
  }

  // 注册项目公共组件（PM-StatCard / PM-Spinner / PM-SectionTitle 等）
  // 以多种命名形式注册，确保模板中 <PM-StatCard> / <pm-stat-card> 均可解析
  ["StatCard", "Spinner", "SectionTitle", "KnowledgeSources"].forEach((n) => {
    app.component("PM" + n, PM[n]);
    app.component("PM-" + n, PM[n]);
    app.component("pm-" + n.toLowerCase(), PM[n]);
  });

  // 通用头像组件：<pm-avatar>（未设置时显示姓名首字，类似学习通）
  app.component("pm-avatar", PM.Avatar);

  // 挂载路由
  app.use(PM.router);

  // 启动前恢复登录态（刷新不丢登录），再挂载应用
  PM.initAuth().finally(() => {
    app.mount("#app");
    const boot = document.getElementById("boot-screen");
    if (boot) boot.remove();
  });
})();
