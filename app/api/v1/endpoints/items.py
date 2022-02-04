from typing import Any, List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from api.deps import get_current_active_user
from db.deps import get_session
from models.user import User
from schemas.item import ItemCreateRequest, ItemResponse, ItemUpdateRequest
from services.item import item_service
from services.user import user_service

router = APIRouter()


@router.get("/", response_model=List[ItemResponse])
def read_items(
        session: Session = Depends(get_session),
        skip: int = 0,
        limit: int = 100,
        current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    Retrieve items.
    """
    if user_service.is_superuser(current_user):
        items = item_service.get_multi(session, skip=skip, limit=limit)
    else:
        items = item_service.get_multi_by_owner(session=session, owner_id=current_user.id, skip=skip, limit=limit)
    return items


@router.post("/", response_model=ItemResponse)
def create_item(
        *,
        session: Session = Depends(get_session),
        item_in: ItemCreateRequest,
        current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    Create new item.
    """
    item = item_service.create_with_owner(session=session, obj_in=item_in, owner_id=current_user.id)
    return item


@router.put("/{id}", response_model=ItemResponse)
def update_item(
        *,
        session: Session = Depends(get_session),
        id: int,
        item_in: ItemUpdateRequest,
        current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    Update an item.
    """
    item = item_service.get(session=session, id=id)
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    if not user_service.is_superuser(current_user) and (item.owner_id != current_user.id):
        raise HTTPException(status_code=400, detail="Not enough permissions")
    item = item_service.update(session=session, db_obj=item, obj_in=item_in)
    return item


@router.get("/{id}", response_model=ItemResponse)
def read_item(
        *,
        session: Session = Depends(get_session),
        id: int,
        current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    Get item by ID.
    """
    item = item_service.get(session=session, id=id)
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    if not user_service.is_superuser(current_user) and (item.owner_id != current_user.id):
        raise HTTPException(status_code=400, detail="Not enough permissions")
    return item


@router.delete("/{id}", response_model=ItemResponse)
def delete_item(
        *,
        session: Session = Depends(get_session),
        id: int,
        current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    Delete an item.
    """
    item = item_service.get(session=session, id=id)
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    if not user_service.is_superuser(current_user) and (item.owner_id != current_user.id):
        raise HTTPException(status_code=400, detail="Not enough permissions")
    item = item_service.remove(session=session, id=id)
    return item
