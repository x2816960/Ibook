<template>
  <el-container class="app-layout">
    <el-header class="app-header">
      <div class="header-left">
        <h1 class="logo" @click="$router.push('/tasks')">Ibook</h1>
      </div>
      <div class="header-right">
        <router-link to="/tasks" class="nav-link">任务</router-link>
        <router-link to="/tasks/trash" class="nav-link">回收站</router-link>
        <router-link v-if="authStore.isAdmin" to="/admin" class="nav-link">管理</router-link>
        <el-dropdown @command="handleCommand">
          <span class="user-info">
            {{ authStore.user?.nickname || authStore.user?.username }}
            <el-icon><ArrowDown /></el-icon>
          </span>
          <template #dropdown>
            <el-dropdown-menu>
              <el-dropdown-item command="settings">个人设置</el-dropdown-item>
              <el-dropdown-item command="logout" divided>退出登录</el-dropdown-item>
            </el-dropdown-menu>
          </template>
        </el-dropdown>
      </div>
    </el-header>
    <el-main>
      <router-view />
    </el-main>
  </el-container>
</template>

<script setup>
import { useRouter } from 'vue-router'
import { ArrowDown } from '@element-plus/icons-vue'
import { useAuthStore } from '../../stores/auth'

const router = useRouter()
const authStore = useAuthStore()

async function handleCommand(cmd) {
  if (cmd === 'settings') router.push('/settings')
  else if (cmd === 'logout') {
    await authStore.logout()
    router.push('/login')
  }
}
</script>

<style scoped>
.app-layout {
  min-height: 100vh;
}
.app-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  background: #fff;
  box-shadow: 0 1px 4px rgba(0, 0, 0, 0.08);
  padding: 0 24px;
}
.logo {
  font-size: 22px;
  color: #409eff;
  cursor: pointer;
  margin: 0;
}
.header-right {
  display: flex;
  align-items: center;
  gap: 20px;
}
.nav-link {
  color: #606266;
  text-decoration: none;
  font-size: 14px;
}
.nav-link:hover,
.nav-link.router-link-active {
  color: #409eff;
}
.user-info {
  display: flex;
  align-items: center;
  gap: 4px;
  cursor: pointer;
  color: #606266;
  font-size: 14px;
}
</style>
