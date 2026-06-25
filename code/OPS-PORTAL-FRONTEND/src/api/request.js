import axios from 'axios'
import router from '../router/index.js'

const request = axios.create({
  baseURL: '',  // 空串 = 同源请求，后端托管前端时无跨域问题
  timeout: 120000,  // 120秒，后端 RAG 超时 60 秒，留足余量
})
// 请求拦截：自动带上 Token 和 ngrok 头
request.interceptors.request.use(config => {
  // config.headers['ngrok-skip-browser-warning'] = 'true'  // 本地开发不需要 ngrok
  const token = localStorage.getItem('token')
  if (token) {
    config.headers['Authorization'] = `Bearer ${token}`
  }
  return config
})

// 响应拦截：401 自动跳登录
request.interceptors.response.use(
  res => res,
  err => {
    if (err.response?.status === 401) {
      localStorage.removeItem('token')
      router.push('/login')
    }
    return Promise.reject(err)
  }
)

export default request




