import { defineStore } from "pinia"


export const useUserStore = defineStore("user", {

  state: () => ({

    // 用户信息
    userInfo: {
      username: "",
      name: "",
      avatar: ""
    },

    // 登录状态
    isLoggedIn: false,

    // Token
    token: ""

  }),


  getters: {

    // 当前用户名
    currentUsername: (state) => {

      return (
        state.userInfo.name ||
        state.userInfo.username ||
        "用户"
      )

    }

  },


  actions: {

    // 登录成功
    login(userInfo = {}, token = "") {

      this.userInfo = {

        username:
          userInfo.username || "",

        name:
          userInfo.name ||
          userInfo.username ||
          "",

        avatar:
          userInfo.avatar || ""

      }


      this.token = token

      this.isLoggedIn = true


      // 保存 Token
      if (token) {

        localStorage.setItem(
          "token",
          token
        )

      }


      // 保存用户信息
      localStorage.setItem(
        "userInfo",
        JSON.stringify(this.userInfo)
      )

    },


    // 从浏览器恢复登录状态
    restoreLogin() {

      const token =
        localStorage.getItem("token")

      const userInfo =
        localStorage.getItem("userInfo")


      if (token) {

        this.token = token

        this.isLoggedIn = true

      }


      if (userInfo) {

        try {

          this.userInfo =
            JSON.parse(userInfo)

        } catch (error) {

          console.error(
            "用户信息解析失败",
            error
          )

        }

      }

    },


    // 退出登录
    logout() {

      this.userInfo = {

        username: "",

        name: "",

        avatar: ""

      }


      this.token = ""

      this.isLoggedIn = false


      localStorage.removeItem("token")

      localStorage.removeItem("userInfo")

    }

  }

})