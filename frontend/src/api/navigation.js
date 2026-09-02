import request from "./request"


// 获取个性化导航建议
export function getNavigationSuggestions() {

  return request({

    url: "/navigation/suggestions",

    method: "get"

  })

}