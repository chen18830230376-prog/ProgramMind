import request from "./request"


// 获取知识地图
export function getKnowledgeMap() {

  return request({

    url: "/knowledge/map",

    method: "get"

  })

}


// 获取知识点详情
export function getKnowledgeInfo(id) {

  return request({

    url: `/knowledge/${id}`,

    method: "get"

  })

}