import { createApp } from 'vue'
import App from './App.vue'
import ElementPlus from 'element-plus'
import axios from 'axios'
import VueAxios from 'vue-axios'

import 'element-plus/dist/index.css'

const app = createApp(App)

app.use(ElementPlus)
app.use(VueAxios, axios)
app.mount('#app')