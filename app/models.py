from pydantic import BaseModel
from typing import Optional, Dict
from datetime import datetime

class UserInfo(BaseModel):
    childAge: str
    childPersonality: str
    kindergarten: str
    interests: str
    languages: str
    familyMembers: int
    hasSiblings: str
    siblingsAge: Optional[str] = None

class ChatRequest(BaseModel):
    thread_id: Optional[str]
    message: str
    user_info: UserInfo
    question_type: str
    subcategory: Optional[str] = None

class WeChatLoginRequest(BaseModel):
    code: str
    user_info: Dict

class User(BaseModel):
    wechat_info: Dict
    created_at: datetime
    last_login: datetime

class Thread(BaseModel):
    thread_id: str
    user_id: str
    created_at: datetime

class Message(BaseModel):
    thread_id: str
    user_id: str
    message: str
    user_info: UserInfo
    question_type: str
    subcategory: Optional[str]
    created_at: datetime

class Response(BaseModel):
    thread_id: str
    user_id: str
    message: str
    created_at: datetime

class UserProfile(BaseModel):
    user_id: str
    child_info: UserInfo
    updated_at: datetime
