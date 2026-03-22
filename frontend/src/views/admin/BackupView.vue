<template>
  <div>
    <h2>备份恢复</h2>

    <el-row :gutter="16" style="margin-top: 16px">
      <el-col :span="12">
        <el-card>
          <template #header><span>数据导出</span></template>
          <p style="color: #909399; font-size: 13px; margin-bottom: 16px">
            导出完整数据库及所有附件为压缩包
          </p>
          <el-button type="primary" :loading="exporting" @click="handleExport">
            一键导出
          </el-button>
        </el-card>
      </el-col>
      <el-col :span="12">
        <el-card>
          <template #header><span>数据导入</span></template>
          <el-alert type="warning" :closable="false" style="margin-bottom: 16px">
            导入将覆盖当前所有数据，请谨慎操作
          </el-alert>
          <el-upload
            :auto-upload="false"
            :on-change="handleFileChange"
            :limit="1"
            accept=".tar.gz,.gz"
          >
            <el-button>选择备份文件</el-button>
          </el-upload>
          <el-button
            v-if="importFile"
            type="danger"
            :loading="importing"
            style="margin-top: 12px"
            @click="handleImport"
          >
            确认导入
          </el-button>
        </el-card>
      </el-col>
    </el-row>

        <el-card style="margin-top: 16px">
      <template #header>
        <div style="display: flex; justify-content: space-between; align-items: center">
          <span>备份历史</span>
          <el-button
            v-if="backups.length > 0"
            type="danger"
            size="small"
            @click="handleDeleteAll"
          >
            一键删除所有
          </el-button>
        </div>
      </template>
      <el-table :data="backups" v-loading="listLoading">
        <el-table-column prop="filename" label="文件名" />
        <el-table-column prop="size" label="大小" width="120">
          <template #default="{ row }">{{ formatFileSize(row.size) }}</template>
        </el-table-column>
        <el-table-column prop="created_at" label="创建时间" width="180">
          <template #default="{ row }">{{ formatDateTime(row.created_at) }}</template>
        </el-table-column>
        <el-table-column label="操作" width="150">
          <template #default="{ row }">
            <el-button size="small" text @click="handleDownload(row.filename)">下载</el-button>
            <el-button size="small" text type="danger" @click="handleDelete(row.filename)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { backupApi } from '../../api/backup'
import { formatFileSize, formatDateTime } from '../../utils/helpers'

const backups = ref([])
const listLoading = ref(false)
const exporting = ref(false)
const importing = ref(false)
const importFile = ref(null)

async function fetchBackups() {
  listLoading.value = true
  try {
    const res = await backupApi.list()
    backups.value = res.data
  } finally {
    listLoading.value = false
  }
}

async function handleExport() {
  exporting.value = true
  try {
    const res = await backupApi.export()
    ElMessage.success('备份已创建: ' + res.data.filename)
    fetchBackups()
  } finally {
    exporting.value = false
  }
}

function handleFileChange(file) {
  importFile.value = file.raw
}

async function handleImport() {
  if (!importFile.value) return
  importing.value = true
  try {
    await backupApi.import(importFile.value)
    ElMessage.success('数据恢复成功，请刷新页面')
    importFile.value = null
  } finally {
    importing.value = false
  }
}

async function handleDownload(filename) {
  try {
    const response = await backupApi.download(filename)
    const blob = new Blob([response.data], { type: 'application/gzip' })
    const url = window.URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = url
    link.download = filename
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
    window.URL.revokeObjectURL(url)
  } catch (error) {
    ElMessage.error('下载失败')
  }
}

async function handleDelete(filename) {
  try {
    await backupApi.delete(filename)
    ElMessage.success('删除成功')
    fetchBackups()
  } catch (error) {
    ElMessage.error('删除失败')
  }
}

async function handleDeleteAll() {
  try {
    await backupApi.deleteAll()
    ElMessage.success('删除成功')
    fetchBackups()
  } catch (error) {
    ElMessage.error('删除失败')
  }
}

onMounted(fetchBackups)
</script>
