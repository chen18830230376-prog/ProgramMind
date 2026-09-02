import axios from "axios"


const request = axios.create({

  // 后续后端正式接口地址可以在这里统一修改
  baseURL: "/api",

  // 请求超时时间
  timeout: 10000

})


// 请求拦截器
request.interceptors.request.use(

  (config) => {

    // 从浏览器中获取 Token
    const token = localStorage.getItem("token")


    if (token) {

      config.headers.Authorization =
        `Bearer ${token}`

    }


    return config

  },


  (error) => {

    return Promise.reject(error)

  }

)


// 响应拦截器
request.interceptors.response.use(

  (response) => {

    return response.data

  },


  (error) => {

    console.error(
      "API请求失败：",
      error
    )


    return Promise.reject(error)

  }

)


export default request