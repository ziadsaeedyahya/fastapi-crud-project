import uuid # 1. استيراد المكتبة
from pydantic import BaseModel
from typing import Optional

class UserCreate(BaseModel):
    username: str
    email: str
    full_name: str
    password: str

class UserUpdate(BaseModel):
    username: Optional[str] = None
    email: Optional[str] = None
    full_name: Optional[str] = None
    password: Optional[str] = None

class UserResponse(BaseModel):
    # 2. تغيير id المستخدم ليكون UUID
    id: uuid.UUID 
    username: str
    email: str
    full_name: str

    class Config:
        from_attributes = True

# Token response (مش محتاج تعديل)
class Token(BaseModel):
    access_token: str
    token_type: str

# Token data (مهم جداً!)
class TokenData(BaseModel):
    # 3. تغيير الـ id المتوقع داخل الـ Token ليكون UUID
    id: Optional[uuid.UUID] = None