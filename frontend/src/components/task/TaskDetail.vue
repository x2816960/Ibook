<template>
  <div class="task-detail">
    <MdPreview v-if="processedContent" :modelValue="processedContent" language="zh-CN" />
    <div v-else class="no-content">暂无详细信息</div>
    <AttachmentList v-if="attachments.length > 0" :attachments="attachments" />
  </div>
</template>

<script setup>
import { ref, watch, onMounted, computed } from 'vue'
import { MdPreview } from 'md-editor-v3'
import 'md-editor-v3/lib/preview.css'
import AttachmentList from '../attachment/AttachmentList.vue'
import { attachmentApi } from '../../api/attachments'

const props = defineProps({
  task: { type: Object, required: true },
})

const content = ref(props.task.detail_content || '')
const attachments = ref([])

// 给 Markdown 中的图片 URL 附加/替换 token
const processedContent = computed(() => {
  if (!content.value) return ''
  const token = localStorage.getItem('token') || sessionStorage.getItem('token')
  if (!token) return content.value
  // 替换整个 query string，确保新 token 在最后
  // 匹配 /api/attachments/{id}/download?preview=true 及其后的 &token=xxx
  // [^)\s"'] 兼容 markdown ![](url) 和 HTML <img>/<video> 标签
  return content.value.replace(
    /\/api\/attachments\/(\d+)\/download\?preview=true(?:&token=[^)\s"']+)?/g,
    `/api/attachments/$1/download?preview=true&token=${token}`
  )
})

watch(() => props.task, (t) => {
  content.value = t.detail_content || ''
  loadAttachments()
}, { immediate: true })

async function loadAttachments() {
  if (!props.task.id) return
  try {
    const res = await attachmentApi.list(props.task.id)
    attachments.value = res.data
  } catch { /* ignore */ }
}

onMounted(loadAttachments)
</script>

<style scoped>
.task-detail {
  padding: 12px;
  background: #fafafa;
  border-radius: 6px;
}
.no-content {
  color: #c0c4cc;
  font-size: 13px;
}
</style>
