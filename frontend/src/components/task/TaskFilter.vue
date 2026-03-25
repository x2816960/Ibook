<template>
  <div class="task-filter">
    <el-row :gutter="12" align="middle">
      <el-col :span="5">
        <el-select 
          v-model="localStatus" 
          placeholder="状态筛选" 
          clearable 
          @change="onStatusChange" 
          style="width: 100%"
          :disabled="!!taskStore.filters.due_filter"
        >
          <el-option label="全部状态" :value="null" />
          <el-option v-for="s in STATUS_OPTIONS" :key="s.value" :label="s.label" :value="s.value" />
        </el-select>
      </el-col>
      <el-col :span="5">
        <el-select v-model="localPriority" placeholder="优先级筛选" clearable @change="onPriorityChange" style="width: 100%">
          <el-option label="全部优先级" :value="null" />
          <el-option v-for="p in PRIORITY_OPTIONS" :key="p.value" :label="p.label" :value="p.value" />
        </el-select>
      </el-col>
      <el-col :span="8">
        <el-input v-model="localKeyword" placeholder="搜索任务标题或描述" clearable @clear="onSearch" @keyup.enter="onSearch">
          <template #prefix>
            <el-icon><Search /></el-icon>
          </template>
        </el-input>
      </el-col>
      <el-col :span="6" style="text-align: right">
        <el-button v-if="hasActiveFilter" @click="clearAllFilters" style="margin-right: 8px;">
          清除筛选
        </el-button>
        <el-button type="primary" @click="$emit('create')">
          <el-icon><Plus /></el-icon> 新增任务
        </el-button>
      </el-col>
    </el-row>
    <!-- 显示当前筛选提示 -->
    <div v-if="taskStore.filters.due_filter" class="filter-tip">
      <el-tag type="warning" closable @close="clearDueFilter">
        {{ taskStore.filters.due_filter === 'today' ? '今日到期' : '已过期' }}
      </el-tag>
    </div>
  </div>
</template>

<script setup>
import { ref, watch, computed } from 'vue'
import { Search, Plus } from '@element-plus/icons-vue'
import { useTaskStore } from '../../stores/task'
import { STATUS_OPTIONS, PRIORITY_OPTIONS } from '../../utils/constants'

defineEmits(['create'])
const taskStore = useTaskStore()

const localStatus = ref(taskStore.filters.status)
const localPriority = ref(taskStore.filters.priority)
const localKeyword = ref(taskStore.filters.keyword)

const hasActiveFilter = computed(() => {
  return taskStore.filters.status || 
         taskStore.filters.priority || 
         taskStore.filters.keyword || 
         taskStore.filters.due_filter
})

watch(() => taskStore.filters.status, (v) => { localStatus.value = v })
watch(() => taskStore.filters.due_filter, () => {
  // 当due_filter变化时，如果设置了due_filter，清除status的本地显示
  if (taskStore.filters.due_filter) {
    localStatus.value = null
  }
})

function onStatusChange(val) { 
  // 清除due_filter
  if (taskStore.filters.due_filter) {
    taskStore.filters.due_filter = null
  }
  taskStore.setFilter('status', val) 
}
function onPriorityChange(val) { taskStore.setFilter('priority', val) }
function onSearch() { taskStore.setFilter('keyword', localKeyword.value) }

function clearDueFilter() {
  taskStore.setFilter('due_filter', null)
}

function clearAllFilters() {
  taskStore.filters.status = null
  taskStore.filters.priority = null
  taskStore.filters.keyword = ''
  taskStore.filters.due_filter = null
  taskStore.filters.page = 1
  localStatus.value = null
  localPriority.value = null
  localKeyword.value = ''
  taskStore.fetchTasks()
}
</script>

<style scoped>
.task-filter {
  margin: 16px 0;
}
.filter-tip {
  margin-top: 8px;
}
</style>
