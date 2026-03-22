<template>
  <div class="task-list">
    <el-card v-loading="taskStore.loading">
      <draggable
        v-model="localTasks"
        item-key="id"
        handle=".drag-handle"
        ghost-class="ghost"
        @end="onDragEnd"
      >
        <template #item="{ element }">
          <TaskItem
            :task="element"
            @edit="$emit('edit', element)"
            @delete="handleDelete"
            @status-change="handleStatusChange"
            @priority-change="handlePriorityChange"
          />
        </template>
      </draggable>
      <el-empty v-if="!taskStore.loading && localTasks.length === 0" description="暂无任务，点击新建" />
    </el-card>

    <div class="pagination-wrap" v-if="taskStore.total > 0">
      <el-pagination
        v-model:current-page="taskStore.filters.page"
        v-model:page-size="taskStore.filters.page_size"
        :total="taskStore.total"
        :page-sizes="[10, 20, 50]"
        layout="total, sizes, prev, pager, next"
        @current-change="onPageChange"
        @size-change="onSizeChange"
      />
    </div>
  </div>
</template>

<script setup>
import { ref, watch } from 'vue'
import draggable from 'vuedraggable'
import { useTaskStore } from '../../stores/task'
import TaskItem from './TaskItem.vue'

defineEmits(['edit'])
const taskStore = useTaskStore()
const localTasks = ref([...taskStore.tasks])

watch(() => taskStore.tasks, (val) => { localTasks.value = [...val] }, { deep: true })

async function onDragEnd() {
  const ids = localTasks.value.map((t) => t.id)
  const originalIds = taskStore.tasks.map((t) => t.id)
  // 只有顺序真正变化时才调用API
  if (JSON.stringify(ids) !== JSON.stringify(originalIds)) {
    try {
      // 使用 silent: true 禁用错误消息显示
      await taskStore.updateSort(ids, { silent: true })
    } catch {
      // 忽略排序更新错误
    }
  }
}

function handleDelete(id) {
  taskStore.deleteTask(id)
}

function handleStatusChange(id, newStatus) {
  taskStore.changeStatus(id, newStatus)
}

function handlePriorityChange(id, newPriority) {
  taskStore.changePriority(id, newPriority)
}

function onPageChange(page) {
  taskStore.setFilter('page', page)
}
function onSizeChange(size) {
  taskStore.setFilter('page_size', size)
}
</script>

<style scoped>
.ghost {
  opacity: 0.4;
  background: #e8f4ff;
}
.pagination-wrap {
  display: flex;
  justify-content: center;
  margin-top: 16px;
}
</style>
