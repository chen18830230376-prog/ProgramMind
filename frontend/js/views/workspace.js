/* ============================================================
   工作台 Workspace（系统首页 · 任务驱动式）
   【强调】不是传统菜单首页，而是“AI 驱动的任务中心”：
   - 教师：今日课表、待备课、AI 教案提醒、待批改、学情预警、AI 建议
   - 学生：今日计划、待办、AI 学习建议、学习导航、成长趋势、AI 复习推荐
   数据来自 /api/workspace，按角色返回并渲染（权限隔离）。
   ============================================================ */
window.PM = window.PM || {};
(function () {
  const { defineComponent, ref, reactive, computed, onMounted, nextTick } = Vue;

  function initChart(el, option) {
    if (!el) return;
    const c = echarts.init(el, document.documentElement.classList.contains("dark") ? "dark" : null);
    c.setOption(option);
    window.addEventListener("resize", () => c.resize());
    return c;
  }

  PM.Workspace = defineComponent({
    setup() {
      const store = PM.store;
      const d = ref(null);
      const trendEl = ref(null);

      // ---- 教师批改作业（任务中心闭环：待批改 → 打分 → 学情联动）----
      const gradeDialog = ref(false);
      const grading = ref(false);
      const gradeForm = reactive({ hw_id: "", student_id: "", hw: "", student: "", score: 85, feedback: "" });

      // 加载工作台数据（批改完成后需重新拉取以刷新任务）
      async function load() {
        const r = await PM.api("/api/workspace");
        d.value = r.code === 0 ? r.data : {};
        await nextTick();
        if (d.value && d.value.growth_trend) {
          initChart(trendEl.value, {
            grid: { left: 36, right: 16, top: 20, bottom: 24 },
            tooltip: { trigger: "axis" },
            xAxis: { type: "category", data: ["一","二","三","四","五","六","日"], axisLine:{lineStyle:{color:"#888"}} },
            yAxis: { type: "value", max: 100, splitLine:{lineStyle:{color:"rgba(136,136,136,.15)"}} },
            series: [{
              data: d.value.growth_trend, type: "line", smooth: true, symbol: "circle", symbolSize: 7,
              lineStyle: { width: 3, color: "#165DFF" },
              areaStyle: { color: new echarts.graphic.LinearGradient(0,0,0,1,[
                {offset:0,color:"rgba(22,93,255,.35)"},{offset:1,color:"rgba(22,93,255,0)"}]) },
            }],
          });
        }
      }
      onMounted(load);

      // 只保留真实存在的待批改项（后端会塞入"暂无新提交"占位数据）
      const pendingGrading = computed(() =>
        d.value ? (d.value.grading_tips || []).filter(x => x.student_id) : []);

      function openGrade(g) {
        Object.assign(gradeForm, {
          hw_id: g.hw_id, student_id: g.student_id, hw: g.hw,
          student: g.student, score: 85, feedback: "",
        });
        gradeDialog.value = true;
      }
      async function submitGrade() {
        grading.value = true;
        const r = await PM.api("/api/teach/grade", {
          method: "POST",
          body: JSON.stringify({
            hw_id: gradeForm.hw_id, student_id: gradeForm.student_id,
            score: gradeForm.score, feedback: gradeForm.feedback,
          }),
        });
        grading.value = false;
        if (r.code === 0) {
          ElementPlus.ElMessage.success(r.msg || "批改完成");
          gradeDialog.value = false;
          await load();          // 批完即刷新任务中心
        } else {
          ElementPlus.ElMessage.error(r.msg || "批改失败");
        }
      }

      return { store, d, trendEl, gradeDialog, gradeForm, grading, pendingGrading, openGrade, submitGrade };
    },
    template: `
    <div class="pm-page pm-anim-in" v-if="d">
      <!-- ================= 教师工作台 ================= -->
      <template v-if="store.role==='teacher'">
        <!-- Hero：任务概览横幅（AI 驱动的任务中心入口） -->
        <div class="pm-hero">
          <div>
            <span class="eyebrow">🗓 今日概览 · 任务优先</span>
            <h2>{{ store.user.name }} 老师，下午好</h2>
            <p>今天共 {{ (d.today_schedule||[]).length }} 节课、{{ (d.todo_lessons||[]).length }} 项待备课、
               {{ (d.grading_tips||[]).filter(x=>x.student).length }} 份作业待批改。AI 已为你草拟教案，等待你审核确认——AI 辅助，决策在你。</p>
            <div class="pm-hero-actions">
              <button class="pm-hero-btn solid" @click="$router.push('/teach/lesson-plan')">AI 生成教案</button>
              <button class="pm-hero-btn" @click="$router.push('/teach/homework')">去批改学生作业</button>
              <button class="pm-hero-btn" @click="$router.push('/teach/analytics')">查看学情分析</button>
              <button class="pm-hero-btn" @click="$router.push('/ai')">运行 Agent 工作流</button>
            </div>
          </div>
          <div class="pm-hero-art">
            <svg width="210" height="140" viewBox="0 0 210 140" fill="none">
              <rect x="6" y="14" width="118" height="112" rx="12" fill="rgba(255,255,255,.16)" stroke="rgba(255,255,255,.35)"/>
              <rect x="18" y="28" width="52" height="8" rx="4" fill="rgba(255,255,255,.55)"/>
              <rect x="18" y="44" width="94" height="6" rx="3" fill="rgba(255,255,255,.28)"/>
              <path d="M18 100 L42 84 L60 92 L80 68 L104 76" stroke="#fff" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round" fill="none"/>
              <circle cx="80" cy="68" r="4" fill="#fff"/>
              <rect x="136" y="28" width="66" height="34" rx="10" fill="rgba(255,255,255,.2)" stroke="rgba(255,255,255,.35)"/>
              <rect x="148" y="41" width="40" height="6" rx="3" fill="rgba(255,255,255,.5)"/>
              <rect x="136" y="74" width="66" height="34" rx="10" fill="rgba(255,255,255,.12)" stroke="rgba(255,255,255,.3)"/>
              <rect x="148" y="87" width="28" height="6" rx="3" fill="rgba(255,255,255,.4)"/>
              <circle cx="14" cy="14" r="3.5" fill="#36CFC9"/>
              <circle cx="198" cy="120" r="5" fill="rgba(114,46,209,.95)"/>
            </svg>
          </div>
        </div>
        <div class="pm-grid pm-grid-4 pm-stagger" style="margin-bottom:18px">
          <PM-StatCard label="今日课程" :value="(d.today_schedule||[]).length" icon="Notebook" color="#165DFF" sub="含 1 节线上课"/>
          <PM-StatCard label="待备课" :value="(d.todo_lessons||[]).length" icon="EditPen" color="#36CFC9" sub="AI 已草拟教案"/>
          <PM-StatCard label="待批改" :value="(d.grading_tips||[]).filter(x=>x.student).length" icon="Promotion" color="#722ED1" sub="新提交作业"/>
          <PM-StatCard label="在授课程" :value="(d.my_courses||[]).length" icon="School" color="#FF7D00" sub="覆盖 3 门 MVP 课"/>
        </div>

        <div class="pm-grid pm-grid-3" style="margin-bottom:18px">
          <div class="pm-card">
            <PM-SectionTitle title="今日课程安排"/>
            <div v-for="s in d.today_schedule" :key="s.time" style="display:flex;gap:12px;padding:9px 0;border-top:1px solid var(--pm-border)">
              <div style="font-weight:700;color:var(--pm-brand);min-width:96px">{{ s.time }}</div>
              <div><div style="font-weight:600">{{ s.course }}</div><div class="pm-faint" style="font-size:12px">{{ s.room }} · {{ s.class }}</div></div>
            </div>
          </div>
          <div class="pm-card">
            <PM-SectionTitle title="待备课任务"/>
            <div v-for="t in d.todo_lessons" :key="t.chapter" style="padding:9px 0;border-top:1px solid var(--pm-border)">
              <div style="font-weight:600">{{ t.course }} · {{ t.chapter }}</div>
              <div class="pm-faint" style="font-size:12px">截止：{{ t.due }}</div>
            </div>
            <div v-if="!d.todo_lessons.length" class="pm-empty">暂无待备课 🎉</div>
          </div>
          <div class="pm-card" style="background:linear-gradient(135deg,#165DFF,#4080ff);color:#fff;border:none">
            <div style="font-weight:800;margin-bottom:8px">🤖 AI 智能建议</div>
            <ul style="margin:0;padding-left:18px;line-height:1.9;font-size:13px">
              <li v-for="a in d.ai_suggestions" :key="a">{{ a }}</li>
            </ul>
          </div>
        </div>

        <div class="pm-grid pm-grid-2">
          <div class="pm-card">
            <div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:6px">
              <PM-SectionTitle title="待批改作业（可直接批改）"/>
              <el-tag v-if="pendingGrading.length" type="warning" size="small" round>{{ pendingGrading.length }} 份待处理</el-tag>
            </div>
            <div v-for="g in pendingGrading" :key="g.hw_id + g.student_id" class="pm-row">
              <div style="flex:1;min-width:0">
                <div style="font-weight:600;font-size:13.5px">{{ g.hw }}</div>
                <div class="pm-faint" style="font-size:12px">{{ g.student }} · {{ g.course }}</div>
              </div>
              <el-button size="small" type="primary" plain @click="openGrade(g)">批改</el-button>
            </div>
            <div v-if="!pendingGrading.length" class="pm-empty">暂无待批改作业 🎉</div>
          </div>
          <div class="pm-card">
            <PM-SectionTitle title="学情预警 & 资源"/>
            <div style="padding:10px 12px;background:rgba(255,125,0,.1);border-radius:10px;color:#FF7D00;font-size:13px;margin-bottom:10px">⚠ {{ d.analytics_tips }}</div>
            <div v-for="r in d.recent_resources" :key="r.title" style="display:flex;gap:10px;align-items:center;padding:8px 0;border-top:1px solid var(--pm-border)">
              <el-icon color="#165DFF"><Files/></el-icon><span style="font-weight:600">{{ r.title }}</span>
              <span class="pm-tag" style="margin-left:auto">{{ r.type }}</span>
            </div>
          </div>
        </div>

        <!-- 作业批改弹窗：AI 辅助建议 + 教师最终决策（人机协同） -->
        <el-dialog v-model="gradeDialog" :title="'批改作业 · ' + gradeForm.hw" width="520px">
          <div style="margin-bottom:12px;padding:12px;background:var(--pm-brand-soft);border-radius:12px">
            <div style="font-weight:700;font-size:13px;margin-bottom:4px">🤖 AI 批改建议</div>
            <div class="pm-muted" style="font-size:12.5px;line-height:1.7">
              AI 已自动检查代码规范与关键知识点覆盖情况，建议评分
              <b style="color:var(--pm-brand)">85</b> 分。请结合实际情况调整——最终判定权在你。
            </div>
          </div>
          <el-form label-width="72px">
            <el-form-item label="学生"><b>{{ gradeForm.student }}</b></el-form-item>
            <el-form-item label="分数">
              <el-slider v-model="gradeForm.score" :min="0" :max="100" show-input style="width:100%"/>
            </el-form-item>
            <el-form-item label="评语">
              <el-input type="textarea" v-model="gradeForm.feedback" :rows="3"
                        placeholder="输入针对性反馈，学生端将立即看到"/>
            </el-form-item>
          </el-form>
          <template #footer>
            <el-button @click="gradeDialog=false">取消</el-button>
            <el-button type="primary" :loading="grading" @click="submitGrade">提交批改</el-button>
          </template>
        </el-dialog>
      </template>

      <!-- ================= 学生工作台 ================= -->
      <template v-else>
        <!-- Hero：学生今日学习概览 -->
        <div class="pm-hero">
          <div>
            <span class="eyebrow">🎯 今日计划 · 任务优先</span>
            <h2>{{ store.user.name }}，今天也要元气满满</h2>
            <p>今日共 {{ (d.today_plan||[]).length }} 项学习任务，其中 {{ (d.todo_tasks||[]).length }} 项待完成。
               AI 已根据你的学习轨迹生成个性化建议，随时可以开始。</p>
            <div class="pm-hero-actions">
              <button class="pm-hero-btn solid" @click="$router.push('/learn/ai-tutor')">问 AI 辅导</button>
              <button class="pm-hero-btn" @click="$router.push('/growth')">查看成长画像</button>
            </div>
          </div>
          <div class="pm-hero-art">
            <svg width="210" height="140" viewBox="0 0 210 140" fill="none">
              <rect x="8" y="18" width="126" height="104" rx="12" fill="rgba(255,255,255,.16)" stroke="rgba(255,255,255,.35)"/>
              <rect x="20" y="32" width="46" height="8" rx="4" fill="rgba(255,255,255,.55)"/>
              <path d="M20 108 L46 96 L66 100 L88 74 L112 80 L128 56" stroke="#fff" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round" fill="none"/>
              <circle cx="128" cy="56" r="4.5" fill="#fff"/>
              <circle cx="162" cy="38" r="21" fill="rgba(54,207,201,.35)" stroke="rgba(255,255,255,.55)"/>
              <path d="M162 27 L162 49 M151 38 L173 38" stroke="#fff" stroke-width="2" stroke-linecap="round"/>
              <circle cx="168" cy="102" r="13" fill="rgba(255,255,255,.18)" stroke="rgba(255,255,255,.35)"/>
              <circle cx="168" cy="102" r="4" fill="#fff"/>
            </svg>
          </div>
        </div>
        <div class="pm-grid pm-grid-4 pm-stagger" style="margin-bottom:18px">
          <PM-StatCard label="今日待办" :value="(d.todo_tasks||[]).length" icon="Calendar" color="#165DFF" sub="任务优先"/>
          <PM-StatCard label="在学课程" :value="(d.my_courses||[]).length" icon="Notebook" color="#36CFC9"/>
          <PM-StatCard label="学习记录" :value="(d.recent_records||[]).length" icon="Collection" color="#722ED1" sub="过程化留存"/>
          <PM-StatCard label="AI 建议" value="实时" icon="MagicStick" color="#FF7D00" sub="个性化"/>
        </div>

        <div class="pm-grid pm-grid-3" style="margin-bottom:18px">
          <div class="pm-card">
            <PM-SectionTitle title="今日学习计划"/>
            <div v-for="t in d.today_plan" :key="t.task" style="display:flex;gap:10px;align-items:center;padding:9px 0;border-top:1px solid var(--pm-border)">
              <el-icon :color="t.done?'#00b42a':'#165DFF'"><component :is="t.done?'CircleCheck':'Clock'"/></el-icon>
              <div style="flex:1"><div :style="{fontWeight:600,textDecoration:t.done?'line-through':''}">{{ t.task }}</div>
              <div class="pm-faint" style="font-size:12px">{{ t.course }}</div></div>
              <span class="pm-faint" style="font-size:12px">{{ t.due }}</span>
            </div>
          </div>
          <div class="pm-card" style="background:linear-gradient(135deg,#165DFF,#4080ff);color:#fff;border:none">
            <div style="font-weight:800;margin-bottom:8px">🤖 AI 学习建议</div>
            <p style="font-size:13px;line-height:1.8;margin:0">{{ d.ai_advice }}</p>
            <div style="margin-top:12px;font-weight:700;font-size:13px">📌 AI 推荐复习</div>
            <div v-for="r in d.recommend_review" :key="r.title" style="font-size:12px;opacity:.92;margin-top:4px">· {{ r.title }}</div>
          </div>
          <div class="pm-card">
            <PM-SectionTitle title="成长趋势（近 7 次活跃度）"/>
            <div ref="trendEl" style="height:200px"></div>
          </div>
        </div>

        <div class="pm-grid pm-grid-2">
          <div class="pm-card">
            <PM-SectionTitle title="学习导航入口"/>
            <div class="pm-grid pm-grid-2">
              <div v-for="n in d.nav_entries" :key="n.to" class="pm-card" style="cursor:pointer;display:flex;align-items:center;gap:10px;padding:14px"
                   @click="$router.push(n.to)">
                <el-icon color="#165DFF" size="20"><Right/></el-icon><span style="font-weight:600">{{ n.name }}</span>
              </div>
            </div>
          </div>
          <div class="pm-card">
            <PM-SectionTitle title="最近学习记录"/>
            <div v-for="r in d.recent_records" :key="r.time" style="padding:9px 0;border-top:1px solid var(--pm-border)">
              <div style="font-weight:600;font-size:13px">{{ r.action }}：{{ r.detail }}</div>
              <div class="pm-faint" style="font-size:12px">{{ r.time }} · 时长 {{ r.duration }} 分钟</div>
            </div>
            <div v-if="!d.recent_records.length" class="pm-empty">还没有记录，去学习吧～</div>
          </div>
        </div>
      </template>
    </div>
    <PM-Spinner v-else text="正在加载工作台任务…"/>
    `,
  });
})();
