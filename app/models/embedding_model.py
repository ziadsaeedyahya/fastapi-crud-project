import uuid # 1. استيراد المكتبة
from sqlalchemy import Column, Text, ForeignKey, DateTime
from sqlalchemy.dialects.postgresql import UUID, ARRAY, FLOAT # 2. تجميع استيرادات Postgres هنا
from sqlalchemy.sql import func
from app.clientsdatabase_clients import Base 

class ItemEmbedding(Base):
    __tablename__ = "items_embeddings"

    # 3. تغيير الـ id ليكون UUID
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    
    # 4. تغيير الـ user_id ليكون UUID عشان يقدر يربط مع جدول users الجديد
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"))
    
    content = Column(Text, nullable=False)
    embedding = Column(ARRAY(FLOAT)) # الـ 1024 رقم هيفضلوا زي ما هما
    created_at = Column(DateTime(timezone=True), server_default=func.now())