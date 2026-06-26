"""
应用配置
所有配置项均支持通过环境变量覆盖，方便部署
"""
import os

# ============================================================
# 数据库配置
# ============================================================
DATABASE_CONFIG = {
    "host": os.getenv("DB_HOST", "localhost"),
    "port": int(os.getenv("DB_PORT", "3306")),
    "user": os.getenv("DB_USER", "root"),
    "password": os.getenv("DB_PASSWORD", "1234"),
    "database": os.getenv("DB_NAME", "ops_portal"),
}

DATABASE_URL = (
    f"mysql+pymysql://{DATABASE_CONFIG['user']}:{DATABASE_CONFIG['password']}"
    f"@{DATABASE_CONFIG['host']}:{DATABASE_CONFIG['port']}"
    f"/{DATABASE_CONFIG['database']}?charset=utf8mb4"
)



RAG_CONFIG = {
    # 本地 AnythingLLM 服务地址
    "api_base": os.getenv("RAG_API_BASE", "http://localhost:3001"),
    # AnythingLLM API 密钥
    "api_key": os.getenv("RAG_API_KEY", "DJBEYXB-1V6MF7X-NB814CT-39RDN05"),
    # 工作区 slug（在 AnythingLLM 工作区设置中查看）
    "workspace": os.getenv("RAG_WORKSPACE", "8e0de4ab-73c9-47e2-80a9-edacc76f3449"),
}

# ============================================================
# JWT 认证配置
# ============================================================
JWT_CONFIG = {
    "secret_key": os.getenv("JWT_SECRET_KEY", "ops-portal-secret-key-2024"),
    "algorithm": "HS256",
    "expire_minutes": 60 * 24,  # 24小时过期
}

# ============================================================
# 服务端口
# ============================================================
SERVER_HOST = os.getenv("SERVER_HOST", "0.0.0.0")
SERVER_PORT = int(os.getenv("SERVER_PORT", "8000"))

