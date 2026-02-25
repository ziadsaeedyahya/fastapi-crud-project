import uuid # 1. استيراد المكتبة
from sqlalchemy import Column, String
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID # 2. استيراد النوع الخاص ببوستجرس
from app.clientsdatabase_clients import Base

class Item(Base):
    __tablename__ = "items"

    # 3. تغيير الـ id ليكون UUID مع التوليد التلقائي
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    
    name = Column(String, nullable=False)
    description = Column(String, nullable=True)

    # العلاقة دي هتفضل زي ما هي، بس هي دلوقتي فاهمة إنها بتتعامل مع UUIDs
    user_items = relationship("UserItem", back_populates="item", cascade="all, delete-orphan")