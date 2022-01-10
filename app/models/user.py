from sqlalchemy import Boolean, Column, String
from sqlalchemy.orm import relationship

from db.base_model import BaseModel


class User(BaseModel):
    __tablename__ = "tbl_users"

    full_name = Column(String(length=255), index=True)
    email = Column(String(length=255), unique=True, index=True, nullable=False)
    hashed_password = Column(String(length=255), nullable=False)
    is_active = Column(Boolean(), default=True)
    is_superuser = Column(Boolean(), default=False)
    items = relationship("Item", back_populates="owner")
