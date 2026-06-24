<template>
    <div class="user-manage">
        <!-- 工具栏 -->
        <div class="toolbar">
            <el-button type="primary" @click="showAddDialog = true">
                <el-icon><Plus /></el-icon>新增用户
            </el-button>
            <el-input
                v-model="searchKeyword"
                placeholder="搜索用户名/姓名/邮箱..."
                clearable
                style="width: 260px"
                @clear="fetchUsers"
                @keyup.enter="fetchUsers"
            >
                <template #prefix>
                    <el-icon><Search /></el-icon>
                </template>
            </el-input>
            <el-button @click="fetchUsers">搜索</el-button>
        </div>

        <!-- 用户列表 -->
        <el-table :data="userList" stripe v-loading="loading" style="width: 100%">
            <el-table-column prop="id" label="ID" width="60" />
            <el-table-column prop="username" label="用户名" width="120" />
            <el-table-column prop="real_name" label="姓名" width="120" />
            <el-table-column prop="email" label="邮箱" min-width="180" show-overflow-tooltip />
            <el-table-column prop="phone" label="手机号" width="130" />
            <el-table-column prop="role" label="角色" width="100">
                <template #default="{ row }">
                    <el-tag :type="row.role === 'admin' ? 'danger' : 'primary'" size="small">
                        {{ row.role === 'admin' ? '管理员' : '普通用户' }}
                    </el-tag>
                </template>
            </el-table-column>
            <el-table-column prop="status" label="状态" width="80">
                <template #default="{ row }">
                    <el-tag :type="row.status === 1 ? 'success' : 'info'" size="small">
                        {{ row.status === 1 ? '启用' : '禁用' }}
                    </el-tag>
                </template>
            </el-table-column>
            <el-table-column prop="last_login_time" label="最后登录" width="170" />
            <el-table-column prop="create_time" label="创建时间" width="170" />
            <el-table-column label="操作" width="200" fixed="right">
                <template #default="{ row }">
                    <el-button text size="small" type="primary" @click="editUser(row)">
                        编辑
                    </el-button>
                    <el-popconfirm
                        :title="row.status === 1 ? '确定禁用此用户？' : '确定启用此用户？'"
                        @confirm="handleToggleStatus(row)"
                    >
                        <template #reference>
                            <el-button text size="small" :type="row.status === 1 ? 'warning' : 'success'">
                                {{ row.status === 1 ? '禁用' : '启用' }}
                            </el-button>
                        </template>
                    </el-popconfirm>
                </template>
            </el-table-column>
        </el-table>

        <!-- 分页 -->
        <div class="pagination-wrap">
            <el-pagination
                v-model:current-page="page"
                v-model:page-size="size"
                :total="total"
                layout="total, prev, pager, next"
                @current-change="fetchUsers"
            />
        </div>

        <!-- 新增/编辑用户对话框 -->
        <el-dialog
            v-model="showDialog"
            :title="isEditing ? '编辑用户' : '新增用户'"
            width="500px"
        >
            <el-form :model="form" label-width="100px">
                <el-form-item label="用户名" required>
                    <el-input v-model="form.username" :disabled="isEditing" placeholder="请输入用户名" />
                </el-form-item>
                <el-form-item v-if="!isEditing" label="密码" required>
                    <el-input v-model="form.password" type="password" placeholder="请输入密码" show-password />
                </el-form-item>
                <el-form-item label="真实姓名">
                    <el-input v-model="form.real_name" placeholder="请输入真实姓名" />
                </el-form-item>
                <el-form-item label="邮箱">
                    <el-input v-model="form.email" placeholder="请输入邮箱" />
                </el-form-item>
                <el-form-item label="手机号">
                    <el-input v-model="form.phone" placeholder="请输入手机号" />
                </el-form-item>
                <el-form-item label="角色">
                    <el-select v-model="form.role" style="width: 100%">
                        <el-option label="管理员" value="admin" />
                        <el-option label="普通用户" value="user" />
                    </el-select>
                </el-form-item>
                <el-form-item label="状态">
                    <el-switch v-model="form.status" :active-value="1" :inactive-value="0" active-text="启用" inactive-text="禁用" />
                </el-form-item>
            </el-form>
            <template #footer>
                <el-button @click="showDialog = false">取消</el-button>
                <el-button type="primary" :loading="saving" @click="handleSave">
                    {{ isEditing ? '保存' : '创建' }}
                </el-button>
            </template>
        </el-dialog>
    </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { Plus, Search } from '@element-plus/icons-vue'
import { getUsers, updateUser, toggleUserStatus, createUser } from '@/api/admin'

const userList = ref([])
const loading = ref(false)
const page = ref(1)
const size = ref(20)
const total = ref(0)
const searchKeyword = ref('')

const showDialog = ref(false)
const saving = ref(false)
const isEditing = computed(() => !!form.id)

const emptyForm = () => ({
    id: null,
    username: '',
    password: '',
    real_name: '',
    email: '',
    phone: '',
    role: 'user',
    status: 1,
})

const form = reactive(emptyForm())

async function fetchUsers() {
    loading.value = true
    try {
        const params = { page: page.value, size: size.value }
        if (searchKeyword.value) params.keyword = searchKeyword.value
        const res = await getUsers(params)
        if (res.code === 200) {
            userList.value = res.data.list
            total.value = res.data.total
        }
    } catch (err) {
        console.error('获取用户列表失败:', err)
    } finally {
        loading.value = false
    }
}

function editUser(row) {
    form.id = row.id
    form.username = row.username
    form.password = ''
    form.real_name = row.real_name || ''
    form.email = row.email || ''
    form.phone = row.phone || ''
    form.role = row.role
    form.status = row.status
    showDialog.value = true
}

function resetForm() {
    Object.assign(form, emptyForm())
}

async function handleSave() {
    if (!form.username) {
        ElMessage.warning('请输入用户名')
        return
    }
    if (!isEditing.value && !form.password) {
        ElMessage.warning('请输入密码')
        return
    }

    saving.value = true
    try {
        let res
        if (isEditing.value) {
            // 编辑：调用 updateUser（不含密码）
            const data = {
                real_name: form.real_name,
                email: form.email,
                phone: form.phone,
                role: form.role,
                status: form.status,
            }
            res = await updateUser(form.id, data)
        } else {
            // 新增：调用 createUser
            res = await createUser({
                username: form.username,
                password: form.password,
                real_name: form.real_name,
                email: form.email,
                phone: form.phone,
                role: form.role,
                status: form.status,
            })
        }
        if (res.code === 200) {
            ElMessage.success(isEditing.value ? '更新成功' : '创建成功')
            showDialog.value = false
            resetForm()
            fetchUsers()
        } else {
            ElMessage.error(res.message || '操作失败')
        }
    } catch (err) {
        console.error('保存用户失败:', err)
    } finally {
        saving.value = false
    }
}

async function handleToggleStatus(row) {
    try {
        const res = await toggleUserStatus(row.id)
        if (res.code === 200) {
            ElMessage.success(res.message || '操作成功')
            fetchUsers()
        }
    } catch (err) {
        console.error('切换状态失败:', err)
    }
}

onMounted(() => {
    fetchUsers()
})
</script>

<style scoped>
.user-manage {
    max-width: 1400px;
    margin: 0 auto;
}

.toolbar {
    display: flex;
    align-items: center;
    gap: 12px;
    margin-bottom: 16px;
    flex-wrap: wrap;
    background: #fff;
    padding: 16px 20px;
    border-radius: 8px;
    box-shadow: 0 1px 4px rgba(0, 0, 0, 0.06);
}

.pagination-wrap {
    display: flex;
    justify-content: flex-end;
    margin-top: 16px;
    background: #fff;
    padding: 12px 20px;
    border-radius: 8px;
    box-shadow: 0 1px 4px rgba(0, 0, 0, 0.06);
}
</style>
