<template>
  <div class="search-page">
    <!-- 搜索栏 -->
    <div class="search-bar">
      <el-input
        v-model="keyword"
        placeholder="搜索文档内容..."
        size="large"
        clearable
        @keyup.enter="doSearch"
        @clear="clearSearch"
      >
        <template #prefix>
          <el-icon><Search /></el-icon>
        </template>
        <template #append>
          <el-button @click="doSearch" :loading="searching">搜索</el-button>
        </template>
      </el-input>
    </div>

    <!-- 搜索结果 -->
    <div v-if="searched" class="search-results">
      <div class="result-meta">
        搜索 "{{ searchKeyword }}" 共找到 <strong>{{ total }}</strong> 条结果
      </div>

      <div v-loading="searching" class="result-list">
        <div v-for="doc in results" :key="doc.id" class="result-item" @click="viewDoc(doc)">
          <div class="result-title">
            <el-tag size="small" type="info">.{{ doc.file_type }}</el-tag>
            {{ doc.title }}
          </div>
          <div class="result-snippet" v-html="doc.snippet"></div>
          <div class="result-meta-info">
            <span>{{ doc.category_name }}</span>
            <span>{{ formatFileSize(doc.file_size) }}</span>
            <span>{{ doc.create_time }}</span>
          </div>
        </div>

        <el-empty v-if="!results.length && !searching" description="未找到相关内容" />
      </div>

      <div class="pagination-wrap" v-if="total > size">
        <el-pagination
          v-model:current-page="page"
          v-model:page-size="size"
          :total="total"
          layout="prev, pager, next"
          @current-change="doSearch"
        />
      </div>
    </div>

    <!-- 初始提示 -->
    <div v-else class="search-hint">
      <el-empty description="输入关键词搜索文档内容" />
    </div>

    <!-- 文档详情对话框 -->
    <el-dialog v-model="showDetail" :title="currentDoc?.title" width="700px">
      <div v-loading="docLoading" class="doc-content">{{ currentDoc?.content || (docLoading ? '加载中...' : '暂无内容') }}</div>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { Search } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import request from '@/api/request'
import { previewDocument } from '@/api/knowledge'
import { formatFileSize } from '@/utils'

const keyword = ref('')
const searchKeyword = ref('')
const results = ref([])
const total = ref(0)
const page = ref(1)
const size = ref(20)
const searching = ref(false)
const searched = ref(false)
const showDetail = ref(false)
const currentDoc = ref(null)
const docLoading = ref(false)

async function doSearch() {
  const q = keyword.value.trim()
  if (!q) {
    ElMessage.warning('请输入搜索关键词')
    return
  }
  searching.value = true
  searched.value = true
  searchKeyword.value = q
  try {
    const res = await request({
      url: '/knowledge/search',
      method: 'get',
      params: { q, page: page.value, size: size.value },
    })
    if (res.code === 200) {
      results.value = res.data.list
      total.value = res.data.total
    }
  } catch (err) {
    console.error('搜索失败:', err)
  } finally {
    searching.value = false
  }
}

function clearSearch() {
  searched.value = false
  results.value = []
  total.value = 0
  page.value = 1
}

async function viewDoc(doc) {
  currentDoc.value = doc
  showDetail.value = true
  docLoading.value = true
  try {
    const res = await previewDocument(doc.id)
    if (res.code === 200 && res.data?.content) {
      currentDoc.value.content = res.data.content
    }
  } catch (err) {
    console.error('获取文档内容失败:', err)
  } finally {
    docLoading.value = false
  }
}
</script>

<style scoped>
.search-page {
  max-width: 900px;
  margin: 0 auto;
  padding: 20px;
}

.search-bar {
  margin-bottom: 20px;
}

.result-meta {
  font-size: 14px;
  color: #606266;
  margin-bottom: 16px;
  padding-bottom: 12px;
  border-bottom: 1px solid #e4e7ed;
}

.result-list {
  min-height: 200px;
}

.result-item {
  padding: 16px;
  border: 1px solid #e4e7ed;
  border-radius: 8px;
  margin-bottom: 12px;
  cursor: pointer;
  transition: all 0.2s;
  background: #fff;
}

.result-item:hover {
  border-color: #409eff;
  box-shadow: 0 2px 8px rgba(64, 158, 255, 0.12);
}

.result-title {
  font-size: 16px;
  font-weight: 600;
  color: #303133;
  margin-bottom: 8px;
  display: flex;
  align-items: center;
  gap: 8px;
}

.result-snippet {
  font-size: 14px;
  color: #606266;
  line-height: 1.7;
  margin-bottom: 8px;
}

.result-snippet :deep(em) {
  color: #f56c6c;
  font-style: normal;
  background: #fef0f0;
  padding: 0 2px;
  border-radius: 2px;
}

.result-meta-info {
  font-size: 12px;
  color: #909399;
  display: flex;
  gap: 16px;
}

.pagination-wrap {
  display: flex;
  justify-content: center;
  margin-top: 20px;
}

.search-hint {
  margin-top: 60px;
}

.doc-content {
  white-space: pre-wrap;
  font-size: 14px;
  line-height: 1.8;
  color: #303133;
  max-height: 500px;
  overflow-y: auto;
}
</style>
