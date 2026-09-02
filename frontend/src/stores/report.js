import { defineStore } from "pinia"


export const useReportStore = defineStore("report", {

  state: () => ({

    // 报告生成状态
    generated: false,


    // 报告生成时间
    generatedAt: "",


    // AI成长总结
    summary: "",


    // AI成长建议
    recommendations: [],


    // 当前成长阶段
    stage: "",


    // 成长等级
    level: "",


    // 报告数据
    reportData: {}

  }),


  actions: {

    // 保存报告
    setReport(data) {

      this.generated = true

      this.generatedAt =
        data.generatedAt ||
        new Date().toLocaleString()


      this.summary =
        data.summary ||
        ""


      this.recommendations =
        data.recommendations ||
        []


      this.stage =
        data.stage ||
        ""


      this.level =
        data.level ||
        ""


      this.reportData =
        data

    },


    // 清空报告
    clearReport() {

      this.generated = false

      this.generatedAt = ""

      this.summary = ""

      this.recommendations = []

      this.stage = ""

      this.level = ""

      this.reportData = {}

    }

  }

})