from typing import Any, Dict, Optional, Union

from sqlalchemy.orm import Session

from core.sercurity import get_password_hash, verify_password
from db.mixin import DBMixin
from models.user import User
from schemas.user import UserCreateRequest, UserUpdateRequest, UserResponse


class UserService(DBMixin[User, UserCreateRequest, UserUpdateRequest]):
    def get_by_email(self, session: Session, *, email: str) -> Optional[UserResponse]:
        return session.query(User).filter(User.email == email).first()

    def create(self, session: Session, *, obj_in: UserCreateRequest) -> UserResponse:
        db_obj = User(
            email=obj_in.email,
            hashed_password=get_password_hash(obj_in.password),
            full_name=obj_in.full_name,
            is_superuser=obj_in.is_superuser,
        )
        session.add(db_obj)
        session.commit()
        session.refresh(db_obj)
        return db_obj

    def update(self, session: Session, *, db_obj: User, obj_in: Union[UserUpdateRequest, Dict[str, Any]]) -> UserResponse:
        if isinstance(obj_in, dict):
            update_data = obj_in
        else:
            update_data = obj_in.dict(exclude_unset=True)
        if update_data["password"]:
            hashed_password = get_password_hash(update_data["password"])
            del update_data["password"]
            update_data["hashed_password"] = hashed_password
        return super().update(session, db_obj=db_obj, obj_in=update_data)

    def authenticate(self, session: Session, *, email: str, password: str) -> Optional[UserResponse]:
        user = self.get_by_email(session, email=email)
        if not user:
            return None
        if not verify_password(password, user.hashed_password):
            return None
        return user

    def is_active(self, user: User) -> bool:
        return user.is_active

    def is_superuser(self, user: User) -> bool:
        return user.is_superuser


user_service = UserService(User)
