from sqlalchemy.orm import Session
from app.models.chat_model import ChatHistory
from app.repositories.base_repository import BaseRepository

class ChatRepository(BaseRepository):
    def __init__(self, db: Session):
        super().__init__(db, ChatHistory)

    def get_history_by_user(self, user_id: int, limit: int = 5):
        return self.db.query(ChatHistory).filter(ChatHistory.user_id == user_id)\
            .order_by(ChatHistory.created_at.desc()).limit(limit).all()