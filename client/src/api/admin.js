import request from './request'

/**
 * 获取仪表盘统计数据
 * @returns {Promise}
 */
export function getDashboard() {
    return request({ url: '/admin/dashboard', method: 'get' })
}

/**
 * 获取统计趋势数据
 * @returns {Promise}
 */
export function getStats() {
    return request({ url: '/admin/stats', method: 'get' })
}

/**
 * 获取操作日志
 * @param {object} params { page, size }
 * @returns {Promise}
 */
export function getLogs(params) {
    return request({ url: '/admin/logs', method: 'get', params })
}

/**
 * 获取用户列表（管理员）
 * @param {object} params { page, size, keyword }
 * @returns {Promise}
 */
export function getUsers(params) {
    return request({ url: '/admin/users', method: 'get', params })
}

/**
 * 更新用户信息（管理员）
 * @param {number} id 用户ID
 * @param {object} data 更新数据
 * @returns {Promise}
 */
export function updateUser(id, data) {
    return request({ url: `/admin/users/${id}`, method: 'put', data })
}

/**
 * 创建用户（管理员）
 * @param {object} data { username, password, real_name, email, phone, role, status }
 * @returns {Promise}
 */
export function createUser(data) {
    return request({ url: '/admin/users', method: 'post', data })
}

/**
 * 启用/禁用用户
 * @param {number} id 用户ID
 * @returns {Promise}
 */
export function toggleUserStatus(id) {
    return request({ url: `/admin/users/${id}/toggle_status`, method: 'post' })
}
