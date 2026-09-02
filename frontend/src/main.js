import { createApp } from "vue"

import { createPinia } from "pinia"

import ElementPlus from "element-plus"

import "element-plus/dist/index.css"

import App from "./App.vue"

import router from "./router"


const app = createApp(App)


// Pinia
const pinia = createPinia()

app.use(pinia)


// Element Plus
app.use(ElementPlus)


// Vue Router
app.use(router)


// 恢复登录状态
import { useUserStore } from "./stores/user"

const userStore = useUserStore()

userStore.restoreLogin()


app.mount("#app")