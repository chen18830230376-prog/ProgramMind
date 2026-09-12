/* ============================================================
   个人中心 Profile（我的）
   子功能：个人信息编辑 / 历史 AI 对话 / 收藏 / 消息通知 / 系统设置（含明暗切换）
   ============================================================ */
window.PM = window.PM || {};
(function () {
  const { defineComponent, ref, reactive, onMounted } = Vue;

  PM.Profile = defineComponent({
    setup() {
      const d = ref(null);
      const form = reactive({ name:"", email:"", intro:"" });
      const tab = ref("info");
      const store = PM.store;
      const dnd = ref(false);                  // 消息免打扰（do not disturb）开关状态
      const avatarChoice = ref("");          // 当前选中的头像值（"" = 姓名默认）
      const fileInput = ref(null);
      // 内置表情头像（类似学习通，可选一个简单图标作为头像）
      const PRESET_EMOJIS = ["🦊","🐱","🐼","🐰","🦁","🐸","🐵","🐯","🐶","🐻","🐨","🐷","🐧","🦄","🐙","🌟","🍎","🚀","🎓","💡"];

      onMounted(async () => {
        const r = await PM.api("/api/profile"); if (r.code === 0) {
          d.value = r.data;
          form.name = r.data.user.name; form.email = r.data.user.email; form.intro = r.data.user.intro || "";
          avatarChoice.value = r.data.user.avatar || "";
          dnd.value = !!r.data.user.do_not_disturb;
        }
      });

      // 头像：恢复默认（按姓名首字显示）
      function pickDefault(){ avatarChoice.value = ""; }
      // 头像：选择一个内置 emoji 表情
      function pickEmoji(e){ avatarChoice.value = "emoji:" + e; }
      // 头像：触发文件选择
      function triggerUpload(){ if (fileInput.value) fileInput.value.click(); }
      // 头像：读取并裁剪为 256px 以内的 base64（控制体积，便于入库与传输）
      function fileToDataURL(file, maxDim, quality){
        maxDim = maxDim || 256; quality = quality || 0.85;
        return new Promise((resolve, reject) => {
          const reader = new FileReader();
          reader.onload = () => {
            const img = new Image();
            img.onload = () => {
              let w = img.width, h = img.height;
              if (w > h && w > maxDim){ h = Math.round(h * maxDim / w); w = maxDim; }
              else if (h > maxDim){ w = Math.round(w * maxDim / h); h = maxDim; }
              const cv = document.createElement("canvas");
              cv.width = w; cv.height = h;
              cv.getContext("2d").drawImage(img, 0, 0, w, h);
              resolve(cv.toDataURL("image/jpeg", quality));
            };
            img.onerror = reject; img.src = reader.result;
          };
          reader.onerror = reject; reader.readAsDataURL(file);
        });
      }
      async function onFile(e){
        const f = e.target.files && e.target.files[0];
        if (!f) return;
        try { avatarChoice.value = await fileToDataURL(f); }
        catch(_) { ElementPlus.ElMessage.error("图片读取失败，请换一张"); }
        e.target.value = "";
      }

      async function save(){
        const r = await PM.api("/api/profile", {
          method: "POST",
          body: JSON.stringify({ name: form.name, email: form.email, intro: form.intro, avatar: avatarChoice.value }),
        });
        if (r.code === 0) {
          d.value.user.avatar = r.user.avatar;
          d.value.user.name = r.user.name; d.value.user.email = r.user.email; d.value.user.intro = r.user.intro || "";
          if (PM.store.user) { PM.store.user.avatar = r.user.avatar; PM.store.user.name = r.user.name; }
          ElementPlus.ElMessage.success("资料已保存");
        } else {
          ElementPlus.ElMessage.error(r.msg || "保存失败");
        }
      }
      const themeText = () => PM.store.theme === "dark" ? "暗黑模式" : "浅色模式";
      function toggleTheme(){ PM.toggleTheme(); }

      // 消息免打扰：切换后立即持久化到后端
      async function saveDnd(val){
        dnd.value = !!val;
        const r = await PM.api("/api/profile", {
          method: "POST",
          body: JSON.stringify({ do_not_disturb: val ? 1 : 0 }),
        });
        if (r.code === 0) {
          if (d.value) d.value.user.do_not_disturb = val ? 1 : 0;
          if (PM.store.user) PM.store.user.do_not_disturb = val ? 1 : 0;
          ElementPlus.ElMessage.success(val ? "已开启消息免打扰" : "已关闭消息免打扰");
        } else {
          dnd.value = !val;
          ElementPlus.ElMessage.error(r.msg || "设置失败");
        }
      }

      // 取消收藏（收藏项来自 AI 回答 / 资料等，体现知识沉淀）
      async function removeFav(f){
        const r = await PM.api("/api/profile/favorite", {
          method: "POST", body: JSON.stringify({ action: "remove", id: f.id }),
        });
        if (r.code === 0) { d.value.favorites = r.data; ElementPlus.ElMessage.success("已取消收藏"); }
      }
      // 标记通知已读（支持 all）
      async function markRead(id){
        const r = await PM.api("/api/notifications/read", {
          method: "POST", body: JSON.stringify({ id }),
        });
        if (r.code === 0) {
          const rr = await PM.api("/api/profile");
          if (rr.code === 0) d.value.notifications = rr.data.notifications;
          ElementPlus.ElMessage.success(id === "all" ? "已全部标记已读" : "已标记已读");
        }
      }

      return { d, form, tab, store, avatarChoice, fileInput, PRESET_EMOJIS, pickDefault, pickEmoji, triggerUpload, onFile, save, themeText, toggleTheme, saveDnd, dnd, removeFav, markRead };
    },
    template: `
    <div class="pm-page pm-anim-in" v-if="d">
      <PM-SectionTitle title="个人中心"/>
      <div class="pm-grid pm-grid-3" style="margin-bottom:16px">
        <div class="pm-card" style="grid-column:span 1;text-align:center">
          <pm-avatar :name="d.user.name" :src="avatarChoice || d.user.avatar" :size="84"/>
          <div style="font-weight:800;font-size:17px;margin-top:10px">{{ d.user.name }}</div>
          <div class="pm-faint">{{ d.user.role==='teacher'?'教师':'学生' }} · {{ d.user.school }}</div>
          <div class="pm-faint" style="font-size:12px;margin-top:4px">账号：{{ d.user.username }}</div>
          <div style="margin-top:12px;display:flex;gap:8px;justify-content:center;flex-wrap:wrap">
            <el-button size="small" @click="pickDefault">默认(名字)</el-button>
            <el-button size="small" @click="triggerUpload">上传图片</el-button>
            <input ref="fileInput" type="file" accept="image/*" style="display:none" @change="onFile"/>
          </div>
        </div>
        <div class="pm-card" style="grid-column:span 2">
          <el-tabs v-model="tab">
            <el-tab-pane label="个人信息" name="info">
              <el-form label-width="80px" style="max-width:480px">
                <el-form-item label="头像">
                  <div style="display:flex;flex-wrap:wrap;gap:8px;max-width:440px">
                    <div v-for="e in PRESET_EMOJIS" :key="e" @click="pickEmoji(e)"
                         :style="{ width:'40px',height:'40px',borderRadius:'50%',display:'flex',alignItems:'center',justifyContent:'center',cursor:'pointer',fontSize:'22px',background: avatarChoice==='emoji:'+e ? 'var(--pm-brand-soft)' : 'var(--pm-surface-2)', border: avatarChoice==='emoji:'+e ? '2px solid var(--pm-brand)' : '2px solid transparent', transition:'all .15s' }">{{ e }}</div>
                  </div>
                  <div class="pm-faint" style="font-size:12px;margin-top:6px">点选表情设为头像；或点上方「上传图片」使用自己的图；「默认(名字)」则为姓名首字圆。</div>
                </el-form-item>
                <el-form-item label="昵称"><el-input v-model="form.name"/></el-form-item>
                <el-form-item label="邮箱"><el-input v-model="form.email"/></el-form-item>
                <el-form-item label="简介"><el-input type="textarea" v-model="form.intro" :rows="3"/></el-form-item>
                <el-button type="primary" @click="save">保存修改</el-button>
              </el-form>
            </el-tab-pane>
            <el-tab-pane label="历史 AI 对话" name="history">
              <div v-for="(m,i) in d.history" :key="i" style="padding:8px 0;border-top:1px solid var(--pm-border)">
                <div style="font-size:12px" :class="m.role==='ai'?'pm-faint':'pm-muted'">{{ m.role==='ai'?'AI':'我' }} · {{ m.time }}</div>
                <div style="font-size:13px;white-space:pre-wrap">{{ m.text.slice(0,120) }}{{ m.text.length>120?'…':'' }}</div>
              </div>
              <div v-if="!d.history.length" class="pm-empty">暂无对话记录</div>
            </el-tab-pane>
            <el-tab-pane label="收藏" name="fav">
              <div v-for="f in d.favorites" :key="f.id" style="display:flex;gap:10px;align-items:center;padding:8px 0;border-top:1px solid var(--pm-border)">
                <el-icon color="#165DFF"><Star/></el-icon><span style="font-weight:600;flex:1">{{ f.title }}</span>
                <el-tag size="small">{{ f.type }}</el-tag><span class="pm-faint" style="font-size:12px">{{ f.course }}</span>
              </div>
              <div v-if="!d.favorites.length" class="pm-empty">暂无收藏</div>
            </el-tab-pane>
            <el-tab-pane label="消息通知" name="noti">
              <div v-for="n in d.notifications" :key="n.id" style="padding:10px 0;border-top:1px solid var(--pm-border)">
                <div style="font-weight:600;font-size:13px">{{ n.title }}</div>
                <div class="pm-muted" style="font-size:12px">{{ n.text }}</div>
                <div class="pm-faint" style="font-size:11px">{{ n.time }}</div>
              </div>
            </el-tab-pane>
            <el-tab-pane label="系统设置" name="set">
              <div style="display:flex;justify-content:space-between;align-items:center;padding:12px 0;border-top:1px solid var(--pm-border)">
                <div><b>主题模式</b><div class="pm-faint" style="font-size:12px">当前：{{ themeText() }}</div></div>
                <el-switch :model-value="store.theme==='dark'" @change="toggleTheme" active-text="暗黑" inactive-text="浅色"/>
              </div>
              <div style="display:flex;justify-content:space-between;align-items:center;padding:12px 0;border-top:1px solid var(--pm-border)">
                <div><b>消息免打扰</b><div class="pm-faint" style="font-size:12px">开启后不再接收作业/学情等消息提醒</div></div>
                <el-switch :model-value="dnd" @change="saveDnd" active-text="开" inactive-text="关"/>
              </div>
              <div class="pm-faint" style="font-size:12px;padding-top:12px">ProgramMind v1.0 · AI-Native 教学科研平台 · 演示版</div>
            </el-tab-pane>
          </el-tabs>
        </div>
      </div>
    </div><PM-Spinner v-else/>`,
  });
})();
