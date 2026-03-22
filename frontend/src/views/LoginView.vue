<template>
  <div class="login-container">
    <el-card class="login-card" shadow="hover">
      <template #header>
        <h2 class="login-title">Ibook - 登录</h2>
      </template>
      <el-form ref="formRef" :model="form" :rules="rules" label-width="0" @submit.prevent="handleLogin">
        <el-form-item prop="username">
          <el-input v-model="form.username" placeholder="用户名或邮箱" prefix-icon="User" size="large" />
        </el-form-item>
        <el-form-item prop="password">
          <el-input v-model="form.password" type="password" placeholder="密码" prefix-icon="Lock" size="large" show-password />
        </el-form-item>
        <el-form-item>
          <el-checkbox v-model="form.remember_me">记住我</el-checkbox>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" size="large" :loading="loading" style="width: 100%" native-type="submit">
            登录
          </el-button>
        </el-form-item>
        <div class="login-footer">
          还没有账户？<router-link to="/register">立即注册</router-link>
        </div>
      </el-form>
    </el-card>

    <!-- Change Password Dialog -->
    <el-dialog v-model="showChangePassword" title="首次登录请修改密码" :close-on-click-modal="false" :close-on-press-escape="false" :show-close="false" width="400px">
      <el-form ref="pwdFormRef" :model="pwdForm" :rules="pwdRules" label-width="80px">
        <el-form-item label="新密码" prop="new_password">
          <el-input v-model="pwdForm.new_password" type="password" show-password />
        </el-form-item>
        <el-form-item label="确认密码" prop="confirm_password">
          <el-input v-model="pwdForm.confirm_password" type="password" show-password />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button type="primary" :loading="pwdLoading" @click="handleChangePassword">确认修改</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { useAuthStore } from '../stores/auth'
import { passwordRules } from '../utils/validators'

const router = useRouter()
const authStore = useAuthStore()
const formRef = ref()
const loading = ref(false)
const showChangePassword = ref(false)
const pwdFormRef = ref()
const pwdLoading = ref(false)

const form = reactive({
  username: '',
  password: '',
  remember_me: false,
})

const rules = {
  username: [{ required: true, message: '请输入用户名', trigger: 'blur' }],
  password: [{ required: true, message: '请输入密码', trigger: 'blur' }],
}

const pwdForm = reactive({ new_password: '', confirm_password: '' })
const pwdRules = {
  new_password: passwordRules,
  confirm_password: [
    { required: true, message: '请确认密码', trigger: 'blur' },
    {
      validator: (rule, value, cb) => {
        if (value !== pwdForm.new_password) cb(new Error('两次输入的密码不一致'))
        else cb()
      },
      trigger: 'blur',
    },
  ],
}

async function handleLogin() {
  await formRef.value.validate()
  loading.value = true
  try {
    const data = await authStore.login(form)
    if (data.must_change_password) {
      showChangePassword.value = true
    } else {
      ElMessage.success('登录成功')
      router.push('/tasks')
    }
  } finally {
    loading.value = false
  }
}

async function handleChangePassword() {
  await pwdFormRef.value.validate()
  pwdLoading.value = true
  try {
    await authStore.changePassword({
      old_password: form.password,
      new_password: pwdForm.new_password,
    })
    showChangePassword.value = false
    ElMessage.success('密码修改成功')
    router.push('/tasks')
  } finally {
    pwdLoading.value = false
  }
}
</script>

<style scoped>
.login-container {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 100vh;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}
.login-card {
  width: 420px;
}
.login-title {
  text-align: center;
  color: #303133;
  margin: 0;
}
.login-footer {
  text-align: center;
  color: #909399;
}
</style>
