import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { authApi } from '../api/auth'

export const useAuthStore = defineStore('auth', () => {
  const token = ref(localStorage.getItem('token') || sessionStorage.getItem('token') || '')
  const user = ref(null)

  const isLoggedIn = computed(() => !!token.value)
  const isAdmin = computed(() => user.value?.is_admin === true)

  async function login(data) {
    const res = await authApi.login(data)
    token.value = res.data.access_token
    if (data.remember_me) {
      localStorage.setItem('token', token.value)
    } else {
      sessionStorage.setItem('token', token.value)
    }
    await fetchProfile()
    return res.data
  }

  async function register(data) {
    return authApi.register(data)
  }

  async function fetchProfile() {
    const res = await authApi.getProfile()
    user.value = res.data
  }

  async function logout() {
    try {
      await authApi.logout()
    } catch { /* ignore */ }
    token.value = ''
    user.value = null
    localStorage.removeItem('token')
    sessionStorage.removeItem('token')
  }

  async function updateProfile(data) {
    const res = await authApi.updateProfile(data)
    user.value = res.data
  }

  async function changePassword(data) {
    return authApi.changePassword(data)
  }

  return {
    token, user, isLoggedIn, isAdmin,
    login, register, fetchProfile, logout, updateProfile, changePassword,
  }
})
