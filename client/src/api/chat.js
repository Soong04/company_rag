import request from './request'

/**
 * 发起问答
 * @param {string} question 问题
 * @param {number} [conversationId] 对话ID（可选）
 * @returns {Promise}
 */
export function askQuestion(question, conversationId) {
    return request({
        url: '/chat/ask',
        method: 'post',
        data: { question, conversation_id: conversationId },
    })
}

/**
 * 获取历史对话列表
 * @param {object} params { page, size }
 * @returns {Promise}
 */
export function getConversations(params) {
    return request({
        url: '/chat/history',
        method: 'get',
        params,
    })
}

/**
 * 获取对话详情
 * @param {number} id 对话ID
 * @returns {Promise}
 */
export function getConversationDetail(id) {
    return request({
        url: `/chat/history/${id}`,
        method: 'get',
    })
}

/**
 * 删除对话
 * @param {number} id 对话ID
 * @returns {Promise}
 */
export function deleteConversation(id) {
    return request({
        url: `/chat/history/${id}`,
        method: 'delete',
    })
}

/**
 * 提交问答反馈
 * @param {number} messageId 消息ID
 * @param {number} rating 评分 1=赞 -1=踩
 * @param {string} comment 备注
 */
export function submitFeedback(messageId, rating, comment = '') {
    return request({
        url: '/chat/feedback',
        method: 'post',
        data: { message_id: messageId, rating, comment },
    })
}

/**
 * 流式问答 - 使用 fetch 读取 SSE 流
 * @param {string} question 问题
 * @param {number|null} conversationId 对话ID
 * @param {function} onToken 每个 token 的回调
 * @param {function} onSources 来源信息的回调
 * @param {function} onDone 完成回调
 */
export function askQuestionStream(question, conversationId, onToken, onSources, onDone) {
    const baseURL = '/api'
    const url = `${baseURL}/chat/stream`

    fetch(url, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        credentials: 'include',
        body: JSON.stringify({ question, conversation_id: conversationId }),
    }).then(async (response) => {
        const reader = response.body.getReader()
        const decoder = new TextDecoder()
        let buffer = ''

        while (true) {
            const { done, value } = await reader.read()
            if (done) break

            buffer += decoder.decode(value, { stream: true })
            const lines = buffer.split('\n')
            buffer = lines.pop() || ''  // 保留未完成的行

            for (const line of lines) {
                if (line.startsWith('data: ')) {
                    try {
                        const event = JSON.parse(line.slice(6))
                        if (event.type === 'token') {
                            onToken(event.data)
                        } else if (event.type === 'sources') {
                            onSources(event.data)
                        } else if (event.type === 'done') {
                            onDone(event.data)
                        }
                    } catch (e) {
                        // 跳过解析失败的行
                    }
                }
            }
        }
    }).catch((err) => {
        onDone({ error: err.message })
    })
}
