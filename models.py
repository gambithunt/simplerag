from sqlalchemy import Column, Integer, String, Text, BigInteger, Boolean, TIMESTAMP, ForeignKey, JSON
from sqlalchemy.sql import func
from database import Base


class Document(Base):
    __tablename__ = "documents"
    
    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String(500), nullable=False)
    file_path = Column(String(1000), nullable=False)
    file_type = Column(String(50), nullable=False)
    file_size_bytes = Column(BigInteger)
    classification = Column(String(50), default="internal")
    department = Column(String(100))
    content_preview = Column(Text)
    metadata_json = Column(JSON)
    is_active = Column(Boolean, default=True)
    created_at = Column(TIMESTAMP, server_default=func.now())
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())


class QueryAuditLog(Base):
    __tablename__ = "query_audit_log"
    
    id = Column(Integer, primary_key=True, index=True)
    query = Column(Text, nullable=False)
    response_time_ms = Column(Integer)
    documents_accessed = Column(JSON)
    created_at = Column(TIMESTAMP, server_default=func.now())
