<template>
  <el-container class="admin-layout">
    <el-header class="admin-header">
      <div class="header-left">
        <h1 class="logo" @click="$router.push('/tasks')">Ibook</h1>
        <span class="admin-badge">管理后台</span>
      </div>
      <div class="header-right">
        <router-link to="/tasks" class="nav-link">返回任务</router-link>
        <el-dropdown @command="handleCommand">
          <span class="user-info">
            {{ authStore.user?.nickname || authStore.user?.username }}
            <el-icon><ArrowDown /></el-icon>
          </span>
          <template #dropdown>
            <el-dropdown-menu>
              <el-dropdown-item command="logout">退出登录</el-dropdown-item>
            </el-dropdown-menu>
          </template>
        </el-dropdown>
      </div>
    </el-header>
    <el-container>
      <el-aside width="200px" class="admin-aside">
        <el-menu :default-active="$route.path" router>
          <el-menu-item index="/admin/users">
            <el-icon><User /></el-icon>
            <span>用户管理</span>
          </el-menu-item>
          <el-menu-item index="/admin/config">
            <el-icon><Setting /></el-icon>
            <span>系统配置</span>
          </el-menu-item>
          <el-menu-item index="/admin/stats">
            <el-icon><DataAnalysis /></el-icon>
            <span>系统统计</span>
          </el-menu-item>
          <el-menu-item index="/admin/backup">
            <el-icon><Download /></el-icon>
            <span>备份恢复</span>
          </el-menu-item>
        </el-menu>
      </el-aside>
      <el-main>
        <router-view />
      </el-main>
    </el-container>
  </el-container>
</template>

<script setup>
import { useRouter } from 'vue-router'
import { ArrowDown, User, Setting, DataAnalysis, Download } from '@element-plus/icons-vue'
import { useAuthStore } from '../../stores/auth'

const router = useRouter()
const authStore = useAuthStore()

async function handleCommand(cmd) {
  if (cmd === 'logout') {
    await authStore.logout()
    router.push('/login')
  }
}
</script>

<style scoped>
.admin-layout {
  min-height: 100vh;
}
.admin-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  background: #fff;
  box-shadow: 0 1px 4px rgba(0, 0, 0, 0.08);
  padding: 0 24px;
}
.header-left {
  display: flex;
  align-items: center;
  gap: 12px;
}
.logo {
  font-size: 22px;
  color: #409eff;
  cursor: pointer;
  margin: 0;
}
.admin-badge {
  background: #409eff;
  color: #fff;
  padding: 2px 8px;
  border-radius: 4px;
  font-size: 12px;
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
.user-info {
  display: flex;
  align-items: center;
  gap: 4px;
  cursor: pointer;
  color: #606266;
  font-size: 14px;
}
.admin-aside {
  background: #fff;
  border-right: 1px solid #e6e6e6;
}
</style>
