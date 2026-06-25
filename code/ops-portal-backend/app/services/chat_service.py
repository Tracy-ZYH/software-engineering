from typing import Optional
from sqlalchemy.orm import Session
from app.utils.rag_client import chat_query
from app.models.ticket import OpsTicket, TicketStatus
from app.schemas.chat import ChatResponse


class ChatService:
    """对话查询服务"""

    def __init__(self, db: Session):
        self.db = db

    async def ask(self, question: str, contact_info: Optional[str] = None) -> dict:
        """
        向知识库提问

        1. 调用 AnythingLLM 对话接口
        2. 有答案 → 直接返回
        3. 无答案 / RAG 异常 → 创建工单 → 返回提示
        """
        # 1. 调用 RAG（增加异常兜底，RAG 不可达时不崩后端）
        try:
            rag_result = await chat_query(question)
            answer = rag_result.get("textResponse", "")
            sources = rag_result.get("sources", [])
            has_answer = bool(sources)
        except Exception as e:
            answer = ""
            sources = []
            has_answer = False
            print(f"[ChatService] RAG 调用异常，将创建工单: {e}")

        # 即使 sources 不为空，也要检查回答文本是否实质为"无法回答"
        NO_ANSWER_PHRASES = ("抱歉", "没有找到", "无法理解", "无法回答", "无法帮助",
                             "无法确定", "不知道", "不清楚", "不能理解",
                             "我不确定", "我不清楚", "我不知道",
                             "i don't know", "i'm not sure", "don't understand",
                             "unable to answer", "no information", "no relevant")
        if has_answer and answer and not any(p in answer.lower() for p in NO_ANSWER_PHRASES):
            return ChatResponse(
                answer=answer,
                has_answer=True,
                ticket_id=None,
            )
        # 有 sources 但回答文本是"无法回答"类型 → 降级为无答案，创建工单
        has_answer = False

        # 2. 无答案 / RAG 异常 → 创建工单
        ticket = OpsTicket(
            question=question,
            rag_answer=answer,
            status=TicketStatus.PENDING,
            created_by="在线用户",
            contact_info=contact_info or "未提供",
        )
        self.db.add(ticket)
        self.db.commit()
        self.db.refresh(ticket)

        return ChatResponse(
            answer="抱歉，知识库中暂未找到相关答案。已为您创建工单，运维人员将尽快处理。",
            has_answer=False,
            ticket_id=ticket.id,
        )

