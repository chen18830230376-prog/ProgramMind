import request from "./request"


// 获取状态仪表盘数据
export function getDashboardData() {

  return request({

    url: "/dashboard",

    method: "get"

  })

}