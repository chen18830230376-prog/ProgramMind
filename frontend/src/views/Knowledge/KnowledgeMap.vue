```vue
<template>
  <div class="knowledge-page">
    <!-- 顶部说明区 -->
    <div class="page-header">
      <div>
        <h1>AI 编程知识图谱</h1>
        <p>
          系统已根据学习数据自动构建编程能力知识体系，
          帮助你发现当前阶段的核心知识节点与推荐学习路径。
        </p>
      </div>

      <el-tag type="success" size="large">
        知识图谱已生成
      </el-tag>
    </div>

    <!-- 主体区域 -->
    <el-row :gutter="20">
      <el-col :span="16">
        <el-card class="panel">
          <template #header>
            <div class="panel-title">
              编程能力知识体系
            </div>
          </template>

          <div
            ref="chartRef"
            class="chart"
          ></div>
        </el-card>
      </el-col>

      <el-col :span="8">
        <el-card class="panel info-panel">
          <template #header>
            <div class="panel-title">
              AI 学习导航
            </div>
          </template>

          <div class="info-section">
            <div class="section-title">当前阶段</div>
            <el-tag type="primary">算法强化阶段</el-tag>
          </div>

          <div class="info-section">
            <div class="section-title">推荐学习路径</div>

            <el-steps direction="vertical" :active="2">
              <el-step title="编程基础" />
              <el-step title="数据结构与算法" />
              <el-step title="机器学习项目" />
              <el-step title="AI 工程实践" />
            </el-steps>
          </div>

          <div class="info-section">
            <div class="section-title">下一学习目标</div>

            <el-alert
              title="建议优先完成动态规划与图论专项训练，并开始机器学习项目实践。"
              type="info"
              :closable="false"
              show-icon
            />
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 底部说明卡片 -->
    <el-row :gutter="20" class="bottom-row">
      <el-col :span="8">
        <el-card class="feature-card">
          <div class="feature-title">知识关联分析</div>
          <p>AI 自动分析知识节点之间的依赖关系，帮助理解学习顺序。</p>
        </el-card>
      </el-col>

      <el-col :span="8">
        <el-card class="feature-card">
          <div class="feature-title">薄弱环节定位</div>
          <p>系统可根据学习记录识别薄弱知识点并生成强化建议。</p>
        </el-card>
      </el-col>

      <el-col :span="8">
        <el-card class="feature-card">
          <div class="feature-title">成长路径规划</div>
          <p>结合能力画像与目标岗位，动态调整推荐学习路线。</p>
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

    series: [
      {
        type: "graph",

        layout: "none",

        roam: true,

        draggable: true,

        label: {
          show: true,
          color: "#0f172a",
          fontWeight: "bold"
        },

        edgeSymbol: ["none", "arrow"],

        edgeSymbolSize: 8,

        lineStyle: {
          color: "#94a3b8",
          width: 2,
          curveness: 0.1
        },

        data: [
          {
            name: "编程基础",
            x: 320,
            y: 60,
            symbolSize: 90,
            itemStyle: {
              color: "#2563eb"
            }
          },

          {
            name: "数据结构",
            x: 320,
            y: 190,
            symbolSize: 82,
            itemStyle: {
              color: "#1d4ed8"
            }
          },

          {
            name: "算法设计",
            x: 320,
            y: 340,
            symbolSize: 92,
            itemStyle: {
              color: "#1e40af"
            }
          },

          {
            name: "机器学习",
            x: 150,
            y: 510,
            symbolSize: 80,
            itemStyle: {
              color: "#0ea5e9"
            }
          },

          {
            name: "工程实践",
            x: 500,
            y: 510,
            symbolSize: 80,
            itemStyle: {
              color: "#0284c7"
            }
          },

          {
            name: "深度学习",
            x: 320,
            y: 650,
            symbolSize: 88,
            itemStyle: {
              color: "#7c3aed"
            }
          }
        ],

        links: [
          { source: "编程基础", target: "数据结构" },
          { source: "数据结构", target: "算法设计" },
          { source: "算法设计", target: "机器学习" },
          { source: "算法设计", target: "工程实践" },
          { source: "机器学习", target: "深度学习" },
          { source: "工程实践", target: "深度学习" }
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
.knowledge-page {
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
  height: 720px;
}

.info-panel {
  height: 100%;
}

.info-section {
  margin-bottom: 28px;
}

.section-title {
  font-size: 15px;
  font-weight: 600;
  color: #1e3a8a;
  margin-bottom: 12px;
}

.bottom-row {
  margin-top: 24px;
}

.feature-card {
  height: 100%;
  border-radius: 18px;
  transition: all 0.3s ease;
}

.feature-card:hover {
  transform: translateY(-4px);
}

.feature-title {
  font-size: 16px;
  font-weight: 600;
  color: #0f172a;
  margin-bottom: 10px;
}

.feature-card p {
  margin: 0;
  color: #475569;
  line-height: 1.7;
}
</style>
```
