import api from './index'

// 将Date对象转换为UTC ISO字符串
function toUTCISOString(date) {
  if (!date) return null
  if (typeof date === 'string') {
    // 如果已经是字符串，确保它是有效的日期
    const d = new Date(date)
    if (isNaN(d.getTime())) return null
    return d.toISOString()
  }
  if (date instanceof Date) {
    return date.toISOString()
  }
  return null
}

// 处理任务数据的日期字段
function processTaskData(data) {
  const processed = { ...data }
  if (data.due_date !== undefined) {
    processed.due_date = toUTCISOString(data.due_date)
  }
  return processed
}

export const taskApi = {
  list: (params) => api.get('/tasks', { params }),
  create: (data) => api.post('/tasks', processTaskData(data)),
  get: (id) => api.get(`/tasks/${id}`),
  update: (id, data) => api.put(`/tasks/${id}`, processTaskData(data)),
  delete: (id) => api.delete(`/tasks/${id}`),
  changeStatus: (id, status) => api.patch(`/tasks/${id}/status`, { status }),
  updateSort: (task_ids, config) => api.put('/tasks/sort', { task_ids }, config),
  getStats: () => api.get('/tasks/stats'),
  getTrash: () => api.get('/tasks/trash'),
  restore: (id) => api.post(`/tasks/${id}/restore`),
  permanentDelete: (id) => api.delete(`/tasks/${id}/permanent`),
}
