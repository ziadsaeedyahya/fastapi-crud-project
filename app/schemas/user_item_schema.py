import uuid # 1. استيراد المكتبة
from pydantic import BaseModel

class UserItemCreate(BaseModel):
    # 2. تغيير user_id و item_id لـ uuid.UUID
    user_id: uuid.UUID
    item_id: uuid.UUID

class UserItemResponse(UserItemCreate):
    # 3. تغيير id السجل نفسه لـ uuid.UUID
    id: uuid.UUID

    class Config:
        from_attributes = True