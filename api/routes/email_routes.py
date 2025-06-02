from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, EmailStr
from typing import Optional
from ..services.email_service import EmailService
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/email", tags=["email"])

class InvitationEmailRequest(BaseModel):
    to_email: EmailStr
    user_name: str
    user: str
    company_spaces: str
    company_logo: Optional[str] = None
    welcome_message: str
    link: str
    language: str = 'en'

@router.post("/invitation")
async def send_invitation_email(request: InvitationEmailRequest):
    """
    Send an invitation email to a user.
    
    Example request body:
    ```json
    {
        "to_email": "otaviomascarenhaspessoal@gmail.com",
        "user_name": "John Smith",
        "user": "john.smith",
        "company_spaces": "Intao Learning Platform",
        "company_logo": "https://s3-eu-west-1.amazonaws.com/t-shaped-new/static/logo.png",
        "welcome_message": "Welcome to our learning platform! We're excited to have you join our community of learners. Together, we'll explore new skills and grow professionally.",
        "link": "https://app.intao.com/invite/abc123xyz",
        "language": "en"
    }
    ```
    """
    try:
        email_service = EmailService()
        success = email_service.send_invitation(
            to_email=request.to_email,
            user_name=request.user_name,
            user=request.user,
            company_spaces=request.company_spaces,
            company_logo=request.company_logo,
            welcome_message=request.welcome_message,
            link=request.link,
            language=request.language
        )
        
        if not success:
            raise HTTPException(status_code=500, detail="Failed to send invitation email")
        
        return {"message": "Invitation email sent successfully"}
    except ValueError as e:
        logger.error(f"Configuration error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        logger.error(f"Error sending invitation email: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e)) 