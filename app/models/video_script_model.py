import uuid
from sqlalchemy import Column, Text, String, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from sqlalchemy.dialects.postgresql import UUID # استيراد نوع UUID الخاص بـ Postgres
from app.clientsdatabase_clients.db_base_client import Base
from pgvector.sqlalchemy import Vector

class VideoScriptEmbedding(Base):
    __tablename__ = "video_script_embeddings"
    
    # 1. تغيير الـ id ليكون UUID
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    
    # 2. تغيير user_id ليكون UUID (بافتراض إن جدول اليوزرز عندك UUID برضه)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"))
    
    video_url = Column(String, nullable=False)
    script_text = Column(Text, nullable=True)
    embedding = Column(Vector(1536), nullable=True) 
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    chunks = relationship("VideoScriptChunk", back_populates="parent_video", cascade="all, delete-orphan")

class VideoScriptChunk(Base):
    __tablename__ = "video_script_chunks"
    
    # 3. تغيير id القطعة ليكون UUID
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    
    # 4. الـ ForeignKey هنا لازم يطابق نوع الـ id اللي فوق (UUID)
    video_id = Column(UUID(as_uuid=True), ForeignKey("video_script_embeddings.id", ondelete="CASCADE"))
    
    chunk_content = Column(Text, nullable=False)
    embedding = Column(Vector(1536), nullable=True) 
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    parent_video = relationship("VideoScriptEmbedding", back_populates="chunks")