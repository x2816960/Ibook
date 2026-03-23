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
      </template>
    </MdEditor>
    <input
      ref="videoInputRef"
      type="file"
      accept="video/mp4,video/avi,video/mov,video/x-matroska"
      style="display: none"
      @change="handleVideoSelected"
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
const content = ref(props.modelValue)

// 工具栏配置：内置工具 + 自定义视频上传按钮（索引 0）
const toolbarConfig = [
  'bold', 'underline', 'italic', 'strikeThrough',
  '-',
  'title', 'sub', 'sup', 'quote', 'unorderedList', 'orderedList', 'task',
  '-',
  'codeRow', 'code', 'link', 'image', 0,  // 0 = 第一个自定义工具栏（视频上传）
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
</script>

<style scoped>
.markdown-editor-wrap {
  margin-top: 8px;
}
</style>
