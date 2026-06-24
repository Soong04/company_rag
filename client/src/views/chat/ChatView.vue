<template>
    <div class="chat-page">
        <div class="chat-container">
            <!-- 左侧：历史对话列表 -->
            <div class="chat-sidebar">
                <div class="sidebar-header">
                    <h3>历史对话</h3>
                    <el-button
                        type="primary"
                        size="small"
                        :icon="Plus"
                        @click="startNewChat"
                    >
                        新对话
                    </el-button>
                </div>
                <div class="sidebar-search">
                    <el-input
                        v-model="searchKeyword"
                        placeholder="搜索对话..."
                        size="small"
                        clearable
                        @input="onSearchConv"
                        @clear="fetchConversations"
                    >
                        <template #prefix>
                            <el-icon><Search /></el-icon>
                        </template>
                    </el-input>
                </div>
                <div class="sidebar-list" v-loading="convLoading">
                    <div
                        v-for="conv in convList"
                        :key="conv.id"
                        class="conv-item"
                        :class="{ active: currentConvId === conv.id }"
                        @click="switchConversation(conv.id)"
                    >
                        <div class="conv-title">
                            <el-icon><ChatDotRound /></el-icon>
                            <span class="conv-text">{{ conv.title }}</span>
                        </div>
                        <div class="conv-meta">
                            <span>{{ conv.message_count }}条消息</span>
                            <span>{{ conv.update_time }}</span>
                        </div>
                        <el-button
                            class="delete-btn"
                            text
                            size="small"
                            type="danger"
                            :icon="Delete"
                            @click.stop="handleDeleteConv(conv.id)"
                        />
                    </div>
                    <el-empty v-if="!convList.length && !convLoading" description="暂无对话" />
                </div>
            </div>

            <!-- 右侧：对话区域 -->
            <div class="chat-main">
                <!-- 消息列表 -->
                <div class="message-list" ref="messageListRef">
                    <div
                        v-for="(msg, index) in messages"
                        :key="index"
                        class="message-item"
                        :class="msg.role"
                    >
                        <div class="message-avatar">
                            <el-avatar
                                :size="36"
                                :icon="msg.role === 'user' ? 'UserFilled' : 'MagicStick'"
                                :style="msg.role === 'user' ? '' : 'background: #409eff'"
                            />
                        </div>
                        <div class="message-content">
                            <div class="message-bubble">
                                <div class="message-text" v-html="renderMarkdown(msg.content)"></div>
                            </div>
                            <!-- 反馈按钮（仅 AI 回答） -->
                            <div v-if="msg.role === 'assistant' && msg.id" class="message-feedback">
                                <el-button
                                    text
                                    size="small"
                                    :type="msg.feedback === 1 ? 'primary' : 'default'"
                                    @click="handleFeedback(msg, 1)"
                                >
                                    👍 {{ msg.feedback === 1 ? '已赞' : '' }}
                                </el-button>
                                <el-button
                                    text
                                    size="small"
                                    :type="msg.feedback === -1 ? 'danger' : 'default'"
                                    @click="handleFeedback(msg, -1)"
                                >
                                    👎 {{ msg.feedback === -1 ? '已踩' : '' }}
                                </el-button>
                            </div>
                            <!-- 引用来源 -->
                            <div v-if="msg.source_docs?.length" class="message-sources">
                                <span class="sources-label">📚 引用来源：</span>
                                <el-tag
                                    v-for="(src, si) in msg.source_docs"
                                    :key="si"
                                    size="small"
                                    type="info"
                                    style="margin: 2px 4px 2px 0"
                                >
                                    {{ src.title }}
                                </el-tag>
                            </div>
                        </div>
                    </div>

                    <!-- 加载中 -->
                    <div v-if="loading" class="message-item assistant">
                        <div class="message-avatar">
                            <el-avatar :size="36" icon="MagicStick" style="background: #409eff" />
                        </div>
                        <div class="message-content">
                            <div class="message-bubble thinking">
                                <span class="thinking-dots">思考中</span>
                                <span class="dot-animation">
                                    <span>.</span><span>.</span><span>.</span>
                                </span>
                            </div>
                        </div>
                    </div>
                </div>

                <!-- 输入区域 -->
                <div class="input-area">
                    <el-input
                        v-model="question"
                        type="textarea"
                        :rows="3"
                        placeholder="请输入您的问题..."
                        :disabled="loading"
                        @keydown.enter.prevent="handleSend"
                    />
                    <div class="input-actions">
                        <span class="input-tip">按 Enter 发送，Shift+Enter 换行</span>
                        <el-button
                            type="primary"
                            :icon="Promotion"
                            :loading="loading"
                            @click="handleSend"
                        >
                            发送
                        </el-button>
                    </div>
                </div>
            </div>
        </div>
    </div>
</template>

<script setup>
import { ref, onMounted, nextTick, watch } from 'vue'
import { useRoute } from 'vue-router'
import { Plus, Delete, Promotion, Search } from '@element-plus/icons-vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { askQuestion, askQuestionStream, getConversations, getConversationDetail, deleteConversation, submitFeedback } from '@/api/chat'

const route = useRoute()

const question = ref('')
const messages = ref([])
const loading = ref(false)
const currentConvId = ref(null)

const convList = ref([])
const convLoading = ref(false)
const convPage = ref(1)
const messageListRef = ref(null)
const searchKeyword = ref('')
let searchTimer = null

// 启动新对话
function startNewChat() {
    currentConvId.value = null
    messages.value = []
    question.value = ''
    // 刷新列表使新对话出现在顶部
    fetchConversations()
}

// 切换对话
async function switchConversation(id) {
    if (loading.value) return
    currentConvId.value = id
    await fetchConversationMessages(id)
}

// 获取对话消息
async function fetchConversationMessages(id) {
    try {
        const res = await getConversationDetail(id)
        if (res.code === 200) {
            messages.value = (res.data.messages || []).map(m => ({
                ...m,
                feedback: null,
            }))
            nextTick(() => scrollToBottom())
        }
    } catch (err) {
        console.error('获取消息失败:', err)
    }
}

// 提交反馈（赞/踩）
async function handleFeedback(msg, rating) {
    if (!msg.id) {
        ElMessage.warning('消息尚未保存，请稍后再试')
        return
    }
    try {
        const res = await submitFeedback(msg.id, rating)
        if (res.code === 200) {
            msg.feedback = msg.feedback === rating ? null : rating
            ElMessage.success(rating === 1 ? '已赞' : '已踩')
        }
    } catch (err) {
        console.error('提交反馈失败:', err)
    }
}

// 发送消息（流式输出）
async function handleSend() {
    const text = question.value.trim()
    if (!text) {
        ElMessage.warning('请输入问题')
        return
    }
    if (loading.value) return

    // 添加用户消息到列表
    messages.value.push({
        role: 'user',
        content: text,
        source_docs: null,
    })
    question.value = ''

    // 添加一个空的 AI 消息占位，逐步填充
    const aiMsgIndex = messages.value.length
    messages.value.push({
        role: 'assistant',
        content: '',
        source_docs: [],
        id: null,
        feedback: null,
    })
    loading.value = true

    try {
        await askQuestionStream(
            text,
            currentConvId.value,
            // onToken - 每个 token 追加到消息
            (token) => {
                messages.value[aiMsgIndex].content += token
                nextTick(() => scrollToBottom())
            },
            // onSources - 来源信息
            (sources) => {
                messages.value[aiMsgIndex].source_docs = sources
            },
            // onDone - 完成
            (data) => {
                if (data.conversation_id) {
                    currentConvId.value = data.conversation_id
                }
                if (data.message_id) {
                    messages.value[aiMsgIndex].id = data.message_id
                }
                if (data.error) {
                    messages.value[aiMsgIndex].content = '抱歉，网络连接失败，请稍后重试。'
                }
                fetchConversations()
                loading.value = false
                nextTick(() => scrollToBottom())
            }
        )
    } catch (err) {
        messages.value[aiMsgIndex].content = '抱歉，网络连接失败，请稍后重试。'
        loading.value = false
        nextTick(() => scrollToBottom())
    }
}

// 删除对话
async function handleDeleteConv(id) {
    try {
        await ElMessageBox.confirm('确定删除此对话？', '提示')
        const res = await deleteConversation(id)
        if (res.code === 200) {
            ElMessage.success('删除成功')
            if (currentConvId.value === id) {
                currentConvId.value = null
                messages.value = []
            }
            fetchConversations()
        }
    } catch {
        // 取消
    }
}

// 获取历史对话列表
async function fetchConversations(keyword = '') {
    convLoading.value = true
    try {
        const params = { page: convPage.value, size: 50 }
        if (keyword) params.keyword = keyword
        const res = await getConversations(params)
        if (res.code === 200) {
            convList.value = res.data.list
        }
    } catch (err) {
        console.error('获取对话列表失败:', err)
    } finally {
        convLoading.value = false
    }
}

// 防抖搜索对话
function onSearchConv() {
    if (searchTimer) clearTimeout(searchTimer)
    searchTimer = setTimeout(() => {
        fetchConversations(searchKeyword.value)
    }, 300)
}

// 滚动到底部
function scrollToBottom() {
    nextTick(() => {
        if (messageListRef.value) {
            messageListRef.value.scrollTop = messageListRef.value.scrollHeight
        }
    })
}

// ====== Markdown 渲染（marked + highlight.js） ======
import { marked } from 'marked'
import hljs from 'highlight.js'
import 'highlight.js/styles/github.css'

// 配置 marked 使用 highlight.js 做代码高亮
marked.setOptions({
    breaks: true,
    gfm: true,
    highlight: function (code, lang) {
        if (lang && hljs.getLanguage(lang)) {
            try {
                return hljs.highlight(code, { language: lang }).value
            } catch (e) { /* fall through */ }
        }
        // 没有指定语言或语言不支持，自动检测
        try {
            return hljs.highlightAuto(code).value
        } catch (e) {
            return code
        }
    }
})

function renderMarkdown(text) {
    if (!text) return ''
    try {
        return marked.parse(text)
    } catch (e) {
        // 降级：转义后原样输出
        return text.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;')
    }
}

// 监听路由参数（如果有对话ID）
watch(
    () => route.params.id,
    (newId) => {
        if (newId) {
            switchConversation(Number(newId))
        }
    }
)

onMounted(() => {
    fetchConversations()

    // 检查路由是否有对话ID
    const convId = route.params.id
    if (convId) {
        switchConversation(Number(convId))
    }
})
</script>

<style scoped>
.chat-page {
    height: 100%;
    padding: 16px;
}

.chat-container {
    display: flex;
    height: 100%;
    background: #fff;
    border-radius: 8px;
    overflow: hidden;
    box-shadow: 0 1px 4px rgba(0, 0, 0, 0.06);
}

/* 左侧历史 */
.chat-sidebar {
    width: 280px;
    border-right: 1px solid #e4e7ed;
    display: flex;
    flex-direction: column;
    background: #fafafa;
}

.sidebar-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 16px;
    border-bottom: 1px solid #e4e7ed;
}

.sidebar-header h3 {
    margin: 0;
    font-size: 15px;
    color: #303133;
}

.sidebar-search {
    padding: 8px 12px;
    border-bottom: 1px solid #e4e7ed;
}

.sidebar-list {
    flex: 1;
    overflow-y: auto;
    padding: 8px;
}

.conv-item {
    padding: 10px 12px;
    border-radius: 6px;
    cursor: pointer;
    margin-bottom: 4px;
    position: relative;
    transition: background 0.2s;
}

.conv-item:hover {
    background: #e8f4ff;
}

.conv-item.active {
    background: #ecf5ff;
    border: 1px solid #b3d8ff;
}

.conv-title {
    display: flex;
    align-items: center;
    gap: 6px;
    font-size: 13px;
    color: #303133;
}

.conv-text {
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
}

.conv-meta {
    font-size: 11px;
    color: #909399;
    margin-top: 4px;
    display: flex;
    justify-content: space-between;
}

.delete-btn {
    position: absolute;
    right: 4px;
    top: 4px;
    opacity: 0;
    transition: opacity 0.2s;
}

.conv-item:hover .delete-btn {
    opacity: 1;
}

/* 右侧对话 */
.chat-main {
    flex: 1;
    display: flex;
    flex-direction: column;
}

.message-list {
    flex: 1;
    overflow-y: auto;
    padding: 20px;
    background: #f5f7fa;
}

.message-item {
    display: flex;
    gap: 12px;
    margin-bottom: 20px;
    max-width: 85%;
}

.message-item.assistant {
    align-self: flex-start;
}

.message-item.user {
    flex-direction: row-reverse;
    align-self: flex-end;
    margin-left: auto;
}

.message-avatar {
    flex-shrink: 0;
}

.message-bubble {
    background: #fff;
    padding: 12px 16px;
    border-radius: 8px;
    box-shadow: 0 1px 3px rgba(0, 0, 0, 0.08);
    line-height: 1.7;
    font-size: 14px;
    color: #303133;
}

.message-item.user .message-bubble {
    background: #409eff;
    color: #fff;
}

.message-sources {
    margin-top: 8px;
    font-size: 12px;
}

.sources-label {
    color: #909399;
    margin-right: 4px;
}

.message-feedback {
    margin-top: 6px;
    display: flex;
    gap: 4px;
    opacity: 0;
    transition: opacity 0.2s;
}

.message-item:hover .message-feedback {
    opacity: 1;
}

.thinking {
    color: #909399;
}

.thinking-dots {
    font-size: 14px;
}

.dot-animation span {
    animation: dot-blink 1.4s infinite;
    opacity: 0;
}

.dot-animation span:nth-child(2) {
    animation-delay: 0.2s;
}

.dot-animation span:nth-child(3) {
    animation-delay: 0.4s;
}

@keyframes dot-blink {
    0%, 60%, 100% { opacity: 0; }
    30% { opacity: 1; }
}

/* 输入区域 */
.input-area {
    padding: 16px 20px;
    border-top: 1px solid #e4e7ed;
    background: #fff;
}

.input-actions {
    display: flex;
    align-items: center;
    justify-content: space-between;
    margin-top: 8px;
}

.input-tip {
    font-size: 12px;
    color: #909399;
}

/* Markdown 样式（marked + highlight.js） */
.message-text :deep(pre) {
    background: #f6f8fa;
    border: 1px solid #e4e7ed;
    border-radius: 6px;
    padding: 16px;
    overflow-x: auto;
    font-size: 13px;
    line-height: 1.6;
    margin: 8px 0;
}

.message-text :deep(pre code) {
    background: none;
    padding: 0;
    border-radius: 0;
    color: inherit;
    font-size: inherit;
}

.message-text :deep(code) {
    background: #f0f2f5;
    padding: 2px 6px;
    border-radius: 3px;
    font-size: 13px;
    color: #d14;
}

.message-item.user .message-text :deep(code) {
    background: rgba(255, 255, 255, 0.2);
    color: #fff;
}

/* 表格支持 */
.message-text :deep(table) {
    border-collapse: collapse;
    width: 100%;
    margin: 8px 0;
    font-size: 13px;
}

.message-text :deep(th),
.message-text :deep(td) {
    border: 1px solid #e4e7ed;
    padding: 8px 12px;
    text-align: left;
}

.message-text :deep(th) {
    background: #f5f7fa;
    font-weight: 600;
}

.message-text :deep(blockquote) {
    border-left: 4px solid #409eff;
    margin: 8px 0;
    padding: 8px 16px;
    background: #f0f7ff;
    color: #606266;
    border-radius: 0 4px 4px 0;
}

.message-text :deep(ul),
.message-text :deep(ol) {
    margin: 4px 0;
    padding-left: 20px;
}

.message-text :deep(li) {
    margin: 2px 0;
}
</style>
