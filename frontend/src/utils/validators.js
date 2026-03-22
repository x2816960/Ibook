export const usernameRules = [
  { required: true, message: '请输入用户名', trigger: 'blur' },
  { min: 4, max: 20, message: '用户名长度为4-20位', trigger: 'blur' },
  { pattern: /^[a-zA-Z0-9_]+$/, message: '用户名只能包含字母、数字、下划线', trigger: 'blur' },
]

export const passwordRules = [
  { required: true, message: '请输入密码', trigger: 'blur' },
  { min: 8, max: 32, message: '密码长度为8-32位', trigger: 'blur' },
  {
    validator: (rule, value, callback) => {
      if (!/[a-zA-Z]/.test(value) || !/\d/.test(value)) {
        callback(new Error('密码需要同时包含字母和数字'))
      } else {
        callback()
      }
    },
    trigger: 'blur',
  },
]
