from typing import Any, List

from fastapi import APIRouter, Body, Depends, HTTPException
from fastapi.encoders import jsonable_encoder
from pydantic.networks import EmailStr
from sqlalchemy.orm import Session

from api.deps import get_current_active_superuser, get_current_active_user
from core.configs import settings
from db.deps import get_session
from models.user import User
from schemas.user import UserCreateRequest, UserResponse, UserUpdateRequest
from services.user import user_service

router = APIRouter()


@router.get("/", response_model=List[UserResponse])
def read_users(
    session: Session = Depends(get_session),
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_active_superuser),
) -> Any:
    """
    Retrieve users.
    """
    users = user_service.get_multi(session, skip=skip, limit=limit)
    return users


@router.post("/", response_model=UserResponse)
def create_user(
    *,
    session: Session = Depends(get_session),
    user_in: UserCreateRequest,
    current_user: User = Depends(get_current_active_superuser),
) -> Any:
    """
    Create new user.
    """
    user = user_service.get_by_email(session, email=user_in.email)
    if user:
        raise HTTPException(
            status_code=400,
            detail="The user with this username already exists in the system.",
        )
    user = user_service.create(session, obj_in=user_in)
    return user


@router.put("/me", response_model=UserResponse)
def update_user_me(
    *,
    session: Session = Depends(get_session),
    password: str = Body(None),
    full_name: str = Body(None),
    email: EmailStr = Body(None),
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    Update own user.
    """
    current_user_data = jsonable_encoder(current_user)
    user_in = UserUpdateRequest(**current_user_data)
    if password is not None:
        user_in.password = password
    if full_name is not None:
        user_in.full_name = full_name
    if email is not None:
        user_in.email = email
    user = user_service.update(session, db_obj=current_user, obj_in=user_in)
    return user


@router.get("/me", response_model=UserResponse)
def read_user_me(
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    Get current user.
    """
    return current_user


@router.post("/open", response_model=UserResponse)
def create_user_open(
    *,
    session: Session = Depends(get_session),
    password: str = Body(...),
    email: EmailStr = Body(...),
    full_name: str = Body(None),
) -> Any:
    """
    Create new user without the need to be logged in.
    """
    if not settings.USERS_OPEN_REGISTRATION:
        raise HTTPException(
            status_code=403,
            detail="Open user registration is forbidden on this server",
        )
    user = user_service.get_by_email(session, email=email)
    if user:
        raise HTTPException(
            status_code=400,
            detail="The user with this username already exists in the system",
        )
    user_in = UserCreateRequest(password=password, email=email, full_name=full_name)
    user = user_service.create(session, obj_in=user_in)
    return user


@router.get("/{user_id}", response_model=UserResponse)
def read_user_by_id(
    user_id: str,
    current_user: User = Depends(get_current_active_user),
    session: Session = Depends(get_session),
) -> Any:
    """
    Get a specific user by id.
    """
    user = user_service.get(session, id=user_id)
    if user == current_user:
        return user
    if not user_service.is_superuser(current_user):
        raise HTTPException(status_code=400, detail="The user doesn't have enough privileges")
    return user


@router.put("/{user_id}", response_model=UserResponse)
def update_user(
    *,
    session: Session = Depends(get_session),
    user_id: str,
    user_in: UserUpdateRequest,
    current_user: User = Depends(get_current_active_superuser),
) -> Any:
    """
    Update a user.
    """
    user = user_service.get(session, id=user_id)
    if not user:
        raise HTTPException(
            status_code=404,
            detail="The user with this username does not exist in the system",
        )
    user = user_service.update(session, db_obj=user, obj_in=user_in)
    return user
