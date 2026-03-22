import api from './index'

export const adminApi = {
  listUsers: (params) => api.get('/admin/users', { params }),
  toggleUser: (id, data) => api.patch(`/admin/users/${id}`, data),
  resetPassword: (id) => api.post(`/admin/users/${id}/reset-password`),
  getStats: () => api.get('/admin/stats'),
  getConfig: () => api.get('/admin/config'),
  updateConfig: (configs) => api.put('/admin/config', { configs }),
}
