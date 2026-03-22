<template>
  <div class="task-filter">
    <el-row :gutter="12" align="middle">
      <el-col :span="6">
        <el-select v-model="localStatus" placeholder="状态筛选" clearable @change="onStatusChange" style="width: 100%">
          <el-option label="全部状态" :value="null" />
          <el-option v-for="s in STATUS_OPTIONS" :key="s.value" :label="s.label" :value="s.value" />
        </el-select>
      </el-col>
      <el-col :span="6">
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
      <el-col :span="4" style="text-align: right">
        <el-button type="primary" @click="$emit('create')">
          <el-icon><Plus /></el-icon> 新增任务
        </el-button>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { ref, watch } from 'vue'
import { Search, Plus } from '@element-plus/icons-vue'
import { useTaskStore } from '../../stores/task'
import { STATUS_OPTIONS, PRIORITY_OPTIONS } from '../../utils/constants'

defineEmits(['create'])
const taskStore = useTaskStore()

const localStatus = ref(taskStore.filters.status)
const localPriority = ref(taskStore.filters.priority)
const localKeyword = ref(taskStore.filters.keyword)

watch(() => taskStore.filters.status, (v) => { localStatus.value = v })

function onStatusChange(val) { taskStore.setFilter('status', val) }
function onPriorityChange(val) { taskStore.setFilter('priority', val) }
function onSearch() { taskStore.setFilter('keyword', localKeyword.value) }
</script>

<style scoped>
.task-filter {
  margin: 16px 0;
}
</style>
