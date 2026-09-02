import request from "./request"


// 获取成长报告
export function getGrowthReport() {

  return request({

    url: "/report",

    method: "get"

  })

}


// 生成成长报告
export function generateGrowthReport() {

  return request({

    url: "/report/generate",

    method: "post"

  })

}