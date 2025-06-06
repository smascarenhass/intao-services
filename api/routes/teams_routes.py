from fastapi import APIRouter, HTTPException, Request
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
    print('1')
    # Se quiser forçar uma URL mockada, basta sobrescrever o campo:
    changes.webhook_url = "https://intaoleaders.webhook.office.com/webhookb2/c2a42877-ee61-4f3f-9f58-c739de81ef2b@2e65c0c9-93de-4e58-9cd6-5a4a42165780/IncomingWebhook/9dc613d545394d1bb70444657dc96c39/cea37b56-6d79-42ef-a4d2-56112b107bdf/V2ylDIkOiCdxRp_R3GUuxgbpAExHfSPAWVvtQdvHaLlB81"
    success = teams_service.send_git_changes(changes)

    print('2')
    
    if success:
        return {"status": "success", "message": "Git changes notification sent successfully"}
    else:
        raise HTTPException(
            status_code=500,
            detail="Failed to send Git changes notification to Teams"
        )

@router.post("/webhook/github")
async def github_webhook(request: Request):
    """
    Handle GitHub webhook events
    
    Args:
        request: FastAPI request object containing the webhook payload
        
    Returns:
        dict: Status of the webhook processing
    """
    payload = await request.json()
    
    # Verifica se é um evento de push
    if request.headers.get('X-GitHub-Event') != 'push':
        return {"status": "ignored", "message": "Not a push event"}
    
    # Verifica se é para a branch main
    if payload.get('ref') != 'refs/heads/main':
        return {"status": "ignored", "message": "Not a push to main branch"}
    
    # Prepara os dados para a notificação
    changes = GitChangeNotification(
        repository=payload['repository']['name'],
        branch='main',
        commits=payload['commits'],
        author=payload['pusher']['name'],
        compare_url=payload['compare'],
        action='push'
    )
    
    # Envia a notificação
    teams_service = TeamsService()
    success = teams_service.send_git_changes(changes)
    
    if success:
        return {"status": "success", "message": "Git changes notification sent successfully"}
    else:
        raise HTTPException(
            status_code=500,
            detail="Failed to send Git changes notification to Teams"
        ) 