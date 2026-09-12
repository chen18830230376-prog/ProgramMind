/* ============================================================
   学习模块（仅学生可见）
   子页面：我的课程 / 今日学习 / AI 学习辅导 / 作业 / 测验 / 学习资料 / 学习记录

   【本次功能升级】从静态展示变为真实业务闭环：
   - 作业提交 → 写入后端 → 教师端"待批改"同步出现
   - 测验提交 → 服务端判分并实时更新知识掌握度 → 成长画像 / 学情分析联动
   - AI 辅导问答 → 持久化到长期记忆（个人中心可回看）→ 可一键收藏
   - 运行代码 / 查看资料 / 提问 → 自动记入学习行为轨迹（全过程成长记录）
   ============================================================ */
window.PM = window.PM || {};
(function () {
  const { defineComponent, ref, onMounted, reactive, nextTick } = Vue;

  function initChart(el, option) {
    if (!el) return;
    const c = echarts.init(el, document.documentElement.classList.contains("dark") ? "dark" : null);
    c.setOption(option); window.addEventListener("resize", () => c.resize()); return c;
  }

  // ---------------- 我的课程 ----------------
  PM.LearnCourses = defineComponent({
    setup() {
      const d = ref(null);
      const catalog = ref([]);          // 课程广场：全部课程
      const catalogVisible = ref(false);
      const catalogMajor = ref("");     // 当前学生专业（用于“为你推荐”提示）
      const enrolling = ref(null);

      async function load(){ const r = await PM.api("/api/learn/overview"); if (r.code === 0) d.value = r.data; }
      onMounted(load);

      // 打开课程广场：拉取全部课程与“是否已加入”；按专业标注核心课 / 推荐课
      async function openCatalog(){
        catalogVisible.value = true;
        const r = await PM.api("/api/courses/catalog");
        if (r.code === 0){ catalog.value = r.data; catalogMajor.value = r.major || ""; }
      }
      async function enroll(c){
        enrolling.value = c.id;
        const r = await PM.api("/api/learn/enroll", { method: "POST", body: JSON.stringify({ course_id: c.id }) });
        enrolling.value = null;
        if (r.code === 0){
          ElementPlus.ElMessage.success(r.msg || "已加入课程");
          // 刷新“我的课程”与课程广场勾选态
          await load();
          const r2 = await PM.api("/api/courses/catalog");
          if (r2.code === 0) catalog.value = r2.data;
        } else ElementPlus.ElMessage.error(r.msg || "加入失败");
      }
      // 教材封面预览
      const previewVisible = ref(false); const preview = reactive({ title: "", cover: "", course: "" });
      function openBook(c){
        preview.title = c.name + "（教材）"; preview.cover = c.textbook || "/assets/textbooks/default.svg";
        preview.course = c.name; previewVisible.value = true;
      }
      return { d, catalog, catalogMajor, catalogVisible, enrolling, openCatalog, enroll, previewVisible, preview, openBook };
    },
    template: `
    <div class="pm-page pm-anim-in" v-if="d">
      <PM-SectionTitle title="我的课程">
        <template #extra>
          <el-button type="primary" @click="openCatalog">
            <el-icon><Plus/></el-icon> 课程广场 · 选课
          </el-button>
        </template>
      </PM-SectionTitle>

      <div v-if="d.courses.length" class="pm-grid pm-grid-3 pm-stagger">
        <div v-for="c in d.courses" :key="c.id" class="pm-card" style="padding:0;overflow:hidden;cursor:pointer" @click="$router.push('/learn/ai-tutor')">
          <!-- 顶部教材插图区：用本地教材 SVG 填满空白，避免在线 cover 图加载失败 -->
          <div style="position:relative;height:150px;display:flex;align-items:center;justify-content:center;overflow:hidden"
               :style="{ background: 'radial-gradient(circle at 50% 70%, ' + c.color + '25 0%, ' + c.color + '08 70%)' }">
            <img :src="c.textbook || '/assets/textbooks/default.svg'" @click.stop="openBook(c)"
                 :title="'查看《' + c.name + '》教材封面'"
                 style="height:118px;width:auto;object-fit:contain;filter:drop-shadow(0 10px 18px rgba(0,0,0,.28));cursor:pointer"/>
            <el-tag size="small" effect="dark" type="primary"
                    style="position:absolute;left:10px;top:10px;cursor:pointer"
                    @click.stop="openBook(c)">
              <el-icon style="vertical-align:-2px"><Notebook/></el-icon> 配套教材
            </el-tag>
          </div>
          <div style="padding:16px">
            <div style="font-weight:700;font-size:15px">{{ c.name }}</div>
            <div class="pm-muted" style="font-size:12px;margin:6px 0 10px">学习进度 {{ c.progress }}%</div>
            <div class="pm-progress"><i :style="{width:c.progress+'%'}"></i></div>
            <div style="margin-top:12px"><el-button size="small" type="primary" plain>进入学习</el-button></div>
          </div>
        </div>
      </div>
      <div v-else class="pm-card" style="text-align:center;padding:40px">
        <el-empty description="你还没有加入任何课程">
          <el-button type="primary" @click="openCatalog">去课程广场选课</el-button>
        </el-empty>
      </div>

      <!-- 课程广场 / 选课中心 弹窗 -->
      <el-dialog v-model="catalogVisible" title="课程广场 · 选课中心" width="780px">
        <el-alert v-if="catalogMajor" type="success" :closable="false" show-icon
                  style="margin-bottom:14px;border-radius:10px"
                  :title="'你的专业是「' + catalogMajor + '」：已自动加入核心课，下方为你标注了推荐选修课'" />
        <p class="pm-muted" style="font-size:13px;margin-top:0">点击「加入课程」即可学习对应资源（作业 / 测验 / 资料）。</p>
        <div class="pm-grid pm-grid-2">
          <div v-for="c in catalog" :key="c.id" class="pm-card" style="display:flex;gap:14px;align-items:center">
            <div style="position:relative;flex:none;width:96px;height:72px;border-radius:10px;display:flex;align-items:center;justify-content:center;overflow:hidden"
                 :style="{ background: 'radial-gradient(circle at 50% 70%, ' + (c.color||'#165DFF') + '28 0%, ' + (c.color||'#165DFF') + '08 70%)' }">
              <!-- 课程广场：用教材封面填满左侧空白，点击可预览 -->
              <img :src="c.textbook || '/assets/textbooks/default.svg'" @click.stop="openBook(c)"
                   :title="'查看《'+c.name+'》教材封面'"
                   style="height:58px;width:auto;object-fit:contain;filter:drop-shadow(0 6px 12px rgba(0,0,0,.28));cursor:pointer"/>
            </div>
            <div style="flex:1;min-width:0">
              <div style="font-weight:700">
                {{ c.name }} <span class="pm-faint" style="font-weight:400;font-size:12px">{{ c.code }}</span>
                <el-tag v-if="c.core" size="small" type="primary" effect="dark" style="margin-left:6px">核心课</el-tag>
                <el-tag v-else-if="c.recommended" size="small" type="warning" effect="plain" style="margin-left:6px">为你推荐</el-tag>
              </div>
              <div class="pm-faint" style="font-size:12px;margin:4px 0">{{ c.teacher }} · {{ c.student_count }} 人在学</div>
              <div class="pm-faint" style="font-size:12px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis">{{ c.description }}</div>
            </div>
            <el-button v-if="!c.enrolled" type="primary" size="small" :loading="enrolling===c.id" @click="enroll(c)">加入课程</el-button>
            <el-tag v-else type="success" size="small">已加入</el-tag>
          </div>
        </div>
      </el-dialog>

      <!-- 教材封面放大预览 -->
      <el-dialog v-model="previewVisible" :title="preview.title" width="360px" align-center>
        <div style="text-align:center">
          <img :src="preview.cover" style="width:200px;height:auto;border-radius:10px;box-shadow:0 10px 30px rgba(0,0,0,.35)"/>
          <p class="pm-faint" style="font-size:13px;margin-top:12px">配套教材 · {{ preview.course }}</p>
        </div>
      </el-dialog>
    </div><PM-Spinner v-else/>`,
  });

  // ---------------- 今日学习 ----------------
  PM.LearnToday = defineComponent({
    setup() {
      const d = ref(null); const done = reactive({});
      onMounted(async () => { const r = await PM.api("/api/learn/overview"); if (r.code === 0) d.value = r.data; });
      function toggle(i){ done[i] = !done[i]; }
      return { d, done, toggle };
    },
    template: `
    <div class="pm-page pm-anim-in" v-if="d">
      <PM-SectionTitle title="今日学习任务清单"/>
      <div class="pm-grid pm-grid-2">
        <div class="pm-card">
          <div v-for="(t,i) in d.today" :key="i" class="pm-row">
            <el-checkbox :model-value="!!done[i]" @change="toggle(i)"/>
            <div :style="{flex:1,textDecoration: done[i]?'line-through':''}">
              <div style="font-weight:600">{{ t.task }}</div><div class="pm-faint" style="font-size:12px">{{ t.course }}</div>
            </div>
            <el-tag :type="done[i]?'success':'warning'" size="small">{{ done[i]?'已完成':'进行中' }}</el-tag>
          </div>
        </div>
        <div class="pm-card" style="background:linear-gradient(135deg,#165DFF,#4080ff);color:#fff;border:none">
          <div style="font-weight:800;margin-bottom:8px">🤖 AI 今日助力</div>
          <p style="font-size:13px;line-height:1.8">根据昨天的学习轨迹，AI 建议先完成『二叉树遍历』复习（掌握度 70），
          再进入『图的存储』预习。遇到卡点随时问我。</p>
          <el-button size="small" @click="$router.push('/learn/ai-tutor')" style="margin-top:8px">问 AI 辅导</el-button>
        </div>
      </div>
    </div><PM-Spinner v-else/>`,
  });

  // ---------------- AI 学习辅导（RAG 模拟 + 来源追溯 + 长期记忆） ----------------
  PM.LearnAiTutor = defineComponent({
    setup() {
      const course = ref("Python 程序设计");
      const input = ref("");
      const messages = ref([
        { role: "ai", html: "你好，我是 ProgramMind 学科辅导助手 🤖\n我可以基于课程知识库回答你的问题，并标注知识来源，保证可信可追溯。" },
      ]);
      const box = ref(null);

      async function send() {
        const q = input.value.trim(); if (!q) return;
        messages.value.push({ role: "user", html: q });
        input.value = "";
        // 携带 q / course / fav，便于"收藏这条回答"
        const ai = reactive({ role: "ai", html: "", loading: true, q, course: course.value, fav: false, sources: [], cited: [] });
        messages.value.push(ai);
        await PM.callAI("answer", { question: q, course: course.value },
          (chunk) => { ai.html = chunk; },
          async (text, sources, cited) => {
            ai.html = text || ai.html;
            ai.sources = sources || [];
            ai.cited = cited || [];
            ai.loading = false; scrollDown();
            // 【长期记忆】问答入库，个人中心 → 历史 AI 对话 可持续回溯
            await PM.api("/api/ai/chat", {
              method: "POST", body: JSON.stringify({ text: q, answer: ai.html }),
            });
            // 【全过程记录】提问本身也是一次学习行为
            await PM.api("/api/learn/record", {
              method: "POST",
              body: JSON.stringify({ action: "AI 辅导", detail: q.slice(0, 24), course: course.value, duration: 8 }),
            });
          });
        scrollDown();
      }

      // 收藏这条 AI 回答 → 沉淀到个人知识库
      async function fav(m) {
        const r = await PM.api("/api/profile/favorite", {
          method: "POST",
          body: JSON.stringify({ action: "add", title: "Q：" + m.q, type: "AI 回答", course: m.course }),
        });
        if (r.code === 0) { m.fav = true; ElementPlus.ElMessage.success("已收藏，可在『我的 → 收藏』查看"); }
      }
      function scrollDown(){ nextTick(()=>{ if(box.value) box.value.scrollTop = box.value.scrollHeight; }); }
      return { course, input, messages, box, send, fav };
    },
    template: `
    <div class="pm-page pm-anim-in">
      <div class="pm-card" style="display:flex;flex-direction:column;height:calc(100vh - 150px)">
        <div style="display:flex;align-items:center;gap:12px;padding-bottom:12px;border-bottom:1px solid var(--pm-border)">
          <el-icon color="#165DFF" size="22"><ChatDotRound/></el-icon>
          <b>AI 学习辅导 · 知识增强检索</b>
          <el-select v-model="course" size="small" style="width:180px;margin-left:auto">
            <el-option label="Python 程序设计" value="Python 程序设计"/>
            <el-option label="数据结构" value="数据结构"/>
            <el-option label="计算机网络" value="计算机网络"/>
          </el-select>
        </div>
        <div ref="box" style="flex:1;overflow:auto;padding:16px 4px">
          <div v-for="(m,i) in messages" :key="i" style="display:flex;margin-bottom:16px;align-items:flex-end;gap:6px"
               :style="{justifyContent: m.role==='user'?'flex-end':'flex-start'}">
            <div style="max-width:76%;display:flex;flex-direction:column;gap:8px;align-items:flex-start">
              <div :style="{padding:'10px 14px',borderRadius:'14px',whiteSpace:'pre-wrap',lineHeight:'1.7',
                   background: m.role==='user'?'#165DFF':'var(--pm-surface-2)',color: m.role==='user'?'#fff':'var(--pm-text)',border:'1px solid var(--pm-border)'}">
                <span v-if="m.loading" class="pm-cursor" v-html="m.html||' '"></span>
                <span v-else v-html="m.html"></span>
              </div>
              <PM-KnowledgeSources v-if="m.role==='ai' && !m.loading" :sources="m.sources || []" :cited="m.cited || []"
                                   :query="m.q || ''" :course="m.course || ''"/>
            </div>
            <el-button v-if="m.role==='ai' && !m.loading && m.q" circle text size="small"
                       :style="{color: m.fav?'#FF7D00':'var(--pm-text-faint)'}"
                       :title="m.fav?'已收藏':'收藏这条回答'" @click="fav(m)">
              <el-icon><Star/></el-icon>
            </el-button>
          </div>
        </div>
        <div style="display:flex;gap:10px;padding-top:12px;border-top:1px solid var(--pm-border)">
          <el-input v-model="input" placeholder="输入问题，如：装饰器有什么用？" @keyup.enter="send"/>
          <el-button type="primary" @click="send">发送</el-button>
        </div>
      </div>
    </div>`,
  });

  // ---------------- 作业（上传图片提交 → 教师端同步） ----------------
  PM.LearnHomework = defineComponent({
    setup() {
      const list = ref([]); const submitting = ref(null);
      const images = reactive({});          // hw_id -> 已上传图片 URL（提交前本地预览）
      const imgPreview = ref(""); const imgVisible = ref(false);
      async function load(){ const r = await PM.api("/api/learn/homework"); if (r.code === 0) list.value = r.data; }
      onMounted(load);
      function beforeUpload(f){
        if (!f.type || !f.type.startsWith("image/")) { ElementPlus.ElMessage.warning("仅支持上传图片"); return false; }
        if (f.size > 6 * 1024 * 1024) { ElementPlus.ElMessage.warning("图片需小于 6MB"); return false; }
        return true;
      }
      function onSuccess(r, h){ if (r.code === 0) images[h.id] = r.url; else ElementPlus.ElMessage.error(r.msg || "上传失败"); }
      function showImg(u){ if (u) { imgPreview.value = u; imgVisible.value = true; } }
      // 真实提交到后端（携带图片），教师端"待批改"任务会同步出现
      async function submit(h){
        submitting.value = h.id;
        const r = await PM.api("/api/learn/homework/submit", {
          method: "POST", body: JSON.stringify({ hw_id: h.id, image: images[h.id] || null }),
        });
        submitting.value = null;
        if (r.code === 0) { ElementPlus.ElMessage.success(r.msg || "提交成功"); await load(); }
        else ElementPlus.ElMessage.error(r.msg || "提交失败");
      }
      function statusTag(s){ return s==='graded'?'success':(s==='submitted'?'warning':'info'); }
      function statusText(s){ return s==='graded'?'已批改':(s==='submitted'?'待批改':'未提交'); }
      return { list, submit, submitting, images, beforeUpload, onSuccess, showImg, imgPreview, imgVisible, statusTag, statusText };
    },
    template: `
    <div class="pm-page pm-anim-in" v-if="list.length">
      <PM-SectionTitle title="我的作业（可上传图片后提交）"/>
      <div class="pm-grid pm-grid-2 pm-stagger">
        <div v-for="h in list" :key="h.id" class="pm-card">
          <div style="display:flex;justify-content:space-between;align-items:center">
            <b>{{ h.title }}</b><el-tag :type="statusTag(h.status)" size="small">{{ statusText(h.status) }}</el-tag>
          </div>
          <div class="pm-faint" style="font-size:12px;margin:4px 0">{{ h.course }} · 截止 {{ h.due }}</div>
          <p class="pm-muted" style="font-size:13px">{{ h.desc }}</p>

          <!-- 已提交 / 已批改：展示图片（只读） -->
          <img v-if="(h.status==='submitted'||h.status==='graded') && h.image" :src="h.image"
               @click="showImg(h.image)"
               style="width:100%;max-height:170px;object-fit:contain;border-radius:10px;margin:8px 0;cursor:pointer;background:var(--pm-surface-2)"/>
          <div v-if="h.status==='graded'" style="padding:10px;background:rgba(0,180,42,.08);border-radius:10px;margin:8px 0">
            <b>得分：{{ h.score }}</b><div class="pm-muted" style="font-size:12px;margin-top:4px">教师反馈：{{ h.feedback || '—' }}</div>
          </div>

          <!-- 未批改：可上传图片并提交 -->
          <template v-if="h.status!=='graded'">
            <el-upload class="pm-upload" action="/api/upload" :show-file-list="false"
                       :before-upload="beforeUpload" :on-success="(r)=>onSuccess(r, h)"
                       accept="image/*">
              <el-button size="small" plain><el-icon><Upload/></el-icon> 上传作业图片</el-button>
            </el-upload>
            <img v-if="images[h.id]" :src="images[h.id]" @click="showImg(images[h.id])"
                 style="width:100%;max-height:170px;object-fit:contain;border-radius:10px;margin-top:8px;cursor:pointer;background:var(--pm-surface-2)"/>
            <el-button size="small" type="primary" :loading="submitting===h.id" @click="submit(h)">提交作业</el-button>
          </template>
        </div>
      </div>

      <!-- 图片放大预览 -->
      <el-dialog v-model="imgVisible" title="作业图片" width="520px" align-center>
        <div style="text-align:center"><img :src="imgPreview" style="max-width:100%;border-radius:10px"/></div>
      </el-dialog>
    </div><PM-Spinner v-else/>`,
  });

  // ---------------- 课程实验（上传图片 + 文字说明提交 → 教师端批改） ----------------
  PM.LearnExperiment = defineComponent({
    setup() {
      const list = ref([]); const submitting = ref(null);
      const images = reactive({});          // exp_id -> 已上传图片 URL
      const contents = reactive({});        // exp_id -> 文字说明
      const reports = reactive({});         // exp_id -> 已上传报告文件 URL
      const reportNames = reactive({});     // exp_id -> 报告原始文件名（本地预览）
      const IMG_EXT = ["png","jpg","jpeg","gif","webp","bmp"];
      const DOC_EXT = ["pdf","doc","docx","ppt","pptx","xls","xlsx","txt","md","csv","zip","rar"];
      const imgPreview = ref(""); const imgVisible = ref(false);
      async function load(){ const r = await PM.api("/api/learn/experiments"); if (r.code === 0) list.value = r.data; }
      onMounted(load);
      function extOf(name){ const i = (name || "").lastIndexOf("."); return i >= 0 ? name.slice(i + 1).toLowerCase() : ""; }
      function beforeUploadImg(f){
        if (!f.type || !f.type.startsWith("image/")) { ElementPlus.ElMessage.warning("仅支持上传图片"); return false; }
        if (f.size > 6 * 1024 * 1024) { ElementPlus.ElMessage.warning("图片需小于 6MB"); return false; }
        return true;
      }
      function beforeUploadReport(f){
        const ext = extOf(f.name);
        if (!IMG_EXT.includes(ext) && !DOC_EXT.includes(ext)) {
          ElementPlus.ElMessage.warning("请上传实验报告（PDF/Word/PPT/Excel/图片/压缩包等）"); return false;
        }
        if (f.size > 30 * 1024 * 1024) { ElementPlus.ElMessage.warning("文件需小于 30MB"); return false; }
        return true;
      }
      function onSuccessImg(r, e){ if (r.code === 0) images[e.id] = r.url; else ElementPlus.ElMessage.error(r.msg || "上传失败"); }
      function onSuccessReport(r, e, file){ if (r.code === 0) { reports[e.id] = r.url; reportNames[e.id] = (file && file.name) ? file.name : "实验报告"; } else ElementPlus.ElMessage.error(r.msg || "上传失败"); }
      function showImg(u){ if (u) { imgPreview.value = u; imgVisible.value = true; } }
      function reportName(url){ if (!url) return ""; const seg = decodeURIComponent((url.split("/").pop() || "")); const i = seg.indexOf("_"); return i >= 0 ? seg.slice(i + 1) : seg; }
      async function submit(e){
        submitting.value = e.id;
        const r = await PM.api("/api/learn/experiments/submit", {
          method: "POST",
          body: JSON.stringify({ exp_id: e.id, content: contents[e.id] || "", image: images[e.id] || null, file: reports[e.id] || null, file_name: reportNames[e.id] || null }),
        });
        submitting.value = null;
        if (r.code === 0) { ElementPlus.ElMessage.success(r.msg || "提交成功"); await load(); }
        else ElementPlus.ElMessage.error(r.msg || "提交失败");
      }
      function statusTag(s){ return s==='graded'?'success':(s==='submitted'?'warning':'info'); }
      function statusText(s){ return s==='graded'?'已批改':(s==='submitted'?'待批改':'未提交'); }
      return { list, submit, submitting, images, contents, reports, reportNames,
               beforeUploadImg, beforeUploadReport, onSuccessImg, onSuccessReport,
               showImg, reportName, imgPreview, imgVisible, statusTag, statusText };
    },
    template: `
    <div class="pm-page pm-anim-in" v-if="list.length">
      <PM-SectionTitle title="课程实验（上传实验报告并说明后提交）"/>
      <div class="pm-grid pm-grid-2 pm-stagger">
        <div v-for="e in list" :key="e.id" class="pm-card">
          <div style="display:flex;justify-content:space-between;align-items:center">
            <b>{{ e.title }}</b><el-tag :type="statusTag(e.status)" size="small">{{ statusText(e.status) }}</el-tag>
          </div>
          <div class="pm-faint" style="font-size:12px;margin:4px 0">{{ e.course }} · 截止 {{ e.due || '未设' }}</div>
          <p class="pm-muted" style="font-size:13px">{{ e.desc }}</p>

          <!-- 已提交 / 已批改：展示内容（只读） -->
          <p v-if="(e.status==='submitted'||e.status==='graded') && e.content" class="pm-muted" style="font-size:13px;background:var(--pm-surface-2);padding:8px 10px;border-radius:10px;white-space:pre-wrap">{{ e.content }}</p>
          <a v-if="(e.status==='submitted'||e.status==='graded') && e.file" :href="e.file" target="_blank" rel="noopener"
             style="display:inline-flex;align-items:center;gap:6px;margin:8px 0;padding:8px 12px;background:var(--pm-brand-soft);color:var(--pm-brand);border-radius:10px;font-size:13px;text-decoration:none;font-weight:600">
            <el-icon><Document/></el-icon> {{ e.file_name || reportName(e.file) || '查看实验报告' }}
          </a>
          <img v-if="(e.status==='submitted'||e.status==='graded') && e.image" :src="e.image"
               @click="showImg(e.image)"
               style="width:100%;max-height:170px;object-fit:contain;border-radius:10px;margin:8px 0;cursor:pointer;background:var(--pm-surface-2)"/>
          <div v-if="e.status==='graded'" style="padding:10px;background:rgba(0,180,42,.08);border-radius:10px;margin:8px 0">
            <b>得分：{{ e.score }}</b><div class="pm-muted" style="font-size:12px;margin-top:4px">教师反馈：{{ e.feedback || '—' }}</div>
          </div>

          <!-- 未批改：可填写说明 + 上传报告/图片并提交 -->
          <template v-if="e.status!=='graded'">
            <el-input v-model="contents[e.id]" type="textarea" :rows="3" placeholder="实验说明 / 代码（可选）" style="margin:8px 0"/>
            <div style="display:flex;gap:10px;flex-wrap:wrap;align-items:center">
              <el-upload class="pm-upload" action="/api/upload" :show-file-list="false"
                         :before-upload="beforeUploadReport" :on-success="(r,file)=>onSuccessReport(r, e, file)"
                         accept=".pdf,.doc,.docx,.ppt,.pptx,.xls,.xlsx,.txt,.md,.csv,.zip,.rar,image/*">
                <el-button size="small" type="primary" plain><el-icon><Upload/></el-icon> 上传实验报告</el-button>
              </el-upload>
              <el-upload class="pm-upload" action="/api/upload" :show-file-list="false"
                         :before-upload="beforeUploadImg" :on-success="(r)=>onSuccessImg(r, e)"
                         accept="image/*">
                <el-button size="small" plain><el-icon><Upload/></el-icon> 上传截图</el-button>
              </el-upload>
            </div>
            <div v-if="reports[e.id]" style="display:inline-flex;align-items:center;gap:6px;margin-top:8px;padding:6px 10px;background:var(--pm-surface-2);border-radius:10px;font-size:12px">
              <el-icon><Document/></el-icon> {{ reportNames[e.id] || '已选择报告' }}
              <el-icon style="cursor:pointer;margin-left:4px" @click="reports[e.id]=null;reportNames[e.id]=''"><Close/></el-icon>
            </div>
            <img v-if="images[e.id]" :src="images[e.id]" @click="showImg(images[e.id])"
                 style="width:100%;max-height:170px;object-fit:contain;border-radius:10px;margin-top:8px;cursor:pointer;background:var(--pm-surface-2)"/>
            <div style="margin-top:8px">
              <el-button size="small" type="primary" :loading="submitting===e.id" @click="submit(e)">
                {{ e.status==='submitted' ? '重新提交' : '提交实验' }}
              </el-button>
            </div>
          </template>
        </div>
      </div>

      <!-- 图片放大预览 -->
      <el-dialog v-model="imgVisible" title="实验图片" width="520px" align-center>
        <div style="text-align:center"><img :src="imgPreview" style="max-width:100%;border-radius:10px"/></div>
      </el-dialog>
    </div><PM-Spinner v-else/>`,
  });

  // ---------------- 测验中心（系统/教师题库 + 自建题库） ----------------
  PM.LearnQuizCenter = defineComponent({
    setup() {
      const list = ref([]); const loading = ref(false);
      onMounted(async () => {
        loading.value = true;
        const r = await PM.api("/api/learn/quizzes");
        if (r.code === 0) list.value = r.data;
        loading.value = false;
      });
      function sourceLabel(s) {
        return s === "teacher" ? "教师题库" : (s === "student" ? "我的题库" : "系统题库");
      }
      return { list, loading, sourceLabel };
    },
    template: `
    <div class="pm-page pm-anim-in">
      <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:14px">
        <PM-SectionTitle title="测验中心"/>
        <el-button type="primary" @click="$router.push('/learn/quiz-import')"><el-icon><Plus/></el-icon> 导入题库</el-button>
      </div>
      <div v-if="loading" class="pm-empty" style="padding:60px">加载中…</div>
      <div v-else-if="!list.length" class="pm-empty" style="padding:60px">暂无可用测验，请先去导入题库或等待老师发布。</div>
      <div v-else class="pm-grid pm-grid-2 pm-stagger">
        <div v-for="q in list" :key="q.id" class="pm-card" style="display:flex;flex-direction:column;justify-content:space-between">
          <div>
            <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:8px">
              <b style="font-size:15px">{{ q.title }}</b>
              <el-tag size="small" :type="q.source==='teacher'?'primary':(q.source==='student'?'success':'info')" effect="plain">
                {{ sourceLabel(q.source) }}
              </el-tag>
            </div>
            <div class="pm-faint" style="font-size:12px">{{ q.question_count }} 道题 · {{ q.course || '公共题库' }}</div>
          </div>
          <div style="margin-top:12px">
            <el-button size="small" type="primary" @click="$router.push('/learn/quiz/'+q.id)">开始测验</el-button>
          </div>
        </div>
      </div>
    </div>`,
  });

  // ---------------- 做题页（动态 quiz_id） ----------------
  PM.LearnQuizDo = defineComponent({
    setup() {
      const route = VueRouter.useRoute();
      const router = VueRouter.useRouter();
      const quiz = ref(null); const answers = reactive({}); const result = ref(null);
      const chartEl = ref(null); const submitting = ref(false);
      const qid = route.params.id;
      onMounted(async () => { if (!qid) return; const r = await PM.api("/api/learn/quiz/"+qid); if (r.code === 0) quiz.value = r.data; });

      async function submit() {
        submitting.value = true;
        const r = await PM.api("/api/learn/quiz/submit", {
          method: "POST", body: JSON.stringify({ quiz_id: qid, answers }),
        });
        submitting.value = false;
        if (r.code !== 0) { ElementPlus.ElMessage.error(r.msg || "提交失败"); return; }
        const data = r.data;
        result.value = { score: data.score, correct: data.correct, total: data.total, points: data.points, msg: data.msg };
        ElementPlus.ElMessage.success(data.msg || "已提交");
        nextTick(()=> initChart(chartEl.value, {
          grid:{left:80,right:20,top:20,bottom:20},
          tooltip:{},
          xAxis:{type:"value",max:100},
          yAxis:{type:"category",data:data.points.map(p=>p.name).reverse()},
          series:[{type:"bar",data:data.points.map(p=>p.val).reverse(),itemStyle:{color:"#165DFF",borderRadius:6},
            label:{show:true,position:"right",formatter:"{c}"}}],
        }));
      }
      function back(){ router.push('/learn/quiz'); }
      return { quiz, answers, result, chartEl, submitting, submit, back };
    },
    template: `
    <div class="pm-page pm-anim-in" v-if="quiz">
      <PM-SectionTitle :title="'测验 · '+quiz.title"/>
      <div class="pm-card" v-if="!result">
        <div v-for="(q,i) in quiz.questions" :key="i" style="padding:14px 0;border-top:1px solid var(--pm-border)">
          <div style="font-weight:600;margin-bottom:8px">{{ i+1 }}. {{ q.q }}</div>
          <el-radio-group v-model="answers[i]">
            <el-radio v-for="(o,oi) in q.options" :key="oi" :value="oi" border style="margin:4px 0;display:block">{{ o }}</el-radio>
          </el-radio-group>
        </div>
        <div style="display:flex;gap:10px;margin-top:14px">
          <el-button type="primary" :loading="submitting" @click="submit">{{ submitting ? 'AI 分析中…' : '提交并查看分析' }}</el-button>
          <el-button @click="back">返回测验中心</el-button>
        </div>
      </div>
      <div v-else class="pm-grid pm-grid-2">
        <div class="pm-card">
          <div style="font-size:22px;font-weight:800">
            得分：<span style="color:var(--pm-brand)">{{ result.score }}</span> 分（{{ result.correct }}/{{ result.total }} 题）
          </div>
          <div style="margin-top:10px;padding:10px 12px;background:var(--pm-brand-soft);border-radius:10px;color:var(--pm-brand);font-size:12.5px;font-weight:600">
            🤖 {{ result.msg }}
          </div>
          <p class="pm-muted" style="font-size:13px;margin-top:8px">下方为逐知识点掌握分析，结果已同步到你的成长画像与教师的学情分析。</p>
          <div ref="chartEl" style="height:240px"></div>
        </div>
        <div class="pm-card">
          <PM-SectionTitle title="AI 复习建议"/>
          <div v-for="p in result.points" :key="p.name" style="padding:8px 0;border-top:1px solid var(--pm-border);display:flex;justify-content:space-between">
            <span>{{ p.name }}</span>
            <el-tag :type="p.val>=100?'success':'warning'" size="small">{{ p.val>=100?'掌握':'待加强' }}</el-tag>
          </div>
          <el-button type="primary" style="margin-top:12px;width:100%" @click="$router.push('/learn/ai-tutor')">去 AI 辅导复习薄弱点</el-button>
          <el-button class="pm-btn-ghost" style="margin-top:8px;width:100%" @click="$router.push('/growth')">查看成长画像变化</el-button>
          <el-button class="pm-btn-ghost" style="margin-top:8px;width:100%" @click="back">返回测验中心</el-button>
        </div>
      </div>
    </div><PM-Spinner v-else/>`,
  });
  PM.LearnQuiz = PM.LearnQuizDo;  // 兼容旧引用

  // ---------------- 学生导入题库（单题添加 / JSON 批量） ----------------
  PM.LearnQuizImport = defineComponent({
    setup() {
      const router = VueRouter.useRouter();
      const store = PM.store;
      const title = ref("");
      const activeTab = ref("manual");
      const jsonText = ref("");
      const questions = reactive([]);
      const saving = ref(false);

      function addQuestion(){
        questions.push({ q: "", options: ["", ""], answer: 0, point: "" });
      }
      function removeQuestion(idx){ questions.splice(idx, 1); }
      function addOption(q){ q.options.push(""); }
      function removeOption(q, oi){ if (q.options.length > 2) q.options.splice(oi, 1); }

      async function save(){
        let payload = [];
        if (activeTab.value === "manual") {
          const valid = questions.filter(q => q.q.trim() && q.options.filter(o => o.trim()).length >= 2);
          if (!valid.length) { ElementPlus.ElMessage.warning("请至少添加一道完整题目"); return; }
          payload = valid.map(q => ({ q: q.q.trim(), options: q.options.map(o => o.trim()), answer: q.answer, point: q.point.trim() || "综合" }));
        } else {
          try {
            const parsed = JSON.parse(jsonText.value);
            payload = Array.isArray(parsed) ? parsed : (parsed.questions || []);
            if (!payload.length) throw new Error("空题库");
          } catch (e) {
            ElementPlus.ElMessage.error("JSON 格式不正确或没有题目"); return;
          }
        }
        saving.value = true;
        const r = await PM.api("/api/learn/quiz/import", {
          method: "POST",
          body: JSON.stringify({ title: title.value || "我的导入题库", questions: payload }),
        });
        saving.value = false;
        if (r.code === 0) {
          ElementPlus.ElMessage.success(r.msg || "导入成功");
          router.push('/learn/quiz');
        } else {
          ElementPlus.ElMessage.error(r.msg || "导入失败");
        }
      }

      addQuestion();
      return { store, title, activeTab, jsonText, questions, saving, addQuestion, removeQuestion, addOption, removeOption, save };
    },
    template: `
    <div class="pm-page pm-anim-in">
      <PM-SectionTitle title="导入题库"/>
      <div class="pm-card">
        <div style="font-weight:600;margin-bottom:10px">题库名称</div>
        <el-input v-model="title" placeholder="例如：数据结构复习题库" style="margin-bottom:16px"/>

        <el-tabs v-model="activeTab" type="border-card">
          <el-tab-pane label="手动添加" name="manual">
            <div v-for="(q, qi) in questions" :key="qi" style="padding:14px 0;border-top:1px solid var(--pm-border)">
              <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:8px">
                <b>题目 {{ qi+1 }}</b>
                <el-button size="small" type="danger" plain @click="removeQuestion(qi)">删除</el-button>
              </div>
              <el-input v-model="q.q" type="textarea" :rows="2" placeholder="题干" style="margin-bottom:8px"/>
              <div style="display:flex;gap:10px;align-items:center;margin-bottom:8px;flex-wrap:wrap">
                <span class="pm-faint" style="font-size:12px">选项：</span>
                <div v-for="(o, oi) in q.options" :key="oi" style="display:flex;gap:6px;align-items:center">
                  <el-radio v-model="q.answer" :value="oi">{{ String.fromCharCode(65+oi) }}</el-radio>
                  <el-input v-model="q.options[oi]" placeholder="选项内容" style="width:180px"/>
                  <el-button size="small" text @click="removeOption(q, oi)" v-if="q.options.length>2">删</el-button>
                </div>
                <el-button size="small" text @click="addOption(q)">+ 选项</el-button>
              </div>
              <el-input v-model="q.point" placeholder="知识点标签（如：栈）" style="width:220px"/>
            </div>
            <el-button type="primary" plain style="margin-top:10px" @click="addQuestion"><el-icon><Plus/></el-icon> 添加题目</el-button>
          </el-tab-pane>

          <el-tab-pane label="JSON 批量导入" name="json">
            <el-input v-model="jsonText" type="textarea" :rows="10" placeholder='粘贴 JSON 题库，格式示例：
[
  {"q":"栈的特点是？","options":["FIFO","LIFO","随机","有序"],"answer":1,"point":"栈"},
  {"q":"链表的优势是？","options":["随机访问快","插入删除灵活","空间更小","缓存友好"],"answer":1,"point":"链表"}
]'/>
          </el-tab-pane>
        </el-tabs>

        <div style="margin-top:16px">
          <el-button type="primary" :loading="saving" @click="save">保存题库</el-button>
          <el-button @click="$router.push('/learn/quiz')">取消</el-button>
        </div>
      </div>
    </div>`,
  });

  // ---------------- 学习资料：教材 + 课件分开展示 ----------------
  PM.LearnMaterials = defineComponent({
    setup() {
      const d = ref(null); const typeIcon = { "教材":"Notebook","PPT":"Picture","实验指导":"Cpu","代码":"Document","资料":"Files" };
      const previewVisible = ref(false); const preview = reactive({ title: "", cover: "", course: "" });
      onMounted(async () => { const r = await PM.api("/api/learn/overview"); if (r.code === 0) d.value = r.data; });
      async function recordView(m) {
        await PM.api("/api/learn/record", {
          method: "POST",
          body: JSON.stringify({ action: "查看资料", detail: m.title, course: m.course, duration: 10 }),
        });
      }
      async function openBook(b) {
        await recordView(b);
        preview.title = b.title; preview.cover = b.cover; preview.course = b.course_name || b.course;
        previewVisible.value = true;
      }
      async function openLink(m) {
        await recordView(m);
        if (m.link) {
          window.open(m.link, "_blank");
          ElementPlus.ElMessage.success("已打开课件《" + m.title + "》新标签页");
        }
      }
      return { d, typeIcon, previewVisible, preview, openBook, openLink };
    },
    template: `
    <div class="pm-page pm-anim-in" v-if="d">
      <!-- 教材专区 -->
      <PM-SectionTitle title="教材"/>
      <div v-if="d.textbooks && d.textbooks.length" class="pm-grid pm-grid-4 pm-stagger" style="margin-bottom:28px">
        <div v-for="b in d.textbooks" :key="b.title" class="pm-card" style="text-align:center;cursor:pointer" @click="openBook(b)">
          <img :src="b.cover || '/assets/textbooks/default.svg'"
               style="width:84px;height:118px;object-fit:cover;border-radius:8px;box-shadow:0 8px 22px rgba(0,0,0,.28);margin-bottom:10px"/>
          <div style="font-weight:700;font-size:14px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis">{{ b.course_name }}</div>
          <div class="pm-faint" style="font-size:12px">配套教材 · 点击查看大图</div>
        </div>
      </div>
      <div v-else class="pm-card" style="text-align:center;padding:30px;margin-bottom:28px"><el-empty description="暂无教材"/></div>

      <!-- 学习资料专区：只保留有外链的课件 -->
      <PM-SectionTitle title="学习资料"/>
      <div v-if="d.materials && d.materials.length" class="pm-grid pm-grid-2 pm-stagger">
        <div v-for="m in d.materials" :key="m.title" class="pm-card" style="display:flex;gap:14px;align-items:center">
          <div style="width:46px;height:46px;border-radius:12px;background:var(--pm-brand-soft);color:var(--pm-brand);display:flex;align-items:center;justify-content:center;flex:none">
            <el-icon size="22"><component :is="typeIcon[m.type]||'Files'"/></el-icon></div>
          <div style="flex:1;min-width:0">
            <div style="font-weight:600;white-space:nowrap;overflow:hidden;text-overflow:ellipsis">{{ m.title }}</div>
            <div class="pm-faint" style="font-size:12px">{{ m.course_name || m.course }}</div>
          </div>
          <el-button size="small" type="primary" link @click="openLink(m)">打开课件 ↗</el-button>
          <el-tag size="small">{{ m.type }}</el-tag>
        </div>
      </div>
      <div v-else class="pm-card" style="text-align:center;padding:30px"><el-empty description="暂无课件链接"/></div>

      <!-- 教材封面放大预览 -->
      <el-dialog v-model="previewVisible" :title="preview.title" width="360px" align-center>
        <div style="text-align:center">
          <img :src="preview.cover" style="width:200px;height:auto;border-radius:10px;box-shadow:0 10px 30px rgba(0,0,0,.35)"/>
          <p class="pm-faint" style="font-size:13px;margin-top:12px">配套教材 · {{ preview.course }}</p>
        </div>
      </el-dialog>
    </div><PM-Spinner v-else/>`,
  });

  // ---------------- 学习记录（过程化轨迹，实时反映各模块行为） ----------------
  PM.LearnRecords = defineComponent({
    setup() {
      const d = ref(null);
      async function load(){ const r = await PM.api("/api/learn/overview"); if (r.code === 0) d.value = r.data; }
      onMounted(load);
      return { d, load };
    },
    template: `
    <div class="pm-page pm-anim-in" v-if="d">
      <div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:6px">
        <PM-SectionTitle title="学习行为轨迹"/>
        <el-button size="small" @click="load"><el-icon><Refresh/></el-icon> 刷新</el-button>
      </div>
      <div class="pm-card">
        <div style="position:relative;padding-left:24px">
          <div style="position:absolute;left:7px;top:0;bottom:0;width:2px;background:var(--pm-border)"></div>
          <div v-for="(r,i) in d.records" :key="i" style="position:relative;padding:0 0 18px 14px">
            <span style="position:absolute;left:-21px;top:4px;width:14px;height:14px;border-radius:50%;background:var(--pm-brand);box-shadow:0 0 0 4px var(--pm-brand-soft)"></span>
            <div style="font-weight:600">{{ r.action }}：{{ r.detail }}</div>
            <div class="pm-faint" style="font-size:12px">{{ r.course }} · {{ r.time }} · {{ r.duration }} 分钟</div>
          </div>
        </div>
        <div v-if="!d.records.length" class="pm-empty">暂无记录</div>
      </div>
    </div><PM-Spinner v-else/>`,
  });
  // ---------------- AI 代码调试（独立页面） ----------------
  PM.LearnAiDebug = defineComponent({
    setup() {
      const { ref } = Vue;
      const code = ref("def add(a, b):\n    return a + b\n\nprint(add(1, '2'))  # 类型错误");
      const dbgInput = ref("");
      const dbgMsg = ref("");
      const loading = ref(false);
      async function aiDebug() {
        const e = dbgInput.value.trim();
        if (!e) { ElementPlus.ElMessage.warning("请描述你遇到的错误"); return; }
        loading.value = true; dbgMsg.value = "";
        await PM.callAI("debug", { error: e, code: code.value },
          (txt) => { dbgMsg.value = txt; }, () => { loading.value = false; });
        dbgInput.value = "";
        await PM.api("/api/learn/record", {
          method: "POST",
          body: JSON.stringify({ action: "AI 调试", detail: e.slice(0, 24), course: "Python 程序设计", duration: 8 }),
        });
      }
      return { code, dbgInput, dbgMsg, loading, aiDebug };
    },
    template: `
    <div class="pm-page pm-anim-in">
      <PM-SectionTitle title="AI 代码调试（贴上报错，AI 帮你定位）"/>
      <div class="pm-grid pm-grid-2">
        <div class="pm-card">
          <PM-SectionTitle title="当前代码"/>
          <el-input type="textarea" v-model="code" :rows="10" style="font-family:monospace"/>
          <div style="margin-top:12px">
            <PM-SectionTitle title="🤖 AI 辅助调试"/>
            <el-input type="textarea" v-model="dbgInput" :rows="4" placeholder="粘贴报错信息 / traceback，如：TypeError: can only concatenate str ..."/>
            <el-button type="primary" plain style="margin-top:10px" :loading="loading" @click="aiDebug">AI 分析</el-button>
          </div>
        </div>
        <div class="pm-card">
          <PM-SectionTitle title="AI 调试建议"/>
          <div v-if="dbgMsg" style="padding:14px;background:var(--pm-brand-soft);border-radius:10px;white-space:pre-wrap;line-height:1.8;font-size:13px" v-html="dbgMsg"></div>
          <div v-else class="pm-empty">提交报错后，AI 将给出定位与修复建议</div>
        </div>
      </div>
    </div>`,
  });

  // ---------------- AI 复习规划（薄弱点优先） ----------------
  PM.LearnAiReview = defineComponent({
    setup() {
      const { ref, onMounted } = Vue;
      const loading = ref(false);
      const weak = ref([]);
      const name = ref("");
      const out = ref("");
      const genLoading = ref(false);

      async function load() {
        loading.value = true;
        const r = await PM.api("/api/growth");
        loading.value = false;
        if (r.code !== 0) return;
        name.value = (PM.store.user && PM.store.user.name) || "";
        weak.value = (r.data.mastery || []).filter((m) => m.value < 60).map((m) => m.name);
      }
      async function gen() {
        if (!weak.value.length) return;
        genLoading.value = true; out.value = "";
        await PM.callAI("review_plan", { weak_points: weak.value, name: name.value },
          (txt) => { out.value = txt; }, () => { genLoading.value = false; });
      }
      onMounted(load);
      return { loading, weak, out, genLoading, gen };
    },
    template: `
    <div class="pm-page pm-anim-in">
      <PM-SectionTitle title="AI 复习规划（薄弱点优先）"/>
      <div v-if="loading" class="pm-empty" style="padding:50px">分析你的掌握度…</div>
      <template v-else>
        <div class="pm-card" style="margin-bottom:16px">
          <div style="font-weight:700;margin-bottom:8px">你的薄弱知识点（掌握度 &lt; 60）</div>
          <div v-if="weak.length" style="display:flex;flex-wrap:wrap;gap:8px">
            <el-tag v-for="w in weak" :key="w" type="warning">{{ w }}</el-tag>
          </div>
          <div v-else class="pm-empty">暂无薄弱点，保持节奏即可 🎉</div>
          <el-button type="primary" style="margin-top:14px" :disabled="!weak.length" :loading="genLoading" @click="gen">
            <el-icon><MagicStick/></el-icon> 生成复习规划
          </el-button>
        </div>
        <div class="pm-card">
          <PM-SectionTitle title="AI 复习规划"/>
          <div v-if="out" style="padding:14px;background:var(--pm-surface-2);border-radius:10px;white-space:pre-wrap;line-height:1.8;font-size:13px" v-html="out"></div>
          <div v-else class="pm-empty">点击“生成复习规划”查看个性化路线</div>
        </div>
      </template>
    </div>`,
  });
})();
