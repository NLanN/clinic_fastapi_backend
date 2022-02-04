from fastapi import APIRouter

from api.v1.endpoints.auth import router as auth_router
from api.v1.endpoints.patients import router as patient_router
from api.v1.endpoints.item_f import router as item_router
from api.v1.endpoints.users import router as user_router

api_router = APIRouter()
api_router.include_router(auth_router, prefix="/auth", tags=["auth"])
api_router.include_router(user_router, prefix="/user", tags=["user"])
api_router.include_router(item_router, prefix="/item", tags=["item"])
api_router.include_router(patient_router, prefix="/patient", tags=["patient"])
