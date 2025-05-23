import requests
import os
from typing import Optional, List, Dict
from ..models.teams import GitChangeNotification

class TeamsService:
    def __init__(self):
        self.env = os.environ.get('ENVIRONMENT', '').strip().upper()
        self.git_webhook_url = os.environ.get('TEAMS_GIT_CHANEL')
        
    def send_notification(self, webhook_url: str, message: str) -> bool:
        """
        Sends notification to Microsoft Teams
        
        Args:
            webhook_url: Teams webhook URL
            message: Message to be sent
            
        Returns:
            bool: True if sent successfully, False otherwise
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
        except requests.RequestException:
            return False

    def send_git_changes(self, changes: GitChangeNotification) -> bool:
        """
        Sends Git changes notification to Microsoft Teams
        
        Args:
            changes: GitChangeNotification object with change information
            
        Returns:
            bool: True if sent successfully, False otherwise
        """
        if not self.git_webhook_url:
            print("[ERROR] TEAMS_GIT_CHANEL not configured")
            return False

        # Format message for Teams
        message = self._format_git_message(changes)
        
        return self.send_notification(self.git_webhook_url, message)

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