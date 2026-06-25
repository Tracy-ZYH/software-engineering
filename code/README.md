# 运维数字员工 - 运行说明


### 构建前端

```bash
cd code/OPS-PORTAL-FRONTEND
npm install        # 安装前端依赖（首次或依赖有变更时）
npm run build      # 构建，产物输出到 dist/
```

> **注意：** 每次修改前端代码后，都需要 `npm run build` 重新构建，后端才会加载最新版本。

### 初始化管理员账号

```bash
cd code/ops-portal-backend
python init_admin.py
```

执行成功后可用以下账号登录：
| 用户名 | 密码 | 角色 |
|--------|------|------|
| `admin` | `admin123` | 管理员 |

### 启动服务

**启动后端（会自动托管前端）：**

```bash
cd code/ops-portal-backend
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

**访问：**
- 前端页面：http://localhost:8000
- API 文档（Swagger UI）：http://localhost:8000/docs

> 后端会自动检测 `OPS-PORTAL-FRONTEND/dist/` 目录，存在则作为静态文件托管。前端和 API 同端口运行，无跨域问题。
