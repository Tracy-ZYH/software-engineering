"""
账号管理业务逻辑
"""
from typing import Optional

from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import or_

from app.models.account import OpsAccount, AccountRole, AccountStatus
from app.models.operation_log import OpsOperationLog
from app.schemas.account import AccountCreate, AccountUpdate, AccountStatusUpdate
from app.utils.auth import hash_password, verify_password, create_access_token


class AccountService:
    """账号管理服务"""

    def __init__(self, db: Session, operator: Optional[OpsAccount] = None):
        self.db = db
        self.operator = operator  # 当前操作人

    # -----------------------------------------------------------
    # 登录
    # -----------------------------------------------------------
    def login(self, username: str, password: str) -> dict:
        """用户登录，返回 Token"""
        account = (
            self.db.query(OpsAccount)
            .filter(OpsAccount.username == username)
            .first()
        )
        if not account:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="用户名或密码错误",
            )
        if account.status == AccountStatus.FROZEN:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="账号已被冻结，请联系管理员",
            )
        if not verify_password(password, account.password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="用户名或密码错误",
            )

        # 签发 Token
        token = create_access_token(
            account_id=account.id,
            username=account.username,
            role=account.role.value,
        )

        # 记录登录日志
        self._log_operation("LOGIN", "ACCOUNT", account.id, "用户登录")

        return {
            "access_token": token,
            "token_type": "bearer",
            "account": account,
        }

    # -----------------------------------------------------------
    # 创建账号
    # -----------------------------------------------------------
    def create(self, data: AccountCreate) -> OpsAccount:
        """创建新账号"""
        # 检查用户名是否已存在
        existing = (
            self.db.query(OpsAccount)
            .filter(OpsAccount.username == data.username)
            .first()
        )
        if existing:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"用户名 '{data.username}' 已存在",
            )

        account = OpsAccount(
            username=data.username,
            password=hash_password(data.password),
            real_name=data.real_name,
            phone=data.phone,
            email=data.email,
            department=data.department,
            role=data.role,
            status=AccountStatus.ACTIVE,
        )
        self.db.add(account)
        self.db.commit()
        self.db.refresh(account)

        # 记录操作日志
        self._log_operation("CREATE", "ACCOUNT", account.id,
                            f"创建账号: {account.username}")

        return account

    # -----------------------------------------------------------
    # 查询账号列表（分页 + 多条件搜索）
    # -----------------------------------------------------------
    def list_accounts(
        self,
        page: int = 1,
        page_size: int = 10,
        keyword: Optional[str] = None,
        role: Optional[str] = None,
        status: Optional[str] = None,
        department: Optional[str] = None,
    ) -> dict:
        """
        查询账号列表
        :param page:       页码（从1开始）
        :param page_size:  每页条数
        :param keyword:    关键字（模糊匹配用户名、姓名、手机号、邮箱）
        :param role:       角色过滤
        :param status:     状态过滤
        :param department: 部门过滤
        """
        query = self.db.query(OpsAccount)

        # 多条件搜索
        if keyword:
            like_pattern = f"%{keyword}%"
            query = query.filter(
                or_(
                    OpsAccount.username.like(like_pattern),
                    OpsAccount.real_name.like(like_pattern),
                    OpsAccount.phone.like(like_pattern),
                    OpsAccount.email.like(like_pattern),
                )
            )
        if role:
            query = query.filter(OpsAccount.role == role)
        if status:
            query = query.filter(OpsAccount.status == status)
        if department:
            query = query.filter(OpsAccount.department == department)

        # 按创建时间倒序
        query = query.order_by(OpsAccount.created_at.desc())

        # 计算总数
        total = query.count()

        # 分页
        offset = (page - 1) * page_size
        items = query.offset(offset).limit(page_size).all()

        return {
            "total": total,
            "items": items,
            "page": page,
            "page_size": page_size,
        }

    # -----------------------------------------------------------
    # 查询单个账号
    # -----------------------------------------------------------
    def get_by_id(self, account_id: int) -> OpsAccount:
        """根据 ID 查询账号"""
        account = (
            self.db.query(OpsAccount)
            .filter(OpsAccount.id == account_id)
            .first()
        )
        if not account:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="账号不存在",
            )
        return account

    # -----------------------------------------------------------
    # 更新账号
    # -----------------------------------------------------------
    def update(self, account_id: int, data: AccountUpdate) -> OpsAccount:
        """更新账号信息"""
        account = self.get_by_id(account_id)

        update_fields = []
        if data.real_name is not None:
            account.real_name = data.real_name
            update_fields.append("real_name")
        if data.password is not None:
            account.password = hash_password(data.password)
            update_fields.append("password")
        if data.phone is not None:
            account.phone = data.phone
            update_fields.append("phone")
        if data.email is not None:
            account.email = data.email
            update_fields.append("email")
        if data.department is not None:
            account.department = data.department
            update_fields.append("department")
        if data.role is not None:
            account.role = data.role
            update_fields.append("role")

        self.db.commit()
        self.db.refresh(account)

        # 记录操作日志
        self._log_operation("UPDATE", "ACCOUNT", account_id,
                            f"更新账号字段: {', '.join(update_fields)}")

        return account

    # -----------------------------------------------------------
    # 更新账号状态（冻结/解冻）
    # -----------------------------------------------------------
    def update_status(self, account_id: int, data: AccountStatusUpdate) -> OpsAccount:
        """更新账号状态（冻结/解冻）"""
        account = self.get_by_id(account_id)
        old_status = account.status.value
        account.status = data.status

        self.db.commit()
        self.db.refresh(account)

        # 记录操作日志
        action = "FREEZE" if data.status == AccountStatus.FROZEN else "UNFREEZE"
        self._log_operation(action, "ACCOUNT", account_id,
                            f"账号状态变更: {old_status} → {data.status.value}")

        return account

    # -----------------------------------------------------------
    # 删除账号
    # -----------------------------------------------------------
    def delete(self, account_id: int):
        """删除账号（物理删除）"""
        account = self.get_by_id(account_id)
        username = account.username

        self.db.delete(account)
        self.db.commit()

        # 记录操作日志
        self._log_operation("DELETE", "ACCOUNT", account_id,
                            f"删除账号: {username}")

    # -----------------------------------------------------------
    # 内部：记录操作日志
    # -----------------------------------------------------------
    def _log_operation(self, action: str, target_type: str,
                       target_id: int, detail: str):
        """记录操作日志"""
        log = OpsOperationLog(
            operator_id=self.operator.id if self.operator else None,
            action=action,
            target_type=target_type,
            target_id=target_id,
            detail=detail,
        )
        self.db.add(log)
        self.db.commit()
