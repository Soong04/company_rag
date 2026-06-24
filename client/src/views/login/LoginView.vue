<template>
    <div class="login-container">
        <ParticleBackground />

        <div class="login-card-wrapper">
            <div class="login-card">
                <div class="login-header">
                    <div class="logo-icon">
                        <el-icon :size="36" color="#6366f1"><Reading /></el-icon>
                    </div>
                    <h2 class="login-title">企业知识库问答系统</h2>
                    <p class="login-subtitle">Enterprise QA RAG System</p>
                </div>

                <el-form
                    ref="formRef"
                    :model="loginForm"
                    :rules="rules"
                    class="login-form"
                    @keyup.enter="handleLogin"
                >
                    <el-form-item prop="username">
                        <el-input
                            v-model="loginForm.username"
                            placeholder="请输入用户名"
                            :prefix-icon="User"
                            size="large"
                        />
                    </el-form-item>

                    <el-form-item prop="password">
                        <el-input
                            v-model="loginForm.password"
                            type="password"
                            placeholder="请输入密码"
                            :prefix-icon="Lock"
                            size="large"
                            show-password
                        />
                    </el-form-item>

                    <el-form-item>
                        <el-button
                            type="primary"
                            size="large"
                            class="login-btn"
                            :loading="loading"
                            @click="handleLogin"
                        >
                            {{ loading ? '登录中...' : '登 录' }}
                        </el-button>
                    </el-form-item>
                </el-form>

                <div class="login-footer">
                    <p class="test-accounts">
                        测试账号：admin / 123456（管理员）
                    </p>
                </div>
            </div>

            <p class="login-copyright">© 2026 Enterprise QA RAG System</p>
        </div>
    </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { User, Lock } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import { login } from '@/api/auth'
import { useUserStore } from '@/store/user'
import ParticleBackground from '@/components/ParticleBackground.vue'

const router = useRouter()
const userStore = useUserStore()

const formRef = ref(null)
const loading = ref(false)

const loginForm = reactive({
    username: '',
    password: '',
})

const rules = {
    username: [{ required: true, message: '请输入用户名', trigger: 'blur' }],
    password: [{ required: true, message: '请输入密码', trigger: 'blur' }],
}

async function handleLogin() {
    if (!formRef.value) return

    await formRef.value.validate(async (valid) => {
        if (!valid) return

        loading.value = true
        try {
            const res = await login(loginForm.username, loginForm.password)
            if (res.code === 200) {
                userStore.setUser(res.data.user)
                ElMessage.success('登录成功')

                if (res.data.user.role === 'admin') {
                    router.push('/admin/home')
                } else {
                    router.push('/user/chat')
                }
            } else {
                ElMessage.error(res.message || '登录失败')
            }
        } catch (err) {
            console.error('登录错误:', err)
        } finally {
            loading.value = false
        }
    })
}
</script>

<style scoped>
.login-container {
    position: relative;
    min-height: 100vh;
    display: flex;
    align-items: center;
    justify-content: center;
    background: linear-gradient(135deg, #0f172a 0%, #1e1b4b 50%, #0f172a 100%);
    overflow: hidden;
}

.login-card-wrapper {
    position: relative;
    z-index: 1;
    display: flex;
    flex-direction: column;
    align-items: center;
}

.login-card {
    width: 420px;
    padding: 44px 40px 36px;
    background: rgba(255, 255, 255, 0.97);
    border-radius: 16px;
    box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
    backdrop-filter: blur(12px);
}

.login-header {
    text-align: center;
    margin-bottom: 32px;
}

.logo-icon {
    width: 64px;
    height: 64px;
    margin: 0 auto 16px;
    background: linear-gradient(135deg, #eef2ff, #e0e7ff);
    border-radius: 16px;
    display: flex;
    align-items: center;
    justify-content: center;
}

.login-title {
    font-size: 22px;
    font-weight: 700;
    color: #1e293b;
    margin: 0 0 6px;
    letter-spacing: 1px;
}

.login-subtitle {
    font-size: 13px;
    color: #94a3b8;
    margin: 0;
    letter-spacing: 0.5px;
}

.login-form {
    margin-top: 8px;
}

.login-form :deep(.el-input__wrapper) {
    border-radius: 10px;
    padding: 4px 16px;
}

.login-form :deep(.el-input__inner) {
    height: 44px;
}

.login-btn {
    width: 100%;
    height: 46px;
    border-radius: 10px;
    font-size: 16px;
    letter-spacing: 2px;
    margin-top: 4px;
}

.login-footer {
    text-align: center;
    margin-top: 20px;
    padding-top: 20px;
    border-top: 1px solid #f1f5f9;
}

.test-accounts {
    font-size: 12px;
    color: #94a3b8;
    margin: 0;
    line-height: 1.6;
}

.login-copyright {
    margin-top: 24px;
    font-size: 12px;
    color: rgba(255, 255, 255, 0.4);
    letter-spacing: 0.5px;
}
</style>
