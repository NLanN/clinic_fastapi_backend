from sqlalchemy import BigInteger, Column, ForeignKey, String
from sqlalchemy.orm import relationship

from db.base_model import BaseModel


class Item(BaseModel):
    __tablename__ = "tbl_items"

    title = Column(String(length=255), index=True)
    description = Column(String(length=255), index=True)
    owner_id = Column(BigInteger, ForeignKey("tbl_users.id"))
    owner = relationship("User", back_populates="items")
