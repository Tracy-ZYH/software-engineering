"""
对话查询 API 路由 —— 前端统一通过此接口调用 RAG 知识库
"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.chat import ChatRequest, ChatResponse
from app.services.chat_service import ChatService

router = APIRouter(prefix="/api", tags=["对话查询"])


@router.post("/chat", response_model=ChatResponse, summary="向知识库提问")
async def chat(data: ChatRequest, db: Session = Depends(get_db)):
    """
    用户提问，从 AnythingLLM 知识库检索答案

    - 知识库有答案 → 直接返回答案
    - 知识库无答案 → 自动创建工单，返回提示信息
    """
    service = ChatService(db)
    result = await service.ask(data.question, data.contact_info)
    return result
