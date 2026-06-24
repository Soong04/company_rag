<template>
    <div class="admin-home">
        <!-- 统计卡片 -->
        <el-row :gutter="20" class="stats-row">
            <el-col :span="6">
                <el-card shadow="hover" class="stats-card">
                    <div class="stats-item">
                        <div class="stats-icon" style="background: #ecf5ff">
                            <el-icon :size="28" color="#409eff"><UserFilled /></el-icon>
                        </div>
                        <div class="stats-info">
                            <div class="stats-value">{{ dashboardData.user_count }}</div>
                            <div class="stats-label">用户总数</div>
                        </div>
                    </div>
                </el-card>
            </el-col>
            <el-col :span="6">
                <el-card shadow="hover" class="stats-card">
                    <div class="stats-item">
                        <div class="stats-icon" style="background: #f0f9eb">
                            <el-icon :size="28" color="#67c23a"><Document /></el-icon>
                        </div>
                        <div class="stats-info">
                            <div class="stats-value">{{ dashboardData.doc_count }}</div>
                            <div class="stats-label">文档总数</div>
                        </div>
                    </div>
                </el-card>
            </el-col>
            <el-col :span="6">
                <el-card shadow="hover" class="stats-card">
                    <div class="stats-item">
                        <div class="stats-icon" style="background: #fdf6ec">
                            <el-icon :size="28" color="#e6a23c"><ChatDotRound /></el-icon>
                        </div>
                        <div class="stats-info">
                            <div class="stats-value">{{ dashboardData.category_count }}</div>
                            <div class="stats-label">分类数量</div>
                        </div>
                    </div>
                </el-card>
            </el-col>
            <el-col :span="6">
                <el-card shadow="hover" class="stats-card">
                    <div class="stats-item">
                        <div class="stats-icon" style="background: #fef0f0">
                            <el-icon :size="28" color="#f56c6c"><Avatar /></el-icon>
                        </div>
                        <div class="stats-info">
                            <div class="stats-value">{{ dashboardData.active_user_count }}</div>
                            <div class="stats-label">活跃用户</div>
                        </div>
                    </div>
                </el-card>
            </el-col>
        </el-row>

        <!-- 图表区域 -->
        <el-row :gutter="20" class="chart-row">
            <el-col :span="14">
                <el-card shadow="hover">
                    <template #header>
                        <span class="card-title">近7日用户登录趋势</span>
                    </template>
                    <div ref="trendChartRef" style="height: 300px"></div>
                </el-card>
            </el-col>
            <el-col :span="10">
                <el-card shadow="hover">
                    <template #header>
                        <span class="card-title">文档分类分布</span>
                    </template>
                    <div ref="pieChartRef" style="height: 300px"></div>
                </el-card>
            </el-col>
        </el-row>

        <!-- 操作日志表格 -->
        <el-card shadow="hover" class="log-card">
            <template #header>
                <span class="card-title">最近操作日志</span>
            </template>
            <el-table :data="logList" stripe style="width: 100%">
                <el-table-column prop="create_time" label="时间" width="170" />
                <el-table-column prop="username" label="用户" width="120" />
                <el-table-column prop="action" label="操作" width="120">
                    <template #default="{ row }">
                        <el-tag :type="getActionType(row.action)" size="small">
                            {{ getActionText(row.action) }}
                        </el-tag>
                    </template>
                </el-table-column>
                <el-table-column prop="detail" label="详情" min-width="200" />
                <el-table-column prop="ip_address" label="IP地址" width="150" />
            </el-table>
            <div class="pagination-wrap">
                <el-pagination
                    v-model:current-page="logPage"
                    v-model:page-size="logSize"
                    :total="logTotal"
                    small
                    layout="prev, pager, next"
                    @current-change="fetchLogs"
                />
            </div>
        </el-card>
    </div>
</template>

<script setup>
import { ref, reactive, onMounted, nextTick, shallowRef } from 'vue'
import { getDashboard, getStats, getLogs } from '@/api/admin'
import * as echarts from 'echarts'

const dashboardData = reactive({
    user_count: 0,
    active_user_count: 0,
    doc_count: 0,
    category_count: 0,
    category_stats: [],
})

const trendChartRef = ref(null)
const pieChartRef = ref(null)
let trendChart = null
let pieChart = null

const logList = ref([])
const logPage = ref(1)
const logSize = ref(10)
const logTotal = ref(0)

function getActionType(action) {
    const map = { login: 'success', query: 'primary', upload: 'warning', delete: 'danger' }
    return map[action] || 'info'
}

function getActionText(action) {
    const map = { login: '登录', query: '查询', upload: '上传', delete: '删除' }
    return map[action] || action
}

async function fetchDashboard() {
    try {
        const res = await getDashboard()
        if (res.code === 200) {
            Object.assign(dashboardData, res.data)
        }
    } catch (err) {
        console.error('获取统计数据失败:', err)
    }
}

async function fetchTrend() {
    try {
        const res = await getStats()
        if (res.code === 200 && res.data?.login_trend) {
            nextTick(() => initTrendChart(res.data.login_trend))
        }
    } catch (err) {
        console.error('获取趋势数据失败:', err)
    }
}

async function fetchLogs() {
    try {
        const res = await getLogs({ page: logPage.value, size: logSize.value })
        if (res.code === 200) {
            logList.value = res.data.list
            logTotal.value = res.data.total
        }
    } catch (err) {
        console.error('获取日志失败:', err)
    }
}

function initTrendChart(data) {
    if (!trendChartRef.value) return
    if (trendChart) trendChart.dispose()

    trendChart = echarts.init(trendChartRef.value)
    trendChart.setOption({
        tooltip: { trigger: 'axis' },
        grid: { left: 40, right: 20, bottom: 30, top: 20 },
        xAxis: {
            type: 'category',
            data: data.map((d) => d.date),
            axisLabel: { fontSize: 12 },
        },
        yAxis: { type: 'value', minInterval: 1 },
        series: [
            {
                type: 'line',
                data: data.map((d) => d.count),
                smooth: true,
                areaStyle: {
                    color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
                        { offset: 0, color: 'rgba(64,158,255,0.3)' },
                        { offset: 1, color: 'rgba(64,158,255,0.05)' },
                    ]),
                },
                lineStyle: { color: '#409eff', width: 2 },
                itemStyle: { color: '#409eff' },
            },
        ],
    })
}

function initPieChart(data) {
    if (!pieChartRef.value) return
    if (pieChart) pieChart.dispose()

    pieChart = echarts.init(pieChartRef.value)
    pieChart.setOption({
        tooltip: { trigger: 'item', formatter: '{b}: {c} ({d}%)' },
        series: [
            {
                type: 'pie',
                radius: ['40%', '70%'],
                center: ['50%', '50%'],
                label: { formatter: '{b}\n{d}%' },
                data: data.length
                    ? data
                    : [{ name: '暂无数据', value: 1 }],
                emphasis: {
                    itemStyle: { shadowBlur: 10, shadowColor: 'rgba(0,0,0,0.2)' },
                },
            },
        ],
    })
}

onMounted(async () => {
    await fetchDashboard()
    await fetchTrend()
    await fetchLogs()

    nextTick(() => {
        if (dashboardData.category_stats?.length) {
            initPieChart(dashboardData.category_stats)
        }
    })
})
</script>

<style scoped>
.admin-home {
    max-width: 1400px;
    margin: 0 auto;
}

.stats-row {
    margin-bottom: 20px;
}

.stats-card {
    border-radius: 8px;
}

.stats-item {
    display: flex;
    align-items: center;
    gap: 16px;
}

.stats-icon {
    width: 56px;
    height: 56px;
    border-radius: 12px;
    display: flex;
    align-items: center;
    justify-content: center;
}

.stats-value {
    font-size: 28px;
    font-weight: 700;
    color: #303133;
    line-height: 1.2;
}

.stats-label {
    font-size: 14px;
    color: #909399;
    margin-top: 4px;
}

.chart-row {
    margin-bottom: 20px;
}

.card-title {
    font-size: 15px;
    font-weight: 600;
    color: #303133;
}

.log-card {
    border-radius: 8px;
}

.pagination-wrap {
    display: flex;
    justify-content: flex-end;
    margin-top: 16px;
}
</style>
