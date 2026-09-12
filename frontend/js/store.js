/* ============================================================
   ProgramMind 全局状态与基础设施（store）
   - 基于 Vue.reactive 的轻量全局状态（登录态 / 角色 / 主题 / loading）
   - 统一 API 封装（携带会话 Cookie，处理 401）
   - 主题：浅色 / 暗黑 切换，持久化到 localStorage
   无任何构建步骤，纯浏览器全局脚本。
   ============================================================ */
window.PM = window.PM || {};
(function () {
  const { reactive } = Vue;

  // 全局响应式状态
  const store = reactive({
    user: null,
    role: null,            // 'teacher' | 'student'
    loggedIn: false,
    theme: localStorage.getItem("pm-theme") || "light",
    loading: false,
    sidebarCollapsed: false,
  });

  // 应用主题到 <html class="dark">
  function applyTheme(t) {
    store.theme = t;
    localStorage.setItem("pm-theme", t);
    if (t === "dark") document.documentElement.classList.add("dark");
    else document.documentElement.classList.remove("dark");
    // Element Plus 暗黑变量依赖 html.dark，已通过 css-vars.css 自动生效
  }
  function toggleTheme() { applyTheme(store.theme === "dark" ? "light" : "dark"); }

  // 统一请求封装
  async function api(path, opts = {}) {
    store.loading = true;
    try {
      const res = await fetch(path, {
        credentials: "same-origin",
        headers: { "Content-Type": "application/json" },
        ...opts,
      });
      let data = {};
      try { data = await res.json(); } catch (e) { data = {}; }
      if (res.status === 401) {
        // 会话失效：清空登录态（路由守卫会跳转登录页）
        store.loggedIn = false; store.user = null; store.role = null;
        data.code = 401;
      }
      return data;
    } catch (e) {
      return { code: -1, msg: "网络请求失败：" + e.message };
    } finally {
      store.loading = false;
    }
  }

  // 启动时恢复登录态（刷新页面不丢登录）
  async function initAuth() {
    const r = await api("/api/auth/me");
    if (r.code === 0 && r.user) {
      store.user = r.user; store.role = r.user.role; store.loggedIn = true;
    }
    return r;
  }

  function setUser(u) { store.user = u; store.role = u.role; store.loggedIn = true; }
  function logout() { store.loggedIn = false; store.user = null; store.role = null; }

  // 统一 AI 调用：所有 AI 功能经此后端流式接口（/api/ai/generate）。
  // 后端默认返回 Mock 演示文案；配置本地大模型环境变量后自动切换真实模型。
  // onChunk(已清洗的累积文本) 在每次收到分块时回调；
  // onDone(已清洗全文, sources, cited) 在结束时回调：
  //   sources —— 后端透传的真实知识来源 [{index, document, score}]
  //   cited   —— 回答里实际引用的知识片段编号（对应 sources[].index）
  // 若后端不可达，自动回退到前端 mock-ai.js（PM.mockTask），保证离线可用。
  // ---------------------------------------------------------------------------
  // 内部 RAG 引用标记：只用于对应知识来源，不应出现在用户看到的正文里。
  // 实际会出现的写法（已实测）：
  //     [知识片段1]   [知识片段 2]   【知识片段3】   “知识片段 6”
  // 规则：必须带左括号或左引号，右括号 / 右引号可有可无（避免误删正文）。
  const CITATION_RE = /[\[【（(“"']\s*知识片段\s*(\d+)\s*[\]】）)”"']?/g;

  // 提取正文中被引用的知识片段编号（去重、保持出现顺序）
  function parseCitations(text) {
    const out = [];
    String(text || "").replace(CITATION_RE, (m, n) => {
      const num = parseInt(n, 10);
      if (num && out.indexOf(num) < 0) out.push(num);
      return m;
    });
    return out;
  }

  // 从正文中移除内部引用标记（只删标记本身与其留下的多余空白，不删正文）
  function stripCitations(text) {
    return String(text || "")
      .replace(CITATION_RE, "")
      .replace(/[ \t]+(?=\n)/g, "")
      .replace(/([。！？；：，、.!?;:,])[ \t]{2,}/g, "$1")
      .replace(/\n{3,}/g, "\n\n");
  }

  async function callAI(task, params, onChunk, onDone) {
    try {
      const res = await fetch("/api/ai/generate", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        credentials: "same-origin",
        body: JSON.stringify({ task, params: params || {}, stream: true }),
      });
      if (!res.ok) throw new Error("HTTP " + res.status);
      const reader = res.body.getReader();
      const decoder = new TextDecoder();
      let buf = "";
      let acc = "";
      let sources = [];
      while (true) {
        const { done, value } = await reader.read();
        if (done) break;
        buf += decoder.decode(value, { stream: true });
        let idx;
        while ((idx = buf.indexOf("\n\n")) >= 0) {
          const evt = buf.slice(0, idx);
          buf = buf.slice(idx + 2);
          const line = evt.split("\n").find((l) => l.startsWith("data:"));
          if (!line) continue;
          let json;
          try { json = JSON.parse(line.slice(5).trim()); } catch (e) { continue; }
          if (json.error) throw new Error(json.error);
          if (json.sources) sources = json.sources;
          if (json.chunk != null) { acc += json.chunk; onChunk && onChunk(stripCitations(acc)); }
        }
      }
      onDone && onDone(stripCitations(acc), sources, parseCitations(acc));
    } catch (e) {
      // 后端不可用 → 回退前端 Mock（仅兜底，正常情况后端返回 Mock 文本）
      const text = PM.mockTask ? PM.mockTask(task, params) : "（AI 服务暂不可用）";
      PM.aiStream(text, (c) => onChunk && onChunk(c), () => onDone && onDone(text, [], []), 10);
    }
  }

  // 初始化主题
  applyTheme(store.theme);

  PM.store = store;
  PM.applyTheme = applyTheme;
  PM.toggleTheme = toggleTheme;
  PM.api = api;
  PM.callAI = callAI;
  PM.stripCitations = stripCitations;
  PM.parseCitations = parseCitations;
  PM.initAuth = initAuth;
  PM.setUser = setUser;
  PM.logout = logout;
})();
