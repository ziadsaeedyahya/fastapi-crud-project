import uuid # 1. لازم نستورد مكتبة uuid
from pydantic import BaseModel
from typing import Optional

class ItemCreate(BaseModel):
    name: str
    description: Optional[str] = None

class ItemUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None

class ItemResponse(ItemCreate):
    # 2. تغيير الـ id من int لـ uuid.UUID
    id: uuid.UUID 

    class Config:
        from_attributes = True