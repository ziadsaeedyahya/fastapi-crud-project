from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Text
from app.clientsdatabase_clients.db_base_client import Base
from datetime import datetime

class ChatHistory(Base):
    __tablename__ = "chat_history"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id")) # ربط مع المستخدم
    prompt = Column(Text)                            # سؤال زياد
    response = Column(Text)                          # رد Cohere
    created_at = Column(DateTime, default=datetime.utcnow)