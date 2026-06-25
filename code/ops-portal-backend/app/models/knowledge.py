"""
知识库条目 ORM 模型
"""
import enum
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy import Enum as SAEnum
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from app.database import Base


class KnowledgeSource(str, enum.Enum):
    """知识条目来源"""
    MANUAL = "manual"   # 手动录入
    TICKET = "ticket"   # 工单转换


class OpsKnowledge(Base):
    """知识库条目表"""
    __tablename__ = "ops_knowledge"

    id = Column(Integer, primary_key=True, autoincrement=True, comment="主键ID")
    question = Column(Text, nullable=False, comment="问题")
    answer = Column(Text, nullable=False, comment="答案/解决方案")
    category = Column(String(50), nullable=True, comment="分类")
    source = Column(SAEnum(KnowledgeSource, values_callable=lambda obj: [e.value for e in obj]), default=KnowledgeSource.MANUAL, nullable=False, comment="来源")
    source_ticket_id = Column(Integer, ForeignKey("ops_ticket.id"), nullable=True, comment="来源工单ID")
    created_by = Column(Integer, ForeignKey("ops_account.id"), nullable=True, comment="创建人ID")
    created_at = Column(DateTime, server_default=func.now(), nullable=False, comment="创建时间")
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), nullable=False, comment="更新时间")

    # 关联关系
    source_ticket = relationship("OpsTicket", foreign_keys=[source_ticket_id])
    creator = relationship("OpsAccount", foreign_keys=[created_by])

    def __repr__(self):
        return f"<OpsKnowledge(id={self.id}, category={self.category})>"
