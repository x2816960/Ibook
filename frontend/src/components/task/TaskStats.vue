<template>
  <div class="task-stats">
    <el-row :gutter="12">
      <el-col :span="3" v-for="item in statItems" :key="item.key">
        <el-card
          shadow="hover"
          class="stat-card"
          :class="{ active: isActive(item) }"
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
const filters = computed(() => taskStore.filters)

const statItems = [
  { key: 'total', label: '任务总数', color: '#303133', filterType: 'status', filterValue: null },
  { key: 'todo', label: '待办', color: '#909399', filterType: 'status', filterValue: '待办' },
  { key: 'in_progress', label: '进行中', color: '#409EFF', filterType: 'status', filterValue: '进行中' },
  { key: 'done', label: '已完成', color: '#67C23A', filterType: 'status', filterValue: '已完成' },
  { key: 'cancelled', label: '已取消', color: '#909399', filterType: 'status', filterValue: '已取消' },
  { key: 'today_due', label: '今日到期', color: '#E6A23C', filterType: 'due_filter', filterValue: 'today' },
  { key: 'overdue', label: '已过期', color: '#F56C6C', filterType: 'due_filter', filterValue: 'overdue' },
]

// 判断当前统计项是否处于激活状态
function isActive(item) {
  if (item.filterType === 'status') {
    return filters.value.status === item.filterValue && !filters.value.due_filter
  } else if (item.filterType === 'due_filter') {
    return filters.value.due_filter === item.filterValue
  }
  return false
}

function handleClick(item) {
  const currentFilterType = item.filterType
  const currentFilterValue = item.filterValue
  
  if (currentFilterType === 'status') {
    // 点击状态筛选
    const currentStatus = filters.value.status
    if (currentStatus === currentFilterValue && !filters.value.due_filter) {
      // 取消筛选
      taskStore.setFilter('status', null)
    } else {
      // 设置状态筛选，同时清除due_filter
      taskStore.filters.due_filter = null
      taskStore.setFilter('status', currentFilterValue)
    }
  } else if (currentFilterType === 'due_filter') {
    // 点击今日到期或已过期
    const currentDueFilter = filters.value.due_filter
    if (currentDueFilter === currentFilterValue) {
      // 取消筛选
      taskStore.setFilter('due_filter', null)
    } else {
      // 设置due_filter，同时清除status
      taskStore.filters.status = null
      taskStore.setFilter('due_filter', currentFilterValue)
    }
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
