## `Navigation.vue`

```vue
<template>
  <div class="navigation-page">
    <!-- 顶部标题区 -->
    <div class="page-header">
      <div>
        <h1>AI 智能学习导航中心</h1>
        <p>
          系统正在结合知识掌握情况、能力画像与成长轨迹，
          为你动态生成下一阶段的最优学习路线。
        </p>
      </div>

      <el-tag type="success" size="large">
        AI 推荐已生成
      </el-tag>
    </div>

    <!-- 顶部推荐指标 -->
    <el-row :gutter="20" class="stats-row">
      <el-col :span="6">
        <el-card class="stat-card">
          <div class="stat-value">95%</div>
          <div class="stat-label">算法强化优先级</div>
        </el-card>
      </el-col>

      <el-col :span="6">
        <el-card class="stat-card">
          <div class="stat-value">88%</div>
          <div class="stat-label">AI 项目实践匹配度</div>
        </el-card>
      </el-col>

      <el-col :span="6">
        <el-card class="stat-card">
          <div class="stat-value">3</div>
          <div class="stat-label">推荐核心任务</div>
        </el-card>
      </el-col>

      <el-col :span="6">
        <el-card class="stat-card">
          <div class="stat-value">A</div>
          <div class="stat-label">成长路径评级</div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 主体区域 -->
    <el-row :gutter="20">
      <el-col :span="16">
        <el-card class="panel route-panel">
          <template #header>
            <div class="panel-title">
              AI 推荐成长路线
            </div>
          </template>

          <div class="route-flow">
            <div class="route-step active">
              <div class="step-badge">1</div>
              <div class="step-content">
                <h3>动态规划专项强化</h3>
                <p>优先提升复杂问题建模与状态转移分析能力。</p>
                <el-progress :percentage="95" status="success" />
              </div>
            </div>

            <div class="route-arrow">↓</div>

            <div class="route-step">
              <div class="step-badge">2</div>
              <div class="step-content">
                <h3>机器学习项目实践</h3>
                <p>完成推荐系统与分类模型项目，强化 AI 实战能力。</p>
                <el-progress :percentage="88" />
              </div>
            </div>

            <div class="route-arrow">↓</div>

            <div class="route-step">
              <div class="step-badge">3</div>
              <div class="step-content">
                <h3>AI 工程化开发</h3>
                <p>学习前后端协同、模型部署与数据可视化集成。</p>
                <el-progress :percentage="82" />
              </div>
            </div>
          </div>
        </el-card>
      </el-col>

      <el-col :span="8">
        <el-card class="panel task-panel">
          <template #header>
            <div class="panel-title">
              当前推荐任务
            </div>
          </template>

          <div class="task-list">
            <div class="task-item high">
              <div class="task-tag">高优先级</div>
              <div class="task-name">动态规划专题训练</div>
            </div>

            <div class="task-item medium">
              <div class="task-tag">中优先级</div>
              <div class="task-name">推荐系统 Demo 开发</div>
            </div>

            <div class="task-item low">
              <div class="task-tag">长期目标</div>
              <div class="task-name">AI 模型部署实践</div>
            </div>
          </div>

          <el-divider />

          <div class="focus-section">
            <div class="focus-title">本周重点方向</div>
            <el-tag type="primary">算法设计</el-tag>
            <el-tag type="success">项目实践</el-tag>
            <el-tag type="warning">工程能力</el-tag>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- AI 推荐理由 -->
    <el-card class="panel reason-panel">
      <template #header>
        <div class="panel-title">
          AI 推荐理由分析
        </div>
      </template>

      <el-row :gutter="20">
        <el-col :span="8">
          <div class="reason-item">
            <div class="reason-title">知识掌握分析</div>
            <p>
              编程基础与数据结构掌握度较高，
              当前瓶颈主要集中在高级算法设计能力。
            </p>
          </div>
        </el-col>

        <el-col :span="8">
          <div class="reason-item">
            <div class="reason-title">能力画像匹配</div>
            <p>
              代码能力与工程能力具备较好基础，
              适合开始中等复杂度 AI 项目开发实践。
            </p>
          </div>
        </el-col>

        <el-col :span="8">
          <div class="reason-item">
            <div class="reason-title">成长趋势预测</div>
            <p>
              按照当前学习投入与成长速度，
              预计 2-3 周后可进入深度学习项目阶段。
            </p>
          </div>
        </el-col>
      </el-row>
    </el-card>

    <!-- 底部智能建议 -->
    <el-row :gutter="20" class="bottom-row">
      <el-col :span="8">
        <el-card class="insight-card">
          <div class="insight-title">推荐学习时长</div>
          <p>建议每天投入 2-3 小时进行算法训练，并保持持续项目实践。</p>
        </el-card>
      </el-col>

      <el-col :span="8">
        <el-card class="insight-card">
          <div class="insight-title">推荐学习资源</div>
          <p>优先学习动态规划、图论算法以及机器学习工程化相关课程内容。</p>
        </el-card>
      </el-col>

      <el-col :span="8">
        <el-card class="insight-card">
          <div class="insight-title">阶段性目标</div>
          <p>完成推荐系统项目后，建议尝试参与 AI 创新竞赛与团队协作开发。</p>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
// AI 导航展示页无需额外逻辑
</script>

<style scoped>
.navigation-page {
  padding: 24px;
  background: #f5f7fa;
  min-height: 100%;
}

.page-header {
  background: linear-gradient(135deg, #0f172a, #2563eb);
  color: white;
  border-radius: 20px;
  padding: 28px 32px;
  margin-bottom: 24px;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.page-header h1 {
  margin: 0 0 10px;
  font-size: 30px;
}

.page-header p {
  margin: 0;
  line-height: 1.7;
  opacity: 0.92;
}

.stats-row {
  margin-bottom: 24px;
}

.stat-card {
  text-align: center;
  border-radius: 18px;
  transition: all 0.3s ease;
}

.stat-card:hover {
  transform: translateY(-6px);
}

.stat-value {
  font-size: 32px;
  font-weight: 700;
  color: #2563eb;
  margin-bottom: 8px;
}

.stat-label {
  color: #64748b;
  font-size: 14px;
}

.panel {
  border-radius: 18px;
  border: none;
  box-shadow: 0 6px 24px rgba(15, 23, 42, 0.06);
}

.panel-title {
  font-size: 18px;
  font-weight: 600;
  color: #0f172a;
}

.route-panel {
  height: 100%;
}

.route-flow {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.route-step {
  display: flex;
  gap: 16px;
  padding: 20px;
  border-radius: 16px;
  background: #f8fafc;
  border: 1px solid #e2e8f0;
}

.route-step.active {
  border-color: #2563eb;
  background: #eff6ff;
}

.step-badge {
  width: 36px;
  height: 36px;
  border-radius: 50%;
  background: #2563eb;
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 700;
  flex-shrink: 0;
}

.step-content h3 {
  margin: 0 0 8px;
  color: #0f172a;
}

.step-content p {
  margin: 0 0 12px;
  color: #475569;
  line-height: 1.6;
}

.route-arrow {
  text-align: center;
  font-size: 24px;
  color: #94a3b8;
}

.task-panel {
  height: 100%;
}

.task-list {
  display: flex;
  flex-direction: column;
  gap: 14px;
}

.task-item {
  padding: 14px;
  border-radius: 14px;
  border-left: 4px solid #2563eb;
  background: #f8fafc;
}

.task-item.high {
  border-left-color: #ef4444;
}

.task-item.medium {
  border-left-color: #f59e0b;
}

.task-item.low {
  border-left-color: #10b981;
}

.task-tag {
  font-size: 12px;
  font-weight: 600;
  margin-bottom: 6px;
  color: #475569;
}

.task-name {
  color: #0f172a;
  font-weight: 500;
}

.focus-section {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.focus-title {
  font-weight: 600;
  color: #1e3a8a;
}

.reason-panel {
  margin-top: 24px;
}

.reason-item {
  padding: 18px;
  border-radius: 16px;
  background: #f8fafc;
  height: 100%;
}

.reason-title {
  font-size: 16px;
  font-weight: 600;
  color: #1e3a8a;
  margin-bottom: 10px;
}

.reason-item p {
  margin: 0;
  color: #475569;
  line-height: 1.7;
}

.bottom-row {
  margin-top: 24px;
}

.insight-card {
  height: 100%;
  border-radius: 18px;
  transition: all 0.3s ease;
}

.insight-card:hover {
  transform: translateY(-4px);
}

.insight-title {
  font-size: 16px;
  font-weight: 600;
  color: #1e3a8a;
  margin-bottom: 10px;
}

.insight-card p {
  margin: 0;
  color: #475569;
  line-height: 1.7;
}
</style>
```
