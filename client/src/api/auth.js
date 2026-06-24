import request from './request'

/**
 * 用户登录
 * @param {string} username 用户名
 * @param {string} password 密码
 * @returns {Promise}
 */
export function login(username, password) {
    return request({
        url: '/auth/login',
        method: 'post',
        data: { username, password },
    })
}

/**
 * 用户登出
 * @returns {Promise}
 */
export function logout() {
    return request({
        url: '/auth/logout',
        method: 'post',
    })
}

/**
 * 获取当前用户信息
 * @returns {Promise}
 */
export function getCurrentUser() {
    return request({
        url: '/auth/current_user',
        method: 'get',
    })
}
