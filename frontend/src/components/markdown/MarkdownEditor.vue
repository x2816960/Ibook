<template>
  <div class="markdown-editor-wrap" :style="$attrs.style">
    <MdEditor
      ref="editorRef"
      v-model="content"
      language="zh-CN"
      :preview="previewOnly"
      :toolbars="previewOnly ? [] : toolbarConfig"
      @onUploadImg="handleUploadImg"
      style="height: 100%"
    >
      <template #defToolbars>
        <NormalToolbar title="上传视频" @onClick="triggerVideoUpload">
          <template #trigger>
            <svg viewBox="0 0 24 24" width="14" height="14" fill="currentColor">
              <path d="M17 10.5V7a1 1 0 0 0-1-1H4a1 1 0 0 0-1 1v10a1 1 0 0 0 1 1h12a1 1 0 0 0 1-1v-3.5l4 4V6.5l-4 4z"/>
            </svg>
          </template>
        </NormalToolbar>
        <NormalToolbar title="上传附件" @onClick="triggerFileUpload">
          <template #trigger>
            <svg viewBox="0 0 24 24" width="14" height="14" fill="currentColor">
              <path d="M16.5 6v11.5c0 2.21-1.79 4-4 4s-4-1.79-4-4V5c0-1.38 1.12-2.5 2.5-2.5s2.5 1.12 2.5 2.5v10.5c0 .55-.45 1-1 1s-1-.45-1-1V6H10v9.5c0 1.38 1.12 2.5 2.5 2.5s2.5-1.12 2.5-2.5V5c0-2.21-1.79-4-4-4S7 2.79 7 5v12.5c0 3.04 2.46 5.5 5.5 5.5s5.5-2.46 5.5-5.5V6h-1.5z"/>
            </svg>
          </template>
        </NormalToolbar>
      </template>
    </MdEditor>
    <input
      ref="videoInputRef"
      type="file"
      accept="video/mp4,video/avi,video/mov,video/x-matroska"
      style="display: none"
      @change="handleVideoSelected"
    />
    <input
      ref="fileInputRef"
      type="file"
      style="display: none"
      @change="handleFileSelected"
    />
  </div>
</template>

<script setup>
import { ref, watch } from 'vue'
import { MdEditor, NormalToolbar } from 'md-editor-v3'
import 'md-editor-v3/lib/style.css'
import { attachmentApi } from '../../api/attachments'
import { ElMessage } from 'element-plus'

const props = defineProps({
  modelValue: { type: String, default: '' },
  taskId: { type: Number, default: null },
  previewOnly: { type: Boolean, default: false },
})
defineOptions({ inheritAttrs: false })
const emit = defineEmits(['update:modelValue'])

const editorRef = ref()
const videoInputRef = ref()
const fileInputRef = ref()
const content = ref(props.modelValue)

// 工具栏配置：内置工具 + 自定义视频上传按钮（索引 0）+ 附件上传按钮（索引 1）
const toolbarConfig = [
  'bold', 'underline', 'italic', 'strikeThrough',
  '-',
  'title', 'sub', 'sup', 'quote', 'unorderedList', 'orderedList', 'task',
  '-',
  'codeRow', 'code', 'link', 'image', 0, 1,  // 0 = 视频上传, 1 = 附件上传
  'table', 'mermaid', 'katex',
  '-',
  'revoke', 'next',
  '=',
  'pageFullscreen', 'fullscreen', 'preview', 'previewOnly',
]

watch(() => props.modelValue, (v) => {
  if (!v) {
    content.value = ''
    return
  }
  const token = localStorage.getItem('token') || sessionStorage.getItem('token')
  if (!token) {
    content.value = v
    return
  }
  // 替换URL中的旧token为当前token（兼容 markdown ![](url) 和 HTML <img>/<video> 标签）
  content.value = v.replace(
    /\/api\/attachments\/(\d+)\/download\?preview=true(?:&token=[^)\s"']+)?/g,
    `/api/attachments/$1/download?preview=true&token=${token}`
  )
}, { immediate: true })
watch(content, (v) => emit('update:modelValue', v))

async function handleUploadImg(files, callback) {
  if (!props.taskId) {
    callback([])
    return
  }
  const token = localStorage.getItem('token') || sessionStorage.getItem('token')
  const urls = []
  for (const file of files) {
    try {
      const res = await attachmentApi.upload(props.taskId, file)
      const baseUrl = attachmentApi.downloadUrl(res.data.id, true)
      urls.push(token ? `${baseUrl}&token=${token}` : baseUrl)
    } catch {
      // skip failed
    }
  }
  callback(urls)
}

function triggerVideoUpload() {
  if (!props.taskId) {
    ElMessage.warning('请先保存任务后再上传视频')
    return
  }
  videoInputRef.value?.click()
}

async function handleVideoSelected(e) {
  const file = e.target.files?.[0]
  if (!file) return
  e.target.value = ''

  try {
    ElMessage.info('视频上传中...')
    const res = await attachmentApi.upload(props.taskId, file)
    const baseUrl = attachmentApi.downloadUrl(res.data.id, true)
    const token = localStorage.getItem('token') || sessionStorage.getItem('token')
    const videoUrl = token ? `${baseUrl}&token=${token}` : baseUrl
    const videoTag = `\n<video src="${videoUrl}" controls style="max-width:100%"></video>\n`
    content.value += videoTag
    ElMessage.success('视频上传成功')
  } catch {
    // error handled by interceptor
  }
}

function triggerFileUpload() {
  if (!props.taskId) {
    ElMessage.warning('请先保存任务后再上传附件')
    return
  }
  fileInputRef.value?.click()
}

async function handleFileSelected(e) {
  const file = e.target.files?.[0]
  if (!file) return
  e.target.value = ''

  // 排除图片和视频类型（它们有专门的上传方式）
  const fileType = file.type.toLowerCase()
  if (fileType.startsWith('image/')) {
    ElMessage.warning('请使用编辑器内置的图片上传功能')
    return
  }
  if (fileType.startsWith('video/')) {
    ElMessage.warning('请使用工具栏上的视频上传按钮')
    return
  }

  try {
    ElMessage.info('附件上传中...')
    const res = await attachmentApi.upload(props.taskId, file)
    const downloadUrl = attachmentApi.downloadUrl(res.data.id, false)
    const token = localStorage.getItem('token') || sessionStorage.getItem('token')
    const fullUrl = token ? `${downloadUrl}&token=${token}` : downloadUrl
    // 插入下载链接到Markdown
    const fileLink = `\n[📎 ${file.name}](${fullUrl})\n`
    content.value += fileLink
    ElMessage.success('附件上传成功')
  } catch {
    // error handled by interceptor
  }
}
</script>

<style scoped>
.markdown-editor-wrap {
  margin-top: 8px;
}
</style>
