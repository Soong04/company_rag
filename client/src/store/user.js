import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { getCurrentUser } from '@/api/auth'

export const useUserStore = defineStore('user', () => {
    const user = ref(null)
    const token = ref(localStorage.getItem('token') || '')

    const isLoggedIn = computed(() => !!user.value)
    const isAdmin = computed(() => user.value?.role === 'admin')

    function setUser(userData) {
        user.value = userData
    }

    function clearUser() {
        user.value = null
        token.value = ''
        localStorage.removeItem('token')
    }

    async function fetchCurrentUser() {
        try {
            const res = await getCurrentUser()
            if (res.code === 200 && res.data?.user) {
                user.value = res.data.user
                return true
            }
            return false
        } catch {
            user.value = null
            return false
        }
    }

    return {
        user,
        token,
        isLoggedIn,
        isAdmin,
        setUser,
        clearUser,
        fetchCurrentUser,
    }
})
