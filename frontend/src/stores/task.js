import { defineStore } from 'pinia'
import { ref } from 'vue'
import { taskApi } from '../api/tasks'

export const useTaskStore = defineStore('task', () => {
  const tasks = ref([])
  const total = ref(0)
  const stats = ref({})
  const loading = ref(false)
  const filters = ref({
    status: null,
    priority: null,
    keyword: '',
    due_filter: null,  // 'today' = 今日到期, 'overdue' = 已过期
    page: 1,
    page_size: 20,
  })

  async function fetchTasks() {
    loading.value = true
    try {
      const params = {}
      if (filters.value.status) params.status = filters.value.status
      if (filters.value.priority) params.priority = filters.value.priority
      if (filters.value.keyword) params.keyword = filters.value.keyword
      if (filters.value.due_filter) params.due_filter = filters.value.due_filter
      params.page = filters.value.page
      params.page_size = filters.value.page_size

      const res = await taskApi.list(params)
      tasks.value = res.data.items
      total.value = res.data.total
    } finally {
      loading.value = false
    }
  }

  async function fetchStats() {
    const res = await taskApi.getStats()
    stats.value = res.data
  }

  async function createTask(data) {
    const res = await taskApi.create(data)
    await fetchTasks()
    await fetchStats()
    return res.data
  }

  async function updateTask(id, data) {
    const res = await taskApi.update(id, data)
    await fetchTasks()
    return res.data
  }

  async function deleteTask(id) {
    await taskApi.delete(id)
    await fetchTasks()
    await fetchStats()
  }

  async function changeStatus(id, status) {
    const res = await taskApi.changeStatus(id, status)
    await fetchTasks()
    await fetchStats()
    return res.data
  }

  async function changePriority(id, priority) {
    const res = await taskApi.update(id, { priority })
    await fetchTasks()
    return res.data
  }

  async function updateSort(taskIds, config = {}) {
    await taskApi.updateSort(taskIds, config)
    // 排序更新后直接修改本地数据，不重新获取列表，避免分页被重置
    const sortedTasks = taskIds.map(id => tasks.value.find(t => t.id === id)).filter(Boolean)
    tasks.value = sortedTasks
  }

  function setFilter(key, value) {
    filters.value[key] = value
    if (key !== 'page') filters.value.page = 1
    fetchTasks()
  }

  return {
    tasks, total, stats, loading, filters,
    fetchTasks, fetchStats, createTask, updateTask, deleteTask,
    changeStatus, changePriority, updateSort, setFilter,
  }
})
