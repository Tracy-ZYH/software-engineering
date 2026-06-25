"""
运维账号 ORM 模型
"""
import enum
from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy import Enum as SAEnum
from sqlalchemy.sql import func

from app.database import Base


class AccountRole(str, enum.Enum):
    """账号角色"""
    ADMIN = "admin"         # 管理员
    OPERATOR = "operator"   # 普通运维人员


class AccountStatus(str, enum.Enum):
    """账号状态"""
    ACTIVE = "active"   # 正常
    FROZEN = "frozen"   # 冻结


class OpsAccount(Base):
    """运维账号表"""
    __tablename__ = "ops_account"

    id = Column(Integer, primary_key=True, autoincrement=True, comment="主键ID")
    username = Column(String(50), unique=True, nullable=False, comment="登录用户名")
    password = Column(String(255), nullable=False, comment="密码(bcrypt加密)")
    real_name = Column(String(50), nullable=False, comment="真实姓名")
    phone = Column(String(20), nullable=True, comment="手机号")
    email = Column(String(100), nullable=True, comment="邮箱")
    department = Column(String(100), nullable=True, comment="所属部门")
    role = Column(SAEnum(AccountRole, values_callable=lambda obj: [e.value for e in obj]), default=AccountRole.OPERATOR, nullable=False, comment="角色")
    status = Column(SAEnum(AccountStatus, values_callable=lambda obj: [e.value for e in obj]), default=AccountStatus.ACTIVE, nullable=False, comment="状态")
    created_at = Column(DateTime, server_default=func.now(), nullable=False, comment="创建时间")
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), nullable=False, comment="更新时间")

    def __repr__(self):
        return f"<OpsAccount(id={self.id}, username={self.username}, role={self.role})>"
