"""
JWT 认证工具
提供 Token 签发、校验以及密码加密/校验功能
"""
from datetime import datetime, timedelta, timezone
from typing import Optional

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy.orm import Session

from app.config import JWT_CONFIG
from app.database import get_db
from app.models.account import OpsAccount, AccountStatus

# ---------- 密码加密 ----------
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# ---------- HTTP Bearer 认证方案 ----------
bearer_scheme = HTTPBearer(auto_error=False)


def hash_password(password: str) -> str:
    """对明文密码进行 bcrypt 哈希"""
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """校验明文密码与哈希是否匹配"""
    return pwd_context.verify(plain_password, hashed_password)


# ---------- JWT Token ----------

def create_access_token(account_id: int, username: str, role: str) -> str:
    """
    签发 JWT Token
    :param account_id: 账号ID
    :param username:   用户名
    :param role:       角色
    :return: JWT Token 字符串
    """
    expire = datetime.now(timezone.utc) + timedelta(minutes=JWT_CONFIG["expire_minutes"])
    payload = {
        "sub": str(account_id),
        "username": username,
        "role": role,
        "exp": expire,
    }
    return jwt.encode(payload, JWT_CONFIG["secret_key"], algorithm=JWT_CONFIG["algorithm"])


def decode_access_token(token: str) -> dict:
    """
    解码 JWT Token，返回 payload
    如果 token 无效或已过期，抛出 HTTPException
    """
    try:
        payload = jwt.decode(
            token, JWT_CONFIG["secret_key"], algorithms=[JWT_CONFIG["algorithm"]]
        )
        return payload
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token 无效或已过期，请重新登录",
            headers={"WWW-Authenticate": "Bearer"},
        )


# ---------- 依赖注入 ----------

def get_current_account(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(bearer_scheme),
    db: Session = Depends(get_db),
) -> OpsAccount:
    """
    从请求中解析 JWT Token，返回当前登录账号
    未提供 Token → 401
    Token 无效 → 401
    账号被冻结 → 403
    """
    if credentials is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="未提供认证 Token",
        )

    payload = decode_access_token(credentials.credentials)
    account_id = int(payload.get("sub"))

    account = db.query(OpsAccount).filter(OpsAccount.id == account_id).first()
    if account is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="账号不存在",
        )
    if account.status == AccountStatus.FROZEN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="账号已被冻结，无法操作",
        )
    return account


def require_admin(account: OpsAccount = Depends(get_current_account)) -> OpsAccount:
    """
    要求当前登录用户是管理员
    非管理员 → 403
    """
    if account.role.value != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="仅管理员可执行此操作",
        )
    return account
