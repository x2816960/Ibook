<template>
  <div class="page-container">
    <TaskStats />
    <TaskFilter @create="openCreate" />
    <TaskList @edit="openEdit" />
    <TaskForm v-model="showForm" :task="editingTask" />
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useTaskStore } from '../stores/task'
import TaskStats from '../components/task/TaskStats.vue'
import TaskFilter from '../components/task/TaskFilter.vue'
import TaskList from '../components/task/TaskList.vue'
import TaskForm from '../components/task/TaskForm.vue'

const taskStore = useTaskStore()
const showForm = ref(false)
const editingTask = ref(null)

onMounted(() => {
  taskStore.fetchTasks()
  taskStore.fetchStats()
})

function openCreate() {
  editingTask.value = null
  showForm.value = true
}

function openEdit(task) {
  editingTask.value = task
  showForm.value = true
}
</script>
