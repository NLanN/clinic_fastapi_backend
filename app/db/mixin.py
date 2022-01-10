from typing import Any, Dict, Generic, List, Optional, Type, TypeVar, Union

from fastapi.encoders import jsonable_encoder
from pydantic import BaseModel
from sqlalchemy import inspect, select
from sqlalchemy.orm import Session

from db.base_model import BaseModel as Base

ModelType = TypeVar("ModelType", bound=Base)
CreateSchemaType = TypeVar("CreateSchemaType", bound=BaseModel)
UpdateSchemaType = TypeVar("UpdateSchemaType", bound=BaseModel)


class DBMixin(Generic[ModelType, CreateSchemaType, UpdateSchemaType]):
    def __init__(self, model: Type[ModelType]):
        """
        CRUD object with default methods to Create, Read, Update, Delete (CRUD).

        **Parameters**

        * `model`: A SQLAlchemy model class
        * `schema`: A Pydantic model (schema) class
        """
        self.model = model

    def get(self, session: Session, id: Any) -> Optional[ModelType]:
        return session.query(self.model).filter(self.model.id == id).first()

    def is_exist(self, session: Session, flt: dict):
        return session.execute(select(self.model).filter_by(**flt)).scalar()

    # SQLALCHEMY 2.0 style
    def get_one_by_filter(self, session: Session, flt: dict):
        return session.execute(select(self.model).filter_by(**flt)).scalar_one()

    def get_multi(self, session: Session, *, skip: int = 0, limit: int = 100) -> List[ModelType]:
        return session.query(self.model).offset(skip).limit(limit).all()

    # SQLALCHEMY 2.0 style
    def get_all(self, session: Session, *, skip: int = 0, limit: int = 100) -> List[ModelType]:
        return session.execute(select(self.model).offset(skip).limit(limit)).scalars().all()

    def create(self, session: Session, *, obj_in: CreateSchemaType) -> ModelType:
        obj_in_data = jsonable_encoder(obj_in)
        db_obj = self.model(**obj_in_data)  # type: ignore
        session.add(db_obj)
        session.commit()
        session.refresh(db_obj)
        return db_obj

    def update(
        self, session: Session, *, db_obj: ModelType, obj_in: Union[UpdateSchemaType, Dict[str, Any]]
    ) -> ModelType:
        obj_data = jsonable_encoder(db_obj)
        if isinstance(obj_in, dict):
            update_data = obj_in
        else:
            update_data = obj_in.dict(exclude_unset=True)
        for field in obj_data:
            if field in update_data:
                setattr(db_obj, field, update_data[field])
        session.add(db_obj)
        session.commit()
        session.refresh(db_obj)
        return db_obj

    def remove(self, session: Session, *, id: int) -> ModelType:
        obj = session.query(self.model).get(id)
        session.delete(obj)
        session.commit()
        return obj

    def to_dict(self, obj, level: int = 1, current_level: int = 0):
        """
        level can't above 5
        """
        if not obj or current_level > level or current_level > 5:
            return None
        res = {}
        res.update({c.key: getattr(obj, c.key) for c in inspect(obj).mapper.column_attrs})
        if inspect(obj).mapper.relationships.keys():
            current_level += 1
            for key in inspect(obj).mapper.relationships.keys():
                res[key] = self.to_dict(getattr(obj, key), level, current_level)
        return res
