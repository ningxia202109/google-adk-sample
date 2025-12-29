from fastapi import APIRouter, HTTPException
from typing import List
from ..models.schemas import User, UserCreate, UserUpdate
from ..services.service import user_service

router = APIRouter(prefix="/users", tags=["users"])

@router.get("", response_model=List[User])
def get_users():
    return user_service.get_users()

@router.get("/{user_id}", response_model=User)
def get_user(user_id: int):
    user = user_service.get_user(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@router.post("", response_model=User, status_code=201)
def create_user(user_create: UserCreate):
    return user_service.create_user(user_create)

@router.put("/{user_id}", response_model=User)
def update_user(user_id: int, user_update: UserUpdate):
    user = user_service.update_user(user_id, user_update)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@router.delete("/{user_id}", status_code=204)
def delete_user(user_id: int):
    success = user_service.delete_user(user_id)
    if not success:
        raise HTTPException(status_code=404, detail="User not found")
    return None
