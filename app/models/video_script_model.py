from sqlalchemy import Column, Integer, Text, String, ForeignKey, DateTime
from sqlalchemy.dialects.postgresql import ARRAY, FLOAT
from sqlalchemy.sql import func
from app.clientsdatabase_clients.db_base_client import Base

class VideoScriptEmbedding(Base):
    __tablename__ = "video_script_embeddings"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"))
    video_url = Column(String, nullable=False)   # رابط الفيديو في سوبابيز
    script_text = Column(Text, nullable=True)    # النص المستخرج (السكريبت)
    embedding = Column(ARRAY(FLOAT), nullable=True) # المتجهات (1024 رقم)
    created_at = Column(DateTime(timezone=True), server_default=func.now())