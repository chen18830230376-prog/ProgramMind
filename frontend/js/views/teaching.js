/* ============================================================
   教学模块（仅教师可见）
   子页面：我的课程 / 教案生成 / PPT 辅助 / 教材管理 / 知识网络 / AI 命题 / 实验管理 / 学情分析
   AI 渗透：教案生成、PPT 大纲、智能命题均为 AI 辅助（前端模拟 + 可编辑）
   可视化：知识图谱（ECharts graph）、学情分析（ECharts 分组柱状图）
   ============================================================ */
window.PM = window.PM || {};
(function () {
  const { defineComponent, ref, computed, watch, onMounted, onUnmounted, reactive, nextTick } = Vue;
  const courseColor = { C001: "#165DFF", C002: "#36CFC9", C003: "#722ED1" };

  function initChart(el, option) {
    if (!el) return;
    const c = echarts.init(el, document.documentElement.classList.contains("dark") ? "dark" : null);
    c.setOption(option); window.addEventListener("resize", () => c.resize()); return c;
  }

  // ---------------- 我的课程（管理 + 学生列表） ----------------
  PM.TeachCourses = defineComponent({
    setup() {
      const store = PM.store;
      const list = ref([]); const dialog = ref(false);
      const form = reactive({ name: "", code: "", desc: "" });
      // 教材封面预览
      const previewVisible = ref(false); const preview = reactive({ title: "", cover: "", course: "" });
      const previewFullscreenVisible = ref(false);
      const zoom = reactive({ scale: 1, panX: 0, panY: 0, dragging: false, lastX: 0, lastY: 0 });
      function resetPreviewZoom(){ zoom.scale = 1; zoom.panX = 0; zoom.panY = 0; zoom.dragging = false; }
      function openBook(c){ preview.title = c.name + "（教材）"; preview.cover = c.textbook || "/assets/textbooks/default.svg"; preview.course = c.name; previewVisible.value = true; resetPreviewZoom(); }
      function openPreviewFullscreen(){ previewVisible.value = false; previewFullscreenVisible.value = true; resetPreviewZoom(); }
      function closePreviewFullscreen(){ previewFullscreenVisible.value = false; }
      function onPreviewWheel(e){ e.preventDefault(); const delta = e.deltaY > 0 ? 0.9 : 1.1; zoom.scale = Math.max(0.5, Math.min(5, zoom.scale * delta)); }
      function onPreviewDblClick(){ if (zoom.scale > 1.05) { zoom.scale = 1; zoom.panX = 0; zoom.panY = 0; } else { zoom.scale = 2; } }
      function onPreviewMouseDown(e){ if (zoom.scale <= 1.05) return; zoom.dragging = true; zoom.lastX = e.clientX; zoom.lastY = e.clientY; }
      function onPreviewMouseMove(e){ if (!zoom.dragging) return; zoom.panX += e.clientX - zoom.lastX; zoom.panY += e.clientY - zoom.lastY; zoom.lastX = e.clientX; zoom.lastY = e.clientY; }
      function onPreviewMouseUp(){ zoom.dragging = false; }
      onMounted(async () => { const r = await PM.api("/api/teach/courses"); if (r.code === 0) list.value = r.data; });
      function create() { if (!form.name) { ElementPlus.ElMessage.warning("请填写课程名称"); return; } ElementPlus.ElMessage.success("课程已创建（演示）"); dialog.value = false; form.name=""; }
      return { list, dialog, form, create, previewVisible, preview, openBook, previewFullscreenVisible, zoom, openPreviewFullscreen, closePreviewFullscreen, onPreviewWheel, onPreviewDblClick, onPreviewMouseDown, onPreviewMouseMove, onPreviewMouseUp, store };
    },
    template: `
    <div class="pm-page pm-anim-in" v-if="list.length">
      <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:14px">
        <PM-SectionTitle title="我的课程"/>
        <el-button type="primary" @click="dialog=true"><el-icon><Plus/></el-icon> 创建课程</el-button>
      </div>
      <div class="pm-grid pm-grid-3 pm-stagger">
        <div v-for="c in list" :key="c.id" class="pm-card" style="padding:0;overflow:hidden">
          <!-- 顶部教材插图区：用本地教材 SVG 填满空白 -->
          <div style="position:relative;height:140px;display:flex;align-items:center;justify-content:center;overflow:hidden"
               :style="{ background: 'radial-gradient(circle at 50% 70%, ' + (c.color||'#165DFF') + '25 0%, ' + (c.color||'#165DFF') + '08 70%)' }">
            <img :src="c.textbook || '/assets/textbooks/default.svg'" @click.stop="openBook(c)"
                 :title="'查看《' + c.name + '》教材封面'"
                 style="height:110px;width:auto;object-fit:contain;filter:drop-shadow(0 10px 18px rgba(0,0,0,.28));cursor:pointer"/>
            <el-tag size="small" effect="dark" type="primary"
                    style="position:absolute;left:10px;top:10px;cursor:pointer"
                    @click.stop="openBook(c)">
              <el-icon style="vertical-align:-2px"><Notebook/></el-icon> 配套教材
            </el-tag>
          </div>
          <div style="padding:14px">
            <div style="font-weight:700">{{ c.name }} <span class="pm-faint" style="font-size:12px">{{ c.code }}</span></div>
            <div class="pm-muted" style="font-size:12px;margin:6px 0">{{ c.description }}</div>
            <div style="font-size:12px;font-weight:600;margin:8px 0 4px">学生（{{ c.students.length }}）</div>
            <div style="display:flex;flex-wrap:wrap;gap:6px">
              <el-tag v-for="s in c.students" :key="s.id" size="small" effect="plain">{{ s.name }}</el-tag>
            </div>
          </div>
        </div>
      </div>
      <el-dialog v-model="dialog" title="创建课程（演示）" width="460px">
        <el-form label-width="80px">
          <el-form-item label="课程名称"><el-input v-model="form.name"/></el-form-item>
          <el-form-item label="课程代码"><el-input v-model="form.code" placeholder="如 CS101"/></el-form-item>
          <el-form-item label="简介"><el-input type="textarea" v-model="form.desc" :rows="3"/></el-form-item>
        </el-form>
        <template #footer><el-button @click="dialog=false">取消</el-button><el-button type="primary" @click="create">创建</el-button></template>
      </el-dialog>

      <!-- 教材封面放大预览 -->
      <el-dialog v-model="previewVisible" :title="preview.title" width="360px" align-center>
        <div style="text-align:center">
          <img :src="preview.cover" style="width:200px;height:auto;border-radius:10px;box-shadow:0 10px 30px rgba(0,0,0,.35)"/>
          <p class="pm-faint" style="font-size:13px;margin-top:12px">配套教材 · {{ preview.course }}</p>
        </div>
        <template #footer>
          <el-button @click="previewVisible=false">关闭</el-button>
          <el-button type="primary" @click="openPreviewFullscreen"><el-icon><FullScreen/></el-icon> 全屏查看</el-button>
        </template>
      </el-dialog>

      <!-- 教材封面全屏预览：占满主内容区（侧边栏右侧 / 顶栏下方） -->
      <teleport to="body">
      <div v-if="previewFullscreenVisible" class="pm-book-fullscreen"
           style="position:fixed;z-index:2000;background:var(--pm-bg);display:flex;flex-direction:column"
           :style="{ left: store.sidebarCollapsed ? '78px' : 'var(--pm-sidebar-w)', top: '64px', right: '0px', bottom: '0px' }">
        <!-- 顶部工具栏 -->
        <div style="height:64px;display:flex;align-items:center;justify-content:space-between;padding:0 24px;background:var(--pm-surface);border-bottom:1px solid var(--pm-border);flex-shrink:0;gap:16px">
          <div style="display:flex;align-items:center;gap:14px;min-width:0">
            <el-button circle @click="closePreviewFullscreen"><el-icon><ArrowLeft/></el-icon></el-button>
            <b style="font-size:16px;white-space:nowrap">教材封面 · {{ preview.title }}</b>
          </div>
          <div style="display:flex;align-items:center;gap:10px;flex-shrink:0">
            <span class="pm-faint" style="font-size:13px">{{ Math.round(zoom.scale*100) }}%</span>
            <el-button @click="resetPreviewZoom"><el-icon><ZoomOut/></el-icon> 重置</el-button>
          </div>
        </div>
        <!-- 主体：大图 -->
        <div style="flex:1;background:var(--pm-surface-2);display:flex;align-items:center;justify-content:center;overflow:hidden;padding:24px;min-height:0"
             @wheel.prevent="onPreviewWheel">
          <img v-if="previewFullscreenVisible" :src="preview.cover"
               @dblclick="onPreviewDblClick"
               @mousedown.prevent="onPreviewMouseDown"
               @mousemove="onPreviewMouseMove"
               @mouseup="onPreviewMouseUp"
               @mouseleave="onPreviewMouseUp"
               :style="{ transform: 'translate(' + zoom.panX + 'px, ' + zoom.panY + 'px) scale(' + zoom.scale + ')', transformOrigin: 'center center', maxWidth: '100%', maxHeight: '100%', objectFit: 'contain', filter: 'drop-shadow(0 20px 50px rgba(0,0,0,.4))', borderRadius: '12px', cursor: zoom.dragging ? 'grabbing' : (zoom.scale > 1.05 ? 'grab' : 'zoom-in'), transition: zoom.dragging ? 'none' : 'transform .12s ease-out', userSelect: 'none' }"/>
        </div>
        <div style="padding:10px 24px;font-size:12px;color:var(--pm-faint);text-align:center;background:var(--pm-surface);border-top:1px solid var(--pm-border)">
          滚轮缩放 · 双击放大/还原 · 放大后按住拖动查看角落 · 配套教材 · {{ preview.course }}
        </div>
      </div>
      </teleport>
    </div><PM-Spinner v-else/>`,
  });

  // ---------------- 作业管理（发布 + 批改 + 查看学生图片） ----------------
  PM.TeachHomework = defineComponent({
    setup() {
      const store = PM.store;
      const courses = ref([]);
      const list = ref([]);
      const pendingList = ref([]);
      const publishVisible = ref(false);
      const gradeVisible = ref(false);
      const graders = ref([]);
      const gradingHw = ref(null);
      const form = reactive({ course_id: "", title: "", desc: "", due: "" });
      const imgPreview = ref(""); const imgVisible = ref(false);
      const zoomScale = ref(1);
      const panX = ref(0); const panY = ref(0); const dragging = ref(false);
      let dragStart = { x: 0, y: 0 }, lastPos = { x: 0, y: 0 };
      function resetZoom(){ zoomScale.value = 1; panX.value = 0; panY.value = 0; }
      function showImg(u){ if (u) { imgPreview.value = u; zoomScale.value = 1; panX.value = 0; panY.value = 0; imgVisible.value = true; } }
      function onWheel(e){ e.preventDefault(); const delta = e.deltaY > 0 ? -0.12 : 0.12; zoomScale.value = Math.max(0.3, Math.min(5, +(zoomScale.value + delta).toFixed(2))); }
      function onImgDblClick(){ if (zoomScale.value > 1.05) resetZoom(); else { zoomScale.value = 2.5; panX.value = 0; panY.value = 0; } }
      function onMouseDown(e){ if (zoomScale.value <= 1.03) return; dragging.value = true; dragStart = { x: e.clientX, y: e.clientY }; lastPos = { x: panX.value, y: panY.value }; }
      function onMouseMove(e){ if (!dragging.value) return; panX.value = lastPos.x + (e.clientX - dragStart.x); panY.value = lastPos.y + (e.clientY - dragStart.y); }
      function onMouseUp(){ dragging.value = false; }

      // 全屏批改覆盖层状态
      const gradeFullscreenVisible = ref(false);
      const currentHw = ref(null);
      const currentSubmissions = ref([]);
      const currentStudentIndex = ref(0);
      const currentStudent = computed(() => currentSubmissions.value[currentStudentIndex.value] || {});

      async function load(){
        const c = await PM.api("/api/teach/courses"); if (c.code === 0) courses.value = c.data;
        const h = await PM.api("/api/teach/homework"); if (h.code === 0) list.value = h.data;
        const s = await PM.api("/api/teach/submissions");
        if (s.code === 0) pendingList.value = s.data.filter(x => x.status === 'submitted').slice(0, 8);
      }
      onMounted(load);
      function openPublish(){
        form.course_id = courses.value[0] ? courses.value[0].id : "";
        form.title = ""; form.desc = ""; form.due = ""; publishVisible.value = true;
      }
      async function publish(){
        if (!form.course_id || !form.title) { ElementPlus.ElMessage.warning("请选择课程并填写标题"); return; }
        const r = await PM.api("/api/teach/homework", { method: "POST", body: JSON.stringify({ ...form }) });
        if (r.code === 0) { ElementPlus.ElMessage.success(r.msg || "作业已发布，学生已收到通知"); publishVisible.value = false; await load(); }
        else ElementPlus.ElMessage.error(r.msg || "发布失败");
      }
      async function openGrade(h){
        currentHw.value = h;
        const r = await PM.api("/api/teach/submissions?hw_id=" + h.id);
        if (r.code === 0) { currentSubmissions.value = r.data; currentStudentIndex.value = 0; gradeFullscreenVisible.value = true; }
      }
      async function openGradeById(hw_id){
        const h = list.value.find(x => x.id === hw_id);
        if (h) await openGrade(h);
      }
      function closeGradeFullscreen(){ gradeFullscreenVisible.value = false; }
      function prevStudent(){ if (currentStudentIndex.value > 0) currentStudentIndex.value--; }
      function nextStudent(){ if (currentStudentIndex.value < currentSubmissions.value.length - 1) currentStudentIndex.value++; }
      async function saveGrade(g){
        const r = await PM.api("/api/teach/grade", {
          method: "POST",
          body: JSON.stringify({ hw_id: g.hw_id, student_id: g.student_id, score: g.score, feedback: g.feedback }),
        });
        if (r.code === 0) { ElementPlus.ElMessage.success(r.msg || "批改完成，学情已同步"); await load(); }
        else ElementPlus.ElMessage.error(r.msg || "批改失败");
      }
      return { store, courses, list, pendingList, publishVisible, gradeVisible, graders, gradingHw,
               form, imgPreview, imgVisible, load, openPublish, publish,
               gradeFullscreenVisible, currentHw, currentSubmissions, currentStudentIndex, currentStudent,
               openGrade, openGradeById, closeGradeFullscreen, prevStudent, nextStudent, saveGrade,
               imgPreview, imgVisible, zoomScale, panX, panY, dragging, showImg, resetZoom, onWheel, onImgDblClick, onMouseDown, onMouseMove, onMouseUp };
    },
    template: `
    <div class="pm-page pm-anim-in">
      <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:14px">
        <PM-SectionTitle title="作业管理（发布 / 批改）"/>
        <el-button type="primary" @click="openPublish"><el-icon><Plus/></el-icon> 发布作业</el-button>
      </div>

      <div v-if="list.length" class="pm-grid pm-grid-2 pm-stagger">
        <div v-for="h in list" :key="h.id" class="pm-card">
          <div style="display:flex;justify-content:space-between;align-items:center">
            <b>{{ h.title }}</b><span class="pm-faint" style="font-size:12px">{{ h.course }}</span>
          </div>
          <div class="pm-faint" style="font-size:12px;margin:4px 0">截止 {{ h.due || '—' }}</div>
          <p class="pm-muted" style="font-size:13px">{{ h.desc }}</p>
          <div style="display:flex;gap:10px;margin:8px 0">
            <el-tag type="warning" effect="plain">待提交 {{ h.pending }}</el-tag>
            <el-tag type="primary" effect="plain">已交 {{ h.submitted }}</el-tag>
            <el-tag type="success" effect="plain">已批改 {{ h.graded }}</el-tag>
          </div>
          <el-button size="small" type="primary" plain @click="openGrade(h)">批改 / 查看</el-button>
        </div>
      </div>
      <div v-else class="pm-card" style="text-align:center;padding:40px">暂无作业，点击右上角发布。</div>

      <!-- 待批改提醒：填充页面下方空白 -->
      <div v-if="pendingList.length" style="margin-top:24px">
        <PM-SectionTitle title="待批改提醒"/>
        <div class="pm-card" style="padding:14px 18px">
          <div v-for="p in pendingList" :key="p.hw_id + '-' + p.student_id" class="pm-row" style="padding:10px 12px;margin:0 -6px;border-radius:12px">
            <div style="width:34px;height:34px;border-radius:50%;background:var(--pm-brand-soft);color:var(--pm-brand);display:flex;align-items:center;justify-content:center;font-weight:700;font-size:13px">{{ p.student.charAt(0) }}</div>
            <div style="flex:1;min-width:0">
              <div style="font-weight:600;font-size:13px">{{ p.student }} · {{ p.hw }}</div>
              <div class="pm-faint" style="font-size:12px">{{ p.course }}</div>
            </div>
            <el-tag size="small" type="warning" effect="plain">待批改</el-tag>
            <el-button size="small" type="primary" plain @click="openGradeById(p.hw_id)">去批改</el-button>
          </div>
        </div>
      </div>

      <!-- 发布作业 -->
      <el-dialog v-model="publishVisible" title="发布作业" width="480px">
        <el-form label-width="80px">
          <el-form-item label="课程"><el-select v-model="form.course_id" style="width:100%">
            <el-option v-for="c in courses" :key="c.id" :label="c.name" :value="c.id"/></el-select></el-form-item>
          <el-form-item label="标题"><el-input v-model="form.title" placeholder="如：实验二 文件读写"/></el-form-item>
          <el-form-item label="说明"><el-input type="textarea" v-model="form.desc" :rows="3"/></el-form-item>
          <el-form-item label="截止"><el-date-picker v-model="form.due" type="date" value-format="YYYY-MM-DD" placeholder="选择日期"/></el-form-item>
        </el-form>
        <template #footer><el-button @click="publishVisible=false">取消</el-button><el-button type="primary" @click="publish">发布</el-button></template>
      </el-dialog>

      <!-- 全屏批改覆盖层：占满主内容区（侧边栏右侧 / 顶栏下方） -->
      <teleport to="body">
      <div v-if="gradeFullscreenVisible" class="pm-grade-fullscreen"
           style="position:fixed;z-index:2000;background:var(--pm-bg);display:flex;flex-direction:column"
           :style="{ left: store.sidebarCollapsed ? '78px' : 'var(--pm-sidebar-w)', top: '64px', right: '0px', bottom: '0px' }">
        <!-- 顶部工具栏 -->
        <div style="height:64px;display:flex;align-items:center;justify-content:space-between;padding:0 24px;background:var(--pm-surface);border-bottom:1px solid var(--pm-border);flex-shrink:0;gap:16px">
          <div style="display:flex;align-items:center;gap:14px;min-width:0">
            <el-button circle @click="closeGradeFullscreen"><el-icon><ArrowLeft/></el-icon></el-button>
            <b style="font-size:16px;white-space:nowrap">批改 · {{ currentHw ? currentHw.title : '' }}</b>
            <span class="pm-faint" style="font-size:13px;white-space:nowrap">{{ currentStudent.student || '' }}</span>
          </div>
          <div style="display:flex;align-items:center;gap:10px;flex-shrink:0">
            <el-button :disabled="currentStudentIndex===0" @click="prevStudent"><el-icon><ArrowLeft/></el-icon> 上一个</el-button>
            <span class="pm-faint" style="font-size:13px">{{ currentStudentIndex + 1 }} / {{ currentSubmissions.length }}</span>
            <el-button :disabled="currentStudentIndex===currentSubmissions.length-1" @click="nextStudent">下一个 <el-icon><ArrowRight/></el-icon></el-button>
            <el-button type="primary" :disabled="!currentStudent || currentStudent.status==='pending'" @click="saveGrade(currentStudent)">保存</el-button>
          </div>
        </div>

        <!-- 主体：左侧学生列表 + 右侧批改区 -->
        <div v-if="!currentSubmissions.length" class="pm-empty" style="flex:1;display:flex;align-items:center;justify-content:center">暂无学生提交记录</div>
        <div v-else style="flex:1;display:flex;overflow:hidden">
          <!-- 左侧学生列表 -->
          <div style="width:260px;border-right:1px solid var(--pm-border);overflow-y:auto;padding:16px;background:var(--pm-surface);flex-shrink:0">
            <div v-for="(g,i) in currentSubmissions" :key="g.student_id" @click="currentStudentIndex=i"
                 style="padding:12px;border-radius:12px;margin-bottom:8px;cursor:pointer;transition:background .2s"
                 :style="{background: i===currentStudentIndex ? 'var(--pm-brand-soft)' : 'transparent', border: i===currentStudentIndex ? '1px solid var(--pm-brand)' : '1px solid transparent'}">
              <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:4px">
                <b style="font-size:14px">{{ g.student }}</b>
                <el-tag size="small" :type="g.status==='graded'?'success':(g.status==='submitted'?'warning':'info')">
                  {{ g.status==='graded'?'已批改':(g.status==='submitted'?'待批改':'未提交') }}
                </el-tag>
              </div>
              <div class="pm-faint" style="font-size:12px">{{ g.status==='graded' ? ('得分 ' + g.score) : (g.status==='submitted' ? '等待批改' : '未提交') }}</div>
            </div>
          </div>

          <!-- 右侧批改区 -->
          <div style="flex:1;display:flex;flex-direction:column;padding:22px;overflow:hidden;min-width:0">
            <!-- 图片区 -->
            <div v-if="currentStudent.status !== 'pending'" style="flex:1;background:var(--pm-surface-2);border-radius:16px;display:flex;align-items:center;justify-content:center;overflow:hidden;border:1px solid var(--pm-border);margin-bottom:16px;min-height:0">
              <img v-if="currentStudent.image" :src="currentStudent.image" @click="showImg(currentStudent.image)" title="点击查看大图"
                   style="max-width:100%;max-height:100%;object-fit:contain;cursor:pointer;padding:10px"/>
              <div v-else class="pm-faint" style="font-size:14px;display:flex;align-items:center;gap:6px">
                <el-icon><Picture/></el-icon> 学生未上传图片
              </div>
            </div>
            <div v-else class="pm-empty" style="flex:1;display:flex;align-items:center;justify-content:center;margin-bottom:16px;background:var(--pm-surface-2);border-radius:16px;border:1px solid var(--pm-border)">学生尚未提交</div>

            <!-- 评分区 -->
            <div v-if="currentStudent.status!=='pending'" style="display:flex;gap:12px;align-items:center;flex-shrink:0;background:var(--pm-surface);padding:14px 16px;border-radius:14px;border:1px solid var(--pm-border)">
              <el-input v-model.number="currentStudent.score" placeholder="分数" style="width:160px" size="default"/>
              <el-input v-model="currentStudent.feedback" placeholder="评语（可选）" style="flex:1" size="default"/>
              <el-button type="primary" size="default" @click="saveGrade(currentStudent)">保存</el-button>
            </div>
          </div>
        </div>
      </div>
      </teleport>

      <el-dialog v-model="imgVisible" title="作业图片" width="90vw" top="5vh" align-center append-to-body :style="{ zIndex: 3000 }" @closed="resetZoom">
        <div style="display:flex;flex-direction:column;align-items:center;justify-content:center;min-height:70vh;width:100%">
          <img :src="imgPreview"
               @wheel.prevent="onWheel"
               @dblclick="onImgDblClick"
               @mousedown.prevent="onMouseDown"
               @mousemove="onMouseMove"
               @mouseup="onMouseUp"
               @mouseleave="onMouseUp"
               :style="{ transform: 'translate(' + panX + 'px, ' + panY + 'px) scale(' + zoomScale + ')', transformOrigin: 'center center', maxWidth: '100%', maxHeight: '64vh', objectFit: 'contain', borderRadius: '10px', cursor: dragging ? 'grabbing' : (zoomScale > 1.05 ? 'grab' : 'zoom-in'), transition: dragging ? 'none' : 'transform .12s ease-out', userSelect: 'none' }"/>
          <div style="margin-top:12px;font-size:12px;color:var(--pm-faint)">滚轮缩放（{{ Math.round(zoomScale*100) }}%）· 双击放大/还原 · 放大后按住拖动查看角落 · 点击图片右上角可看原图</div>
        </div>
      </el-dialog>
    </div>`,
  });

  // ---------------- AI 教案生成（可编辑） ----------------
  PM.TeachLessonPlan = defineComponent({
    setup() {
      const course = ref("Python 程序设计"); const chapter = ref("第4章 面向对象");
      const content = ref(""); const loading = ref(false);
      function gen() {
        loading.value = true;
        PM.callAI("lesson_plan", { course: course.value, chapter: chapter.value },
          (c) => { content.value = c; }, () => { loading.value = false; });
      }
      return { course, chapter, content, loading, gen };
    },
    template: `
    <div class="pm-page pm-anim-in">
      <PM-SectionTitle title="AI 教案生成（草拟后可编辑）"/>
      <div class="pm-grid pm-grid-2">
        <div class="pm-card">
          <el-form label-position="top">
            <el-form-item label="课程"><el-select v-model="course" style="width:100%">
              <el-option label="Python 程序设计" value="Python 程序设计"/><el-option label="数据结构" value="数据结构"/><el-option label="计算机网络" value="计算机网络"/>
            </el-select></el-form-item>
            <el-form-item label="章节"><el-input v-model="chapter"/></el-form-item>
            <el-button type="primary" :loading="loading" @click="gen"><el-icon><MagicStick/></el-icon> AI 生成教案</el-button>
          </el-form>
          <div style="margin-top:10px" class="pm-muted" style="font-size:12px">💡 人机协同：AI 生成草案，教师审核修改后发布，AI 不替代教师。</div>
        </div>
        <div class="pm-card">
          <div style="font-weight:700;margin-bottom:8px">教案内容（可编辑）</div>
          <el-input type="textarea" v-model="content" :rows="14" placeholder="点击左侧『AI 生成教案』后在此查看并编辑"/>
          <el-button class="pm-btn-ghost" style="margin-top:10px" :disabled="!content" @click="ElementPlus.ElMessage.success('已保存（演示）')">保存教案</el-button>
        </div>
      </div>
    </div>`,
  });

  // ---------------- PPT 辅助生成 ----------------
  PM.TeachPpt = defineComponent({
    setup() {
      const points = ref("变量与类型, 函数定义, 面向对象, 异常处理");
      const outline = ref("");
      function gen() {
        const arr = points.value.split(/[,，]/).map(s=>s.trim()).filter(Boolean);
        PM.callAI("ppt_outline", { points: arr }, (c) => { outline.value = c; }, () => {});
      }
      return { points, outline, gen };
    },
    template: `
    <div class="pm-page pm-anim-in">
      <PM-SectionTitle title="PPT 辅助生成（输入知识点 → 大纲预览）"/>
      <div class="pm-grid pm-grid-2">
        <div class="pm-card">
          <div style="font-weight:600;margin-bottom:8px">输入课程知识点（逗号分隔）</div>
          <el-input type="textarea" v-model="points" :rows="5"/>
          <el-button type="primary" style="margin-top:10px" @click="gen"><el-icon><Picture/></el-icon> 生成 PPT 大纲</el-button>
        </div>
        <div class="pm-card">
          <div style="font-weight:700;margin-bottom:8px">大纲预览</div>
          <pre v-if="outline" style="white-space:pre-wrap;font-size:13px;line-height:1.7;background:var(--pm-surface-2);padding:12px;border-radius:10px">{{ outline }}</pre>
          <div v-else class="pm-empty">尚无内容</div>
        </div>
      </div>
    </div>`,
  });

  // ---------------- 教材管理 ----------------
  PM.TeachTextbook = defineComponent({
    setup() {
      const list = ref([{ title:"Python 程序设计（教材）", type:"教材", course:"Python 程序设计" },
        { title:"数据结构 PPT 第3章", type:"PPT", course:"数据结构" },
        { title:"实验指导：链表与栈", type:"实验指导", course:"数据结构" }]);
      const form = reactive({ title:"", type:"教材", course:"Python 程序设计", file:"（演示，未真实上传）" });
      function upload(){ if(!form.title){ElementPlus.ElMessage.warning("请填写资源名称");return;} list.value.unshift({...form}); ElementPlus.ElMessage.success("已上传（演示）"); form.title=""; }
      return { list, form, upload };
    },
    template: `
    <div class="pm-page pm-anim-in">
      <PM-SectionTitle title="教材 / 资源管理"/>
      <div class="pm-grid pm-grid-2">
        <div class="pm-card">
          <div style="font-weight:600;margin-bottom:8px">上传教学资源（模拟）</div>
          <el-form label-position="top">
            <el-form-item label="资源名称"><el-input v-model="form.title"/></el-form-item>
            <el-form-item label="类型"><el-select v-model="form.type" style="width:100%"><el-option label="教材" value="教材"/><el-option label="PPT" value="PPT"/><el-option label="实验指导" value="实验指导"/><el-option label="代码" value="代码"/></el-select></el-form-item>
            <el-form-item label="所属课程"><el-select v-model="form.course" style="width:100%"><el-option label="Python 程序设计" value="Python 程序设计"/><el-option label="数据结构" value="数据结构"/><el-option label="计算机网络" value="计算机网络"/></el-select></el-form-item>
            <el-upload drag action="#" :auto-upload="false" :show-file-list="false"><div style="padding:20px" class="pm-muted">将文件拖到此处（演示：不真实上传）</div></el-upload>
            <el-button type="primary" style="margin-top:6px" @click="upload">确认上传</el-button>
          </el-form>
        </div>
        <div class="pm-card">
          <div style="font-weight:700;margin-bottom:8px">资源列表</div>
          <div v-for="r in list" :key="r.title" style="display:flex;gap:10px;align-items:center;padding:9px 0;border-top:1px solid var(--pm-border)">
            <el-icon color="#165DFF"><Files/></el-icon><span style="font-weight:600;flex:1">{{ r.title }}</span>
            <el-tag size="small">{{ r.type }}</el-tag><span class="pm-faint" style="font-size:12px">{{ r.course }}</span>
          </div>
        </div>
      </div>
    </div>`,
  });

  // ---------------- 知识网络（ECharts 知识图谱） ----------------
  PM.TeachKnowledge = defineComponent({
    setup() {
      const graph = ref(null);
      const el = ref(null);
      const chart = ref(null);
      const loading = ref(false);
      const selected = ref(null);
      const selectedCourses = ref([]);
      const isDark = ref(document.documentElement.classList.contains("dark"));

      const stats = computed(() => {
        if (!graph.value) return { nodeCount: 0, edgeCount: 0, coreCount: 0, courseCount: 0 };
        const nodes = filteredNodes.value;
        return {
          nodeCount: nodes.length,
          edgeCount: filteredEdges.value.length,
          coreCount: nodes.filter(n => (n.val || 0) >= 15).length,
          courseCount: new Set(nodes.map(n => n.course)).size,
        };
      });

      const filteredNodes = computed(() => {
        if (!graph.value) return [];
        if (!selectedCourses.value.length) return graph.value.nodes;
        return graph.value.nodes.filter(n => selectedCourses.value.includes(n.course));
      });

      const filteredEdges = computed(() => {
        if (!graph.value) return [];
        const names = new Set(filteredNodes.value.map(n => n.name));
        return graph.value.edges.filter(e => names.has(e.sourceName) && names.has(e.targetName));
      });

      const selectedDetail = computed(() => {
        if (!selected.value || !graph.value) return null;
        const name = selected.value.name;
        const prereqs = graph.value.edges
          .filter(e => e.targetName === name && e.relation === "prerequisite")
          .map(e => ({ name: e.sourceName, course: e.sourceCourse, id: e.sourceId }));
        const related = graph.value.edges
          .filter(e => (e.sourceName === name || e.targetName === name) && e.relation === "related")
          .map(e => ({ name: e.sourceName === name ? e.targetName : e.sourceName, course: e.sourceName === name ? e.targetCourse : e.sourceCourse, id: e.sourceName === name ? e.targetId : e.sourceId }));
        return { ...selected.value, prereqs, related };
      });

      function nodeName(g, id) { const n = g.nodes.find(x => x.id === id); return n ? n.name : id; }
      function nodeCourse(g, id) { const n = g.nodes.find(x => x.id === id); return n ? n.course : id; }

      function getOption() {
        const dark = isDark.value;
        const textColor = dark ? "#e5e7eb" : "#1f2937";
        const mutedColor = dark ? "#94a3b8" : "#64748b";
        const bgColor = dark ? "rgba(30,41,59,0.4)" : "rgba(255,255,255,0.6)";
        const cats = [...new Set(filteredNodes.value.map(n => n.course))];
        const categories = cats.map(c => ({ name: c, itemStyle: { color: courseColor[c] || "#165DFF" } }));
        const nodeMap = {};
        filteredNodes.value.forEach(n => { nodeMap[n.name] = n; });

        return {
          tooltip: {
            backgroundColor: dark ? "rgba(15,23,42,0.95)" : "rgba(255,255,255,0.95)",
            borderColor: dark ? "#334155" : "#e2e8f0",
            textStyle: { color: textColor },
            formatter: (p) => {
              if (p.dataType === "node") {
                const n = nodeMap[p.name] || {};
                const courseName = { C001: "Python 程序设计", C002: "数据结构", C003: "计算机网络" }[n.course] || n.course;
                return `<div style="font-weight:700">${p.name}</div><div style="font-size:12px;color:${mutedColor}">${courseName} · ${n.category || ""}</div>`;
              }
              const rel = p.data.relation === "prerequisite" ? "先修关系" : "相关关系";
              return `<div style="font-size:12px">${p.data.source} → ${p.data.target}</div><div style="font-weight:600">${rel}</div>`;
            }
          },
          legend: { show: false },
          animationDuration: 1200,
          animationEasingUpdate: "cubicOut",
          series: [{
            type: "graph", layout: "force", roam: true,
            categories,
            data: filteredNodes.value.map(n => ({
              name: n.name, value: n.val, category: categories.findIndex(c => c.name === n.course),
              symbolSize: 48 + n.val * 1.3,
              itemStyle: { color: courseColor[n.course] || "#165DFF", borderColor: dark ? "#fff" : "#fff", borderWidth: 3, shadowBlur: 16, shadowColor: (courseColor[n.course] || "#165DFF") + "55" },
              label: { show: true, color: textColor, fontSize: 13, fontWeight: 600, formatter: "{b}", position: "bottom", distance: 8 },
              select: { itemStyle: { borderWidth: 4, borderColor: "#F59E0B" } },
              original: n
            })),
            links: filteredEdges.value.map(e => ({
              source: e.sourceName, target: e.targetName, relation: e.relation,
              lineStyle: {
                color: e.relation === "prerequisite" ? (dark ? "#60a5fa" : "#3b82f6") : (dark ? "#94a3b8" : "#94a3b8"),
                width: e.relation === "prerequisite" ? 2.5 : 1.5,
                type: e.relation === "prerequisite" ? "solid" : "dashed",
                curveness: 0.12
              },
              symbol: ["none", "arrow"],
              symbolSize: e.relation === "prerequisite" ? 12 : 8,
            })),
            emphasis: {
              focus: "adjacency",
              lineStyle: { width: 4 },
              label: { fontSize: 14, fontWeight: 700 }
            },
            force: { repulsion: 420, edgeLength: 130, gravity: 0.12, layoutAnimation: true },
            zoom: 0.85,
          }],
        };
      }

      function init() {
        if (!el.value || !graph.value) return;
        if (chart.value) { chart.value.dispose(); }
        chart.value = echarts.init(el.value, isDark.value ? "dark" : null);
        chart.value.setOption(getOption());
        chart.value.on("click", (p) => {
          if (p.dataType === "node") {
            selected.value = p.data.original;
          } else {
            selected.value = null;
          }
        });
        chart.value.on("zr:dblclick", () => { selected.value = null; });
        window.addEventListener("resize", onResize);
      }

      function onResize() { if (chart.value) chart.value.resize(); }

      function resetView() {
        selected.value = null;
        selectedCourses.value = [];
        if (chart.value) {
          chart.value.dispatchAction({ type: "restore" });
          chart.value.setOption(getOption(), true);
        }
      }

      watch(selectedCourses, () => { if (chart.value) chart.value.setOption(getOption(), true); });
      watch(selected, async () => {
        await nextTick();
        setTimeout(() => { if (chart.value) chart.value.resize(); }, 260);
      });

      onMounted(async () => {
        loading.value = true;
        const r = await PM.api("/api/knowledge-graph");
        loading.value = false;
        if (r.code !== 0) return;
        const g = r.data;
        g.edges = g.edges.map(e => ({
          ...e,
          sourceName: nodeName(g, e.source),
          targetName: nodeName(g, e.target),
          sourceCourse: nodeCourse(g, e.source),
          targetCourse: nodeCourse(g, e.target),
          sourceId: e.source,
          targetId: e.target,
        }));
        graph.value = g;
        selectedCourses.value = [...new Set(g.nodes.map(n => n.course))];
        await nextTick();
        init();
      });

      onUnmounted(() => {
        window.removeEventListener("resize", onResize);
        if (chart.value) { chart.value.dispose(); chart.value = null; }
      });

      const courseLabels = { C001: "Python 程序设计", C002: "数据结构", C003: "计算机网络" };
      return { el, loading, graph, selected, selectedCourses, selectedDetail, stats, courseLabels, courseColor, resetView };
    },
    template: `
    <div class="pm-page pm-anim-in">
      <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:14px;flex-wrap:wrap;gap:10px">
        <PM-SectionTitle title="课程知识网络（知识图谱）"/>
        <div style="display:flex;gap:8px">
          <el-button @click="resetView" size="small"><el-icon><RefreshRight /></el-icon> 重置视图</el-button>
        </div>
      </div>

      <!-- 统计卡片区 -->
      <div class="pm-grid pm-grid-4" style="margin-bottom:14px">
        <div class="pm-card" style="display:flex;align-items:center;gap:12px">
          <div style="width:44px;height:44px;border-radius:12px;background:#165DFF18;display:flex;align-items:center;justify-content:center"><el-icon size="22" color="#165DFF"><Collection /></el-icon></div>
          <div><div class="pm-muted" style="font-size:12px">知识点总数</div><div style="font-size:22px;font-weight:700">{{ stats.nodeCount }}</div></div>
        </div>
        <div class="pm-card" style="display:flex;align-items:center;gap:12px">
          <div style="width:44px;height:44px;border-radius:12px;background:#36CFC918;display:flex;align-items:center;justify-content:center"><el-icon size="22" color="#36CFC9"><Share /></el-icon></div>
          <div><div class="pm-muted" style="font-size:12px">关联关系数</div><div style="font-size:22px;font-weight:700">{{ stats.edgeCount }}</div></div>
        </div>
        <div class="pm-card" style="display:flex;align-items:center;gap:12px">
          <div style="width:44px;height:44px;border-radius:12px;background:#F59E0B18;display:flex;align-items:center;justify-content:center"><el-icon size="22" color="#F59E0B"><Star /></el-icon></div>
          <div><div class="pm-muted" style="font-size:12px">核心知识点</div><div style="font-size:22px;font-weight:700">{{ stats.coreCount }}</div></div>
        </div>
        <div class="pm-card" style="display:flex;align-items:center;gap:12px">
          <div style="width:44px;height:44px;border-radius:12px;background:#722ED118;display:flex;align-items:center;justify-content:center"><el-icon size="22" color="#722ED1"><Reading /></el-icon></div>
          <div><div class="pm-muted" style="font-size:12px">覆盖课程</div><div style="font-size:22px;font-weight:700">{{ stats.courseCount }}</div></div>
        </div>
      </div>

      <!-- 主体：筛选 + 图谱 + 详情 -->
      <div class="pm-card" style="display:flex;gap:16px;padding:16px;min-height:600px">
        <!-- 左侧筛选 -->
        <div style="width:220px;flex-shrink:0;display:flex;flex-direction:column;gap:16px;border-right:1px solid var(--pm-border);padding-right:16px">
          <div>
            <div style="font-weight:700;margin-bottom:10px">课程筛选</div>
            <el-checkbox-group v-model="selectedCourses" style="display:flex;flex-direction:column;gap:8px">
              <el-checkbox value="C001" size="large" border style="margin:0">
                <span style="display:inline-flex;align-items:center;gap:6px"><span style="width:10px;height:10px;border-radius:50%;background:#165DFF"></span>Python 程序设计</span>
              </el-checkbox>
              <el-checkbox value="C002" size="large" border style="margin:0">
                <span style="display:inline-flex;align-items:center;gap:6px"><span style="width:10px;height:10px;border-radius:50%;background:#36CFC9"></span>数据结构</span>
              </el-checkbox>
              <el-checkbox value="C003" size="large" border style="margin:0">
                <span style="display:inline-flex;align-items:center;gap:6px"><span style="width:10px;height:10px;border-radius:50%;background:#722ED1"></span>计算机网络</span>
              </el-checkbox>
            </el-checkbox-group>
          </div>

          <div>
            <div style="font-weight:700;margin-bottom:10px">关系说明</div>
            <div style="display:flex;flex-direction:column;gap:10px;font-size:13px;color:var(--pm-text-secondary)">
              <div style="display:flex;align-items:center;gap:8px"><span style="width:28px;height:0;border-top:2.5px solid #3b82f6"></span><span>实线箭头：先修关系</span></div>
              <div style="display:flex;align-items:center;gap:8px"><span style="width:28px;height:0;border-top:1.5px dashed #94a3b8"></span><span>虚线：相关关系</span></div>
            </div>
          </div>

          <div>
            <div style="font-weight:700;margin-bottom:10px">操作提示</div>
            <div style="font-size:12px;color:var(--pm-text-secondary);line-height:1.7">
              • 滚轮 / 双指缩放图谱<br>
              • 拖拽节点调整布局<br>
              • 单击节点查看详情<br>
              • 双击空白处取消选中
            </div>
          </div>
        </div>

        <!-- 中央图谱 -->
        <div style="flex:1;position:relative;min-height:560px;border-radius:12px;overflow:hidden;background:var(--pm-surface-2)">
          <div v-if="loading" style="position:absolute;inset:0;display:flex;align-items:center;justify-content:center;z-index:10;background:var(--pm-surface)">
            <el-icon size="32" class="is-loading"><Loading /></el-icon>
          </div>
          <div ref="el" style="width:100%;height:100%;min-height:560px"></div>
        </div>

        <!-- 右侧详情 -->
        <div v-show="selectedDetail" style="width:300px;flex-shrink:0;border-left:1px solid var(--pm-border);padding-left:16px;display:flex;flex-direction:column;transition:all .25s ease">
          <template v-if="selectedDetail">
            <div style="display:flex;align-items:center;gap:10px;margin-bottom:12px">
              <div style="width:48px;height:48px;border-radius:50%;display:flex;align-items:center;justify-content:center;color:#fff;font-weight:700;font-size:18px" :style="{ background: courseColor[selectedDetail.course] || '#165DFF' }">{{ selectedDetail.name.slice(0,1) }}</div>
              <div>
                <div style="font-size:17px;font-weight:700">{{ selectedDetail.name }}</div>
                <div style="font-size:12px;color:var(--pm-text-secondary)">{{ courseLabels[selectedDetail.course] }} · {{ selectedDetail.category }}</div>
              </div>
            </div>
            <div style="background:var(--pm-surface-2);border-radius:10px;padding:12px;margin-bottom:14px">
              <div style="font-size:12px;color:var(--pm-text-secondary);margin-bottom:6px">重要度</div>
              <el-progress :percentage="selectedDetail.val * 5" :color="courseColor[selectedDetail.course] || '#165DFF'" :stroke-width="10" :show-text="false"/>
              <div style="display:flex;justify-content:space-between;margin-top:6px;font-size:12px;color:var(--pm-text-secondary)"><span>基础</span><span>核心</span></div>
            </div>
            <div style="font-size:13px;line-height:1.7;color:var(--pm-text);margin-bottom:16px">{{ selectedDetail.description || '暂无描述' }}</div>

            <div v-if="selectedDetail.prereqs.length" style="margin-bottom:14px">
              <div style="font-weight:700;margin-bottom:8px">先修知识点</div>
              <div style="display:flex;flex-direction:column;gap:8px">
                <div v-for="p in selectedDetail.prereqs" :key="p.id" style="display:flex;align-items:center;gap:8px;padding:8px 10px;border-radius:8px;background:var(--pm-surface-2)">
                  <span style="width:8px;height:8px;border-radius:50%;background:#3b82f6"></span>
                  <span style="flex:1;font-size:13px">{{ p.name }}</span>
                  <el-tag size="small" effect="plain" style="font-size:11px">{{ courseLabels[p.course] }}</el-tag>
                </div>
              </div>
            </div>

            <div v-if="selectedDetail.related.length" style="margin-bottom:14px">
              <div style="font-weight:700;margin-bottom:8px">相关知识点</div>
              <div style="display:flex;flex-direction:column;gap:8px">
                <div v-for="p in selectedDetail.related" :key="p.id" style="display:flex;align-items:center;gap:8px;padding:8px 10px;border-radius:8px;background:var(--pm-surface-2)">
                  <span style="width:8px;height:8px;border-radius:50%;background:#94a3b8"></span>
                  <span style="flex:1;font-size:13px">{{ p.name }}</span>
                  <el-tag size="small" effect="plain" style="font-size:11px">{{ courseLabels[p.course] }}</el-tag>
                </div>
              </div>
            </div>

            <div v-if="!selectedDetail.prereqs.length && !selectedDetail.related.length" class="pm-empty" style="margin-top:20px">暂无关联知识点</div>
          </template>

          <div v-else style="flex:1;display:flex;flex-direction:column;align-items:center;justify-content:center;color:var(--pm-text-secondary);text-align:center">
            <el-icon size="48" style="margin-bottom:12px;opacity:.6"><Pointer /></el-icon>
            <div style="font-size:14px">点击图谱中的节点<br>查看知识点详情与关联关系</div>
          </div>
        </div>
      </div>
    </div>`,
  });

  // ---------------- AI 智能命题 + 教师题库管理 ----------------
  PM.TeachQuestion = defineComponent({
    setup() {
      const activeTab = ref("ai");
      const points = ref(["变量与类型","函数定义","面向对象"]); const difficulty = ref("medium"); const out = ref("");
      const genLoading = ref(false);
      const pointOptions = ["变量与类型","函数定义","面向对象","异常处理","二叉树","链表","栈","队列","TCP","IP","HTTP"];
      async function gen(){
        if(!points.value.length) return;
        genLoading.value = true; out.value = "";
        await PM.callAI("questions", { points: points.value, difficulty: difficulty.value },
          (txt) => { out.value = txt; }, () => { genLoading.value = false; });
      }

      const courses = ref([]);
      const myQuizzes = ref([]);
      const quizForm = reactive({ course_id: "", title: "", questions: [] });
      const publishing = ref(false);

      async function load(){
        const c = await PM.api("/api/teach/courses"); if (c.code === 0) courses.value = c.data;
        if (courses.value.length && !quizForm.course_id) quizForm.course_id = courses.value[0].id;
        await loadMyQuizzes();
      }
      async function loadMyQuizzes(){
        const r = await PM.api("/api/teach/quiz"); if (r.code === 0) myQuizzes.value = r.data;
      }
      onMounted(load);

      function addQuestion(){ quizForm.questions.push({ q: "", options: ["", "", "", ""], answer: 0, point: "" }); }
      function removeQuestion(idx){ quizForm.questions.splice(idx, 1); }
      function addOption(q){ q.options.push(""); }
      function removeOption(q, oi){ if (q.options.length > 2) q.options.splice(oi, 1); }

      async function publishQuiz(){
        if (!quizForm.course_id || !quizForm.title.trim()) { ElementPlus.ElMessage.warning("请选择课程并填写标题"); return; }
        const valid = quizForm.questions.filter(q => q.q.trim() && q.options.filter(o => o.trim()).length >= 2);
        if (!valid.length) { ElementPlus.ElMessage.warning("请至少添加一道完整题目"); return; }
        publishing.value = true;
        const r = await PM.api("/api/teach/quiz", {
          method: "POST",
          body: JSON.stringify({
            course_id: quizForm.course_id,
            title: quizForm.title.trim(),
            questions: valid.map(q => ({ q: q.q.trim(), options: q.options.map(o => o.trim()), answer: q.answer, point: q.point.trim() || "综合" })),
          }),
        });
        publishing.value = false;
        if (r.code === 0) {
          ElementPlus.ElMessage.success(r.msg || "测验已发布");
          quizForm.title = ""; quizForm.questions = [];
          activeTab.value = "bank";
          await loadMyQuizzes();
        } else {
          ElementPlus.ElMessage.error(r.msg || "发布失败");
        }
      }

      return { activeTab, points, difficulty, out, genLoading, pointOptions, gen,
               courses, myQuizzes, quizForm, publishing,
               addQuestion, removeQuestion, addOption, removeOption, publishQuiz };
    },
    template: `
    <div class="pm-page pm-anim-in">
      <PM-SectionTitle title="AI 智能命题 · 题库管理"/>
      <el-tabs v-model="activeTab" type="border-card">
        <el-tab-pane label="AI 智能命题" name="ai">
          <div class="pm-grid pm-grid-2">
            <div class="pm-card">
              <div style="font-weight:600;margin-bottom:8px">选择知识点</div>
              <el-checkbox-group v-model="points">
                <el-checkbox v-for="o in pointOptions" :key="o" :value="o" border style="margin:4px">{{ o }}</el-checkbox>
              </el-checkbox-group>
              <div style="font-weight:600;margin:14px 0 8px">难度</div>
              <el-radio-group v-model="difficulty">
                <el-radio value="easy" border>基础</el-radio><el-radio value="medium" border>中等</el-radio><el-radio value="hard" border>提高</el-radio>
              </el-radio-group>
              <div style="margin-top:14px"><el-button type="primary" :disabled="!points.length" :loading="genLoading" @click="gen"><el-icon><Promotion/></el-icon> 生成题目</el-button></div>
            </div>
            <div class="pm-card">
              <div style="font-weight:700;margin-bottom:8px">题目预览</div>
              <pre v-if="out" style="white-space:pre-wrap;font-size:13px;line-height:1.7;background:var(--pm-surface-2);padding:12px;border-radius:10px" v-html="out"></pre>
              <div v-else class="pm-empty">选择知识点后生成</div>
            </div>
          </div>
        </el-tab-pane>

        <el-tab-pane label="上传题库" name="upload">
          <div class="pm-card">
            <div style="display:flex;gap:12px;margin-bottom:14px">
              <div style="flex:1">
                <div style="font-weight:600;margin-bottom:6px">所属课程</div>
                <el-select v-model="quizForm.course_id" placeholder="选择课程" style="width:100%">
                  <el-option v-for="c in courses" :key="c.id" :label="c.name" :value="c.id"/>
                </el-select>
              </div>
              <div style="flex:2">
                <div style="font-weight:600;margin-bottom:6px">测验标题</div>
                <el-input v-model="quizForm.title" placeholder="例如：第 3 章 循环结构小测"/>
              </div>
            </div>

            <div v-for="(q, qi) in quizForm.questions" :key="qi" style="padding:14px 0;border-top:1px solid var(--pm-border)">
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
              <el-input v-model="q.point" placeholder="知识点标签（用于学情分析）" style="width:260px"/>
            </div>

            <div style="display:flex;gap:10px;margin-top:14px">
              <el-button type="primary" plain @click="addQuestion"><el-icon><Plus/></el-icon> 添加题目</el-button>
              <el-button type="primary" :loading="publishing" @click="publishQuiz" :disabled="!quizForm.questions.length">发布测验</el-button>
            </div>
            <div v-if="!quizForm.questions.length" class="pm-empty" style="padding:40px 0">点击“添加题目”开始创建测验</div>
          </div>
        </el-tab-pane>

        <el-tab-pane label="我的题库" name="bank">
          <div v-if="!myQuizzes.length" class="pm-empty" style="padding:60px">暂无已发布题库，请先在“上传题库”中创建。</div>
          <div v-else class="pm-grid pm-grid-2 pm-stagger">
            <div v-for="q in myQuizzes" :key="q.id" class="pm-card">
              <div style="font-weight:700">{{ q.title }}</div>
              <div class="pm-faint" style="font-size:12px">{{ q.question_count }} 道题 · {{ q.course }}</div>
            </div>
          </div>
        </el-tab-pane>
      </el-tabs>
    </div>`,
  });

  // ---------------- 实验管理 ----------------
  PM.TeachExperiment = defineComponent({
    setup() {
      const { ref, reactive, onMounted } = Vue;
      const list = ref([]);
      const myCourses = ref([]);
      const publishVisible = ref(false);
      const form = reactive({ course: "", title: "", desc: "", due: "" });
      const detailVisible = ref(false);
      const detail = ref(null);
      const gradeVisible = ref(false);
      const grading = reactive({ sid: null, score: null, feedback: "" });
      const imgPreview = ref(""); const imgVisible = ref(false);

      async function load() {
        const r = await PM.api("/api/teach/experiments");
        if (r.code === 0) list.value = r.data;
      }
      async function loadCourses() {
        const r = await PM.api("/api/teach/courses");
        if (r.code === 0) myCourses.value = r.data;
      }
      onMounted(async () => { await loadCourses(); await load(); });

      function openPublish() {
        form.course = myCourses.value.length ? myCourses.value[0].id : "";
        form.title = ""; form.desc = ""; form.due = "";
        publishVisible.value = true;
      }
      async function publish() {
        if (!form.course || !form.title.trim()) { ElementPlus.ElMessage.warning("请选择课程并填写实验名称"); return; }
        const r = await PM.api("/api/teach/experiments", {
          method: "POST",
          body: JSON.stringify({ course: form.course, title: form.title, desc: form.desc, due: form.due }),
        });
        if (r.code === 0) { ElementPlus.ElMessage.success(r.msg || "实验已发布"); publishVisible.value = false; await load(); }
        else ElementPlus.ElMessage.error(r.msg || "发布失败");
      }
      async function openDetail(e) {
        const r = await PM.api("/api/teach/experiments/" + e.id);
        if (r.code === 0) { detail.value = r.data; detailVisible.value = true; }
        else ElementPlus.ElMessage.error(r.msg || "加载失败");
      }
      function openGrade(s) {
        grading.sid = s.student_id; grading.score = s.score ?? null; grading.feedback = s.feedback || "";
        gradeVisible.value = true;
      }
      async function doGrade() {
        if (grading.score === null || grading.score === "" || isNaN(grading.score)) {
          ElementPlus.ElMessage.warning("请填写分数"); return;
        }
        const r = await PM.api("/api/teach/experiments/grade", {
          method: "POST",
          body: JSON.stringify({ exp_id: detail.value.id, student_id: grading.sid, score: Number(grading.score), feedback: grading.feedback }),
        });
        if (r.code === 0) {
          ElementPlus.ElMessage.success(r.msg || "批改完成");
          gradeVisible.value = false;
          const rr = await PM.api("/api/teach/experiments/" + detail.value.id);
          if (rr.code === 0) detail.value = rr.data;
          await load();
        } else ElementPlus.ElMessage.error(r.msg || "批改失败");
      }
      function statusTag(s) { return s === "graded" ? "success" : (s === "submitted" ? "warning" : "info"); }
      function statusText(s) { return s === "graded" ? "已批改" : (s === "submitted" ? "待批改" : "未提交"); }
      function reportName(url){ if (!url) return ""; const seg = decodeURIComponent((url.split("/").pop() || "")); const i = seg.indexOf("_"); return i >= 0 ? seg.slice(i + 1) : seg; }
      return { list, myCourses, publishVisible, form, openPublish, publish, openDetail,
               detailVisible, detail, openGrade, gradeVisible, grading, doGrade, statusTag, statusText, reportName, imgPreview, imgVisible };
    },
    template: `
    <div class="pm-page pm-anim-in">
      <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:14px">
        <PM-SectionTitle title="实验管理（发布 / 批改）"/>
        <el-button type="primary" @click="openPublish"><el-icon><Plus/></el-icon> 发布实验</el-button>
      </div>

      <div v-if="list.length" class="pm-grid pm-grid-2 pm-stagger">
        <div v-for="e in list" :key="e.id" class="pm-card">
          <div style="display:flex;justify-content:space-between;align-items:flex-start">
            <b style="font-size:15px">{{ e.title }}</b>
            <el-tag :type="e.pending? 'warning':'success'" size="small" effect="plain">{{ e.graded }}/{{ e.total }} 已批改</el-tag>
          </div>
          <div class="pm-faint" style="font-size:12px;margin:4px 0">{{ e.course }} · 截止 {{ e.due || '未设' }}</div>
          <p class="pm-muted" style="font-size:13px">{{ e.desc || '暂无说明' }}</p>
          <div style="display:flex;gap:10px;margin:8px 0">
            <el-tag type="warning" effect="plain" size="small">待批改 {{ e.pending }}</el-tag>
            <el-tag type="success" effect="plain" size="small">已交 {{ e.submitted }}</el-tag>
            <el-tag effect="plain" size="small">共 {{ e.total }}</el-tag>
          </div>
          <el-button size="small" type="primary" plain @click="openDetail(e)">查看提交并批改</el-button>
        </div>
      </div>
      <div v-else class="pm-card" style="text-align:center;padding:40px">暂无实验，点击右上角发布。</div>

      <!-- 发布实验 -->
      <el-dialog v-model="publishVisible" title="发布实验" width="480px" align-center>
        <el-form label-width="80px">
          <el-form-item label="课程">
            <el-select v-model="form.course" style="width:100%">
              <el-option v-for="c in myCourses" :key="c.id" :label="c.name" :value="c.id"/>
            </el-select>
          </el-form-item>
          <el-form-item label="实验名称"><el-input v-model="form.title" placeholder="如：实验二 文件读写"/></el-form-item>
          <el-form-item label="说明"><el-input v-model="form.desc" type="textarea" :rows="3" placeholder="实验要求与步骤"/></el-form-item>
          <el-form-item label="截止日期"><el-date-picker v-model="form.due" type="date" value-format="YYYY-MM-DD" placeholder="选择日期" style="width:100%"/></el-form-item>
        </el-form>
        <template #footer>
          <el-button @click="publishVisible=false">取消</el-button>
          <el-button type="primary" @click="publish">发布</el-button>
        </template>
      </el-dialog>

      <!-- 提交详情 + 批改 -->
      <el-dialog v-model="detailVisible" :title="(detail?detail.title:'')+' · 提交情况'" width="760px" top="4vh" align-center>
        <div v-if="detail" style="max-height:70vh;overflow:auto">
          <div class="pm-faint" style="font-size:12px;margin-bottom:10px">{{ detail.course }} · 截止 {{ detail.due || '未设' }} · {{ detail.submissions.length }} 名学生</div>
          <div v-for="s in detail.submissions" :key="s.student_id" class="pm-card" style="margin-bottom:12px">
            <div style="display:flex;justify-content:space-between;align-items:center">
              <div style="display:flex;align-items:center;gap:10px">
                <pm-avatar :name="s.student" :src="s.avatar" :size="36"/>
                <b>{{ s.student }}</b>
                <el-tag :type="statusTag(s.status)" size="small">{{ statusText(s.status) }}</el-tag>
              </div>
              <el-button v-if="s.status!=='graded'" size="small" type="primary" @click="openGrade(s)">批改</el-button>
              <span v-else style="color:var(--pm-brand);font-weight:700">得分 {{ s.score != null ? s.score : '已批改' }}</span>
            </div>
            <p class="pm-muted" style="font-size:13px;margin:8px 0" v-if="s.content">{{ s.content }}</p>
            <a v-if="s.file" :href="s.file" target="_blank" rel="noopener"
               style="display:inline-flex;align-items:center;gap:6px;margin:6px 0;padding:8px 12px;background:var(--pm-brand-soft);color:var(--pm-brand);border-radius:10px;font-size:13px;text-decoration:none;font-weight:600">
              <el-icon><Document/></el-icon> {{ s.file_name || reportName(s.file) || '查看实验报告' }}
            </a>
            <img v-if="s.image" :src="s.image" style="max-width:100%;max-height:200px;border-radius:10px;margin:6px 0;background:var(--pm-surface-2)" @click="imgPreview=s.image;imgVisible=true"/>
            <div v-if="s.status==='graded'" style="padding:8px 10px;background:rgba(0,180,42,.08);border-radius:10px;font-size:13px;margin-top:6px">
              教师反馈：{{ s.feedback || '—' }} <span class="pm-faint">· 提交于 {{ s.submitted_at }}</span>
            </div>
          </div>
        </div>
        <el-dialog v-model="imgVisible" title="图片预览" width="520px" append-to-body align-center>
          <div style="text-align:center"><img :src="imgPreview" style="max-width:100%;border-radius:10px"/></div>
        </el-dialog>
      </el-dialog>

      <!-- 批改弹窗 -->
      <el-dialog v-model="gradeVisible" title="批改实验" width="460px" append-to-body align-center>
        <el-form label-width="70px" v-if="detail">
          <el-form-item label="学生">
            {{ detail.submissions.find(x=>x.student_id===grading.sid)?.student }}
          </el-form-item>
          <el-form-item label="得分">
            <el-input-number v-model="grading.score" :min="0" :max="100" :step="1"/>
          </el-form-item>
          <el-form-item label="评语">
            <el-input v-model="grading.feedback" type="textarea" :rows="3" placeholder="给学生的反馈"/>
          </el-form-item>
        </el-form>
        <template #footer>
          <el-button @click="gradeVisible=false">取消</el-button>
          <el-button type="primary" @click="doGrade">提交批改</el-button>
        </template>
      </el-dialog>
    </div>`,
  });

  // ---------------- 学情分析（ECharts 分组柱状图） ----------------
  PM.TeachAnalytics = defineComponent({
    setup() {
      const data = ref(null);
      const students = ref([]);
      const summary = ref({ total: 0, at_risk: 0, class_overall_avg: 0, total_weak_points: 0 });
      const selectedStudent = ref(null);
      const masteryEl = ref(null);
      const weakEl = ref(null);
      let masteryChart = null;
      let weakChart = null;

      async function load() {
        const r = await PM.api("/api/teach/analytics");
        if (r.code !== 0) return;
        data.value = r.data;
        students.value = r.data.students || [];
        summary.value = r.data.summary || summary.value;
        if (students.value.length && !selectedStudent.value) {
          selectedStudent.value = students.value[0];
        }
        await nextTick();
        renderCharts();
      }
      onMounted(load);

      function selectStudent(s) {
        selectedStudent.value = s;
        nextTick(() => renderMastery());
      }

      function renderMastery() {
        if (!masteryEl.value || !selectedStudent.value) return;
        if (masteryChart) masteryChart.dispose();
        const items = selectedStudent.value.mastery.slice().sort((a, b) => a.value - b.value).slice(0, 12);
        masteryChart = initChart(masteryEl.value, {
          tooltip: { trigger: "axis", formatter: "{b}：{c}" },
          grid: { left: 90, right: 36, top: 16, bottom: 20 },
          xAxis: { type: "value", max: 100, splitLine: { lineStyle: { color: "rgba(136,136,136,.15)" } }, axisLabel: { color: "var(--pm-text-soft)" } },
          yAxis: { type: "category", data: items.map(i => i.point), axisLabel: { color: "var(--pm-text-soft)" } },
          series: [{
            type: "bar", data: items.map(i => i.value),
            itemStyle: {
              borderRadius: [0, 4, 4, 0],
              color: function(p){ return p.value < 60 ? "#FF7D00" : (p.value < 80 ? "#165DFF" : "#36CFC9"); },
            },
            label: { show: true, position: "right", formatter: "{c}", color: "var(--pm-text)" },
          }],
        });
      }

      function renderWeak() {
        if (!weakEl.value || !data.value) return;
        if (weakChart) weakChart.dispose();
        weakChart = initChart(weakEl.value, {
          tooltip: { trigger: "axis" },
          grid: { left: 40, right: 20, top: 30, bottom: 70 },
          xAxis: { type: "category", data: data.value.weak_global.map(i => i.point), axisLabel: { interval: 0, rotate: 28, color: "var(--pm-text-soft)" } },
          yAxis: { type: "value", max: 100, splitLine: { lineStyle: { color: "rgba(136,136,136,.15)" } }, axisLabel: { color: "var(--pm-text-soft)" } },
          series: [{
            type: "bar", data: data.value.weak_global.map(i => i.avg),
            itemStyle: { color: "#FF7D00", borderRadius: [4, 4, 0, 0] },
            label: { show: true, position: "top", formatter: "{c}", color: "var(--pm-text)" },
          }],
        });
      }

      function renderCharts() {
        renderMastery();
        renderWeak();
      }

      return { data, students, summary, selectedStudent, selectStudent, masteryEl, weakEl };
    },
    template: `
    <div class="pm-page pm-anim-in">
      <PM-SectionTitle title="学情分析"/>

      <!-- 班级概览指标 -->
      <div class="pm-grid pm-grid-4 pm-stagger" style="margin-bottom:18px">
        <PM-StatCard label="在授学生" :value="summary.total" icon="User" color="#165DFF"/>
        <PM-StatCard label="班级综合均分" :value="summary.class_overall_avg" icon="TrendCharts" color="#36CFC9"/>
        <PM-StatCard label="预警学生" :value="summary.at_risk" icon="Warning" color="#FF7D00"/>
        <PM-StatCard label="薄弱知识点" :value="summary.total_weak_points" icon="Memo" color="#722ED1"/>
      </div>

      <div class="pm-grid pm-grid-3" style="margin-bottom:18px">
        <!-- 学生列表 -->
        <div class="pm-card" style="grid-column:span 1;max-height:640px;overflow:auto">
          <div style="font-weight:800;margin-bottom:10px">学生列表</div>
          <div v-for="s in students" :key="s.id" @click="selectStudent(s)"
               style="display:flex;align-items:center;gap:10px;padding:10px;border-radius:10px;cursor:pointer;margin-bottom:8px"
               :style="{ background: selectedStudent && selectedStudent.id===s.id ? 'var(--pm-brand-soft)' : 'var(--pm-surface-2)' }">
            <pm-avatar :name="s.name" :src="s.avatar" :size="38"/>
            <div style="flex:1;min-width:0">
              <div style="font-weight:700;font-size:13px">{{ s.name }}</div>
              <div class="pm-faint" style="font-size:12px">均分 {{ s.overall_avg }} · {{ s.weak_count }} 个薄弱点</div>
            </div>
            <el-tag v-if="s.risk_level==='高危'" type="danger" size="small">高危</el-tag>
            <el-tag v-else-if="s.risk_level==='预警'" type="warning" size="small">预警</el-tag>
            <el-tag v-else-if="s.risk_level==='未评估'" type="info" size="small">未评估</el-tag>
            <el-tag v-else type="success" size="small">良好</el-tag>
          </div>
        </div>

        <!-- 学生详情 -->
        <div class="pm-card" style="grid-column:span 2">
          <div v-if="selectedStudent">
            <div style="display:flex;align-items:center;gap:14px;margin-bottom:16px;padding-bottom:14px;border-bottom:1px solid var(--pm-border)">
              <pm-avatar :name="selectedStudent.name" :src="selectedStudent.avatar" :size="52"/>
              <div>
                <div style="font-weight:800;font-size:17px">{{ selectedStudent.name }}</div>
                <div class="pm-faint" style="font-size:13px">综合均分 <b style="color:var(--pm-brand)">{{ selectedStudent.overall_avg }}</b> · {{ selectedStudent.weak_count }} 个薄弱点 · 风险等级
                  <el-tag v-if="selectedStudent.risk_level==='高危'" type="danger" size="small">{{ selectedStudent.risk_level }}</el-tag>
                  <el-tag v-else-if="selectedStudent.risk_level==='预警'" type="warning" size="small">{{ selectedStudent.risk_level }}</el-tag>
                  <el-tag v-else-if="selectedStudent.risk_level==='未评估'" type="info" size="small">{{ selectedStudent.risk_level }}</el-tag>
                  <el-tag v-else type="success" size="small">{{ selectedStudent.risk_level }}</el-tag>
                </div>
              </div>
            </div>

            <div style="font-weight:700;margin-bottom:10px">各课程掌握情况</div>
            <div v-for="c in selectedStudent.courses" :key="c.course_id" style="margin-bottom:14px">
              <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:5px">
                <span style="font-weight:600;font-size:13px">{{ c.course_name }}</span>
                <span style="font-size:12px">课程均分 <b>{{ c.avg }}</b> · 学习进度 {{ c.progress }}%</span>
              </div>
              <el-progress :percentage="c.avg" :color="c.color" :show-text="false" style="margin-bottom:5px"/>
              <div v-if="c.weak_points.length" style="font-size:12px;color:#FF7D00">薄弱：{{ c.weak_points.join('、') }}</div>
              <div v-else style="font-size:12px;color:#00b42a">该课程暂无薄弱点</div>
            </div>

            <div style="margin-top:20px">
              <div style="font-weight:700;margin-bottom:8px">知识点掌握度（低到高，取最低 12 项）</div>
              <div ref="masteryEl" style="height:300px"></div>
            </div>
          </div>
          <div v-else class="pm-empty" style="padding:60px">请选择左侧学生查看详细学情</div>
        </div>
      </div>

      <!-- 班级薄弱知识点 -->
      <div class="pm-card">
        <PM-SectionTitle title="班级薄弱知识点 TOP"/>
        <div ref="weakEl" style="height:260px"></div>
      </div>
    </div>`,
  });
  // ---------------- AI 学情总结（基于班级学情数据自动生成） ----------------
  PM.TeachAiSummary = defineComponent({
    setup() {
      const { ref, onMounted } = Vue;
      const loading = ref(false);
      const summary = ref(null);
      const weakGlobal = ref([]);
      const courses = ref([]);
      const out = ref("");
      const genLoading = ref(false);

      async function load() {
        loading.value = true;
        const r = await PM.api("/api/teach/analytics");
        loading.value = false;
        if (r.code !== 0) return;
        const d = r.data;
        summary.value = d.summary;
        weakGlobal.value = d.weak_global || [];
        const set = new Set();
        (d.students || []).forEach((s) => (s.courses || []).forEach((c) => set.add(c.course_name)));
        courses.value = [...set];
      }

      async function gen() {
        if (!summary.value) return;
        genLoading.value = true; out.value = "";
        const weakPoints = weakGlobal.value.map((w) => w.point);
        await PM.callAI("class_summary", {
          overall_avg: summary.value.class_overall_avg || 0,
          at_risk: summary.value.at_risk || 0,
          total: summary.value.total || 0,
          weak_points: weakPoints,
          course: courses.value.join("、") || "本班",
        }, (txt) => { out.value = txt; }, () => { genLoading.value = false; });
      }

      onMounted(load);
      return { loading, summary, weakGlobal, out, genLoading, gen };
    },
    template: `
    <div class="pm-page pm-anim-in">
      <PM-SectionTitle title="AI 学情总结（基于班级学情数据自动生成）"/>
      <div v-if="loading" class="pm-empty" style="padding:60px">加载学情数据…</div>
      <template v-else>
        <div class="pm-grid pm-grid-4" style="margin-bottom:16px" v-if="summary">
          <PM-StatCard label="班级人数" :value="summary.total" icon="User" color="#165DFF"/>
          <PM-StatCard label="平均掌握度" :value="summary.class_overall_avg + ' 分'" icon="TrendCharts" color="#36CFC9"/>
          <PM-StatCard label="风险学生" :value="summary.at_risk" icon="WarningFilled" color="#F56C6C"/>
          <PM-StatCard label="未评估" :value="summary.unassessed" icon="InfoFilled" color="#909399"/>
        </div>
        <div class="pm-grid pm-grid-2">
          <div class="pm-card">
            <PM-SectionTitle title="班级共性薄弱知识点"/>
            <div v-if="weakGlobal.length">
              <div v-for="w in weakGlobal" :key="w.point" style="display:flex;align-items:center;gap:10px;padding:8px 0;border-top:1px solid var(--pm-border)">
                <el-tag type="danger" size="small">{{ w.point }}</el-tag>
                <span class="pm-faint" style="font-size:12px">平均掌握度 {{ w.avg }} · {{ w.count }} 人薄弱</span>
              </div>
            </div>
            <div v-else class="pm-empty">暂无显著薄弱点</div>
            <el-button type="primary" style="margin-top:14px" :loading="genLoading" @click="gen">
              <el-icon><MagicStick/></el-icon> 生成 AI 学情总结
            </el-button>
          </div>
          <div class="pm-card">
            <PM-SectionTitle title="AI 总结"/>
            <div v-if="out" style="padding:14px;background:var(--pm-surface-2);border-radius:10px;white-space:pre-wrap;line-height:1.8;font-size:13px" v-html="out"></div>
            <div v-else class="pm-empty">点击左侧“生成 AI 学情总结”查看</div>
          </div>
        </div>
      </template>
    </div>`,
  });
})();
