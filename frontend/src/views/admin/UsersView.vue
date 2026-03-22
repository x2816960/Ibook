<template>
  <div>
    <h2>用户管理</h2>
    <el-table :data="users" v-loading="loading" style="margin-top: 16px">
      <el-table-column prop="username" label="用户名" width="120" />
      <el-table-column prop="nickname" label="昵称" width="120" />
      <el-table-column prop="email" label="邮箱" />
      <el-table-column prop="is_active" label="状态" width="80">
        <template #default="{ row }">
          <el-tag :type="row.is_active ? 'success' : 'danger'" size="small">
            {{ row.is_active ? '正常' : '禁用' }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="locked_until" label="锁定" width="80">
        <template #default="{ row }">
          <el-tag v-if="row.locked_until" type="warning" size="small">已锁定</el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="created_at" label="注册时间" width="170">
        <template #default="{ row }">{{ formatDateTime(row.created_at) }}</template>
      </el-table-column>
      <el-table-column label="操作" width="220">
        <template #default="{ row }">
          <template v-if="!row.is_admin">
            <el-button size="small" @click="handleToggle(row)">
              {{ row.is_active ? '禁用' : '启用' }}
            </el-button>
            <el-button v-if="row.locked_until" size="small" type="warning" @click="handleUnlock(row)">解锁</el-button>
            <el-popconfirm title="确定重置密码？" @confirm="handleReset(row)">
              <template #reference>
                <el-button size="small" type="danger">重置密码</el-button>
              </template>
            </el-popconfirm>
          </template>
          <span v-else style="color: #909399; font-size: 13px">管理员</span>
        </template>
      </el-table-column>
    </el-table>
    <div style="margin-top: 16px; text-align: center">
      <el-pagination
        v-model:current-page="page"
        :total="total"
        :page-size="20"
        layout="prev, pager, next"
        @current-change="fetchUsers"
      />
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { adminApi } from '../../api/admin'
import { formatDateTime } from '../../utils/helpers'

const users = ref([])
const total = ref(0)
const page = ref(1)
const loading = ref(false)

async function fetchUsers() {
  loading.value = true
  try {
    const res = await adminApi.listUsers({ page: page.value, page_size: 20 })
    users.value = res.data.items
    total.value = res.data.total
  } finally {
    loading.value = false
  }
}

async function handleToggle(row) {
  await adminApi.toggleUser(row.id, { is_active: !row.is_active })
  ElMessage.success(row.is_active ? '已禁用' : '已启用')
  fetchUsers()
}

async function handleUnlock(row) {
  await adminApi.toggleUser(row.id, { unlock: true })
  ElMessage.success('已解锁')
  fetchUsers()
}

async function handleReset(row) {
  const res = await adminApi.resetPassword(row.id)
  ElMessageBox.alert(`新密码: ${res.data.new_password}`, '密码已重置', {
    confirmButtonText: '已复制',
  })
}

onMounted(fetchUsers)
</script>
