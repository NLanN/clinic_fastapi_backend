from pydantic import BaseModel


class BaseSchema(BaseModel):
    class Config:
        orm_mode = True


class APIResponse(BaseSchema):
    code: int
    data: dict


class APIListResponse(BaseSchema):
    code: int
    count: int
    data: list


class ErrorResponse(BaseSchema):
    code: int
    name: str
    description: str
