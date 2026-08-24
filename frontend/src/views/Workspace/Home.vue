```vue
<template>
  <div class="home-page">
    <!-- 顶部欢迎区域 -->
    <div class="hero">
      <div>
        <h1>ProgramMind AI 学习成长平台</h1>
        <p>
          基于 AI 的编程能力分析、知识图谱构建与个性化成长导航系统
        </p>
      </div>

      <el-tag type="success" size="large">
        AI 智能分析已启动
      </el-tag>
    </div>

    <!-- 数据概览 -->
    <el-row :gutter="20" class="stats-row">
      <el-col :span="6">
        <el-card class="stat-card">
          <div class="stat-value">4.5h</div>
          <div class="stat-label">今日学习时长</div>
        </el-card>
      </el-col>

      <el-col :span="6">
        <el-card class="stat-card">
          <div class="stat-value">12</div>
          <div class="stat-label">完成学习任务</div>
        </el-card>
      </el-col>

      <el-col :span="6">
        <el-card class="stat-card">
          <div class="stat-value">89</div>
          <div class="stat-label">AI 综合评分</div>
        </el-card>
      </el-col>

      <el-col :span="6">
        <el-card class="stat-card">
          <div class="stat-value">A</div>
          <div class="stat-label">成长等级</div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 中间区域 -->
    <el-row :gutter="20">
      <el-col :span="16">
        <el-card class="panel">
          <template #header>
            <div class="panel-title">本周成长趋势</div>
          </template>

          <div class="trend-chart">
            <div class="trend-item">
              <span>周一</span>
              <el-progress :percentage="55" />
            </div>

            <div class="trend-item">
              <span>周二</span>
              <el-progress :percentage="68" />
            </div>

            <div class="trend-item">
              <span>周三</span>
              <el-progress :percentage="74" />
            </div>

            <div class="trend-item">
              <span>周四</span>
              <el-progress :percentage="83" />
            </div>

            <div class="trend-item">
              <span>周五</span>
              <el-progress :percentage="91" status="success" />
            </div>
          </div>
        </el-card>
      </el-col>

      <el-col :span="8">
        <el-card class="panel ai-card">
          <template #header>
            <div class="panel-title">AI 今日建议</div>
          </template>

          <el-alert
            title="建议优先完成动态规划专项训练"
            type="info"
            :closable="false"
            show-icon
          />

          <div class="task-list">
            <div class="task-item">
              <el-tag type="primary">算法</el-tag>
              <span>动态规划练习</span>
            </div>

            <div class="task-item">
              <el-tag type="success">项目</el-tag>
              <span>完成推荐系统 Demo</span>
            </div>

            <div class="task-item">
              <el-tag type="warning">AI</el-tag>
              <span>学习模型评估方法</span>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 底部快速入口 -->
    <el-card class="panel quick-panel">
      <template #header>
        <div class="panel-title">快速功能入口</div>
      </template>

      <el-row :gutter="16">
        <el-col :span="6">
          <div class="quick-item">
            <div class="quick-title">知识地图</div>
            <div class="quick-desc">查看 AI 知识图谱</div>
          </div>
        </el-col>

        <el-col :span="6">
          <div class="quick-item">
            <div class="quick-title">状态仪表盘</div>
            <div class="quick-desc">分析能力画像</div>
          </div>
        </el-col>

        <el-col :span="6">
          <div class="quick-item">
            <div class="quick-title">成长轨迹</div>
            <div class="quick-desc">查看成长趋势</div>
          </div>
        </el-col>

        <el-col :span="6">
          <div class="quick-item">
            <div class="quick-title">成长报告</div>
            <div class="quick-desc">生成 AI 学习报告</div>
          </div>
        </el-col>
      </el-row>
    </el-card>
  </div>
</template>

<script setup>
// 首页展示无需额外逻辑
</script>

<style scoped>
.home-page {
  padding: 24px;
  background: #f5f7fa;
  min-height: 100%;
}

.hero {
  background: linear-gradient(135deg, #1e3a8a, #2563eb);
  color: white;
  border-radius: 20px;
  padding: 32px;
  margin-bottom: 24px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  box-shadow: 0 10px 30px rgba(37, 99, 235, 0.2);
}

.hero h1 {
  font-size: 34px;
  margin-bottom: 10px;
}

.hero p {
  opacity: 0.92;
  line-height: 1.7;
}

.stats-row {
  margin-bottom: 24px;
}

.stat-card {
  text-align: center;
  border-radius: 16px;
  transition: all 0.3s ease;
}

.stat-card:hover {
  transform: translateY(-6px);
}

.stat-value {
  font-size: 34px;
  font-weight: bold;
  color: #2563eb;
  margin-bottom: 8px;
}

.stat-label {
  color: #64748b;
}

.panel {
  border-radius: 18px;
  margin-bottom: 24px;
}

.panel-title {
  font-size: 18px;
  font-weight: 600;
  color: #0f172a;
}

.trend-chart {
  display: flex;
  flex-direction: column;
  gap: 18px;
}

.trend-item {
  display: flex;
  align-items: center;
  gap: 16px;
}

.trend-item span {
  width: 48px;
  color: #475569;
}

.ai-card {
  height: 100%;
}

.task-list {
  margin-top: 20px;
  display: flex;
  flex-direction: column;
  gap: 14px;
}

.task-item {
  display: flex;
  align-items: center;
  gap: 12px;
  color: #334155;
}

.quick-panel {
  margin-bottom: 0;
}

.quick-item {
  background: #eff6ff;
  border-radius: 14px;
  padding: 18px;
  text-align: center;
  transition: all 0.25s ease;
  cursor: pointer;
}

.quick-item:hover {
  background: #dbeafe;
  transform: translateY(-4px);
}

.quick-title {
  font-weight: 600;
  color: #1e3a8a;
  margin-bottom: 8px;
}

.quick-desc {
  font-size: 13px;
  color: #64748b;
}
</style>
```
