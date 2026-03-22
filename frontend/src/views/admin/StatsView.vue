<template>
  <div>
    <h2>系统统计</h2>
    <el-row :gutter="16" style="margin-top: 16px">
      <el-col :span="8">
        <el-card shadow="hover">
          <div class="stat-value">{{ stats.total_users || 0 }}</div>
          <div class="stat-label">注册用户数</div>
        </el-card>
      </el-col>
      <el-col :span="8">
        <el-card shadow="hover">
          <div class="stat-value">{{ stats.total_tasks || 0 }}</div>
          <div class="stat-label">任务总数</div>
        </el-card>
      </el-col>
    </el-row>

    <el-card style="margin-top: 16px" v-if="stats.tasks_by_status">
      <template #header><span>各状态任务占比</span></template>
      <div class="status-list">
        <div v-for="(count, status) in stats.tasks_by_status" :key="status" class="status-item">
          <span>{{ status }}</span>
          <el-progress
            :percentage="stats.total_tasks ? Math.round(count / stats.total_tasks * 100) : 0"
            :stroke-width="18"
            style="flex: 1; margin: 0 16px"
          />
          <span>{{ count }}</span>
        </div>
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { adminApi } from '../../api/admin'

const stats = ref({})

async function fetchStats() {
  const res = await adminApi.getStats()
  stats.value = res.data
}

onMounted(fetchStats)
</script>

<style scoped>
.stat-value {
  font-size: 36px;
  font-weight: 700;
  color: #409eff;
  text-align: center;
}
.stat-label {
  text-align: center;
  color: #909399;
  margin-top: 4px;
}
.status-item {
  display: flex;
  align-items: center;
  margin-bottom: 12px;
}
.status-item span:first-child {
  width: 60px;
}
</style>
