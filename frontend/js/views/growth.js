/* ============================================================
   成长模块 Growth（全部用户可见 · 平台核心创新亮点）
   体现“记录完整学习过程，而不只记录考试结果”：
   - 学习画像（标签 + 理论/实践能力）
   - 知识掌握热力地图（近 18 周活跃度，ECharts 热力图）
   - 成长轨迹时间线（过程化事件）
   - 学习导航推荐（AI 个性化）
   - 理论/实践能力分析（雷达图）
   - AI 个性化成长建议 + 自动生成成长报告预览
   ============================================================ */
window.PM = window.PM || {};
(function () {
  const { defineComponent, ref, onMounted, nextTick } = Vue;

  function initChart(el, option) {
    if (!el) return;
    const c = echarts.init(el, document.documentElement.classList.contains("dark") ? "dark" : null);
    c.setOption(option); window.addEventListener("resize", () => c.resize()); return c;
  }

  PM.Growth = defineComponent({
    setup() {
      const d = ref(null);
      const heatEl = ref(null); const radarEl = ref(null); const report = ref("");

      onMounted(async () => {
        const r = await PM.api("/api/growth"); if (r.code !== 0) return;
        d.value = r.data; await nextTick();
        renderHeat(); renderRadar();
      });

      function renderHeat() {
        const vals = (d.value.heatmap || []).map(x => x.value);
        const weeks = 18, days = 7; const data = [];
        for (let i = 0; i < weeks * days; i++) data.push([i % weeks, Math.floor(i / weeks), vals[i] || 0]);
        initChart(heatEl.value, {
          tooltip: { position: "top" },
          grid: { left: 40, right: 16, top: 10, bottom: 30 },
          xAxis: { type: "category", data: Array.from({length:weeks},(_,i)=>"W"+(i+1)), axisLabel:{ color:"#9fb0cc", fontSize:10 }, splitArea:{ show:true } },
          yAxis: { type: "category", data: ["一","二","三","四","五","六","日"], axisLabel:{ color:"#9fb0cc" }, splitArea:{ show:true } },
          visualMap: { min:0, max:9, calculable:true, orient:"horizontal", left:"center", bottom:0, textStyle:{color:"#9fb0cc"},
            inRange:{ color:["#1a2540","#165DFF","#40c4ff"] } },
          series: [{ type:"heatmap", data, label:{ show:false }, emphasis:{ itemStyle:{ shadowBlur:8, shadowColor:"rgba(0,0,0,.4)" } } }],
        });
      }

      function renderRadar() {
        const avg = (arr) => Math.round(arr.reduce((a,b)=>a+b,0)/Math.max(arr.length,1));
        const m = d.value.mastery || [];
        const prog = avg(m.filter(x=>["变量与类型","函数定义","面向对象","顺序表","链表","栈"].includes(x.name)).map(x=>x.value));
        const algo = avg(m.filter(x=>["二叉树","堆","图的存储","最短路径"].includes(x.name)).map(x=>x.value));
        const net  = avg(m.filter(x=>["HTTP","TCP","IP","TLS/SSL"].includes(x.name)).map(x=>x.value));
        initChart(radarEl.value, {
          tooltip: {},
          radar: { indicator: [
            { name:"编程能力", max:100 },{ name:"算法思维", max:100 },{ name:"网络理解", max:100 },
            { name:"理论基础", max:100 },{ name:"实践能力", max:100 },{ name:"协作沟通", max:100 } ],
            axisName:{ color:"#9fb0cc" }, splitLine:{ lineStyle:{ color:"rgba(136,136,136,.2)" } } },
          series: [{ type:"radar", data:[{ value:[prog, algo, net, d.value.theory, d.value.practice, 75],
            areaStyle:{ color:"rgba(22,93,255,.25)" }, lineStyle:{ color:"#165DFF" }, itemStyle:{ color:"#165DFF" } }] }],
        });
      }

      function genReport() {
        const weak = (d.value.mastery||[]).filter(x=>x.value<55).map(x=>x.name).join("、") || "图论与网络层协议";
        const strong = (d.value.mastery||[]).filter(x=>x.value>=80).map(x=>x.name).join("、") || "动手实验、代码实现";
        report.value = PM.mockAI.growthReport((PM.store.user&&PM.store.user.name)||"同学", weak, strong);
      }

      return { d, heatEl, radarEl, report, genReport };
    },
    template: `
    <div class="pm-page pm-anim-in" v-if="d">
      <PM-SectionTitle title="成长模块 · 全过程学习记录"/>
      <div class="pm-muted" style="margin-bottom:14px">这里记录的不是考试分数，而是你每一次学习、实验、提问与辅导的足迹。</div>

      <div class="pm-grid pm-grid-4 pm-stagger" style="margin-bottom:18px">
        <PM-StatCard label="学习画像标签" :value="(d.tags||[]).length" icon="Collection" color="#165DFF" sub="多维刻画"/>
        <PM-StatCard label="理论能力" :value="d.theory" icon="Reading" color="#36CFC9" sub="/100"/>
        <PM-StatCard label="实践能力" :value="d.practice" icon="Cpu" color="#722ED1" sub="/100"/>
        <PM-StatCard label="推荐学习项" :value="(d.recommendations||[]).length" icon="Compass" color="#FF7D00" sub="AI 个性化"/>
      </div>

      <div class="pm-grid pm-grid-2" style="margin-bottom:18px">
        <div class="pm-card">
          <PM-SectionTitle title="知识掌握热力地图（近 18 周）"/>
          <div ref="heatEl" style="height:300px"></div>
        </div>
        <div class="pm-card">
          <PM-SectionTitle title="理论 / 实践能力分析"/>
          <div ref="radarEl" style="height:300px"></div>
        </div>
      </div>

      <div class="pm-grid pm-grid-2" style="margin-bottom:18px">
        <div class="pm-card">
          <PM-SectionTitle title="成长轨迹时间线"/>
          <div style="position:relative;padding-left:22px">
            <div style="position:absolute;left:6px;top:0;bottom:0;width:2px;background:var(--pm-border)"></div>
            <div v-for="(t,i) in d.timeline" :key="i" style="position:relative;padding:0 0 16px 14px">
              <span style="position:absolute;left:-19px;top:4px;width:13px;height:13px;border-radius:50%;background:var(--pm-brand);box-shadow:0 0 0 4px var(--pm-brand-soft)"></span>
              <div style="font-weight:600;font-size:13px">{{ t.date }} · {{ t.text }}</div>
              <div class="pm-faint" style="font-size:12px">{{ t.type }}</div>
            </div>
          </div>
        </div>
        <div class="pm-card" style="background:linear-gradient(135deg,#165DFF,#4080ff);color:#fff;border:none">
          <div style="font-weight:800;margin-bottom:8px">🤖 AI 个性化成长建议</div>
          <p style="font-size:13px;line-height:1.8">{{ d.ai_advice }}</p>
          <div style="margin-top:12px;font-weight:700">📌 学习导航推荐</div>
          <div v-for="r in d.recommendations" :key="r.title" style="font-size:12px;opacity:.95;margin-top:6px">· {{ r.title }} — {{ r.reason }}</div>
        </div>
      </div>

      <div class="pm-card">
        <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:10px">
          <PM-SectionTitle title="成长报告（AI 自动生成预览）"/>
          <el-button type="primary" @click="genReport"><el-icon><Document/></el-icon> 生成报告</el-button>
        </div>
        <pre v-if="report" style="white-space:pre-wrap;font-size:13px;line-height:1.7;background:var(--pm-surface-2);padding:14px;border-radius:10px" v-html="report"></pre>
        <div v-else class="pm-empty">点击“生成报告”查看 AI 为你撰写的成长报告</div>
      </div>
    </div><PM-Spinner v-else text="正在加载成长数据…"/>`,
  });
})();
