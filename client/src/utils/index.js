/**
 * 格式化文件大小
 * @param {number} bytes 字节数
 * @returns {string}
 */
export function formatFileSize(bytes) {
    if (!bytes || bytes === 0) return '0 B'
    const units = ['B', 'KB', 'MB', 'GB']
    const k = 1024
    const i = Math.floor(Math.log(bytes) / Math.log(k))
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + units[i]
}

/**
 * 格式化日期时间
 * @param {string|Date} date
 * @returns {string}
 */
export function formatDateTime(date) {
    if (!date) return ''
    const d = new Date(date)
    const year = d.getFullYear()
    const month = String(d.getMonth() + 1).padStart(2, '0')
    const day = String(d.getDate()).padStart(2, '0')
    const hour = String(d.getHours()).padStart(2, '0')
    const min = String(d.getMinutes()).padStart(2, '0')
    return `${year}-${month}-${day} ${hour}:${min}`
}

/**
 * 获取文档处理状态文本
 * @param {number} status
 * @returns {string}
 */
export function getDocStatusText(status) {
    const map = {
        0: '待处理',
        1: '处理中',
        2: '已完成',
        '-1': '失败',
    }
    return map[status] || '未知'
}

/**
 * 获取文档状态标签类型
 * @param {number} status
 * @returns {string}
 */
export function getDocStatusType(status) {
    const map = {
        0: 'info',
        1: 'warning',
        2: 'success',
        '-1': 'danger',
    }
    return map[status] || 'info'
}

/**
 * 获取用户角色文本
 * @param {string} role
 * @returns {string}
 */
export function getRoleText(role) {
    return role === 'admin' ? '管理员' : '普通用户'
}

/**
 * 获取用户角色标签类型
 * @param {string} role
 * @returns {string}
 */
export function getRoleType(role) {
    return role === 'admin' ? 'danger' : 'primary'
}
