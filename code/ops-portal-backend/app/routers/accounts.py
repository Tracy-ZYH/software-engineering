"""
账号管理 API 路由
"""
from typing import Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.account import OpsAccount
from app.schemas.account import (
    AccountCreate,
    AccountUpdate,
    AccountResponse,
    AccountListResponse,
    AccountStatusUpdate,
    LoginRequest,
    LoginResponse,
)
from app.services.account_service import AccountService
from app.utils.auth import get_current_account, require_admin

router = APIRouter(prefix="/api", tags=["账号管理"])


# ============================================================
# 登录
# ============================================================

@router.post("/auth/login", response_model=LoginResponse, summary="用户登录")
def login(data: LoginRequest, db: Session = Depends(get_db)):
    """使用用户名和密码登录，返回 JWT Token"""
    service = AccountService(db)
    result = service.login(data.username, data.password)
    return {
        "access_token": result["access_token"],
        "token_type": "bearer",
        "account": AccountResponse.model_validate(result["account"]),
    }


@router.get("/auth/me", response_model=AccountResponse, summary="获取当前登录用户信息")
def get_current_user(current_account: OpsAccount = Depends(get_current_account)):
    """获取当前登录的账号信息"""
    return AccountResponse.model_validate(current_account)


# ============================================================
# 账号 CRUD（需要登录）
# ============================================================

@router.post("/accounts", response_model=AccountResponse,
             summary="创建账号", dependencies=[Depends(require_admin)])
def create_account(
    data: AccountCreate,
    db: Session = Depends(get_db),
    current_account: OpsAccount = Depends(get_current_account),
):
    """【管理员】创建新的运维账号"""
    service = AccountService(db, operator=current_account)
    account = service.create(data)
    return AccountResponse.model_validate(account)


@router.get("/accounts", response_model=AccountListResponse, summary="查询账号列表")
def list_accounts(
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(10, ge=1, le=100, description="每页条数"),
    keyword: Optional[str] = Query(None, description="关键字搜索(用户名/姓名/手机/邮箱)"),
    role: Optional[str] = Query(None, description="角色过滤(admin/operator)"),
    status: Optional[str] = Query(None, description="状态过滤(active/frozen)"),
    department: Optional[str] = Query(None, description="部门过滤"),
    db: Session = Depends(get_db),
    current_account: OpsAccount = Depends(get_current_account),
):
    """查询运维账号列表，支持分页和多条件搜索"""
    service = AccountService(db, operator=current_account)
    result = service.list_accounts(
        page=page, page_size=page_size,
        keyword=keyword, role=role,
        status=status, department=department,
    )
    return AccountListResponse(
        total=result["total"],
        items=[AccountResponse.model_validate(item) for item in result["items"]],
        page=result["page"],
        page_size=result["page_size"],
    )


@router.get("/accounts/{account_id}", response_model=AccountResponse,
            summary="查询单个账号")
def get_account(
    account_id: int,
    db: Session = Depends(get_db),
    current_account: OpsAccount = Depends(get_current_account),
):
    """根据 ID 查询账号详情"""
    service = AccountService(db, operator=current_account)
    account = service.get_by_id(account_id)
    return AccountResponse.model_validate(account)


@router.put("/accounts/{account_id}", response_model=AccountResponse,
            summary="修改账号", dependencies=[Depends(require_admin)])
def update_account(
    account_id: int,
    data: AccountUpdate,
    db: Session = Depends(get_db),
    current_account: OpsAccount = Depends(get_current_account),
):
    """【管理员】修改账号信息"""
    service = AccountService(db, operator=current_account)
    account = service.update(account_id, data)
    return AccountResponse.model_validate(account)


@router.delete("/accounts/{account_id}", summary="删除账号",
               dependencies=[Depends(require_admin)])
def delete_account(
    account_id: int,
    db: Session = Depends(get_db),
    current_account: OpsAccount = Depends(get_current_account),
):
    """【管理员】删除账号（物理删除）"""
    service = AccountService(db, operator=current_account)
    service.delete(account_id)
    return {"message": "账号已删除", "id": account_id}


@router.put("/accounts/{account_id}/status", response_model=AccountResponse,
            summary="冻结/解冻账号", dependencies=[Depends(require_admin)])
def update_account_status(
    account_id: int,
    data: AccountStatusUpdate,
    db: Session = Depends(get_db),
    current_account: OpsAccount = Depends(get_current_account),
):
    """【管理员】冻结或解冻账号"""
    service = AccountService(db, operator=current_account)
    account = service.update_status(account_id, data)
    return AccountResponse.model_validate(account)
