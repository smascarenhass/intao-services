from fastapi import APIRouter, HTTPException, Depends
from typing import List, Dict
from pydantic import BaseModel
from datetime import datetime, timedelta
from ..auth import get_current_user_from_token
from ..services.membership_pro import MembershipProService, User
from ..services.database import get_db
from sqlalchemy.orm import Session
from ..models.user import MembershipProUserCreate
from passlib.hash import phpass

router = APIRouter(
    prefix="/api/membership-pro",
    tags=["membership-pro"]
)

class MembershipProResponse(BaseModel):
    user_id: int
    user_email: str
    display_name: str
    user_registered: datetime
    status: str
    plan: str

@router.get("/users")
async def get_membership_users(
    db: Session = Depends(get_db)
):
    """
    Returns all Membership Pro users
    """
    try:
        users = await MembershipProService.list_users(db)
        return [
            {
                "user": user
            }
            for user in users
        ]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching users: {str(e)}")

@router.get("/users/{user_id}")
async def get_membership_user(
    user_id: int,
    current_user: str = Depends(get_current_user_from_token),
    db: Session = Depends(get_db)
):
    """
    Returns details of a specific Membership Pro user
    """
    try:
        user = await MembershipProService.get_user_by_id(db, user_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
            
        return {
            "user_id": user.ID,
            "user_email": user.user_email,
            "display_name": user.display_name,
            "user_registered": user.user_registered,
            "status": "active",  # You can add logic to determine status
            "plan": "pro"  # You can add logic to determine plan
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching user: {str(e)}")

@router.post("/users/{user_id}/activate")
async def activate_membership(
    user_id: int,
    current_user: str = Depends(get_current_user_from_token),
    db: Session = Depends(get_db)
):
    """
    Activates membership pro for a user
    """
    try:
        success = await MembershipProService.update_user_status(db, user_id, "active")
        if not success:
            raise HTTPException(status_code=404, detail="User not found")
            
        return {"message": "Membership Pro activated successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error activating membership: {str(e)}")

@router.post("/users/{user_id}/deactivate")
async def deactivate_membership(
    user_id: int,
    current_user: str = Depends(get_current_user_from_token),
    db: Session = Depends(get_db)
):
    """
    Deactivates membership pro for a user
    """
    try:
        success = await MembershipProService.update_user_status(db, user_id, "inactive")
        if not success:
            raise HTTPException(status_code=404, detail="User not found")
            
        return {"message": "Membership Pro deactivated successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error deactivating membership: {str(e)}")

@router.get("/status/{user_id}")
async def get_membership_status(
    user_id: int,
    current_user: str = Depends(get_current_user_from_token),
    db: Session = Depends(get_db)
):
    """
    Checks membership pro status for a user
    """
    try:
        user = await MembershipProService.get_user_by_id(db, user_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
            
        return {
            "user_id": user.ID,
            "user_email": user.user_email,
            "status": "active",  # You can add logic to determine status
            "plan": "pro",  # You can add logic to determine plan
            "last_updated": datetime.now()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error checking membership status: {str(e)}")

@router.post("/users")
async def add_membership_user(
    user: MembershipProUserCreate,
    db: Session = Depends(get_db)
):
    try:
        new_user = await MembershipProService.add_user(db, user)
        return {"user": new_user}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error adding user: {str(e)}")