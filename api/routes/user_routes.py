from fastapi import APIRouter, HTTPException, Depends
from typing import List
from ..models.user import User
from sqlalchemy.orm import Session

router = APIRouter(
    prefix="/users",
    tags=["users"]
)

@router.get("/", response_model=List[User])
async def get_users():
    # TODO: Implement database session and query
    return []

@router.get("/{user_id}", response_model=User)
async def get_user(user_id: int):
    # TODO: Implement database session and query
    return {"id": user_id, "email": "example@email.com", "username": "example"}

@router.post("/", response_model=User)
async def create_user(user: User):
    # TODO: Implement database session and query
    return user

@router.put("/{user_id}", response_model=User)
async def update_user(user_id: int, user: User):
    # TODO: Implement database session and query
    return user

@router.delete("/{user_id}")
async def delete_user(user_id: int):
    # TODO: Implement database session and query
    return {"message": "User deleted successfully"} 