"""
AnythingLLM RAG API 客户端
封装对话查询、文本上传两个核心接口
"""
import httpx
from typing import Optional

from app.config import RAG_CONFIG

# ---------- 配置 ----------
API_BASE = RAG_CONFIG["api_base"].rstrip("/")
API_KEY = RAG_CONFIG["api_key"]
WORKSPACE = RAG_CONFIG["workspace"]
HEADERS = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json",
}


# ============================================================
# 公共错误处理
# ============================================================

class RAGClientError(Exception):
    """RAG API 调用异常"""
    def __init__(self, message: str, status_code: int = 500):
        self.message = message
        self.status_code = status_code
        super().__init__(self.message)


# ============================================================
# 1. 对话查询接口
# ============================================================

async def chat_query(question: str) -> dict:
    """
    向知识库提问，获取答案
    :param question: 用户问题
    :return: RAG 响应（含 textResponse）
    :raises RAGClientError: 调用失败时
    """
    url = f"{API_BASE}/api/v1/workspace/{WORKSPACE}/chat"
    payload = {
        "message": question,
        "mode": "query",  # 仅向量检索，速度快（不经过 LLM 生成回答）
    }

    async with httpx.AsyncClient(timeout=60.0) as client:
        try:
            response = await client.post(url, json=payload, headers=HEADERS)
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            raise RAGClientError(
                f"RAG 查询失败: HTTP {e.response.status_code} - {e.response.text}",
                status_code=e.response.status_code,
            )
        except httpx.RequestError as e:
            raise RAGClientError(f"RAG 服务连接失败: {str(e)}")


# ============================================================
# 2. 文本上传接口
# ============================================================
'''
async def upload_raw_text(
    text_content: str,
    title: str = "运维FAQ-自动录入",
    doc_author: str = "运维系统",
    description: str = "工单处理完成后自动录入",
) -> dict:
    """
    直接将文本内容上传到知识库
    :param text_content: 文本内容（建议格式："问题：xxx\n解决方案：xxx"）
    :param title:        文档标题
    :param doc_author:   文档作者
    :param description:  文档描述
    :return: 上传结果
    :raises RAGClientError: 调用失败时
    """
    url = f"{API_BASE}/api/v1/document/raw-text"
    payload = {
        "textContent": text_content,
        "addToWorkspaces": WORKSPACE,  # API 要求数组格式
        "metadata": {
            "title": title,
            "docAuthor": doc_author,
            "description": description,
        },
    }

    async with httpx.AsyncClient(timeout=60.0) as client:
        try:
            response = await client.post(url, json=payload, headers=HEADERS)
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            raise RAGClientError(
                f"RAG 文本上传失败: HTTP {e.response.status_code} - {e.response.text}",
                status_code=e.response.status_code,
            )
        except httpx.RequestError as e:
            raise RAGClientError(f"RAG 服务连接失败: {str(e)}")

'''
async def upload_raw_text(
    text_content: str,
    title: str = "运维FAQ-自动录入",
    doc_author: str = "运维系统",
    description: str = "工单处理完成后自动录入",
) -> dict:
    """
    直接将文本内容上传到知识库
    :param text_content: 文本内容（建议格式："问题：xxx\n解决方案：xxx"）
    :param title:        文档标题
    :param doc_author:   文档作者
    :param description:  文档描述
    :return: 上传结果
    :raises RAGClientError: 调用失败时
    """
    url = f"{API_BASE}/api/v1/document/raw-text"
    payload = {
        "textContent": text_content,
        "addToWorkspaces": WORKSPACE,
        "metadata": {
            "title": title,
            "docAuthor": doc_author,
            "description": description,
        },
    }

    async with httpx.AsyncClient(timeout=60.0) as client:
        try:
            response = await client.post(url, json=payload, headers=HEADERS)
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            raise RAGClientError(
                f"RAG 文本上传失败: HTTP {e.response.status_code} - {e.response.text}",
                status_code=e.response.status_code,
            )
        except httpx.RequestError as e:
            raise RAGClientError(f"RAG 服务连接失败: {str(e)}")

def format_knowledge_text(question: str, answer: str) -> str:
    """
    将问题和答案格式化为知识库文本
    """
    return f"问题：{question}\n解决方案：{answer}"



