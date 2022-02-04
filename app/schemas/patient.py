from typing import Optional

from pydantic import BaseModel


# Shared properties
class PatientBase(BaseModel):
    name: Optional[str] = None
    age: Optional[str] = None


# Properties to receive on item creation
class PatientCreateRequest(PatientBase):
    ...


# Properties to receive on item update
class PatientUpdateRequest(PatientBase):
    ...


# Properties shared by models stored in DB
class PatientInDBBase(PatientBase):
    name: str
    age: str

    class Config:
        orm_mode = True


# Properties to return to client
class PatientResponse(PatientInDBBase):
    pass


# Properties properties stored in DB
class PatientInDBPatientResponse(PatientInDBBase):
    pass
