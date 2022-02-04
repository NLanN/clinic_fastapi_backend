from datetime import timedelta
from typing import Any

from fastapi import APIRouter, Body, Depends
from fastapi import HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from api.deps import get_current_user
from core.configs import settings
from core.sercurity import create_access_token, get_password_hash
from db.deps import get_session
from models.user import User
from schemas.msg import Msg
from schemas.token import Token
from schemas.user import UserResponse
from services.user import user_service
from utils.helpers import verify_password_reset_token

router = APIRouter()


@router.post("/access-token", response_model=Token)
def login_access_token(
        session: Session = Depends(get_session),
        form_data: OAuth2PasswordRequestForm = Depends(),
) -> Any:
    """
    OAuth2 compatible token login, get an access token for future requests
    """
    user = user_service.authenticate(session, email=form_data.username, password=form_data.password)
    if not user:
        raise HTTPException(status_code=400, detail="Incorrect email or password")
    elif not user_service.is_active(user):
        raise HTTPException(status_code=400, detail="Inactive user")
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    return {
        "access_token": create_access_token(user.id, expires_delta=access_token_expires),
        "token_type": "bearer",
    }


@router.post("/test-token", response_model=UserResponse)
def test_token(current_user: User = Depends(get_current_user)) -> Any:
    """
    Test access token
    """
    return current_user


@router.post("/reset-password/", response_model=Msg)
def reset_password(
        token: str = Body(...),
        new_password: str = Body(...),
        session: Session = Depends(get_session),
) -> Any:
    """
    Reset password
    """
    email = verify_password_reset_token(token)
    if not email:
        raise HTTPException(status_code=400, detail="Invalid token")
    user = user_service.get_by_email(session, email=email)
    if not user:
        raise HTTPException(
            status_code=404,
            detail="The user with this username does not exist in the system.",
        )
    elif not user_service.is_active(user):
        raise HTTPException(status_code=400, detail="Inactive user")
    hashed_password = get_password_hash(new_password)
    user.hashed_password = hashed_password
    session.add(user)
    session.commit()
    return {"msg": "Password updated successfully"}
