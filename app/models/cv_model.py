import uuid
from sqlalchemy import Column, String, Text, Float, JSON, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from app.clientsdatabase_clients.db_base_client import Base

class CVAnalysis(Base):
    __tablename__ = "cv_analyses"

    # الـ ID الأساسي للجدول
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # الـ user_id كـ String عشان يرضي سوبابيز والـ Local DB
    user_id = Column(String, nullable=True) 
    
    candidate_name = Column(String, nullable=True)
    
    # --- الإضافات الجديدة هنا ---
    university = Column(String, nullable=True)        # لتخزين اسم الجامعة
    graduation_year = Column(String, nullable=True)   # لتخزين سنة التخرج
    # ---------------------------

    cv_url = Column(String, nullable=False)
    raw_text = Column(Text, nullable=True)
    analysis_result = Column(JSON, nullable=False)    # الـ JSON الكامل هيفضل هنا برضه للاحتياط
    score = Column(Float, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())