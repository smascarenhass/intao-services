from sqlalchemy import Column, Integer, String, DateTime, Text
from sqlalchemy.ext.declarative import declarative_base
from pydantic import BaseModel
from datetime import datetime
from typing import Optional

Base = declarative_base()

class User(Base):
    __tablename__ = "xwh_users"

    ID = Column(Integer, primary_key=True, index=True)
    user_login = Column(String(60), nullable=False)
    user_pass = Column(String(255), nullable=False)
    user_nicename = Column(String(50), nullable=False)
    user_email = Column(String(100), nullable=False)
    user_url = Column(String(100), nullable=False)
    user_registered = Column(DateTime, nullable=False)
    user_activation_key = Column(String(255), nullable=False)
    user_status = Column(Integer, nullable=False)
    display_name = Column(String(250), nullable=False)

    class Config:
        orm_mode = True

# Pydantic models for API responses
class UserBase(BaseModel):
    user_email: str
    display_name: str
    user_login: str
    user_nicename: str
    user_url: str
    user_registered: datetime
    user_status: int

class UserCreate(UserBase):
    user_pass: str
    user_activation_key: str

class UserResponse(UserBase):
    user_id: int

    class Config:
        orm_mode = True

class MembershipProUserCreate(BaseModel):
    user_login: str
    user_pass: str
    user_nicename: str
    user_email: str
    user_url: Optional[str] = ""
    user_registered: Optional[datetime] = None
    user_activation_key: Optional[str] = ""
    user_status: int = 0
    display_name: str 