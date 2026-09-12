/* ============================================================
   登录页（Login）
   - 账号密码登录，区分教师 / 学生身份
   - 登录失败：ElMessage 友好提示（对应“flash 消息提示”要求）
   - 登录成功：写入会话并跳转对应身份工作台
   - 未登录访问内部页：由路由守卫统一拦截跳转此处
   ============================================================ */
window.PM = window.PM || {};
(function () {
  const { defineComponent, ref, onMounted } = Vue;

  PM.Login = defineComponent({
    setup() {
      const router = VueRouter.useRouter();
      const mode = ref("login");           // 'login' | 'register'
      const role = ref("student");
      const form = ref({ username: "", password: "" });

      // 注册表单（默认角色为 student，新学生注册后即可选课学习）
      const reg = ref({ username: "", password: "", name: "", school: "", major: "", grade: "" });
      const majors = ref([]);              // 专业下拉数据（来自 /api/courses/majors）
      const loading = ref(false);

      // 进入注册页时拉取可选专业，驱动“选专业 -> 自动匹配课程”
      onMounted(async () => {
        const r = await PM.api("/api/courses/majors");
        if (r.code === 0) majors.value = r.data;
      });

      async function submit() {
        if (!form.value.username || !form.value.password) {
          ElementPlus.ElMessage.warning("请输入账号和密码");
          return;
        }
        loading.value = true;
        const r = await PM.api("/api/auth/login", {
          method: "POST",
          body: JSON.stringify({ ...form.value, role: role.value }),
        });
        loading.value = false;
        if (r.code === 0) {
          PM.setUser(r.user);
          ElementPlus.ElMessage.success("登录成功，正在进入工作台…");
          router.push("/workspace");
        } else {
          ElementPlus.ElMessage.error(r.msg || "登录失败");
        }
      }

      async function doRegister() {
        const d = reg.value;
        if (!d.username || !d.password || !d.name) {
          ElementPlus.ElMessage.warning("请填写账号、密码和姓名");
          return;
        }
        // 学生注册必须选择专业，才能自动匹配课程
        if (role.value === "student" && !d.major) {
          ElementPlus.ElMessage.warning("请选择你的专业，我们将为你自动匹配课程");
          return;
        }
        loading.value = true;
        const r = await PM.api("/api/auth/register", {
          method: "POST",
          body: JSON.stringify({ ...d, role: role.value }),
        });
        loading.value = false;
        if (r.code === 0) {
          PM.setUser(r.user);
          // 明确告知自动加入 / 推荐的课程，体现“选专业即匹配课程”
          let tip = "注册成功，已自动登录！";
          if (r.auto_joined && r.auto_joined.length) {
            tip += " 已为你自动加入核心课：" + r.auto_joined.join("、") + "。";
          }
          if (r.recommended && r.recommended.length) {
            tip += " 另推荐你选修：" + r.recommended.join("、") + "。";
          }
          ElementPlus.ElMessage.success({ message: tip, duration: 4000 });
          router.push("/workspace");
        } else {
          ElementPlus.ElMessage.error(r.msg || "注册失败");
        }
      }

      function fillDemo(r) {
        role.value = r;
        form.value.username = r === "teacher" ? "teacher01" : "student01";
        form.value.password = form.value.username;
      }

      return { mode, role, form, reg, majors, loading, submit, doRegister, fillDemo };
    },
    template: `
    <div class="pm-login">
      <!-- 品牌侧：科技教育风插画（内联 SVG 知识网络） -->
      <aside class="pm-login-aside">
        <div class="glow g1"></div><div class="glow g2"></div><div class="glow g3"></div>
        <div class="pm-logo" style="color:#fff;font-size:22px;margin-bottom:24px;font-weight:800">
          <span class="mark">PM</span> ProgramMind
        </div>
        <h1 style="font-size:31px;line-height:1.42;margin:0 0 14px;font-weight:800;letter-spacing:.3px">
          面向高校计算机学科的<br/>AI-Native 教学科研平台
        </h1>
        <p style="color:#a9c0ee;max-width:430px;line-height:1.9;font-size:14px;margin:0 0 4px">
          任务优先 · 知识可信 · 人机协同 · 长期记忆 · AI 原生。<br/>
          让教与学从“结果评价”走向“全过程成长”。
        </p>
        <div class="pm-feature-list">
          <div><el-icon><Aim/></el-icon> 任务驱动的工作台，而非菜单首页</div>
          <div><el-icon><Connection/></el-icon> 知识图谱 + 来源追溯，知识可信</div>
          <div><el-icon><TrendCharts/></el-icon> 全过程成长记录，不只记录分数</div>
        </div>
        <svg viewBox="0 0 420 220" style="margin-top:30px;width:100%;max-width:460px;opacity:.92">
          <defs>
            <linearGradient id="lg" x1="0" y1="0" x2="1" y2="1">
              <stop offset="0" stop-color="#4080ff"/><stop offset="1" stop-color="#36CFC9"/>
            </linearGradient>
          </defs>
          <g stroke="url(#lg)" stroke-width="1.4" opacity=".7">
            <line x1="60" y1="60" x2="200" y2="40"/><line x1="200" y1="40" x2="340" y2="80"/>
            <line x1="60" y1="60" x2="150" y2="160"/><line x1="150" y1="160" x2="300" y2="150"/>
            <line x1="200" y1="40" x2="150" y2="160"/><line x1="340" y1="80" x2="300" y2="150"/>
            <line x1="150" y1="160" x2="300" y2="150"/>
          </g>
          <g fill="#4080ff">
            <circle cx="60" cy="60" r="9"/><circle cx="200" cy="40" r="11" fill="#36CFC9"/>
            <circle cx="340" cy="80" r="9"/><circle cx="150" cy="160" r="12" fill="#722ED1"/>
            <circle cx="300" cy="150" r="9"/>
          </g>
          <g fill="#cfe0ff" font-size="11" font-family="sans-serif">
            <text x="50" y="20">知识图谱</text><text x="190" y="22">RAG</text>
            <text x="330" y="100">AI</text><text x="120" y="190">成长轨迹</text>
          </g>
        </svg>
      </aside>

      <!-- 表单侧 -->
      <section class="pm-login-panel">
        <div class="pm-login-box pm-anim-in">
          <!-- ===== 登录视图 ===== -->
          <template v-if="mode==='login'">
            <div style="margin-bottom:18px">
              <div style="font-size:22px;font-weight:800">欢迎使用 ProgramMind</div>
              <div class="pm-muted" style="font-size:13px;margin-top:4px">请选择身份并登录演示账号</div>
            </div>

            <div class="pm-role-switch">
              <div class="opt" :class="{active: role==='student'}" @click="role='student'">
                <el-icon><User/></el-icon> 学生
              </div>
              <div class="opt" :class="{active: role==='teacher'}" @click="role='teacher'">
                <el-icon><Avatar/></el-icon> 教师
              </div>
            </div>

            <el-form label-position="top">
              <el-form-item label="账号">
                <el-input v-model="form.username" size="large" placeholder="如 student01 / teacher01">
                  <template #prefix><el-icon><User/></el-icon></template>
                </el-input>
              </el-form-item>
              <el-form-item label="密码">
                <el-input v-model="form.password" type="password" size="large" show-password placeholder="演示密码与账号一致">
                  <template #prefix><el-icon><Lock/></el-icon></template>
                </el-input>
              </el-form-item>
              <el-button type="primary" size="large" style="width:100%;height:44px;font-weight:700;font-size:15px"
                         :loading="loading" @click="submit">
                {{ loading ? '登录中…' : '登 录' }}
              </el-button>
            </el-form>

            <div class="pm-card" style="margin-top:18px;padding:14px">
              <div style="font-size:12px;font-weight:700;margin-bottom:8px">一键填充演示账号</div>
              <div style="display:flex;gap:10px">
                <button class="pm-btn-ghost" style="flex:1" @click="fillDemo('student')">学生 student01</button>
                <button class="pm-btn-ghost" style="flex:1" @click="fillDemo('teacher')">教师 teacher01</button>
              </div>
              <div class="pm-faint" style="font-size:11px;margin-top:8px">更多账号：student02~04 / teacher02（密码同账号）</div>
            </div>

            <div style="text-align:center;margin-top:16px;font-size:13px" class="pm-muted">
              还没有账号？
              <a href="javascript:;" style="color:var(--pm-brand);font-weight:700" @click="mode='register'">立即注册 →</a>
            </div>
          </template>

          <!-- ===== 注册视图（真实写入数据库） ===== -->
          <template v-else>
            <div style="margin-bottom:18px">
              <div style="font-size:22px;font-weight:800">创建 ProgramMind 账号</div>
              <div class="pm-muted" style="font-size:13px;margin-top:4px">注册即写入数据库，新学生可立即选课学习</div>
            </div>

            <div class="pm-role-switch">
              <div class="opt" :class="{active: role==='student'}" @click="role='student'">
                <el-icon><User/></el-icon> 学生
              </div>
              <div class="opt" :class="{active: role==='teacher'}" @click="role='teacher'">
                <el-icon><Avatar/></el-icon> 教师
              </div>
            </div>

            <el-form label-position="top">
              <el-form-item label="姓名">
                <el-input v-model="reg.name" size="large" placeholder="你的真实姓名 / 昵称">
                  <template #prefix><el-icon><Edit/></el-icon></template>
                </el-input>
              </el-form-item>
              <el-form-item label="账号">
                <el-input v-model="reg.username" size="large" placeholder="至少 3 个字符，登录时使用">
                  <template #prefix><el-icon><User/></el-icon></template>
                </el-input>
              </el-form-item>
              <el-form-item label="密码">
                <el-input v-model="reg.password" type="password" size="large" show-password placeholder="设置登录密码">
                  <template #prefix><el-icon><Lock/></el-icon></template>
                </el-input>
              </el-form-item>
              <el-form-item label="专业" :required="role==='student'">
                <el-select v-model="reg.major" size="large" placeholder="选择专业，自动匹配课程"
                           style="width:100%" :disabled="role!=='student'">
                  <el-option v-for="m in majors" :key="m" :label="m" :value="m"/>
                </el-select>
              </el-form-item>
              <el-form-item label="学院（选填）">
                <el-input v-model="reg.school" size="large" placeholder="如 计算机科学与技术学院">
                  <template #prefix><el-icon><School/></el-icon></template>
                </el-input>
              </el-form-item>
              <el-alert v-if="role==='student'" type="info" :closable="false" show-icon
                        style="margin-bottom:14px;border-radius:10px"
                        title="选择专业后，系统会自动为你加入该专业核心课程；相关专业拓展课将作为『为你推荐』供你选修。"
                        description="例如：选『软件工程』会直接加入《Python 程序设计》《数据结构》，并推荐《计算机网络》。"/>
              <el-button type="primary" size="large" style="width:100%;height:44px;font-weight:700;font-size:15px"
                         :loading="loading" @click="doRegister">
                {{ loading ? '注册中…' : '注 册 并 登 录' }}
              </el-button>
            </el-form>

            <div style="text-align:center;margin-top:16px;font-size:13px" class="pm-muted">
              已有账号？
              <a href="javascript:;" style="color:var(--pm-brand);font-weight:700" @click="mode='login'">返回登录 →</a>
            </div>
          </template>
        </div>
      </section>
    </div>
    `,
  });
})();
