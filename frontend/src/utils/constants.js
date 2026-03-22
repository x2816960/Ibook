export const PRIORITY_OPTIONS = [
  { label: '高', value: '高', color: '#F56C6C' },
  { label: '中', value: '中', color: '#E6A23C' },
  { label: '低', value: '低', color: '#67C23A' },
]

export const STATUS_OPTIONS = [
  { label: '待办', value: '待办', color: '#909399', type: 'info' },
  { label: '进行中', value: '进行中', color: '#409EFF', type: 'primary' },
  { label: '已完成', value: '已完成', color: '#67C23A', type: 'success' },
  { label: '已取消', value: '已取消', color: '#909399', type: 'info' },
]

export const ALLOWED_TRANSITIONS = {
  '待办': ['进行中', '已取消'],
  '进行中': ['已完成', '待办'],
  '已完成': ['进行中'],
  '已取消': ['待办'],
}

export const IMAGE_EXTENSIONS = ['jpg', 'jpeg', 'png', 'gif', 'bmp', 'webp']
export const VIDEO_EXTENSIONS = ['mp4', 'avi', 'mov', 'mkv']
export const FILE_EXTENSIONS = ['pdf', 'doc', 'docx', 'xls', 'xlsx', 'ppt', 'pptx', 'txt', 'zip', 'rar']
