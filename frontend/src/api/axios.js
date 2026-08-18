import axios from 'axios'

const instance = axios.create({
  baseURL: '/api/v1',
  timeout: 10000,
})

// 响应拦截器：统一处理错误
instance.interceptors.response.use(
  (response) => response,
  (error) => {
    const message =
      error.response?.data?.detail || error.message || '请求失败，请稍后再试'
    console.error('[API error]', message)
    return Promise.reject(new Error(message))
  }
)

export default instance