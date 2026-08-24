```vue
<template>
  <div class="dashboard-page">
    <!-- 页面标题区 -->
    <div class="page-header">
      <div>
        <h1>学习状态仪表盘</h1>
        <p>AI 正在根据你的学习行为实时生成能力画像与成长分析</p>
      </div>

      <el-tag type="success" size="large">
        实时分析中
      </el-tag>
    </div>

    <!-- 顶部指标 -->
    <el-row :gutter="20" class="metrics-row">
      <el-col :span="6">
        <el-card class="metric-card">
          <div class="metric-value">89</div>
          <div class="metric-label">综合能力评分</div>
        </el-card>
      </el-col>

      <el-col :span="6">
        <el-card class="metric-card">
          <div class="metric-value">A</div>
          <div class="metric-label">成长等级</div>
        </el-card>
      </el-col>

      <el-col :span="6">
        <el-card class="metric-card">
          <div class="metric-value">12</div>
          <div class="metric-label">已完成任务</div>
        </el-card>
      </el-col>

      <el-col :span="6">
        <el-card class="metric-card">
          <div class="metric-value">4.5h</div>
          <div class="metric-label">今日学习时长</div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 主体区域 -->
    <el-row :gutter="20">
      <el-col :span="16">
        <el-card class="panel">
          <template #header>
            <div class="panel-title">
              AI 编程能力画像
            </div>
          </template>

          <div
            ref="chartRef"
            class="chart"
          ></div>
        </el-card>
      </el-col>

      <el-col :span="8">
        <el-card class="panel analysis-panel">
          <template #header>
            <div class="panel-title">
              AI 智能分析
            </div>
          </template>

          <div class="ability-list">
            <div class="ability-item">
              <span>算法能力</span>
              <el-progress :percentage="85" />
            </div>

            <div class="ability-item">
              <span>代码能力</span>
              <el-progress :percentage="90" status="success" />
            </div>

            <div class="ability-item">
              <span>AI能力</span>
              <el-progress :percentage="78" status="warning" />
            </div>

            <div class="ability-item">
              <span>工程能力</span>
              <el-progress :percentage="82" />
            </div>

            <div class="ability-item">
              <span>创新能力</span>
              <el-progress :percentage="88" status="success" />
            </div>
          </div>

          <el-alert
            title="AI 建议：优先提升 AI 模型实践能力，可重点完成机器学习项目与深度学习框架训练。"
            type="info"
            :closable="false"
            show-icon
          />
        </el-card>
      </el-col>
    </el-row>

    <!-- 底部洞察 -->
    <el-row :gutter="20" class="insight-row">
      <el-col :span="8">
        <el-card class="panel insight-card">
          <div class="insight-title">学习优势</div>
          <p>代码实现能力和创新能力表现突出，具备较强的问题解决能力。</p>
        </el-card>
      </el-col>

      <el-col :span="8">
        <el-card class="panel insight-card">
          <div class="insight-title">待提升方向</div>
          <p>AI 模型调参与工程化部署能力仍有提升空间。</p>
        </el-card>
      </el-col>

      <el-col :span="8">
        <el-card class="panel insight-card">
          <div class="insight-title">下一阶段目标</div>
          <p>完成深度学习项目实战，并尝试参与 AI 创新竞赛。</p>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import {
  ref,
  onMounted
} from "vue"

import * as echarts from "echarts"

const chartRef = ref(null)

onMounted(() => {
  const chart = echarts.init(chartRef.value)

  const option = {
    tooltip: {},

    radar: {
      radius: "65%",

      indicator: [
        { name: "算法能力", max: 100 },
        { name: "代码能力", max: 100 },
        { name: "AI能力", max: 100 },
        { name: "工程能力", max: 100 },
        { name: "创新能力", max: 100 }
      ],

      splitArea: {
        areaStyle: {
          color: [
            "rgba(37,99,235,0.05)",
            "rgba(37,99,235,0.08)"
          ]
        }
      },

      axisLine: {
        lineStyle: {
          color: "rgba(37,99,235,0.3)"
        }
      }
    },

    series: [
      {
        type: "radar",

        data: [
          {
            value: [85, 90, 78, 82, 88],

            name: "当前能力",

            areaStyle: {
              color: "rgba(37,99,235,0.25)"
            },

            lineStyle: {
              width: 3,
              color: "#2563eb"
            },

            itemStyle: {
              color: "#2563eb"
            }
          }
        ]
      }
    ]
  }

  chart.setOption(option)

  window.addEventListener("resize", () => {
    chart.resize()
  })
})
</script>

<style scoped>
.dashboard-page {
  padding: 24px;
  background: #f5f7fa;
  min-height: 100%;
}

.page-header {
  background: linear-gradient(135deg, #0f172a, #1e3a8a);
  color: white;
  border-radius: 20px;
  padding: 28px 32px;
  margin-bottom: 24px;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.page-header h1 {
  margin: 0 0 8px;
  font-size: 30px;
}

.page-header p {
  margin: 0;
  opacity: 0.9;
}

.metrics-row {
  margin-bottom: 24px;
}

.metric-card {
  text-align: center;
  border-radius: 18px;
  transition: all 0.3s ease;
}

.metric-card:hover {
  transform: translateY(-6px);
}

.metric-value {
  font-size: 32px;
  font-weight: 700;
  color: #2563eb;
  margin-bottom: 8px;
}

.metric-label {
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

.chart {
  width: 100%;
  height: 460px;
}

.analysis-panel {
  height: 100%;
}

.ability-list {
  display: flex;
  flex-direction: column;
  gap: 18px;
  margin-bottom: 24px;
}

.ability-item span {
  display: block;
  margin-bottom: 8px;
  color: #334155;
  font-weight: 500;
}

.insight-row {
  margin-top: 24px;
}

.insight-card {
  height: 100%;
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
