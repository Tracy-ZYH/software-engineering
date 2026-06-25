<template>
  <div class="wrap">
<div class="theme-toggle" @click="handleToggleTheme" :title="currentTheme === 'light' ? '切换深色主题' : '切换浅色主题'">
  <i :class="currentTheme === 'light' ? 'ti ti-moon' : 'ti ti-sun'"></i>
</div>

    <div class="logo-area">
      <div class="logo-icon"><i class="ti ti-robot" aria-hidden="true"></i></div>
      <p class="logo-title">运维数字员工</p>
      <p class="logo-sub">智能运维知识库 · 快速解答您的运维问题</p>
    </div>

    <div class="card">
      <div class="input-label"><i class="ti ti-message-question" aria-hidden="true"></i>请描述您遇到的问题</div>
      <textarea
        class="q-input"
        v-model="question"
        placeholder="例如：账号冻结怎么处理？VPN 无法连接怎么办？"
        :disabled="loading"
        @keydown.enter.exact.prevent="askQuestion"
      ></textarea>
      <div class="btn-row">
  <div class="quick-contacts">
    <a href="tel:13302332400" class="btn-contact">
      <i class="ti ti-phone" aria-hidden="true"></i>拨打热线
    </a>
    <a href="mailto:ops@company.com?subject=运维问题反馈&body=问题描述：" class="btn-contact">
      <i class="ti ti-mail" aria-hidden="true"></i>发送邮件
    </a>
  </div>
  <button class="btn-ask" @click="askQuestion" :disabled="loading || !question.trim()">
    <i class="ti ti-send" aria-hidden="true"></i>
    {{ loading ? '查询中...' : '提交问题' }}
  </button>
</div>
    </div>

    <div v-if="answerText" class="card" style="padding: 0;">
      <div class="answer-card">
        <div class="answer-header">
          <div class="answer-dot"></div>
          <span class="answer-label">返回结果</span>
        </div>
        <p class="answer-text">{{ answerText }}</p>
      </div>
    </div>

    <div v-if="showTicketForm" class="card" style="padding: 0;">
      <div class="ticket-card">
        <div class="ticket-header">
          <i class="ti ti-headset" aria-hidden="true"></i>
          <span class="ticket-title">转人工处理</span>
        </div>
        <p class="ticket-hint">知识库暂无该问题的答案，留下联系方式，运维人员将尽快回访您。</p>
        <div class="contact-row">
          <input
            class="contact-input"
            v-model="contactInfo"
            placeholder="请输入您的手机号或联系方式"
            :disabled="ticketLoading"
          />
          <button class="btn-submit" @click="submitTicket" :disabled="ticketLoading || !contactInfo.trim()">
            <i class="ti ti-clipboard-check" aria-hidden="true"></i>
            {{ ticketLoading ? '提交中...' : '提交工单' }}
          </button>
        </div>
        <p v-if="ticketResult" :class="ticketSuccess ? 'msg-success' : 'msg-error'">{{ ticketResult }}</p>
      </div>
    </div>

    <div class="admin-row">
      <router-link to="/login" class="admin-link">
        <i class="ti ti-lock" aria-hidden="true"></i>运维人员登录后台
      </router-link>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import request from '../api/request'
import { getSavedTheme, toggleTheme } from '../theme'

const question = ref('')
const loading = ref(false)
const answerText = ref('')
const showTicketForm = ref(false)
const contactInfo = ref('')
const ticketLoading = ref(false)
const ticketResult = ref('')
const ticketSuccess = ref(false)

const currentTheme = ref(getSavedTheme())
const handleToggleTheme = () => {
  currentTheme.value = toggleTheme()
}

const NO_ANSWER_KEYWORDS = ['没有找到', '暂无', '无法回答', 'not found', 'no answer', '抱歉', '对不起', '无法理解', '无法帮助', '无法确定', '我不确定', '我不清楚', '我不知道', "i don't know", "i'm not sure", "don't understand", 'unable to']

const isNoAnswer = (text) => {
  if (!text) return true
  return NO_ANSWER_KEYWORDS.some(k => text.toLowerCase().includes(k.toLowerCase()))
}

const askQuestion = async () => {
  if (!question.value.trim()) return
  loading.value = true
  answerText.value = ''
  showTicketForm.value = false
  ticketResult.value = ''

  try {
    const res = await request.post('/api/chat', { question: question.value.trim() })
    const data = res.data
    const text = typeof data === 'string'
      ? data
      : (data.answer || data.textResponse || data.message || JSON.stringify(data))
    answerText.value = text
    if (isNoAnswer(text)) showTicketForm.value = true
  } catch (err) {
    answerText.value = '查询失败，请稍后重试。'
    showTicketForm.value = true
  } finally {
    loading.value = false
  }
}

const submitTicket = async () => {
  if (!contactInfo.value.trim()) return
  ticketLoading.value = true
  ticketResult.value = ''
  try {
    await request.post('/api/tickets', {
      question: question.value.trim(),
      contact_info: contactInfo.value.trim(),
      created_by: contactInfo.value.trim()

    })
    ticketSuccess.value = true
    ticketResult.value = '✅ 工单已提交！运维人员将尽快联系您。'
    showTicketForm.value = false
  } catch (err) {
    ticketSuccess.value = false
    ticketResult.value = '❌ 工单提交失败，请拨打运维热线：13302332400'
  } finally {
    ticketLoading.value = false
  }
}
</script>

<style scoped>
@import url('https://cdn.jsdelivr.net/npm/@tabler/icons-webfont@latest/tabler-icons.min.css');

.wrap { min-height: 100vh; background: var(--bg-page); padding: 3rem 2rem; display: flex; flex-direction: column; align-items: center; font-family: var(--font-sans, 'Microsoft YaHei', sans-serif); box-sizing: border-box; width: 100%; }

.logo-area { text-align: center; margin-bottom: 2.5rem; }
.logo-icon { width: 52px; height: 52px; background: var(--blue); border-radius: 16px; display: inline-flex; align-items: center; justify-content: center; margin-bottom: 12px; }
.logo-icon i { font-size: 26px; color: #fff; }
.logo-title { font-size: 22px; font-weight: 500; color: var(--text-primary); letter-spacing: 3px; margin: 0; }
.logo-sub { font-size: 13px; color: var(--text-secondary); margin: 6px 0 0; }

.card { background: var(--bg-card); border: 0.5px solid var(--border); border-radius: 16px; padding: 1.5rem; margin-bottom: 1rem; box-sizing: border-box; width: 100%; max-width: 860px; }

.input-label { font-size: 13px; color: var(--text-muted); margin-bottom: 10px; display: flex; align-items: center; gap: 6px; }
.input-label i { font-size: 15px; }

.q-input { width: 100%; min-height: 160px; resize: vertical; box-sizing: border-box; background: var(--bg-input); color: var(--text-primary); border: 0.5px solid var(--border-input); border-radius: 12px; padding: 14px 16px; font-size: 16px; font-family: inherit; outline: none; transition: border-color 0.2s, box-shadow 0.2s; line-height: 1.6; }
.q-input:focus { border-color: var(--blue); box-shadow: 0 0 0 3px var(--blue-glow); }
.q-input:disabled { opacity: 0.5; }

.btn-row { display: flex; justify-content: space-between; align-items: center; margin-top: 12px; }
.quick-contacts { display: flex; gap: 8px; }
.btn-contact { display: inline-flex; align-items: center; gap: 6px; padding: 8px 16px; border-radius: 999px; background: transparent; color: var(--text-secondary); border: 0.5px solid var(--border-input); font-size: 13px; text-decoration: none; transition: all 0.2s; cursor: pointer; }
.btn-contact:hover { background: var(--bg-sidebar); color: var(--processing-text); border-color: var(--blue); }
.btn-contact i { font-size: 14px; }
.btn-ask { display: inline-flex; align-items: center; gap: 8px; padding: 10px 24px; border-radius: 999px; background: var(--blue); color: #fff; border: none; font-size: 14px; font-weight: 500; cursor: pointer; transition: background 0.2s; }
.btn-ask:hover:not(:disabled) { background: var(--blue-hover); }
.btn-ask:disabled { opacity: 0.5; cursor: not-allowed; }
.btn-ask i { font-size: 15px; }

.answer-card { background: var(--bg-solid); border-radius: 16px; padding: 1.25rem 1.5rem; }
.answer-header { display: flex; align-items: center; gap: 8px; margin-bottom: 12px; }
.answer-dot { width: 8px; height: 8px; border-radius: 50%; background: var(--blue); flex-shrink: 0; }
.answer-label { font-size: 11px; color: var(--text-secondary); font-weight: 500; letter-spacing: 1.5px; text-transform: uppercase; }
.answer-text { font-size: 16px; color: var(--text-primary); line-height: 1.8; white-space: pre-wrap; text-align: left; margin: 0; }

.ticket-card { border-left: 3px solid var(--orange); border-radius: 0 16px 16px 0; padding: 1.25rem 1.5rem; background: var(--bg-solid); }
.ticket-header { display: flex; align-items: center; gap: 8px; margin-bottom: 6px; }
.ticket-header i { font-size: 18px; color: var(--orange); }
.ticket-title { font-size: 15px; font-weight: 500; color: var(--text-primary); }
.ticket-hint { font-size: 13px; color: var(--text-secondary); margin: 0 0 14px; line-height: 1.6; }
.contact-row { display: flex; gap: 10px; }
.contact-input { flex: 1; padding: 10px 16px; border-radius: 999px; background: var(--bg-input); color: var(--text-primary); border: 0.5px solid var(--border-input); font-size: 15px; outline: none; transition: border-color 0.2s, box-shadow 0.2s; }
.contact-input:focus { border-color: var(--orange); box-shadow: 0 0 0 3px var(--orange-glow); }
.contact-input:disabled { opacity: 0.5; }
.btn-submit { padding: 10px 20px; border-radius: 999px; background: var(--orange); color: #fff; border: none; font-size: 14px; cursor: pointer; white-space: nowrap; display: inline-flex; align-items: center; gap: 6px; transition: background 0.2s; }
.btn-submit:hover:not(:disabled) { background: var(--orange-hover); }
.btn-submit:disabled { opacity: 0.5; cursor: not-allowed; }
.btn-submit i { font-size: 15px; }

.msg-success { color: var(--success); font-size: 13px; margin: 12px 0 0; }
.msg-error { color: var(--error); font-size: 13px; margin: 12px 0 0; }

.admin-row { text-align: center; margin-top: 1.5rem; }
.admin-link { font-size: 13px; color: var(--text-secondary); text-decoration: none; display: inline-flex; align-items: center; gap: 5px; transition: color 0.2s; }
.admin-link:hover { color: var(--text-muted); }
.admin-link i { font-size: 14px; }
</style>



/* 主题切换按钮 */
.theme-toggle {
  position: fixed;
  top: 16px;
  right: 16px;
  width: 40px;
  height: 40px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  background: var(--bg-card);
  border: 1px solid var(--border);
  color: var(--text-secondary);
  font-size: 18px;
  z-index: 1000;
  transition: all 0.2s;
}
.theme-toggle:hover {
  border-color: var(--blue);
  color: var(--blue);
}


