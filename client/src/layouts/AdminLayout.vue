<template>
    <el-container style="height: 100vh">
        <!-- 侧边栏 -->
        <el-aside :width="isCollapse ? '64px' : '220px'" class="admin-aside">
            <div class="logo" @click="handleLogoClick">
                <el-icon :size="28"><Management /></el-icon>
                <span v-show="!isCollapse" class="logo-text">管理后台</span>
            </div>
            <el-menu
                :default-active="activeMenu"
                :collapse="isCollapse"
                :router="true"
                background-color="#001529"
                text-color="#ffffffa6"
                active-text-color="#fff"
            >
                <el-menu-item index="/admin/home">
                    <el-icon><DataAnalysis /></el-icon>
                    <span>首页概览</span>
                </el-menu-item>
                <el-menu-item index="/admin/users">
                    <el-icon><User /></el-icon>
                    <span>用户管理</span>
                </el-menu-item>
                <el-menu-item index="/admin/categories">
                    <el-icon><FolderOpened /></el-icon>
                    <span>分类管理</span>
                </el-menu-item>
                <el-menu-item index="/admin/documents">
                    <el-icon><Document /></el-icon>
                    <span>文档管理</span>
                </el-menu-item>
                <el-menu-item index="/admin/chat">
                    <el-icon><ChatDotRound /></el-icon>
                    <span>智能问答</span>
                </el-menu-item>
                <el-menu-item index="/admin/search">
                    <el-icon><Search /></el-icon>
                    <span>全文搜索</span>
                </el-menu-item>
            </el-menu>
        </el-aside>

        <el-container>
            <!-- 顶部栏 -->
            <el-header class="admin-header">
                <div class="header-left">
                    <el-icon
                        class="collapse-btn"
                        :size="20"
                        @click="isCollapse = !isCollapse"
                    >
                        <Fold v-if="!isCollapse" />
                        <Expand v-else />
                    </el-icon>
                    <span class="page-title">{{ route.meta.title }}</span>
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
            <el-main class="admin-main">
                <router-view />
            </el-main>
        </el-container>
    </el-container>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useUserStore } from '@/store/user'
import { logout as logoutApi } from '@/api/auth'
import { ElMessageBox } from 'element-plus'

const route = useRoute()
const router = useRouter()
const userStore = useUserStore()

const isCollapse = ref(false)

const activeMenu = computed(() => {
    const path = route.path
    if (path.startsWith('/admin/home')) return '/admin/home'
    if (path.startsWith('/admin/users')) return '/admin/users'
    if (path.startsWith('/admin/categories')) return '/admin/categories'
    if (path.startsWith('/admin/documents')) return '/admin/documents'
    if (path.startsWith('/admin/chat')) return '/admin/chat'
    if (path.startsWith('/admin/search')) return '/admin/search'
    return path
})

async function handleCommand(command) {
    if (command === 'profile') {
        router.push('/profile')
    } else if (command === 'logout') {
        await handleLogout()
    }
}

async function handleLogout() {
    try {
        await ElMessageBox.confirm('确定要退出登录吗？', '提示')
        await logoutApi()
        userStore.clearUser()
        router.push('/login')
    } catch {
        // 取消操作
    }
}

function handleLogoClick() {
    router.push('/admin/home')
}
</script>

<style scoped>
.admin-aside {
    background-color: #001529;
    transition: width 0.3s;
    overflow: hidden;
}

.logo {
    height: 60px;
    display: flex;
    align-items: center;
    justify-content: center;
    color: #fff;
    cursor: pointer;
    gap: 8px;
    border-bottom: 1px solid rgba(255, 255, 255, 0.1);
}

.logo-text {
    font-size: 18px;
    font-weight: 600;
    white-space: nowrap;
}

.admin-header {
    background: #fff;
    border-bottom: 1px solid #e4e7ed;
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 0 20px;
    height: 60px;
}

.header-left {
    display: flex;
    align-items: center;
    gap: 12px;
}

.collapse-btn {
    cursor: pointer;
    color: #606266;
}

.page-title {
    font-size: 16px;
    font-weight: 500;
    color: #303133;
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

.admin-main {
    background-color: #f0f2f5;
    padding: 20px;
    overflow-y: auto;
}
</style>
