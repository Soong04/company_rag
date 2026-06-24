<template>
    <el-container style="height: 100vh">
        <!-- 顶部导航 -->
        <el-header class="user-header">
            <div class="header-left">
                <el-icon :size="24" style="color: #409eff"><Reading /></el-icon>
                <span class="app-title">企业知识库问答系统</span>
            </div>
            <div class="header-nav">
                <el-menu
                    :default-active="activeMenu"
                    mode="horizontal"
                    :ellipsis="false"
                    @select="handleMenuSelect"
                >
                    <el-menu-item index="/user/chat">
                        <el-icon><ChatDotRound /></el-icon>
                        <span>智能问答</span>
                    </el-menu-item>
                    <el-menu-item index="/user/knowledge">
                        <el-icon><Folder /></el-icon>
                        <span>知识浏览</span>
                    </el-menu-item>
                    <el-menu-item index="/user/search">
                        <el-icon><Search /></el-icon>
                        <span>全文搜索</span>
                    </el-menu-item>
                </el-menu>
            </div>
            <div class="header-right">
                <el-dropdown trigger="click" @command="handleCommand">
                    <span class="user-info">
                        <el-avatar :size="32" icon="UserFilled" />
                        <span class="username">{{ userStore.user?.real_name || userStore.user?.username }}</span>
                        <el-icon><ArrowDown /></el-icon>
                    </span>
                    <template #dropdown>
                        <el-dropdown-menu>
                            <el-dropdown-item command="profile">
                                <el-icon><User /></el-icon>个人信息
                            </el-dropdown-item>
                            <el-dropdown-item command="logout" divided>
                                <el-icon><SwitchButton /></el-icon>退出登录
                            </el-dropdown-item>
                        </el-dropdown-menu>
                    </template>
                </el-dropdown>
            </div>
        </el-header>

        <!-- 内容区域 -->
        <el-main class="user-main">
            <router-view />
        </el-main>
    </el-container>
</template>

<script setup>
import { computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useUserStore } from '@/store/user'
import { logout as logoutApi } from '@/api/auth'
import { ElMessageBox } from 'element-plus'

const route = useRoute()
const router = useRouter()
const userStore = useUserStore()

const activeMenu = computed(() => {
    const path = route.path
    if (path.startsWith('/user/chat')) return '/user/chat'
    if (path.startsWith('/user/knowledge')) return '/user/knowledge'
    if (path.startsWith('/user/search')) return '/user/search'
    return path
})

function handleMenuSelect(index) {
    router.push(index)
}

async function handleCommand(command) {
    if (command === 'profile') {
        router.push('/profile')
    } else if (command === 'logout') {
        try {
            await ElMessageBox.confirm('确定要退出登录吗？', '提示')
            await logoutApi()
            userStore.clearUser()
            router.push('/login')
        } catch {
            // 取消
        }
    }
}
</script>

<style scoped>
.user-header {
    background: #fff;
    border-bottom: 1px solid #e4e7ed;
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 0 20px;
    height: 60px;
    box-shadow: 0 1px 4px rgba(0, 0, 0, 0.08);
}

.header-left {
    display: flex;
    align-items: center;
    gap: 10px;
}

.app-title {
    font-size: 18px;
    font-weight: 600;
    color: #303133;
}

.header-nav :deep(.el-menu) {
    border-bottom: none;
}

.header-right {
    display: flex;
    align-items: center;
}

.user-info {
    display: flex;
    align-items: center;
    gap: 8px;
    cursor: pointer;
}

.username {
    font-size: 14px;
    color: #303133;
}

.user-main {
    background-color: #f5f7fa;
    padding: 0;
    overflow-y: auto;
}
</style>
