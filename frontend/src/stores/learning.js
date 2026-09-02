import { defineStore } from "pinia"


export const useLearningStore = defineStore("learning", {

  state: () => ({

    // 综合能力
    overallScore: 0,

    // 各项能力
    ability: {

      programming: 0,

      algorithm: 0,

      ai: 0,

      engineering: 0

    },


    // 知识掌握度
    knowledgeMastery: 0,


    // 学习活跃度
    learningActivity: 0,


    // 当前成长等级
    level: "",


    // 当前学习阶段
    currentStage: "",


    // 学习时间
    learningHours: 0,


    // 知识节点
    knowledgeNodes: [],


    // 成长记录
    growthRecords: []

  }),


  getters: {

    // 获取综合能力
    score: (state) => {

      return state.overallScore

    },


    // 获取当前成长等级
    growthLevel: (state) => {

      return state.level || "暂无"

    }

  },


  actions: {

    // 设置完整学习数据
    setLearningData(data) {

      this.overallScore =
        data.overallScore ??
        this.overallScore


      this.ability = {

        programming:
          data.ability?.programming ??
          this.ability.programming,

        algorithm:
          data.ability?.algorithm ??
          this.ability.algorithm,

        ai:
          data.ability?.ai ??
          this.ability.ai,

        engineering:
          data.ability?.engineering ??
          this.ability.engineering

      }


      this.knowledgeMastery =
        data.knowledgeMastery ??
        this.knowledgeMastery


      this.learningActivity =
        data.learningActivity ??
        this.learningActivity


      this.level =
        data.level ??
        this.level


      this.currentStage =
        data.currentStage ??
        this.currentStage


      this.learningHours =
        data.learningHours ??
        this.learningHours


      this.knowledgeNodes =
        data.knowledgeNodes ??
        this.knowledgeNodes


      this.growthRecords =
        data.growthRecords ??
        this.growthRecords

    },


    // 更新能力
    updateAbility(ability) {

      this.ability = {

        ...this.ability,

        ...ability

      }

    },


    // 添加成长记录
    addGrowthRecord(record) {

      this.growthRecords.push(record)

    }

  }

})