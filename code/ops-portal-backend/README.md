# 运维数字员工 - 后端 API

## 项目简介

运维数字员工后端服务，提供运维账号管理、工单处理、知识库管理等 API 接口。

## 技术栈

- **框架**：FastAPI (Python)
- **数据库**：MySQL 8.0+
- **ORM**：SQLAlchemy 2.0
- **认证**：JWT (python-jose)
- **RAG**：AnythingLLM API

## 项目结构

```
ops-portal-backend/
├── app/                          # 应用主目录
│   ├── main.py                   # FastAPI 入口（自动建表、CORS、路由注册）
│   ├── config.py                 # 配置项（数据库、RAG、JWT、端口）
│   ├── database.py               # 数据库连接引擎 + Session 管理
│   │
│   ├── models/                   # ORM 模型层（SQLAlchemy）
│   │   ├── account.py            #   运维账号表
│   │   ├── ticket.py             #   工单/在线记录表
│   │   ├── knowledge.py          #   知识库条目表
│   │   └── operation_log.py      #   操作审计日志表
│   │
│   ├── schemas/                  # 请求/响应模型层（Pydantic）
│   │   ├── account.py            #   账号相关
│   │   ├── ticket.py             #   工单相关
│   │   └── knowledge.py          #   知识库相关
│   │
│   ├── routers/                  # API 路由层
│   │   ├── accounts.py           #   账号管理（CRUD + 冻结/解冻）
│   │   ├── tickets.py            #   工单管理（处理、同步知识库）
│   │   └── knowledge.py          #   知识库管理（录入、删除）
│   │
│   ├── services/                 # 业务逻辑层
│   │   ├── account_service.py    #   账号管理逻辑
│   │   ├── ticket_service.py     #   工单流转逻辑
│   │   └── knowledge_service.py  #   知识库管理逻辑
│   │
│   └── utils/                    # 工具模块
│       ├── auth.py               #   JWT 认证 + 密码 bcrypt 加密
│       └── rag_client.py         #   AnythingLLM API 客户端封装
│
├── sql/                          # 数据库脚本
│   ├── init.sql                  #   建库建表脚本（4张表）
│   └── seed.sql                  #   初始数据脚本
│
├── requirements.txt              # Python 依赖清单
├── init_admin.py                 # 初始化管理员账号脚本
└── README.md                     # 本项目文档（API 接口说明）
```

## 快速启动

### 1. 环境要求

- Python 3.10+
- MySQL 8.0+

### 2. 初始化数据库

```bash
# 登录 MySQL 并执行建表脚本
mysql -u root -p < sql/init.sql
```

### 3. 安装依赖

```bash
pip install -r requirements.txt
```

### 4. 启动服务

```bash
# 开发模式（热重载）
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# 生产模式
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

### 5. 向知识库提问（对话查询）

```bash
# 知识库有答案 → 直接返回
curl -X POST http://localhost:8000/api/chat \
  -H "Content-Type: application/json" \
  -d '{"question": "账号冻结怎么处理？"}'

# 知识库无答案 → 自动创建工单
curl -X POST http://localhost:8000/api/chat \
  -H "Content-Type: application/json" \
  -d '{"question": "xxx", "contact_info": "13800000000"}'
```

首次启动后，数据库中没有账号，需要先创建管理员才能登录：

```bash
python init_admin.py
```

执行成功后，可用以下账号登录：

| 用户名 | 密码 | 角色 |
|--------|------|------|
| `admin` | `admin123` | 管理员 |

### 6. 访问 API 文档

- Swagger UI：http://localhost:8000/docs
- ReDoc：http://localhost:8000/redoc

## API 接口清单

### 认证

| 方法 | 路径 | 说明 | 是否需要登录 |
|------|------|------|------------|
| POST | `/api/auth/login` | 用户登录，获取 Token | 否 |
| GET | `/api/auth/me` | 获取当前登录用户信息 | 是 |

### 账号管理

| 方法 | 路径 | 说明 | 权限 |
|------|------|------|------|
| POST | `/api/accounts` | 创建运维账号 | admin |
| GET | `/api/accounts` | 查询账号列表（分页+搜索） | 登录 |
| GET | `/api/accounts/{id}` | 查询单个账号详情 | 登录 |
| PUT | `/api/accounts/{id}` | 修改账号信息 | admin |
| DELETE | `/api/accounts/{id}` | 删除账号 | admin |
| PUT | `/api/accounts/{id}/status` | 冻结/解冻账号 | admin |

### 工单管理

| 方法 | 路径 | 说明 | 是否需要登录 |
|------|------|------|------------|
| POST | `/api/tickets` | 创建工单（前台用户提交） | 否 |
| GET | `/api/tickets` | 查询工单列表（分页+筛选） | 是 |
| GET | `/api/tickets/{id}` | 查询工单详情 | 是 |
| PUT | `/api/tickets/{id}` | 处理工单（填写方案） | 是 |
| POST | `/api/tickets/{id}/sync-knowledge` | 同步工单到知识库+RAG | 是 |

### 知识库管理

| 方法 | 路径 | 说明 | 是否需要登录 |
|------|------|------|------------|
| POST | `/api/knowledge` | 手动录入知识（同步到RAG） | 是 |
| GET | `/api/knowledge` | 查询知识列表（分页+搜索） | 是 |
| GET | `/api/knowledge/{id}` | 查询知识详情 | 是 |
| DELETE | `/api/knowledge/{id}` | 删除知识条目 | 是 |

### 对话查询

| 方法 | 路径 | 说明 | 是否需要登录 |
|------|------|------|------------|
| POST | `/api/chat` | 向知识库提问（有答案直接返回，无答案自动创建工单） | 否 |

## 调用示例

### 1. 登录

```bash
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "admin123"}'
```

### 2. 查询账号列表

```bash
curl http://localhost:8000/api/accounts?page=1&page_size=10 \
  -H "Authorization: Bearer <TOKEN>"
```

### 3. 创建账号

```bash
curl -X POST http://localhost:8000/api/accounts \
  -H "Authorization: Bearer <TOKEN>" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "zhangsan",
    "password": "pass123",
    "real_name": "张三",
    "phone": "13800138000",
    "department": "技术部",
    "role": "operator"
  }'
```

### 4. 冻结账号

```bash
curl -X PUT http://localhost:8000/api/accounts/1/status \
  -H "Authorization: Bearer <TOKEN>" \
  -H "Content-Type: application/json" \
  -d '{"status": "frozen"}'
```

## 数据库表结构

见 `sql/init.sql`，共 4 张表：

| 表名 | 说明 |
|------|------|
| `ops_account` | 运维账号 |
| `ops_ticket` | 工单/在线记录 |
| `ops_knowledge` | 知识库条目 |
| `ops_operation_log` | 操作审计日志 |
