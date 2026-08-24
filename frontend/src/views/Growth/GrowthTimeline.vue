```vue
<template>
  <div class="growth-page">
    <!-- 顶部标题区 -->
    <div class="page-header">
      <div>
        <h1>AI 成长轨迹分析</h1>
        <p>
          系统持续记录学习行为、项目实践与能力变化，
          自动生成个人成长趋势与阶段性分析结果。
        </p>
      </div>

      <el-tag type="success" size="large">
        成长数据持续更新
      </el-tag>
    </div>

    <!-- 顶部统计卡片 -->
    <el-row :gutter="20" class="stats-row">
      <el-col :span="6">
        <el-card class="stat-card">
          <div class="stat-value">92</div>
          <div class="stat-label">当前成长指数</div>
        </el-card>
      </el-col>

      <el-col :span="6">
        <el-card class="stat-card">
          <div class="stat-value">+32%</div>
          <div class="stat-label">近三个月提升</div>
        </el-card>
      </el-col>

      <el-col :span="6">
        <el-card class="stat-card">
          <div class="stat-value">4</div>
          <div class="stat-label">已完成成长阶段</div>
        </el-card>
      </el-col>

      <el-col :span="6">
        <el-card class="stat-card">
          <div class="stat-value">A</div>
          <div class="stat-label">AI 评估等级</div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 主体区域 -->
    <el-row :gutter="20">
      <el-col :span="16">
        <el-card class="panel">
          <template #header>
            <div class="panel-title">
              能力成长趋势
            </div>
          </template>

          <div
            ref="chartRef"
            class="chart"
          ></div>
        </el-card>
      </el-col>

      <el-col :span="8">
        <el-card class="panel summary-panel">
          <template #header>
            <div class="panel-title">
              AI 成长总结
            </div>
          </template>

          <div class="summary-item">
            <div class="summary-title">最明显提升</div>
            <div class="summary-content">
              算法设计与工程实践能力提升显著
            </div>
          </div>

          <div class="summary-item">
            <div class="summary-title">当前阶段</div>
            <el-tag type="primary">AI 应用开发阶段</el-tag>
          </div>

          <div class="summary-item">
            <div class="summary-title">下一阶段目标</div>
            <div class="summary-content">
              深度学习项目实战与 AI 工程化部署
            </div>
          </div>

          <el-alert
            title="AI 判断：你已经具备较完整的编程基础，建议开始参与中大型 AI 项目实践。"
            type="success"
            :closable="false"
            show-icon
          />
        </el-card>
      </el-col>
    </el-row>

    <!-- 成长时间轴 -->
    <el-card class="panel timeline-panel">
      <template #header>
        <div class="panel-title">
          学习阶段记录
        </div>
      </template>

      <el-timeline>
        <el-timeline-item
          timestamp="2026-01"
          type="primary"
          placement="top"
        >
          <div class="timeline-card">
            <div class="timeline-title">
              Python 基础学习完成
            </div>
            <p>
              掌握 Python 语法、函数、面向对象编程与基础算法实现。
            </p>
          </div>
        </el-timeline-item>

        <el-timeline-item
          timestamp="2026-02"
          type="success"
          placement="top"
        >
          <div class="timeline-card">
            <div class="timeline-title">
              数据结构与算法强化
            </div>
            <p>
              完成数组、链表、树、图以及动态规划等核心算法训练。
            </p>
          </div>
        </el-timeline-item>

        <el-timeline-item
          timestamp="2026-03"
          type="warning"
          placement="top"
        >
          <div class="timeline-card">
            <div class="timeline-title">
              机器学习项目实践
            </div>
            <p>
              完成推荐系统与分类模型项目，开始接触真实数据分析流程。
            </p>
          </div>
        </el-timeline-item>

        <el-timeline-item
          timestamp="2026-04"
          type="danger"
          placement="top"
        >
          <div class="timeline-card">
            <div class="timeline-title">
              AI 应用开发阶段
            </div>
            <p>
              开始构建 AI 学习成长系统，并尝试前后端协同与可视化分析。
            </p>
          </div>
        </el-timeline-item>
      </el-timeline>
    </el-card>

    <!-- 底部能力洞察 -->
    <el-row :gutter="20" class="bottom-row">
      <el-col :span="8">
        <el-card class="insight-card">
          <div class="insight-title">学习稳定性</div>
          <p>近四个月学习投入保持稳定，成长曲线呈持续上升趋势。</p>
        </el-card>
      </el-col>

      <el-col :span="8">
        <el-card class="insight-card">
          <div class="insight-title">项目实践能力</div>
          <p>已具备从算法学习过渡到 AI 项目实践的能力基础。</p>
        </el-card>
      </el-col>

      <el-col :span="8">
        <el-card class="insight-card">
          <div class="insight-title">未来发展建议</div>
          <p>建议继续强化工程化部署与团队协作能力，为真实项目开发做准备。</p>
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
    tooltip: {
      trigger: "axis"
    },

    xAxis: {
      type: "category",

      data: [
        "1月",
        "2月",
        "3月",
        "4月"
      ],

      axisLine: {
        lineStyle: {
          color: "#cbd5e1"
        }
      }
    },

    yAxis: {
      type: "value",

      max: 100,

      axisLine: {
        show: false
      },

      splitLine: {
        lineStyle: {
          color: "#e2e8f0"
        }
      }
    },

    series: [
      {
        name: "成长指数",

        type: "line",

        smooth: true,

        data: [60, 72, 85, 92],

        symbol: "circle",

        symbolSize: 10,

        lineStyle: {
          width: 4,
          color: "#2563eb"
        },

        itemStyle: {
          color: "#2563eb"
        },

        areaStyle: {
          color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
            {
              offset: 0,
              color: "rgba(37,99,235,0.35)"
            },
            {
              offset: 1,
              color: "rgba(37,99,235,0.05)"
            }
          ])
        }
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
.growth-page {
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

.chart {
  width: 100%;
  height: 420px;
}

.summary-panel {
  height: 100%;
}

.summary-item {
  margin-bottom: 24px;
}

.summary-title {
  font-size: 15px;
  font-weight: 600;
  color: #1e3a8a;
  margin-bottom: 10px;
}

.summary-content {
  color: #475569;
  line-height: 1.7;
}

.timeline-panel {
  margin-top: 24px;
}

.timeline-card {
  background: #f8fafc;
  border-radius: 14px;
  padding: 16px;
  border-left: 4px solid #2563eb;
}

.timeline-title {
  font-size: 16px;
  font-weight: 600;
  color: #0f172a;
  margin-bottom: 8px;
}

.timeline-card p {
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
