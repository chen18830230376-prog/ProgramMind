<template>
  <div class="report-page">

    <!-- 顶部标题 -->
    <div class="page-header">
      <div>
        <div class="eyebrow">AI LEARNING INSIGHT</div>

        <h1>AI个人成长报告</h1>

        <p>
          基于知识掌握、学习状态与成长轨迹生成的阶段性能力分析
        </p>
      </div>

      <div class="report-status">
        <span class="status-dot"></span>
        AI分析完成
      </div>
    </div>


    <!-- 核心数据 -->
    <div class="overview-grid">

      <div class="overview-card">
        <div class="card-label">综合能力</div>

        <div class="big-number">
          86
          <span>/100</span>
        </div>

        <div class="progress">
          <div
            class="progress-inner"
            style="width:86%"
          ></div>
        </div>

        <div class="card-tip">
          较上阶段提升 12%
        </div>
      </div>


      <div class="overview-card">
        <div class="card-label">知识掌握度</div>

        <div class="big-number">
          82
          <span>%</span>
        </div>

        <div class="progress">
          <div
            class="progress-inner"
            style="width:82%"
          ></div>
        </div>

        <div class="card-tip">
          已掌握核心知识节点
        </div>
      </div>


      <div class="overview-card">
        <div class="card-label">学习活跃度</div>

        <div class="big-number">
          91
          <span>%</span>
        </div>

        <div class="progress">
          <div
            class="progress-inner"
            style="width:91%"
          ></div>
        </div>

        <div class="card-tip">
          本阶段学习状态良好
        </div>
      </div>


      <div class="overview-card level-card">

        <div class="card-label">
          当前成长等级
        </div>

        <div class="level">
          A
        </div>

        <div class="level-name">
          AI应用开发阶段
        </div>

        <div class="card-tip">
          已进入项目实践阶段
        </div>

      </div>

    </div>


    <!-- 主体区域 -->
    <div class="content-grid">


      <!-- AI总结 -->
      <el-card class="report-card">

        <template #header>

          <div class="card-title">

            <span class="title-icon">
              ✦
            </span>

            AI成长总结

          </div>

        </template>


        <div class="ai-summary">

          <div class="summary-highlight">

            <strong>
              当前学习状态：稳定提升
            </strong>

            <span>
              综合能力处于持续增长阶段
            </span>

          </div>


          <p>
            根据近期学习数据分析，你已经建立较为完整的
            编程知识体系，在算法训练、项目实践和人工智能
            应用方面表现出较好的学习基础。
          </p>


          <p>
            当前阶段的主要优势是学习状态稳定，并能够将
            已掌握的知识逐步应用到实际项目中。后续可以
            进一步加强复杂算法、模型应用以及工程实践能力。
          </p>

        </div>

      </el-card>



      <!-- 能力分析 -->
      <el-card class="report-card">

        <template #header>

          <div class="card-title">

            <span class="title-icon">
              ◈
            </span>

            核心能力分析

          </div>

        </template>


        <div class="ability-list">


          <div class="ability-item">

            <div class="ability-top">

              <span>
                编程基础
              </span>

              <strong>
                90
              </strong>

            </div>

            <el-progress
              :percentage="90"
              :show-text="false"
            />

          </div>



          <div class="ability-item">

            <div class="ability-top">

              <span>
                算法能力
              </span>

              <strong>
                85
              </strong>

            </div>

            <el-progress
              :percentage="85"
              :show-text="false"
            />

          </div>



          <div class="ability-item">

            <div class="ability-top">

              <span>
                AI能力
              </span>

              <strong>
                78
              </strong>

            </div>

            <el-progress
              :percentage="78"
              :show-text="false"
            />

          </div>



          <div class="ability-item">

            <div class="ability-top">

              <span>
                工程实践
              </span>

              <strong>
                82
              </strong>

            </div>

            <el-progress
              :percentage="82"
              :show-text="false"
            />

          </div>


        </div>

      </el-card>

    </div>



    <!-- 成长建议 -->
    <el-card class="report-card recommendation-card">

      <template #header>

        <div class="card-title">

          <span class="title-icon">
            ◎
          </span>

          下一阶段成长建议

        </div>

      </template>


      <div class="recommendations">


        <div class="recommendation">

          <div class="recommendation-number">
            01
          </div>

          <div>

            <h3>
              深入学习人工智能核心技术
            </h3>

            <p>
              重点加强机器学习、深度学习及模型应用能力。
            </p>

          </div>

        </div>



        <div class="recommendation">

          <div class="recommendation-number">
            02
          </div>

          <div>

            <h3>
              增强项目工程实践
            </h3>

            <p>
              将知识应用到完整项目中，提升系统设计和开发能力。
            </p>

          </div>

        </div>



        <div class="recommendation">

          <div class="recommendation-number">
            03
          </div>

          <div>

            <h3>
              开展创新实践
            </h3>

            <p>
              尝试将AI技术应用到实际场景，形成具有创新性的项目成果。
            </p>

          </div>

        </div>


      </div>

    </el-card>



    <!-- 报告底部 -->
    <div class="report-footer">

      <div>

        <span class="footer-label">
          REPORT GENERATED BY
        </span>

        <strong>
          ProgramMind AI
        </strong>

      </div>


      <div>
        当前成长阶段 · AI应用开发
      </div>

    </div>


  </div>
</template>


<script setup>

</script>


<style scoped>

.report-page {
  padding: 28px;
  min-height: 100%;
  box-sizing: border-box;
}


/* 顶部 */

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 26px;
}


.eyebrow {
  font-size: 12px;
  letter-spacing: 2px;
  font-weight: 600;
  margin-bottom: 8px;
  opacity: 0.55;
}


.page-header h1 {
  margin: 0;
  font-size: 30px;
  font-weight: 700;
}


.page-header p {
  margin: 10px 0 0;
  opacity: 0.65;
}


.report-status {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 9px 14px;
  border-radius: 20px;
  background: rgba(37, 99, 235, 0.08);
  font-size: 13px;
}


.status-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: #22c55e;
}


/* 核心数据 */

.overview-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 18px;
  margin-bottom: 20px;
}


.overview-card {
  padding: 22px;
  border-radius: 16px;
  background: white;
  border: 1px solid #e5e7eb;
  box-sizing: border-box;
}


.card-label {
  font-size: 13px;
  color: #64748b;
}


.big-number {
  margin-top: 10px;
  font-size: 34px;
  font-weight: 700;
}


.big-number span {
  font-size: 15px;
  color: #94a3b8;
}


.progress {
  height: 6px;
  margin-top: 16px;
  border-radius: 10px;
  background: #e2e8f0;
  overflow: hidden;
}


.progress-inner {
  height: 100%;
  border-radius: 10px;
  background: #2563eb;
}


.card-tip {
  margin-top: 12px;
  font-size: 12px;
  color: #64748b;
}


.level-card {
  text-align: center;
}


.level {
  margin-top: 4px;
  font-size: 46px;
  font-weight: 800;
  color: #2563eb;
}


.level-name {
  margin-top: 2px;
  font-size: 14px;
  font-weight: 600;
}


/* 主体 */

.content-grid {
  display: grid;
  grid-template-columns: 1.2fr 1fr;
  gap: 20px;
  margin-bottom: 20px;
}


.report-card {
  border-radius: 16px;
  border: 1px solid #e5e7eb;
}


.card-title {
  display: flex;
  align-items: center;
  gap: 10px;
  font-weight: 700;
}


.title-icon {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 28px;
  height: 28px;
  border-radius: 8px;
  background: rgba(37, 99, 235, 0.08);
  color: #2563eb;
}


.ai-summary {
  line-height: 1.8;
  color: #475569;
}


.summary-highlight {
  display: flex;
  flex-direction: column;
  gap: 4px;
  padding: 14px 16px;
  margin-bottom: 16px;
  border-radius: 12px;
  background: #f8fafc;
}


.summary-highlight strong {
  color: #1e293b;
}


.summary-highlight span {
  font-size: 13px;
  color: #64748b;
}


.ai-summary p {
  margin: 12px 0;
}


/* 能力 */

.ability-list {
  display: flex;
  flex-direction: column;
  gap: 20px;
}


.ability-top {
  display: flex;
  justify-content: space-between;
  margin-bottom: 8px;
  font-size: 14px;
}


.ability-top strong {
  color: #2563eb;
}


/* 推荐 */

.recommendation-card {
  margin-bottom: 20px;
}


.recommendations {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 18px;
}


.recommendation {
  display: flex;
  gap: 14px;
  padding: 18px;
  border-radius: 14px;
  background: #f8fafc;
}


.recommendation-number {
  font-size: 20px;
  font-weight: 700;
  color: #2563eb;
}


.recommendation h3 {
  margin: 0 0 8px;
  font-size: 15px;
}


.recommendation p {
  margin: 0;
  font-size: 13px;
  line-height: 1.7;
  color: #64748b;
}


/* 底部 */

.report-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 4px;
  font-size: 12px;
  color: #64748b;
}


.footer-label {
  margin-right: 8px;
  font-size: 10px;
  letter-spacing: 1px;
}


.report-footer strong {
  color: #334155;
}


/* 自适应 */

@media (max-width: 1100px) {

  .overview-grid {
    grid-template-columns: repeat(2, 1fr);
  }

  .content-grid {
    grid-template-columns: 1fr;
  }

  .recommendations {
    grid-template-columns: 1fr;
  }

}


@media (max-width: 700px) {

  .report-page {
    padding: 16px;
  }

  .page-header {
    flex-direction: column;
    gap: 15px;
  }

  .overview-grid {
    grid-template-columns: 1fr;
  }

}

</style>