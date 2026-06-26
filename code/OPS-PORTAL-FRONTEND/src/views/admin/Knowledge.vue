<template>
  <div>
    <div class="page-header">
      <h2>知识库管理</h2>
      <button class="btn-primary" @click="openCreate">+ 手动录入</button>
    </div>

    <div class="toolbar">
      <input v-model="search.keyword" placeholder="搜索关键字" @keyup.enter="page=1;loadKnowledge()" />
      <button @click="page=1;loadKnowledge()">搜索</button>
    </div>

    <div class="table-wrap">
      <table>
        <thead>
          <tr><th>ID</th><th>问题</th><th>答案摘要</th><th>来源</th><th>创建时间</th><th>操作</th></tr>
        </thead>
        <tbody>
          <tr v-if="loading"><td colspan="6" class="center">加载中...</td></tr>
          <tr v-else-if="list.length === 0"><td colspan="6" class="center">暂无知识条目</td></tr>
          <tr v-for="k in list" :key="k.id">
            <td>#{{ k.id }}</td>
            <td class="td-clip">{{ k.question }}</td>
            <td class="td-clip">{{ k.answer }}</td>
            <td><span class="badge">{{ k.source === 'ticket' ? '工单同步' : '手动录入' }}</span></td>
            <td>{{ formatDate(k.created_at) }}</td>
            <td>
              <button class="btn-sm" @click="openDetail(k)">详情</button>
              <button class="btn-sm btn-del" @click="deleteItem(k)">删除</button>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <div class="pagination">
      <button :disabled="page <= 1" @click="page--; loadKnowledge()">上一页</button>
      <span>第 {{ page }} 页 / 共 {{ totalPages }} 页</span>
      <button :disabled="page >= totalPages" @click="page++; loadKnowledge()">下一页</button>
    </div>

    <!-- 新建弹窗 -->
    <div v-if="showCreate" class="modal-mask">
      <div class="modal">
        <h3>手动录入知识</h3>
        <label>问题</label>
        <input v-model="form.question" placeholder="运维问题" />
        <label>答案</label>
        <textarea v-model="form.answer" placeholder="解决方案..." rows="5"></textarea>
        <label>分类（可选）</label>
        <input v-model="form.category" placeholder="如：账号管理" />
        <div class="modal-footer">
          <button @click="showCreate = false">取消</button>
          <button class="btn-primary" @click="submitCreate" :disabled="createLoading">
            {{ createLoading ? '提交中...' : '确认录入' }}
          </button>
        </div>
        <p v-if="createMsg" :class="createOk ? 'success' : 'error'">{{ createMsg }}</p>
      </div>
    </div>

    <!-- 详情弹窗 -->
    <div v-if="showDetail" class="modal-mask">
      <div class="modal">
        <h3>知识详情 #{{ detail.id }}</h3>
        <label>问题</label>
        <p class="detail-text">{{ detail.question }}</p>
        <label>答案</label>
        <p class="detail-text">{{ detail.answer }}</p>
        <label>来源</label>
        <p class="detail-text">{{ detail.source === 'ticket' ? '工单同步' : '手动录入' }}</p>
        <div class="modal-footer">
          <button @click="showDetail = false">关闭</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, computed } from 'vue'
import request from '../../api/request'

const list = ref([])
const loading = ref(false)
const total = ref(0)
const page = ref(1)
const pageSize = 10
const search = reactive({ keyword: '' })
const totalPages = computed(() => Math.max(1, Math.ceil(total.value / pageSize)))

const showCreate = ref(false)
const form = reactive({ question: '', answer: '', category: '' })
const createLoading = ref(false)
const createMsg = ref('')
const createOk = ref(false)

const showDetail = ref(false)
const detail = ref({})

const formatDate = s => s ? s.slice(0, 16).replace('T', ' ') : '-'

const loadKnowledge = async () => {
  loading.value = true
  try {
    const res = await request.get('/api/knowledge', {
      params: { page: page.value, page_size: pageSize, keyword: search.keyword || undefined }
    })
    list.value = res.data.items || res.data.knowledge || []
    total.value = res.data.total || 0
  } catch { list.value = [] } finally { loading.value = false }
}

const openCreate = () => {
  Object.assign(form, { question: '', answer: '', category: '' })
  createMsg.value = ''
  showCreate.value = true
}

const submitCreate = async () => {
  if (!form.question || !form.answer) { createMsg.value = '问题和答案不能为空'; createOk.value = false; return }
  createLoading.value = true
  createMsg.value = ''
  try {
    await request.post('/api/knowledge', { question: form.question, answer: form.answer, category: form.category || undefined })
    createOk.value = true
    createMsg.value = '✅ 录入成功，已同步到 AnythingLLM'
    setTimeout(() => { showCreate.value = false; loadKnowledge() }, 800)
  } catch (err) {
    createOk.value = false
    createMsg.value = '❌ 失败：' + (err.response?.data?.detail || err.message)
  } finally { createLoading.value = false }
}

const openDetail = async (k) => {
  try {
    const res = await request.get(`/api/knowledge/${k.id}`)
    detail.value = res.data
  } catch { detail.value = k }
  showDetail.value = true
}

const deleteItem = async (k) => {
  if (!confirm(`确认删除知识条目 #${k.id}？`)) return
  try {
    await request.delete(`/api/knowledge/${k.id}`)
    loadKnowledge()
  } catch (err) { alert('删除失败：' + (typeof err.response?.data?.detail === 'string' ? err.response.data.detail : err.message)) }
}

onMounted(loadKnowledge)
</script>

<style scoped>
.page-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 24px; }
h2 { margin: 0; font-size: 1.2rem; font-weight: 500; color: var(--text-heading); letter-spacing: 1px; }
.btn-primary { padding: 8px 20px; background: var(--blue); color: #fff; border: none; border-radius: 8px; font-size: 13px; cursor: pointer; transition: background 0.2s; }
.btn-primary:hover { background: var(--blue-hover); }

.toolbar { display: flex; gap: 10px; margin-bottom: 20px; }
.toolbar input { flex: 1; padding: 8px 14px; background: var(--bg-solid); color: var(--text-primary); border: 0.5px solid var(--border); border-radius: 8px; font-size: 13px; outline: none; transition: border-color 0.2s; }
.toolbar input:focus { border-color: var(--blue); }
.toolbar button { padding: 8px 20px; background: var(--blue); color: #fff; border: none; border-radius: 8px; font-size: 13px; cursor: pointer; }
.toolbar button:hover { background: var(--blue-hover); }

.table-wrap { background: var(--bg-solid); border: 0.5px solid var(--border); border-radius: 12px; overflow: hidden; }
table { width: 100%; border-collapse: collapse; font-size: 13px; }
th { background: var(--bg-input); padding: 11px 14px; text-align: left; color: var(--text-secondary); font-weight: 500; font-size: 12px; letter-spacing: 0.5px; border-bottom: 0.5px solid var(--border); }
td { padding: 11px 14px; border-bottom: 0.5px solid #f0f4f8; color: var(--text-table); vertical-align: middle; }
tr:last-child td { border-bottom: none; }
tr:hover td { background: var(--bg-hover); }
.td-clip { max-width: 200px; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
.center { text-align: center; color: var(--text-muted); padding: 40px; }

.badge { padding: 3px 10px; border-radius: 999px; font-size: 11px; font-weight: 500; background: var(--bg-input); color: var(--blue); }

.btn-sm { padding: 4px 12px; font-size: 12px; border-radius: 6px; cursor: pointer; margin-right: 6px; border: 0.5px solid var(--border-input); background: var(--bg-input); color: var(--blue); transition: all 0.15s; }
.btn-sm:hover { background: var(--border); }
.btn-del { background: #fef2f2; color: var(--error); border-color: #fecaca; }
.btn-del:hover { background: #fee2e2; }

.pagination { display: flex; align-items: center; gap: 16px; margin-top: 20px; justify-content: center; font-size: 13px; color: var(--text-muted); }
.pagination button { padding: 6px 18px; background: var(--bg-solid); color: var(--text-secondary); border: 0.5px solid var(--border); border-radius: 8px; cursor: pointer; transition: all 0.15s; }
.pagination button:hover:not(:disabled) { background: var(--bg-card); }
.pagination button:disabled { opacity: 0.3; cursor: not-allowed; }

.modal-mask { position: fixed; inset: 0; background: rgba(0,0,0,0.7); display: flex; align-items: center; justify-content: center; z-index: 100; }
.modal { background: var(--bg-solid); border: 0.5px solid var(--border); border-radius: 14px; padding: 28px 32px; width: 500px; display: flex; flex-direction: column; gap: 14px; max-height: 90vh; overflow-y: auto; }
.modal h3 { margin: 0; font-size: 1rem; font-weight: 500; color: var(--text-heading); }
label { font-size: 12px; color: var(--text-secondary); letter-spacing: 0.5px; }
.modal input, .modal textarea { padding: 10px 12px; background: var(--bg-input); color: var(--text-primary); border: 0.5px solid var(--border); border-radius: 8px; font-size: 14px; outline: none; transition: border-color 0.2s; }
.modal input:focus, .modal textarea:focus { border-color: var(--blue); }
.detail-text { background: var(--bg-input); padding: 12px 14px; border-radius: 8px; color: var(--text-table); font-size: 14px; line-height: 1.7; margin: 0; white-space: pre-wrap; border-left: 3px solid var(--border-input); }
.modal-footer { display: flex; justify-content: flex-end; gap: 10px; margin-top: 4px; }
.modal-footer button { padding: 8px 22px; border: 0.5px solid var(--border); border-radius: 8px; cursor: pointer; background: var(--bg-input); color: var(--text-secondary); font-size: 13px; transition: all 0.15s; }
.modal-footer button:hover { background: var(--bg-card); }
.btn-primary { background: var(--blue) !important; color: #fff !important; border-color: var(--blue) !important; }
.btn-primary:hover { background: var(--blue-hover) !important; }
.btn-primary:disabled { opacity: 0.5; cursor: not-allowed; }
.success { color: var(--resolved-text); font-size: 13px; }
.error { color: var(--error); font-size: 13px; }
</style>

