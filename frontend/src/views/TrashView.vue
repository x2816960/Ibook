<template>
  <div class="page-container">
    <div class="trash-header">
      <h2>回收站</h2>
      <p class="trash-tip">已删除的任务将在 30 天后自动永久清除</p>
    </div>
    <el-card v-loading="loading">
      <div v-for="task in tasks" :key="task.id" class="trash-item">
        <div class="trash-info">
          <span class="trash-title">{{ task.title }}</span>
          <el-tag size="small" type="info">{{ task.priority }}</el-tag>
          <span class="trash-date">删除于 {{ formatDateTime(task.updated_at) }}</span>
        </div>
        <div class="trash-actions">
          <el-button size="small" type="primary" text @click="handleRestore(task.id)">恢复</el-button>
          <el-popconfirm title="永久删除后不可恢复，确定删除？" @confirm="handlePermanentDelete(task.id)">
            <template #reference>
              <el-button size="small" type="danger" text>永久删除</el-button>
            </template>
          </el-popconfirm>
        </div>
      </div>
      <el-empty v-if="!loading && tasks.length === 0" description="回收站为空" />
    </el-card>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { taskApi } from '../api/tasks'
import { formatDateTime } from '../utils/helpers'

const tasks = ref([])
const loading = ref(false)

async function fetchTrash() {
  loading.value = true
  try {
    const res = await taskApi.getTrash()
    tasks.value = res.data
  } finally {
    loading.value = false
  }
}

async function handleRestore(id) {
  await taskApi.restore(id)
  ElMessage.success('任务已恢复')
  fetchTrash()
}

async function handlePermanentDelete(id) {
  await taskApi.permanentDelete(id)
  ElMessage.success('任务已永久删除')
  fetchTrash()
}

onMounted(fetchTrash)
</script>

<style scoped>
.trash-header {
  margin-bottom: 16px;
}
.trash-header h2 {
  margin: 0;
}
.trash-tip {
  color: #909399;
  font-size: 13px;
  margin: 4px 0 0;
}
.trash-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 12px 0;
  border-bottom: 1px solid #f0f0f0;
}
.trash-item:last-child {
  border-bottom: none;
}
.trash-info {
  display: flex;
  align-items: center;
  gap: 8px;
}
.trash-title {
  font-weight: 500;
}
.trash-date {
  font-size: 12px;
  color: #c0c4cc;
}
.trash-actions {
  display: flex;
  gap: 4px;
}
</style>
