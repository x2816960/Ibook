import api from './index'

export const taskApi = {
  list: (params) => api.get('/tasks', { params }),
  create: (data) => api.post('/tasks', data),
  get: (id) => api.get(`/tasks/${id}`),
  update: (id, data) => api.put(`/tasks/${id}`, data),
  delete: (id) => api.delete(`/tasks/${id}`),
  changeStatus: (id, status) => api.patch(`/tasks/${id}/status`, { status }),
  updateSort: (task_ids, config) => api.put('/tasks/sort', { task_ids }, config),
  getStats: () => api.get('/tasks/stats'),
  getTrash: () => api.get('/tasks/trash'),
  restore: (id) => api.post(`/tasks/${id}/restore`),
  permanentDelete: (id) => api.delete(`/tasks/${id}/permanent`),
}
