<template>
  <div class="task-item" :class="{ expanded: isExpanded }">
    <div class="task-row" @click="toggleExpand">
      <span class="drag-handle" @mousedown="onDragStart" @click.stop>
        <el-icon><Rank /></el-icon>
      </span>
      <div class="task-title" :title="task.title">{{ task.title }}</div>
      <el-tooltip v-if="task.description" :content="task.description" placement="top" :show-after="500">
        <span class="task-desc">{{ task.description }}</span>
      </el-tooltip>
      <PrioritySwitch :priority="task.priority" @change="handlePriorityChange" @click.stop />
      <StatusSwitch :status="task.status" @change="handleStatusChange" @click.stop />
      <span class="task-due" :class="{ overdue: isDueOverdue, today: isDueToday }">
        {{ dueLabel }}
      </span>
      <span v-if="task.attachment_count" class="task-attachment" @click.stop>
        📎 {{ task.attachment_count }}
      </span>
      <div class="task-actions" @click.stop>
        <el-button size="small" text @click="$emit('edit', task)">
          <el-icon><Edit /></el-icon>
        </el-button>
        <el-popconfirm 
          v-if="!isDragging" 
          title="确定删除此任务？" 
          @confirm="$emit('delete', task.id)" 
          :popper-options="{ modifiers: [{ name: 'computeStyles', options: { adaptive: false } }] }"
        >
          <template #reference>
            <el-button size="small" text type="danger">
              <el-icon><Delete /></el-icon>
            </el-button>
          </template>
        </el-popconfirm>
        <el-button v-else size="small" text type="danger">
          <el-icon><Delete /></el-icon>
        </el-button>
      </div>
    </div>
    <div v-if="isExpanded" class="task-detail-area">
      <TaskDetail :task="task" />
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { Rank, Edit, Delete } from '@element-plus/icons-vue'
import StatusSwitch from './StatusSwitch.vue'
import PrioritySwitch from './PrioritySwitch.vue'
import TaskDetail from './TaskDetail.vue'
import { formatDateTime, isOverdue, isToday } from '../../utils/helpers'

const props = defineProps({
  task: { type: Object, required: true },
})
const emit = defineEmits(['edit', 'delete', 'statusChange', 'priorityChange'])

const isExpanded = ref(false)
const isDragging = ref(false)

function onDragStart() {
  isDragging.value = true
  // 在拖动结束时重置标志
  setTimeout(() => {
    isDragging.value = false
  }, 1000) // 1秒后自动重置，防止popconfirm显示
}

const isDueOverdue = computed(() =>
  props.task.due_date && !props.task.is_indefinite &&
  ['待办', '进行中'].includes(props.task.status) &&
  isOverdue(props.task.due_date)
)

const isDueToday = computed(() =>
  props.task.due_date && isToday(props.task.due_date)
)

const dueLabel = computed(() => {
  if (props.task.is_indefinite) return '无限期'
  if (!props.task.due_date) return ''
  return formatDateTime(props.task.due_date)
})

function toggleExpand() {
  isExpanded.value = !isExpanded.value
}

function handleStatusChange(newStatus) {
  emit('statusChange', props.task.id, newStatus)
}

function handlePriorityChange(newPriority) {
  emit('priorityChange', props.task.id, newPriority)
}
</script>

<style scoped>
.task-item {
  border-bottom: 1px solid #f0f0f0;
}
.task-item:last-child {
  border-bottom: none;
}
.task-row {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px 16px;
  cursor: pointer;
  transition: background 0.15s;
  position: relative;
  z-index: 1;
}
.task-row:hover {
  background: #f5f7fa;
}
.drag-handle {
  cursor: grab;
  color: #c0c4cc;
  font-size: 18px;
}
.task-title {
  flex: 1;
  font-weight: 500;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  min-width: 0;
}
.task-desc {
  color: #909399;
  font-size: 13px;
  max-width: 200px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}
.task-due {
  font-size: 13px;
  color: #909399;
  white-space: nowrap;
}
.task-due.overdue {
  color: #f56c6c;
  font-weight: 500;
}
.task-due.today {
  color: #e6a23c;
}
.task-attachment {
  font-size: 13px;
  color: #909399;
}
.task-actions {
  display: flex;
  gap: 4px;
}
.task-detail-area {
  padding: 0 16px 16px 48px;
}
.detail-content {
  background: #fafafa;
  padding: 12px;
  border-radius: 6px;
  font-size: 14px;
  line-height: 1.6;
}
.no-detail {
  color: #c0c4cc;
  font-size: 13px;
}
</style>
