<template>
  <div>
    <div class="page-header">
      <h2>工单管理</h2>
    </div>

    <!-- 搜索栏 -->
    <div class="toolbar">
      <input v-model="search.keyword" placeholder="搜索问题" @keyup.enter="loadTickets" />
      <select v-model="search.status" @change="loadTickets">
        <option value="">全部状态</option>
        <option value="pending">待处理</option>
        <option value="processing">处理中</option>
        <option value="resolved">已解决</option>
      </select>
      <button @click="loadTickets">搜索</button>
    </div>

    <!-- 工单列表 -->
    <div class="table-wrap">
      <table>
        <thead>
          <tr>
            <th>ID</th><th>问题</th><th>联系方式</th><th>状态</th><th>创建时间</th><th>操作</th>
          </tr>
        </thead>
        <tbody>
          <tr v-if="loading"><td colspan="6" class="center">加载中...</td></tr>
          <tr v-else-if="tickets.length === 0"><td colspan="6" class="center">暂无工单</td></tr>
          <tr v-for="t in tickets" :key="t.id">
            <td>#{{ t.id }}</td>
            <td class="td-question">{{ t.question }}</td>
            <td>{{ t.contact_info || '-' }}</td>
            <td><span :class="'badge badge-' + t.status">{{ statusLabel(t.status) }}</span></td>
            <td>{{ formatDate(t.created_at) }}</td>
            <td>
              <button class="btn-sm" @click="openProcess(t)">处理</button>
              <button class="btn-sm btn-sync" @click="syncKnowledge(t)" v-if="t.status === 'resolved' && !t.synced">同步知识库</button>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- 分页 -->
    <div class="pagination">
      <button :disabled="page <= 1" @click="page--; loadTickets()">上一页</button>
      <span>第 {{ page }} 页 / 共 {{ totalPages }} 页</span>
      <button :disabled="page >= totalPages" @click="page++; loadTickets()">下一页</button>
    </div>

    <!-- 处理工单弹窗 -->
    <div v-if="showModal" class="modal-mask" @click.self="showModal = false">
      <div class="modal">
        <h3>处理工单 #{{ current.id }}</h3>
        <p class="modal-question">{{ current.question }}</p>
        <label>状态</label>
        <select v-model="processForm.status">
          <option value="processing">处理中</option>
          <option value="resolved">已解决</option>
        </select>
        <label>处理方案</label>
        <textarea v-model="processForm.solution" placeholder="请填写处理方案..." rows="5"></textarea>
        <div class="modal-footer">
          <button @click="showModal = false">取消</button>
          <button class="btn-primary" @click="submitProcess" :disabled="processLoading">
            {{ processLoading ? '提交中...' : '确认提交' }}
          </button>
        </div>
        <p v-if="processMsg" :class="processOk ? 'success' : 'error'">{{ processMsg }}</p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, computed } from 'vue'
import request from '../../api/request'

const tickets = ref([])
const loading = ref(false)
const total = ref(0)
const page = ref(1)
const pageSize = 10
const search = reactive({ keyword: '', status: '' })
const totalPages = computed(() => Math.max(1, Math.ceil(total.value / pageSize)))

const showModal = ref(false)
const current = ref({})
const processForm = reactive({ status: 'processing', solution: '' })
const processLoading = ref(false)
const processMsg = ref('')
const processOk = ref(false)

const statusLabel = s => ({ pending: '待处理', processing: '处理中', resolved: '已解决' }[s] || s)
const formatDate = s => s ? s.slice(0, 16).replace('T', ' ') : '-'

const loadTickets = async () => {
  loading.value = true
  try {
    const res = await request.get('/api/tickets', {
      params: { page: page.value, page_size: pageSize, keyword: search.keyword, status: search.status || undefined }
    })
    tickets.value = res.data.items || res.data.tickets || []
    total.value = res.data.total || 0
  } catch { tickets.value = [] } finally { loading.value = false }
}

const openProcess = async (t) => {
  processMsg.value = ''
  processForm.status = t.status === 'resolved' ? 'resolved' : 'processing'
  processForm.solution = ''
  current.value = t
  showModal.value = true  // 先打开弹窗，避免等待感

  try {
    // 从详情接口拿完整数据（列表接口可能不含 solution）
    const res = await request.get(`/api/tickets/${t.id}`)
    current.value = res.data
    processForm.status = res.data.status === 'resolved' ? 'resolved' : 'processing'
    processForm.solution = res.data.resolution || ''
    console.log('工单详情:', res.data)  // 确认字段名
  } catch (err) {
    console.error('获取详情失败', err)
  }
}

const submitProcess = async () => {
  processLoading.value = true
  processMsg.value = ''
  try {
    const payload = {
  status: processForm.status,
  resolution: processForm.solution}

    console.log('提交处理数据:', payload)  // ← 加这行
    await request.put(`/api/tickets/${current.value.id}`, payload)
    processOk.value = true
    processMsg.value = '✅ 处理成功'
    setTimeout(() => { showModal.value = false; loadTickets() }, 800)
  } catch (err) {
    processOk.value = false
    processMsg.value = '❌ 提交失败：' + (err.response?.data?.detail || err.message)
    console.log('提交失败响应:', err.response?.data)  // ← 加这行
  } finally { processLoading.value = false }
}

const syncKnowledge = async (t) => {
  if (!confirm(`确认将工单 #${t.id} 同步到知识库？`)) return
  try {
    // 先获取工单详情拿到 solution
    const detail = await request.get(`/api/tickets/${t.id}`)
    const solution = detail.data.resolution || ''
    if (!solution) {
      alert('该工单暂无处理方案，请先在"处理"中填写方案后再同步')
      return
    }
    await request.post(`/api/tickets/${t.id}/sync-knowledge`, {
      solution: solution
    })
    alert('✅ 同步成功')
    loadTickets()
  } catch (err) {
    alert('❌ 同步失败：' + (err.response?.data?.detail || err.message))
  }
}

onMounted(loadTickets)
</script>

<style scoped>
.page-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 24px; }
h2 { margin: 0; font-size: 1.2rem; font-weight: 500; color: var(--text-heading); letter-spacing: 1px; }

.toolbar { display: flex; gap: 10px; margin-bottom: 20px; }
.toolbar input, .toolbar select {
  padding: 8px 14px; background: var(--bg-solid); color: var(--text-primary);
  border: 0.5px solid var(--border); border-radius: 8px; font-size: 13px; outline: none;
  transition: border-color 0.2s;
}
.toolbar input { flex: 1; }
.toolbar input:focus, .toolbar select:focus { border-color: var(--blue); }
.toolbar button {
  padding: 8px 20px; background: var(--blue); color: #fff;
  border: none; border-radius: 8px; font-size: 13px; cursor: pointer;
  transition: background 0.2s;
}
.toolbar button:hover { background: var(--blue-hover); }

.table-wrap { background: var(--bg-solid); border: 0.5px solid var(--border); border-radius: 12px; overflow: hidden; }
table { width: 100%; border-collapse: collapse; font-size: 13px; }
th { background: var(--bg-input); padding: 11px 14px; text-align: left; color: var(--text-secondary); font-weight: 500; font-size: 12px; letter-spacing: 0.5px; border-bottom: 0.5px solid var(--border); }
td { padding: 11px 14px; border-bottom: 0.5px solid #f0f4f8; color: var(--text-table); vertical-align: middle; }
tr:last-child td { border-bottom: none; }
tr:hover td { background: var(--bg-hover); }
.td-question { max-width: 240px; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
.center { text-align: center; color: var(--text-muted); padding: 40px; }

.badge { padding: 3px 10px; border-radius: 999px; font-size: 11px; font-weight: 500; }
.badge-pending  { background: #fefce8; color: var(--pending-text); }
.badge-processing { background: #e8f0fe; color: var(--processing-text); }
.badge-resolved { background: #ecfdf5; color: var(--resolved-text); }

.btn-sm {
  padding: 4px 12px; font-size: 12px; border-radius: 6px; cursor: pointer;
  margin-right: 6px; border: 0.5px solid var(--border-input);
  background: var(--bg-input); color: var(--blue); transition: all 0.15s;
}
.btn-sm:hover { background: var(--border); color: var(--blue); }
.btn-sync { background: #f0fdf0; color: var(--success); border-color: #bbf7d0; }
.btn-sync:hover { background: #dcfce7; }

.pagination { display: flex; align-items: center; gap: 16px; margin-top: 20px; justify-content: center; font-size: 13px; color: var(--text-muted); }
.pagination button { padding: 6px 18px; background: var(--bg-solid); color: var(--text-secondary); border: 0.5px solid var(--border); border-radius: 8px; cursor: pointer; transition: all 0.15s; }
.pagination button:hover:not(:disabled) { background: var(--bg-card); color: var(--text-table); }
.pagination button:disabled { opacity: 0.3; cursor: not-allowed; }

.modal-mask { position: fixed; inset: 0; background: rgba(0,0,0,0.7); display: flex; align-items: center; justify-content: center; z-index: 100; }
.modal { background: var(--bg-solid); border: 0.5px solid var(--border); border-radius: 14px; padding: 28px 32px; width: 500px; display: flex; flex-direction: column; gap: 14px; max-height: 90vh; overflow-y: auto; }
.modal h3 { margin: 0; font-size: 1rem; font-weight: 500; color: var(--text-heading); }
.modal-question { background: var(--bg-input); padding: 12px 14px; border-radius: 8px; color: var(--text-secondary); font-size: 13px; margin: 0; line-height: 1.6; border-left: 3px solid var(--blue); }
label { font-size: 12px; color: var(--text-secondary); letter-spacing: 0.5px; }
.modal select, .modal textarea { padding: 10px 12px; background: var(--bg-input); color: var(--text-primary); border: 0.5px solid var(--border); border-radius: 8px; font-size: 14px; outline: none; transition: border-color 0.2s; }
.modal select:focus, .modal textarea:focus { border-color: var(--blue); }
.modal-footer { display: flex; justify-content: flex-end; gap: 10px; margin-top: 4px; }
.modal-footer button { padding: 8px 22px; border: 0.5px solid var(--border); border-radius: 8px; cursor: pointer; background: var(--bg-input); color: var(--text-secondary); font-size: 13px; transition: all 0.15s; }
.modal-footer button:hover { background: var(--bg-card); }
.btn-primary { background: var(--blue) !important; color: #fff !important; border-color: var(--blue) !important; }
.btn-primary:hover { background: var(--blue-hover) !important; }
.btn-primary:disabled { opacity: 0.5; cursor: not-allowed; }
.success { color: var(--resolved-text); font-size: 13px; }
.error { color: var(--error); font-size: 13px; }
</style>