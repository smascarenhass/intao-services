from pydantic import BaseModel, HttpUrl
from typing import List, Optional

class TeamsNotification(BaseModel):
    webhook_url: HttpUrl
    message: str

class GitChangeNotification(BaseModel):
    repository: str
    branch: str
    commits: List[dict]
    author: str
    compare_url: str
    action: str
    webhook_url: Optional[HttpUrl] = None