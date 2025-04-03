# backend/auth/models.py
from sqlmodel import SQLModel, Field
from typing import Optional
import datetime

class User(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    username: str
    email: str
    hashed_password: str
    is_active: bool = True
    is_premium: bool = False
    created_at: datetime.datetime = Field(default_factory=datetime.datetime.utcnow)
