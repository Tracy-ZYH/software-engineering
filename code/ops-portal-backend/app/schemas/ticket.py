"""
工单 Pydantic 请求/响应模型
"""
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field

from app.models.ticket import TicketStatus


# ============================================================
# 请求模型
# ============================================================

class TicketCreate(BaseModel):
    """创建工单请求（由前台发起）"""
    question: str = Field(..., description="用户问题")
    rag_answer: Optional[str] = Field(None, description="RAG返回的答案（如果有）")
    created_by: str = Field(..., max_length=100, description="报障人")
    contact_info: Optional[str] = Field(None, max_length=100, description="联系方式")


class TicketUpdate(BaseModel):
    """处理工单请求（后台运维人员使用）"""
    status: TicketStatus = Field(..., description="工单状态")
    resolution: Optional[str] = Field(None, description="处理方案")


class TicketSyncKnowledge(BaseModel):
    """同步到知识库请求"""
    category: Optional[str] = Field(None, max_length=50, description="知识分类")


# ============================================================
# 响应模型
# ============================================================

class TicketResponse(BaseModel):
    """工单响应"""
    id: int
    question: str
    rag_answer: Optional[str] = None
    status: TicketStatus
    created_by: str
    contact_info: Optional[str] = None
    resolver_id: Optional[int] = None
    resolver_name: Optional[str] = Field(None, description="处理人姓名")
    resolution: Optional[str] = None
    is_added_to_kb: bool = False
    created_at: datetime
    resolved_at: Optional[datetime] = None
    updated_at: datetime

    model_config = {"from_attributes": True}

    @classmethod
    def from_orm_with_relation(cls, ticket):
        """从 ORM 对象构建响应（含关联字段）"""
        d = cls.model_validate(ticket)
        d.resolver_name = ticket.resolver.real_name if ticket.resolver else None
        return d


class TicketListResponse(BaseModel):
    """工单列表响应（分页）"""
    total: int
    items: list[TicketResponse]
    page: int
    page_size: int
