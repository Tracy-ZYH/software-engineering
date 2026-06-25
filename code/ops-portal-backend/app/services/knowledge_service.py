"""
知识库管理业务逻辑
"""
from typing import Optional

from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import desc

from app.models.account import OpsAccount
from app.models.knowledge import OpsKnowledge, KnowledgeSource
from app.models.operation_log import OpsOperationLog
from app.schemas.knowledge import KnowledgeCreate
from app.utils.rag_client import upload_raw_text, format_knowledge_text


class KnowledgeService:
    """知识库管理服务"""

    def __init__(self, db: Session, operator: Optional[OpsAccount] = None):
        self.db = db
        self.operator = operator

    # -----------------------------------------------------------
    # 手动录入知识
    # -----------------------------------------------------------
    async def create(self, data: KnowledgeCreate) -> OpsKnowledge:
        """手动录入知识条目，同时同步到 AnythingLLM"""
        # 1. 写入本地库
        knowledge = OpsKnowledge(
            question=data.question,
            answer=data.answer,
            category=data.category,
            source=KnowledgeSource.MANUAL,
            created_by=self.operator.id if self.operator else None,
        )
        self.db.add(knowledge)
        self.db.commit()
        self.db.refresh(knowledge)

        # 2. 同步到 AnythingLLM
        try:
            text_content = format_knowledge_text(data.question, data.answer)
            await upload_raw_text(
                text_content=text_content,
                title=f"手动录入-{data.category or '未分类'}-{data.question[:20]}",
                doc_author=self.operator.real_name if self.operator else "运维系统",
            )
        except Exception as e:
            # RAG 同步失败不影响本地保存，但记录日志
            self._log_operation("RAG_SYNC_FAIL", "KNOWLEDGE", knowledge.id,
                                f"同步到 AnythingLLM 失败: {str(e)}")

        self._log_operation("CREATE", "KNOWLEDGE", knowledge.id,
                            f"手动录入知识: {data.question[:50]}...")
        return knowledge

    # -----------------------------------------------------------
    # 查询知识列表
    # -----------------------------------------------------------
    def list_knowledge(
        self,
        page: int = 1,
        page_size: int = 10,
        category: Optional[str] = None,
        keyword: Optional[str] = None,
    ) -> dict:
        """查询知识库列表"""
        query = self.db.query(OpsKnowledge)

        if category:
            query = query.filter(OpsKnowledge.category == category)
        if keyword:
            like_pattern = f"%{keyword}%"
            query = query.filter(
                OpsKnowledge.question.like(like_pattern)
            )

        query = query.order_by(desc(OpsKnowledge.created_at))
        total = query.count()
        offset = (page - 1) * page_size
        items = query.offset(offset).limit(page_size).all()

        return {
            "total": total,
            "items": items,
            "page": page,
            "page_size": page_size,
        }

    # -----------------------------------------------------------
    # 查询单个知识条目
    # -----------------------------------------------------------
    def get_by_id(self, knowledge_id: int) -> OpsKnowledge:
        """查询知识详情"""
        knowledge = self.db.query(OpsKnowledge).filter(
            OpsKnowledge.id == knowledge_id
        ).first()
        if not knowledge:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="知识条目不存在",
            )
        return knowledge

    # -----------------------------------------------------------
    # 删除知识条目
    # -----------------------------------------------------------
    def delete(self, knowledge_id: int):
        """删除知识条目"""
        knowledge = self.get_by_id(knowledge_id)
        self.db.delete(knowledge)
        self.db.commit()

        self._log_operation("DELETE", "KNOWLEDGE", knowledge_id,
                            f"删除知识条目: {knowledge.question[:50]}...")

    # -----------------------------------------------------------
    # 内部方法
    # -----------------------------------------------------------
    def _log_operation(self, action: str, target_type: str,
                       target_id: int, detail: str):
        log = OpsOperationLog(
            operator_id=self.operator.id if self.operator else None,
            action=action,
            target_type=target_type,
            target_id=target_id,
            detail=detail,
        )
        self.db.add(log)
        self.db.commit()
