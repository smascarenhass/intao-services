import requests
import os
from typing import Optional, List, Dict
from ..models.teams import TeamsNotification, GitChangeNotification

class TeamsService:
    def __init__(self):
        self.env = os.environ.get('ENVIRONMENT', '').strip().upper()
        self.git_webhook_url = os.environ.get('TEAMS_GIT_CHANEL')
        
    def send_notification(self, webhook_url: str, message: str) -> bool:
        """
        Send a notification to Microsoft Teams
        
        Args:
            webhook_url: Teams webhook URL
            message: Message to send
            
        Returns:
            bool: True if successful, False otherwise
        """
        if self.env == 'DEV':
            print(f"[DEV MODE] Teams message suppressed: {message}")
            return True
            
        if not self.env:
            print("[WARNING] ENVIRONMENT not set, defaulting to PROD behavior")
            
        headers = {
            'Content-Type': 'application/json'
        }
        
        payload = {
            'text': message
        }
        
        try:
            response = requests.post(webhook_url, json=payload, headers=headers)
            return response.status_code == 200
        except Exception as e:
            print(f"Error sending Teams notification: {str(e)}")
            return False

    def send_git_changes(self, changes: GitChangeNotification) -> bool:
        """
        Send Git changes notification to Microsoft Teams
        
        Args:
            changes: GitChangeNotification object containing repository, branch, commits, and author information
            
        Returns:
            bool: True if successful, False otherwise
        """
        print('3')
        if not changes.webhook_url and not self.git_webhook_url:
            print("No webhook URL provided for Teams notification")
            return False
        webhook_url = changes.webhook_url or self.git_webhook_url
        changes.webhook_url = webhook_url
        print('4')
            
        try:

            # Formata a mensagem com os commits
            message = f"## 🚀 New changes in {changes.repository}\n\n"
            message += f"**Branch:** {changes.branch}\n"
            message += f"**Author:** {changes.author}\n"
            message += f"**Action:** {changes.action}\n\n"
            

            if changes.commits:
                print('5')
                message += "### 📝 Commits:\n\n"
                for commit in changes.commits:
                    message += f"- {commit['message']} ({commit['id'][:7]})\n"

            message += f"\n[View changes]({changes.compare_url})"
            print('6')
            return self.send_notification(str(changes.webhook_url), message)
        except Exception as e:
            print(f"Error sending Git changes notification: {str(e)}")
            return False

    def _format_git_message(self, changes: GitChangeNotification) -> str:
        """
        Formats Git changes message for Teams
        
        Args:
            changes: GitChangeNotification object with change information
            
        Returns:
            str: Formatted message
        """
        message = f"## 🔄 Git Changes - {changes.repository}\n\n"
        message += f"**Branch:** {changes.branch}\n"
        message += f"**Author:** {changes.author}\n"
        message += f"**Action:** {changes.action}\n\n"
        
        if changes.compare_url:
            message += f"[View Changes]({changes.compare_url})\n\n"
        
        message += "### Commits:\n"
        for commit in changes.commits:
            message += f"- {commit.get('message', 'No message')} ({commit.get('id', '')[:7]})\n"
        
        return message