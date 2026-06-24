<template>
    <div class="profile-page">
        <el-card shadow="hover" class="profile-card">
            <template #header>
                <div class="profile-header">
                    <el-avatar :size="64" icon="UserFilled" style="background: #409eff" />
                    <div class="profile-title">
                        <h2>{{ userStore.user?.real_name || userStore.user?.username }}</h2>
                        <el-tag :type="userStore.user?.role === 'admin' ? 'danger' : 'primary'" size="small">
                            {{ userStore.user?.role === 'admin' ? '管理员' : '普通用户' }}
                        </el-tag>
                    </div>
                </div>
            </template>

            <el-descriptions :column="1" border>
                <el-descriptions-item label="用户名">
                    {{ userStore.user?.username }}
                </el-descriptions-item>
                <el-descriptions-item label="真实姓名">
                    {{ userStore.user?.real_name || '-' }}
                </el-descriptions-item>
                <el-descriptions-item label="邮箱">
                    {{ userStore.user?.email || '-' }}
                </el-descriptions-item>
                <el-descriptions-item label="手机号">
                    {{ userStore.user?.phone || '-' }}
                </el-descriptions-item>
                <el-descriptions-item label="角色">
                    <el-tag :type="userStore.user?.role === 'admin' ? 'danger' : 'primary'" size="small">
                        {{ userStore.user?.role === 'admin' ? '管理员' : '普通用户' }}
                    </el-tag>
                </el-descriptions-item>
                <el-descriptions-item label="账号状态">
                    <el-tag :type="userStore.user?.status === 1 ? 'success' : 'info'" size="small">
                        {{ userStore.user?.status === 1 ? '正常' : '已禁用' }}
                    </el-tag>
                </el-descriptions-item>
                <el-descriptions-item label="最后登录IP">
                    {{ userStore.user?.last_login_ip || '-' }}
                </el-descriptions-item>
                <el-descriptions-item label="最后登录时间">
                    {{ userStore.user?.last_login_time || '-' }}
                </el-descriptions-item>
                <el-descriptions-item label="创建时间">
                    {{ userStore.user?.create_time || '-' }}
                </el-descriptions-item>
            </el-descriptions>
        </el-card>
    </div>
</template>

<script setup>
import { useUserStore } from '@/store/user'
const userStore = useUserStore()
</script>

<style scoped>
.profile-page {
    max-width: 600px;
    margin: 40px auto;
}

.profile-card {
    border-radius: 8px;
}

.profile-header {
    display: flex;
    align-items: center;
    gap: 16px;
}

.profile-title h2 {
    margin: 0 0 4px;
    font-size: 20px;
    color: #303133;
}
</style>
