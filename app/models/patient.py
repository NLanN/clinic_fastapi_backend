from sqlalchemy import BigInteger, Column, ForeignKey, String

from db.base_model import BaseModel


class Patient(BaseModel):
    __tablename__ = "tbl_patients"

    name = Column(String(length=255), index=True)
    age = Column(String(length=255), index=True)
