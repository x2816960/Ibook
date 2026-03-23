<template>
  <div class="attachment-list" v-if="attachments.length > 0">
    <div class="attachment-item" v-for="att in attachments" :key="att.id">
      <div class="att-preview">
        <el-image
          v-if="att.file_type === 'image'"
          :src="getPreviewUrl(att.id)"
          :preview-src-list="imageUrls"
          fit="cover"
          class="att-thumb"
        />
        <el-icon v-else-if="att.file_type === 'video'" class="att-icon" @click="playVideo(att)"><VideoCamera /></el-icon>
        <el-icon v-else class="att-icon"><Document /></el-icon>
      </div>
      <div class="att-info">
        <span class="att-name" :title="att.file_name">{{ att.file_name }}</span>
        <span class="att-size">{{ formatFileSize(att.file_size) }}</span>
      </div>
      <div class="att-actions">
        <el-button size="small" text @click="download(att)">
          <el-icon><Download /></el-icon>
        </el-button>
        <el-popconfirm v-if="editable" title="确定删除此附件？" @confirm="handleDelete(att.id)">
          <template #reference>
            <el-button size="small" text type="danger">
              <el-icon><Delete /></el-icon>
            </el-button>
          </template>
        </el-popconfirm>
      </div>
    </div>

    <!-- Video Player Dialog -->
    <el-dialog v-model="videoVisible" title="视频播放" width="720px" destroy-on-close>
      <video v-if="videoUrl" :src="videoUrl" controls style="width: 100%" />
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { VideoCamera, Document, Download, Delete } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import { attachmentApi } from '../../api/attachments'
import { formatFileSize } from '../../utils/helpers'

const props = defineProps({
  attachments: { type: Array, default: () => [] },
  editable: { type: Boolean, default: false },
})
const emit = defineEmits(['deleted'])

const videoVisible = ref(false)
const videoUrl = ref('')

const imageUrls = computed(() =>
  props.attachments
    .filter(a => a.file_type === 'image')
    .map(a => getPreviewUrl(a.id))
)

function getPreviewUrl(id) {
  const baseUrl = attachmentApi.downloadUrl(id, true)
  const token = localStorage.getItem('token') || sessionStorage.getItem('token')
  if (token) {
    return `${baseUrl}&token=${token}`
  }
  return baseUrl
}

function download(att) {
  window.open(attachmentApi.downloadUrl(att.id), '_blank')
}

function playVideo(att) {
  videoUrl.value = getPreviewUrl(att.id)
  videoVisible.value = true
}

async function handleDelete(id) {
  await attachmentApi.delete(id)
  ElMessage.success('附件已删除')
  emit('deleted')
}
</script>

<style scoped>
.attachment-list {
  margin-top: 8px;
}
.attachment-item {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 6px 0;
  border-bottom: 1px solid #f0f0f0;
}
.att-thumb {
  width: 40px;
  height: 40px;
  border-radius: 4px;
}
.att-icon {
  font-size: 28px;
  color: #909399;
  cursor: pointer;
}
.att-info {
  flex: 1;
  min-width: 0;
}
.att-name {
  display: block;
  font-size: 13px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}
.att-size {
  font-size: 12px;
  color: #c0c4cc;
}
.att-actions {
  display: flex;
  gap: 2px;
}
</style>
