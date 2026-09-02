import request from "./request"


// 获取成长轨迹
export function getGrowthTimeline() {

  return request({

    url: "/growth/timeline",

    method: "get"

  })

}


// 获取成长阶段
export function getGrowthStage() {

  return request({

    url: "/growth/stage",

    method: "get"

  })

}