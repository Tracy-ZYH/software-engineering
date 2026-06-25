"""
工单管理业务逻辑
"""
from datetime import datetime, timezone
from typing import Optional

from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import desc

from app.models.account import OpsAccount
from app.models.ticket import OpsTicket, TicketStatus
from app.models.knowledge import OpsKnowledge, KnowledgeSource
from app.models.operation_log import OpsOperationLog
from app.schemas.ticket import TicketCreate, TicketUpdate
from app.schemas.knowledge import KnowledgeCreate
from app.utils.rag_client import upload_raw_text, format_knowledge_text


class TicketService:
    """工单管理服务"""

    def __init__(self, db: Session, operator: Optional[OpsAccount] = None):
        self.db = db
        self.operator = operator  # 当前操作人

    # -----------------------------------------------------------
    # 创建工单（前台调用）
    # -----------------------------------------------------------
    def create(self, data: TicketCreate) -> OpsTicket:
        """创建工单"""
        ticket = OpsTicket(
            question=data.question,
            rag_answer=data.rag_answer,
            status=TicketStatus.PENDING,
            created_by=data.created_by,
            contact_info=data.contact_info,
        )
        self.db.add(ticket)
        self.db.commit()
        self.db.refresh(ticket)

        self._log_operation("CREATE", "TICKET", ticket.id,
                            f"创建工单: {ticket.question[:50]}...")
        return ticket

    # -----------------------------------------------------------
    # 查询工单列表
    # -----------------------------------------------------------
    def list_tickets(
        self,
        page: int = 1,
        page_size: int = 10,
        status: Optional[str] = None,
        keyword: Optional[str] = None,
    ) -> dict:
        """查询工单列表（分页 + 筛选）"""
        query = self.db.query(OpsTicket)

        if status:
            query = query.filter(OpsTicket.status == status)
        if keyword:
            like_pattern = f"%{keyword}%"
            query = query.filter(
                OpsTicket.question.like(like_pattern)
            )

        query = query.order_by(desc(OpsTicket.created_at))
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
    # 查询单个工单
    # -----------------------------------------------------------
    def get_by_id(self, ticket_id: int) -> OpsTicket:
        """查询工单详情"""
        ticket = self.db.query(OpsTicket).filter(OpsTicket.id == ticket_id).first()
        if not ticket:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="工单不存在",
            )
        return ticket

    # -----------------------------------------------------------
    # 处理工单
    # -----------------------------------------------------------
    def process(self, ticket_id: int, data: TicketUpdate) -> OpsTicket:
        """处理工单（填写处理方案）"""
        ticket = self.get_by_id(ticket_id)

        ticket.status = data.status
        if data.resolution is not None:
            ticket.resolution = data.resolution
            ticket.resolver_id = self.operator.id if self.operator else None
        if data.status == TicketStatus.RESOLVED:
            ticket.resolved_at = datetime.now(timezone.utc)

        self.db.commit()
        self.db.refresh(ticket)

        self._log_operation("UPDATE", "TICKET", ticket_id,
                            f"处理工单: 状态={data.status.value}")
        return ticket

    # -----------------------------------------------------------
    # 同步工单到知识库 + RAG
    # -----------------------------------------------------------
    async def sync_to_knowledge(self, ticket_id: int,
                                category: Optional[str] = None) -> dict:
        """
        将已处理的工单同步到知识库，同时调用 AnythingLLM 上传文本
        :param ticket_id: 工单ID
        :param category:  知识分类（可选）
        :return: 同步结果
        """
        ticket = self.get_by_id(ticket_id)

        if ticket.status != TicketStatus.RESOLVED:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="仅已解决的工单可同步到知识库",
            )
        # 允许覆盖同步（即使已同步过也可重新上传到 RAG）
        if ticket.is_added_to_kb:
            print(f"[Sync] 工单 #{ticket_id} 已同步过，将覆盖重新上传到 RAG")
        if not ticket.resolution:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="工单缺少处理方案，请先填写处理方案",
            )

        # 1. 写入本地知识库表
        knowledge = OpsKnowledge(
            question=ticket.question,
            answer=ticket.resolution,
            category=category or "工单处理",
            source=KnowledgeSource.TICKET,
            source_ticket_id=ticket.id,
            created_by=self.operator.id if self.operator else None,
        )
        self.db.add(knowledge)

        # 2. 更新工单标记
        ticket.is_added_to_kb = 1
        self.db.commit()
        self.db.refresh(knowledge)

        # 3. 调用 AnythingLLM 文本上传接口（失败不阻塞本地保存）
        text_content = format_knowledge_text(ticket.question, ticket.resolution)
        rag_success = False
        try:
            rag_result = await upload_raw_text(
                text_content=text_content,
                title=f"工单#{ticket.id}-{ticket.question[:30]}",
                doc_author=self.operator.real_name if self.operator else "运维系统",
            )
            rag_success = True
            print(f"[Sync] 工单 #{ticket_id} RAG 上传成功")
        except Exception as e:
            rag_result = {"error": str(e), "success": False}
            print(f"[Sync] 工单 #{ticket_id} RAG 上传失败: {e}")

        self._log_operation("SYNC_KB", "TICKET", ticket_id,
                            f"工单同步到知识库, RAG结果: {rag_result.get('success', False)}")

        return {
            "knowledge_id": knowledge.id,
            "rag_result": rag_result,
        }

    # -----------------------------------------------------------
    # 内部：记录操作日志
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
