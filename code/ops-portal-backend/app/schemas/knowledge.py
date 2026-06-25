"""
知识库条目 Pydantic 请求/响应模型
"""
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field

from app.models.knowledge import KnowledgeSource


# ============================================================
# 请求模型
# ============================================================

class KnowledgeCreate(BaseModel):
    """创建知识条目请求"""
    question: str = Field(..., description="问题")
    answer: str = Field(..., description="答案/解决方案")
    category: Optional[str] = Field(None, max_length=50, description="分类")


# ============================================================
# 响应模型
# ============================================================

class KnowledgeResponse(BaseModel):
    """知识条目响应"""
    id: int
    question: str
    answer: str
    category: Optional[str] = None
    source: KnowledgeSource
    source_ticket_id: Optional[int] = None
    created_by: Optional[int] = None
    creator_name: Optional[str] = Field(None, description="创建人姓名")
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class KnowledgeListResponse(BaseModel):
    """知识条目列表响应（分页）"""
    total: int
    items: list[KnowledgeResponse]
    page: int
    page_size: int
