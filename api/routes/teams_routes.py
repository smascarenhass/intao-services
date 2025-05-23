from fastapi import APIRouter, HTTPException
from ..models.teams import TeamsNotification, GitChangeNotification
from ..services.teams import TeamsService

router = APIRouter(
    prefix="/teams",
    tags=["teams"]
)

@router.post("/send-message")
async def send_notification(notification: TeamsNotification):
    """
    Send a notification to Microsoft Teams
    
    Args:
        notification: TeamsNotification object containing webhook_url and message
        
    Returns:
        dict: Status of the notification
    """
    teams_service = TeamsService()
    success = teams_service.send_notification(
        webhook_url=str(notification.webhook_url),
        message=notification.message
    )
    
    if success:
        return {"status": "success", "message": "Notification sent successfully"}
    else:
        raise HTTPException(
            status_code=500,
            detail="Failed to send notification to Teams"
        )

@router.post("/send-message/git")
async def send_git_notification(changes: GitChangeNotification):
    """
    Send Git changes notification to Microsoft Teams
    
    Args:
        changes: GitChangeNotification object containing repository, branch, commits, and author information
        
    Returns:
        dict: Status of the notification
    """
    teams_service = TeamsService()
    success = teams_service.send_git_changes(changes)
    
    if success:
        return {"status": "success", "message": "Git changes notification sent successfully"}
    else:
        raise HTTPException(
            status_code=500,
            detail="Failed to send Git changes notification to Teams"
        ) 