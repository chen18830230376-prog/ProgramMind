<template>

<div class="login-page">

  <div class="login-box">

    <h1 class="title">
      ProgramMind
    </h1>

    <p class="subtitle">
      AI驱动的编程学习成长系统
    </p>



    <el-form
      :model="form"
      @submit.prevent="handleLogin"
    >



      <el-form-item>

        <el-input
          v-model="form.username"
          placeholder="请输入学号 / 用户名"
          size="large"
        />

      </el-form-item>



      <el-form-item>

        <el-input
          v-model="form.password"
          type="password"
          placeholder="请输入密码"
          size="large"
          show-password
        />

      </el-form-item>



      <el-form-item>

        <el-button
          type="primary"
          size="large"
          class="login-btn"
          @click="handleLogin"
        >
          登录系统
        </el-button>

      </el-form-item>



    </el-form>



    <div class="tips">

      <p>测试账号：student</p>

      <p>测试密码：123456</p>

    </div>

  </div>

</div>

</template>



<script setup>

import {
  reactive
} from "vue"

import {
  useRouter
} from "vue-router"

import {
  ElMessage
} from "element-plus"



const router = useRouter()



const form = reactive({

  username: "",

  password: ""

})



const handleLogin = () => {

  if (!form.username || !form.password) {

    ElMessage.warning("请输入用户名和密码")

    return

  }



  ElMessage.success("登录成功")



  router.push("/app/workspace")

}

</script>



<style scoped>

.login-page {
  width: 100%;
  height: 100vh;
  display: flex;
  justify-content: center;
  align-items: center;
  background: linear-gradient(135deg, #0f172a, #1e3a8a, #2563eb);
}

.login-box {
  width: 420px;
  padding: 40px;
  border-radius: 20px;
  background: rgba(255, 255, 255, 0.96);
  box-shadow: 0 12px 40px rgba(0, 0, 0, 0.2);
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
</style>