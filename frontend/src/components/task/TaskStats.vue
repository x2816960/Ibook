<template>
  <div class="task-stats">
    <el-row :gutter="12">
      <el-col :span="3" v-for="item in statItems" :key="item.key">
        <el-card
          shadow="hover"
          class="stat-card"
          :class="{ active: activeFilter === item.filterValue }"
          @click="handleClick(item)"
        >
          <div class="stat-number" :style="{ color: item.color }">{{ stats[item.key] || 0 }}</div>
          <div class="stat-label">{{ item.label }}</div>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useTaskStore } from '../../stores/task'

const taskStore = useTaskStore()
const stats = computed(() => taskStore.stats)
const activeFilter = computed(() => taskStore.filters.status)

const statItems = [
  { key: 'total', label: '任务总数', color: '#303133', filterValue: null },
  { key: 'todo', label: '待办', color: '#909399', filterValue: '待办' },
  { key: 'in_progress', label: '进行中', color: '#409EFF', filterValue: '进行中' },
  { key: 'done', label: '已完成', color: '#67C23A', filterValue: '已完成' },
  { key: 'cancelled', label: '已取消', color: '#909399', filterValue: '已取消' },
  { key: 'today_due', label: '今日到期', color: '#E6A23C', filterValue: null },
  { key: 'overdue', label: '已过期', color: '#F56C6C', filterValue: null },
]

function handleClick(item) {
  if (item.filterValue !== undefined) {
    const current = taskStore.filters.status
    taskStore.setFilter('status', current === item.filterValue ? null : item.filterValue)
  }
}
</script>

<style scoped>
.stat-card {
  cursor: pointer;
  text-align: center;
  transition: all 0.2s;
}
.stat-card:hover {
  transform: translateY(-2px);
}
.stat-card.active {
  border-color: #409eff;
}
.stat-number {
  font-size: 28px;
  font-weight: 700;
  line-height: 1.2;
}
.stat-label {
  font-size: 13px;
  color: #909399;
  margin-top: 4px;
}
</style>
