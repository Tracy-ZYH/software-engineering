"""
工单管理 API 路由
"""
from typing import Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.account import OpsAccount
from app.schemas.ticket import (
    TicketCreate,
    TicketUpdate,
    TicketResponse,
    TicketListResponse,
    TicketSyncKnowledge,
)
from app.services.ticket_service import TicketService
from app.utils.auth import get_current_account

router = APIRouter(prefix="/api/tickets", tags=["工单管理"])


# ============================================================
# 工单 CRUD
# ============================================================

@router.post("", response_model=TicketResponse, summary="创建工单（前台调用）")
def create_ticket(
    data: TicketCreate,
    db: Session = Depends(get_db),
):
    """前台用户提交问题，当 RAG 无法回答时创建此工单（无需登录）"""
    service = TicketService(db)
    ticket = service.create(data)
    return _to_response(ticket)


@router.get("", response_model=TicketListResponse, summary="查询工单列表")
def list_tickets(
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(10, ge=1, le=100, description="每页条数"),
    status: Optional[str] = Query(None, description="状态过滤(pending/processing/resolved/closed)"),
    keyword: Optional[str] = Query(None, description="问题关键字搜索"),
    db: Session = Depends(get_db),
    current_account: OpsAccount = Depends(get_current_account),
):
    """查询工单列表（需要登录）"""
    service = TicketService(db, operator=current_account)
    result = service.list_tickets(
        page=page, page_size=page_size,
        status=status, keyword=keyword,
    )
    return TicketListResponse(
        total=result["total"],
        items=[_to_response(item) for item in result["items"]],
        page=result["page"],
        page_size=result["page_size"],
    )


@router.get("/{ticket_id}", response_model=TicketResponse, summary="查询工单详情")
def get_ticket(
    ticket_id: int,
    db: Session = Depends(get_db),
    current_account: OpsAccount = Depends(get_current_account),
):
    """查询单个工单详情（需要登录）"""
    service = TicketService(db, operator=current_account)
    ticket = service.get_by_id(ticket_id)
    return _to_response(ticket)


@router.put("/{ticket_id}", response_model=TicketResponse, summary="处理工单")
def process_ticket(
    ticket_id: int,
    data: TicketUpdate,
    db: Session = Depends(get_db),
    current_account: OpsAccount = Depends(get_current_account),
):
    """后台运维人员处理工单，填写处理方案和状态"""
    service = TicketService(db, operator=current_account)
    ticket = service.process(ticket_id, data)
    return _to_response(ticket)


@router.post("/{ticket_id}/sync-knowledge", summary="同步工单到知识库")
async def sync_ticket_to_knowledge(
    ticket_id: int,
    data: TicketSyncKnowledge = TicketSyncKnowledge(),
    db: Session = Depends(get_db),
    current_account: OpsAccount = Depends(get_current_account),
):
    """
    将已处理的工单同步到知识库
    1. 写入本地 ops_knowledge 表
    2. 调用 AnythingLLM raw-text 接口上传到 RAG 知识库
    """
    service = TicketService(db, operator=current_account)
    result = await service.sync_to_knowledge(ticket_id, category=data.category)
    return {
        "message": "工单已成功同步到知识库",
        "knowledge_id": result["knowledge_id"],
        "rag_sync_success": result["rag_result"].get("success", False),
    }


# ============================================================
# 辅助函数
# ============================================================

def _to_response(ticket) -> TicketResponse:
    """将 ORM 对象转换为响应模型"""
    resp = TicketResponse.model_validate(ticket)
    resp.is_added_to_kb = bool(ticket.is_added_to_kb)
    if ticket.resolver:
        resp.resolver_name = ticket.resolver.real_name
    return resp
