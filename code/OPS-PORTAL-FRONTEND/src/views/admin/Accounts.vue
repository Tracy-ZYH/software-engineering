<template>
  <div>
    <div class="page-header">
      <h2>账号管理</h2>
      <button class="btn-primary" @click="openCreate">+ 新建账号</button>
    </div>

    <div class="toolbar">
      <input v-model="search.keyword" placeholder="搜索用户名/姓名" @keyup.enter="page=1;loadAccounts()" />
      <select v-model="search.role" @change="page=1;loadAccounts()">
        <option value="">全部角色</option>
        <option value="admin">管理员</option>
        <option value="operator">运维人员</option>
      </select>
      <select v-model="search.status" @change="page=1;loadAccounts()">
        <option value="">全部状态</option>
        <option value="active">正常</option>
        <option value="frozen">已冻结</option>
      </select>
      <button @click="page=1;loadAccounts()">搜索</button>
    </div>

    <div class="table-wrap">
      <table>
        <thead>
          <tr><th>ID</th><th>用户名</th><th>姓名</th><th>部门</th><th>角色</th><th>状态</th><th>操作</th></tr>
        </thead>
        <tbody>
          <tr v-if="loading"><td colspan="7" class="center">加载中...</td></tr>
          <tr v-else-if="accounts.length === 0"><td colspan="7" class="center">暂无账号</td></tr>
          <tr v-for="a in accounts" :key="a.id">
            <td>#{{ a.id }}</td>
            <td>{{ a.username }}</td>
            <td>{{ a.real_name || '-' }}</td>
            <td>{{ a.department || '-' }}</td>
            <td><span class="badge">{{ a.role === 'admin' ? '管理员' : '运维人员' }}</span></td>
            <td><span :class="'badge badge-' + a.status">{{ a.status === 'active' ? '正常' : '已冻结' }}</span></td>
            <td>
              <button class="btn-sm" @click="openEdit(a)">编辑</button>
              <button class="btn-sm" @click="toggleStatus(a)">{{ a.status === 'active' ? '冻结' : '解冻' }}</button>
              <button class="btn-sm btn-del" @click="deleteAccount(a)">删除</button>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <div class="pagination">
      <button :disabled="page <= 1" @click="page--; loadAccounts()">上一页</button>
      <span>第 {{ page }} 页 / 共 {{ totalPages }} 页</span>
      <button :disabled="page >= totalPages" @click="page++; loadAccounts()">下一页</button>
    </div>

    <!-- 新建/编辑弹窗 -->
    <div v-if="showModal" class="modal-mask">
      <div class="modal">
        <h3>{{ isEdit ? '编辑账号' : '新建账号' }}</h3>
        <label>用户名</label>
        <input v-model="form.username" :disabled="isEdit" placeholder="用户名" />
        <label>{{ isEdit ? '新密码（不填则不修改）' : '密码' }}</label>
        <input v-model="form.password" type="password" placeholder="密码" />
        <label>真实姓名</label>
        <input v-model="form.real_name" placeholder="真实姓名" />
        <label>手机号</label>
        <input v-model="form.phone" placeholder="手机号" />
        <label>部门</label>
        <input v-model="form.department" placeholder="部门" />
        <label>角色</label>
        <select v-model="form.role">
          <option value="operator">运维人员</option>
          <option value="admin">管理员</option>
        </select>
        <div class="modal-footer">
          <button @click="showModal = false">取消</button>
          <button class="btn-primary" @click="submitForm" :disabled="formLoading">
            {{ formLoading ? '提交中...' : '确认' }}
          </button>
        </div>
        <p v-if="formMsg" :class="formOk ? 'success' : 'error'">{{ formMsg }}</p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, computed } from 'vue'
import request from '../../api/request'

const accounts = ref([])
const loading = ref(false)
const total = ref(0)
const page = ref(1)
const pageSize = 10
const search = reactive({ keyword: '', role: '', status: '' })
const totalPages = computed(() => Math.max(1, Math.ceil(total.value / pageSize)))

const showModal = ref(false)
const isEdit = ref(false)
const editId = ref(null)
const form = reactive({ username: '', password: '', real_name: '', phone: '', department: '', role: 'operator' })
const formLoading = ref(false)
const formMsg = ref('')
const formOk = ref(false)

const loadAccounts = async () => {
  loading.value = true
  try {
    const res = await request.get('/api/accounts', {
      params: { page: page.value, page_size: pageSize, keyword: search.keyword || undefined, role: search.role || undefined, status: search.status || undefined }
    })
    accounts.value = res.data.items || res.data.accounts || []
    total.value = res.data.total || 0
  } catch { accounts.value = [] } finally { loading.value = false }
}

const openCreate = () => {
  isEdit.value = false
  Object.assign(form, { username: '', password: '', real_name: '', phone: '', department: '', role: 'operator' })
  formMsg.value = ''
  showModal.value = true
}

const openEdit = (a) => {
  isEdit.value = true
  editId.value = a.id
  Object.assign(form, { username: a.username, password: '', real_name: a.real_name || '', phone: a.phone || '', department: a.department || '', role: a.role })
  formMsg.value = ''
  showModal.value = true
}

const submitForm = async () => {
  // 前端校验必填字段
  if (!isEdit.value && !form.username) { formMsg.value = '❌ 请输入用户名'; formLoading.value = false; return }
  if (!isEdit.value && !form.password) { formMsg.value = '❌ 请输入密码'; formLoading.value = false; return }
  if (!form.real_name) { formMsg.value = '❌ 请输入真实姓名'; formLoading.value = false; return }
  formLoading.value = true
  formMsg.value = ''
  try {
    const payload = { ...form }
    if (isEdit.value && !payload.password) delete payload.password
    if (isEdit.value) {
      await request.put(`/api/accounts/${editId.value}`, payload)
    } else {
      await request.post('/api/accounts', payload)
    }
    formOk.value = true
    formMsg.value = '✅ 操作成功'
    setTimeout(() => { showModal.value = false; loadAccounts() }, 800)
  } catch (err) {
    formOk.value = false
    const _errDetail = err.response?.data?.detail
      const _errMsg = typeof _errDetail === 'string' ? _errDetail : Array.isArray(_errDetail) ? _errDetail.map(e => e.msg || e.message).join('; ') : err.message
      formMsg.value = '❌ ' + _errMsg
  } finally { formLoading.value = false }
}

const toggleStatus = async (a) => {
  const next = a.status === 'active' ? 'frozen' : 'active'
  if (!confirm(`确认${next === 'frozen' ? '冻结' : '解冻'}账号 ${a.username}？`)) return
  try {
    await request.put(`/api/accounts/${a.id}/status`, { status: next })
    loadAccounts()
  } catch (err) { alert('操作失败：' + (typeof err.response?.data?.detail === 'string' ? err.response.data.detail : err.message)) }
}

const deleteAccount = async (a) => {
  if (!confirm(`确认删除账号 ${a.username}？此操作不可恢复！`)) return
  try {
    await request.delete(`/api/accounts/${a.id}`)
    loadAccounts()
  } catch (err) { alert('删除失败：' + (typeof err.response?.data?.detail === 'string' ? err.response.data.detail : err.message)) }
}

onMounted(loadAccounts)
</script>

<style scoped>
.page-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 24px; }
h2 { margin: 0; font-size: 1.2rem; font-weight: 500; color: var(--text-heading); letter-spacing: 1px; }
.btn-primary { padding: 8px 20px; background: var(--blue); color: #fff; border: none; border-radius: 8px; font-size: 13px; cursor: pointer; transition: background 0.2s; }
.btn-primary:hover { background: var(--blue-hover); }

.toolbar { display: flex; gap: 10px; margin-bottom: 20px; }
.toolbar input, .toolbar select { padding: 8px 14px; background: var(--bg-solid); color: var(--text-primary); border: 0.5px solid var(--border); border-radius: 8px; font-size: 13px; outline: none; transition: border-color 0.2s; }
.toolbar input { flex: 1; }
.toolbar input:focus, .toolbar select:focus { border-color: var(--blue); }
.toolbar button { padding: 8px 20px; background: var(--blue); color: #fff; border: none; border-radius: 8px; font-size: 13px; cursor: pointer; }
.toolbar button:hover { background: var(--blue-hover); }

.table-wrap { background: var(--bg-solid); border: 0.5px solid var(--border); border-radius: 12px; overflow: hidden; }
table { width: 100%; border-collapse: collapse; font-size: 13px; }
th { background: var(--bg-input); padding: 11px 14px; text-align: left; color: var(--text-secondary); font-weight: 500; font-size: 12px; letter-spacing: 0.5px; border-bottom: 0.5px solid var(--border); }
td { padding: 11px 14px; border-bottom: 0.5px solid #f0f4f8; color: var(--text-table); vertical-align: middle; }
tr:last-child td { border-bottom: none; }
tr:hover td { background: var(--bg-hover); }
.center { text-align: center; color: var(--text-muted); padding: 40px; }

.badge { padding: 3px 10px; border-radius: 999px; font-size: 11px; font-weight: 500; background: var(--bg-input); color: var(--blue); }
.badge-active { background: #ecfdf5; color: var(--resolved-text); }
.badge-frozen { background: #fef2f2; color: var(--error); }

.btn-sm { padding: 4px 12px; font-size: 12px; border-radius: 6px; cursor: pointer; margin-right: 6px; border: 0.5px solid var(--border-input); background: var(--bg-input); color: var(--blue); transition: all 0.15s; }
.btn-sm:hover { background: var(--border); }
.btn-del { background: #fef2f2; color: var(--error); border-color: #fecaca; }
.btn-del:hover { background: #fee2e2; }

.pagination { display: flex; align-items: center; gap: 16px; margin-top: 20px; justify-content: center; font-size: 13px; color: var(--text-muted); }
.pagination button { padding: 6px 18px; background: var(--bg-solid); color: var(--text-secondary); border: 0.5px solid var(--border); border-radius: 8px; cursor: pointer; transition: all 0.15s; }
.pagination button:hover:not(:disabled) { background: var(--bg-card); }
.pagination button:disabled { opacity: 0.3; cursor: not-allowed; }

.modal-mask { position: fixed; inset: 0; background: rgba(0,0,0,0.7); display: flex; align-items: center; justify-content: center; z-index: 100; }
.modal { background: var(--bg-solid); border: 0.5px solid var(--border); border-radius: 14px; padding: 28px 32px; width: 440px; display: flex; flex-direction: column; gap: 12px; max-height: 90vh; overflow-y: auto; }
.modal h3 { margin: 0; font-size: 1rem; font-weight: 500; color: var(--text-heading); }
label { font-size: 12px; color: var(--text-secondary); letter-spacing: 0.5px; }
.modal input, .modal select { padding: 10px 12px; background: var(--bg-input); color: var(--text-primary); border: 0.5px solid var(--border); border-radius: 8px; font-size: 14px; outline: none; transition: border-color 0.2s; }
.modal input:focus, .modal select:focus { border-color: var(--blue); }
.modal input:disabled { opacity: 0.4; }
.modal-footer { display: flex; justify-content: flex-end; gap: 10px; margin-top: 4px; }
.modal-footer button { padding: 8px 22px; border: 0.5px solid var(--border); border-radius: 8px; cursor: pointer; background: var(--bg-input); color: var(--text-secondary); font-size: 13px; transition: all 0.15s; }
.modal-footer button:hover { background: var(--bg-card); }
.btn-primary { background: var(--blue) !important; color: #fff !important; border-color: var(--blue) !important; }
.btn-primary:hover { background: var(--blue-hover) !important; }
.btn-primary:disabled { opacity: 0.5; cursor: not-allowed; }
.success { color: var(--resolved-text); font-size: 13px; }
.error { color: var(--error); font-size: 13px; }
</style>


