"""
操作日志 ORM 模型
"""
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from app.database import Base


class OpsOperationLog(Base):
    """操作日志表"""
    __tablename__ = "ops_operation_log"

    id = Column(Integer, primary_key=True, autoincrement=True, comment="主键ID")
    operator_id = Column(Integer, ForeignKey("ops_account.id"), nullable=True, comment="操作人ID")
    action = Column(String(50), nullable=False, comment="操作类型")
    target_type = Column(String(50), nullable=False, comment="操作对象类型")
    target_id = Column(Integer, nullable=True, comment="操作对象ID")
    detail = Column(Text, nullable=True, comment="操作详情")
    created_at = Column(DateTime, server_default=func.now(), nullable=False, comment="操作时间")

    # 关联关系
    operator = relationship("OpsAccount", foreign_keys=[operator_id])

    def __repr__(self):
        return f"<OpsOperationLog(id={self.id}, action={self.action})>"
