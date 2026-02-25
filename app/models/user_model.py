import uuid # 1. لازم نستورد مكتبة الـ uuid
from sqlalchemy import Column, String
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID # 2. استيراد نوع الـ UUID الخاص ببوستجرس
from app.clientsdatabase_clients import Base

class User(Base):
    __tablename__ = "users"

    # 3. تعديل الـ id ليكون UUID مع توليد تلقائي (uuid4)
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    
    username = Column(String, unique=True, nullable=False)
    email = Column(String, unique=True, nullable=False)
    full_name = Column(String, nullable=False)
    password_hash = Column(String, nullable=False)

    items = relationship("UserItem", back_populates="user", cascade="all, delete-orphan")