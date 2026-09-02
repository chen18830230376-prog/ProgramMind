<template>

  <div class="login-page">

    <div class="login-box">

      <!-- 系统名称 -->
      <h1 class="title">
        ProgramMind
      </h1>


      <!-- 系统介绍 -->
      <p class="subtitle">
        AI驱动的编程学习成长系统
      </p>


      <!-- 登录表单 -->
      <el-form
        :model="form"
        @submit.prevent="handleLogin"
      >

        <!-- 用户名 -->
        <el-form-item>

          <el-input
            v-model="form.username"
            placeholder="请输入学号 / 用户名"
            size="large"
            clearable
          />

        </el-form-item>


        <!-- 密码 -->
        <el-form-item>

          <el-input
            v-model="form.password"
            type="password"
            placeholder="请输入密码"
            size="large"
            show-password
            clearable
            @keyup.enter="handleLogin"
          />

        </el-form-item>


        <!-- 登录按钮 -->
        <el-form-item>

          <el-button
            type="primary"
            size="large"
            class="login-btn"
            :loading="loading"
            @click="handleLogin"
          >

            {{ loading ? "登录中..." : "登录系统" }}

          </el-button>

        </el-form-item>

      </el-form>


      <!-- 测试账号 -->
      <div class="tips">

        <p>
          测试账号：student
        </p>

        <p>
          测试密码：123456
        </p>

      </div>

    </div>

  </div>

</template>


<script setup>

import {
  reactive,
  ref
} from "vue"


import {
  useRouter
} from "vue-router"


import {
  ElMessage
} from "element-plus"


import {
  useUserStore
} from "../../stores/user"


const router = useRouter()


const userStore = useUserStore()


// 登录按钮状态
const loading = ref(false)


// 登录表单
const form = reactive({

  username: "",

  password: ""

})


// =============================
// 登录
// =============================

const handleLogin = async () => {

  // 防止重复点击
  if (loading.value) {

    return

  }


  // 检查用户名
  if (!form.username.trim()) {

    ElMessage.warning(
      "请输入用户名"
    )

    return

  }


  // 检查密码
  if (!form.password) {

    ElMessage.warning(
      "请输入密码"
    )

    return

  }


  loading.value = true


  try {

    /*
     * 当前阶段：
     * 使用前端测试账号完成登录流程。
     *
     * 后续拿到后端真实登录接口以后，
     * 再把这里替换成 API 调用。
     */


    if (
      form.username !== "student" ||
      form.password !== "123456"
    ) {

      ElMessage.error(
        "用户名或密码错误"
      )

      return

    }


    // 模拟 Token
    const token =
      "programmind-demo-token"


    // 保存用户信息 + Token
    userStore.login(

      {
        username: form.username,

        name: "学生用户",

        avatar: ""

      },

      token

    )


    ElMessage.success(
      "登录成功"
    )


    // 跳转首页
    await router.push(
      "/workspace"
    )


  } catch (error) {

    console.error(
      "登录失败：",
      error
    )


    ElMessage.error(
      "登录失败，请稍后重试"
    )


  } finally {

    loading.value = false

  }

}

</script>


<style scoped>

.login-page {

  width: 100%;

  height: 100vh;

  display: flex;

  justify-content: center;

  align-items: center;

  background:
    linear-gradient(
      135deg,
      #0f172a,
      #1e3a8a,
      #2563eb
    );

}


.login-box {

  width: 420px;

  padding: 40px;

  border-radius: 20px;

  background:
    rgba(
      255,
      255,
      255,
      0.96
    );

  box-shadow:
    0 12px 40px
    rgba(
      0,
      0,
      0,
      0.2
    );

}


.title {

  text-align: center;

  font-size: 34px;

  font-weight: bold;

  color: #2563eb;

  margin-bottom: 10px;

}


.subtitle {

  text-align: center;

  color: #64748b;

  margin-bottom: 30px;

}


.login-btn {

  width: 100%;

}


.tips {

  margin-top: 20px;

  text-align: center;

  color: #64748b;

  font-size: 13px;

}


.tips p {

  margin: 6px 0;

}

</style>