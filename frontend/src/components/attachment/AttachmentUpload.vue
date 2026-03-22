<template>
  <div class="attachment-upload">
    <el-upload
      :auto-upload="false"
      :file-list="fileList"
      :on-change="handleChange"
      :on-remove="handleRemove"
      :before-upload="beforeUpload"
      multiple
      :limit="10"
    >
      <el-button type="primary">选择文件</el-button>
      <template #tip>
        <div class="el-upload__tip">
          支持图片、视频、文档等格式
        </div>
      </template>
    </el-upload>
    <el-button
      v-if="pendingFiles.length > 0"
      type="primary"
      size="small"
      :loading="uploading"
      style="margin-top: 8px"
      @click="startUpload"
    >
      上传 {{ pendingFiles.length }} 个文件
    </el-button>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { UploadFilled } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import { attachmentApi } from '../../api/attachments'
import { IMAGE_EXTENSIONS, VIDEO_EXTENSIONS, FILE_EXTENSIONS } from '../../utils/constants'

const props = defineProps({
  taskId: { type: Number, default: null },
})
const emit = defineEmits(['uploaded'])

const fileList = ref([])
const pendingFiles = ref([])
const uploading = ref(false)

defineExpose({ startUpload, hasPending: () => pendingFiles.value.length > 0 })

const allExtensions = [...IMAGE_EXTENSIONS, ...VIDEO_EXTENSIONS, ...FILE_EXTENSIONS]

function handleChange(file, files) {
  const ext = file.name.split('.').pop()?.toLowerCase()
  if (!allExtensions.includes(ext)) {
    ElMessage.error('不支持的文件类型')
    fileList.value = files.filter(f => f.uid !== file.uid)
    return
  }
  pendingFiles.value = files.filter(f => f.status !== 'success')
}

function handleRemove(file, files) {
  pendingFiles.value = files.filter(f => f.status !== 'success')
}

function beforeUpload() {
  return false
}

async function startUpload() {
  if (!props.taskId) {
    ElMessage.warning('请先保存任务')
    return
  }
  uploading.value = true
  try {
    for (const file of pendingFiles.value) {
      await attachmentApi.upload(props.taskId, file.raw)
      file.status = 'success'
    }
    pendingFiles.value = []
    ElMessage.success('上传完成')
    emit('uploaded')
  } catch (e) {
    // error handled by interceptor
  } finally {
    uploading.value = false
  }
}
</script>

<style scoped>
.attachment-upload {
  margin-top: 12px;
}
</style>
