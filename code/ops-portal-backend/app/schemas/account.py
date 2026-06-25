"""
运维账号 Pydantic 请求/响应模型
"""
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, field_validator

from app.models.account import AccountRole, AccountStatus


# ============================================================
# 请求模型
# ============================================================

class AccountCreate(BaseModel):
    """创建账号请求"""
    username: str = Field(..., min_length=2, max_length=50, description="登录用户名")
    password: str = Field(..., min_length=6, max_length=100, description="密码")
    real_name: str = Field(..., min_length=1, max_length=50, description="真实姓名")
    phone: Optional[str] = Field(None, max_length=20, description="手机号")
    email: Optional[str] = Field(None, max_length=100, description="邮箱")
    department: Optional[str] = Field(None, max_length=100, description="所属部门")
    role: AccountRole = Field(AccountRole.OPERATOR, description="角色")


class AccountUpdate(BaseModel):
    """更新账号请求（所有字段可选）"""
    real_name: Optional[str] = Field(None, min_length=1, max_length=50, description="真实姓名")
    password: Optional[str] = Field(None, min_length=6, max_length=100, description="新密码")
    phone: Optional[str] = Field(None, max_length=20, description="手机号")
    email: Optional[str] = Field(None, max_length=100, description="邮箱")
    department: Optional[str] = Field(None, max_length=100, description="所属部门")
    role: Optional[AccountRole] = Field(None, description="角色")


class AccountStatusUpdate(BaseModel):
    """更新账号状态请求（冻结/解冻）"""
    status: AccountStatus = Field(..., description="目标状态：active=解冻, frozen=冻结")


class LoginRequest(BaseModel):
    """登录请求"""
    username: str = Field(..., description="用户名")
    password: str = Field(..., description="密码")


# ============================================================
# 响应模型
# ============================================================

class AccountResponse(BaseModel):
    """账号响应（不含密码）"""
    id: int
    username: str
    real_name: str
    phone: Optional[str] = None
    email: Optional[str] = None
    department: Optional[str] = None
    role: AccountRole
    status: AccountStatus
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class AccountListResponse(BaseModel):
    """账号列表响应（分页）"""
    total: int = Field(..., description="总记录数")
    items: list[AccountResponse] = Field(..., description="当前页数据")
    page: int = Field(..., description="当前页码")
    page_size: int = Field(..., description="每页条数")


class LoginResponse(BaseModel):
    """登录响应"""
    access_token: str = Field(..., description="JWT Token")
    token_type: str = Field("bearer", description="Token 类型")
    account: AccountResponse = Field(..., description="当前登录账号信息")
