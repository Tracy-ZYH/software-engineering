# 运维数字员工 · 前端
 
> 基于 Vue 3 + Vite 构建的运维门户前端，包含用户前台问答页面与运维人员后台管理系统。
 
---
 重要：
 1.可供测试的登陆账号：admin  密码：admin123    无权限普通人：lisi 密码：lisi123

 2.经过本人初步测试，知识库手动录入的知识疑似不能被llm识别，我输入过几个问题，基本都失败了，但是原装FQA是没问题的，fetch了一下疑似是后端的问题，但不确定

 3.“工单管理”中“状态”得要手动调整成“已解决”才能有录入知识库的按钮，这不是bug，考虑到解决中的问题可能过十分钟又不行了，把知识录入知识库还是得确认问题完全解决才可以

 4.想要测试功能的话，得通知llm那边开一下，再通知前后端都开一下，才能看到成功的页面

 5.前端的包里那个ngrok.exe主要是为前端这边运行服务的，单纯debug代码的话可以删掉
## 技术栈
 
| 技术 | 版本 | 用途 |
|------|------|------|
| Vue 3 | ^3.x | 前端框架 |
| Vite | ^8.x | 构建工具 |
| Vue Router | ^4.x | 前端路由 |
| Axios | ^1.x | HTTP 请求 |
 
---
 
## 项目结构
 
```
src/
├── api/
│   └── request.js          # Axios 实例，自动携带 JWT Token 与 ngrok 请求头
├── router/
│   └── index.js            # 路由配置，含登录态守卫
├── views/
│   ├── Portal.vue          # 前台用户问答页面
│   ├── Login.vue           # 运维人员登录页
│   └── admin/
│       ├── Layout.vue      # 后台整体布局（侧边栏 + 路由出口）
│       ├── Tickets.vue     # 工单管理页面
│       ├── Accounts.vue    # 账号管理页面
│       └── Knowledge.vue   # 知识库管理页面
├── App.vue                 # 根组件（仅含 router-view）
└── main.js                 # 应用入口，注册路由
```
 
---
 
## 功能模块
 
### 一、前台用户门户 `/`
 
面向普通用户，无需登录即可访问。
 
- **智能问答**：用户输入问题，调用后端 `POST /api/chat` 接口，后端调用 AnythingLLM 知识库检索答案并返回
- **自动判断无答案**：若返回内容包含"没有找到"、"抱歉"等关键词，或 `has_answer: false`，自动展示转人工模块
- **在线留单**：用户填写联系方式后提交工单（`POST /api/tickets`），运维人员可在后台查看处理
- **快捷联系**：提问框旁提供一键拨打运维热线和发送邮件的快捷入口
### 二、运维人员登录页 `/login`
 
- 用户名 + 密码登录，调用 `POST /api/auth/login`
- 登录成功后 JWT Token 存入 `localStorage`，自动跳转后台
- 登录失败展示具体错误信息


重要：可供测试的登陆账号：admin，密码：admin123.
### 三、后台管理系统 `/admin`
 
需登录后访问，未登录自动跳转登录页（路由守卫）。侧边栏导航支持快速切换模块，并提供返回前台入口。
 
#### 工单管理 `/admin/tickets`
 
- 工单列表展示，含问题、联系方式、状态、创建时间
- 支持按关键字、联系方式（前端过滤）、状态筛选
- **处理工单**：弹窗填写处理方案，更新工单状态（处理中 / 已解决）
- **同步知识库**：已解决的工单可一键同步到本地知识库及 AnythingLLM RAG，供后续问答使用
- 分页浏览
#### 账号管理 `/admin/accounts`
 
- 账号列表展示，含用户名、姓名、部门、角色、状态
- 支持按关键字、角色（管理员 / 运维人员）、状态筛选
- **新建账号**：填写用户名、密码、姓名、手机号、部门、角色
- **编辑账号**：修改基本信息，密码留空则不修改
- **冻结 / 解冻**：切换账号状态，冻结后该账号无法登录
- **删除账号**：物理删除，操作前二次确认
- 分页浏览
#### 知识库管理 `/admin/knowledge`
 
- 知识条目列表展示，含问题、答案摘要、来源（手动录入 / 工单同步）、创建时间
- 支持关键字搜索
- **手动录入**：直接填写问答对，同步到 AnythingLLM RAG
- **查看详情**：查看完整问题与答案内容
- **删除条目**：删除本地记录
- 分页浏览
---
 
## 本地开发
 
```bash
# 安装依赖
npm install
 
# 启动开发服务（含后端代理，解决 CORS）
npm run dev
```
 
开发模式下，所有 `/api` 请求通过 Vite 代理转发到后端，无需处理跨域问题。
 
后端地址在 `vite.config.js` 中配置：
 
```javascript
proxy: {
  '/api': {
    target: 'https://后端ngrok地址',
    changeOrigin: true,
    secure: false,
  }
}
```
 
---
 
## 构建与部署（公网访问）
 
```bash
# 1. 修改 src/api/request.js，将 baseURL 改为后端 ngrok 地址
# 2. 构建
npm run build
 
# 3. 本地预览构建产物
serve dist -p 4173
 
# 4. 使用 ngrok 暴露到公网
.\ngrok.exe http 4173
```
 
> 注意：构建后 Vite 代理失效，需直接写后端地址。后端须开启 CORS（`allow_origins=["*"]`）。
 
---
 
## 接口依赖
 
前端仅调用以下后端接口，全部由后端（FastAPI）统一提供：
 
| 接口 | 说明 | 是否需要登录 |
|------|------|------------|
| `POST /api/auth/login` | 用户登录，获取 JWT Token | 否 |
| `POST /api/chat` | 前台智能问答 | 否 |
| `POST /api/tickets` | 创建工单（前台留单） | 否 |
| `GET /api/tickets` | 查询工单列表 | 是 |
| `GET /api/tickets/{id}` | 查询工单详情 | 是 |
| `PUT /api/tickets/{id}` | 处理工单 | 是 |
| `POST /api/tickets/{id}/sync-knowledge` | 同步工单到知识库 | 是 |
| `GET /api/accounts` | 查询账号列表 | 是 |
| `POST /api/accounts` | 创建账号 | 是 |
| `PUT /api/accounts/{id}` | 修改账号 | 是 |
| `PUT /api/accounts/{id}/status` | 冻结/解冻账号 | 是 |
| `DELETE /api/accounts/{id}` | 删除账号 | 是 |
| `GET /api/knowledge` | 查询知识库列表 | 是 |
| `POST /api/knowledge` | 手动录入知识 | 是 |
| `GET /api/knowledge/{id}` | 查询知识详情 | 是 |
| `DELETE /api/knowledge/{id}` | 删除知识条目 | 是 |
 