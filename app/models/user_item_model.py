import uuid # 1. استيراد المكتبة لتوليد الـ ID
from sqlalchemy import Column, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID # 2. استيراد نوع البيانات UUID
from app.clientsdatabase_clients import Base

class UserItem(Base):
    __tablename__ = "user_items"

    # 3. تغيير الـ id ليكون UUID
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    # 4. تغيير الـ user_id والـ item_id ليكونوا UUID عشان يطابقوا الجداول الأصلية
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    item_id = Column(UUID(as_uuid=True), ForeignKey("items.id"), nullable=False)

    user = relationship("User", back_populates="items")
    item = relationship("Item", back_populates="user_items")

    __table_args__ = (
        UniqueConstraint('user_id', 'item_id', name='unique_user_item'),
    )