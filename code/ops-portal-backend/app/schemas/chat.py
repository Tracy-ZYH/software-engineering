"""
对话查询 Pydantic 请求/响应模型
"""
from typing import Optional
from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    """对话查询请求"""
    question: str = Field(..., min_length=1, max_length=2000, description="用户问题")
    contact_info: Optional[str] = Field(None, max_length=100, description="联系方式（当RAG无法回答时，用于创建工单）")


class ChatResponse(BaseModel):
    """对话查询响应"""
    answer: str = Field(..., description="知识库返回的答案")
    has_answer: bool = Field(..., description="是否从知识库中找到答案")
    ticket_id: Optional[int] = Field(None, description="如未找到答案，自动创建的工单ID")
