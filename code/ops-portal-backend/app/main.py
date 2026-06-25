"""
运维数字员工 - 后端服务入口

启动方式：
    uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
"""
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.database import engine, Base
from app.routers import accounts, tickets, knowledge, chat
from fastapi.staticfiles import StaticFiles
from starlette.responses import FileResponse
import os


# ============================================================
# 应用生命周期
# ============================================================

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    应用启动时自动建表（开发环境用）
    生产环境请使用 sql/init.sql 手动建表
    """
    # 启动时：建表（如果不存在）
    Base.metadata.create_all(bind=engine)
    yield
    # 关闭时：无需清理


# ============================================================
# FastAPI 应用
# ============================================================

app = FastAPI(
    title="运维数字员工 - 后端 API",
    description="""
    运维数字员工后端服务

    ## 功能模块
    - **账号管理**：运维账号的增删改查、冻结/解冻
    - **工单管理**：在线记录/工单的处理与流转
    - **知识库管理**：知识条目的录入与维护（同步 AnythingLLM）

    ## 认证方式
    除登录和创建工单接口外，均需在请求头中携带：
    ```
    Authorization: Bearer <JWT_TOKEN>
    ```

    ## 相关文档
    - [AnythingLLM 知识库接口文档](https://sloped-putt-unable.ngrok-free.dev)
    """,
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs",       # Swagger UI 地址
    redoc_url="/redoc",     # ReDoc 地址
)

# ============================================================
# 跨域配置（允许前端跨域访问）
# ============================================================

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 生产环境应替换为具体的前端地址
    allow_credentials=False,  # 使用 JWT Header 鉴权，不需要 cookie 凭据
    allow_methods=["*"],
    allow_headers=["*"],
)

# ============================================================
# 注册路由
# ============================================================

app.include_router(accounts.router)
app.include_router(tickets.router)
app.include_router(knowledge.router)
app.include_router(chat.router)



# ============================================================
# 前端静态文件托管（同端口运行，彻底消除跨域）
# ============================================================
from pathlib import Path
frontend_dist = str(Path(__file__).resolve().parent.parent.parent / "OPS-PORTAL-FRONTEND" / "dist")
if os.path.isdir(frontend_dist):
    assets_dir = os.path.join(frontend_dist, "assets")
    if os.path.isdir(assets_dir):
        app.mount("/assets", StaticFiles(directory=assets_dir), name="frontend_assets")

    from starlette.routing import NoMatchFound

    @app.get("/{full_path:path}")
    async def serve_frontend(full_path: str):
        # 跳过 API 和内置文档路径
        if full_path.startswith("api/") or full_path in ("docs", "redoc", "openapi.json"):
            from starlette.responses import JSONResponse
            return JSONResponse({"detail": "Not Found"}, status_code=404)
        index = os.path.join(frontend_dist, "index.html")
        if os.path.isfile(index):
            return FileResponse(index, media_type="text/html")
        from starlette.responses import JSONResponse
        return JSONResponse({"detail": "Not Found"}, status_code=404)

# ============================================================
# 根路径
# ============================================================

@app.get("/", tags=["系统"])
def root():
    """服务状态检查"""
    return {
        "service": "运维数字员工 - 后端服务",
        "version": "1.0.0",
        "status": "running",
        "docs": "/docs",
    }



