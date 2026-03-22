<template>
  <div class="page-container">
    <h2>个人设置</h2>
    <el-card style="max-width: 500px; margin-top: 16px">
      <el-form ref="profileFormRef" :model="profileForm" label-width="80px">
        <el-form-item label="用户名">
          <el-input :value="authStore.user?.username" disabled />
        </el-form-item>
        <el-form-item label="昵称">
          <el-input v-model="profileForm.nickname" placeholder="设置昵称" />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" :loading="profileLoading" @click="handleUpdateProfile">保存昵称</el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <el-card style="max-width: 500px; margin-top: 16px">
      <template #header><span>修改密码</span></template>
      <el-form ref="pwdFormRef" :model="pwdForm" :rules="pwdRules" label-width="80px">
        <el-form-item label="旧密码" prop="old_password">
          <el-input v-model="pwdForm.old_password" type="password" show-password />
        </el-form-item>
        <el-form-item label="新密码" prop="new_password">
          <el-input v-model="pwdForm.new_password" type="password" show-password />
        </el-form-item>
        <el-form-item label="确认密码" prop="confirm">
          <el-input v-model="pwdForm.confirm" type="password" show-password />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" :loading="pwdLoading" @click="handleChangePassword">修改密码</el-button>
        </el-form-item>
      </el-form>
    </el-card>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { useAuthStore } from '../stores/auth'
import { passwordRules } from '../utils/validators'

const authStore = useAuthStore()
const profileFormRef = ref()
const pwdFormRef = ref()
const profileLoading = ref(false)
const pwdLoading = ref(false)

const profileForm = reactive({
  nickname: authStore.user?.nickname || '',
})

onMounted(() => {
  profileForm.nickname = authStore.user?.nickname || ''
})

const pwdForm = reactive({ old_password: '', new_password: '', confirm: '' })
const pwdRules = {
  old_password: [{ required: true, message: '请输入旧密码', trigger: 'blur' }],
  new_password: passwordRules,
  confirm: [
    { required: true, message: '请确认新密码', trigger: 'blur' },
    {
      validator: (r, v, cb) => {
        if (v !== pwdForm.new_password) cb(new Error('两次输入的密码不一致'))
        else cb()
      },
      trigger: 'blur',
    },
  ],
}

async function handleUpdateProfile() {
  profileLoading.value = true
  try {
    await authStore.updateProfile({ nickname: profileForm.nickname })
    ElMessage.success('昵称已更新')
  } finally {
    profileLoading.value = false
  }
}

async function handleChangePassword() {
  await pwdFormRef.value.validate()
  pwdLoading.value = true
  try {
    await authStore.changePassword({
      old_password: pwdForm.old_password,
      new_password: pwdForm.new_password,
    })
    ElMessage.success('密码已修改')
    pwdForm.old_password = ''
    pwdForm.new_password = ''
    pwdForm.confirm = ''
  } finally {
    pwdLoading.value = false
  }
}
</script>
