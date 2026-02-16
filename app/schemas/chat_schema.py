from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class ChatCreate(BaseModel):
    prompt: str
    user_id: int  # ضفنا ده عشان نعرف مين المستخدم اللي بيسأل
    provider: Optional[str] = "cohere"  # ده الحقل اللي هتقدر تختار منه (cohere أو groq)

class ChatResponse(BaseModel):
    prompt: str
    response: str
    created_at: datetime

    class Config:
        from_attributes = True