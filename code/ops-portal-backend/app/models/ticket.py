"""
工单/在线记录 ORM 模型
"""
import enum
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, SmallInteger
from sqlalchemy import Enum as SAEnum
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from app.database import Base


class TicketStatus(str, enum.Enum):
    """工单状态"""
    PENDING = "pending"         # 待处理
    PROCESSING = "processing"   # 处理中
    RESOLVED = "resolved"       # 已解决
    CLOSED = "closed"           # 已关闭


class OpsTicket(Base):
    """工单/在线记录表"""
    __tablename__ = "ops_ticket"

    id = Column(Integer, primary_key=True, autoincrement=True, comment="主键ID")
    question = Column(Text, nullable=False, comment="用户问题")
    rag_answer = Column(Text, nullable=True, comment="RAG返回的答案")
    status = Column(SAEnum(TicketStatus, values_callable=lambda obj: [e.value for e in obj]), default=TicketStatus.PENDING, nullable=False, comment="状态")
    created_by = Column(String(100), nullable=False, comment="报障人姓名/标识")
    contact_info = Column(String(100), nullable=True, comment="报障人联系方式")
    resolver_id = Column(Integer, ForeignKey("ops_account.id"), nullable=True, comment="处理人ID")
    resolution = Column(Text, nullable=True, comment="处理方案")
    is_added_to_kb = Column(SmallInteger, default=0, nullable=False, comment="是否已录入知识库")
    created_at = Column(DateTime, server_default=func.now(), nullable=False, comment="创建时间")
    resolved_at = Column(DateTime, nullable=True, comment="处理完成时间")
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), nullable=False, comment="更新时间")

    # 关联关系
    resolver = relationship("OpsAccount", foreign_keys=[resolver_id])

    def __repr__(self):
        return f"<OpsTicket(id={self.id}, status={self.status})>"
