from pydantic import BaseModel, HttpUrl
from typing import List, Optional

class TeamsNotification(BaseModel):
    webhook_url: HttpUrl
    message: str

class GitChangeNotification(BaseModel):
    repository: Optional[str] = None
    branch: Optional[str] = None
    commits: Optional[List[dict]] = None
    author: Optional[str] = None
    compare_url: Optional[str] = None
    action: Optional[str] = "push"  # push, merge, pull_request, etc.