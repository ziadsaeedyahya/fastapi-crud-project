import uuid # 1. استيراد المكتبة
from sqlalchemy import Column, String, ForeignKey, DateTime, Text
from sqlalchemy.dialects.postgresql import UUID # 2. استيراد نوع الـ UUID لبوستجرس
from app.clientsdatabase_clients.db_base_client import Base
from sqlalchemy.sql import func # 3. الأفضل نستخدم func.now() للوقت

class ChatHistory(Base):
    __tablename__ = "chat_history"

    # 4. تغيير الـ id ليكون UUID
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    
    # 5. تغيير الـ user_id ليكون UUID عشان يقدر يربط مع اليوزر الجديد
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id")) 
    
    prompt = Column(Text)              # سؤال المستخدم
    response = Column(Text)            # رد الـ AI
    
    # استخدمنا func.now() عشان الداتابيز هي اللي تحط الوقت وقت الحفظ
    created_at = Column(DateTime(timezone=True), server_default=func.now())