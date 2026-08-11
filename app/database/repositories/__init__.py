from typing import Generic, TypeVar, Type, Optional, List
from sqlalchemy.orm import Session
from app.database.connection import Base

ModelType = TypeVar("ModelType", bound=Base)


class BaseRepository(Generic[ModelType]):
    """
    Abstract Generic Repository following Object-Oriented Programming (POO) design.
    Provides standard CRUD operations for database entities.
    """

    def __init__(self, model: Type[ModelType], db_session: Session):
        self.model = model
        self.db_session = db_session

    def get(self, item_id: str) -> Optional[ModelType]:
        return self.db_session.query(self.model).filter(self.model.id == item_id).first()

    def get_all(self, skip: int = 0, limit: int = 100) -> List[ModelType]:
        return self.db_session.query(self.model).offset(skip).limit(limit).all()

    def create(self, obj_in: dict) -> ModelType:
        db_obj = self.model(**obj_in)
        self.db_session.add(db_obj)
        self.db_session.commit()
        self.db_session.refresh(db_obj)
        return db_obj

    def delete(self, item_id: str) -> bool:
        obj = self.get(item_id)
        if obj:
            self.db_session.delete(obj)
            self.db_session.commit()
            return True
        return False
