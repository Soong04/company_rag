<template>
    <div class="knowledge-page">
        <el-tabs v-model="activeTab" class="page-tabs">
            <!-- 标签1：文档列表 -->
            <el-tab-pane label="文档列表" name="documents">
                <div class="toolbar">
                    <el-button type="primary" @click="openUploadDialog">
                        <el-icon><Upload /></el-icon>上传文档
                    </el-button>
                    <el-select
                        v-model="filterCategory"
                        placeholder="筛选分类"
                        clearable
                        style="width: 160px"
                    >
                        <el-option
                            v-for="cat in categoryTree"
                            :key="cat.id"
                            :label="cat.name"
                            :value="cat.id"
                        />
                    </el-select>
                    <el-input
                        v-model="filterKeyword"
                        placeholder="搜索文档标题..."
                        clearable
                        style="width: 220px"
                        @clear="fetchDocuments"
                    >
                        <template #prefix>
                            <el-icon><Search /></el-icon>
                        </template>
                    </el-input>
                    <el-button @click="fetchDocuments">搜索</el-button>
                </div>

                <el-table :data="docList" stripe style="width: 100%" v-loading="docLoading">
                    <el-table-column prop="id" label="ID" width="60" />
                    <el-table-column prop="title" label="文档标题" min-width="200" show-overflow-tooltip />
                    <el-table-column prop="category_name" label="分类" width="120" />
                    <el-table-column prop="file_type" label="格式" width="80">
                        <template #default="{ row }">
                            <el-tag size="small">.{{ row.file_type }}</el-tag>
                        </template>
                    </el-table-column>
                    <el-table-column prop="file_size" label="大小" width="100">
                        <template #default="{ row }">
                            {{ formatFileSize(row.file_size) }}
                        </template>
                    </el-table-column>
                    <el-table-column prop="status" label="状态" width="100">
                        <template #default="{ row }">
                            <el-tag :type="getDocStatusType(row.status)" size="small">
                                {{ getDocStatusText(row.status) }}
                            </el-tag>
                        </template>
                    </el-table-column>
                    <el-table-column prop="chunk_count" label="分块数" width="80" />
                    <el-table-column prop="uploader_name" label="上传者" width="100" />
                    <el-table-column prop="create_time" label="创建时间" width="170" />
                    <el-table-column label="操作" width="240" fixed="right">
                        <template #default="{ row }">
                            <el-button text size="small" type="primary" @click="previewDoc(row)">
                                预览
                            </el-button>
                            <el-button
                                v-if="row.file_type === 'pdf'"
                                text
                                size="small"
                                type="primary"
                                @click="openPdf(row)"
                            >
                                打开PDF
                            </el-button>
                            <el-button
                                v-if="row.status === -1"
                                text
                                size="small"
                                type="warning"
                                :loading="revectorizingId === row.id"
                                @click="handleRevectorize(row)"
                            >
                                {{ revectorizingId === row.id ? '处理中' : '重新处理' }}
                            </el-button>
                            <el-popconfirm
                                title="确定删除此文档？"
                                @confirm="handleDeleteDoc(row.id)"
                            >
                                <template #reference>
                                    <el-button text size="small" type="danger">删除</el-button>
                                </template>
                            </el-popconfirm>
                        </template>
                    </el-table-column>
                </el-table>

                <div class="pagination-wrap">
                    <el-pagination
                        v-model:current-page="docPage"
                        v-model:page-size="docSize"
                        :total="docTotal"
                        layout="total, prev, pager, next"
                        @current-change="fetchDocuments"
                    />
                </div>
            </el-tab-pane>

            <!-- 标签2：分类管理 -->
            <el-tab-pane label="分类管理" name="categories">
                <div class="toolbar">
                    <el-button type="primary" @click="showCategoryDialog = true">
                        <el-icon><Plus /></el-icon>新增分类
                    </el-button>
                </div>
                <el-table :data="categoryTree" row-key="id" stripe default-expand-all>
                    <el-table-column label="分类名称" min-width="160">
                        <template #default="{ row }">
                            <el-link
                                type="primary"
                                :underline="false"
                                :disabled="!docCountByCategory[row.id]"
                                @click="viewCategoryDocs(row)"
                            >
                                {{ row.name }}
                            </el-link>
                        </template>
                    </el-table-column>
                    <el-table-column label="文档数量" width="100" align="center">
                        <template #default="{ row }">
                            <el-tag size="small" :type="docCountByCategory[row.id] > 0 ? 'primary' : 'info'">
                                {{ docCountByCategory[row.id] || 0 }}
                            </el-tag>
                        </template>
                    </el-table-column>
                    <el-table-column prop="description" label="描述" min-width="200" show-overflow-tooltip />
                    <el-table-column prop="sort_order" label="排序" width="70" />
                    <el-table-column label="操作" width="200" fixed="right">
                        <template #default="{ row }">
                            <el-button text size="small" type="primary" @click="editCategory(row)">
                                编辑
                            </el-button>
                            <el-popconfirm
                                title="确定删除此分类？"
                                @confirm="handleDeleteCategory(row.id)"
                            >
                                <template #reference>
                                    <el-button text size="small" type="danger">删除</el-button>
                                </template>
                            </el-popconfirm>
                        </template>
                    </el-table-column>
                </el-table>
            </el-tab-pane>
        </el-tabs>

        <!-- 上传文档对话框 -->
        <el-dialog v-model="showUploadDialog" title="上传文档" width="520px">
            <el-form :model="uploadForm" label-width="80px">
                <el-form-item label="文档标题">
                    <el-input v-model="uploadForm.title" placeholder="留空则使用文件名" />
                </el-form-item>
                <el-form-item label="文档分类">
                    <el-select v-model="uploadForm.category_id" placeholder="请选择分类" style="width: 100%">
                        <el-option
                            v-for="cat in flatCategories"
                            :key="cat.id"
                            :label="cat.name"
                            :value="cat.id"
                        />
                    </el-select>
                </el-form-item>
                <el-form-item label="选择文件">
                    <el-upload
                        ref="uploadRef"
                        :auto-upload="false"
                        multiple
                        :on-change="handleFileChange"
                        :on-remove="handleFileRemove"
                        accept=".pdf,.docx,.doc,.txt,.md"
                    >
                        <template #trigger>
                            <el-button type="primary">选择文件</el-button>
                        </template>
                        <template #tip>
                            <span style="font-size: 12px; color: #909399">
                                支持 PDF、DOCX、TXT、MD 格式，最大 50MB，可多选
                            </span>
                        </template>
                    </el-upload>
                </el-form-item>
            </el-form>
            <div v-if="selectedFiles.length" class="upload-file-list">
                <div v-for="(f, i) in selectedFiles" :key="i" class="upload-file-item">
                    <span>{{ f.name }}</span>
                    <el-tag v-if="f.uploaded === true" type="success" size="small">已完成</el-tag>
                    <el-tag v-else-if="f.uploaded === false" type="danger" size="small">失败</el-tag>
                    <el-tag v-else-if="f.uploading" type="warning" size="small">上传中</el-tag>
                </div>
            </div>
            <template #footer>
                <el-button @click="cancelUpload">取消</el-button>
                <el-button type="primary" :loading="uploading" @click="handleUpload">
                    {{ uploading ? `上传中 ${uploadProgress}/${selectedFiles.length}` : '确认上传' }}
                </el-button>
            </template>
        </el-dialog>

        <!-- 新增/编辑分类对话框 -->
        <el-dialog v-model="showCategoryDialog" :title="categoryForm.id ? '编辑分类' : '新增分类'" width="450px">
            <el-form :model="categoryForm" label-width="80px">
                <el-form-item label="分类名称">
                    <el-input v-model="categoryForm.name" placeholder="请输入分类名称" />
                </el-form-item>
                <el-form-item label="上级分类">
                    <el-select
                        v-model="categoryForm.parent_id"
                        placeholder="顶级分类"
                        clearable
                        style="width: 100%"
                    >
                        <el-option label="顶级分类" :value="0" />
                        <el-option
                            v-for="cat in topCategories"
                            :key="cat.id"
                            :label="cat.name"
                            :value="cat.id"
                            :disabled="cat.id === categoryForm.id"
                        />
                    </el-select>
                </el-form-item>
                <el-form-item label="排序">
                    <el-input-number v-model="categoryForm.sort_order" :min="0" :max="999" />
                </el-form-item>
                <el-form-item label="描述">
                    <el-input
                        v-model="categoryForm.description"
                        type="textarea"
                        :rows="3"
                        placeholder="请输入分类描述"
                    />
                </el-form-item>
            </el-form>
            <template #footer>
                <el-button @click="showCategoryDialog = false">取消</el-button>
                <el-button type="primary" @click="handleSaveCategory">
                    {{ categoryForm.id ? '保存' : '创建' }}
                </el-button>
            </template>
        </el-dialog>

        <!-- 文档预览对话框 -->
        <el-dialog v-model="showPreview" :title="previewData?.title || '文档预览'" width="750px" top="3vh">
            <template v-if="previewData">
                <div class="preview-meta">
                    <el-tag size="small" type="info">.{{ previewData.file_type }}</el-tag>
                    <span>{{ formatFileSize(previewData.file_size) }}</span>
                    <span>{{ previewData.category_name }}</span>
                    <span>{{ previewData.create_time }}</span>
                    <el-button
                        v-if="previewData.file_type === 'pdf'"
                        text
                        type="primary"
                        size="small"
                        @click="openPdfById(previewData.id)"
                    >
                        <el-icon><Download /></el-icon> 打开原始PDF
                    </el-button>
                </div>
                <div class="preview-content" v-if="previewData.content">
                    {{ previewData.content }}
                </div>
                <el-empty v-else description="暂无文本内容可预览" />
            </template>
        </el-dialog>
    </div>
</template>

<script setup>
import { ref, reactive, computed, watch, onMounted, onUnmounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import {
    getDocuments,
    deleteDocument,
    getCategories,
    createCategory,
    updateCategory,
    deleteCategory,
    uploadDocument,
    previewDocument,
    revectorizeDocument,
    getDocumentFileUrl,
} from '@/api/knowledge'
import { formatFileSize, getDocStatusText, getDocStatusType } from '@/utils'

const activeTab = ref('documents')
const route = useRoute()
const router = useRouter()

// ====== 文档管理 ======
const docList = ref([])
const docLoading = ref(false)
const docPage = ref(1)
const docSize = ref(10)
const docTotal = ref(0)
const filterCategory = ref(null)
const filterKeyword = ref('')

const showUploadDialog = ref(false)
const showPreview = ref(false)
const previewData = ref(null)
const previewLoading = ref(false)
const uploadRef = ref(null)
const uploadForm = reactive({
    category_id: null,
    title: '',
})
const uploading = ref(false)
const uploadProgress = ref(0)

const selectedFiles = ref([])

function openUploadDialog() {
    resetUploadForm()
    showUploadDialog.value = true
}

function cancelUpload() {
    resetUploadForm()
    showUploadDialog.value = false
}

function resetUploadForm() {
    selectedFiles.value = []
    uploadForm.category_id = null
    uploadForm.title = ''
    // 清除 el-upload 内部维护的文件列表
    if (uploadRef.value) {
        uploadRef.value.clearFiles()
    }
}

// ====== 重新向量化 ======
const revectorizingId = ref(null)

async function handleRevectorize(row) {
    try {
        revectorizingId.value = row.id
        const res = await revectorizeDocument(row.id)
        if (res.code === 200) {
            ElMessage.success('已重新提交向量化任务')
            row.status = 1  // 改为处理中
            fetchDocuments()
            startPolling()
        } else {
            ElMessage.error(res.message || '操作失败')
        }
    } catch (err) {
        ElMessage.error('请求失败: ' + (err.message || ''))
    } finally {
        revectorizingId.value = null
    }
}

// ====== 处理状态自动轮询 ======
const processingDocIds = ref(new Set())
let pollTimer = null
const POLL_INTERVAL = 5000  // 5 秒
const MAX_POLL_TIME = 300000  // 最多轮询 5 分钟

function startPolling() {
    // 检查列表中是否还有处理中的文档
    const hasProcessing = docList.value.some(d => d.status === 1)
    if (!hasProcessing) {
        stopPolling()
        return
    }

    if (pollTimer) return  // 已在轮询中

    const startTime = Date.now()
    pollTimer = setInterval(async () => {
        // 超时保护
        if (Date.now() - startTime > MAX_POLL_TIME) {
            stopPolling()
            return
        }

        // 重新获取文档列表
        try {
            const params = { page: docPage.value, size: docSize.value }
            if (filterCategory.value) params.category_id = filterCategory.value
            if (filterKeyword.value) params.keyword = filterKeyword.value
            const res = await getDocuments(params)
            if (res.code === 200) {
                docList.value = res.data.list
                docTotal.value = res.data.total

                // 检查是否还有处理中的文档
                const stillProcessing = res.data.list.some(d => d.status === 1)
                if (!stillProcessing) {
                    stopPolling()
                }
            }
        } catch (err) {
            // 单次轮询失败不影响继续
            console.warn('[轮询] 获取文档状态失败:', err)
        }
    }, POLL_INTERVAL)
}

function stopPolling() {
    if (pollTimer) {
        clearInterval(pollTimer)
        pollTimer = null
    }
}

// ====== 分类管理 ======
const categoryTree = ref([])
const showCategoryDialog = ref(false)
const categoryForm = reactive({
    id: null,
    name: '',
    parent_id: 0,
    sort_order: 0,
    description: '',
})

const topCategories = computed(() =>
    categoryTree.value.filter((c) => c.parent_id === 0)
)

const docCountByCategory = computed(() => {
    const counts = {}
    for (const doc of docList.value) {
        const catId = doc.category_id
        counts[catId] = (counts[catId] || 0) + 1
    }
    return counts
})

const flatCategories = computed(() => {
    const result = []
    function flatten(list, prefix = '') {
        list.forEach((item) => {
            result.push({ ...item, name: prefix + item.name })
            if (item.children) flatten(item.children, prefix + '  ')
        })
    }
    flatten(categoryTree.value)
    return result
})

async function fetchDocuments() {
    docLoading.value = true
    try {
        const params = {
            page: docPage.value,
            size: docSize.value,
        }
        if (filterCategory.value) params.category_id = filterCategory.value
        if (filterKeyword.value) params.keyword = filterKeyword.value

        const res = await getDocuments(params)
        if (res.code === 200) {
            docList.value = res.data.list
            docTotal.value = res.data.total
            // 如果有处理中的文档，自动启动轮询
            if (res.data.list.some(d => d.status === 1)) {
                startPolling()
            }
        }
    } catch (err) {
        console.error('获取文档列表失败:', err)
    } finally {
        docLoading.value = false
    }
}

function viewCategoryDocs(category) {
    router.push({ path: '/admin/documents', query: { category_id: category.id } })
}

async function fetchCategories() {
    try {
        const res = await getCategories()
        if (res.code === 200) {
            categoryTree.value = res.data
        }
    } catch (err) {
        console.error('获取分类失败:', err)
    }
}

function handleFileChange(file) {
    const exists = selectedFiles.value.find(f => f.uid === file.uid)
    if (!exists) {
        // 选择第一个文件时自动填入文件名作为标题
        if (!uploadForm.title && selectedFiles.value.length === 0) {
            const name = file.name || ''
            uploadForm.title = name.replace(/\.(pdf|docx|txt|md)$/i, '')
        }
        selectedFiles.value.push({
            uid: file.uid,
            name: file.name,
            raw: file.raw,
            uploading: false,
            uploaded: null,
        })
    }
}

function handleFileRemove(file) {
    selectedFiles.value = selectedFiles.value.filter(f => f.uid !== file.uid)
}

async function handleUpload() {
    if (!uploadForm.category_id) {
        ElMessage.warning('请选择分类')
        return
    }
    if (!selectedFiles.value.length) {
        ElMessage.warning('请选择文件')
        return
    }

    uploading.value = true
    uploadProgress.value = 0
    let successCount = 0
    let failCount = 0

    for (const file of selectedFiles.value) {
        if (file.uploaded === true) {
            uploadProgress.value++
            continue
        }
        file.uploading = true
        try {
            const formData = new FormData()
            formData.append('file', file.raw)
            formData.append('category_id', uploadForm.category_id)
            if (uploadForm.title) {
                formData.append('title', uploadForm.title)
            }
            const res = await uploadDocument(formData)
            if (res.code === 200) {
                file.uploaded = true
                successCount++
            } else {
                file.uploaded = false
                failCount++
            }
        } catch (err) {
            file.uploaded = false
            failCount++
        } finally {
            file.uploading = false
            uploadProgress.value++
        }
    }

    uploading.value = false
    if (successCount > 0) {
        ElMessage.success(`上传完成：成功 ${successCount} 个${failCount > 0 ? `，失败 ${failCount} 个` : ''}`)
        showUploadDialog.value = false
        uploadForm.category_id = null
        uploadForm.title = ''
        selectedFiles.value = []
        fetchDocuments()
        // 启动轮询，跟踪处理进度
        startPolling()
    } else {
        ElMessage.error('全部上传失败')
    }
}

async function handleDeleteDoc(id) {
    try {
        const res = await deleteDocument(id)
        if (res.code === 200) {
            ElMessage.success('删除成功')
            fetchDocuments()
            // 检查是否还有处理中的文档
            if (!docList.value.some(d => d.status === 1)) {
                stopPolling()
            }
        }
    } catch (err) {
        console.error('删除失败:', err)
    }
}

async function previewDoc(row) {
    previewLoading.value = true
    showPreview.value = true
    previewData.value = null
    try {
        const res = await previewDocument(row.id)
        if (res.code === 200) {
            previewData.value = res.data
        }
    } catch (err) {
        console.error('获取预览失败:', err)
        previewData.value = { ...row, content: '' }
    } finally {
        previewLoading.value = false
    }
}

function openPdf(row) {
    window.open(getDocumentFileUrl(row.id), '_blank')
}

function openPdfById(id) {
    window.open(getDocumentFileUrl(id), '_blank')
}

// ====== 分类操作 ======
function editCategory(row) {
    categoryForm.id = row.id
    categoryForm.name = row.name
    categoryForm.parent_id = row.parent_id
    categoryForm.sort_order = row.sort_order
    categoryForm.description = row.description || ''
    showCategoryDialog.value = true
}

function resetCategoryForm() {
    categoryForm.id = null
    categoryForm.name = ''
    categoryForm.parent_id = 0
    categoryForm.sort_order = 0
    categoryForm.description = ''
}

async function handleSaveCategory() {
    if (!categoryForm.name) {
        ElMessage.warning('请输入分类名称')
        return
    }
    try {
        let res
        if (categoryForm.id) {
            res = await updateCategory(categoryForm.id, { ...categoryForm })
        } else {
            res = await createCategory({ ...categoryForm })
        }
        if (res.code === 200) {
            ElMessage.success(categoryForm.id ? '更新成功' : '创建成功')
            showCategoryDialog.value = false
            resetCategoryForm()
            fetchCategories()
        }
    } catch (err) {
        console.error('保存分类失败:', err)
    }
}

async function handleDeleteCategory(id) {
    try {
        const res = await deleteCategory(id)
        if (res.code === 200) {
            ElMessage.success('删除成功')
            fetchCategories()
        } else {
            ElMessage.error(res.message || '删除失败')
        }
    } catch (err) {
        console.error('删除分类失败:', err)
    }
}

// ⚠️ watch 必须在所有 ref 和函数声明之后注册（immediate 会在 setup 阶段立即执行）
watch(
    () => route.fullPath,
    (fullPath) => {
        if (fullPath.includes('/categories')) {
            activeTab.value = 'categories'
            fetchCategories()
        } else if (fullPath.includes('/documents')) {
            activeTab.value = 'documents'
            const catId = route.query.category_id
            filterCategory.value = catId ? Number(catId) : null
            docPage.value = 1
            fetchDocuments()
        }
    },
    { immediate: true }
)

onMounted(() => {
    fetchDocuments()
    fetchCategories()
})

onUnmounted(() => {
    stopPolling()
})
</script>

<style scoped>
.knowledge-page {
    max-width: 1400px;
    margin: 0 auto;
}

.page-tabs {
    background: #fff;
    padding: 16px 20px;
    border-radius: 8px;
    box-shadow: 0 1px 4px rgba(0, 0, 0, 0.06);
}

.toolbar {
    display: flex;
    align-items: center;
    gap: 12px;
    margin-bottom: 16px;
    flex-wrap: wrap;
}

.pagination-wrap {
    display: flex;
    justify-content: flex-end;
    margin-top: 16px;
}

.upload-file-list {
    padding: 0 10px 10px;
    max-height: 200px;
    overflow-y: auto;
}

.upload-file-item {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 6px 0;
    font-size: 13px;
    border-bottom: 1px solid #f0f0f0;
}

.upload-file-item:last-child {
    border-bottom: none;
}

.preview-meta {
    display: flex;
    align-items: center;
    gap: 12px;
    font-size: 13px;
    color: #909399;
    margin-bottom: 16px;
    padding-bottom: 12px;
    border-bottom: 1px solid #e4e7ed;
    flex-wrap: wrap;
}

.preview-content {
    white-space: pre-wrap;
    font-size: 14px;
    line-height: 1.8;
    color: #303133;
    max-height: 65vh;
    overflow-y: auto;
    background: #fafafa;
    padding: 16px;
    border-radius: 6px;
    border: 1px solid #e4e7ed;
}
</style>
