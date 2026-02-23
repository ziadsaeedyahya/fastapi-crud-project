from sqlalchemy import Column, Integer, Text, ForeignKey, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from app.clientsdatabase_clients import Base # تأكد من اسم ملف الـ Base عندك

from sqlalchemy.dialects.postgresql import ARRAY, FLOAT

class ItemEmbedding(Base):
    __tablename__ = "items_embeddings"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"))
    content = Column(Text, nullable=False)
    embedding = Column(ARRAY(FLOAT)) # هنخزن الـ 1024 رقم هنا
    created_at = Column(DateTime(timezone=True), server_default=func.now())