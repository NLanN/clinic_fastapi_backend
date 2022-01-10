from typing import List

from fastapi.encoders import jsonable_encoder
from sqlalchemy.orm import Session

from db.mixin import DBMixin
from models.item import Item
from schemas.item import ItemCreateRequest, ItemUpdateRequest


class ItemService(DBMixin[Item, ItemCreateRequest, ItemUpdateRequest]):
    def create_with_owner(self, session: Session, *, obj_in: ItemCreateRequest, owner_id: int) -> Item:
        obj_in_data = jsonable_encoder(obj_in)
        db_obj = self.model(**obj_in_data, owner_id=owner_id)
        session.add(db_obj)
        session.commit()
        session.refresh(db_obj)
        return db_obj

    def get_multi_by_owner(self, session: Session, *, owner_id: int, skip: int = 0, limit: int = 100) -> List[Item]:
        return session.query(self.model).filter(Item.owner_id == owner_id).offset(skip).limit(limit).all()


item_service = ItemService(Item)
