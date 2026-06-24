import axios from 'axios'
import { ElMessage } from 'element-plus'
import router from '@/router'

// 创建 Axios 实例
const request = axios.create({
    baseURL: '/api',
    timeout: 60000,
    withCredentials: true,
})

// 响应拦截器
request.interceptors.response.use(
    (response) => {
        const res = response.data
        return res
    },
    (error) => {
        if (error.response) {
            const { status, data } = error.response
            switch (status) {
                case 401:
                    ElMessage.error('登录已过期，请重新登录')
                    router.push('/login')
                    break
                case 403:
                    ElMessage.error(data?.message || '权限不足')
                    break
                case 404:
                    ElMessage.error('请求的资源不存在')
                    break
                case 500:
                    ElMessage.error(data?.message || '服务器错误，请稍后重试')
                    break
                default:
                    ElMessage.error(data?.message || '请求失败')
            }
        } else if (error.request) {
            ElMessage.error('网络连接失败，请检查网络')
        } else {
            ElMessage.error('请求配置错误')
        }
        return Promise.reject(error)
    }
)

export default request
