<template>
  <div class="task-detail">
    <MdPreview v-if="content" :modelValue="content" language="zh-CN" />
    <div v-else class="no-content">暂无详细信息</div>
    <AttachmentList v-if="attachments.length > 0" :attachments="attachments" />
  </div>
</template>

<script setup>
import { ref, watch, onMounted } from 'vue'
import { MdPreview } from 'md-editor-v3'
import 'md-editor-v3/lib/preview.css'
import AttachmentList from '../attachment/AttachmentList.vue'
import { attachmentApi } from '../../api/attachments'

const props = defineProps({
  task: { type: Object, required: true },
})

const content = ref(props.task.detail_content || '')
const attachments = ref([])

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
