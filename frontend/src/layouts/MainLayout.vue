```vue
<template>
  <el-container class="layout">
    <!-- 左侧导航 -->
    <el-aside width="240px" class="aside">
      <div class="logo">
        <div class="logo-icon">🧠</div>
        <div>
          <div class="logo-title">ProgramMind</div>
          <div class="logo-subtitle">AI Growth System</div>
        </div>
      </div>

      <el-menu
        router
        default-active="/app/workspace"
        class="menu"
        background-color="#0f172a"
        text-color="#cbd5e1"
        active-text-color="#60a5fa"
      >
        <el-menu-item index="/app/workspace">
          <el-icon><House /></el-icon>
          <span>工作台</span>
        </el-menu-item>

        <el-menu-item index="/app/knowledge">
          <el-icon><Share /></el-icon>
          <span>知识地图</span>
        </el-menu-item>

        <el-menu-item index="/app/dashboard">
          <el-icon><DataAnalysis /></el-icon>
          <span>状态仪表盘</span>
        </el-menu-item>

        <el-menu-item index="/app/growth">
          <el-icon><TrendCharts /></el-icon>
          <span>成长轨迹</span>
        </el-menu-item>

        <el-menu-item index="/app/navigation">
          <el-icon><Guide /></el-icon>
          <span>导航建议</span>
        </el-menu-item>

        <el-menu-item index="/app/report">
          <el-icon><Document /></el-icon>
          <span>成长报告</span>
        </el-menu-item>
      </el-menu>
    </el-aside>

    <!-- 主区域 -->
    <el-container>
      <el-header class="header">
        <div class="header-left">
          <h2>AI 编程学习成长平台</h2>
        </div>

        <div class="header-right">
          <el-tag type="success">系统在线</el-tag>

          <el-dropdown>
            <span class="user-info">
              👩 韩静怡
              <el-icon class="el-icon--right">
                <ArrowDown />
              </el-icon>
            </span>

            <template #dropdown>
              <el-dropdown-menu>
                <el-dropdown-item>个人中心</el-dropdown-item>
                <el-dropdown-item divided @click="handleLogout">
                  退出登录
                </el-dropdown-item>
              </el-dropdown-menu>
            </template>
          </el-dropdown>
        </div>
      </el-header>

      <el-main class="main">
        <router-view v-slot="{ Component }">
          <transition name="fade-slide" mode="out-in">
            <component :is="Component" />
          </transition>
        </router-view>
      </el-main>
    </el-container>
  </el-container>
</template>

<script setup>
import {
  ArrowDown,
  House,
  Share,
  DataAnalysis,
  TrendCharts,
  Guide,
  Document
} from "@element-plus/icons-vue"

import { useRouter } from "vue-router"
import { ElMessageBox, ElMessage } from "element-plus"

const router = useRouter()

const handleLogout = async () => {
  try {
    await ElMessageBox.confirm(
      "确认退出当前系统？",
      "退出登录",
      {
        confirmButtonText: "确认",
        cancelButtonText: "取消",
        type: "warning"
      }
    )

    ElMessage.success("已退出登录")
    router.push("/login")
  } catch {
    // 用户取消
  }
}
</script>

<style scoped>
.layout {
  width: 100%;
  height: 100vh;
  overflow: hidden;
}

.aside {
  background: linear-gradient(180deg, #0f172a 0%, #111827 100%);
  border-right: 1px solid rgba(255,255,255,0.06);
}

.logo {
  height: 72px;
  display: flex;
  align-items: center;
  gap: 14px;
  padding: 0 20px;
  border-bottom: 1px solid rgba(255,255,255,0.08);
}

.logo-icon {
  width: 42px;
  height: 42px;
  border-radius: 12px;
  background: rgba(96,165,250,0.15);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 22px;
}

.logo-title {
  color: #ffffff;
  font-size: 18px;
  font-weight: 700;
}

.logo-subtitle {
  color: #94a3b8;
  font-size: 12px;
}

.menu {
  border-right: none;
  padding-top: 12px;
}

.menu :deep(.el-menu-item) {
  height: 48px;
  margin: 6px 12px;
  border-radius: 12px;
}

.menu :deep(.el-menu-item.is-active) {
  background: rgba(96,165,250,0.15) !important;
}

.header {
  background: rgba(255,255,255,0.92);
  backdrop-filter: blur(10px);
  border-bottom: 1px solid #e5e7eb;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 24px;
}

.header-left h2 {
  margin: 0;
  font-size: 20px;
  color: #0f172a;
}

.header-right {
  display: flex;
  align-items: center;
  gap: 16px;
}

.user-info {
  display: flex;
  align-items: center;
  cursor: pointer;
  color: #334155;
  font-weight: 500;
}

.main {
  background: #f5f7fa;
  overflow: auto;
}

.fade-slide-enter-active,
.fade-slide-leave-active {
  transition: all 0.25s ease;
}

.fade-slide-enter-from {
  opacity: 0;
  transform: translateY(8px);
}

.fade-slide-leave-to {
  opacity: 0;
  transform: translateY(-8px);
}
</style>
```
