<template>
  <div class="layout">
    <aside class="sidebar">
      <div class="logo">运维后台</div>
<nav>
  <router-link to="/admin/tickets">🎫 工单管理</router-link>
  <router-link to="/admin/accounts">👤 账号管理</router-link>
  <router-link to="/admin/knowledge">📚 知识库</router-link>
  <router-link to="/" class="back-link">← 返回前台</router-link>
</nav>
<div class="theme-toggle-sidebar" @click="handleToggleTheme" :title="currentTheme === 'light' ? '深色主题' : '浅色主题'">
    <i :class="currentTheme === 'light' ? 'ti ti-moon' : 'ti ti-sun'"></i>
    <span>{{ currentTheme === 'light' ? '深色模式' : '浅色模式' }}</span>
</div>
      <div class="user-info">
        <span>{{ username }}</span>
        <button @click="logout">退出</button>
      </div>
    </aside>
    <main class="main">
      <router-view />
    </main>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'

import { getSavedTheme, toggleTheme } from '../../theme'
const router = useRouter()
const username = ref(localStorage.getItem('username') || 'admin')

const currentTheme = ref(getSavedTheme())
const handleToggleTheme = () => { currentTheme.value = toggleTheme() }

const logout = () => {
  localStorage.removeItem('token')
  localStorage.removeItem('username')
  router.push('/login')
}
</script>

<style scoped>
@import url('https://cdn.jsdelivr.net/npm/@tabler/icons-webfont@latest/tabler-icons.min.css');

.layout { display: flex; min-height: 100vh; background: var(--bg-page); color: var(--text-primary); }

.sidebar { width: 220px; background: var(--bg-sidebar); display: flex; flex-direction: column; flex-shrink: 0; border-right: 0.5px solid var(--border); }

.logo { font-size: 1rem; font-weight: 500; text-align: center; padding: 28px 20px 24px; border-bottom: 0.5px solid var(--border); letter-spacing: 3px; color: var(--text-heading); }

nav { display: flex; flex-direction: column; padding: 12px 0; flex: 1; }

nav a { padding: 11px 24px; color: var(--text-secondary); text-decoration: none; font-size: 14px; transition: all 0.15s; border-left: 3px solid transparent; }
nav a:hover { background: var(--bg-solid); color: var(--text-heading); }
nav a.router-link-active { background: var(--bg-solid); color: var(--blue); border-left: 3px solid var(--blue); }

.back-link { margin-top: auto; border-top: 0.5px solid var(--border); color: var(--text-muted) !important; font-size: 13px; }
.back-link:hover { color: var(--text-secondary) !important; }

.user-info { padding: 14px 20px; border-top: 0.5px solid var(--border); display: flex; align-items: center; justify-content: space-between; font-size: 13px; color: var(--text-secondary); }
.user-info button { padding: 4px 10px; background: transparent; color: var(--text-secondary); border: 0.5px solid var(--border-input); border-radius: 6px; cursor: pointer; font-size: 12px; transition: all 0.15s; }
.user-info button:hover { color: var(--error); border-color: #fca5a5; }

.main { flex: 1; padding: 36px 40px; overflow-y: auto; background: var(--bg-page); }

.theme-toggle-sidebar {
  padding: 11px 24px;
  color: var(--text-secondary);
  font-size: 14px;
  cursor: pointer;
  transition: all 0.15s;
  display: flex;
  align-items: center;
  gap: 8px;
  border-left: 3px solid transparent;
}
.theme-toggle-sidebar:hover {
  background: var(--bg-solid);
  color: var(--text-heading);
}

</style>

