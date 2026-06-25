"""
知识库管理 API 路由
"""
from typing import Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.account import OpsAccount
from app.schemas.knowledge import (
    KnowledgeCreate,
    KnowledgeResponse,
    KnowledgeListResponse,
)
from app.services.knowledge_service import KnowledgeService
from app.utils.auth import get_current_account

router = APIRouter(prefix="/api/knowledge", tags=["知识库管理"])


# ============================================================
# 知识库 CRUD
# ============================================================

@router.post("", response_model=KnowledgeResponse, summary="手动录入知识")
async def create_knowledge(
    data: KnowledgeCreate,
    db: Session = Depends(get_db),
    current_account: OpsAccount = Depends(get_current_account),
):
    """手动录入知识条目，同时同步到 AnythingLLM"""
    service = KnowledgeService(db, operator=current_account)
    knowledge = await service.create(data)
    return _to_response(knowledge)


@router.get("", response_model=KnowledgeListResponse, summary="查询知识库列表")
def list_knowledge(
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(10, ge=1, le=100, description="每页条数"),
    category: Optional[str] = Query(None, description="分类过滤"),
    keyword: Optional[str] = Query(None, description="问题关键字搜索"),
    db: Session = Depends(get_db),
    current_account: OpsAccount = Depends(get_current_account),
):
    """查询知识库条目列表"""
    service = KnowledgeService(db, operator=current_account)
    result = service.list_knowledge(
        page=page, page_size=page_size,
        category=category, keyword=keyword,
    )
    return KnowledgeListResponse(
        total=result["total"],
        items=[_to_response(item) for item in result["items"]],
        page=result["page"],
        page_size=result["page_size"],
    )


@router.get("/{knowledge_id}", response_model=KnowledgeResponse, summary="查询知识详情")
def get_knowledge(
    knowledge_id: int,
    db: Session = Depends(get_db),
    current_account: OpsAccount = Depends(get_current_account),
):
    """查询单条知识条目详情"""
    service = KnowledgeService(db, operator=current_account)
    knowledge = service.get_by_id(knowledge_id)
    return _to_response(knowledge)


@router.delete("/{knowledge_id}", summary="删除知识条目")
def delete_knowledge(
    knowledge_id: int,
    db: Session = Depends(get_db),
    current_account: OpsAccount = Depends(get_current_account),
):
    """删除知识条目"""
    service = KnowledgeService(db, operator=current_account)
    service.delete(knowledge_id)
    return {"message": "知识条目已删除", "id": knowledge_id}


# ============================================================
# 辅助函数
# ============================================================

def _to_response(knowledge) -> KnowledgeResponse:
    """将 ORM 对象转换为响应模型"""
    resp = KnowledgeResponse.model_validate(knowledge)
    if knowledge.creator:
        resp.creator_name = knowledge.creator.real_name
    return resp
