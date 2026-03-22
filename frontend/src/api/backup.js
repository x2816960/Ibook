import api from './index'

export const backupApi = {
  export: () => api.post('/admin/backup/export'),
  list: () => api.get('/admin/backup/list'),
  downloadUrl: (filename) => `/api/admin/backup/download/${filename}`,
  download: (filename) => api.get(`/admin/backup/download/${filename}`, { responseType: 'blob' }),
  delete: (filename) => api.delete(`/admin/backup/delete/${filename}`),
  deleteAll: () => api.delete('/admin/backup/delete-all'),
  import: (file) => {
    const formData = new FormData()
    formData.append('file', file)
    return api.post('/admin/backup/import', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    })
  },
}
