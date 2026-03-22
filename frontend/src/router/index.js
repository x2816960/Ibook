import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '../stores/auth'

const routes = [
  {
    path: '/login',
    name: 'Login',
    component: () => import('../views/LoginView.vue'),
    meta: { guest: true },
  },
  {
    path: '/register',
    name: 'Register',
    component: () => import('../views/RegisterView.vue'),
    meta: { guest: true },
  },
  {
    path: '/',
    component: () => import('../components/layout/AppLayout.vue'),
    meta: { requiresAuth: true },
    children: [
      { path: '', redirect: '/tasks' },
      { path: 'tasks', name: 'Tasks', component: () => import('../views/TasksView.vue') },
      { path: 'tasks/trash', name: 'Trash', component: () => import('../views/TrashView.vue') },
      { path: 'settings', name: 'Settings', component: () => import('../views/SettingsView.vue') },
    ],
  },
  {
    path: '/admin',
    component: () => import('../components/layout/AdminLayout.vue'),
    meta: { requiresAuth: true, requiresAdmin: true },
    children: [
      { path: '', redirect: '/admin/users' },
      { path: 'users', name: 'AdminUsers', component: () => import('../views/admin/UsersView.vue') },
      { path: 'config', name: 'AdminConfig', component: () => import('../views/admin/ConfigView.vue') },
      { path: 'stats', name: 'AdminStats', component: () => import('../views/admin/StatsView.vue') },
      { path: 'backup', name: 'AdminBackup', component: () => import('../views/admin/BackupView.vue') },
    ],
  },
  { path: '/:pathMatch(.*)*', redirect: '/login' },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

router.beforeEach(async (to, from, next) => {
  const authStore = useAuthStore()

  if (authStore.token && !authStore.user) {
    try {
      await authStore.fetchProfile()
    } catch {
      authStore.logout()
      return next('/login')
    }
  }

  if (to.meta.requiresAuth && !authStore.isLoggedIn) {
    return next('/login')
  }
  if (to.meta.guest && authStore.isLoggedIn) {
    return next('/tasks')
  }
  if (to.meta.requiresAdmin && !authStore.isAdmin) {
    return next('/tasks')
  }
  next()
})

export default router
