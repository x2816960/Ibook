<template>
  <el-drawer
    v-model="visible"
    :title="isEdit ? '编辑任务' : '新增任务'"
    size="600px"
  >
    <el-form ref="formRef" :model="form" :rules="rules" label-width="80px">
      <el-form-item label="标题" prop="title">
        <el-input v-model="form.title" placeholder="请输入任务标题" maxlength="100" show-word-limit />
      </el-form-item>
      <el-form-item label="描述" prop="description">
        <el-input v-model="form.description" type="textarea" :rows="3" placeholder="请输入任务描述（选填）" maxlength="2000" show-word-limit />
      </el-form-item>
      <el-form-item label="优先级" prop="priority">
        <el-radio-group v-model="form.priority">
          <el-radio-button v-for="p in PRIORITY_OPTIONS" :key="p.value" :value="p.value">
            {{ p.label }}
          </el-radio-button>
        </el-radio-group>
      </el-form-item>
      <el-form-item label="状态" prop="status">
        <el-radio-group v-model="form.status">
          <el-radio-button v-for="s in STATUS_OPTIONS" :key="s.value" :value="s.value">
            {{ s.label }}
          </el-radio-button>
        </el-radio-group>
      </el-form-item>
      <el-form-item label="截止时间">
        <div style="display: flex; align-items: center; gap: 12px; width: 100%">
          <el-date-picker
            v-model="form.due_date"
            type="datetime"
            placeholder="选择截止时间"
            :disabled="form.is_indefinite"
            style="flex: 1"
          />
          <el-checkbox v-model="form.is_indefinite" @change="onIndefiniteChange">无限期</el-checkbox>
        </div>
      </el-form-item>

      <!-- Detail Content (Markdown) - only show for edit mode or after first save -->
      <el-form-item v-if="isEdit || savedTaskId" label="详细信息">
        <div style="width: 100%">
          <el-button type="primary" text @click="detailDialogVisible = true">
            {{ form.detail_content ? '编辑详细信息' : '编写详细信息' }}
          </el-button>
          <span v-if="form.detail_content" style="color: #909399; font-size: 12px; margin-left: 8px">已填写</span>
        </div>
      </el-form-item>

      <!-- Detail Content Dialog -->
      <el-dialog
        v-model="detailDialogVisible"
        title="编写详细信息"
        width="90%"
        top="5vh"
        destroy-on-close
        append-to-body
      >
        <MarkdownEditor
          v-model="detailDraft"
          :task-id="savedTaskId || (task && task.id)"
          style="height: calc(80vh - 120px)"
        />
        <template #footer>
          <el-button @click="detailDialogVisible = false">取消</el-button>
          <el-button type="primary" @click="confirmDetail">确定</el-button>
        </template>
      </el-dialog>

      <!-- Attachments -->
      <el-form-item v-if="isEdit || savedTaskId" label="附件">
        <div style="width: 100%">
          <el-alert
            title="请在“编写详细信息”中上传图片、视频及附件"
            type="info"
            :closable="false"
            style="margin-bottom: 12px"
          />
          <AttachmentList
            :attachments="attachments"
            :editable="true"
            @deleted="loadAttachments"
          />
        </div>
      </el-form-item>
    </el-form>
    <template #footer>
      <el-button @click="visible = false">取消</el-button>
      <el-button type="primary" :loading="submitting" @click="handleSubmit">
        {{ isEdit ? '保存' : '创建' }}
      </el-button>
    </template>
  </el-drawer>
</template>

<script setup>
import { ref, reactive, watch, nextTick } from 'vue'
import { ElMessage } from 'element-plus'
import { useTaskStore } from '../../stores/task'
import { PRIORITY_OPTIONS, STATUS_OPTIONS } from '../../utils/constants'
import MarkdownEditor from '../markdown/MarkdownEditor.vue'
import AttachmentList from '../attachment/AttachmentList.vue'
import { attachmentApi } from '../../api/attachments'

const props = defineProps({
  modelValue: { type: Boolean, default: false },
  task: { type: Object, default: null },
})
const emit = defineEmits(['update:modelValue'])
const taskStore = useTaskStore()
const formRef = ref()
const submitting = ref(false)
const saving = ref(false)  // guard: 保存期间阻止 watch 重置表单
const detailDialogVisible = ref(false)
const detailDraft = ref('')
const savedTaskId = ref(null)
const attachments = ref([])

const visible = ref(props.modelValue)
watch(() => props.modelValue, (v) => { visible.value = v })
watch(visible, (v) => {
  emit('update:modelValue', v)
  if (!v) {
    resetForm()  // 抽屉关闭时同步重置，不等动画结束
  } else if (v && !props.task) {
    // 抽屉打开且是新增任务时，确保表单已重置
    isEdit.value = false  // 明确设置为新增模式
    savedTaskId.value = null  // 清除保存的任务ID
    resetForm()
  }
})

const isEdit = ref(false)

const form = reactive({
  title: '',
  description: '',
  detail_content: '',
  priority: '中',
  status: '待办',
  due_date: null,
  is_indefinite: false,
})

const rules = {
  title: [{ required: true, message: '请输入任务标题', trigger: 'blur' }],
}

watch(() => props.task, (t) => {
  if (saving.value) return  // 保存期间不重置表单
  if (t) {
    isEdit.value = true
    form.title = t.title
    form.description = t.description || ''
    form.detail_content = t.detail_content || ''
    form.priority = t.priority
    form.status = t.status
    form.due_date = t.due_date
    form.is_indefinite = t.is_indefinite
    savedTaskId.value = null
    loadAttachments()
  } else {
    isEdit.value = false
    resetForm()
  }
}, { immediate: true })

function resetForm() {
  form.title = ''
  form.description = ''
  form.detail_content = ''
  form.priority = '中'
  form.status = '待办'
  form.due_date = null
  form.is_indefinite = false
  detailDialogVisible.value = false
  savedTaskId.value = null
  attachments.value = []
  // 清除表单验证状态
  nextTick(() => {
    formRef.value?.clearValidate()
  })
}

function onIndefiniteChange(val) {
  if (val) form.due_date = null
}

watch(detailDialogVisible, (v) => {
  if (v) detailDraft.value = form.detail_content
})

function confirmDetail() {
  form.detail_content = detailDraft.value
  detailDialogVisible.value = false
}

async function loadAttachments() {
  const id = savedTaskId.value || (props.task && props.task.id)
  if (!id) return
  try {
    const res = await attachmentApi.list(id)
    attachments.value = res.data
  } catch { /* ignore */ }
}

async function handleSubmit() {
  const valid = await formRef.value.validate().catch(() => false)
  if (!valid) return  // 验证失败，不继续提交
  
  submitting.value = true
  saving.value = true  // 阻止 watch 在 store 刷新时重置表单
  try {
    const data = { ...form }
    if (data.is_indefinite) data.due_date = null
    if (!data.description) data.description = null
    if (!data.detail_content) data.detail_content = null

    if (isEdit.value) {
      const taskId = savedTaskId.value || props.task.id
      await taskStore.updateTask(taskId, data)
      ElMessage.success('任务已更新')
      visible.value = false
    } else {
      const result = await taskStore.createTask(data)
      savedTaskId.value = result.id
      isEdit.value = true  // 切换为编辑模式，避免重复创建
      ElMessage.success('任务已创建')
      visible.value = false  // 关闭抽屉
    }
  } finally {
    submitting.value = false
    saving.value = false
  }
}
</script>
