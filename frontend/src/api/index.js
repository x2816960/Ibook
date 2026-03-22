import axios from 'axios'
import { ElMessage } from 'element-plus'
import router from '../router'

const api = axios.create({
  baseURL: '/api',
  timeout: 30000,
})

api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token') || sessionStorage.getItem('token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

api.interceptors.response.use(
  (response) => response,
  (error) => {
    // 如果配置了silent: true，则不显示错误消息
    if (!error.config?.silent) {
      const msg = error.response?.data?.detail || '请求失败'
      if (error.response?.status === 401) {
        localStorage.removeItem('token')
        sessionStorage.removeItem('token')
        router.push('/login')
        ElMessage.error('登录已过期，请重新登录')
      } else {
        ElMessage.error(msg)
      }
    }
    return Promise.reject(error)
  }
)

export default api
