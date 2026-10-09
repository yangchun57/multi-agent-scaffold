import axios from 'axios'
import type { AxiosInstance, InternalAxiosRequestConfig } from 'axios'
import { ElMessage } from 'element-plus'

const request: AxiosInstance = axios.create({
  baseURL: '/api',
  timeout: 15000,
})

// 请求拦截器
request.interceptors.request.use(
  (config: InternalAxiosRequestConfig) => {
    // TODO: 从 user store 注入 token（`Authorization: Bearer xxx`）
    return config
  },
  (error) => Promise.reject(error),
)

// 响应拦截器
request.interceptors.response.use(
  (response) => {
    // 直接返回 data，调用处拿到的就是 ApiResult<T>
    return response.data
  },
  (error) => {
    ElMessage.error('网络错误，请稍后重试')
    console.error('request error:', error)
    return Promise.reject(error)
  },
)

export default request
