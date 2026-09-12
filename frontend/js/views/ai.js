/* ============================================================
   AI 助手模块（全部用户可见 · AI 能力中心）
   【强调】不是单纯聊天框，而是“AI 能力中心”：
   集成 AI 问答 / 文档生成 / 命题 / 总结 / Agent 多任务工作流演示。
   工作流示例：教材分析 → 教案生成 → PPT 生成 → 作业设计（完整流程演示）
   所有输出均为前端模拟，体现 AI-Native 渗透到各业务。
   ============================================================ */
window.PM = window.PM || {};
(function () {
  const { defineComponent, ref, reactive, nextTick } = Vue;

  PM.AICenter = defineComponent({
    setup() {
      const tools = [
        { key: "qa", name: "AI 问答", icon: "ChatDotRound", desc: "基于学科知识库的问答" },
        { key: "doc", name: "AI 文档生成", icon: "Document", desc: "生成报告/大纲草稿" },
        { key: "qgen", name: "AI 命题", icon: "Promotion", desc: "按知识点智能出题" },
        { key: "sum", name: "AI 总结", icon: "Memo", desc: "长文本要点提炼" },
        { key: "flow", name: "Agent 工作流", icon: "Cpu", desc: "教材→教案→PPT→作业" },
      ];
      const active = ref("qa");

      // 问答
      const qInput = ref(""); const qMessages = ref([{ role:"ai", html:"我是 ProgramMind 通用学科助手，问我就好～" }]);
      const qBox = ref(null);
      function qSend(){
        const t = qInput.value.trim(); if(!t) return; qMessages.value.push({role:"user",html:t}); qInput.value="";
        const ai = reactive({role:"ai",html:"",sources:[],cited:[],q:t,course:"计算机学科"}); qMessages.value.push(ai);
        PM.callAI("answer", { question: t, course: "计算机学科" },
          (c) => { ai.html = c; },
          (text, sources, cited) => {
            ai.html = text || ai.html; ai.sources = sources || []; ai.cited = cited || []; scroll();
          }); scroll();
      }
      function scroll(){ nextTick(()=>{ if(qBox.value) qBox.value.scrollTop=qBox.value.scrollHeight; }); }

      // 文档生成
      const docTopic = ref("实验报告：链表反转"); const docType = ref("实验报告"); const docOut = ref("");
      function genDoc(){ PM.callAI("doc", { topic: docTopic.value, type: docType.value }, (c) => { docOut.value = c; }, () => {}); }

      // 命题
      const qPoints = ref(["二叉树","链表","栈"]); const qDiff = ref("medium"); const qOut = ref("");
      function genQ(){ PM.callAI("questions", { points: qPoints.value, difficulty: qDiff.value }, (c) => { qOut.value = c; }, () => {}); }

      // 总结
      const sumIn = ref("本节课讲解了树的定义、遍历方式与性质，强调递归实现与前中后序区别……"); const sumOut = ref("");
      function genSum(){ PM.callAI("summarize", { text: sumIn.value }, (c) => { sumOut.value = c; }, () => {}); }

      // Agent 工作流
      const flowSteps = ["教材分析","教案生成","PPT生成","作业设计"];
      const flowState = reactive({ running:false, current:-1, logs:[], done:[] });
      function runFlow(){
        if(flowState.running) return;
        flowState.running=true; flowState.current=-1; flowState.logs=[]; flowState.done=[];
        let i=0;
        const step = ()=>{
          if(i>=flowSteps.length){ flowState.running=false; flowState.current=-1; flowState.logs.push("✅ 工作流完成：已产出教案、PPT 大纲与作业设计，可一键发布。"); return; }
          flowState.current=i;
          const line = reactive({ step: flowSteps[i], text:"" });
          flowState.logs.push(line);
          PM.callAI("workflow", { step: flowSteps[i] },
            (c) => { line.text = c; },
            () => { flowState.done.push(i); i++; setTimeout(step, 500); });
        };
        step();
      }

      return { tools, active, qInput, qMessages, qBox, qSend,
        docTopic, docType, docOut, genDoc,
        qPoints, qDiff, qOut, genQ,
        sumIn, sumOut, genSum,
        flowSteps, flowState, runFlow };
    },
    template: `
    <div class="pm-page pm-anim-in">
      <PM-SectionTitle title="AI 助手 · 能力中心"/>
      <div class="pm-grid pm-grid-4" style="margin-bottom:16px">
        <div v-for="t in tools" :key="t.key" class="pm-card" style="cursor:pointer" :style="active===t.key?{borderColor:'var(--pm-brand)',boxShadow:'var(--pm-shadow-hover)'}:{}" @click="active=t.key">
          <el-icon :color="active===t.key?'#165DFF':'#9fb0cc'" size="22"><component :is="t.icon"/></el-icon>
          <div style="font-weight:700;margin-top:6px">{{ t.name }}</div>
          <div class="pm-faint" style="font-size:12px">{{ t.desc }}</div>
        </div>
      </div>

      <!-- AI 问答 -->
      <div v-if="active==='qa'" class="pm-card" style="height:calc(100vh - 280px);display:flex;flex-direction:column">
        <div ref="qBox" style="flex:1;overflow:auto;padding:8px">
          <div v-for="(m,i) in qMessages" :key="i" style="display:flex;margin-bottom:14px" :style="{justifyContent:m.role==='user'?'flex-end':'flex-start'}">
            <div style="max-width:80%;display:flex;flex-direction:column;gap:8px;align-items:flex-start">
              <div :style="{padding:'10px 14px',borderRadius:'14px',whiteSpace:'pre-wrap',lineHeight:'1.7',background:m.role==='user'?'#165DFF':'var(--pm-surface-2)',color:m.role==='user'?'#fff':'var(--pm-text)',border:'1px solid var(--pm-border)'}">
                <span v-html="m.html"></span>
              </div>
              <PM-KnowledgeSources v-if="m.role==='ai'" :sources="m.sources || []" :cited="m.cited || []"
                                   :query="m.q || ''" :course="m.course || ''"/>
            </div>
          </div>
        </div>
        <div style="display:flex;gap:10px;padding-top:10px;border-top:1px solid var(--pm-border)">
          <el-input v-model="qInput" placeholder="输入任何学科问题…" @keyup.enter="qSend"/><el-button type="primary" @click="qSend">发送</el-button>
        </div>
      </div>

      <!-- AI 文档生成 -->
      <div v-else-if="active==='doc'" class="pm-grid pm-grid-2">
        <div class="pm-card">
          <el-form label-position="top">
            <el-form-item label="主题"><el-input v-model="docTopic"/></el-form-item>
            <el-form-item label="文档类型"><el-select v-model="docType" style="width:100%"><el-option label="实验报告" value="实验报告"/><el-option label="课程总结" value="课程总结"/><el-option label="教案" value="教案"/></el-select></el-form-item>
            <el-button type="primary" @click="genDoc"><el-icon><Document/></el-icon> 生成</el-button>
          </el-form>
        </div>
        <div class="pm-card"><pre v-if="docOut" style="white-space:pre-wrap;font-size:13px;line-height:1.7;background:var(--pm-surface-2);padding:12px;border-radius:10px" v-html="docOut"></pre><div v-else class="pm-empty">点击生成</div></div>
      </div>

      <!-- AI 命题 -->
      <div v-else-if="active==='qgen'" class="pm-grid pm-grid-2">
        <div class="pm-card">
          <div style="font-weight:600;margin-bottom:8px">知识点</div>
          <el-checkbox-group v-model="qPoints"><el-checkbox v-for="p in ['二叉树','链表','栈','TCP','IP','HTTP','函数定义','面向对象']" :key="p" :value="p" border style="margin:4px">{{ p }}</el-checkbox></el-checkbox-group>
          <div style="font-weight:600;margin:12px 0 8px">难度</div>
          <el-radio-group v-model="qDiff"><el-radio value="easy" border>基础</el-radio><el-radio value="medium" border>中等</el-radio><el-radio value="hard" border>提高</el-radio></el-radio-group>
          <div style="margin-top:12px"><el-button type="primary" :disabled="!qPoints.length" @click="genQ"><el-icon><Promotion/></el-icon> 生成</el-button></div>
        </div>
        <div class="pm-card"><pre v-if="qOut" style="white-space:pre-wrap;font-size:13px;line-height:1.7;background:var(--pm-surface-2);padding:12px;border-radius:10px" v-html="qOut"></pre><div v-else class="pm-empty">选择知识点</div></div>
      </div>

      <!-- AI 总结 -->
      <div v-else-if="active==='sum'" class="pm-grid pm-grid-2">
        <div class="pm-card"><div style="font-weight:600;margin-bottom:8px">原文</div><el-input type="textarea" v-model="sumIn" :rows="8"/></div>
        <div class="pm-card"><div style="font-weight:700;margin-bottom:8px">AI 总结</div><pre v-if="sumOut" style="white-space:pre-wrap;font-size:13px;line-height:1.7;background:var(--pm-surface-2);padding:12px;border-radius:10px" v-html="sumOut"></pre><el-button v-else type="primary" @click="genSum">生成总结</el-button></div>
      </div>

      <!-- Agent 工作流 -->
      <div v-else class="pm-card">
        <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:12px">
          <div style="font-weight:700">多任务 Agent 工作流演示：教材分析 → 教案生成 → PPT 生成 → 作业设计</div>
          <el-button type="primary" :loading="flowState.running" @click="runFlow"><el-icon><VideoPlay/></el-icon> {{ flowState.running?'运行中…':'运行工作流' }}</el-button>
        </div>
        <div style="display:flex;gap:10px;flex-wrap:wrap;margin-bottom:14px">
          <div v-for="(s,i) in flowSteps" :key="s" class="pm-tag" :style="flowState.done.includes(i)?{background:'rgba(0,180,42,.12)',color:'#00b42a'}:(flowState.current===i?{background:'var(--pm-brand-soft)',color:'var(--pm-brand)'}:{})">
            <el-icon v-if="flowState.done.includes(i)"><CircleCheck/></el-icon> {{ s }}
          </div>
        </div>
        <div style="background:var(--pm-surface-2);border-radius:12px;padding:14px;min-height:160px;font-family:monospace;font-size:13px;line-height:1.8">
          <div v-for="(l,i) in flowState.logs" :key="i">
            <span style="color:var(--pm-brand);font-weight:700">[{{ l.step }}]</span> <span class="pm-cursor" v-if="flowState.current===i && flowState.running">{{ l.text }}</span><span v-else>{{ l.text }}</span>
          </div>
          <div v-if="!flowState.logs.length" class="pm-faint">点击“运行工作流”查看 AI 如何串联多个教学任务。</div>
        </div>
      </div>
    </div>`,
  });
})();
