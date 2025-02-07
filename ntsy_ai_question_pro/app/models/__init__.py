# app/models/__init__.py

from dataclasses import dataclass
from typing import List, Dict, Optional
from datetime import datetime

@dataclass
class KnowledgeBase:
    """知识库模型"""
    name: str
    created_at: datetime
    document_count: int = 0
    description: Optional[str] = None

@dataclass
class Document:
    """文档模型"""
    filename: str
    content: str
    metadata: Dict
    knowledge_base: str
    created_at: datetime

@dataclass
class ChatMessage:
    """聊天消息模型"""
    role: str  # 'user' 或 'assistant'
    content: str
    timestamp: datetime
    knowledge_base: Optional[str] = None

@dataclass
class ChatSession:
    """聊天会话模型"""
    id: str
    messages: List[ChatMessage]
    created_at: datetime
    updated_at: datetime
    knowledge_base: Optional[str] = None

@dataclass
class UploadResult:
    """文件上传结果模型"""
    filename: str
    success: bool
    error: Optional[str] = None
    document_id: Optional[str] = None

class ModelRegistry:
    """模型注册表，用于管理所有数据模型"""
    
    @staticmethod
    def create_knowledge_base(name: str, description: Optional[str] = None) -> KnowledgeBase:
        """创建新的知识库实例"""
        return KnowledgeBase(
            name=name,
            description=description,
            created_at=datetime.utcnow()
        )

    @staticmethod
    def create_document(
        filename: str,
        content: str,
        knowledge_base: str,
        metadata: Optional[Dict] = None
    ) -> Document:
        """创建新的文档实例"""
        return Document(
            filename=filename,
            content=content,
            metadata=metadata or {},
            knowledge_base=knowledge_base,
            created_at=datetime.utcnow()
        )

    @staticmethod
    def create_chat_message(
        role: str,
        content: str,
        knowledge_base: Optional[str] = None
    ) -> ChatMessage:
        """创建新的聊天消息实例"""
        return ChatMessage(
            role=role,
            content=content,
            timestamp=datetime.utcnow(),
            knowledge_base=knowledge_base
        )

    @staticmethod
    def create_chat_session(
        session_id: str,
        knowledge_base: Optional[str] = None
    ) -> ChatSession:
        """创建新的聊天会话实例"""
        now = datetime.utcnow()
        return ChatSession(
            id=session_id,
            messages=[],
            created_at=now,
            updated_at=now,
            knowledge_base=knowledge_base
        )

    @staticmethod
    def create_upload_result(
        filename: str,
        success: bool,
        error: Optional[str] = None,
        document_id: Optional[str] = None
    ) -> UploadResult:
        """创建文件上传结果实例"""
        return UploadResult(
            filename=filename,
            success=success,
            error=error,
            document_id=document_id
        )