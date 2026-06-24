import { createRouter, createWebHistory } from 'vue-router'
import { useUserStore } from '@/store/user'
import { ElMessage } from 'element-plus'

const routes = [
    // ---- 登录页（所有用户） ----
    {
        path: '/login',
        name: 'Login',
        component: () => import('@/views/login/LoginView.vue'),
        meta: { title: '登录' },
    },

    // ---- 管理员布局（需要 admin 角色） ----
    {
        path: '/admin',
        component: () => import('@/layouts/AdminLayout.vue'),
        meta: { requiresAuth: true, role: 'admin' },
        children: [
            { path: '', redirect: '/admin/home' },
            {
                path: 'home',
                name: 'AdminHome',
                component: () => import('@/views/admin/AdminHome.vue'),
                meta: { title: '首页概览' },
            },
            {
                path: 'users',
                name: 'UserManage',
                component: () => import('@/views/admin/UserManage.vue'),
                meta: { title: '用户管理' },
            },
            {
                path: 'categories',
                name: 'CategoryManage',
                component: () => import('@/views/knowledge/KnowledgeList.vue'),
                meta: { title: '分类管理' },
            },
            {
                path: 'documents',
                name: 'DocManage',
                component: () => import('@/views/knowledge/KnowledgeList.vue'),
                meta: { title: '文档管理' },
            },
            {
                path: 'chat',
                name: 'AdminChat',
                component: () => import('@/views/chat/ChatView.vue'),
                meta: { title: '智能问答' },
            },
            {
                path: 'chat/:id',
                name: 'AdminChatDetail',
                component: () => import('@/views/chat/ChatView.vue'),
                meta: { title: '对话详情' },
            },
            {
                path: 'search',
                name: 'AdminSearch',
                component: () => import('@/views/knowledge/SearchView.vue'),
                meta: { title: '全文搜索' },
            },
        ],
    },

    // ---- 普通用户布局（需要登录） ----
    {
        path: '/user',
        component: () => import('@/layouts/UserLayout.vue'),
        meta: { requiresAuth: true, role: 'user' },
        children: [
            { path: '', redirect: '/user/chat' },
            {
                path: 'chat',
                name: 'ChatView',
                component: () => import('@/views/chat/ChatView.vue'),
                meta: { title: '智能问答' },
            },
            {
                path: 'chat/:id',
                name: 'ChatDetail',
                component: () => import('@/views/chat/ChatView.vue'),
                meta: { title: '对话详情' },
            },
            {
                path: 'knowledge',
                name: 'KnowledgeBrowse',
                component: () => import('@/views/knowledge/KnowledgeList.vue'),
                meta: { title: '知识浏览' },
            },
            {
                path: 'search',
                name: 'UserSearch',
                component: () => import('@/views/knowledge/SearchView.vue'),
                meta: { title: '全文搜索' },
            },
        ],
    },

    // ---- 个人信息（所有登录用户） ----
    {
        path: '/profile',
        name: 'Profile',
        component: () => import('@/views/Profile.vue'),
        meta: { title: '个人信息', requiresAuth: true },
    },

    // ---- 默认跳转 ----
    { path: '/', redirect: '/login' },
    { path: '/:pathMatch(.*)*', redirect: '/login' },
]

const router = createRouter({
    history: createWebHistory(),
    routes,
})

// 路由守卫
router.beforeEach((to, from, next) => {
    document.title = to.meta.title ? `${to.meta.title} - 企业知识库问答系统` : '企业知识库问答系统'

    const userStore = useUserStore()

    if (to.meta.requiresAuth) {
        if (!userStore.isLoggedIn) {
            ElMessage.warning('请先登录')
            return next('/login')
        }

        if (to.meta.role && userStore.user.role !== to.meta.role) {
            ElMessage.error('权限不足')
            // 根据角色跳转
            if (userStore.user.role === 'admin') {
                return next('/admin/home')
            } else {
                return next('/user/chat')
            }
        }
    }

    // 已登录时访问登录页，跳转对应首页
    if (to.path === '/login' && userStore.isLoggedIn) {
        if (userStore.user.role === 'admin') {
            return next('/admin/home')
        } else {
            return next('/user/chat')
        }
    }

    next()
})

export default router
