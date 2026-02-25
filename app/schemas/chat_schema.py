import uuid # 1. استيراد المكتبة
from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class ChatCreate(BaseModel):
    prompt: str
    # 2. تغيير user_id من int لـ uuid.UUID
    user_id: uuid.UUID  
    provider: Optional[str] = "cohere"

class ChatResponse(BaseModel):
    # 3. يفضل إضافة الـ ID الخاص بالرسالة نفسها لو هتحتاجه في الفرونت إند
    id: uuid.UUID 
    prompt: str
    response: str
    created_at: datetime

    class Config:
        from_attributes = True