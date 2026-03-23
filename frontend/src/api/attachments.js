import api from './index'

export const attachmentApi = {
  upload: (taskId, file, onProgress) => {
    const formData = new FormData()
    formData.append('file', file)
    return api.post(`/tasks/${taskId}/attachments`, formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
      onUploadProgress: onProgress,
    })
  },
  list: (taskId) => api.get(`/tasks/${taskId}/attachments`),
  delete: (id) => api.delete(`/attachments/${id}`),
  downloadUrl: (id, preview = false) => {
    const params = new URLSearchParams()
    if (preview) params.set('preview', 'true')
    return `/api/attachments/${id}/download?${params.toString()}`
  },
}
