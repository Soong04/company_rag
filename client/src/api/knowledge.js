import request from './request'

// ========== 分类管理 ==========

export function getCategories() {
    return request({ url: '/knowledge/categories', method: 'get' })
}

export function createCategory(data) {
    return request({ url: '/knowledge/categories', method: 'post', data })
}

export function updateCategory(id, data) {
    return request({ url: `/knowledge/categories/${id}`, method: 'put', data })
}

export function deleteCategory(id) {
    return request({ url: `/knowledge/categories/${id}`, method: 'delete' })
}

// ========== 文档管理 ==========

export function getDocuments(params) {
    return request({ url: '/knowledge/documents', method: 'get', params })
}

export function getDocument(id) {
    return request({ url: `/knowledge/documents/${id}`, method: 'get' })
}

export function uploadDocument(formData) {
    return request({
        url: '/knowledge/documents',
        method: 'post',
        data: formData,
    })
}

export function updateDocument(id, data) {
    return request({ url: `/knowledge/documents/${id}`, method: 'put', data })
}

export function deleteDocument(id) {
    return request({ url: `/knowledge/documents/${id}`, method: 'delete' })
}

// ========== 文档预览 ==========

export function previewDocument(id) {
    return request({ url: `/knowledge/documents/${id}/preview`, method: 'get' })
}

/**
 * 获取文档原始文件的下载/预览URL
 * 用于浏览器直接打开 PDF 等
 */
export function getDocumentFileUrl(id) {
    return `/api/knowledge/documents/${id}/file`
}

// ========== 重新向量化 ==========

/**
 * 重新向量化文档（重试失败的文档）
 * @param {number} id 文档ID
 * @returns {Promise}
 */
export function revectorizeDocument(id) {
    return request({
        url: `/knowledge/documents/${id}/revectorize`,
        method: 'post',
    })
}
