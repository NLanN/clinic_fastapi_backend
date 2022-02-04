from sqlalchemy import BigInteger, Column
from sqlalchemy.ext.declarative import as_declarative, declared_attr


@as_declarative()
class BaseModel(object):
    __abstract__ = True
    __table_args__ = {"extend_existing": True}
    __name__: str

    id = Column(BigInteger, primary_key=True, index=True)

    @declared_attr
    def __tablename__(cls) -> str:
        return cls.__name__.lower()
