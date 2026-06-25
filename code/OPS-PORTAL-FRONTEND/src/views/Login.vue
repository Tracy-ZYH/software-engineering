<template>
  <div class="login-page">
    <div class="login-box">
      <h2>运维后台登录</h2>
      <input v-model="form.username" placeholder="用户名" @keyup.enter="login" />
      <input v-model="form.password" type="password" placeholder="密码" @keyup.enter="login" />
      <button @click="login" :disabled="loading">
        {{ loading ? '登录中...' : '登录' }}
      </button>
      <p v-if="error" class="error">{{ error }}</p>
      <router-link to="/" class="back">← 返回前台</router-link>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import request from '../api/request'

const router = useRouter()
const form = reactive({ username: '', password: '' })
const loading = ref(false)
const error = ref('')

const login = async () => {
  if (!form.username || !form.password) { error.value = '请填写用户名和密码'; return }
  loading.value = true
  error.value = ''
  try {
    const res = await request.post('/api/auth/login', {
      username: form.username,
      password: form.password
    })
    localStorage.setItem('token', res.data.access_token)
    localStorage.setItem('username', form.username)
    router.push('/admin/tickets')
  } catch (err) {
    error.value = err.response?.data?.detail || '用户名或密码错误'
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.login-page { min-height: 100vh; display: flex; align-items: center; justify-content: center; background: var(--bg-page); }
.login-box { background: var(--bg-card); border: 1px solid var(--border-strong); border-radius: 12px; padding: 40px; width: 360px; display: flex; flex-direction: column; gap: 16px; }
h2 { text-align: center; color: var(--text-primary); margin: 0 0 8px; }
input { padding: 11px 14px; background: var(--bg-solid); color: var(--text-primary); border: 1px solid var(--border-input); border-radius: 6px; font-size: 15px; }
button { padding: 12px; background: var(--blue); color: white; border: none; border-radius: 6px; font-size: 15px; cursor: pointer; }
button:disabled { opacity: 0.5; }
.error { color: var(--error); text-align: center; margin: 0; font-size: 14px; }
.back { text-align: center; color: var(--text-secondary); font-size: 13px; text-decoration: none; }
</style>

