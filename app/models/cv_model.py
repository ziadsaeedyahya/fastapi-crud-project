import uuid
from sqlalchemy import Column, String, Text, Float, JSON, ForeignKey, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from app.clientsdatabase_clients.db_base_client import Base

class CVAnalysis(Base):
    __tablename__ = "cv_analyses"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"))
    candidate_name = Column(String, nullable=True)
    cv_url = Column(String, nullable=False) # لينك الملف في الـ Storage
    raw_text = Column(Text, nullable=True)   # النص المستخرج
    analysis_result = Column(JSON, nullable=False) # الـ JSON اللي فيه الـ Skills والضعف
    score = Column(Float, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())