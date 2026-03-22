<template>
  <div>
    <h2>系统配置</h2>
    <el-card style="margin-top: 16px; max-width: 600px" v-loading="loading">
      <el-form label-width="200px">
        <el-form-item v-for="item in configs" :key="item.key" :label="item.description || item.key">
          <el-input-number
            v-model="item.value"
            :min="1"
            style="width: 200px"
          />
          <span style="margin-left: 8px; color: #909399; font-size: 13px">
            {{ item.key.includes('size') ? 'MB' : '个' }}
          </span>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" :loading="saving" @click="handleSave">保存配置</el-button>
        </el-form-item>
      </el-form>
    </el-card>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { adminApi } from '../../api/admin'

const configs = ref([])
const loading = ref(false)
const saving = ref(false)

async function fetchConfig() {
  loading.value = true
  try {
    const res = await adminApi.getConfig()
    configs.value = res.data.map(c => ({ ...c, value: Number(c.value) }))
  } finally {
    loading.value = false
  }
}

async function handleSave() {
  saving.value = true
  try {
    await adminApi.updateConfig(configs.value.map(c => ({
      key: c.key,
      value: String(c.value),
      description: c.description,
    })))
    ElMessage.success('配置已保存')
  } finally {
    saving.value = false
  }
}

onMounted(fetchConfig)
</script>
