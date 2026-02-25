from typing import Type, TypeVar, Generic, Any
from sqlalchemy.orm import Session

T = TypeVar("T")

class BaseRepository(Generic[T]):
    def __init__(self, db: Session, model: Type[T]):
        self.db = db
        self.model = model

    # الدالة اللي كانت ناقصة ومسببة المشكلة:
    def create(self, obj: T) -> T:
        self.db.add(obj)
        self.db.commit()
        self.db.refresh(obj)
        return obj

    def get_all(self):
        return self.db.query(self.model).all()

    def get_by_id(self, obj_id: Any): 
        return self.db.query(self.model).filter(
            self.model.id == obj_id
        ).first()

    def update(self, obj: T) -> T:
        self.db.commit()
        self.db.refresh(obj)
        return obj

    def delete(self, obj: T) -> None:
        self.db.delete(obj)
        self.db.commit()