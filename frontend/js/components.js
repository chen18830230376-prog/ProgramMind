/* ============================================================
   ProgramMind 公共组件
   - Layout：整体框架（侧边栏 + 顶栏 + 路由出口），按角色渲染菜单，体现权限隔离
   - StatCard：指标卡
   - Spinner：加载动画
   - SourceTags：知识来源标签
   使用全局 Vue / ElementPlus / 图标（已在 main.js 注册）
   ============================================================ */
window.PM = window.PM || {};

(function () {
  const { defineComponent, computed, ref, reactive, onMounted, onUnmounted } = Vue;

  // ---------------------------------------------------------------------------
  // 通用头像组件（类似学习通：未设置头像时显示「姓名首字 + 自动配色」圆形字）
  //   src 为空            → 姓名首字 + 依姓名哈希的柔和配色
  //   src = "emoji:🦊"     → 彩色圆底 + emoji
  //   src = "data:image/…" 或 http(s)://… → 圆内图片
  // 用法：<pm-avatar :name="u.name" :src="u.avatar" :size="36" />
  // ---------------------------------------------------------------------------
  PM.Avatar = defineComponent({
    props: {
      name: { type: String, default: "" },
      src: { type: String, default: "" },
      size: { type: Number, default: 36 },
    },
    setup(props) {
      const PALETTE = ["#165DFF", "#36CFC9", "#722ED1", "#F53C3C", "#FF7D00",
        "#3491FA", "#7C4DFF", "#2DD4BF", "#EC5990", "#27C397", "#F7BA1E", "#0FC6C2"];
      function hash(str) {
        let h = 0;
        for (let i = 0; i < str.length; i++) h = (h * 31 + str.charCodeAt(i)) >>> 0;
        return h;
      }
      const color = computed(() => PALETTE[hash((props.name || props.src || "?").trim()) % PALETTE.length]);
      const initial = computed(() => {
        const n = (props.name || "?").trim();
        if (!n) return "?";
        return /[一-龥]/.test(n) ? n.slice(-1) : n[0].toUpperCase();
      });
      const kind = computed(() => {
        const s = props.src || "";
        if (s.startsWith("data:image/") || s.startsWith("http://") || s.startsWith("https://")) return "img";
        if (s.startsWith("emoji:")) return "emoji";
        return "text";
      });
      const emoji = computed(() => (props.src || "").replace(/^emoji:/, ""));
      const fontSize = computed(() => Math.round(props.size * 0.42) + "px");
      return { color, initial, kind, emoji, fontSize };
    },
    template: `
      <span class="pm-avatar" :style="{
        width: size + 'px', height: size + 'px',
        background: kind === 'img' ? 'transparent' : color,
        fontSize: fontSize,
      }">
        <img v-if="kind === 'img'" :src="src" alt=""/>
        <span v-else-if="kind === 'emoji'" class="pm-avatar-emoji">{{ emoji }}</span>
        <span v-else>{{ initial }}</span>
      </span>`,
  });

  // 角色化菜单（权限隔离核心：学生看不到教学模块，教师看不到学生专属模块）
  // AI 功能按角色分别整合为独立分组：教师「AI 教学中心」/ 学生「AI 学习中心」
  const MENUS = {
    teacher: [
      { group: "工作台", items: [
        { name: "工作台首页", to: "/workspace", icon: "HomeFilled" },
      ]},
      { group: "教学中心", items: [
        { name: "我的课程", to: "/teach/courses", icon: "Notebook" },
        { name: "知识网络", to: "/teach/knowledge", icon: "Connection" },
        { name: "实验管理", to: "/teach/experiment", icon: "Cpu" },
        { name: "作业管理", to: "/teach/homework", icon: "Document" },
        { name: "学情分析", to: "/teach/analytics", icon: "TrendCharts" },
      ]},
      { group: "AI 教学中心", items: [
        { name: "AI 智能命题", to: "/teach/question", icon: "Promotion" },
        { name: "AI 教案生成", to: "/teach/lesson-plan", icon: "EditPen" },
        { name: "AI PPT 生成", to: "/teach/ppt", icon: "Picture" },
        { name: "AI 教材分析", to: "/teach/textbook", icon: "Files" },
        { name: "AI 学情总结", to: "/teach/ai-summary", icon: "TrendCharts" },
        { name: "AI 通用工具", to: "/ai", icon: "MagicStick" },
      ]},
      { group: "成长与个人", items: [
        { name: "成长模块", to: "/growth", icon: "DataLine" },
        { name: "个人中心", to: "/profile", icon: "User" },
      ]},
    ],
    student: [
      { group: "工作台", items: [
        { name: "工作台首页", to: "/workspace", icon: "HomeFilled" },
      ]},
      { group: "学习中心", items: [
        { name: "我的课程", to: "/learn/courses", icon: "Notebook" },
        { name: "今日学习", to: "/learn/today", icon: "Calendar" },
        { name: "课程实验", to: "/learn/experiment", icon: "Cpu" },
        { name: "作业", to: "/learn/homework", icon: "EditPen" },
        { name: "测验", to: "/learn/quiz", icon: "Memo" },
        { name: "学习资料", to: "/learn/materials", icon: "Files" },
        { name: "学习记录", to: "/learn/records", icon: "Collection" },
      ]},
      { group: "AI 学习中心", items: [
        { name: "AI 学习辅导", to: "/learn/ai-tutor", icon: "ChatDotRound" },
        { name: "AI 代码调试", to: "/learn/ai-debug", icon: "Cpu" },
        { name: "AI 复习规划", to: "/learn/ai-review", icon: "Reading" },
        { name: "AI 通用工具", to: "/ai", icon: "MagicStick" },
      ]},
      { group: "成长与个人", items: [
        { name: "成长模块", to: "/growth", icon: "DataLine" },
        { name: "个人中心", to: "/profile", icon: "User" },
      ]},
    ],
  };

  // 页面标题映射（顶栏显示）
  const TITLES = {
    "/workspace": "工作台 · 任务中心",
    "/teach/courses": "我的课程", "/teach/lesson-plan": "AI 教案生成",
    "/teach/ppt": "PPT 辅助生成", "/teach/textbook": "教材管理",
    "/teach/knowledge": "知识网络", "/teach/question": "AI 智能命题 & 题库",
    "/teach/experiment": "实验管理", "/teach/homework": "作业管理", "/teach/analytics": "学情分析",
    "/teach/lesson-plan": "AI 教案生成", "/teach/ppt": "AI PPT 生成",
    "/teach/textbook": "AI 教材分析", "/teach/ai-summary": "AI 学情总结",
    "/learn/courses": "我的课程", "/learn/today": "今日学习",
    "/learn/ai-tutor": "AI 学习辅导",
    "/learn/homework": "作业", "/learn/quiz": "测验中心",
    "/learn/experiment": "课程实验",
    "/learn/quiz-import": "导入题库",
    "/learn/materials": "学习资料", "/learn/records": "学习记录",
    "/learn/ai-debug": "AI 代码调试", "/learn/ai-review": "AI 复习规划",
    "/ai": "AI 通用工具 · 能力中心", "/growth": "成长模块", "/profile": "个人中心",
  };

  PM.Layout = defineComponent({
    setup() {
      const route = VueRouter.useRoute();
      const router = VueRouter.useRouter();
      const store = PM.store;
      const notifications = ref([]);
      const notiVisible = ref(false);

      const menu = computed(() => MENUS[store.role] || MENUS.student);
      const title = computed(() => TITLES[route.path] || "ProgramMind");
      const unreadCount = computed(() => notifications.value.filter(n => !n.read).length);

      // 当前激活项：精确匹配优先，否则前缀匹配（分组高亮）
      function isActive(to) {
        if (route.path === to) return true;
        return false;
      }

      // 拉取通知：只更新消息列表/红点，不再自动弹窗打扰
      async function refreshNoti() {
        const r = await PM.api("/api/notifications");
        if (r.code !== 0) return;
        notifications.value = r.data || [];
      }

      let notiTimer = null;
      onMounted(async () => {
        await refreshNoti();
        // 每 12 秒轮询一次，仅刷新红点与列表
        notiTimer = setInterval(refreshNoti, 12000);
      });
      onUnmounted(() => { if (notiTimer) clearInterval(notiTimer); });

      async function markRead(n) {
        if (n.read) return;
        await PM.api("/api/notifications/read", { method: "POST", body: JSON.stringify({ id: n.id }) });
        await refreshNoti();
      }
      async function markAllRead() {
        if (!unreadCount.value) return;
        await PM.api("/api/notifications/read", { method: "POST", body: JSON.stringify({ id: "all" }) });
        await refreshNoti();
      }

      async function doLogout() {
        await PM.api("/api/auth/logout", { method: "POST" });
        PM.logout();
        router.push("/login");
      }
      function goProfile() { router.push("/profile"); }

      return { PM, store, menu, title, route, isActive, notifications, notiVisible, unreadCount,
               refreshNoti, markRead, markAllRead, doLogout, goProfile };
    },
    template: `
    <div class="pm-layout">
      <!-- 侧边栏（可折叠，毛玻璃质感） -->
      <aside class="pm-sidebar" :class="{collapsed: store.sidebarCollapsed}">
        <div class="pm-logo">
          <span class="mark">PM</span><span>ProgramMind</span>
        </div>
        <div style="overflow:auto;flex:1">
          <template v-for="g in menu" :key="g.group">
            <div class="pm-nav-group">{{ g.group }}</div>
            <div v-for="it in g.items" :key="it.to"
                 class="pm-nav-item" :class="{active: isActive(it.to)}"
                 :title="store.sidebarCollapsed ? it.name : ''"
                 @click="$router.push(it.to)">
              <span class="ic"><el-icon><component :is="it.icon"/></el-icon></span>
              <span>{{ it.name }}</span>
            </div>
          </template>
        </div>
        <div class="pm-side-foot">AI-Native · 任务优先 · 知识可信</div>
      </aside>

      <!-- 主区 -->
      <div class="pm-main">
        <header class="pm-topbar">
          <div style="display:flex;align-items:center;gap:14px;min-width:0">
            <button class="pm-icon-btn" @click="store.sidebarCollapsed=!store.sidebarCollapsed"
                    :title="store.sidebarCollapsed?'展开菜单':'收起菜单'">
              <el-icon size="17"><component :is="store.sidebarCollapsed?'Expand':'Fold'"/></el-icon>
            </button>
            <div class="pm-page-title">
              <b>{{ title }}</b>
              <span>{{ store.role==='teacher'?'教师教学工作台':'学生学习工作台' }} · AI-Native 教学科研平台</span>
            </div>
          </div>

          <div style="display:flex;align-items:center;gap:12px">
            <el-input placeholder="搜索课程 / 知识点" style="width:210px" size="default">
              <template #prefix><el-icon><Search/></el-icon></template>
            </el-input>
            <span class="pm-icon-btn" role="button" tabindex="0" @click="PM.toggleTheme()"
                  @keyup.enter="PM.toggleTheme()" style="cursor:pointer">
              <el-tooltip :content="store.theme==='dark'?'切换浅色模式':'切换暗黑模式'" placement="bottom">
                <span style="display:inline-flex;align-items:center;justify-content:center;width:100%;height:100%">
                  <el-icon size="17"><component :is="store.theme==='dark'?'Sunny':'Moon'"/></el-icon>
                </span>
              </el-tooltip>
            </span>
            <el-popover :visible="notiVisible" placement="bottom-end" :width="320" trigger="click">
              <template #reference>
                <el-badge :value="unreadCount" :max="9" :hidden="unreadCount===0" @click="notiVisible=!notiVisible">
                  <button class="pm-icon-btn"><el-icon size="17"><Bell/></el-icon></button>
                </el-badge>
              </template>
              <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:8px">
                <div style="font-weight:800">消息通知 <span v-if="unreadCount" style="color:#f56c6c;font-size:12px">({{ unreadCount }} 条未读)</span></div>
                <el-button v-if="unreadCount" size="small" text type="primary" @click="markAllRead">全部已读</el-button>
              </div>
              <div v-for="n in notifications" :key="n.id" @click="markRead(n)" style="padding:10px 0;border-top:1px solid var(--pm-border);cursor:pointer">
                <div style="display:flex;align-items:flex-start;gap:8px">
                  <span v-if="!n.read" style="width:7px;height:7px;border-radius:50%;background:#f56c6c;margin-top:6px;flex-shrink:0"></span>
                  <span v-else style="width:7px;height:7px;flex-shrink:0"></span>
                  <div style="flex:1">
                    <div style="font-size:13px;font-weight:700" :style="{color: n.read ? 'var(--pm-text-soft)' : 'var(--pm-text)'}">{{ n.title }}</div>
                    <div class="pm-muted" style="font-size:12px;line-height:1.5">{{ n.text }}</div>
                    <div class="pm-faint" style="font-size:11px;margin-top:3px">{{ n.time }}</div>
                  </div>
                </div>
              </div>
              <div v-if="!notifications.length" class="pm-empty" style="padding:16px">暂无消息</div>
            </el-popover>
            <el-dropdown @command="c=>c==='logout'?doLogout():goProfile()">
              <div class="pm-user-chip">
                <pm-avatar :name="(store.user && store.user.name) || ''" :src="(store.user && store.user.avatar) || ''" :size="32"/>
                <span style="font-size:13px;font-weight:700">{{ store.user && store.user.name }}</span>
                <el-icon size="12"><ArrowDown/></el-icon>
              </div>
              <template #dropdown>
                <el-dropdown-menu>
                  <el-dropdown-item command="profile"><el-icon><User/></el-icon> 个人中心</el-dropdown-item>
                  <el-dropdown-item command="logout" divided><el-icon><SwitchButton/></el-icon> 退出登录</el-dropdown-item>
                </el-dropdown-menu>
              </template>
            </el-dropdown>
          </div>
        </header>

        <!-- 路由出口：子页面在此渲染 -->
        <main style="flex:1;overflow:auto">
          <router-view v-slot="{ Component }">
            <transition name="pm-fade" mode="out-in">
              <component :is="Component" />
            </transition>
          </router-view>
        </main>
      </div>
    </div>
    `,
  });

  // 指标卡
  PM.StatCard = defineComponent({
    props: { label: String, value: [String, Number], sub: String, icon: String, color: { type: String, default: "#165DFF" } },
    template: `
    <div class="pm-card" style="display:flex;align-items:center;gap:14px">
      <div :style="{background:color+'1a',color:color,width:46,height:46,borderRadius:12,display:'flex',alignItems:'center',justifyContent:'center'}">
        <el-icon size="22"><component :is="icon"/></el-icon>
      </div>
      <div>
        <div style="font-size:22px;font-weight:800">{{ value }}</div>
        <div class="pm-muted" style="font-size:12px">{{ label }}</div>
        <div v-if="sub" class="pm-faint" style="font-size:11px">{{ sub }}</div>
      </div>
    </div>`,
  });

  // 加载动画
  PM.Spinner = defineComponent({
    props: { text: { type: String, default: "加载中…" } },
    template: `
    <div style="display:flex;flex-direction:column;align-items:center;justify-content:center;padding:60px;color:var(--pm-text-soft)">
      <el-icon class="is-loading" size="34" color="#165DFF"><Loading/></el-icon>
      <div style="margin-top:10px;font-size:13px">{{ text }}</div>
    </div>`,
  });

  // 章节标题
  PM.SectionTitle = defineComponent({
    props: { title: String },
    template: `<div class="pm-section-title"><span class="bar"></span>{{ title }}</div>`,
  });

  // ---------------------------------------------------------------------------
  // 知识来源面板（方案 B：可展开 + 可点击查看真实内容）
  //   props.sources —— 真实检索来源 [{index, document, score}]（来自正式 RAG，不做任何猜测）
  //   props.cited   —— 回答正文里实际引用的知识片段编号，用于只展示"被引用到"的来源
  //   props.query   —— 本次提问，点击来源时用它向 /api/knowledge/source 取回真实片段内容
  //   props.course  —— 当前课程（可选，用于课程/章节归属推断）
  //   默认收起；没有来源或无引用时整体不渲染
  // ---------------------------------------------------------------------------
  PM.KnowledgeSources = defineComponent({
    props: {
      sources: { type: Array, default: () => [] },
      // 传入引用的知识片段编号（数组）时只展示被引用到的来源；
      // 传 [] 表示"本次回答没有引用"→ 整个面板不渲染（需求：无引用不显示来源区域）；
      // 不传该属性则展示全部检索来源。
      cited: { type: Array, default: undefined },
      query: { type: String, default: "" },
      course: { type: String, default: "" },
      defaultOpen: { type: Boolean, default: false },
    },
    setup(props) {
      const open = ref(props.defaultOpen);
      const detail = reactive({ open: false, loading: false, error: "", data: null });

      // 展示用文件名：去掉上传时自动加的哈希前缀，保留真实来源文件名
      function prettyName(document) {
        const base = String(document || "").replace(/\\/g, "/").split("/").pop() || "";
        return base.replace(/^[0-9a-f]{16,}[_-]/i, "");
      }

      function prettyScore(score) {
        const num = Number(score);
        if (!isFinite(num) || num <= 0) return "";
        return Math.round(num * 100) + "%";
      }

      const items = computed(() => {
        let list = (props.sources || []).filter((s) => s && s.document);
        const cited = props.cited;
        if (Array.isArray(cited)) {
          if (!cited.length) return [];
          const only = list.filter((s) => cited.indexOf(s.index) >= 0);
          if (only.length) list = only;
        }
        // 同一来源文件的多个知识片段在界面上合并为一条
        const seen = {};
        return list.filter((s) => {
          const key = String(s.document);
          if (seen[key]) return false;
          seen[key] = true;
          return true;
        });
      });

      // 点击某条来源 → 按需取回该来源对应的真实知识片段（不预置、不伪造内容）
      async function openDetail(item) {
        detail.open = true;
        detail.loading = true;
        detail.error = "";
        detail.data = null;

        const r = await PM.api("/api/knowledge/source", {
          method: "POST",
          body: JSON.stringify({
            query: props.query || "",
            document: item.document,
            score: item.score,
            index: item.index,
            course: props.course || "",
          }),
        });

        if (r && r.code === 0 && r.source) detail.data = r.source;
        else detail.error = (r && r.msg) || "未取到该知识片段";

        detail.loading = false;
      }

      return { open, items, prettyName, prettyScore, detail, openDetail };
    },
    template: `
    <div v-if="items.length" class="pm-src">
      <button type="button" class="pm-src-head" :class="{'is-open': open}" @click="open = !open">
        <span class="pm-src-emoji">📚</span>
        <span>知识来源 · {{ items.length }} 条</span>
        <span class="pm-src-caret">›</span>
      </button>
      <div v-show="open" class="pm-src-body">
        <div v-for="(s, k) in items" :key="k" class="pm-src-item is-clickable"
             title="点击查看该来源的真实知识片段" @click="openDetail(s)">
          <span class="pm-src-dot">›</span>
          <div class="pm-src-text">
            <div class="pm-src-name">{{ prettyName(s.document) }}</div>
            <div class="pm-src-meta" v-if="prettyScore(s.score)">相关度 {{ prettyScore(s.score) }}</div>
          </div>
          <span class="pm-src-open">查看</span>
        </div>
      </div>
      <el-dialog v-model="detail.open" title="知识来源详情" width="680px" append-to-body>
        <div v-if="detail.loading" class="pm-src-loading">正在读取真实知识片段…</div>
        <div v-else-if="detail.error" class="pm-src-error">{{ detail.error }}</div>
        <div v-else-if="detail.data" class="pm-src-detail">
          <div class="pm-src-detail-title">{{ prettyName(detail.data.source) }}</div>
          <div class="pm-src-chips">
            <span v-if="detail.data.course_name" class="pm-src-chip">课程：{{ detail.data.course_name }}</span>
            <span v-if="detail.data.chapter" class="pm-src-chip">章节：{{ detail.data.chapter }}</span>
            <span v-if="detail.data.title" class="pm-src-chip">标题：{{ detail.data.title }}</span>
            <span v-if="prettyScore(detail.data.score)" class="pm-src-chip">相似度 {{ prettyScore(detail.data.score) }}</span>
            <span v-if="detail.data.chunk_id !== null && detail.data.chunk_id !== undefined" class="pm-src-chip">片段序号 {{ detail.data.chunk_id }}</span>
          </div>
          <div class="pm-src-content">{{ detail.data.content }}</div>
          <div class="pm-src-note">以上内容来自课程知识库的真实检索结果，未做任何改写。</div>
        </div>
      </el-dialog>
    </div>`,
  });
})();
